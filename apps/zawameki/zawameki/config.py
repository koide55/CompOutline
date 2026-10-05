"""環境変数から設定を読む。値の意味は .env.example に書いてある。"""
from __future__ import annotations

import os
import re
import secrets
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    db: str
    public_url: str
    teacher_user: str
    teacher_password: str
    secret: bytes
    student_id_pattern: re.Pattern[str]
    ng_words: tuple[str, ...]
    room_hours: float


def _secret(db: str) -> bytes:
    """「同じく」の票を鍵つきハッシュにする鍵。無ければ DB の隣に作って残す。"""
    env = os.environ.get("ZAWAMEKI_SECRET", "")
    if env:
        return env.encode()
    if db == ":memory:":
        return secrets.token_bytes(32)
    path = Path(db).with_name("secret.key")
    if path.exists():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    key = secrets.token_bytes(32)
    path.write_bytes(key)
    path.chmod(0o600)
    return key


def load() -> Config:
    db = os.environ.get("ZAWAMEKI_DB", "/data/zawameki.sqlite3")
    password = os.environ.get("ZAWAMEKI_TEACHER_PASSWORD", "")
    if not password:
        # 教員の入口を無認証で開けない。起動のたびに作り直し、ログに1度だけ出す
        password = secrets.token_urlsafe(12)
        print(f"[zawameki] ZAWAMEKI_TEACHER_PASSWORD が未設定なので仮のパスワードを作った: {password}",
              file=sys.stderr, flush=True)
    ng = tuple(w.strip() for w in os.environ.get("ZAWAMEKI_NG_WORDS", "").split(",") if w.strip())
    ng_file = os.environ.get("ZAWAMEKI_NG_WORDS_FILE", "")
    if ng_file and Path(ng_file).exists():
        ng += tuple(w.strip() for w in Path(ng_file).read_text(encoding="utf-8").splitlines() if w.strip())
    return Config(
        db=db,
        public_url=os.environ.get("ZAWAMEKI_PUBLIC_URL", "").rstrip("/"),
        teacher_user=os.environ.get("ZAWAMEKI_TEACHER_USER", "teacher"),
        teacher_password=password,
        secret=_secret(db),
        student_id_pattern=re.compile(os.environ.get("ZAWAMEKI_STUDENT_ID_PATTERN", r"^[0-9A-Z]{5,12}$")),
        ng_words=ng,
        room_hours=float(os.environ.get("ZAWAMEKI_ROOM_HOURS", "4")),
    )
