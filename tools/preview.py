#!/usr/bin/env python3
"""SVG を PNG のコンタクトシートにまとめる（目視確認用）。

cairosvg が要るので、システムの python ではなく用意した仮想環境で動かす。
図が増えると1枚に詰め込みすぎるので、--per で1枚あたりの図数を切る。

    venv/bin/python tools/preview.py figures/fig-01-*.svg -o /tmp/sheet.png
"""
import argparse
import glob
import io
import os
import re

import cairosvg
from PIL import Image, ImageDraw

# cairosvg は <style> で指定した font-family のフォールバックをたどらず、
# 日本語が豆腐になる。属性で指定すると効くので、確認用の描画のときだけ
# CSS の指定を外して root の属性に置き換える。出力する SVG 自体は触らない。
QA_FONT = 'Arial Unicode MS'


def _for_raster(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'font-family:[^;}]*;?', '', s)
    return s.replace('<svg ', f'<svg font-family="{QA_FONT}" ', 1)


def sheet(paths, out, cols=2, width=760, pad=14, per=None, label_h=20):
    imgs = []
    for p in paths:
        png = cairosvg.svg2png(bytestring=_for_raster(p).encode(), output_width=width)
        im = Image.open(io.BytesIO(png)).convert('RGB')
        imgs.append((os.path.basename(p), im))
    if per:
        outs = []
        for i in range(0, len(imgs), per):
            o = out.replace('.png', f'-{i // per + 1}.png')
            outs.append(_one(imgs[i:i + per], o, cols, pad, label_h))
        return outs
    return [_one(imgs, out, cols, pad, label_h)]


def _one(imgs, out, cols, pad, label_h):
    rows = (len(imgs) + cols - 1) // cols
    cw = max(im.width for _, im in imgs) + pad
    heights = []
    for r in range(rows):
        chunk = imgs[r * cols:(r + 1) * cols]
        heights.append(max(im.height for _, im in chunk) + pad + label_h)
    sh = Image.new('RGB', (cw * cols + pad, sum(heights) + pad), 'white')
    d = ImageDraw.Draw(sh)
    y = pad
    for r in range(rows):
        x = pad
        for name, im in imgs[r * cols:(r + 1) * cols]:
            d.text((x, y), name, fill='#888')
            sh.paste(im, (x, y + label_h))
            d.rectangle([x - 1, y + label_h - 1, x + im.width, y + label_h + im.height],
                        outline='#ddd')
            x += cw
        y += heights[r]
    sh.save(out)
    print(out, sh.size)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('svgs', nargs='+')
    ap.add_argument('-o', '--out', default='/tmp/sheet.png')
    ap.add_argument('--cols', type=int, default=2)
    ap.add_argument('--width', type=int, default=760)
    ap.add_argument('--per', type=int)
    a = ap.parse_args()
    files = []
    for s in a.svgs:
        files += sorted(glob.glob(s)) if '*' in s else [s]
    sheet(files, a.out, cols=a.cols, width=a.width, per=a.per)
