#!/usr/bin/env python3
"""PowerPoint スライドのベクタ図形を取り出す。

小出先生が PowerPoint 上で図形として描いた図は、スライド XML の中に
座標つきで入っている。写真や引用画像（p:pic）とは違い、これは自作物なので
そのまま素材として使える。ここではその図形を位置・大きさ・種類・文字だけの
素朴な辞書に落とし、描画は svgkit 側の統一スタイルに任せる。

使い方:
    python3 tools/pptx_shapes.py CompOutline2024.pptx 40          # 一覧を見る
    python3 tools/pptx_shapes.py CompOutline2024.pptx 40 --json out.json
"""
import argparse
import json
import zipfile
from xml.etree import ElementTree as ET

A = '{http://schemas.openxmlformats.org/drawingml/2006/main}'
P = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
EMU = 12700.0   # 1pt = 12700 EMU


def slide_files(z):
    """presentation.xml の並び順でスライドのファイル名を返す。"""
    pres = ET.fromstring(z.read('ppt/presentation.xml'))
    rels = ET.fromstring(z.read('ppt/_rels/presentation.xml.rels'))
    rmap = {c.get('Id'): c.get('Target').split('/')[-1] for c in rels}
    return [rmap[s.get(R + 'id')] for s in pres.find(P + 'sldIdLst')]


def _xfrm(node):
    x = node.find(A + 'xfrm')
    if x is None:
        return None
    off, ext = x.find(A + 'off'), x.find(A + 'ext')
    if off is None or ext is None:
        return None
    d = dict(x=int(off.get('x')), y=int(off.get('y')),
             w=int(ext.get('cx')), h=int(ext.get('cy')),
             rot=int(x.get('rot') or 0), fh=x.get('flipH') == '1', fv=x.get('flipV') == '1')
    cho, che = x.find(A + 'chOff'), x.find(A + 'chExt')
    if cho is not None and che is not None:
        d['chx'], d['chy'] = int(cho.get('x')), int(cho.get('y'))
        d['chw'], d['chh'] = int(che.get('cx')), int(che.get('cy'))
    return d


def _text(sp):
    """段落ごとにまとめた文字列のリストと、代表の文字サイズ・太字。"""
    tx = sp.find(P + 'txBody')
    if tx is None:
        return [], None, False
    paras, size, bold = [], None, False
    for p in tx.findall(A + 'p'):
        s = ''.join(t.text or '' for t in p.iter(A + 't'))
        if s.strip():
            paras.append(s.strip())
        for rpr in p.iter(A + 'rPr'):
            if size is None and rpr.get('sz'):
                size = int(rpr.get('sz')) / 100.0
            if rpr.get('b') == '1':
                bold = True
    return paras, size, bold


def _geom(sp):
    g = sp.find('./' + P + 'spPr/' + A + 'prstGeom')
    if g is not None:
        return g.get('prst')
    return 'custom' if sp.find('./' + P + 'spPr/' + A + 'custGeom') is not None else 'rect'


def _fill(sp):
    spr = sp.find(P + 'spPr')
    if spr is None:
        return 'none'
    if spr.find(A + 'noFill') is not None:
        return 'none'
    sf = spr.find(A + 'solidFill')
    if sf is not None:
        c = sf.find(A + 'srgbClr')
        if c is not None:
            return '#' + c.get('val')
        c = sf.find(A + 'schemeClr')
        if c is not None:
            return 'scheme:' + c.get('val')
        return 'solid'
    # p:style の fillRef でテーマ色が指定されている場合
    if sp.find('./' + P + 'style/' + A + 'fillRef') is not None:
        return 'themed'
    return 'none'


def _arrows(sp):
    ln = sp.find('./' + P + 'spPr/' + A + 'ln')
    if ln is None:
        return False, False
    h = ln.find(A + 'headEnd')
    t = ln.find(A + 'tailEnd')
    return (h is not None and (h.get('type') or 'none') != 'none',
            t is not None and (t.get('type') or 'none') != 'none')


