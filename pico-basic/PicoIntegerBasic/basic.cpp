// basic.cpp — Apple II Integer BASIC 相当のインタプリタ
//
// 方針
//   - 数値は 16 ビット符号付き整数 (-32767..32767)。範囲外は ">32767 ERR"。
//   - プログラムは入力した文字列のまま行番号順に保持し、実行時に直接解釈する
//     （中間コードへの変換はしない）。
//   - 文字列は DIM A$(n) で最大長を決める（DIM しなければ 255 文字）。
//     連結演算子はなく、部分文字列 A$(i,j) と A$(LEN(A$)+1)=B$ で扱う。
//   - IF 条件 THEN 文 は、条件が偽のとき THEN の直後の 1 文だけを飛ばす。
//     同じ行の ':' 以降の文は条件によらず実行される（Integer BASIC の仕様）。
//   - ハードウェアへの依存はすべて console.h 経由。

#include <setjmp.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#include "basic.h"
#include "console.h"

#define INBUF_MAX 200
#define VNAME_MAX 16
#define MAX_VARS 200
#define MAX_FOR 16
#define MAX_GOSUB 16
#define DEF_STR_DIM 255
#define DEF_ARR_DIM 10
#define MAX_NUM 32767

// ---------------------------------------------------------------------------
// エラー

enum {
  E_SYNTAX = 1, E_RANGE, E_OVERFLOW, E_BAD_BRANCH, E_BAD_RETURN, E_BAD_NEXT,
  E_GOSUBS, E_FORS, E_DIM, E_STR_OVFL, E_NO_END, E_MEM, E_FILE
};
static const char* const errMsg[] = {
  "", "SYNTAX", "RANGE", ">32767", "BAD BRANCH", "BAD RETURN", "BAD NEXT",
  "16 GOSUBS", "16 FORS", "DIM", "STR OVFL", "NO END", "MEM FULL", "FILE"
};

static jmp_buf errJmp;

// ---------------------------------------------------------------------------
// プログラム

struct PLine { int16_t num; char* text; };
static PLine* prog = nullptr;
static int nlines = 0, capLines = 0;

// ---------------------------------------------------------------------------
// 実行状態

static const char* tp;          // 解釈中の位置
static const char* stmtStart;   // 実行中の文の先頭（CON で再開する位置）
static int curLine = -1;        // 実行中の行の添字。-1 は直接実行
static bool jumped, stopReq;
static char inbuf[INBUF_MAX];
static char immBuf[INBUF_MAX];

static int contLine = -1;
static const char* contTp = nullptr;
static bool contValid = false;

static bool autoMode = false;
static int autoNum = 10, autoStep = 10;
static int grColor = 0;
static int lastKey = 0;
static uint8_t* mem;            // PEEK / POKE 用の 64KB

struct Var {
  char name[VNAME_MAX + 1];
  uint8_t kind;
  int16_t val;
  int16_t dim;                  // 配列: 最大添字
  int16_t cap, len;             // 文字列: 最大長と現在長
  int16_t* arr;
  char* str;
};
enum { K_NUM, K_ARR, K_STR };
static Var vars[MAX_VARS];
static int nvars = 0;

struct ForFrame { Var* v; int16_t limit, step; int line; const char* tp; };
static ForFrame forStack[MAX_FOR];
static int forSp = 0;

struct GosubFrame { int line; const char* tp; };
static GosubFrame gosubStack[MAX_GOSUB];
static int gosubSp = 0;

// ---------------------------------------------------------------------------
// 出力の小物

static void newlineIfNeeded() { if (con_col() != 0) con_putc('\n'); }

static void printNum(int32_t v) {
  char b[8];
  int n = 0;
  bool neg = v < 0;
  uint32_t u = neg ? -v : v;
  do { b[n++] = '0' + u % 10; u /= 10; } while (u);
  if (neg) con_putc('-');
  while (n) con_putc(b[--n]);
}

[[noreturn]] static void error(int e) {
  fs_close();
  con_bell();
  newlineIfNeeded();
  con_puts("*** ");
  con_puts(errMsg[e]);
  con_puts(" ERR\n");
  if (curLine >= 0) {
    con_puts("STOPPED AT ");
    printNum(prog[curLine].num);
    con_putc('\n');
  }
  autoMode = false;
  longjmp(errJmp, 1);
}

// Ctrl-C による中断。CON で中断した文から再開できる。
[[noreturn]] static void breakHere() {
  contLine = curLine;
  contTp = stmtStart;
  contValid = curLine >= 0;
  newlineIfNeeded();
  if (curLine >= 0) {
    con_puts("STOPPED AT ");
    printNum(prog[curLine].num);
    con_putc('\n');
  }
  longjmp(errJmp, 1);
}

