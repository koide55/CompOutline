"""200人の教室を模して負荷をかける。

    python tools/loadtest.py --base http://127.0.0.1:8100 --students 200 --seconds 60 --password ...

部屋を1つ開き、学生をつなぎ、迷子・ペース・投稿・「同じく」をばらばらに送る。
教員の接続で、学生が送ってから届くまでの遅れを測る（SPEC §9 の目標は2秒以内）。
"""
from __future__ import annotations

import argparse
import asyncio
import base64
import json
import random
import statistics
import time
import urllib.request

import websockets

KINDS = ["comment"] * 6 + ["question", "opinion", "naive"]


def api(base: str, path: str, auth: str, body: dict | None = None) -> dict:
    req = urllib.request.Request(base + path, data=json.dumps(body).encode() if body is not None else None,
                                 headers={"Authorization": "Basic " + auth, "Content-Type": "application/json"},
                                 method="POST" if body is not None else "GET")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


async def student(ws_url: str, code: str, n: int, until: float, stats: dict, ids: list[int]) -> None:
    sid = f"9LT{n:05d}"
    await asyncio.sleep(random.random() * 5)   # 授業の始まりに、ばらばらに入ってくる
    try:
        async with websockets.connect(ws_url + "/ws", max_queue=None) as ws:
            await ws.send(json.dumps({"type": "hello", "code": code, "sid": sid}))
            stats["joined"] += 1

            async def reader():
                async for raw in ws:
                    m = json.loads(raw)
                    for it in (m["items"] if m["type"] == "batch" else [m]):
                        stats["received"] += 1
                        if it["type"] == "ok":
                            ids.append(it["id"])
                        elif it["type"] == "error":
                            stats["rejected"] += 1

            task = asyncio.create_task(reader())
            while time.time() < until:
                await asyncio.sleep(random.expovariate(1 / 8))   # 平均8秒に1回なにかする
                r = random.random()
                if r < 0.35:
                    await ws.send(json.dumps({"type": "lost"}))
                elif r < 0.5:
                    await ws.send(json.dumps({"type": "got"}))
                elif r < 0.6:
                    await ws.send(json.dumps({"type": "pace", "dir": random.choice(["slow", "fast"])}))
                elif r < 0.8:
                    kind = random.choice(KINDS)
                    await ws.send(json.dumps({"type": "post", "kind": kind, "text": f"@{time.time():.3f} {sid}"}))
                    stats["sent"] += 1
                elif ids:
                    await ws.send(json.dumps({"type": "metoo", "id": random.choice(ids)}))
            task.cancel()
    except Exception as e:
        stats["errors"] += 1
        stats["last_error"] = repr(e)


async def teacher(ws_url: str, code: str, key: str, until: float, lat: list[float], ticks: list[dict]) -> None:
    async with websockets.connect(ws_url + "/ws/teacher", max_queue=None) as ws:
        await ws.send(json.dumps({"type": "hello", "code": code, "key": key}))
        while time.time() < until + 3:
            try:
                raw = await asyncio.wait_for(ws.recv(), timeout=1)
            except asyncio.TimeoutError:
                continue
            m = json.loads(raw)
            for it in (m["items"] if m["type"] == "batch" else [m]):
                if it["type"] == "post" and it["p"]["votes"] == 0 and it["p"]["text"].startswith("@"):
                    lat.append(time.time() - float(it["p"]["text"][1:].split()[0]))
                elif it["type"] == "tick":
                    ticks.append(it)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8100")
    ap.add_argument("--students", type=int, default=200)
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--user", default="teacher")
    ap.add_argument("--password", required=True)
    args = ap.parse_args()
    auth = base64.b64encode(f"{args.user}:{args.password}".encode()).decode()
    code = api(args.base, "/api/teacher/rooms", auth, {"title": f"負荷試験 {args.students}人"})["code"]
    key = api(args.base, f"/api/teacher/rooms/{code}", auth)["key"]
    ws_url = args.base.replace("http", "ws", 1)
    until = time.time() + args.seconds
    stats = {"joined": 0, "sent": 0, "received": 0, "rejected": 0, "errors": 0}
    lat: list[float] = []
    ticks: list[dict] = []
    ids: list[int] = []
    print(f"部屋 {code} に {args.students}人を {args.seconds}秒つなぎます…")
    await asyncio.gather(teacher(ws_url, code, key, until, lat, ticks),
                         *(student(ws_url, code, i, until, stats, ids) for i in range(args.students)))
    peak = max((t["present"] for t in ticks), default=0)
    print(f"入室 {stats['joined']}人 / 同時在室の最大 {peak}人 / 接続の失敗 {stats['errors']}")
    print(f"投稿 {stats['sent']}件（待ち時間で断られた操作 {stats['rejected']}件）/ 学生が受け取った出来事 {stats['received']}件")
    if lat:
        lat.sort()
        p95 = lat[int(len(lat) * 0.95) - 1]
        print(f"教員に届くまでの遅れ: 中央値 {statistics.median(lat) * 1000:.0f} ms / 95% {p95 * 1000:.0f} ms / 最大 {lat[-1] * 1000:.0f} ms")
        ok = p95 < 2.0 and stats["errors"] == 0 and peak >= args.students * 0.95
        print("✓ 目標（2秒以内・全員接続）を満たした" if ok else "✗ 目標を満たさなかった")
    if stats.get("last_error"):
        print("最後のエラー:", stats["last_error"])
    api(args.base, f"/api/teacher/rooms/{code}/close", auth, {})


if __name__ == "__main__":
    asyncio.run(main())
