#!/usr/bin/env python3
"""講義ノートの図を描くための最小限の SVG 部品。

figures/README.md の方針に従う:
  - 区別は 形・線種・ラベル でつける。色は補助
  - 明暗どちらのテーマでも読める
  - 文字は本文と同じ書体・サイズ感
"""
from html import escape

# 明暗両テーマ対応のスタイル。色に情報を担わせないので、
# 暗／明で入れ替わるのは「地と文字」だけ。
STYLE = """
svg { font-family: "Helvetica Neue", Arial, "Hiragino Sans", "Yu Gothic", "Noto Sans JP", sans-serif; }
/* 線のクラスを先に置く。fill: none を持たせているのは、線だけの図形が
   既定の黒で塗られないようにするため。ただしこれを塗りのクラスより
   後に書くと、同じ詳細度なので後勝ちで cls='tint2 s' の塗りが消える。
   実際そうなっており、全図で塗りが出ていなかった（2026-09-22 に修正）。 */
.s    { stroke: #16191d; stroke-width: 1.6; fill: none; }
.s2   { stroke: #16191d; stroke-width: 2.6; fill: none; }
.sm   { stroke: #5f6672; stroke-width: 1.2; fill: none; }
.sa   { stroke: #0b5cad; stroke-width: 2.2; fill: none; }
.dash { stroke-dasharray: 5 4; }
.dot  { stroke-dasharray: 1.5 3; }
/* 塗りのクラス。線のクラスより後に置くことで cls='tint2 s' が塗られる */
.bg   { fill: #ffffff; }
.ink  { fill: #16191d; }
.mut  { fill: #5f6672; }
.tint { fill: #eef1f5; }
.tint2{ fill: #dde4ec; }
.acc  { fill: #0b5cad; }
.accT { fill: #d9e6f4; }
.none { fill: none; }
text  { fill: #16191d; font-size: 14px; }
.t-s  { font-size: 12px; }
.t-xs { font-size: 10.5px; }
.t-l  { font-size: 17px; }
.t-xl { font-size: 21px; }
.b    { font-weight: 700; }
.i    { font-style: italic; }
.m    { font-family: "SF Mono", Menlo, Consolas, monospace; }
.lbl  { fill: #5f6672; }
@media (prefers-color-scheme: dark) {
  .bg   { fill: #14171b; }
  .ink  { fill: #e8ebef; }
  .mut  { fill: #9aa3b0; }
  .tint { fill: #232830; }
  .tint2{ fill: #2e343d; }
  .acc  { fill: #6ab0f3; }
  .accT { fill: #1e2c3c; }
  .s, .s2 { stroke: #e8ebef; }
  .sm   { stroke: #9aa3b0; }
  .sa   { stroke: #6ab0f3; }
  text  { fill: #e8ebef; }
  .lbl  { fill: #9aa3b0; }
}
"""

ARROW_DEFS = """
<defs>
 <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
   orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="ink"/></marker>
 <marker id="aa" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
   orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="acc"/></marker>
 <marker id="am" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6"
   orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="mut"/></marker>
 <marker id="o" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6">
   <circle cx="5" cy="5" r="3.5" class="bg s"/></marker>
</defs>
"""


