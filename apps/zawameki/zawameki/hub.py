"""開いている部屋と、そこにつながっている接続を束ねる。

学生が押すたびに全員へ配ると、200人 × 200人で通信が膨れる。
そこで出来事はいったん溜め、0.25秒ごとにまとめて配る。
集計（天気など）は教員へ1秒ごと、学生へ5秒ごとに配る（SPEC §8.1）。
"""
from __future__ import annotations

import asyncio
import contextlib
import hashlib
import hmac
import json
import logging
import secrets
import time
from typing import Any

from starlette.websockets import WebSocket

from .config import Config
from .room import Room, Settings
from .store import Store

log = logging.getLogger("zawameki")

FLUSH_INTERVAL = 0.25
TEACHER_TICK = 1.0
STUDENT_TICK = 5.0
SAVE_TICK = 5.0


class Conn:
    """1本の WebSocket。送信は専用のタスクに任せ、遅い端末に全体を待たせない。"""

    def __init__(self, ws: WebSocket, sid: str | None = None):
        self.ws = ws
        self.sid = sid
        self.queue: asyncio.Queue[str | None] = asyncio.Queue(maxsize=200)
        self.task: asyncio.Task | None = None

    def start(self) -> None:
        self.task = asyncio.create_task(self._run())

    def send(self, text: str) -> None:
        try:
            self.queue.put_nowait(text)
        except asyncio.QueueFull:
            # 受け取れていない端末。切って、向こうから再接続させる
            self.close()

    def send_obj(self, obj: dict[str, Any]) -> None:
        self.send(json.dumps(obj, ensure_ascii=False))

    def close(self) -> None:
        with contextlib.suppress(asyncio.QueueFull):
            self.queue.put_nowait(None)

    async def _run(self) -> None:
        try:
            while True:
                text = await self.queue.get()
                if text is None:
                    break
                await self.ws.send_text(text)
        except Exception:
            pass
        finally:
            with contextlib.suppress(Exception):
                await self.ws.close()


class Live:
    """部屋1つぶんの実行時の状態（Room + 接続 + 配る前の出来事）。"""

    def __init__(self, room: Room):
        self.room = room
        self.students: set[Conn] = set()
        self.teachers: set[Conn] = set()
        self.out_students: list[dict[str, Any]] = []
        self.out_teachers: list[dict[str, Any]] = []
        self.last_student_tick = 0.0
        self.last_save = 0.0
        self.last_counts: dict[str, Any] = {}

    def to_students(self, msg: dict[str, Any]) -> None:
        self.out_students.append(msg)

    def to_teachers(self, msg: dict[str, Any]) -> None:
        self.out_teachers.append(msg)

    def to_all(self, msg: dict[str, Any]) -> None:
        self.to_students(msg)
        self.to_teachers(msg)

    def flush(self) -> None:
        for conns, out in ((self.students, self.out_students), (self.teachers, self.out_teachers)):
            if not out:
                continue
            msg = out[0] if len(out) == 1 else {"type": "batch", "items": out}
            text = json.dumps(msg, ensure_ascii=False)   # 1回だけ文字列にして全員に配る
            for c in list(conns):
                c.send(text)
            out.clear()


class Hub:
    def __init__(self, config: Config, store: Store):
        self.config = config
        self.store = store
        self.live: dict[str, Live] = {}
        self.task: asyncio.Task | None = None

    # ---- 部屋 ----
    def restore(self) -> None:
        """再起動の前に開いていた部屋を戻す。学生は自動で入り直す。"""
        for row in self.store.open_rooms():
            room = Room(row["id"], row["code"], row["key"], row["title"], row["opened_at"], self.config.ng_words)
            room.slide = row["slide"]
            s = json.loads(row["settings"] or "{}")
            room.settings = Settings(**{k: v for k, v in s.items() if k in Settings.__dataclass_fields__})
            room.restore(self.store.load_posts(room.id, 1000),
                         {r["student_id"] for r in self.store.attendance(room.id)})
            self.live[room.code] = Live(room)
            log.info("restored room %s (%s)", room.code, room.title)

    def open_room(self, title: str, now: float | None = None) -> Room:
        now = time.time() if now is None else now
        for _ in range(100):
            code = f"{secrets.randbelow(9000) + 1000}"
            if code not in self.live:
                break
        else:
            raise RuntimeError("部屋コードが尽きた")
        key = secrets.token_urlsafe(24)
        room_id = self.store.create_room(code, key, title, now)
        room = Room(room_id, code, key, title, now, self.config.ng_words)
        self.live[code] = Live(room)
        return room

    def close_room(self, code: str, now: float | None = None) -> None:
        live = self.live.pop(code, None)
        if live is None:
            return
        now = time.time() if now is None else now
        self.store.add_tick(live.room.id, live.room.counts(now))
        self.store.close_room(live.room.id, now)
        live.out_students.clear()
        live.out_teachers.clear()
        live.to_all({"type": "closed"})
        live.flush()
        for c in list(live.students) + list(live.teachers):
            c.close()

    def save_room(self, live: Live) -> None:
        self.store.save_room_state(live.room.id, live.room.slide, live.room.settings.public())

    def voter(self, room: Room, sid: str) -> str:
        """「同じく」の重複を数えるための鍵つきハッシュ。学生番号には戻せない。"""
        msg = f"{room.id}:{sid}".encode()
        return hmac.new(self.config.secret, msg, hashlib.sha256).hexdigest()[:32]

    # ---- 時計 ----
    def start(self) -> None:
        self.task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self.task:
            self.task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.task

    async def _loop(self) -> None:
        last_teacher = 0.0
        while True:
            try:
                now = time.time()
                if now - last_teacher >= TEACHER_TICK:
                    last_teacher = now
                    self.tick(now)
                for live in list(self.live.values()):
                    live.flush()
            except Exception:
                log.exception("tick failed")
            await asyncio.sleep(FLUSH_INTERVAL)

    def tick(self, now: float) -> None:
        for code, live in list(self.live.items()):
            room = live.room
            if now - room.opened_at > self.config.room_hours * 3600:
                log.info("auto-closing room %s", code)
                self.close_room(code, now)
                continue
            c = room.record(now)
            live.last_counts = c
            live.to_teachers({"type": "tick", **c})
            if c["fireworks"]:
                live.to_all({"type": "fireworks", "count": c["fireworks"]})
            if now - live.last_student_tick >= STUDENT_TICK:
                live.last_student_tick = now
                live.to_students(self.student_tick(live, c))
            if now - live.last_save >= SAVE_TICK:
                live.last_save = now
                self.store.add_tick(room.id, c)

    def student_tick(self, live: Live, c: dict[str, Any]) -> dict[str, Any]:
        msg = {"type": "tick", "present": c["present"], "slide": c["slide"]}
        if live.room.settings.show_weather:
            msg["weather"] = c["weather"]
            msg["lost"] = c["lost"]
        return msg
