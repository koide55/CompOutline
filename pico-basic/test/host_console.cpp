// host_console.cpp — PC 上でインタプリタを試すための console.h 実装
//
// 標準入力をキーボード、標準出力を画面として使う。入力が尽きたら終了する。
// SAVE / LOAD はカレントディレクトリの NAME.BAS を読み書きする。
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "../PicoIntegerBasic/console.h"

static int col = 0;
static unsigned char grbuf[48][40];
static FILE* fsFile = nullptr;

void con_init() {}

void con_putc(char c) {
  if (c == '\n' || c == '\r') { putchar('\n'); col = 0; return; }
  if (c == '\b') { if (col > 0) col--; fputs("\b \b", stdout); return; }
  if (c == 7) return;
  if ((unsigned char)c < 32) return;
  putchar(c);
  if (++col >= 40) { putchar('\n'); col = 0; }
}

void con_puts(const char* s) { while (*s) con_putc(*s++); }
int con_col() { return col; }
int con_width() { return 40; }
void con_home() { puts("[HOME]"); col = 0; }
void con_clreol() {}
void con_clreos() {}
void con_vtab(int row) { printf("[VTAB %d]", row); }
void con_htab(int c) { while (col < c - 1) con_putc(' '); }
void con_bell() {}

int con_getkey() {
  int c = getchar();
  if (c == EOF) { fflush(stdout); exit(0); }
  return c == '\n' ? '\r' : c;
}
int con_peekkey() { return -1; }
int con_pollkey() { return -1; }
void con_push_key(uint8_t) {}
void con_idle() {}

void gr_mode(bool on) { printf("[%s]\n", on ? "GR" : "TEXT"); col = 0; }
void gr_clear() { memset(grbuf, 0, sizeof grbuf); }
void gr_plot(int x, int y, int c) { grbuf[y][x] = c; }
int gr_scrn(int x, int y) { return grbuf[y][x]; }

int hw_pdl(int) { return 128; }
int hw_button(int) { return 0; }
void hw_speaker() {}
uint32_t hw_random() { return (uint32_t)rand(); }

static void path(const char* name, char* out) { snprintf(out, 64, "%s.BAS", name); }

bool fs_open_write(const char* name) {
  char p[64];
  path(name, p);
  fsFile = fopen(p, "w");
  return fsFile != nullptr;
}
void fs_write_line(const char* s) { fprintf(fsFile, "%s\n", s); }
bool fs_open_read(const char* name) {
  char p[64];
  path(name, p);
  fsFile = fopen(p, "r");
  return fsFile != nullptr;
}
bool fs_read_line(char* buf, int max) {
  if (!fsFile || !fgets(buf, max, fsFile)) return false;
  buf[strcspn(buf, "\r\n")] = 0;
  return true;
}
void fs_close() { if (fsFile) { fclose(fsFile); fsFile = nullptr; } }
void fs_catalog() { con_puts("(CATALOG)\n"); }

int main() {
  setvbuf(stdout, nullptr, _IONBF, 0);
  srand(1);
  extern void basic_main();
  basic_main();
}
