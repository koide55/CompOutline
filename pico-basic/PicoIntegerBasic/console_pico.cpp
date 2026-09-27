// console_pico.cpp — 実機用の console.h 実装
//
// 画面   : SSD1306 128x64 に 6x8 ドットの文字で 21 桁 x 8 行
// 入力   : USB キーボード (usb_keyboard.cpp がキューに積む) と USB シリアル
// 出力   : OLED と USB シリアルの両方に出す（シリアルはデバッグ用の写し）
// GR     : 40x40 のブロックを 2x1 ドットで上部 40 ドットに描き、下 3 行をテキストに使う
// 保存   : LittleFS (/NAME.BAS)
#include <Arduino.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <LittleFS.h>
#include <Wire.h>
#include <pico/util/queue.h>

#include "config.h"
#include "console.h"

#define COLS 21
#define ROWS 8
#define GR_ROWS 40       // 画面に出す GR の行数（40..47 は記憶だけ）
#define GR_X0 24         // (128 - 40*2) / 2
#define GR_TEXT_TOP 5    // GR モードでテキストに使う最初の行

static Adafruit_SSD1306 oled(128, 64, &Wire, -1);
static bool oledOk = false;

static char scr[ROWS][COLS];
static int cx = 0, cy = 0, winTop = 0;
static bool grMode = false;
static uint8_t grbuf[48][40];

static bool dirty = true, cursorOn = false, blinkOn = true;
static uint32_t lastDraw = 0, lastBlink = 0, lastTick = 0;

static queue_t keyq;
static bool serialLastCR = false;

static bool fsOk = false;
static File fsFile;

// ---------------------------------------------------------------------------
// 描画

static void draw() {
  oled.clearDisplay();
  if (grMode) {
    for (int y = 0; y < GR_ROWS; y++)
      for (int x = 0; x < 40; x++)
        if (grbuf[y][x]) oled.drawFastHLine(GR_X0 + x * 2, y, 2, SSD1306_WHITE);
  }
  for (int r = grMode ? GR_TEXT_TOP : 0; r < ROWS; r++)
    for (int c = 0; c < COLS; c++)
      if (scr[r][c] != ' ')
        oled.drawChar(c * 6, r * 8, scr[r][c], SSD1306_WHITE, SSD1306_BLACK, 1);
  if (cursorOn && blinkOn) oled.fillRect(cx * 6, cy * 8, 6, 8, SSD1306_INVERSE);
  oled.display();
}

void con_idle() {
  uint32_t us = micros();
  if (us - lastTick < 1000) return;                  // 1ms に 1 回で十分
  lastTick = us;

  yield();                                           // USB デバイス (シリアル) の処理

  // シリアルからの入力もキーとして扱う。キューが満杯なら読まずに待たせるので、
  // 端末からプログラムを貼り付けても取りこぼさない。
  while (Serial.available() && !queue_is_full(&keyq)) {
    int c = Serial.read();
    if (c == '\n' && serialLastCR) { serialLastCR = false; continue; }
    serialLastCR = c == '\r';
    if (c == '\n') c = '\r';
    con_push_key((uint8_t)c);
  }

  uint32_t now = millis();
  if (cursorOn && now - lastBlink >= 400) {
    blinkOn = !blinkOn;
    lastBlink = now;
    dirty = true;
  }
  if (dirty && oledOk && now - lastDraw >= REFRESH_MS) {
    draw();
    dirty = false;
    lastDraw = millis();
  }
}

// ---------------------------------------------------------------------------
// テキスト

void con_init() {
  queue_init(&keyq, 1, 64);
  Serial.begin(115200);

  Wire.setSDA(PIN_OLED_SDA);
  Wire.setSCL(PIN_OLED_SCL);
  oledOk = oled.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR);
  if (oledOk) oled.setTextWrap(false);
  memset(scr, ' ', sizeof scr);

  if (PIN_SPEAKER >= 0) pinMode(PIN_SPEAKER, OUTPUT);
  pinMode(PIN_BUTTON0, INPUT_PULLUP);
  pinMode(PIN_BUTTON1, INPUT_PULLUP);

  fsOk = LittleFS.begin();
}

static void scrollUp() {
  for (int r = winTop; r < ROWS - 1; r++) memcpy(scr[r], scr[r + 1], COLS);
  memset(scr[ROWS - 1], ' ', COLS);
}

static void newline() {
  cx = 0;
  if (++cy >= ROWS) {
    cy = ROWS - 1;
    scrollUp();
  }
  dirty = true;
}

void con_putc(char c) {
  if (Serial) {
    if (c == '\n' || c == '\r') Serial.write("\r\n");
    else if (c == '\b') Serial.write("\b \b");
    else Serial.write(c);
  }
  switch (c) {
    case '\r':
    case '\n': newline(); return;
    case '\b':
      if (cx > 0) cx--;
      else if (cy > winTop) { cy--; cx = COLS - 1; }
      scr[cy][cx] = ' ';
      dirty = true;
      return;
    case 7: con_bell(); return;
  }
  if ((uint8_t)c < 32 || (uint8_t)c >= 127) return;
  scr[cy][cx] = c;
  dirty = true;
  if (++cx >= COLS) newline();
}

