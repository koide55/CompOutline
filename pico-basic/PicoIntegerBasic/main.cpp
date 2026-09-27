// main.cpp — 起動処理と 2 つのコアへの仕事の割り当て
#include <Arduino.h>
#include "Adafruit_TinyUSB.h"

#include "basic.h"
#include "config.h"
#include "console.h"

bool usbkbd_begin();
void usbkbd_task();

static volatile bool consoleReady = false;
static volatile int usbState = 0;  // 0: 準備中, 1: 動作中, 2: クロック設定が合わない

void setup() {
  con_init();
  consoleReady = true;

  uint32_t t0 = millis();
  while (usbState == 0 && millis() - t0 < 2000) con_idle();
  if (usbState == 2) con_puts("USB HOST: SET CPU\nSPEED TO 120/240MHZ\n");
}

void loop() {
  basic_main();  // 戻らない
}

void setup1() {
  while (!consoleReady) delay(1);  // キーキューができるまで待つ
  usbState = usbkbd_begin() ? 1 : 2;
}

void loop1() {
  if (usbState == 1) usbkbd_task();
}
