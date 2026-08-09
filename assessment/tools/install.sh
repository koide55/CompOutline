#!/bin/bash
# シナリオを arena に配置する。
#
#   assessment/tools/install.sh [arena のパス]
#
# 既定の配置先は ~/Documents/Playground/cyber-social-implementation-arena。
# シナリオ以外のファイルには触れない。
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$HERE/../scenarios"
ARENA="${1:-$HOME/Documents/Playground/cyber-social-implementation-arena}"
DST="$ARENA/webarena/data/scenarios"

[ -d "$DST" ] || { echo "arena が見つからない: $DST" >&2
                   echo "第1引数で arena のパスを指定してください" >&2; exit 1; }

n=0
for f in "$SRC"/*.json; do
  [ -e "$f" ] || continue
  # 配置名は scenario_id に合わせる。arena は id で読むため
  id=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1]))['scenario_id'])" "$f")
  cp "$f" "$DST/$id.json"
  echo "  $(basename "$f")  →  $id.json"
  n=$((n + 1))
done
echo "$n 本を配置した: $DST"

cat <<'EOF'

まだ手で行う必要があるもの:
  - arena を再起動して、シナリオが読み込まれることを確認する
  - 講義用のカテゴリを作る場合は webarena/data/categories.json に追記する
      {"id": "lecture", "label": "講義理解度確認", "order": 5}
    追記したら scenarios/*.json の category も合わせて変更すること
    （現状は既存の "education" を使っている）
EOF