// ---------------------------------------------------------------------------
// 字句解析の小物

static inline bool isDigit(char c) { return c >= '0' && c <= '9'; }
static inline bool isAlpha(char c) { return c >= 'A' && c <= 'Z'; }
static inline bool isAlnum(char c) { return isDigit(c) || isAlpha(c); }
static inline void sp() { while (*tp == ' ') tp++; }

static bool kwAt(const char* p, const char* k) {
  while (*k) if (*p++ != *k++) return false;
  return true;
}

static bool accept(const char* k) {
  sp();
  if (!kwAt(tp, k)) return false;
  tp += strlen(k);
  return true;
}

static bool acceptc(char c) {
  sp();
  if (*tp != c) return false;
  tp++;
  return true;
}

static void expect(char c) { if (!acceptc(c)) error(E_SYNTAX); }

// 関数名の直後に '(' があるときだけ関数とみなす（LENGTH などを変数にできる）
static bool acceptFn(const char* k) {
  sp();
  if (!kwAt(tp, k)) return false;
  const char* q = tp + strlen(k);
  while (*q == ' ') q++;
  if (*q != '(') return false;
  tp = q + 1;
  return true;
}

// 変数名。空白なしで "FORI=1TO10" や "IFA>BTHEN10" と書けるよう、
// 2 文字目以降に THEN / TO / STEP が現れたらそこで名前を打ち切る。
static const char* const nameStops[] = { "THEN", "TO", "STEP", nullptr };

static bool readName(char* out) {
  sp();
  if (!isAlpha(*tp)) return false;
  int n = 0;
  out[n++] = *tp++;
  while (isAlnum(*tp)) {
    bool stop = false;
    for (int i = 0; nameStops[i]; i++) if (kwAt(tp, nameStops[i])) stop = true;
    if (stop) break;
    if (n < VNAME_MAX) out[n++] = *tp;
    tp++;
  }
  out[n] = 0;
  return true;
}

static int32_t parseNumber() {
  sp();
  if (!isDigit(*tp)) error(E_SYNTAX);
  int32_t v = 0;
  while (isDigit(*tp)) {
    v = v * 10 + (*tp++ - '0');
    if (v > MAX_NUM) error(E_OVERFLOW);
  }
  return v;
}

// ---------------------------------------------------------------------------
// プログラムの格納

static int lineIndex(int num, bool* exact) {
  int lo = 0, hi = nlines;
  while (lo < hi) {
    int m = (lo + hi) / 2;
    if (prog[m].num < num) lo = m + 1; else hi = m;
  }
  if (exact) *exact = lo < nlines && prog[lo].num == num;
  return lo;
}

static void deleteLineAt(int i) {
  free(prog[i].text);
  memmove(&prog[i], &prog[i + 1], (nlines - i - 1) * sizeof(PLine));
  nlines--;
}

// 行を編集すると行の添字がずれるので、FOR/GOSUB の記録と CON を無効にする
static void invalidateRun() { forSp = gosubSp = 0; contValid = false; }

static void storeLine(int num, const char* text) {
  invalidateRun();
  bool exact;
  int i = lineIndex(num, &exact);
  if (!*text) {
    if (exact) deleteLineAt(i);
    return;
  }
  char* t = (char*)malloc(strlen(text) + 1);
  if (!t) error(E_MEM);
  strcpy(t, text);
  if (exact) {
    free(prog[i].text);
    prog[i].text = t;
    return;
  }
  if (nlines == capLines) {
    int nc = capLines ? capLines * 2 : 64;
    PLine* np = (PLine*)realloc(prog, nc * sizeof(PLine));
    if (!np) { free(t); error(E_MEM); }
    prog = np;
    capLines = nc;
  }
  memmove(&prog[i + 1], &prog[i], (nlines - i) * sizeof(PLine));
  prog[i].num = num;
  prog[i].text = t;
  nlines++;
}

static void newProgram() {
  for (int i = 0; i < nlines; i++) free(prog[i].text);
  nlines = 0;
  invalidateRun();
}

// ---------------------------------------------------------------------------
// 変数

static void clearVars() {
  for (int i = 0; i < nvars; i++) { free(vars[i].arr); free(vars[i].str); }
  nvars = 0;
  invalidateRun();
}

static Var* lookup(const char* name, uint8_t kind) {
  for (int i = 0; i < nvars; i++)
    if (vars[i].kind == kind && strcmp(vars[i].name, name) == 0) return &vars[i];
  return nullptr;
}

