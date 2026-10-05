import re
import sqlite3

import pytest
from fastapi.testclient import TestClient

from zawameki.app import create_app
from zawameki.config import Config

AUTH = ("teacher", "pw")
H = {"X-Zawameki": "1"}


@pytest.fixture
def client(tmp_path):
    cfg = Config(db=str(tmp_path / "z.sqlite3"), public_url="http://arena.example:8100",
                 teacher_user="teacher", teacher_password="pw", secret=b"s" * 32,
                 student_id_pattern=re.compile(r"^[0-9A-Z]{5,12}$"), ng_words=(), room_hours=4)
    app = create_app(cfg)
    with TestClient(app) as c:
        c.db_path = cfg.db
        yield c


def open_room(client):
    code = client.post("/api/teacher/rooms", json={"title": "第3回"}, auth=AUTH, headers=H).json()["code"]
    key = client.get(f"/api/teacher/rooms/{code}", auth=AUTH).json()["key"]
    return code, key


def recv_until(ws, kind, limit=50):
    for _ in range(limit):
        m = ws.receive_json()
        items = m["items"] if m["type"] == "batch" else [m]
        for it in items:
            if it["type"] == kind:
                return it
    raise AssertionError(f"{kind} not received")


def test_teacher_pages_need_password(client):
    assert client.get("/teacher").status_code == 401
    assert client.get("/api/teacher/rooms").status_code == 401
    assert client.get("/api/teacher/rooms", auth=("teacher", "wrong")).status_code == 401
    assert client.get("/teacher", auth=AUTH).status_code == 200


def test_teacher_post_needs_custom_header(client):
    # 他サイトのフォームからは独自ヘッダを付けられない。Basic 認証が通っていても断る
    r = client.post("/api/teacher/rooms", content='{"title": "x"}', auth=AUTH,
                    headers={"Content-Type": "text/plain"})
    assert r.status_code == 403
    code, _ = open_room(client)
    assert client.post(f"/api/teacher/rooms/{code}/close", auth=AUTH).status_code == 403
    assert code in [r["code"] for r in client.get("/api/teacher/rooms", auth=AUTH).json()["rooms"] if r["open"]]


def test_security_headers(client):
    r = client.get("/")
    assert "script-src 'self'" in r.headers["content-security-policy"]
    assert r.headers["x-content-type-options"] == "nosniff"


def test_join_rejects_unknown_room_and_bad_student_id(client):
    code, _ = open_room(client)
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "code": "0000", "sid": "1TE24001X"})
        assert ws.receive_json()["reason"] == "no_room"
    with client.websocket_connect("/ws") as ws:
        ws.send_json({"type": "hello", "code": code, "sid": "<script>"})
        assert ws.receive_json()["reason"] == "bad_sid"


def test_teacher_ws_needs_key(client):
    code, _ = open_room(client)
    with client.websocket_connect("/ws/teacher") as ws:
        ws.send_json({"type": "hello", "code": code, "key": "nope"})
        assert ws.receive_json()["fatal"] is True


def test_anonymous_post_flow(client):
    code, key = open_room(client)
    with client.websocket_connect("/ws/teacher") as t, \
            client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
        t.send_json({"type": "hello", "code": code, "key": key})
        assert recv_until(t, "welcome")["join_url"] == f"http://arena.example:8100/r/{code}"
        a.send_json({"type": "hello", "code": code, "sid": "1te24001x"})   # 小文字も受ける
        recv_until(a, "welcome")
        b.send_json({"type": "hello", "code": code, "sid": "1TE24002Y"})
        recv_until(b, "welcome")

        a.send_json({"type": "post", "kind": "naive", "text": "素朴な疑問です"})
        ok = recv_until(a, "ok")
        assert ok["kind"] == "naive"
        seen = recv_until(t, "post")["p"]
        assert seen["text"] == "素朴な疑問です" and seen["named"] is None
        assert recv_until(b, "post")["p"]["kind"] == "naive"

        b.send_json({"type": "metoo", "id": ok["id"]})
        assert recv_until(b, "metoo")["mine"] is True
        assert recv_until(t, "post")["p"]["votes"] == 1

        a.send_json({"type": "lost"})
        assert recv_until(a, "you")["lost_left"] > 80
        tick = recv_until(t, "tick")
        assert tick["present"] == 2

        t.send_json({"type": "mark", "id": ok["id"], "status": "hidden"})
        assert recv_until(b, "post_removed")["id"] == ok["id"]

    # 出席には学生番号が残るが、匿名の投稿には残らない
    att = client.get(f"/api/teacher/rooms/{code}/attendance.csv", auth=AUTH).text
    assert "1TE24001X" in att and "1TE24002Y" in att
    posts = client.get(f"/api/teacher/rooms/{code}/posts.csv", auth=AUTH).text
    assert "素朴な疑問です" in posts and "1TE24001X" not in posts
    db = sqlite3.connect(client.db_path)
    dump = "\n".join(db.iterdump())
    rows_with_text = [l for l in dump.splitlines() if "素朴な疑問です" in l]
    assert rows_with_text and all("1TE24001X" not in l for l in rows_with_text)
    assert "1TE24002Y" not in "".join(l for l in dump.splitlines() if "post_votes" in l)


