# ざわめき（Zawameki）

講義中の理解度・コメント・質問を、リアルタイムに教員へ届ける Web アプリ。
設計は [SPEC.md](SPEC.md)。

学生はスマホで QR を読み、学生番号を入れて入室する。
**学生番号は出席の記録にだけ使い、迷子ボタン・投稿とは結びつけない**（匿名で発言できる）。

## 何ができるか

| 学生（スマホ） | 教員（操作画面） | 投影画面 |
| --- | --- | --- |
| 😵 迷子（90秒で消える）／💡 わかった！ | 教室の天気・迷子率の線・ペースの綱引き | 入室 QR と部屋コード |
| 🐢 遅くして／🐇 速くてよい | 質問・意見を「同じく」の多い順に。答えた／あとで／隠す | 質問・意見ボード（上位6件） |
| 投稿は4種類: 💬 コメント／❓ 質問／📣 ご意見申す／🔰 素人質問ですが | コメントの流れ。隠す・受付を止める・間隔を変える | 流れるコメント |
| 質問・意見に「同じく」「同感」 | スライド番号の手送り（← →）、投影の切り替え | 説明が効いたら花火 |
| 学生番号を添えるかは1回ごとに選べる（教員にだけ見える） | 講義後の「迷子の地図」と CSV／Markdown 書き出し | |

| 種類 | 字数 | 送れる間隔 | 「同じく」 |
| --- | ---: | --- | --- |
| 💬 コメント | 80 | 教員が決める（既定10秒）。止めることもできる | なし（流れるだけ） |
| ❓ 質問 | 200 | 質問・意見あわせて30秒に1件 | 同じく |
| 📣 ご意見申す | 200 | 〃 | 同感 |
| 🔰 素人質問ですが | 200 | 〃 | 同じく。投影では「素人質問で恐縮ですが、」を添えて出す |

## 動かす（arena.koidelab.net の別ポート）

arena とは別のコンテナとして、ポート **8100** で動かす。
**arena.koidelab.net では、arena の Caddy に HTTPS を任せる**（次の節）。ファイアウォールで 8100/tcp を開けておくこと（AWS の EC2 なら、インスタンスのセキュリティグループのインバウンドルールに 8100/tcp を足す）。
教員の入口（`/teacher`）は Basic 認証で守ってある。

教員パスワードを設定し直すときは、`sudo sh tools/reset-password.sh`（自動で作る）か
`sudo sh tools/reset-password.sh 'パスワード'`（指定する）。`.env` を書き換え、コンテナを作り直し、
新しいパスワードで入れることまで確かめる。

### 講義の流れ

1. `/teacher` で部屋を開く → 操作画面に移る
2. 「📽 投影画面を開く」を教室の PC で開き、`f` キーで全画面にする。学生に QR を読ませる
3. 話しながら操作画面を見る。スライドを送ったら ◀ ▶（または ← →）で番号を合わせる
4. 区切りで投影を「質問・意見」に切り替えて答える。答えたら「✓ 答えた」
5. 終わったら「部屋を閉じる」→ 迷子の地図が出る

部屋は4時間たつと自動で閉じる（`ZAWAMEKI_ROOM_HOURS`）。

## arena.koidelab.net で動かす（arena の Caddy に HTTPS を任せる）

arena.koidelab.net では、arena の **Caddy**（コンテナ `cyber-arena-caddy-1`）が 80・443 番を持ち、
Let's Encrypt の証明書を取って更新している。証明書はポートではなくホスト名に付くので、
**Caddy に「8100 番で受けて、ざわめきへ渡す」設定を足すだけでよい**。certbot も nginx も要らない。

```
 学生のスマホ ── https://arena.koidelab.net:8100 ──▶ Caddy（arena と共用）──▶ zawameki（arena の Docker ネットワーク内だけ）
```

> **certbot の `--standalone` は使わないこと。** 80 番を空けるために Caddy を止めることになり、
> そのあいだ arena も止まる。証明書は Caddy がすでに持っている。

### 1. Caddy の置き場所とネットワークを調べる

