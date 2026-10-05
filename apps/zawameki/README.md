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

arena（ポート 8000）とは別のコンテナとして、ポート **8100** で動かす。
**HTTPS で動かす手順は下の「HTTPS で動かす」**。ファイアウォールで 8100/tcp を開けておくこと。
教員の入口（`/teacher`）は Basic 認証で守ってある。

### 講義の流れ

1. `/teacher` で部屋を開く → 操作画面に移る
2. 「📽 投影画面を開く」を教室の PC で開き、`f` キーで全画面にする。学生に QR を読ませる
3. 話しながら操作画面を見る。スライドを送ったら ◀ ▶（または ← →）で番号を合わせる
4. 区切りで投影を「質問・意見」に切り替えて答える。答えたら「✓ 答えた」
5. 終わったら「部屋を閉じる」→ 迷子の地図が出る

部屋は4時間たつと自動で閉じる（`ZAWAMEKI_ROOM_HOURS`）。

## HTTPS で動かす（推奨）

nginx コンテナを前に置き、**8100 番で HTTPS を受けて**アプリへ渡す。アプリのコンテナはホストへ出さない。

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

80 番を既に別の Web サーバが使っているなら、`--standalone` の代わりに
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
| `nginx/` | HTTPS の終端（コンテナ用・ホスト用）と、証明書更新のフック |
| `docker-compose.https.yml` | HTTPS で動かすときに重ねる設定 |

状態は1プロセスのメモリに持つので、**ワーカーは1つ**で動かす（`python -m zawameki` がそうしている）。
再起動しても、開いていた部屋と投稿は SQLite から戻り、学生の画面は自動で入り直す。
