#!/bin/bash
# pptx を PowerPoint で開いて PDF に書き出し、1枚ずつの画像にする。
#
#   slides/tools/render.sh 第01回_計算とは何か.pptx
#
# PowerPoint は同じパスのファイルをメモリ上に残していることがあり、
# 作り直した pptx を開いても古い内容を書き出してしまう。
# そのため毎回一意な名前に複製してから開く。
#
# 先生が開いている書類には触れない。開いた複製だけを閉じる。
set -euo pipefail

SLIDES="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$SLIDES/${1:?pptx のファイル名を渡すこと}"
[ -f "$SRC" ] || { echo "見つからない: $SRC" >&2; exit 1; }

BASE="$(basename "${SRC%.pptx}")"
STAMP="$(date +%H%M%S)"
TMP="$SLIDES/.render-$STAMP.pptx"
PDF="$SLIDES/.render-$STAMP.pdf"
OUT="${2:-$SLIDES/preview/$BASE}"

cp "$SRC" "$TMP"
mkdir -p "$(dirname "$OUT")"

osascript <<EOF >/dev/null
set hfs to (POSIX file "$PDF") as text
tell application "Microsoft PowerPoint"
  open POSIX file "$TMP"
  delay 2
  set p to active presentation
  save p in hfs as save as PDF
  delay 3
  close p saving no
end tell
EOF

rm -f "$TMP"
[ -f "$PDF" ] || { echo "PDF が作られなかった" >&2; exit 1; }

rm -f "$OUT"-*.jpg
pdftoppm -jpeg -r 110 "$PDF" "$OUT"
rm -f "$PDF"
echo "$(ls "$OUT"-*.jpg | wc -l | tr -d ' ') 枚を $OUT-NN.jpg に書き出した"
