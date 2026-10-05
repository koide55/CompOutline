#!/bin/sh
# 教員パスワード（/teacher の Basic 認証）を設定し直す。
#
#   sudo sh tools/reset-password.sh            … 新しいパスワードを作る（英数字16字）
#   sudo sh tools/reset-password.sh 'MyPass1'  … 指定したパスワードにする
#
# .env を書き換え、コンテナを作り直し、新しいパスワードで実際に入れることを確かめる。
set -eu
cd "$(dirname "$0")/.."

PW=${1:-$(openssl rand -hex 8)}
# 記号は .env や sed で崩れることがあるので、英数字と . _ - に限る
case "$PW" in
  ''|*[!A-Za-z0-9._-]*) echo "パスワードに使えるのは英数字と . _ - だけです" >&2; exit 1 ;;
esac

[ -f .env ] || cp .env.example .env
if grep -q '^ZAWAMEKI_TEACHER_PASSWORD=' .env; then
  sed -i "s/^ZAWAMEKI_TEACHER_PASSWORD=.*/ZAWAMEKI_TEACHER_PASSWORD=$PW/" .env
else
  echo "ZAWAMEKI_TEACHER_PASSWORD=$PW" >> .env
fi
USER_NAME=$(sed -n 's/^ZAWAMEKI_TEACHER_USER=//p' .env)
USER_NAME=${USER_NAME:-teacher}

# 動いているコンテナが使った compose ファイル（Caddy 用・nginx 用の重ね方）をそのまま使う
FILES=""
USED=$(docker inspect zawameki-zawameki-1 --format '{{ index .Config.Labels "com.docker.compose.project.config_files" }}' 2>/dev/null || true)
if [ -n "$USED" ]; then
  for f in $(echo "$USED" | tr ',' ' '); do FILES="$FILES -f $f"; done
else
  FILES="-f docker-compose.yml -f docker-compose.caddy.yml"
fi

echo "コンテナを作り直します（$FILES）"
# shellcheck disable=SC2086
docker compose $FILES up -d --force-recreate zawameki

# 新しいパスワードで入れるか、コンテナの中から確かめる（Caddy・nginx を通さない）
i=0
until docker compose $FILES exec -T zawameki python -c '
import base64, sys, urllib.request
req = urllib.request.Request("http://127.0.0.1:8100/api/teacher/rooms",
    headers={"Authorization": "Basic " + base64.b64encode(sys.argv[1].encode()).decode()})
urllib.request.urlopen(req, timeout=3)
' "$USER_NAME:$PW" 2>/dev/null; do
  i=$((i + 1))
  if [ "$i" -ge 30 ]; then
    echo "✗ 新しいパスワードで入れませんでした。docker compose $FILES logs zawameki を見てください" >&2
    exit 1
  fi
  sleep 1
done

echo
echo "✓ 設定しました"
echo "  ユーザー名: $USER_NAME"
echo "  パスワード: $PW"
echo
echo "ブラウザが古いパスワードを覚えていることがあります。"
echo "入れないときは、ブラウザをいったん全部閉じるか、シークレットウィンドウで開いてください。"
