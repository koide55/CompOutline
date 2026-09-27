# Pico Integer BASIC

Raspberry Pi Pico 2 W で動く、Apple II の **Integer BASIC**（ROM 6KB に入っていた Wozniak の BASIC）相当のインタプリタ。

- 入力: USB キーボード（PIO-USB で GP0/GP1 を USB ホストにする）
- 表示: SSD1306 128x64 OLED（I2C）に 21 桁 x 8 行
- 保存: 内蔵フラッシュ（LittleFS）に `SAVE` / `LOAD`
- USB シリアル (Micro-B) にも同じ内容を出力し、そこからの入力も受け付ける

## 配線

```
Pico 2 W                 USB-A メス (キーボード)
VBUS (pin 40) ─────────── VBUS
GP0  (pin 1)  ─────────── D+
GP1  (pin 2)  ─────────── D-
GND  (pin 3)  ─────────── GND

Pico 2 W                 SSD1306 OLED
3V3  (pin 36) ─────────── VCC
GND  (pin 38) ─────────── GND
GP4  (pin 6)  ─────────── SDA
GP5  (pin 7)  ─────────── SCL

任意: GP15 ── 圧電スピーカー ── GND
      GP14 / GP13 ── ボタン ── GND（PEEK(-16287) / PEEK(-16286)）
      GP26..28 ── 可変抵抗（PDL(0..2)）
```

電源は Micro-B（PC か USB 充電器）から入れる。キーボードへの 5V は VBUS ピンから出る。
ピンは `PicoIntegerBasic/config.h` で変えられる。

## ビルド（Arduino IDE）

1. ボードマネージャで **Raspberry Pi Pico/RP2040/RP2350**（earlephilhower 版）を入れる
2. ライブラリマネージャで次の 3 つを入れる
   - **Pico PIO USB**
   - **Adafruit SSD1306**（Adafruit GFX Library も一緒に入る）
   - Adafruit TinyUSB Library はボードパッケージに同梱されている
3. 「ツール」メニューを次のように設定する

   | 項目 | 設定 |
   | --- | --- |
   | ボード | Raspberry Pi Pico 2W |
   | CPU Speed | **120 MHz** または **240 MHz**（PIO-USB は 12MHz の倍数でないと動かない） |
   | USB Stack | **Adafruit TinyUSB** |
   | Flash Size | FS 領域のあるもの（例: 4MB (Sketch: 3MB, FS: 1MB)） |

4. `PicoIntegerBasic/PicoIntegerBasic.ino` を開いて書き込む

CPU Speed が合っていないと、起動時に `USB HOST: SET CPU SPEED TO 120/240MHZ` と表示される。

キーボード配列は `config.h` の `KEYBOARD_JIS`（1 = JIS、0 = US）で切り替える。

## 使い方

プロンプトは `>`。行番号を付けて入力すると行を格納し、行番号だけを入力するとその行を消す。

```
>10 FOR I=1 TO 5
>20 PRINT I*I
>30 NEXT I
>40 END
>RUN
```

| キー | 働き |
| --- | --- |
| Enter | 1 行を確定 |
| ← / BackSpace | 1 文字消す |
| Ctrl-X | 入力中の行を取り消す |
| Ctrl-C | 実行を止める（`CON` で続きから再開） |
| LIST 中に任意のキー | 一時停止（もう一度押すと再開） |

`examples/` のプログラムは、PC の端末ソフト（115200bps）から USB シリアルに貼り付ければ入力できる。

## 言語仕様

### 数値と演算

- 数値は 16 ビット整数 -32767..32767。範囲を超えると `*** >32767 ERR`
- 演算子（優先順位の高い順）
  1. 単項 `-` `+` `NOT`
  2. `^`
  3. `*` `/` `MOD`
  4. `+` `-`
  5. `=` `#` `<>` `<` `>` `<=` `>=`（真は 1、偽は 0）
  6. `AND`
  7. `OR`
- 変数名は英字で始まる英数字。先頭 16 文字まで区別する

### 文字列

- `DIM A$(n)` で最大長 n（1..255）を決める。DIM しなければ 255
- `A$(i,j)` は i 文字目から j 文字目まで、`A$(i)` は i 文字目から最後まで
- 連結の演算子はない。`A$(LEN(A$)+1)=B$` で後ろに付け足す
- 比較は `=` `#` `<>` `<` `>` `<=` `>=`

### 文

