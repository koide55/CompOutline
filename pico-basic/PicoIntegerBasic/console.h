// console.h — インタプリタから見た入出力の抽象化
//
// basic.cpp はこのインタフェースだけに依存する。実機では console_pico.cpp が
// OLED・USB キーボード・LittleFS で実装し、PC 上のテストでは
// test/host_console.cpp が標準入出力で実装する。
#pragma once
#include <stdint.h>

// ---- テキスト画面 ----
void con_init();
void con_putc(char c);        // '\n' で改行、'\b' で 1 文字消去、7 でベル
void con_puts(const char* s);
int  con_col();               // 現在のカーソル桁 (0 始まり)
int  con_width();             // 1 行の文字数
void con_home();              // テキストウィンドウを消去してカーソルを左上へ
void con_clreol();            // カーソルから行末まで消去
void con_clreos();            // カーソルから画面末まで消去
void con_vtab(int row);       // Apple の行番号 1..24 を画面の行に対応させる
void con_htab(int col);       // 1 始まりの桁
void con_bell();

// ---- キー入力 (文字コードは ASCII、Enter は '\r'、Ctrl-C は 3) ----
int  con_getkey();            // 押されるまで待つ（待つ間カーソルを点滅）
int  con_peekkey();           // 取り出さずに先頭を見る。なければ -1
int  con_pollkey();           // 取り出す。なければ -1
void con_push_key(uint8_t c); // キーボード側からキューへ入れる（別コアから呼んでよい）

// 画面更新・シリアル入力の取り込みなど。インタプリタが 1 文ごとに呼ぶ。
void con_idle();

// ---- 低解像度グラフィックス (40x48、下部はテキスト 3 行) ----
void gr_mode(bool on);
void gr_clear();
void gr_plot(int x, int y, int color);
int  gr_scrn(int x, int y);

// ---- その他のハードウェア ----
int      hw_pdl(int n);       // 0..255
int      hw_button(int n);    // 押されていれば 1
void     hw_speaker();        // スピーカーを 1 回クリック
uint32_t hw_random();

// ---- プログラムの保存 ----
bool fs_open_write(const char* name);
void fs_write_line(const char* s);
bool fs_open_read(const char* name);
bool fs_read_line(char* buf, int max);
void fs_close();              // 開いていなくても呼んでよい
void fs_catalog();