```bash
# arena の compose を置いたディレクトリ（ここに Caddyfile と docker-compose.yml がある）
sudo docker inspect cyber-arena-caddy-1 --format '{{ index .Config.Labels "com.docker.compose.project.working_dir" }}'
# Caddyfile のホスト側の場所と、証明書の置き場（/data）がボリュームになっているか
sudo docker inspect cyber-arena-caddy-1 --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{println}}{{end}}'
# Caddy がつながっている Docker ネットワーク（ふつうは cyber-arena_default）
sudo docker inspect cyber-arena-caddy-1 --format '{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{println}}{{end}}'
```

`/data` がボリュームになっていることを確かめる。なっていないと、手順 3 で Caddy を作り直したときに証明書を取り直すことになる。

### 2. ざわめきを起動する

```bash
cd apps/zawameki
cp .env.example .env
#   ZAWAMEKI_TEACHER_PASSWORD を設定
#   ZAWAMEKI_PUBLIC_URL=https://arena.koidelab.net:8100
#   ZAWAMEKI_CADDY_NETWORK=cyber-arena_default   ← 手順 1 の3つ目で出た名前
docker compose -f docker-compose.yml -f docker-compose.caddy.yml up -d --build
```

ざわめきは arena のネットワークに入り、Caddy から `zawameki:8100` で届く。ホストへはポートを出さない。
arena のネットワークが先にできている必要があるので、**arena を先に起動しておく**。

### 3. Caddy に足す

手順 1 で分かった arena のディレクトリで、2か所を直す。

**Caddyfile の末尾**に [`caddy/zawameki.Caddyfile`](caddy/zawameki.Caddyfile) の中身を貼る。

```caddyfile
arena.koidelab.net:8100 {
	reverse_proxy zawameki:8100
}
```

**arena の docker-compose.yml** の `caddy` サービスの `ports:` に1行足す。

```yaml
    ports:
      # （いまある 80 と 443 の行はそのまま残す）
      - "8100:8100"     # ← 足す（ざわめき）
```

Caddy を作り直す（ポートを足したので reload では足りない）。**arena が数秒止まるので、講義のない時間に。**

```bash
sudo docker compose up -d caddy
sudo docker compose logs --tail 20 caddy     # エラーが無いこと
curl -s https://arena.koidelab.net:8100/healthz   # {"ok":true,...}
```

あとで Caddyfile だけを直したときは、作り直さずに読み直せばよい。

```bash
sudo docker compose exec caddy caddy reload --config /etc/caddy/Caddyfile
```

EC2 のセキュリティグループで 8100/tcp を開けておくこと。

| 誰が | URL |
| --- | --- |
| 教員 | `https://arena.koidelab.net:8100/teacher` |
| 学生 | `https://arena.koidelab.net:8100/r/部屋コード`（投影の QR から） |

`http://arena.koidelab.net:8100/` と打つと Caddy は「HTTP request to an HTTPS server」を返す（転送はしない）。
学生は QR から入るので困らない。

### 確かめたこと（2026-10-05、Caddy の内部 CA の証明書で同じ構成を組んで）

- `cyber-arena` という名前の compose で Caddy を立て、ざわめきをそのネットワークに入れた
- `https://` で入室から投稿・「同じく」・隠す・部屋を閉じるまでブラウザで通し、エラー無し。
  Caddy は Host をポートつきで渡すので、CSP の `wss://arena.koidelab.net:8100` もそのまま通る
- 200人を `wss://` で60秒: 全員接続、教員に届くまで 中央値 167 ms／95% 260 ms。Caddy は CPU 0.2%・メモリ 31 MB

## Caddy の無いサーバで HTTPS にする（nginx）

前に何も無いサーバでは、nginx コンテナを前に置き、**8100 番で HTTPS を受けて**アプリへ渡す。アプリのコンテナはホストへ出さない。

```
 学生のスマホ ── https://arena.koidelab.net:8100 ──▶ nginx（TLS 終端）──▶ zawameki（平文、コンテナ間だけ）
```

### 1. 証明書を取る（初回だけ）

Let's Encrypt を使う。サーバで certbot を入れ、ドメインの証明書を取る。
**80 番ポートが一時的に空いていて、外から届くこと**が要る（HTTP-01 チャレンジ）。

```bash
sudo apt install certbot
sudo certbot certonly --standalone -d arena.koidelab.net
#   → /etc/letsencrypt/live/arena.koidelab.net/{fullchain,privkey}.pem
```