static Var* create(const char* name, uint8_t kind, int size) {
  if (nvars >= MAX_VARS) error(E_MEM);
  Var* v = &vars[nvars];
  memset(v, 0, sizeof *v);
  strcpy(v->name, name);
  v->kind = kind;
  if (kind == K_ARR) {
    v->arr = (int16_t*)calloc(size + 1, sizeof(int16_t));
    if (!v->arr) error(E_MEM);
    v->dim = size;
  } else if (kind == K_STR) {
    v->str = (char*)malloc(size);
    if (!v->str) error(E_MEM);
    v->cap = size;
  }
  nvars++;
  return v;
}

static Var* getVar(const char* name, uint8_t kind) {
  Var* v = lookup(name, kind);
  return v ? v : create(name, kind, kind == K_STR ? DEF_STR_DIM : DEF_ARR_DIM);
}

// ---------------------------------------------------------------------------
// 式

struct SVal { const char* p; int len; };

static int32_t expr();

static int32_t chk(int32_t v) {
  if (v > MAX_NUM || v < -MAX_NUM) error(E_OVERFLOW);
  return v;
}

// 名前の直後の "(添字)" を読んで数値変数・配列要素の場所を返す
static int16_t* numRef(const char* name) {
  if (acceptc('(')) {
    int32_t i = expr();
    expect(')');
    Var* v = getVar(name, K_ARR);
    if (i < 0 || i > v->dim) error(E_RANGE);
    return &v->arr[i];
  }
  return &getVar(name, K_NUM)->val;
}

static bool isStrStart() {
  sp();
  if (*tp == '"') return true;
  if (!isAlpha(*tp)) return false;
  const char* q = tp;
  while (isAlnum(*q)) q++;
  return *q == '$';
}

// 文字列リテラル、A$、A$(i)、A$(i,j)
static SVal strExpr() {
  sp();
  SVal r;
  if (*tp == '"') {
    r.p = ++tp;
    while (*tp && *tp != '"') tp++;
    r.len = tp - r.p;
    if (*tp == '"') tp++;
    return r;
  }
  char name[VNAME_MAX + 1];
  if (!readName(name) || *tp != '$') error(E_SYNTAX);
  tp++;
  Var* v = getVar(name, K_STR);
  int32_t lo = 1, hi = v->len;
  if (acceptc('(')) {
    lo = expr();
    if (acceptc(',')) hi = expr();
    expect(')');
    if (lo < 1 || hi < 0) error(E_RANGE);
    if (hi > v->len) hi = v->len;
    if (lo > v->len + 1) lo = v->len + 1;
  }
  r.p = v->str + lo - 1;
  r.len = hi >= lo ? hi - lo + 1 : 0;
  return r;
}

static int strCompare(SVal a, SVal b) {
  int n = a.len < b.len ? a.len : b.len;
  int c = memcmp(a.p, b.p, n);
  if (c) return c < 0 ? -1 : 1;
  return (a.len > b.len) - (a.len < b.len);
}

static int32_t peekMem(int32_t addr);

static int32_t rnd(int32_t n) {
  if (n == 0) return 0;
  int32_t m = n < 0 ? -n : n;
  int32_t v = hw_random() % m;
  return n < 0 ? -v : v;
}

static int32_t primary() {
  sp();
  if (*tp == '(') {
    tp++;
    int32_t v = expr();
    expect(')');
    return v;
  }
  if (isDigit(*tp)) return parseNumber();

  int32_t v;
  if (acceptFn("ABS")) { v = expr(); expect(')'); return v < 0 ? -v : v; }
  if (acceptFn("SGN")) { v = expr(); expect(')'); return (v > 0) - (v < 0); }
  if (acceptFn("PEEK")) { v = expr(); expect(')'); return peekMem(v); }
  if (acceptFn("RND")) { v = expr(); expect(')'); return rnd(v); }
  if (acceptFn("PDL")) { v = expr(); expect(')'); return hw_pdl(v); }
  if (acceptFn("SCRN")) {
    int32_t x = expr();
    expect(',');
    int32_t y = expr();
    expect(')');
    if (x < 0 || x > 39 || y < 0 || y > 47) error(E_RANGE);
    return gr_scrn(x, y);
  }
  if (acceptFn("LEN")) { SVal s = strExpr(); expect(')'); return s.len; }
  if (acceptFn("ASC")) {
    // Apple II の文字コードは最上位ビットが立つ（"A" は 193）
    SVal s = strExpr();
    expect(')');
    return s.len ? ((uint8_t)s.p[0] | 0x80) : 0;
  }

  char name[VNAME_MAX + 1];
  if (readName(name)) {
    if (*tp == '$') error(E_SYNTAX);   // 数値が要る所に文字列
    return *numRef(name);
  }
  error(E_SYNTAX);
}