def _stroked(sp):
    """枠線が見えるか。塗りなし・枠なしの「ただの文字」と、枠のある箱を区別する。"""
    ln = sp.find('./' + P + 'spPr/' + A + 'ln')
    if ln is not None:
        if ln.find(A + 'noFill') is not None:
            return False
        if ln.find(A + 'solidFill') is not None or ln.get('w'):
            return True
    # p:style の lnRef はテーマの線を使う指定
    if sp.find('./' + P + 'style/' + A + 'lnRef') is not None:
        return True
    # テキストボックスは既定で枠なし、オートシェイプは既定で枠あり
    return sp.find('./' + P + 'nvSpPr/' + P + 'cNvSpPr[@txBox="1"]') is None


def walk(node, tf, out, depth=0):
    """図形ツリーを再帰的にたどる。tf は親グループの座標変換。"""
    for ch in node:
        tag = ch.tag
        if tag in (P + 'sp', P + 'cxnSp'):
            x = _xfrm(ch.find(P + 'spPr'))
            if x is None:
                continue
            paras, size, bold = _text(ch)
            ph = ch.find('.//' + P + 'ph')
            hx, tl = _arrows(ch)
            out.append(dict(
                kind='cxn' if tag == P + 'cxnSp' else 'sp',
                geom=_geom(ch), fill=_fill(ch),
                ph=(ph.get('type') if ph is not None else None),
                text=paras, size=size, bold=bold, stroked=_stroked(ch),
                head=hx, tail=tl, depth=depth,
                **_apply(x, tf)))
        elif tag == P + 'grpSp':
            x = _xfrm(ch.find(P + 'grpSpPr'))
            walk(ch, _compose(tf, x), out, depth + 1)
        elif tag == P + 'pic':
            x = _xfrm(ch.find(P + 'spPr'))
            if x:
                out.append(dict(kind='pic', geom='rect', fill='none', ph=None,
                                text=[], size=None, bold=False, stroked=False,
                                head=False, tail=False,
                                depth=depth, **_apply(x, tf)))


def _compose(tf, x):
    """親の変換 tf に、グループ x の子座標系への写像を合成する。"""
    if x is None:
        return tf
    box = _apply(x, tf)
    cw = x.get('chw') or x['w'] or 1
    chh = x.get('chh') or x['h'] or 1
    return dict(sx=tf['sx'] * (x['w'] / cw), sy=tf['sy'] * (x['h'] / chh),
                dx=box['x'] - x.get('chx', 0) * tf['sx'] * (x['w'] / cw),
                dy=box['y'] - x.get('chy', 0) * tf['sy'] * (x['h'] / chh))


def _apply(x, tf):
    return dict(x=round(x['x'] * tf['sx'] + tf['dx'], 1),
                y=round(x['y'] * tf['sy'] + tf['dy'], 1),
                w=round(x['w'] * tf['sx'], 1), h=round(x['h'] * tf['sy'], 1),
                rot=round(x['rot'] / 60000.0, 1), fh=x['fh'], fv=x['fv'])


def extract(pptx, slide_no, scale=1.0 / EMU):
    """1枚のスライドの図形を pt 単位で返す。"""
    z = zipfile.ZipFile(pptx)
    fn = slide_files(z)[slide_no - 1]
    root = ET.fromstring(z.read('ppt/slides/' + fn))
    tree = root.find('./' + P + 'cSld/' + P + 'spTree')
    out = []
    walk(tree, dict(sx=scale, sy=scale, dx=0, dy=0), out)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pptx')
    ap.add_argument('slide', type=int)
    ap.add_argument('--json')
    a = ap.parse_args()
    shapes = extract(a.pptx, a.slide)
    if a.json:
        json.dump(shapes, open(a.json, 'w'), ensure_ascii=False, indent=1)
        print(f'{len(shapes)} 個の図形を {a.json} に書き出した')
        return
    for s in shapes:
        t = ' / '.join(s['text'])[:44]
        print(f"{'  ' * s['depth']}{s['kind']:4s} {s['geom']:18s} "
              f"({s['x']:6.0f},{s['y']:6.0f}) {s['w']:5.0f}x{s['h']:5.0f} "
              f"fill={s['fill']:12s} {'→' if s['tail'] else ' '}{'←' if s['head'] else ' '} {t}")


if __name__ == '__main__':
    main()