class Fig:
    """SVG を組み立てる。座標は左上原点、単位なし（viewBox 座標）。"""

    def __init__(self, w, h, title=''):
        self.w, self.h, self.title = w, h, title
        self.parts = []

    # --- 基本図形 -------------------------------------------------
    def rect(self, x, y, w, h, cls='bg s', rx=0, **kw):
        r = f' rx="{rx}"' if rx else ''
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}"{r} '
                          f'class="{cls}"{self._kw(kw)}/>')
        return self

    def circle(self, cx, cy, r, cls='bg s', **kw):
        self.parts.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" class="{cls}"{self._kw(kw)}/>')
        return self

    def ellipse(self, cx, cy, rx, ry, cls='bg s', **kw):
        self.parts.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" '
                          f'class="{cls}"{self._kw(kw)}/>')
        return self

    def line(self, x1, y1, x2, y2, cls='s', arrow=None, **kw):
        m = f' marker-end="url(#{arrow})"' if arrow else ''
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                          f'class="{cls}"{m}{self._kw(kw)}/>')
        return self

    def path(self, d, cls='s', arrow=None, **kw):
        m = f' marker-end="url(#{arrow})"' if arrow else ''
        self.parts.append(f'<path d="{d}" class="{cls}"{m}{self._kw(kw)}/>')
        return self

    def poly(self, pts, cls='bg s', **kw):
        p = ' '.join(f'{x},{y}' for x, y in pts)
        self.parts.append(f'<polygon points="{p}" class="{cls}"{self._kw(kw)}/>')
        return self

    # --- 文字 -----------------------------------------------------
    def text(self, x, y, s, cls='', anchor='middle', baseline='middle', **kw):
        self.parts.append(
            f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="{baseline}" '
            f'class="{cls}"{self._kw(kw)}>{escape(str(s))}</text>')
        return self

    def lines(self, x, y, rows, cls='', anchor='middle', lh=16):
        """複数行のテキスト。rows は文字列のリスト、または (文字列, 追加class)。"""
        for i, row in enumerate(rows):
            s, extra = row if isinstance(row, tuple) else (row, '')
            self.text(x, y + i * lh, s, cls=(cls + ' ' + extra).strip(), anchor=anchor)
        return self

    # --- 組み合わせ部品 -------------------------------------------
    def box(self, x, y, w, h, label, cls='bg s', tcls='', rx=0, lh=16):
        """枠と、その中央に置いたラベル。label は文字列またはリスト。"""
        self.rect(x, y, w, h, cls, rx=rx)
        rows = label if isinstance(label, list) else [label]
        y0 = y + h / 2 - (len(rows) - 1) * lh / 2
        self.lines(x + w / 2, y0, rows, cls=tcls, lh=lh)
        return self

    def arrow(self, x1, y1, x2, y2, cls='s', label=None, lcls='t-s lbl', dy=-7, marker='a'):
        self.line(x1, y1, x2, y2, cls=cls, arrow=marker)
        if label is not None:
            self.text((x1 + x2) / 2, (y1 + y2) / 2 + dy, label, cls=lcls)
        return self

    def brace_v(self, x, y1, y2, label, side=1, cls='sm'):
        """縦の波括弧もどき（角括弧）とラベル。side=1 で右向き。"""
        t = 6 * side
        self.path(f'M{x - t},{y1} L{x},{y1} L{x},{y2} L{x - t},{y2}', cls=cls)
        self.text(x + 10 * side, (y1 + y2) / 2, label, cls='t-s lbl',
                  anchor='start' if side > 0 else 'end')
        return self

    def grid(self, x, y, cw, ch, cols, rows, cls='none s'):
        for c in range(cols + 1):
            self.line(x + c * cw, y, x + c * cw, y + rows * ch, cls=cls.replace('none ', ''))
        for r in range(rows + 1):
            self.line(x, y + r * ch, x + cols * cw, y + r * ch, cls=cls.replace('none ', ''))
        return self

    def caption(self, x, y, s, anchor='start'):
        self.text(x, y, s, cls='t-s lbl', anchor=anchor)
        return self

    # --- 出力 -----------------------------------------------------
    @staticmethod
    def _kw(kw):
        out = ''
        for k, v in kw.items():
            out += f' {k.replace("_", "-")}="{v}"'
        return out

    def render(self):
        t = f'<title>{escape(self.title)}</title>' if self.title else ''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
                f'width="{self.w}" height="{self.h}" role="img">{t}'
                f'<style>{STYLE}</style>{ARROW_DEFS}'
                f'<rect width="{self.w}" height="{self.h}" class="bg"/>'
                + ''.join(self.parts) + '</svg>\n')

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.render())
        return path