static int32_t unary() {
  sp();
  if (*tp == '-') { tp++; return chk(-unary()); }
  if (*tp == '+') { tp++; return unary(); }
  if (accept("NOT")) return !unary();
  return primary();
}

static int32_t power() {
  int32_t a = unary();
  while (acceptc('^')) {
    int32_t b = unary();
    if (b < 0) error(E_RANGE);
    int32_t r = 1;
    while (b-- > 0) {
      r = chk(r * a);
      if (r == 0 || r == 1) break;
    }
    a = r;
  }
  return a;
}

static int32_t term() {
  int32_t a = power();
  for (;;) {
    sp();
    if (*tp == '*') { tp++; a = chk(a * power()); }
    else if (*tp == '/') {
      tp++;
      int32_t b = power();
      if (!b) error(E_OVERFLOW);
      a /= b;
    } else if (accept("MOD")) {
      int32_t b = power();
      if (!b) error(E_OVERFLOW);
      a %= b;
    } else return a;
  }
}

static int32_t sum() {
  int32_t a = term();
  for (;;) {
    sp();
    if (*tp == '+') { tp++; a = chk(a + term()); }
    else if (*tp == '-') { tp++; a = chk(a - term()); }
    else return a;
  }
}

// 1:=  2:# <>  3:<  4:>  5:<=  6:>=
static int relop() {
  sp();
  switch (*tp) {
    case '=': tp++; return 1;
    case '#': tp++; return 2;
    case '<':
      tp++;
      if (*tp == '>') { tp++; return 2; }
      if (*tp == '=') { tp++; return 5; }
      return 3;
    case '>':
      tp++;
      if (*tp == '=') { tp++; return 6; }
      return 4;
  }
  return 0;
}

static int32_t cmpResult(int op, int c) {
  switch (op) {
    case 1: return c == 0;
    case 2: return c != 0;
    case 3: return c < 0;
    case 4: return c > 0;
    case 5: return c <= 0;
    default: return c >= 0;
  }
}

static int32_t relation() {
  if (isStrStart()) {
    SVal a = strExpr();
    int op = relop();
    if (!op) error(E_SYNTAX);
    SVal b = strExpr();
    return cmpResult(op, strCompare(a, b));
  }
  int32_t a = sum();
  for (;;) {
    int op = relop();
    if (!op) return a;
    int32_t b = sum();
    a = cmpResult(op, (a > b) - (a < b));
  }
}

static int32_t conj() {
  int32_t a = relation();
  while (accept("AND")) {
    int32_t b = relation();
    a = a && b;
  }
  return a;
}

static int32_t expr() {
  int32_t a = conj();
  while (accept("OR")) {
    int32_t b = conj();
    a = a || b;
  }
  return a;
}

// ---------------------------------------------------------------------------
// メモリと入出力アドレス（よく使われるものだけ Apple II をまねる）

static int32_t peekMem(int32_t addr) {
  uint16_t a = (uint16_t)addr;
  switch (a) {
    case 0x24: return con_col();                     // CH: カーソル桁
    case 0xC000: {                                   // キーボード
      int k = con_peekkey();
      return k >= 0 ? ((k & 0x7F) | 0x80) : (lastKey & 0x7F);
    }
    case 0xC010: {                                   // ストローブ解除
      int k = con_pollkey();
      if (k >= 0) lastKey = k;
      return lastKey & 0x7F;
    }
    case 0xC030: hw_speaker(); return 0;
    case 0xC061: return hw_button(0) ? 128 : 0;
    case 0xC062: return hw_button(1) ? 128 : 0;
  }
  return mem[a];
}

static void pokeMem(int32_t addr, int32_t val) {
  uint16_t a = (uint16_t)addr;
  switch (a) {
    case 0x24: con_htab(val + 1); return;
    case 0xC010: { int k = con_pollkey(); if (k >= 0) lastKey = k; return; }
    case 0xC030: hw_speaker(); return;
    case 0xC050: gr_mode(true); return;
    case 0xC051: gr_mode(false); return;
  }
  mem[a] = (uint8_t)val;
}

// ---------------------------------------------------------------------------
// 入力

