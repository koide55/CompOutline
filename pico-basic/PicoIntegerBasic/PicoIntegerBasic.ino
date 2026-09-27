// PicoIntegerBasic — Raspberry Pi Pico 2 W で動く Apple II Integer BASIC 相当のインタプリタ
//
//   コア0: BASIC インタプリタ + OLED 表示 (console_pico.cpp, basic.cpp)
//   コア1: PIO-USB による USB キーボードのホスト処理 (usb_keyboard.cpp)
//
// ビルド設定 (Arduino IDE、earlephilhower 版 Raspberry Pi Pico/RP2040/RP2350 コア)
//   ボード       : Raspberry Pi Pico 2W
//   CPU Speed    : 120 MHz または 240 MHz（PIO-USB は 12MHz の倍数が必要）
//   USB Stack    : Adafruit TinyUSB
//   Flash Size   : FS 領域ありのもの (例: 4MB (Sketch: 2MB, FS: 2MB))
// 必要なライブラリ: Pico PIO USB, Adafruit SSD1306, Adafruit GFX Library
//
// 処理の本体は main.cpp（.ino に関数を置かないのは、IDE による
// プロトタイプ自動生成の影響を受けないようにするため）。