80 番を同じホストの Web サーバ（nginx など）が使っているなら、`--standalone` の代わりに
`--webroot -w <そのサーバの公開ディレクトリ>` で取る。学内の証明書（NII のサーバ証明書など）を使う場合は、
同じ名前（`fullchain.pem` と `privkey.pem`）で `.env` の `ZAWAMEKI_LETSENCRYPT_DIR` 配下の
`live/arena.koidelab.net/` に置けばよい。

### 2. 起動する

```bash
cd apps/zawameki
cp .env.example .env
#   ZAWAMEKI_TEACHER_PASSWORD を設定
#   ZAWAMEKI_PUBLIC_URL=https://arena.koidelab.net:8100   ← https にする（QR に入る）
docker compose -f docker-compose.yml -f docker-compose.https.yml up -d --build
```

| 誰が | URL |
| --- | --- |
| 教員 | `https://arena.koidelab.net:8100/teacher` |
| 学生 | `https://arena.koidelab.net:8100/r/部屋コード` |

`http://arena.koidelab.net:8100/` と打っても `https://` に送り直す。

`docker-compose.https.yml` は `ports: !reset []` を使うので、Docker Compose **v2.24.4 以降**が要る（`docker compose version` で確かめる）。

### 3. 更新のあとに nginx へ読み直させる

certbot は証明書を自動で更新するが、動いている nginx は古い証明書を持ったままになる。
更新のたびに読み直させるフックを置く。

```bash
sudo install -m 755 nginx/renew-hook.sh /etc/letsencrypt/renewal-hooks/deploy/zawameki.sh
sudo sed -i "s#/opt/zawameki#$PWD#" /etc/letsencrypt/renewal-hooks/deploy/zawameki.sh
sudo certbot renew --dry-run
```

### 設定の中身（`nginx/zawameki.conf`）

| 項目 | 設定 | 理由 |
| --- | --- | --- |
| WebSocket | `/ws` で `Upgrade` を渡し、読み取りの時間切れを3時間にする | 90分の講義のあいだ接続を切らない |
| Host | `$http_host`（ポートつき）を渡す | アプリの CSP が `wss://arena.koidelab.net:8100` を許すため。`$host` だとポートが落ちて接続が拒まれる |
| 平文で来たとき | `error_page 497` で `https://` へ 301 | 学生が `http://` と打っても入れる |
| TLS | 1.2 と 1.3 だけ | |
| HSTS | **付けない** | HSTS はポートを区別しない。付けると同じホストの arena（8000番、平文）が開けなくなる |
| IPv6 | コンテナでは `listen [::]` を書かない | コンテナに IPv6 が無いと nginx が起動しない |

### ホストの nginx を使う場合

ホストに既に nginx が入っていて、それに任せたいときは `nginx/host-zawameki.conf` を使う。

```bash
sudo cp nginx/host-zawameki.conf /etc/nginx/conf.d/zawameki.conf
sudo nginx -t && sudo systemctl reload nginx
# .env に ZAWAMEKI_PUBLISH=127.0.0.1:8101 を書き、アプリは 127.0.0.1 にだけ出す
docker compose up -d --build
```

このときは更新フックの代わりに `--deploy-hook "systemctl reload nginx"` を certbot に付ける。

### 確かめたこと（2026-10-05、自己署名の証明書で）

- `https://` で入室から投稿・「同じく」・隠す・部屋を閉じるまでブラウザで通し、エラー無し
- `http://` で来たら `https://` に 301、TLS 1.3・HTTP/2 で話す
- 200人を `wss://` で60秒: 全員接続、教員に届くまで 中央値 161 ms／95% 265 ms。nginx は CPU ほぼ0・メモリ 6 MB
- アプリのポートはホストに出ていない

### HTTPS にしない場合

`docker compose up -d --build`（`docker-compose.yml` だけ）で、`http://arena.koidelab.net:8100/` で動く。

## 出席の記録

学生が入室すると、**その回で最初に入室した時刻**を学生番号と一緒に残す
（SQLite の `attendance` 表。Docker ボリューム `zawameki_zawameki_data` の `/data/zawameki.sqlite3`）。
退室や滞在時間は残らない。部屋を閉じても消えない。時刻は日本時間で出る（Dockerfile の `TZ=Asia/Tokyo`）。

