"""SQLite への保存。

保存するのは「部屋」「出席」「投稿」「集計した時系列」だけである。
**学生番号と、匿名の投稿とを結びつける列は持たない**（SPEC §3）。
「同じく」の重複を数えるための票は鍵つきハッシュで持ち、部屋を閉じたら消す。
"""
from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Any

from .room import Post

SCHEMA = """
CREATE TABLE IF NOT EXISTS rooms (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  code TEXT NOT NULL,
  key TEXT NOT NULL,
  title TEXT NOT NULL,
  opened_at REAL NOT NULL,
  closed_at REAL,
  slide INTEGER NOT NULL DEFAULT 1,
  settings TEXT NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS rooms_code ON rooms(code, closed_at);
CREATE TABLE IF NOT EXISTS attendance (
  room_id INTEGER NOT NULL,
  student_id TEXT NOT NULL,
  joined_at REAL NOT NULL,
  PRIMARY KEY (room_id, student_id)
);
CREATE TABLE IF NOT EXISTS posts (
  room_id INTEGER NOT NULL,
  id INTEGER NOT NULL,
  t REAL NOT NULL,
  slide INTEGER NOT NULL,
  kind TEXT NOT NULL,
  text TEXT NOT NULL,
  named TEXT,
  status TEXT NOT NULL DEFAULT 'open',
  votes INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (room_id, id)
);
CREATE TABLE IF NOT EXISTS post_votes (
  room_id INTEGER NOT NULL,
  pid INTEGER NOT NULL,
  voter TEXT NOT NULL,
  PRIMARY KEY (room_id, pid, voter)
);
CREATE TABLE IF NOT EXISTS ticks (
  room_id INTEGER NOT NULL,
  t REAL NOT NULL,
  slide INTEGER NOT NULL,
  present INTEGER NOT NULL,
  lost INTEGER NOT NULL,
  aha INTEGER NOT NULL,
  slow INTEGER NOT NULL,
  fast INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS ticks_room ON ticks(room_id, t);
CREATE TABLE IF NOT EXISTS slides (
  room_id INTEGER NOT NULL,
  t REAL NOT NULL,
  no INTEGER NOT NULL
);
"""


class Store:
    def __init__(self, path: str | Path):
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        self.conn.executescript(SCHEMA)
        self.lock = threading.Lock()

    def _exec(self, sql: str, args: tuple = ()) -> sqlite3.Cursor:
        with self.lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur

    def _all(self, sql: str, args: tuple = ()) -> list[sqlite3.Row]:
        with self.lock:
            return self.conn.execute(sql, args).fetchall()

    # ---- 部屋 ----
    def create_room(self, code: str, key: str, title: str, opened_at: float) -> int:
        cur = self._exec("INSERT INTO rooms(code, key, title, opened_at) VALUES (?,?,?,?)",
                         (code, key, title, opened_at))
        return int(cur.lastrowid)

    def close_room(self, room_id: int, closed_at: float) -> None:
        self._exec("UPDATE rooms SET closed_at=? WHERE id=?", (closed_at, room_id))
        self._exec("DELETE FROM post_votes WHERE room_id=?", (room_id,))

    def save_room_state(self, room_id: int, slide: int, settings: dict[str, Any]) -> None:
        self._exec("UPDATE rooms SET slide=?, settings=? WHERE id=?",
                   (slide, json.dumps(settings), room_id))

    def open_rooms(self) -> list[sqlite3.Row]:
        return self._all("SELECT * FROM rooms WHERE closed_at IS NULL ORDER BY id")

    def room_by_code(self, code: str) -> sqlite3.Row | None:
        rows = self._all("SELECT * FROM rooms WHERE code=? ORDER BY id DESC LIMIT 1", (code,))
        return rows[0] if rows else None

    def room(self, room_id: int) -> sqlite3.Row | None:
        rows = self._all("SELECT * FROM rooms WHERE id=?", (room_id,))
        return rows[0] if rows else None

    def recent_rooms(self, limit: int = 30) -> list[sqlite3.Row]:
        return self._all(
            "SELECT r.*, (SELECT COUNT(*) FROM attendance a WHERE a.room_id=r.id) AS joined,"
            " (SELECT COUNT(*) FROM posts p WHERE p.room_id=r.id AND p.kind<>'comment') AS nquestions,"
            " (SELECT COUNT(*) FROM posts p WHERE p.room_id=r.id AND p.kind='comment') AS ncomments"
            " FROM rooms r ORDER BY r.id DESC LIMIT ?", (limit,))

    # ---- 出席 ----
    def add_attendance(self, room_id: int, student_id: str, at: float) -> None:
        self._exec("INSERT OR IGNORE INTO attendance(room_id, student_id, joined_at) VALUES (?,?,?)",
                   (room_id, student_id, at))

    def attendance(self, room_id: int) -> list[sqlite3.Row]:
        return self._all("SELECT student_id, joined_at FROM attendance WHERE room_id=? ORDER BY student_id",
                         (room_id,))

    # ---- 投稿 ----
    def add_post(self, room_id: int, p: Post) -> None:
        self._exec("INSERT INTO posts(room_id, id, t, slide, kind, text, named, status, votes)"
                   " VALUES (?,?,?,?,?,?,?,?,?)",
                   (room_id, p.id, p.t, p.slide, p.kind, p.text, p.named, p.status, len(p.voters)))

    def update_post(self, room_id: int, p: Post) -> None:
        self._exec("UPDATE posts SET status=?, votes=? WHERE room_id=? AND id=?",
                   (p.status, len(p.voters), room_id, p.id))

    def set_vote(self, room_id: int, pid: int, voter: str, on: bool) -> None:
        if on:
            self._exec("INSERT OR IGNORE INTO post_votes(room_id, pid, voter) VALUES (?,?,?)",
                       (room_id, pid, voter))
        else:
            self._exec("DELETE FROM post_votes WHERE room_id=? AND pid=? AND voter=?",
                       (room_id, pid, voter))

    def posts(self, room_id: int) -> list[sqlite3.Row]:
        return self._all("SELECT * FROM posts WHERE room_id=? ORDER BY id", (room_id,))

    def load_posts(self, room_id: int, limit: int) -> list[Post]:
        votes: dict[int, set[str]] = {}
        for row in self._all("SELECT pid, voter FROM post_votes WHERE room_id=?", (room_id,)):
            votes.setdefault(row["pid"], set()).add(row["voter"])
        rows = self._all("SELECT * FROM posts WHERE room_id=? ORDER BY id DESC LIMIT ?", (room_id, limit))
        return [Post(r["id"], r["t"], r["slide"], r["kind"], r["text"], r["named"],
                     votes.get(r["id"], set()), r["status"]) for r in reversed(rows)]

    # ---- 時系列 ----
    def add_tick(self, room_id: int, c: dict[str, Any]) -> None:
        self._exec("INSERT INTO ticks(room_id, t, slide, present, lost, aha, slow, fast)"
                   " VALUES (?,?,?,?,?,?,?,?)",
                   (room_id, c["t"], c["slide"], c["present"], c["lost"], c["aha"], c["slow"], c["fast"]))

    def ticks(self, room_id: int) -> list[sqlite3.Row]:
        return self._all("SELECT * FROM ticks WHERE room_id=? ORDER BY t", (room_id,))

    def add_slide(self, room_id: int, t: float, no: int) -> None:
        self._exec("INSERT INTO slides(room_id, t, no) VALUES (?,?,?)", (room_id, t, no))