// 1 行読む。Ctrl-C なら false。英小文字は大文字にする。
static bool getLine(char* buf, int max) {
  int n = 0;
  for (;;) {
    int c = con_getkey();
    if (c == '\r' || c == '\n') {
      con_putc('\n');
      buf[n] = 0;
      return true;
    }
    if (c == 3) {
      con_putc('\n');
      buf[0] = 0;
      return false;
    }
    if (c == 8 || c == 0x7F) {                        // ← / BS / DEL
      if (n > 0) { n--; con_putc('\b'); }
      continue;
    }
    if (c == 0x18) {                                  // Ctrl-X: 行を取り消す
      while (n > 0) { n--; con_putc('\b'); }
      continue;
    }
    if (c >= ' ' && c < 0x7F && n < max - 1) {
      if (c >= 'a' && c <= 'z') c -= 32;
      buf[n++] = (char)c;
      con_putc((char)c);
    }
  }
}

// ---------------------------------------------------------------------------
// 文

static void execStatement();

static void assignStr(Var* v, int32_t pos, SVal s) {
  if (pos < 1 || pos > v->len + 1) error(E_RANGE);
  int32_t newLen = pos - 1 + s.len;
  if (newLen > v->cap) error(E_STR_OVFL);
  memmove(v->str + pos - 1, s.p, s.len);
  v->len = newLen;
}

static int findTarget(int32_t num) {
  bool exact;
  int i = lineIndex(num, &exact);
  if (!exact) error(E_BAD_BRANCH);
  return i;
}

static void jumpToIndex(int i) {
  curLine = i;
  tp = prog[i].text;
  jumped = true;
}

static void st_let() {
  char name[VNAME_MAX + 1];
  if (!readName(name)) error(E_SYNTAX);
  if (acceptc('$')) {
    Var* v = getVar(name, K_STR);
    int32_t pos = 1;
    if (acceptc('(')) { pos = expr(); expect(')'); }
    expect('=');
    assignStr(v, pos, strExpr());
  } else {
    int16_t* p = numRef(name);
    expect('=');
    *p = (int16_t)expr();
  }
}

static void st_print() {
  bool nl = true;
  for (;;) {
    sp();
    if (*tp == 0 || *tp == ':') break;
    if (acceptc(';')) { nl = false; continue; }
    if (acceptc(',')) {                               // 8 桁ごとのタブ
      int n = 8 - con_col() % 8;
      if (con_col() + n >= con_width()) con_putc('\n');
      else while (n--) con_putc(' ');
      nl = false;
      continue;
    }
    nl = true;
    if (isStrStart()) {
      SVal s = strExpr();
      for (int i = 0; i < s.len; i++) con_putc(s.p[i]);
    } else {
      printNum(expr());
    }
  }
  if (nl) con_putc('\n');
}

static void st_input() {
  sp();
  bool prompted = false;
  if (*tp == '"') {
    SVal s = strExpr();
    for (int i = 0; i < s.len; i++) con_putc(s.p[i]);
    if (!acceptc(',')) expect(';');
    prompted = true;
  }
  const char* ip = nullptr;                           // 数値入力の読みかけ位置
  do {
    char name[VNAME_MAX + 1];
    if (!readName(name)) error(E_SYNTAX);
    if (acceptc('$')) {
      Var* v = getVar(name, K_STR);
      int32_t pos = 1;
      if (acceptc('(')) { pos = expr(); expect(')'); }
      if (!getLine(inbuf, INBUF_MAX)) breakHere();
      SVal s = { inbuf, (int)strlen(inbuf) };
      assignStr(v, pos, s);
      ip = nullptr;
    } else {
      int16_t* p = numRef(name);
      for (;;) {
        if (!ip || !*ip) {
          if (ip) con_puts("??");
          else if (!prompted) con_putc('?');
          if (!getLine(inbuf, INBUF_MAX)) breakHere();
          ip = inbuf;
        }
        while (*ip == ' ') ip++;
        bool neg = false;
        if (*ip == '-' || *ip == '+') neg = *ip++ == '-';
        if (!isDigit(*ip)) {
          con_puts("RETYPE LINE\n");
          ip = nullptr;
          prompted = false;
          continue;
        }
        int32_t v = 0;
        while (isDigit(*ip)) {
          v = v * 10 + (*ip++ - '0');
          if (v > MAX_NUM) error(E_OVERFLOW);
        }
        while (*ip == ' ') ip++;
        if (*ip == ',') ip++;
        *p = (int16_t)(neg ? -v : v);
        break;
      }
    }
    prompted = true;
  } while (acceptc(','));
}

// 条件が偽のときに THEN の後の 1 文を読み飛ばす
static void skipStatement() {
  sp();
  if (kwAt(tp, "REM")) { tp += strlen(tp); return; }
  bool q = false;
  while (*tp && (q || *tp != ':')) {
    if (*tp == '"') q = !q;
    tp++;
  }
}

