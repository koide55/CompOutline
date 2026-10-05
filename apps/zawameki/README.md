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

```bash
cd apps/zawameki
cp .env.example .env
#   ZAWAMEKI_TEACHER_PASSWORD を必ず設定する
#   ZAWAMEKI_PUBLIC_URL=http://arena.koidelab.net:8100 （QR に入る URL）
docker compose up -d --build
docker compose logs -f
```

| 誰が | URL |
| --- | --- |
| 教員 | `http://arena.koidelab.net:8100/teacher`（Basic 認証） |
| 学生 | `http://arena.koidelab.net:8100/r/部屋コード`（投影の QR から） |

ファイアウォールで 8100/tcp を開けておくこと。

### 講義の流れ

1. `/teacher` で部屋を開く → 操作画面に移る
2. 「📽 投影画面を開く」を教室の PC で開き、`f` キーで全画面にする。学生に QR を読ませる
3. 話しながら操作画面を見る。スライドを送ったら ◀ ▶（または ← →）で番号を合わせる
4. 区切りで投影を「質問・意見」に切り替えて答える。答えたら「✓ 答えた」
5. 終わったら「部屋を閉じる」→ 迷子の地図が出る

部屋は4時間たつと自動で閉じる（`ZAWAMEKI_ROOM_HOURS`）。

### HTTPS にする場合

学生のスマホから学外回線で入るなら、HTTPS にしたほうがよい。
方法は2つ。どちらでもアプリ側の変更は要らない（WebSocket は `wss://` に自動で切り替わる）。

- **前段の nginx で終端する**: 8100 番で `ssl` を受けて `127.0.0.1:8101` へ渡す。
  WebSocket のために `proxy_set_header Upgrade $http_upgrade; proxy_set_header Connection "upgrade";` を入れる。
  `.env` で `ZAWAMEKI_PUBLISH=127.0.0.1:8101` にして、コンテナを外へ直接出さない
- **アプリが直接出す**: 証明書をコンテナに読み取り専用で渡し、`.env` の `ZAWAMEKI_SSL_CERTFILE` と `ZAWAMEKI_SSL_KEYFILE` を設定する

どちらの場合も `ZAWAMEKI_PUBLIC_URL` を `https://` に変える。

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

状態は1プロセスのメモリに持つので、**ワーカーは1つ**で動かす（`python -m zawameki` がそうしている）。
再起動しても、開いていた部屋と投稿は SQLite から戻り、学生の画面は自動で入り直す。
