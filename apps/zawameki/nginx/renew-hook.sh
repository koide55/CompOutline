#!/bin/sh
# certbot が証明書を更新したあとに nginx コンテナへ読み直させる。
#
#   sudo install -m 755 renew-hook.sh /etc/letsencrypt/renewal-hooks/deploy/zawameki.sh
#
# ZAWAMEKI_DIR は apps/zawameki を置いた場所に合わせる。
ZAWAMEKI_DIR=${ZAWAMEKI_DIR:-/opt/zawameki}
cd "$ZAWAMEKI_DIR" && docker compose -f docker-compose.yml -f docker-compose.https.yml exec -T nginx nginx -s reload
