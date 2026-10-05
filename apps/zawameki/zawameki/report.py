"""講義後の「迷子の地図」（SPEC §5.7）。HTML と Markdown で出す。"""
from __future__ import annotations

import sqlite3
import time
from html import escape
from typing import Any

from .room import KINDS
from .store import Store

TICK_SECONDS = 5  # ticks 表に1行を書く間隔（hub.SAVE_TICK）
STATUS = {"open": "未対応", "answered": "答えた", "later": "あとで", "hidden": "隠した"}


def summarize(store: Store, row: sqlite3.Row) -> dict[str, Any]:
    rid = row["id"]
    ticks = store.ticks(rid)
    posts = [dict(p) for p in store.posts(rid) if p["status"] != "hidden"]
    voices = [p for p in posts if KINDS[p["kind"]]["votable"]]   # 質問・ご意見・素人質問
    comments = [p for p in posts if not KINDS[p["kind"]]["votable"]]
    slides: dict[int, dict[str, Any]] = {}

    def slot(no: int) -> dict[str, Any]:
        return slides.setdefault(no, {"slide": no, "seconds": 0, "peak": 0, "peak_rate": 0.0,
                                      "rate_sum": 0.0, "n": 0, "voices": 0, "votes": 0, "comments": 0})

    for t in ticks:
        s = slot(t["slide"])
        s["seconds"] += TICK_SECONDS
        s["peak"] = max(s["peak"], t["lost"])
        if t["present"]:
            rate = t["lost"] / t["present"]
            s["peak_rate"] = max(s["peak_rate"], rate)
            s["rate_sum"] += rate
            s["n"] += 1
    for p in voices:
        s = slot(p["slide"])
        s["voices"] += 1
        s["votes"] += p["votes"]
    for p in comments:
        slot(p["slide"])["comments"] += 1
    for s in slides.values():
        s["mean_rate"] = s["rate_sum"] / s["n"] if s["n"] else 0.0
    by_slide = sorted(slides.values(), key=lambda s: s["slide"])
    hot = sorted((s for s in by_slide if s["peak"] > 0), key=lambda s: (-s["peak_rate"], -s["peak"]))[:5]
    return {
        "title": row["title"], "code": row["code"], "opened_at": row["opened_at"], "closed_at": row["closed_at"],
        "joined": len(store.attendance(rid)),
        "peak_present": max((t["present"] for t in ticks), default=0),
        "ticks": ticks, "slides": by_slide, "hot": hot,
        "voices": sorted(voices, key=lambda p: (-p["votes"], p["id"])),
        "comments": comments,
        "by_kind": {k: sum(1 for p in posts if p["kind"] == k) for k in KINDS},
    }


def _when(ts: float | None) -> str:
    return time.strftime("%Y-%m-%d %H:%M", time.localtime(ts)) if ts else "（開いたまま）"


def _mmss(t: float) -> str:
    t = int(t)
    return f"{t // 60}:{t % 60:02d}"


def _chart(ticks: list[sqlite3.Row]) -> str:
    """迷子率の推移を SVG の折れ線で描く。"""
    if not ticks:
        return "<p class=muted>記録がありません。</p>"
    w, h, pad = 900, 220, 34
    tmax = max(t["t"] for t in ticks) or 1
    xs = lambda t: pad + (w - 2 * pad) * t / tmax
    ys = lambda r: h - pad - (h - 2 * pad) * min(r, 0.5) / 0.5
    pts = " ".join(f"{xs(t['t']):.1f},{ys(t['lost'] / t['present'] if t['present'] else 0):.1f}" for t in ticks)
    grid = []
    for r, label in ((0.05, "5%"), (0.2, "20%"), (0.35, "35%"), (0.5, "50%")):
        y = ys(r)
        grid.append(f'<line x1="{pad}" x2="{w - pad}" y1="{y:.1f}" y2="{y:.1f}" class="grid"/>'
                    f'<text x="{pad - 4}" y="{y + 4:.1f}" text-anchor="end">{label}</text>')
    step = 600 if tmax > 1800 else 300
    for m in range(0, int(tmax) + 1, step):
        grid.append(f'<text x="{xs(m):.1f}" y="{h - pad + 16}" text-anchor="middle">{m // 60}分</text>')
    # スライドの切り替わりに縦線
    marks, last = [], None
    for t in ticks:
        if t["slide"] != last:
            marks.append(f'<line x1="{xs(t["t"]):.1f}" x2="{xs(t["t"]):.1f}" y1="{pad}" y2="{h - pad}" class="slide"/>'
                         f'<text x="{xs(t["t"]) + 2:.1f}" y="{pad - 4}" class="sl">{t["slide"]}</text>')
            last = t["slide"]
    return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="迷子率の推移">'
            f'{"".join(grid)}{"".join(marks)}<polyline points="{pts}" class="line"/></svg>')


