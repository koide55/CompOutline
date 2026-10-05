"""部屋1つぶんの状態と、その集計。

通信も保存も知らない。押された・書かれたを受け取り、配るべき出来事を返すだけにしてある。
時刻はすべて引数 now（UNIX 秒）で受け取るので、試験で時間を進められる。
"""
from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field
from typing import Any

LOST_TTL = 90.0          # 迷子の信号が自然に消えるまで（§5.1）
PACE_TTL = 60.0          # ペースの信号が消えるまで（§5.3）
HEAVY_INTERVAL = 30.0    # 質問・意見は1人30秒に1件まで
POST_KEEP = 1000         # メモリに持つ投稿の数
HISTORY_SECONDS = 600    # 教員の画面に出す迷子率の線（直近10分）

WEATHERS = ["sunny", "fair", "cloudy", "rain", "storm"]

# 花火（§5.2）
FIREWORKS_WINDOW = 60.0
FIREWORKS_MIN_PEAK = 4
FIREWORKS_MIN_AHA = 5
FIREWORKS_COOLDOWN = 120.0

POST_STATUSES = ("open", "answered", "later", "hidden")
PROJECTOR_MODES = ("join", "board", "stream")


class Rejected(Exception):
    """学生に理由を返して断る操作。"""


def weather(present: int, lost: int) -> str:
    """迷子率から天気を決める。迷子が3人未満なら「晴れ」より悪くしない。"""
    if present <= 0 or lost <= 0:
        return "sunny"
    rate = lost / present
    if rate < 0.05:
        level = 0
    elif rate < 0.10:
        level = 1
    elif rate < 0.20:
        level = 2
    elif rate < 0.35:
        level = 3
    else:
        level = 4
    if lost < 3:
        level = min(level, 1)
    return WEATHERS[level]