def test_named_post_shows_student_id_to_teacher_only(client):
    code, key = open_room(client)
    with client.websocket_connect("/ws/teacher") as t, \
            client.websocket_connect("/ws") as a, client.websocket_connect("/ws") as b:
        t.send_json({"type": "hello", "code": code, "key": key})
        recv_until(t, "welcome")
        for ws, sid in ((a, "1TE24001X"), (b, "1TE24002Y")):
            ws.send_json({"type": "hello", "code": code, "sid": sid})
            recv_until(ws, "welcome")
        a.send_json({"type": "post", "kind": "opinion", "text": "ご意見", "named": True})
        assert recv_until(t, "post")["p"]["named"] == "1TE24001X"
        assert "named" not in recv_until(b, "post")["p"]


def test_comments_pause_and_rate_limit(client):
    code, key = open_room(client)
    with client.websocket_connect("/ws/teacher") as t, client.websocket_connect("/ws") as a:
        t.send_json({"type": "hello", "code": code, "key": key})
        recv_until(t, "welcome")
        a.send_json({"type": "hello", "code": code, "sid": "1TE24001X"})
        recv_until(a, "welcome")
        a.send_json({"type": "post", "kind": "comment", "text": "1件目"})
        recv_until(a, "ok")
        a.send_json({"type": "post", "kind": "comment", "text": "2件目"})
        assert "待って" in recv_until(a, "error")["message"]
        t.send_json({"type": "settings", "settings": {"comments_open": False}})
        assert recv_until(a, "settings")["settings"]["comments_open"] is False


def test_close_room_and_report(client):
    code, key = open_room(client)
    with client.websocket_connect("/ws") as a:
        a.send_json({"type": "hello", "code": code, "sid": "1TE24001X"})
        recv_until(a, "welcome")
        a.send_json({"type": "post", "kind": "question", "text": "<b>太字</b>?"})
        recv_until(a, "ok")
        assert client.post(f"/api/teacher/rooms/{code}/close", auth=AUTH, headers=H).status_code == 200
        recv_until(a, "closed")
    html = client.get(f"/teacher/{code}/report", auth=AUTH).text
    assert "&lt;b&gt;太字&lt;/b&gt;" in html and "<b>太字</b>" not in html
    md = client.get(f"/api/teacher/rooms/{code}/report.md", auth=AUTH).text
    assert "# 迷子の地図" in md and "質問 1件" in md
    with client.websocket_connect("/ws") as a:
        a.send_json({"type": "hello", "code": code, "sid": "1TE24001X"})
        assert a.receive_json()["reason"] == "no_room"


def test_qr_svg(client):
    code, _ = open_room(client)
    r = client.get(f"/qr/{code}.svg")
    assert r.status_code == 200 and r.text.lstrip().startswith("<svg")


def test_rooms_survive_restart(tmp_path):
    cfg = Config(db=str(tmp_path / "z.sqlite3"), public_url="", teacher_user="teacher", teacher_password="pw",
                 secret=b"s" * 32, student_id_pattern=re.compile(r"^[0-9A-Z]{5,12}$"), ng_words=(), room_hours=4)
    with TestClient(create_app(cfg)) as c:
        code, _ = open_room(c)
        with c.websocket_connect("/ws") as a:
            a.send_json({"type": "hello", "code": code, "sid": "1TE24001X"})
            recv_until(a, "welcome")
            a.send_json({"type": "post", "kind": "question", "text": "再起動しても残る?"})
            recv_until(a, "ok")
    with TestClient(create_app(cfg)) as c:
        with c.websocket_connect("/ws") as a:
            a.send_json({"type": "hello", "code": code, "sid": "1TE24001X"})
            w = recv_until(a, "welcome")
            assert [p["text"] for p in w["posts"]] == ["再起動しても残る?"]