| 文 | 例 |
| --- | --- |
| `LET`（省略可） | `A=1` / `A$="HI"` / `B(3)=5` |
| `PRINT` | `PRINT "X=";X,Y;`（`,` は 8 桁ごとのタブ、末尾 `;` で改行しない） |
| `INPUT` | `INPUT A,B` / `INPUT "NAME? ",N$` |
| `IF ... THEN` | `IF A>0 THEN 100` / `IF A$="Y" THEN PRINT "OK"` |
| `GOTO` / `GOSUB` / `RETURN` / `POP` | `GOTO N*10`（計算した行番号でもよい） |
| `FOR` / `NEXT` | `FOR I=10 TO 1 STEP -1` … `NEXT I` |
| `DIM` | `DIM A(100), S$(40)` |
| `REM` / `END` | Integer BASIC ではプログラムの最後に `END` が必要（ないと `NO END ERR`） |
| `TAB n` / `VTAB n` | カーソル移動（VTAB は Apple の 1..24 行を 8 行に対応させる） |
| `POKE` / `CALL` | `CALL -936` で画面消去（下表） |
| `GR` / `TEXT` / `COLOR=` / `PLOT` / `HLIN` / `VLIN` | 低解像度グラフィックス（下記） |
| `HIMEM:` / `LOMEM:` | 受け付けるが何もしない |

**Integer BASIC 特有の IF**: 条件が偽のとき飛ばすのは `THEN` の直後の 1 文だけ。
同じ行の `:` 以降の文は条件によらず実行される。

```
10 IF 0 THEN PRINT "A": PRINT "B"     ← "B" は表示される
```

### 関数

`ABS(x)` `SGN(x)` `RND(n)`（0..n-1） `LEN(A$)` `ASC(A$)` `PEEK(a)` `SCRN(x,y)` `PDL(n)`

`ASC` は Apple II と同じく最上位ビットが立った値を返す（`ASC("A")` は 193）。

### コマンド

`RUN [行]` `LIST [a[,b]]` `NEW` `CLR` `DEL a[,b]` `AUTO [a[,b]]`（空行で終了） `MAN` `CON`

追加コマンド（本物にはない）: `SAVE ["名前"]` `LOAD ["名前"]` `CATALOG`
名前を省略すると `PROGRAM`。

### グラフィックス

`GR` で 40x40 の低解像度画面（1 ブロック = 2x1 ドット）になり、下 3 行がテキストになる。
単色なので `COLOR=0` が黒、1..15 が白。`SCRN(x,y)` は設定した色番号を返す。
座標は 0..39（y は 47 まで書けるが表示されない）。

### 再現している Apple II のアドレス

| アドレス | 働き |
| --- | --- |
| `PEEK(-16384)` | キー入力。押されていれば 128 以上（文字コード + 128） |
| `POKE -16368,0` | キー入力のフラグを消す（キーを読み捨てる） |
| `PEEK(-16336)` | スピーカーをクリック |
| `PEEK(-16287)` / `PEEK(-16286)` | ボタン 0 / 1（押されていれば 128 以上） |
| `PEEK(36)` / `POKE 36,n` | カーソルの桁 |
| `POKE -16304,0` / `POKE -16303,0` | GR / TEXT |
| `CALL -936` | 画面消去（HOME） |
| `CALL -958` / `CALL -868` | 画面末まで / 行末まで消去 |
| `CALL -198` | ベル |
| `CALL -1998` | GR 画面の消去 |

これ以外のアドレスは 64KB の作業用メモリとして読み書きできる。

### エラーメッセージ

`SYNTAX` `RANGE` `>32767` `BAD BRANCH` `BAD RETURN` `BAD NEXT` `16 GOSUBS` `16 FORS`
`DIM` `STR OVFL` `NO END` `MEM FULL` `FILE`（`*** SYNTAX ERR` のように表示し、実行中なら `STOPPED AT 行番号` を続ける）

### 本物との違い

- 画面は 21 桁 x 8 行（本物は 40 x 24）
- 構文の誤りは実行したときに見つける（本物は行を入力したときに見つける）
- DIM していない配列は添字 0..10 で自動的に作る
- 入力は大文字に変換される（Apple II と同じく英小文字はない）
- 画面上のカーソル移動による行編集（ESC 系）はない

## PC 上で試す

インタプリタ本体 (`basic.cpp`) は `console.h` の関数だけに依存しているので、PC でもビルドできる。

```sh
cd test
make          # ./basic で対話的に動く（Ctrl-D で終了）
make test     # programs/*.in を流して programs/*.out と比べる
```

## ファイル構成

| ファイル | 内容 |
| --- | --- |
| `PicoIntegerBasic/basic.cpp` | インタプリタ本体（ハードウェア非依存） |
| `PicoIntegerBasic/console.h` | インタプリタと入出力の境界 |
| `PicoIntegerBasic/console_pico.cpp` | OLED・キー入力・LittleFS の実装 |
| `PicoIntegerBasic/usb_keyboard.cpp` | PIO-USB + TinyUSB による USB キーボード（コア1） |
| `PicoIntegerBasic/main.cpp` | 起動処理 |
| `PicoIntegerBasic/config.h` | ピン配置・キーボード配列 |
| `examples/` | サンプルプログラム |
| `test/` | PC 用のコンソール実装とテスト |