def clean_text(text: Any, limit: int, ng_words: tuple[str, ...] = ()) -> str:
    if not isinstance(text, str):
        raise Rejected("文字を入れてください")
    text = re.sub(r"[\x00-\x08\x0b-\x1f\x7f]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        raise Rejected("文字を入れてください")
    if len(text) > limit:
        raise Rejected(f"{limit}字までです")
    for word in ng_words:
        if word and word in text:
            text = text.replace(word, "＊" * len(word))
    return text


# 投稿の種類（学生の画面の4つのボタン）
#   votable: 「同じく」を押せるか。押せるものは多い順に教員へ届く
#   limit:   字数の上限
#   slow:    重い投稿（質問・意見）は1人30秒に1件まで。コメントは教員が決めた間隔
KINDS: dict[str, dict[str, Any]] = {
    "comment": {"label": "コメント", "votable": False, "limit": 80, "slow": False},
    "question": {"label": "質問", "votable": True, "limit": 200, "slow": True},
    "opinion": {"label": "ご意見申す", "votable": True, "limit": 200, "slow": True},
    "naive": {"label": "素人質問ですが", "votable": True, "limit": 200, "slow": True},
}


@dataclass
class Post:
    id: int
    t: float
    slide: int
    kind: str
    text: str
    named: str | None = None          # 学生が自分で添えた学生番号。匿名なら None
    voters: set[str] = field(default_factory=set)
    status: str = "open"              # open / answered / later / hidden

    @property
    def votable(self) -> bool:
        return KINDS[self.kind]["votable"]

    def public(self, voter: str | None = None) -> dict[str, Any]:
        d = {"id": self.id, "t": round(self.t), "slide": self.slide, "kind": self.kind, "text": self.text,
             "votes": len(self.voters), "status": self.status}
        if voter is not None:
            d["mine"] = voter in self.voters
        return d

    def for_teacher(self) -> dict[str, Any]:
        d = self.public()
        d["named"] = self.named
        return d


@dataclass
class Settings:
    comments_open: bool = True       # コメントを受け付けるか（質問・意見は止めない）
    comment_interval: float = 10.0   # コメントは1人何秒に1件まで
    show_weather: bool = True        # 学生の画面にも天気を出すか

    def public(self) -> dict[str, Any]:
        return {"comments_open": self.comments_open, "comment_interval": self.comment_interval,
                "show_weather": self.show_weather}


class Room:
    def __init__(self, room_id: int, code: str, key: str, title: str, opened_at: float,
                 ng_words: tuple[str, ...] = ()):
        self.id = room_id
        self.code = code
        self.key = key
        self.title = title
        self.opened_at = opened_at
        self.ng_words = ng_words
        self.slide = 1
        self.settings = Settings()
        self.projector_mode = "join"

        self.attendance: set[str] = set()       # 入室した学生番号（出席の記録）
        self.connections: dict[str, int] = {}   # 学生番号 → 開いている接続の数
        self.lost: dict[str, float] = {}        # 学生番号 → 迷子が消える時刻
        self.pace: dict[str, tuple[str, float]] = {}
        self.aha: deque[float] = deque()        # 「わかった！」の時刻
        self.history: deque[tuple[float, int, int]] = deque()  # (時刻, 在室, 迷子)
        self.last_heavy: dict[str, float] = {}     # 質問・意見を最後に送った時刻
        self.last_comment: dict[str, float] = {}
        self.last_fireworks = 0.0

        self.posts: dict[int, Post] = {}   # id の順（dict は挿入順を保つ）
        self._next_id = 1

    # ---- 時刻 ----
    def rel(self, now: float) -> float:
        return max(0.0, now - self.opened_at)

    # ---- 入退室 ----
    def connect(self, sid: str) -> bool:
        """接続を数える。初めての入室なら True（出席として記録する）。"""
        self.connections[sid] = self.connections.get(sid, 0) + 1
        first = sid not in self.attendance
        self.attendance.add(sid)
        return first

    def disconnect(self, sid: str) -> None:
        n = self.connections.get(sid, 0) - 1
        if n > 0:
            self.connections[sid] = n
        else:
            self.connections.pop(sid, None)

    @property
    def present(self) -> int:
        return len(self.connections)

    # ---- 信号 ----
    def expire(self, now: float) -> None:
        for sid, until in list(self.lost.items()):
            if until <= now:
                del self.lost[sid]
        for sid, (_, until) in list(self.pace.items()):
            if until <= now:
                del self.pace[sid]
        while self.aha and self.aha[0] < now - FIREWORKS_WINDOW:
            self.aha.popleft()

    def press_lost(self, sid: str, now: float) -> float:
        self.lost[sid] = now + LOST_TTL
        return LOST_TTL

    def press_got(self, sid: str, now: float) -> None:
        if self.lost.pop(sid, None) is not None:
            self.aha.append(now)

    def press_pace(self, sid: str, direction: str, now: float) -> float:
        if direction not in ("slow", "fast"):
            raise Rejected("ペースは slow か fast です")
        current = self.pace.get(sid)
        if current and current[0] == direction and current[1] > now:
            del self.pace[sid]   # 同じ側をもう一度押すと取り消し
            return 0.0
        self.pace[sid] = (direction, now + PACE_TTL)
        return PACE_TTL

    def you(self, sid: str, now: float) -> dict[str, Any]:
        lost = self.lost.get(sid)
        pace = self.pace.get(sid)
        return {
            "lost_left": round(max(0.0, lost - now), 1) if lost else 0,
            "pace": pace[0] if pace and pace[1] > now else None,
            "pace_left": round(max(0.0, pace[1] - now), 1) if pace and pace[1] > now else 0,
        }

    def counts(self, now: float) -> dict[str, Any]:
        self.expire(now)
        # 接続していない学生の迷子は数えない（ページを閉じた人で天気を悪くしない）
        lost = sum(1 for sid in self.lost if sid in self.connections)
        slow = sum(1 for sid, (d, _) in self.pace.items() if d == "slow" and sid in self.connections)
        fast = sum(1 for sid, (d, _) in self.pace.items() if d == "fast" and sid in self.connections)
        present = self.present
        return {"present": present, "joined": len(self.attendance), "lost": lost,
                "aha": len(self.aha), "slow": slow, "fast": fast,
                "weather": weather(present, lost), "slide": self.slide,
                "t": round(self.rel(now))}

    def record(self, now: float) -> dict[str, Any]:
        """1秒に1回呼ぶ。直近の線を伸ばし、花火を上げるか決める。"""
        c = self.counts(now)
        self.history.append((now, c["present"], c["lost"]))
        while self.history and self.history[0][0] < now - HISTORY_SECONDS:
            self.history.popleft()
        c["fireworks"] = self._fireworks(now, c["lost"])
        return c

    def _fireworks(self, now: float, lost_now: int) -> int:
        if now - self.last_fireworks < FIREWORKS_COOLDOWN:
            return 0
        recent = [lost for (t, _, lost) in self.history if t >= now - FIREWORKS_WINDOW]
        if not recent:
            return 0
        peak = max(recent)
        if peak < FIREWORKS_MIN_PEAK or lost_now > peak / 2:
            return 0
        if len(self.aha) < FIREWORKS_MIN_AHA:
            return 0
        self.last_fireworks = now
        return len(self.aha)

    def history_series(self) -> list[list[float]]:
        return [[round(self.rel(t)), present, lost] for (t, present, lost) in self.history]

    # ---- 投稿 ----
    def post(self, sid: str, kind: Any, text: Any, named: bool, now: float) -> Post:
        spec = KINDS.get(kind) if isinstance(kind, str) else None
        if spec is None:
            raise Rejected("投稿の種類が不正です")
        if spec["slow"]:
            last, interval, what = self.last_heavy.get(sid), HEAVY_INTERVAL, spec["label"]
        else:
            if not self.settings.comments_open:
                raise Rejected("いまはコメントを止めています（質問・意見は送れます）")
            last, interval, what = self.last_comment.get(sid), self.settings.comment_interval, "コメント"
        if last is not None and now - last < interval:
            raise Rejected(f"{what}はあと {int(interval - (now - last)) + 1} 秒待ってください")
        text = clean_text(text, spec["limit"], self.ng_words)
        p = Post(self._next_id, self.rel(now), self.slide, kind, text, sid if named else None)
        self._next_id += 1
        self.posts[p.id] = p
        while len(self.posts) > POST_KEEP:
            del self.posts[next(iter(self.posts))]
        (self.last_heavy if spec["slow"] else self.last_comment)[sid] = now
        return p

    def metoo(self, voter: str, pid: Any) -> Post:
        p = self.posts.get(pid) if isinstance(pid, int) else None
        if p is None or p.status == "hidden" or not p.votable:
            raise Rejected("その投稿には押せません")
        if voter in p.voters:
            p.voters.discard(voter)    # もう一度押すと取り消し
        else:
            p.voters.add(voter)
        return p

    def mark(self, pid: Any, status: Any) -> Post:
        p = self.posts.get(pid) if isinstance(pid, int) else None
        if p is None:
            raise Rejected("その投稿はありません")
        if status not in POST_STATUSES:
            raise Rejected("状態が不正です")
        p.status = status
        return p

    def visible_posts(self, voter: str | None = None, limit: int = 200) -> list[dict[str, Any]]:
        ps = [p for p in self.posts.values() if p.status != "hidden"][-limit:]
        return [p.public(voter) for p in ps]

    # ---- 教員の操作 ----
    def set_slide(self, no: Any) -> int:
        if not isinstance(no, int) or not 1 <= no <= 999:
            raise Rejected("スライド番号が不正です")
        self.slide = no
        return no

    def update_settings(self, data: dict[str, Any]) -> Settings:
        if "comments_open" in data:
            self.settings.comments_open = bool(data["comments_open"])
        if "comment_interval" in data:
            v = data["comment_interval"]
            if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 600:
                raise Rejected("コメントの間隔は0〜600秒です")
            self.settings.comment_interval = float(v)
        if "show_weather" in data:
            self.settings.show_weather = bool(data["show_weather"])
        return self.settings

    def set_projector(self, mode: Any) -> str:
        if mode not in PROJECTOR_MODES:
            raise Rejected("投影の切り替え先が不正です")
        self.projector_mode = mode
        return mode

    # ---- 再起動から戻す ----
    def restore(self, posts: list[Post], attendance: set[str]) -> None:
        for p in posts:
            self.posts[p.id] = p
            self._next_id = max(self._next_id, p.id + 1)
        self.attendance |= attendance