static void st_if() {
  int32_t c = expr();
  if (!accept("THEN")) {
    if (!accept("GOTO")) error(E_SYNTAX);
    int32_t n = expr();
    if (c) jumpToIndex(findTarget(n));
    return;
  }
  sp();
  if (isDigit(*tp)) {
    int32_t n = parseNumber();
    if (c) jumpToIndex(findTarget(n));
    return;
  }
  if (c) execStatement();
  else skipStatement();
}

static void st_goto() { jumpToIndex(findTarget(expr())); }

static void st_gosub() {
  int i = findTarget(expr());
  if (gosubSp >= MAX_GOSUB) error(E_GOSUBS);
  gosubStack[gosubSp].line = curLine;
  gosubStack[gosubSp].tp = tp;
  gosubSp++;
  jumpToIndex(i);
}

static void st_return() {
  if (gosubSp == 0) error(E_BAD_RETURN);
  gosubSp--;
  curLine = gosubStack[gosubSp].line;
  tp = gosubStack[gosubSp].tp;
  jumped = true;
}

static void st_pop() {
  if (gosubSp == 0) error(E_BAD_RETURN);
  gosubSp--;
}

static void st_for() {
  char name[VNAME_MAX + 1];
  if (!readName(name) || *tp == '$' || *tp == '(') error(E_SYNTAX);
  Var* v = getVar(name, K_NUM);
  expect('=');
  int32_t start = expr();
  if (!accept("TO")) error(E_SYNTAX);
  int32_t limit = expr();
  int32_t step = 1;
  if (accept("STEP")) step = expr();
  v->val = (int16_t)start;
  for (int i = forSp - 1; i >= 0; i--)                // 同じ変数のループは作り直す
    if (forStack[i].v == v) { forSp = i; break; }
  if (forSp >= MAX_FOR) error(E_FORS);
  ForFrame& f = forStack[forSp++];
  f.v = v;
  f.limit = (int16_t)limit;
  f.step = (int16_t)step;
  f.line = curLine;
  f.tp = tp;
}

static void st_next() {
  do {
    int f = forSp - 1;
    char name[VNAME_MAX + 1];
    const char* save = tp;
    if (readName(name)) {
      Var* v = lookup(name, K_NUM);
      while (f >= 0 && forStack[f].v != v) f--;
    } else {
      tp = save;
    }
    if (f < 0) error(E_BAD_NEXT);
    forSp = f + 1;
    ForFrame& fr = forStack[f];
    int32_t nv = fr.v->val + fr.step;
    bool again = fr.step >= 0 ? nv <= fr.limit : nv >= fr.limit;
    if (nv > MAX_NUM || nv < -MAX_NUM) again = false;
    else fr.v->val = (int16_t)nv;
    if (again) {
      curLine = fr.line;
      tp = fr.tp;
      jumped = true;
      return;
    }
    forSp--;
  } while (acceptc(','));
}

static void st_dim() {
  do {
    char name[VNAME_MAX + 1];
    if (!readName(name)) error(E_SYNTAX);
    bool isStr = acceptc('$');
    expect('(');
    int32_t n = expr();
    expect(')');
    if (isStr) {
      if (n < 1 || n > 255) error(E_RANGE);
      if (lookup(name, K_STR)) error(E_DIM);
      create(name, K_STR, n);
    } else {
      if (n < 0) error(E_RANGE);
      if (lookup(name, K_ARR)) error(E_DIM);
      create(name, K_ARR, n);
    }
  } while (acceptc(','));
}

static void st_rem() { tp += strlen(tp); }
static void st_end() { stopReq = true; }

static void st_poke() {
  int32_t a = expr();
  expect(',');
  pokeMem(a, expr());
}

static void st_call() {
  switch (expr()) {
    case -936: con_home(); break;                     // HOME
    case -958: con_clreos(); break;
    case -868: con_clreol(); break;
    case -922: con_putc('\n'); break;
    case -198: con_bell(); break;
    case -1998:
    case -1994: gr_clear(); break;
    default: break;                                   // それ以外は何もしない
  }
}

static void st_tab() {
  int32_t n = expr();
  if (n < 1 || n > 255) error(E_RANGE);
  con_htab(n);
}

static void st_vtab() {
  int32_t n = expr();
  if (n < 1 || n > 24) error(E_RANGE);
  con_vtab(n);
}

static void st_text() { gr_mode(false); }
static void st_gr() { gr_mode(true); gr_clear(); }

static void st_color() {
  expect('=');
  grColor = expr() & 15;
}

static void checkXY(int32_t x, int32_t y) {
  if (x < 0 || x > 39 || y < 0 || y > 47) error(E_RANGE);
}

