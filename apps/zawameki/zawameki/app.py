"""HTTP と WebSocket の入口。"""
from __future__ import annotations

import asyncio
import contextlib
import csv
import hmac
import io
import json
import logging
import time
from pathlib import Path
from typing import Any

import segno
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from . import config as config_mod
from . import report
from .hub import Conn, Hub, Live
from .room import KINDS, Rejected
from .store import Store

STATIC = Path(__file__).parent / "static"
MAX_MESSAGE = 2048         # 学生から受け取る1通の上限（バイト）
RATE_PER_SEC = 8           # 1本の接続から受け取る1秒あたりの上限

log = logging.getLogger("zawameki")


def normalize_sid(raw: Any) -> str:
    if not isinstance(raw, str):
        return ""
    return raw.strip().upper().replace("-", "").replace(" ", "").replace("　", "")


class Bucket:
    """接続ごとの送信量の制限（トークンバケツ）。"""

    def __init__(self, rate: float):
        self.rate = rate
        self.tokens = rate
        self.at = time.monotonic()

    def take(self) -> bool:
        now = time.monotonic()
        self.tokens = min(self.rate, self.tokens + (now - self.at) * self.rate)
        self.at = now
        if self.tokens < 1:
            return False
        self.tokens -= 1
        return True


class SecurityHeaders(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)
        host = request.headers.get("host", "")
        resp.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
            f"img-src 'self' data:; connect-src 'self' ws://{host} wss://{host}; "
            "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp


