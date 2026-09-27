// usb_keyboard.cpp — PIO-USB で USB キーボードを読む（コア1 で動かす）
//
// TinyUSB のホスト機能を PIO-USB (GP0=D+, GP1=D-) の上で動かし、
// HID ブートプロトコルのキーボードレポートを ASCII に変換してキューに積む。
// キーを押し続けたときのリピートもここで作る。
#include <Arduino.h>
#include <hardware/clocks.h>

#include "pio_usb.h"
#include "Adafruit_TinyUSB.h"

#include "config.h"
#include "console.h"

static Adafruit_USBH_Host USBHost;

static uint8_t prevKeys[6];
static uint8_t repKey = 0, repMod = 0;
static bool repActive = false;
static uint32_t repTime = 0;

#define REPEAT_DELAY_MS 500
#define REPEAT_RATE_MS 50

bool usbkbd_begin() {
  // PIO-USB はシステムクロックが 12MHz の倍数 (120 / 240MHz) でないと動かない
  if (clock_get_hz(clk_sys) % 12000000UL) return false;

  pio_usb_configuration_t pio_cfg = PIO_USB_DEFAULT_CONFIG;
  pio_cfg.pin_dp = PIN_USB_HOST_DP;
#if defined(ARDUINO_RASPBERRY_PI_PICO_W) || defined(ARDUINO_RASPBERRY_PI_PICO_2W)
  // Pico W 系は無線チップ (CYW43) との通信にも PIO と DMA を使うので、ぶつからない割り当てにする
  pio_cfg.sm_tx = 3;
  pio_cfg.sm_rx = 2;
  pio_cfg.sm_eop = 3;
  pio_cfg.pio_rx_num = 0;
  pio_cfg.pio_tx_num = 1;
  pio_cfg.tx_ch = 9;
#endif
  USBHost.configure_pio_usb(1, &pio_cfg);
  USBHost.begin(1);
  return true;
}

// ---------------------------------------------------------------------------
// キーコード → ASCII

static const uint8_t keymapUS[128][2] = { HID_KEYCODE_TO_ASCII };

#if KEYBOARD_JIS
// JIS 配列で US 配列と文字が違うキーだけを上書きする { キーコード, 通常, Shift }
struct JisKey { uint8_t kc; char normal, shifted; };
static const JisKey jisKeys[] = {
  { 0x1F, '2', '"' },  { 0x23, '6', '&' },  { 0x24, '7', '\'' },
  { 0x25, '8', '(' },  { 0x26, '9', ')' },  { 0x27, '0', 0 },
  { 0x2D, '-', '=' },  { 0x2E, '^', '~' },  { 0x2F, '@', '`' },
  { 0x30, '[', '{' },  { 0x31, ']', '}' },  { 0x32, ']', '}' },
  { 0x33, ';', '+' },  { 0x34, ':', '*' },  { 0x35, 0, 0 },     // 0x35 = 半角/全角
  { 0x87, '\\', '_' }, { 0x89, '\\', '|' },                     // ろ, ¥
};
#endif

static int keyToAscii(uint8_t kc, uint8_t mod) {
  bool shift = mod & (KEYBOARD_MODIFIER_LEFTSHIFT | KEYBOARD_MODIFIER_RIGHTSHIFT);
  bool ctrl = mod & (KEYBOARD_MODIFIER_LEFTCTRL | KEYBOARD_MODIFIER_RIGHTCTRL);

  switch (kc) {
    case HID_KEY_ENTER:
    case HID_KEY_KEYPAD_ENTER: return '\r';
    case HID_KEY_BACKSPACE:
    case HID_KEY_ARROW_LEFT: return 8;               // Apple II の ← は BS
    case HID_KEY_DELETE: return 0x7F;
    case HID_KEY_ESCAPE: return 27;
    case HID_KEY_ARROW_RIGHT: return 0x15;
    case HID_KEY_ARROW_UP: return 0x0B;
    case HID_KEY_ARROW_DOWN: return 0x0A;
  }

  int c = 0;
  bool found = false;
#if KEYBOARD_JIS
  for (const JisKey& j : jisKeys)
    if (j.kc == kc) { c = shift ? j.shifted : j.normal; found = true; break; }
#endif
  if (!found) {
    if (kc >= 128) return 0;
    c = keymapUS[kc][shift ? 1 : 0];
  }
  if (!c) return 0;

  if (ctrl) {                                         // Ctrl-A..Z → 1..26
    if (c >= 'a' && c <= 'z') return c - 'a' + 1;
    if (c >= 'A' && c <= 'Z') return c - 'A' + 1;
    return 0;
  }
  return c;
}

static bool contains(const uint8_t* keys, uint8_t kc) {
  for (int i = 0; i < 6; i++) if (keys[i] == kc) return true;
  return false;
}

static void handleKeyboard(const hid_keyboard_report_t* r) {
  for (int i = 0; i < 6; i++) {                       // 新しく押されたキー
    uint8_t kc = r->keycode[i];
    if (kc < 4 || contains(prevKeys, kc)) continue;   // 0..3 はエラー/ロールオーバー
    int a = keyToAscii(kc, r->modifier);
    if (a <= 0) continue;
    con_push_key((uint8_t)a);
    repKey = kc;
    repActive = true;
    repTime = millis() + REPEAT_DELAY_MS;
  }
  if (repActive && !contains(r->keycode, repKey)) repActive = false;
  repMod = r->modifier;
  memcpy(prevKeys, r->keycode, 6);
}

void usbkbd_task() {
  USBHost.task();
  if (repActive && (int32_t)(millis() - repTime) >= 0) {
    int a = keyToAscii(repKey, repMod);
    if (a > 0) con_push_key((uint8_t)a);
    repTime = millis() + REPEAT_RATE_MS;
  }
}

// ---------------------------------------------------------------------------
// TinyUSB のコールバック（コア1 の USBHost.task() から呼ばれる）

extern "C" {

void tuh_hid_mount_cb(uint8_t dev_addr, uint8_t instance, uint8_t const* desc_report,
                      uint16_t desc_len) {
  (void)desc_report;
  (void)desc_len;
  if (tuh_hid_interface_protocol(dev_addr, instance) == HID_ITF_PROTOCOL_KEYBOARD)
    tuh_hid_receive_report(dev_addr, instance);
}

void tuh_hid_umount_cb(uint8_t dev_addr, uint8_t instance) {
  (void)dev_addr;
  (void)instance;
  memset(prevKeys, 0, sizeof prevKeys);
  repActive = false;
}

void tuh_hid_report_received_cb(uint8_t dev_addr, uint8_t instance, uint8_t const* report,
                                uint16_t len) {
  if (tuh_hid_interface_protocol(dev_addr, instance) == HID_ITF_PROTOCOL_KEYBOARD &&
      len >= sizeof(hid_keyboard_report_t))
    handleKeyboard((const hid_keyboard_report_t*)report);
  tuh_hid_receive_report(dev_addr, instance);
}

}  // extern "C"