static void st_plot() {
  int32_t x = expr();
  expect(',');
  int32_t y = expr();
  checkXY(x, y);
  gr_plot(x, y, grColor);
}

static void st_hlin() {
  int32_t a = expr();
  expect(',');
  int32_t b = expr();
  if (!accept("AT")) error(E_SYNTAX);
  int32_t y = expr();
  if (a > b) { int32_t t = a; a = b; b = t; }
  checkXY(a, y);
  checkXY(b, y);
  for (int32_t x = a; x <= b; x++) gr_plot(x, y, grColor);
}

static void st_vlin() {
  int32_t a = expr();
  expect(',');
  int32_t b = expr();
  if (!accept("AT")) error(E_SYNTAX);
  int32_t x = expr();
  if (a > b) { int32_t t = a; a = b; b = t; }
  checkXY(x, a);
  checkXY(x, b);
  for (int32_t y = a; y <= b; y++) gr_plot(x, y, grColor);
}

static void st_ignoreExpr() { expr(); }              // HIMEM: / LOMEM:

// ---- 主に直接実行で使うコマンド ----

static void immediateOnly() { if (curLine >= 0) error(E_SYNTAX); }

static void st_list() {
  int32_t lo = 0, hi = MAX_NUM;
  sp();
  if (isDigit(*tp)) {
    lo = hi = parseNumber();
    if (acceptc(',') || acceptc('-')) {
      sp();
      hi = isDigit(*tp) ? parseNumber() : MAX_NUM;
    }
  }
  for (int i = 0; i < nlines; i++) {
    if (prog[i].num < lo || prog[i].num > hi) continue;
    printNum(prog[i].num);
    con_putc(' ');
    con_puts(prog[i].text);
    con_putc('\n');
    con_idle();
    int k = con_pollkey();                            // 何か押すと一時停止
    if (k == 3) break;
    if (k >= 0 && con_getkey() == 3) break;
  }
}

static void st_run() {
  sp();
  int32_t start = isDigit(*tp) ? parseNumber() : 0;
  clearVars();
  int i = lineIndex(start, nullptr);
  if (i >= nlines) { stopReq = true; return; }
  jumpToIndex(i);
}

static void st_new() { immediateOnly(); newProgram(); clearVars(); }
static void st_clr() { clearVars(); }

static void st_del() {
  immediateOnly();
  int32_t a = parseNumber(), b = a;
  if (acceptc(',')) b = parseNumber();
  invalidateRun();
  for (int i = nlines - 1; i >= 0; i--)
    if (prog[i].num >= a && prog[i].num <= b) deleteLineAt(i);
}

static void st_auto() {
  immediateOnly();
  autoNum = 10;
  autoStep = 10;
  sp();
  if (isDigit(*tp)) autoNum = parseNumber();
  if (acceptc(',')) autoStep = parseNumber();
  if (autoStep < 1) error(E_RANGE);
  autoMode = true;
}

static void st_man() { autoMode = false; }

static void st_con() {
  if (!contValid) return;
  curLine = contLine;
  tp = contTp;
  contValid = false;
  jumped = true;
}

// ---- 追加コマンド: プログラムをフラッシュに保存する ----

static void readFileName(char* out, int max) {
  sp();
  int n = 0;
  if (*tp == '"') {
    tp++;
    while (*tp && *tp != '"') {
      char c = *tp++;
      if ((isAlnum(c) || c == '_' || c == '-') && n < max - 1) out[n++] = c;
    }
    if (*tp == '"') tp++;
  } else {
    while (isAlnum(*tp) && n < max - 1) out[n++] = *tp++;
  }
  if (!n) { strcpy(out, "PROGRAM"); return; }
  out[n] = 0;
}

static void st_save() {
  char fn[24];
  readFileName(fn, sizeof fn);
  if (!fs_open_write(fn)) error(E_FILE);
  char buf[INBUF_MAX + 8];
  for (int i = 0; i < nlines; i++) {
    int n = 0, v = prog[i].num;
    char d[8];
    int k = 0;
    do { d[k++] = '0' + v % 10; v /= 10; } while (v);
    while (k) buf[n++] = d[--k];
    buf[n++] = ' ';
    strncpy(buf + n, prog[i].text, sizeof buf - n - 1);
    buf[sizeof buf - 1] = 0;
    fs_write_line(buf);
  }
  fs_close();
}

