"""全回の出席を CSV で書き出す。

    docker compose ... exec -T zawameki python -m zawameki.attendance            > 出席.csv
    docker compose ... exec -T zawameki python -m zawameki.attendance --matrix   > 出席簿.csv

既定は1行に1件（回・学生番号・入室時刻）。--matrix は学生番号 × 回の表（入室していれば 1）。
記録されるのは各回の**最初の入室時刻**だけで、退室や滞在時間は残らない。
"""
from __future__ import annotations

import argparse
import csv
import os
import sqlite3
import sys
import time


def _t(ts: float) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--db", default=os.environ.get("ZAWAMEKI_DB", "/data/zawameki.sqlite3"))
    ap.add_argument("--matrix", action="store_true", help="学生番号 × 回の表にする")
    args = ap.parse_args(argv)

    db = sqlite3.connect(f"file:{args.db}?mode=ro", uri=True)
    rooms = db.execute("SELECT id, code, title, opened_at FROM rooms ORDER BY opened_at").fetchall()
    rows = db.execute("SELECT room_id, student_id, joined_at FROM attendance").fetchall()

    sys.stdout.write("﻿")   # Excel で文字化けしないよう BOM を付ける
    w = csv.writer(sys.stdout)
    if args.matrix:
        present = {(rid, sid) for rid, sid, _ in rows}
        students = sorted({sid for _, sid, _ in rows})
        w.writerow(["student_id"] + [f"{_t(opened)[:10]} {title}" for _, _, title, opened in rooms] + ["出席回数"])
        for sid in students:
            marks = [1 if (rid, sid) in present else 0 for rid, *_ in rooms]
            w.writerow([sid] + marks + [sum(marks)])
    else:
        info = {rid: (code, title, opened) for rid, code, title, opened in rooms}
        w.writerow(["lecture_date", "title", "code", "student_id", "joined_at"])
        for rid, sid, joined in sorted(rows, key=lambda r: (info[r[0]][2], r[1])):
            code, title, opened = info[rid]
            w.writerow([_t(opened)[:10], title, code, sid, _t(joined)])


if __name__ == "__main__":
    main()