def create_app(cfg: config_mod.Config | None = None) -> FastAPI:
    cfg = cfg or config_mod.load()
    store = Store(cfg.db)
    hub = Hub(cfg, store)
    hub.restore()

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        hub.start()
        yield
        await hub.stop()

    app = FastAPI(title="ざわめき", lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.hub = hub
    app.add_middleware(SecurityHeaders)
    app.mount("/static", StaticFiles(directory=STATIC), name="static")
    basic = HTTPBasic(realm="zawameki teacher")

    def teacher(creds: HTTPBasicCredentials = Depends(basic)) -> str:
        ok_user = hmac.compare_digest(creds.username.encode(), cfg.teacher_user.encode())
        ok_pass = hmac.compare_digest(creds.password.encode(), cfg.teacher_password.encode())
        if not (ok_user and ok_pass):
            raise HTTPException(401, "unauthorized", headers={"WWW-Authenticate": 'Basic realm="zawameki teacher"'})
        return creds.username

    def join_url(request: Request, code: str) -> str:
        base = cfg.public_url or str(request.base_url).rstrip("/")
        return f"{base}/r/{code}"

    def live_or_404(code: str) -> Live:
        live = hub.live.get(code)
        if live is None:
            raise HTTPException(404, "その部屋は開いていません")
        return live

    def room_row_or_404(code: str):
        live = hub.live.get(code)
        row = store.room(live.room.id) if live else store.room_by_code(code)
        if row is None:
            raise HTTPException(404, "その部屋はありません")
        return row

    # ---- 学生の入口 ----
    @app.get("/", include_in_schema=False)
    @app.get("/r/{code}", include_in_schema=False)
    def student_page(code: str | None = None):
        return FileResponse(STATIC / "student.html", headers={"Cache-Control": "no-cache"})

    @app.get("/healthz", include_in_schema=False)
    def healthz():
        return {"ok": True, "rooms": len(hub.live)}

    @app.get("/api/rooms/{code}")
    def room_public(code: str):
        live = live_or_404(code)
        return {"code": code, "title": live.room.title}

    @app.get("/api/config")
    def public_config():
        return {"student_id_pattern": cfg.student_id_pattern.pattern}

    @app.get("/qr/{code}.svg", include_in_schema=False)
    def qr(code: str, request: Request):
        live_or_404(code)
        buf = io.BytesIO()
        segno.make(join_url(request, code), error="m").save(buf, kind="svg", scale=10, border=2,
                                                          dark="#000", light="#fff", xmldecl=False)
        return Response(buf.getvalue(), media_type="image/svg+xml")

    # ---- 教員の画面 ----
    @app.get("/teacher", include_in_schema=False)
    def teacher_home(_: str = Depends(teacher)):
        return FileResponse(STATIC / "teacher.html", headers={"Cache-Control": "no-cache"})

    @app.get("/teacher/{code}", include_in_schema=False)
    def teacher_console(code: str, _: str = Depends(teacher)):
        return FileResponse(STATIC / "console.html", headers={"Cache-Control": "no-cache"})

    @app.get("/projector/{code}", include_in_schema=False)
    def projector(code: str):
        # 鍵は URL の ?key= で渡す（投影用の PC で Basic 認証を求めないため）。確かめるのは WebSocket 側
        return FileResponse(STATIC / "projector.html", headers={"Cache-Control": "no-cache"})

    @app.get("/teacher/{code}/report", include_in_schema=False, response_class=HTMLResponse)
    def report_page(code: str, _: str = Depends(teacher)):
        row = room_row_or_404(code)
        return report.html(store, row)

    # ---- 教員の API ----
    @app.get("/api/teacher/rooms")
    def list_rooms(_: str = Depends(teacher)):
        rooms = []
        for r in store.recent_rooms():
            rooms.append({"code": r["code"], "title": r["title"], "opened_at": r["opened_at"],
                          "closed_at": r["closed_at"], "joined": r["joined"],
                          "questions": r["nquestions"], "comments": r["ncomments"],
                          "open": r["closed_at"] is None and r["code"] in hub.live})
        return {"rooms": rooms}

    @app.post("/api/teacher/rooms")
    async def create_room(request: Request, _: str = Depends(teacher)):
        body = await request.json()
        title = str(body.get("title", "")).strip()[:80] or "講義"
        room = hub.open_room(title)
        return {"code": room.code}

    @app.get("/api/teacher/rooms/{code}")
    def room_detail(code: str, request: Request, _: str = Depends(teacher)):
        live = live_or_404(code)
        return {"code": code, "title": live.room.title, "key": live.room.key,
                "join_url": join_url(request, code)}

    @app.post("/api/teacher/rooms/{code}/close")
    def close_room(code: str, _: str = Depends(teacher)):
        live_or_404(code)
        hub.close_room(code)
        return {"ok": True}

    @app.get("/api/teacher/rooms/{code}/{name}")
    def export(code: str, name: str, _: str = Depends(teacher)):
        row = room_row_or_404(code)
        rid = row["id"]
        if name == "report.md":
            return PlainTextResponse(report.markdown(store, row), media_type="text/markdown; charset=utf-8",
                                     headers=_attachment(f"zawameki-{code}.md"))
        tables = {
            "attendance.csv": (["student_id", "joined_at"],
                               [(r["student_id"], _iso(r["joined_at"])) for r in store.attendance(rid)]),
            "posts.csv": (["id", "t", "slide", "kind", "votes", "status", "named", "text"],
                          [(r["id"], round(r["t"]), r["slide"], KINDS[r["kind"]]["label"], r["votes"], r["status"],
                            r["named"] or "", r["text"]) for r in store.posts(rid)]),
            "ticks.csv": (["t", "slide", "present", "lost", "aha", "slow", "fast"],
                          [(round(r["t"]), r["slide"], r["present"], r["lost"], r["aha"], r["slow"], r["fast"])
                           for r in store.ticks(rid)]),
        }
        if name not in tables:
            raise HTTPException(404)
        header, rows = tables[name]
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(header)
        w.writerows(rows)
        # Excel で文字化けしないよう BOM を付ける
        return Response("﻿" + buf.getvalue(), media_type="text/csv; charset=utf-8",
                        headers=_attachment(f"zawameki-{code}-{name}"))

    # ---- 学生の WebSocket ----
    @app.websocket("/ws")
    async def ws_student(ws: WebSocket):
        await ws.accept()
        try:
            hello = json.loads(await asyncio.wait_for(ws.receive_text(), timeout=15))
        except Exception:
            await ws.close(code=1008)
            return
        code = str(hello.get("code", ""))
        sid = normalize_sid(hello.get("sid"))
        live = hub.live.get(code)
        if live is None:
            await ws.send_json({"type": "error", "fatal": True, "reason": "no_room",
                                "message": "その部屋は開いていません。部屋コードを確かめてください"})
            await ws.close()
            return
        if not cfg.student_id_pattern.match(sid):
            await ws.send_json({"type": "error", "fatal": True, "reason": "bad_sid",
                                "message": "学生番号の形が正しくありません"})
            await ws.close()
            return

        room = live.room
        now = time.time()
        if room.connect(sid):
            store.add_attendance(room.id, sid, now)
        voter = hub.voter(room, sid)
        conn = Conn(ws, sid)
        conn.start()
        live.students.add(conn)
        conn.send_obj({
            "type": "welcome", "code": code, "title": room.title, "settings": room.settings.public(),
            "you": room.you(sid, now), "posts": room.visible_posts(voter),
        })
        conn.send_obj({"type": "tick", **hub.student_tick(live, room.counts(now))})
        bucket = Bucket(RATE_PER_SEC)
        try:
            while True:
                text = await ws.receive_text()
                if len(text) > MAX_MESSAGE or not bucket.take():
                    conn.send_obj({"type": "error", "message": "送信が多すぎます。少し待ってください"})
                    continue
                try:
                    msg = json.loads(text)
                    if not isinstance(msg, dict):
                        raise ValueError
                except ValueError:
                    continue
                if code not in hub.live:
                    break
                try:
                    handle_student(live, conn, sid, voter, msg, time.time())
                except Rejected as e:
                    conn.send_obj({"type": "error", "message": str(e)})
        except WebSocketDisconnect:
            pass
        except Exception:
            log.exception("student ws")
        finally:
            live.students.discard(conn)
            room.disconnect(sid)
            conn.close()

    def handle_student(live: Live, conn: Conn, sid: str, voter: str, msg: dict, now: float) -> None:
        room = live.room
        kind = msg.get("type")
        if kind == "lost":
            room.press_lost(sid, now)
            conn.send_obj({"type": "you", **room.you(sid, now)})
        elif kind == "got":
            room.press_got(sid, now)
            conn.send_obj({"type": "you", **room.you(sid, now)})
        elif kind == "pace":
            room.press_pace(sid, msg.get("dir"), now)
            conn.send_obj({"type": "you", **room.you(sid, now)})
        elif kind == "post":
            p = room.post(sid, msg.get("kind"), msg.get("text"), bool(msg.get("named")), now)
            store.add_post(room.id, p)
            live.to_students({"type": "post", "p": p.public()})
            live.to_teachers({"type": "post", "p": p.for_teacher()})
            conn.send_obj({"type": "ok", "what": "post", "id": p.id, "kind": p.kind})
        elif kind == "metoo":
            p = room.metoo(voter, msg.get("id"))
            mine = voter in p.voters
            store.set_vote(room.id, p.id, voter, mine)
            store.update_post(room.id, p)
            live.to_students({"type": "post", "p": p.public()})
            live.to_teachers({"type": "post", "p": p.for_teacher()})
            conn.send_obj({"type": "metoo", "id": p.id, "mine": mine})
        elif kind == "ping":
            conn.send_obj({"type": "pong"})

    # ---- 教員・投影の WebSocket ----
    @app.websocket("/ws/teacher")
    async def ws_teacher(ws: WebSocket):
        # 鍵は URL に載せず最初の1通で受け取る（アクセスログに残さないため）
        await ws.accept()
        try:
            hello = json.loads(await asyncio.wait_for(ws.receive_text(), timeout=15))
            code, key = str(hello.get("code", "")), str(hello.get("key", ""))
        except Exception:
            await ws.close(code=1008)
            return
        live = hub.live.get(code)
        if live is None or not hmac.compare_digest(key.encode(), live.room.key.encode()):
            await ws.send_json({"type": "error", "fatal": True, "reason": "no_room",
                                "message": "部屋が閉じているか、鍵が違います"})
            await ws.close()
            return
        room = live.room
        conn = Conn(ws)
        conn.start()
        live.teachers.add(conn)
        now = time.time()
        conn.send_obj({
            "type": "welcome", "code": code, "title": room.title, "settings": room.settings.public(),
            "projector": room.projector_mode, "history": room.history_series(),
            "posts": [p.for_teacher() for p in list(room.posts.values())[-500:]],
            "opened_at": room.opened_at, "tick": {**room.counts(now), "fireworks": 0},
            "join_url": (cfg.public_url or f"{'https' if ws.url.scheme == 'wss' else 'http'}://{ws.headers.get('host', '')}")
                        + f"/r/{code}",
        })
        try:
            while True:
                text = await ws.receive_text()
                if len(text) > MAX_MESSAGE:
                    continue
                try:
                    msg = json.loads(text)
                    if not isinstance(msg, dict):
                        raise ValueError
                except ValueError:
                    continue
                if code not in hub.live:
                    break
                try:
                    handle_teacher(live, msg, time.time())
                except Rejected as e:
                    conn.send_obj({"type": "error", "message": str(e)})
        except WebSocketDisconnect:
            pass
        except Exception:
            log.exception("teacher ws")
        finally:
            live.teachers.discard(conn)
            conn.close()

    def handle_teacher(live: Live, msg: dict, now: float) -> None:
        room = live.room
        kind = msg.get("type")
        if kind == "slide":
            no = room.set_slide(msg.get("no"))
            store.add_slide(room.id, room.rel(now), no)
            hub.save_room(live)
            live.to_all({"type": "slide", "no": no})
        elif kind == "mark":
            p = room.mark(msg.get("id"), msg.get("status"))
            store.update_post(room.id, p)
            live.to_teachers({"type": "post", "p": p.for_teacher()})
            if p.status == "hidden":
                live.to_students({"type": "post_removed", "id": p.id})
            else:
                live.to_students({"type": "post", "p": p.public()})
        elif kind == "settings":
            s = room.update_settings(msg.get("settings") or {})
            hub.save_room(live)
            live.to_all({"type": "settings", "settings": s.public()})
            live.to_students(hub.student_tick(live, room.counts(now)))
        elif kind == "projector":
            mode = room.set_projector(msg.get("mode"))
            live.to_teachers({"type": "projector", "mode": mode})

    return app


def _attachment(filename: str) -> dict[str, str]:
    return {"Content-Disposition": f'attachment; filename="{filename}"'}


def _iso(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))