static void st_load() {
  immediateOnly();
  char fn[24];
  readFileName(fn, sizeof fn);
  if (!fs_open_read(fn)) error(E_FILE);
  newProgram();
  clearVars();
  while (fs_read_line(inbuf, INBUF_MAX)) {
    char* s = inbuf;
    bool q = false;
    for (char* p = s; *p; p++) {                      // 文字列の外を大文字に
      if (*p == '"') q = !q;
      else if (!q && *p >= 'a' && *p <= 'z') *p -= 32;
    }
    while (*s == ' ') s++;
    if (!isDigit(*s)) continue;
    int32_t n = 0;
    while (isDigit(*s)) n = n * 10 + (*s++ - '0');
    while (*s == ' ') s++;
    if (n <= MAX_NUM) storeLine(n, s);
  }
  fs_close();
}

static void st_catalog() { fs_catalog(); }

// ---------------------------------------------------------------------------
// 文の振り分け

struct Cmd { const char* kw; void (*fn)(); };
static const Cmd cmds[] = {
  { "PRINT", st_print }, { "?", st_print },
  { "INPUT", st_input }, { "IF", st_if },
  { "GOTO", st_goto }, { "GOSUB", st_gosub },
  { "RETURN", st_return }, { "FOR", st_for }, { "NEXT", st_next },
  { "LET", st_let }, { "DIM", st_dim }, { "REM", st_rem },
  { "END", st_end }, { "POKE", st_poke }, { "CALL", st_call },
  { "POP", st_pop }, { "TAB", st_tab }, { "VTAB", st_vtab },
  { "TEXT", st_text }, { "GR", st_gr }, { "COLOR", st_color },
  { "PLOT", st_plot }, { "HLIN", st_hlin }, { "VLIN", st_vlin },
  { "HIMEM:", st_ignoreExpr }, { "LOMEM:", st_ignoreExpr },
  { "LIST", st_list }, { "RUN", st_run }, { "NEW", st_new },
  { "CLR", st_clr }, { "DEL", st_del }, { "AUTO", st_auto },
  { "MAN", st_man }, { "CON", st_con },
  { "SAVE", st_save }, { "LOAD", st_load }, { "CATALOG", st_catalog },
};

static void execStatement() {
  sp();
  for (const Cmd& c : cmds)
    if (accept(c.kw)) { c.fn(); return; }
  st_let();                                           // LET は省略できる
}

static void execLoop() {
  for (;;) {
    sp();
    if (*tp == 0) {
      if (curLine < 0) return;
      if (++curLine >= nlines) {                      // END がないまま末尾に到達
        curLine = -1;
        error(E_NO_END);
      }
      tp = prog[curLine].text;
      continue;
    }
    if (*tp == ':') { tp++; continue; }

    con_idle();
    if (con_peekkey() == 3) { con_pollkey(); breakHere(); }

    stmtStart = tp;
    jumped = stopReq = false;
    execStatement();
    if (stopReq) { curLine = -1; return; }
    if (jumped) continue;
    sp();
    if (*tp && *tp != ':') error(E_SYNTAX);
  }
}

// 直接実行の FOR/GOSUB は immBuf を指しているので、次の行を実行する前に捨てる
static void dropImmediateFrames() {
  int n = 0;
  for (int i = 0; i < forSp; i++) if (forStack[i].line >= 0) forStack[n++] = forStack[i];
  forSp = n;
  n = 0;
  for (int i = 0; i < gosubSp; i++) if (gosubStack[i].line >= 0) gosubStack[n++] = gosubStack[i];
  gosubSp = n;
}

static void processLine(char* s) {
  while (*s == ' ') s++;
  if (!*s) return;
  if (isDigit(*s)) {
    int32_t n = 0;
    while (isDigit(*s)) {
      n = n * 10 + (*s++ - '0');
      if (n > MAX_NUM) error(E_RANGE);
    }
    while (*s == ' ') s++;
    storeLine(n, s);
    return;
  }
  strcpy(immBuf, s);
  curLine = -1;
  tp = immBuf;
  dropImmediateFrames();
  execLoop();
}

void basic_main() {
  mem = (uint8_t*)calloc(65536, 1);
  con_puts("INTEGER BASIC\nFOR PICO 2 W\n\n");

  setjmp(errJmp);                                     // エラー・中断はここへ戻る
  for (;;) {
    curLine = -1;
    if (autoMode) {
      printNum(autoNum);
      con_putc(' ');
      if (!getLine(inbuf, INBUF_MAX) || !inbuf[0]) { autoMode = false; continue; }
      char* s = inbuf;
      while (*s == ' ') s++;
      storeLine(autoNum, s);
      autoNum += autoStep;
      if (autoNum > MAX_NUM) autoMode = false;
      continue;
    }
    con_putc('>');
    if (!getLine(inbuf, INBUF_MAX)) continue;
    processLine(inbuf);
  }
}