| 欲しいもの | 出し方 |
| --- | --- |
| 1回ぶん | レポート（`/teacher/部屋コード/report`）の「出席 CSV」 |
| 全回を1行1件で | 下のコマンド |
| 全回を出席簿の形（学生番号 × 回、出席回数つき）で | 下のコマンドに `--matrix` |

```bash
cd ~/CompOutline/apps/zawameki
C="sudo docker compose -f docker-compose.yml -f docker-compose.caddy.yml"
$C exec -T zawameki python -m zawameki.attendance          > 出席.csv
$C exec -T zawameki python -m zawameki.attendance --matrix > 出席簿.csv
```

**入室では本人確認をしない。** 部屋コードと他人の学生番号が分かれば、教室の外からでも入室できる
（部屋コードは講義ごとに変わるが、LINE などで回せば届く）。出席を成績に使うなら、この記録だけに頼らないこと。

バックアップ（講義のない時間に。DB の一貫した写しを取る）:

```bash
$C exec -T zawameki python -c "import sqlite3; s=sqlite3.connect('/data/zawameki.sqlite3'); d=sqlite3.connect('/data/backup.sqlite3'); s.backup(d); d.close()"
sudo docker cp zawameki-zawameki-1:/data/backup.sqlite3 ./zawameki-$(date +%F).sqlite3
```

## 匿名について

- 保存するのは「部屋」「出席（学生番号と入室時刻）」「投稿」「集計した時系列」だけ。
  **投稿の表には、学生番号の列がない**（学生が自分で添えた記名投稿を除く）
- 「同じく」の重複を防ぐ票は、学生番号を鍵つきハッシュ（`/data/secret.key`）にして持ち、部屋を閉じたら消す
- 迷子・ペースの信号は集計値だけを残す
- 入室時に学生番号を確かめる仕組み（パスワードなど）は無い。他人の番号でも入れる。
  記録は成績に使わない前提なので、これで足りると判断した

試験 `tests/test_app.py::test_anonymous_post_flow` が、DB の中身に投稿と学生番号の結びつきが無いことを確かめている。

## 開発

```bash
cd apps/zawameki
python3 -m venv .venv && .venv/bin/pip install -r requirements-dev.txt
ZAWAMEKI_DB=./dev.sqlite3 ZAWAMEKI_TEACHER_PASSWORD=dev .venv/bin/python -m zawameki
#   → http://127.0.0.1:8100/teacher （teacher / dev）
.venv/bin/python -m pytest -q
```

負荷試験（200人を60秒）:

```bash
.venv/bin/python tools/loadtest.py --base http://127.0.0.1:8100 --students 200 --seconds 60 --password dev
```

2026-10-05 の実測（コンテナ1つ）: 200人全員が接続、投稿が教員に届くまで 中央値 150 ms／95% 254 ms、
CPU 0.2%、メモリ 56 MB。目標（2秒以内）を十分に満たす。

| パス | 内容 |
| --- | --- |
| `zawameki/room.py` | 部屋1つぶんの状態と集計（天気・減衰・花火・投稿の種類）。通信も保存も知らない |
| `zawameki/hub.py` | 開いている部屋と接続。出来事を 0.25 秒ごとにまとめて配る |
| `zawameki/app.py` | HTTP と WebSocket の入口 |
| `zawameki/store.py` | SQLite |
| `zawameki/report.py` | 迷子の地図（HTML／Markdown） |
| `zawameki/static/` | 画面（素の HTML と JavaScript。ビルド工程なし） |
| `tools/loadtest.py` | 負荷試験 |
| `tools/reset-password.sh` | 教員パスワードを設定し直す |
| `zawameki/attendance.py` | 全回の出席を CSV で書き出す |
| `caddy/zawameki.Caddyfile` | arena の Caddy に足す設定 |
| `docker-compose.caddy.yml` | arena の Caddy に HTTPS を任せるときに重ねる設定 |
| `nginx/` | Caddy の無いサーバ用。HTTPS の終端（コンテナ用・ホスト用）と、証明書更新のフック |
| `docker-compose.https.yml` | HTTPS で動かすときに重ねる設定 |

状態は1プロセスのメモリに持つので、**ワーカーは1つ**で動かす（`python -m zawameki` がそうしている）。
再起動しても、開いていた部屋と投稿は SQLite から戻り、学生の画面は自動で入り直す。
