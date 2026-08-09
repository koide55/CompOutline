#!/usr/bin/env python3
"""抽出した PowerPoint 図形を、svgkit の統一スタイルで SVG に描き直す。

元の色やフォントはそのままにせず、位置と大きさと文字だけを引き継ぐ。
旧スライドは配色がばらばら（蛍光色の塗り、テーマ色依存）で、
そのまま持ってくると図ごとに見た目が変わってしまうため。

扱える図形は rect / roundRect / ellipse / triangle / line / connector / can に限る。
custGeom（フリーハンドの多角形）は無視するので、それが主役のスライドは
この変換器では絵にならない。その場合は手で描くこと。

使い方:
    python3 tools/pptx_to_svg.py CompOutline2024.pptx 40 -o figures/_draft/s40.svg
    python3 tools/pptx_to_svg.py CompOutline2024.pptx 40 --crop 0,90,700,470
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pptx_shapes import extract           # noqa: E402
from svgkit import Fig                    # noqa: E402

# 元の塗りを、統一パレットの3段階に丸める
def _fill_class(fill):
    if fill in ('none', None):
        return 'none s'
    if fill.startswith('scheme:bg') or fill in ('#FFFFFF',):
        return 'bg s'
    if fill in ('themed',) or fill.startswith('scheme:accent'):
        return 'tint s'
    return 'tint2 s'


SKIP_GEOM = {'custom'}


def render(shapes, crop=None, drop_text=(), scale=1.0):
    """図形のリストを SVG に。crop=(x,y,w,h) で切り出す。"""
    xs = [s for s in shapes if s['geom'] not in SKIP_GEOM and s['kind'] != 'pic']
    if crop:
        cx, cy, cw, ch = crop
        xs = [s for s in xs
              if s['x'] + s['w'] > cx and s['x'] < cx + cw
              and s['y'] + s['h'] > cy and s['y'] < cy + ch]
    else:
        cx = min(s['x'] for s in xs) - 10
        cy = min(s['y'] for s in xs) - 10
        cw = max(s['x'] + s['w'] for s in xs) - cx + 10
        ch = max(s['y'] + s['h'] for s in xs) - cy + 10

    f = Fig(round(cw * scale), round(ch * scale))

    def X(v):
        return round((v - cx) * scale, 1)

    def Y(v):
        return round((v - cy) * scale, 1)

    for s in xs:
        txt = [t for t in s['text'] if t not in drop_text and not t.isdigit()]
        x, y, w, h = X(s['x']), Y(s['y']), s['w'] * scale, s['h'] * scale
        g, fc = s['geom'], _fill_class(s['fill'])

        if s['kind'] == 'cxn' or g in ('line', 'straightConnector1'):
            x2 = x + (w if not s['fh'] else -w) if w else x
            y2 = y + (h if not s['fv'] else -h) if h else y
            if s['fh']:
                x, x2 = x + w, x
            if s['fv']:
                y, y2 = y + h, y
            f.line(x, y, x2 if w else x, y2 if h else y,
                   cls='s', arrow='a' if s['tail'] else None)
            continue

        if not txt and w < 3 and h < 3:
            continue

        if g in ('ellipse', 'can'):
            f.ellipse(x + w / 2, y + h / 2, w / 2, h / 2, cls=fc)
        elif g in ('triangle',):
            f.poly([(x + w / 2, y), (x + w, y + h), (x, y + h)], cls=fc)
        elif g in ('rtTriangle',):
            f.poly([(x, y), (x + w, y + h), (x, y + h)], cls=fc)
        elif g == 'roundRect':
            f.rect(x, y, w, h, cls=fc, rx=min(10, h / 4))
        else:
            if not s.get('stroked', True) and fc == 'none s':
                pass          # 枠も塗りもない、ただの文字。箱は描かない
            else:
                f.rect(x, y, w, h, cls=fc if s.get('stroked', True) else fc.replace(' s', ''))

        if txt:
            lh = 15
            y0 = y + h / 2 - (len(txt) - 1) * lh / 2
            f.lines(x + w / 2, y0, [t[:40] for t in txt],
                    cls='t-s' if (s['size'] or 14) < 15 else '', lh=lh)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('slide', type=int)
    ap.add_argument('-o', '--out')
    ap.add_argument('--crop', help='x,y,w,h（pt単位）')
    ap.add_argument('--scale', type=float, default=1.0)
    a = ap.parse_args()
    crop = tuple(float(v) for v in a.crop.split(',')) if a.crop else None
    f = render(extract(a.pptx, a.slide), crop=crop, scale=a.scale)
    out = a.out or f'figures/_draft/s{a.slide}.svg'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    f.save(out)
    print(f'{out} ({f.w}x{f.h})')


if __name__ == '__main__':
    main()