void con_puts(const char* s) { while (*s) con_putc(*s++); }
int con_col() { return cx; }
int con_width() { return COLS; }

void con_home() {
  for (int r = winTop; r < ROWS; r++) memset(scr[r], ' ', COLS);
  cx = 0;
  cy = winTop;
  dirty = true;
}

void con_clreol() {
  memset(&scr[cy][cx], ' ', COLS - cx);
  dirty = true;
}

void con_clreos() {
  con_clreol();
  for (int r = cy + 1; r < ROWS; r++) memset(scr[r], ' ', COLS);
}

// Apple の 24 行を 8 行に対応させる。GR モードでは VTAB 22..24 が下 3 行。
void con_vtab(int row) {
  int r = grMode ? GR_TEXT_TOP + (row - 22) : row - 1;
  if (r < winTop) r = winTop;
  if (r > ROWS - 1) r = ROWS - 1;
  cy = r;
  dirty = true;
}

void con_htab(int col) {
  cx = col - 1;
  if (cx < 0) cx = 0;
  if (cx > COLS - 1) cx = COLS - 1;
}

void con_bell() {
  if (oledOk) oled.invertDisplay(true);
  if (PIN_SPEAKER >= 0) {
    for (int i = 0; i < 100; i++) {                  // 1kHz を 0.1 秒
      digitalWrite(PIN_SPEAKER, HIGH);
      delayMicroseconds(500);
      digitalWrite(PIN_SPEAKER, LOW);
      delayMicroseconds(500);
    }
  } else {
    delay(100);
  }
  if (oledOk) oled.invertDisplay(false);
}

// ---------------------------------------------------------------------------
// キー入力

void con_push_key(uint8_t c) { queue_try_add(&keyq, &c); }

int con_getkey() {
  uint8_t c;
  cursorOn = blinkOn = dirty = true;
  lastBlink = millis();
  while (!queue_try_remove(&keyq, &c)) con_idle();
  cursorOn = false;
  dirty = true;
  return c;
}

int con_peekkey() {
  uint8_t c;
  return queue_try_peek(&keyq, &c) ? c : -1;
}

int con_pollkey() {
  uint8_t c;
  return queue_try_remove(&keyq, &c) ? c : -1;
}

// ---------------------------------------------------------------------------
// 低解像度グラフィックス

void gr_mode(bool on) {
  grMode = on;
  winTop = on ? GR_TEXT_TOP : 0;
  if (cy < winTop) { cy = ROWS - 1; cx = 0; }
  dirty = true;
}

void gr_clear() {
  memset(grbuf, 0, sizeof grbuf);
  dirty = true;
}

void gr_plot(int x, int y, int color) {
  grbuf[y][x] = (uint8_t)color;
  if (grMode && y < GR_ROWS) dirty = true;
}

int gr_scrn(int x, int y) { return grbuf[y][x]; }

// ---------------------------------------------------------------------------
// その他のハードウェア

int hw_pdl(int n) {
  if (n < 0 || n > 2) return 0;
  return analogRead(A0 + n) >> 2;                    // 10 ビット → 0..255
}

int hw_button(int n) {
  int pin = n == 0 ? PIN_BUTTON0 : PIN_BUTTON1;
  return digitalRead(pin) == LOW;
}

void hw_speaker() {
  static bool s = false;
  if (PIN_SPEAKER < 0) return;
  s = !s;
  digitalWrite(PIN_SPEAKER, s);
}

uint32_t hw_random() { return rp2040.hwrand32(); }

// ---------------------------------------------------------------------------
// LittleFS
// Arduino IDE の「ツール → Flash Size」で FS 領域を確保しておく必要がある。

static void makePath(const char* name, char* out, size_t n) {
  snprintf(out, n, "/%s.BAS", name);
}

bool fs_open_write(const char* name) {
  if (!fsOk) return false;
  char p[40];
  makePath(name, p, sizeof p);
  fsFile = LittleFS.open(p, "w");
  return (bool)fsFile;
}

void fs_write_line(const char* s) {
  fsFile.print(s);
  fsFile.print('\n');
}

bool fs_open_read(const char* name) {
  if (!fsOk) return false;
  char p[40];
  makePath(name, p, sizeof p);
  fsFile = LittleFS.open(p, "r");
  return (bool)fsFile;
}

bool fs_read_line(char* buf, int max) {
  if (!fsFile || !fsFile.available()) return false;
  int n = 0;
  while (fsFile.available()) {
    int c = fsFile.read();
    if (c == '\n') break;
    if (c == '\r') continue;
    if (n < max - 1) buf[n++] = (char)c;
  }
  buf[n] = 0;
  return true;
}

void fs_close() {
  if (fsFile) fsFile.close();
}

void fs_catalog() {
  if (!fsOk) {
    con_puts("NO FILE SYSTEM\n");
    return;
  }
  Dir d = LittleFS.openDir("/");
  while (d.next()) {
    String n = d.fileName();
    if (n.startsWith("/")) n.remove(0, 1);
    if (!n.endsWith(".BAS")) continue;
    n.remove(n.length() - 4);
    con_puts(n.c_str());
    con_putc(' ');
    char b[12];
    snprintf(b, sizeof b, "%u", (unsigned)d.fileSize());
    con_puts(b);
    con_putc('\n');
  }
}
