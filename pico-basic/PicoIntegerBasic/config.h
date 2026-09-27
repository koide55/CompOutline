// config.h — ピン配置と動作設定
#pragma once

// ---- USB ホスト (PIO-USB) ----
// D+ を GP0、D- を GP1 に接続する（D- は必ず D+ の次の番号）。
#define PIN_USB_HOST_DP 0

// キーボード配列: 1 = JIS (日本語配列), 0 = US 配列
#define KEYBOARD_JIS 1

// ---- OLED (SSD1306 128x64, I2C0) ----
#define PIN_OLED_SDA 4
#define PIN_OLED_SCL 5
#define OLED_ADDR 0x3C

// 画面の最短更新間隔 [ms]。I2C 400kHz で 1 フレーム約 25ms かかる。
#define REFRESH_MS 33

// ---- 任意の周辺機器（つながなくても動く） ----
// 圧電スピーカー: ベル音と POKE -16336 (スピーカー) に使う。-1 で無効。
#define PIN_SPEAKER 15
// プッシュボタン (GND に落とすと押下): PEEK(-16287), PEEK(-16286)
#define PIN_BUTTON0 14
#define PIN_BUTTON1 13
// パドル PDL(0..2) は ADC0..2 (GP26..GP28) を 0..255 で読む。