def html(store: Store, row: sqlite3.Row) -> str:
    s = summarize(store, row)
    code = escape(s["code"])
    rows = "".join(
        f"<tr><td>{x['slide']}</td><td>{_mmss(x['seconds'])}</td><td>{x['peak']}</td>"
        f"<td><span class=bar style=\"width:{min(100, x['peak_rate'] * 200):.0f}px\"></span>{x['peak_rate']:.0%}</td>"
        f"<td>{x['mean_rate']:.1%}</td><td>{x['voices']}</td><td>{x['votes']}</td><td>{x['comments']}</td></tr>"
        for x in s["slides"])
    hot = "".join(f"<li>スライド {x['slide']} — 迷子 最大 {x['peak']}人（{x['peak_rate']:.0%}）</li>" for x in s["hot"]) \
        or "<li>迷子の山はありませんでした。</li>"
    qs = "".join(
        f"<tr><td>{q['votes']}</td><td>{q['slide']}</td><td><span class=\"badge k-{q['kind']}\">{KINDS[q['kind']]['label']}</span></td>"
        f"<td>{STATUS[q['status']]}</td><td>{escape(q['text'])}</td><td>{escape(q['named'] or '')}</td></tr>"
        for q in s["voices"]) \
        or "<tr><td colspan=6 class=muted>質問・意見はありませんでした。</td></tr>"
    rs = "".join(
        f"<li><span class=muted>{_mmss(r['t'])} / S{r['slide']}</span> {escape(r['text'])}"
        f"{' <span class=muted>(' + escape(r['named']) + ')</span>' if r['named'] else ''}</li>" for r in s["comments"]) \
        or "<li class=muted>コメントはありませんでした。</li>"
    kinds = "".join(f"<div>{KINDS[k]['label']}<b>{n}件</b></div>" for k, n in s["by_kind"].items())
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>迷子の地図 — {escape(s['title'])}</title>
<link rel="icon" href="data:,">
<link rel="stylesheet" href="/static/common.css">
<style>
 main{{max-width:960px;margin:0 auto;padding:16px}}
 table{{border-collapse:collapse;width:100%;font-size:14px}}
 th,td{{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}}
 svg{{width:100%;height:auto;background:var(--panel);border-radius:12px}}
 svg text{{font-size:11px;fill:var(--muted)}} svg .sl{{fill:var(--accent)}}
 svg .grid{{stroke:var(--line)}} svg .slide{{stroke:var(--accent);stroke-opacity:.25}}
 svg .line{{fill:none;stroke:var(--storm);stroke-width:2}}
 .bar{{display:inline-block;height:10px;background:var(--storm);border-radius:3px;margin-right:6px;vertical-align:middle}}
 .stats{{display:flex;gap:12px;flex-wrap:wrap}} .stats div{{background:var(--panel);border-radius:12px;padding:10px 14px}}
 .stats b{{display:block;font-size:24px}}
 ul.remarks{{list-style:none;padding:0;columns:2;font-size:14px}} ul.remarks li{{break-inside:avoid;padding:3px 0}}
 @media (max-width:640px){{ul.remarks{{columns:1}}}}
</style></head><body><main>
<p><a href="/teacher">← 部屋の一覧</a></p>
<h1>迷子の地図 — {escape(s['title'])}</h1>
<p class=muted>部屋 {code}　{_when(s['opened_at'])} 〜 {_when(s['closed_at'])}</p>
<div class=stats>
 <div>入室<b>{s['joined']}人</b></div><div>同時在室の最大<b>{s['peak_present']}人</b></div>
 {kinds}
</div>
<h2>迷子率の推移</h2>{_chart(s['ticks'])}
<h2>迷子の多かったスライド</h2><ol>{hot}</ol>
<h2>スライドごと</h2>
<table><tr><th>スライド</th><th>滞在</th><th>迷子 最大</th><th>迷子率 最大</th><th>迷子率 平均</th><th>質問・意見</th><th>同じく</th><th>コメント</th></tr>{rows}</table>
<h2>質問・意見（同じく の多い順）</h2>
<table><tr><th>同じく</th><th>スライド</th><th>種類</th><th>状態</th><th>本文</th><th>記名</th></tr>{qs}</table>
<h2>コメント</h2><ul class=remarks>{rs}</ul>
<h2>書き出し</h2>
<p><a href="/api/teacher/rooms/{code}/report.md">Markdown</a> ・
<a href="/api/teacher/rooms/{code}/posts.csv">投稿 CSV</a> ・
<a href="/api/teacher/rooms/{code}/ticks.csv">時系列 CSV</a> ・
<a href="/api/teacher/rooms/{code}/attendance.csv">出席 CSV</a></p>
</main></body></html>"""


def markdown(store: Store, row: sqlite3.Row) -> str:
    s = summarize(store, row)
    out = [f"# 迷子の地図 — {s['title']}", "",
           f"- 部屋: {s['code']}（{_when(s['opened_at'])} 〜 {_when(s['closed_at'])}）",
           f"- 入室 {s['joined']}人 / 同時在室の最大 {s['peak_present']}人",
           "- " + " / ".join(f"{KINDS[k]['label']} {n}件" for k, n in s["by_kind"].items()),
           "", "## 迷子の多かったスライド", ""]
    out += [f"1. スライド {x['slide']} — 迷子 最大 {x['peak']}人（{x['peak_rate']:.0%}）" for x in s["hot"]] or ["（なし）"]
    out += ["", "## スライドごと", "",
            "| スライド | 滞在 | 迷子 最大 | 迷子率 最大 | 迷子率 平均 | 質問・意見 | 同じく | コメント |",
            "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    out += [f"| {x['slide']} | {_mmss(x['seconds'])} | {x['peak']} | {x['peak_rate']:.0%} | {x['mean_rate']:.1%} "
            f"| {x['voices']} | {x['votes']} | {x['comments']} |" for x in s["slides"]]
    out += ["", "## 質問・意見（同じく の多い順）", "",
            "| 同じく | スライド | 種類 | 状態 | 本文 |", "| ---: | ---: | --- | --- | --- |"]
    out += [f"| {q['votes']} | {q['slide']} | {KINDS[q['kind']]['label']} | {STATUS[q['status']]} "
            f"| {q['text'].replace('|', '｜')} |" for q in s["voices"]]
    out += ["", "## コメント", ""]
    out += [f"- {_mmss(r['t'])} / S{r['slide']} {r['text']}" for r in s["comments"]]
    return "\n".join(out) + "\n"
