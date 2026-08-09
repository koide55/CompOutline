#!/bin/bash
# 図の SVG を PowerPoint に貼れる PNG にする。
#
#   slides/tools/figs2png.sh 01        # 第1回の図だけ
#   slides/tools/figs2png.sh           # 全部
#
# SVG のまま貼ると PowerPoint が確実に描いてくれないので、3倍解像度の PNG にする。
# 変換のときだけ font-family を差し替えるのは、cairosvg が <style> 内の
# font-family のフォールバックをたどらず日本語が豆腐になるため。
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VENV="${VENV:-$ROOT/.venv/bin/python}"
[ -x "$VENV" ] || { echo "cairosvg の入った python が要る: $VENV" >&2
                    echo "  python3 -m venv .venv && .venv/bin/pip install cairosvg pillow" >&2; exit 1; }

PAT="${1:-}"
GLOB="fig-*.svg"
[ -n "$PAT" ] && GLOB="fig-$PAT-*.svg"

mkdir -p "$ROOT/slides/png"
"$VENV" - "$ROOT" "$GLOB" <<'PY'
import cairosvg, glob, os, re, sys
root, pat = sys.argv[1], sys.argv[2]
n = 0
for p in sorted(glob.glob(os.path.join(root, 'figures', pat))):
    s = open(p, encoding='utf-8').read()
    s = re.sub(r'font-family:[^;}]*;?', '', s)
    s = s.replace('<svg ', '<svg font-family="Arial Unicode MS" ', 1)
    out = os.path.join(root, 'slides', 'png', os.path.basename(p)[:-4] + '.png')
    cairosvg.svg2png(bytestring=s.encode(), write_to=out, scale=3.0)
    n += 1
print(f'{n} 点を slides/png/ に書き出した')
PY
