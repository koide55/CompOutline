"""第1〜4回の図。

[旧] と注記したものは CompOutline2024.pptx の該当スライドから
図形の座標を取り出して引き継いだもの（tools/pptx_shapes.py 参照）。
"""
from svgkit import Fig


# ---------------------------------------------------------------- 第1回
def f0101():
    """互除法の各ステップ"""
    f = Fig(700, 310)
    # 1071x462 の長方形から、正方形を順に切り取っていく
    S = 0.42
    x0, y0 = 80, 46
    W, H = 1071 * S, 462 * S
    # 462 の正方形 2つ（1071 = 462×2 + 147）
    for i in range(2):
        f.rect(x0 + i * H, y0, H, H, cls='tint s')
        f.text(x0 + i * H + H / 2, y0 + H / 2, '462', cls='t-s')
    # 残った 147×462 の帯から 147 の正方形 3つ（462 = 147×3 + 21）
    rx, sq = x0 + 2 * H, 147 * S
    for i in range(3):
        f.rect(rx, y0 + i * sq, sq, sq, cls='tint2 s')
    f.text(rx + sq / 2, y0 + sq / 2, '147', cls='t-xs')
    # 残った 147×21 の帯から 21 の正方形 7つ（147 = 21×7 + 0 → 割り切れた）
    qy, q = y0 + 3 * sq, 21 * S
    for i in range(7):
        f.rect(rx + i * q, qy, q, q, cls='accT sa')
    f.rect(x0, y0, W, H, cls='none s2')

    f.text(rx + sq + 34, qy + q / 2, '21', cls='t-s acc b', anchor='start')
    f.line(rx + sq + 4, qy + q / 2, rx + sq + 28, qy + q / 2, cls='sa')
    f.text(x0 + W / 2, y0 - 18, '1071', cls='t-s lbl')
    f.text(x0 - 14, y0 + H / 2, '462', cls='t-s lbl', anchor='end')
    f.text(40, 268, '1071 = 462×2 + 147   →   462 = 147×3 + 21   →   147 = 21×7 + 0',
           cls='t-s m', anchor='start')
    f.text(40, 292, '最後に残った正方形の一辺 21 が最大公約数', cls='t-s b', anchor='start')
    return f


def f0102():
    """[旧 slide 21] チューリングマシンの構成"""
    f = Fig(700, 330)
    cw, n = 26, 22
    tx, ty = 40, 200
    # テープ
    for i in range(n):
        f.rect(tx + i * cw, ty, cw, 46, cls='bg s')
    for i, ch in enumerate('101110110001'):
        f.text(tx + (5 + i) * cw + cw / 2, ty + 23, ch, cls='t-s m')
    f.text(tx - 14, ty + 23, '…', cls='lbl', anchor='end')
    f.text(tx + n * cw + 14, ty + 23, '…', cls='lbl', anchor='start')
    f.text(tx + n * cw / 2, ty + 70, '無限に長いテープ', cls='t-s lbl')

    # ヘッド
    hx = tx + 10 * cw + cw / 2
    f.poly([(hx, ty - 8), (hx - 9, ty - 24), (hx + 9, ty - 24)], cls='ink')
    f.line(hx, ty - 24, hx, ty - 56, cls='s')

    # 有限制御部
    f.rect(hx - 85, ty - 128, 170, 72, cls='tint s', rx=8)
    f.text(hx, ty - 108, '有限制御部', cls='b')
    f.text(hx, ty - 86, '現在の状態  q', cls='t-s m')
    f.text(hx, ty - 68, '（状態は有限個）', cls='t-xs lbl')

    # 読み書きの往復
    f.path(f'M{hx - 34},{ty - 56} L{hx - 34},{ty - 30}', cls='sa', arrow='aa')
    f.path(f'M{hx + 34},{ty - 30} L{hx + 34},{ty - 56}', cls='sa', arrow='aa')
    f.text(hx - 44, ty - 44, '書く記号', cls='t-xs lbl', anchor='end')
    f.text(hx + 44, ty - 44, '読んだ記号', cls='t-xs lbl', anchor='start')

    # 1ステップの説明
    f.rect(430, 30, 250, 92, cls='none sm dash', rx=6)
    f.text(555, 46, '1ステップですること', cls='t-s b')
    for i, s in enumerate(['① ヘッドの下の記号を読む', '② そこに記号を書く',
                           '③ ヘッドを左か右に1マス動かす', '④ 状態を変える']):
        f.text(444, 64 + i * 16, s, cls='t-xs', anchor='start')
    f.text(tx + n * cw / 2, ty + 96, 'ヘッドは左右に1マスずつ動ける', cls='t-xs lbl')
    return f


def f0103():
    """「1を足す機械」の状態遷移図"""
    f = Fig(560, 250)
    f.circle(160, 130, 46, cls='tint s')
    f.text(160, 130, 'carry', cls='b')
    f.circle(400, 130, 46, cls='bg s')
    f.circle(400, 130, 40, cls='none s')
    f.text(400, 130, 'halt', cls='b')
    # 開始
    f.arrow(60, 130, 112, 130, cls='s')
    f.text(60, 112, '開始', cls='t-xs lbl', anchor='start')
    # 自己ループ
    f.path('M136,90 C120,40 200,40 184,90', cls='s', arrow='a')
    f.text(160, 40, '1 / 0, 左へ', cls='t-s m')
    # carry -> halt
    f.arrow(206, 118, 354, 118, cls='s', label='0 / 1, 停止', lcls='t-s m', dy=-8)
    f.arrow(206, 146, 354, 146, cls='s', label='␣ / 1, 停止', lcls='t-s m', dy=18)
    f.text(280, 215, '読んだ記号 / 書く記号, 動作', cls='t-xs lbl')
    return f


def f0104():
    """停止問題の対角線論法"""
    f = Fig(560, 360)
    x0, y0, c = 130, 70, 66
    cols = ['x₁', 'x₂', 'x₃', 'x₄', '…']
    rows = ['P₁', 'P₂', 'P₃', 'P₄', '⋮']
    tbl = [['停', '止', '停', '止'],
           ['止', '止', '停', '停'],
           ['停', '停', '止', '停'],
           ['止', '停', '停', '止']]
    for j, cname in enumerate(cols):
        f.text(x0 + j * c + c / 2, y0 - 14, cname, cls='t-s lbl')
    for i, rname in enumerate(rows):
        f.text(x0 - 16, y0 + i * 40 + 20, rname, cls='t-s lbl', anchor='end')
    for i in range(4):
        for j in range(4):
            diag = i == j
            f.rect(x0 + j * c, y0 + i * 40, c, 40,
                   cls='accT s' if diag else 'bg s')
            f.text(x0 + j * c + c / 2, y0 + i * 40 + 20, tbl[i][j],
                   cls='t-s b acc' if diag else 't-s')
    f.text(x0 + 4 * c + 22, y0 + 80, '…', cls='lbl')
    f.text(x0 + 2 * c, y0 + 4 * 40 + 18, '⋮', cls='lbl')

    f.rect(x0, y0 + 190, 4 * c, 40, cls='tint2 s')
    f.text(x0 - 16, y0 + 210, 'trouble', cls='t-s b', anchor='end')
    for j in range(4):
        f.text(x0 + j * c + c / 2, y0 + 210, ['止', '停', '停', '止'][j], cls='t-s b')
    f.text(x0 + 2 * c, y0 + 250, '対角線をすべて反転させたもの', cls='t-s')
    f.text(x0 + 2 * c, y0 + 268, 'どの行とも1マス以上食い違う → 表のどこにも存在しない',
           cls='t-s b')
    for j in range(4):
        f.path(f'M{x0 + j * c + c / 2},{y0 + j * 40 + 42} L{x0 + j * c + c / 2},{y0 + 186}',
               cls='sa dot', arrow='aa')
    return f


# ---------------------------------------------------------------- 第2回
def f0201():
    """電圧レベルと状態の識別"""
    f = Fig(620, 340)
    for k, (bx, n, title) in enumerate([(80, 10, '10段階に区切る'), (380, 2, '2段階にする')]):
        f.text(bx + 70, 34, title, cls='b')
        f.rect(bx, 60, 140, 240, cls='none s')
        if n == 10:
            for i in range(10):
                f.line(bx, 60 + i * 24, bx + 140, 60 + i * 24, cls='sm')
                f.text(bx - 8, 60 + i * 24 + 12, str(9 - i), cls='t-xs lbl', anchor='end')
            # ばらつき
            for i, cy in enumerate([100, 172, 244]):
                f.rect(bx + 30 + i * 34, cy - 26, 14, 52, cls='accT sa')
            f.text(bx + 70, 320, 'ばらつきが隣の段階にはみ出す', cls='t-xs acc')
        else:
            f.rect(bx, 60, 140, 84, cls='tint s')
            f.text(bx + 70, 102, '1 の領域', cls='t-s')
            f.rect(bx, 144, 140, 72, cls='none sm dash')
            f.text(bx + 70, 180, '不定', cls='t-xs lbl')
            f.rect(bx, 216, 140, 84, cls='tint s')
            f.text(bx + 70, 258, '0 の領域', cls='t-s')
            for i, cy in enumerate([100, 258]):
                f.rect(bx + 40 + i * 40, cy - 26, 14, 52, cls='accT sa')
            f.text(bx + 70, 320, '同じばらつきが領域内に収まる', cls='t-xs acc')
    f.text(30, 180, '電圧', cls='t-s lbl')
    f.line(52, 300, 52, 60, cls='sm', arrow='am')
    f.text(50, 46, '3.3V', cls='t-xs lbl', anchor='end')
    f.text(50, 306, '0V', cls='t-xs lbl', anchor='end')
    return f


def f0202():
    """実数直線と浮動小数点数の分布"""
    f = Fig(680, 220)
    y = 130
    f.line(40, y, 650, y, cls='s', arrow='a')
    f.text(650, y + 22, '実数', cls='t-s lbl', anchor='end')
    # 指数ごとに間隔が倍になる
    x = 60
    step = 3.0
    while x < 640:
        f.line(x, y - 12, x, y + 12, cls='sm')
        x += step
        step *= 1.055
    for lx, lab in [(60, '0 の近く'), (330, ''), (600, '大きな値')]:
        if lab:
            f.text(lx, y + 40, lab, cls='t-s')
    f.text(150, y - 40, '密：表せる数が細かい', cls='t-s')
    f.text(520, y - 40, '疎：とびとびになる', cls='t-s')
    f.line(150, y - 28, 110, y - 16, cls='sm', arrow='am')
    f.line(520, y - 28, 560, y - 16, cls='sm', arrow='am')
    f.text(340, 40, '指数が1増えるごとに、隣どうしの間隔が2倍になる', cls='b')
    f.text(340, 190, '0.1 は2進数では循環小数 → 有限ビットでは表しきれない', cls='t-s')
    return f


def f0203():
    """オーダの伸び方"""
    import math
    f = Fig(660, 400)
    L, R, T, B = 90, 600, 40, 330
    f.line(L, B, R, B, cls='s', arrow='a')
    f.line(L, B, L, T, cls='s', arrow='a')
    f.text(R, B + 34, 'n（入力の大きさ）', cls='t-s lbl', anchor='end')
    f.text(L - 60, T + 6, '操作回数', cls='t-s lbl', anchor='start')
    f.text(L - 10, B, '1', cls='t-xs lbl', anchor='end')
    for p, lab in [(2, '10²'), (4, '10⁴'), (6, '10⁶'), (8, '10⁸')]:
        yy = B - p / 9.0 * (B - T)
        f.line(L, yy, R, yy, cls='sm dot')
        f.text(L - 10, yy, lab, cls='t-xs lbl', anchor='end')

    def curve(fn, cls, name, lx):
        pts = []
        for i in range(0, 101):
            n = 1 + i / 100.0 * 99
            v = fn(n)
            if v <= 0:
                continue
            p = math.log10(v)
            if p > 9:
                break          # 画面の上に振り切れたら、そこで描くのをやめる
            pts.append((L + i / 100.0 * (R - L), B - p / 9.0 * (B - T)))
        f.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts), cls=cls)
        px, py = pts[min(lx, len(pts) - 1)]
        f.text(px + 6, py - 10, name, cls='t-xs b', anchor='start')

    curve(lambda n: 1, 's', 'O(1)', 100)
    curve(lambda n: math.log2(n) if n > 1 else 1, 'sm', 'O(log n)', 100)
    curve(lambda n: n, 's dash', 'O(n)', 96)
    curve(lambda n: n * math.log2(n) if n > 1 else 1, 's', 'O(n log n)', 84)
    curve(lambda n: n * n, 'sa', 'O(n²)', 66)
    curve(lambda n: 2 ** n, 'sa dash', 'O(2ⁿ)', 26)
    f.text(330, 370, 'n=100 のとき O(n²) は10マイクロ秒、O(2ⁿ) は宇宙の年齢の1000倍',
           cls='t-s b')
    return f


# ---------------------------------------------------------------- 第3回
GATES = [('NOT', [(0, 1), (1, 0)]), ('AND', [(0, 0), (0, 0), (0, 0), (1, 1)]),
         ('OR', None), ('XOR', None), ('NAND', None), ('NOR', None)]


def _gate(f, x, y, kind, w=54, h=40):
    """MIL記号ふう。AND系は右が丸く、OR系は先が尖る。"""
    if kind in ('AND', 'NAND'):
        f.path(f'M{x},{y} L{x + w * 0.5},{y} A{h / 2},{h / 2} 0 0 1 {x + w * 0.5},{y + h} '
               f'L{x},{y + h} Z', cls='bg s')
    elif kind == 'NOT':
        f.poly([(x, y), (x + w - 8, y + h / 2), (x, y + h)], cls='bg s')
    else:
        f.path(f'M{x},{y} Q{x + w * 0.45},{y + h / 2} {x},{y + h} '
               f'Q{x + w * 0.55},{y + h} {x + w},{y + h / 2} '
               f'Q{x + w * 0.55},{y} {x},{y} Z', cls='bg s')
        if kind == 'XOR':
            f.path(f'M{x - 8},{y} Q{x + w * 0.37},{y + h / 2} {x - 8},{y + h}', cls='s')
    if kind in ('NOT', 'NAND', 'NOR'):
        cx = x + (w - 4 if kind != 'NOT' else w - 4)
        f.circle(cx, y + h / 2, 5, cls='bg s')


def f0301():
    """基本論理ゲートの記号"""
    f = Fig(740, 310)
    truth = {'NOT': ['A → 出力', '0 → 1', '1 → 0'],
             'AND': ['両方1のとき1', '00→0 ／ 01→0', '10→0 ／ 11→1'],
             'OR': ['どちらか1なら1', '00→0 ／ 01→1', '10→1 ／ 11→1'],
             'XOR': ['異なるとき1', '00→0 ／ 01→1', '10→1 ／ 11→0'],
             'NAND': ['AND の否定', '00→1 ／ 01→1', '10→1 ／ 11→0'],
             'NOR': ['OR の否定', '00→1 ／ 01→0', '10→0 ／ 11→0']}
    for i, k in enumerate(['NOT', 'AND', 'OR', 'XOR', 'NAND', 'NOR']):
        col, row = i % 3, i // 3
        x, y = 44 + col * 234, 44 + row * 140
        f.text(x + 30, y - 12, k, cls='b')
        _gate(f, x + 6, y, k)
        if k != 'NOT':
            f.line(x - 16, y + 10, x + 6, y + 10, cls='s')
            f.line(x - 16, y + 30, x + 6, y + 30, cls='s')
        else:
            f.line(x - 16, y + 20, x + 6, y + 20, cls='s')
        f.line(x + 66, y + 20, x + 88, y + 20, cls='s')
        f.lines(x + 100, y + 4, truth[k], cls='t-xs', anchor='start', lh=15)
    f.text(370, 300, '出力側の小円が「否定」を表す。AND に付けると NAND になる', cls='t-s lbl')
    return f


def f0302():
    """NAND による NOT・AND・OR の構成"""
    f = Fig(660, 330)
    rows = [('NOT', 'NAND(A, A)'), ('AND', 'NOT(NAND(A, B))'), ('OR', 'NAND(¬A, ¬B)')]
    for i, (name, expr) in enumerate(rows):
        y = 40 + i * 96
        f.text(46, y + 22, name, cls='b', anchor='start')
        f.text(46, y + 44, expr, cls='t-xs m lbl', anchor='start')
        if name == 'NOT':
            _gate(f, 180, y, 'NAND')
            f.path(f'M150,{y + 10} L180,{y + 10}', cls='s')
            f.path(f'M150,{y + 30} L180,{y + 30}', cls='s')
            f.path(f'M150,{y + 10} L150,{y + 30}', cls='s')
            f.text(140, y + 20, 'A', cls='t-s', anchor='end')
            f.line(250, y + 20, 300, y + 20, cls='s')
            f.text(310, y + 20, '¬A', cls='t-s', anchor='start')
        elif name == 'AND':
            _gate(f, 180, y, 'NAND')
            _gate(f, 300, y, 'NAND')
            f.text(160, y + 10, 'A', cls='t-s', anchor='end')
            f.text(160, y + 30, 'B', cls='t-s', anchor='end')
            f.line(166, y + 10, 180, y + 10, cls='s')
            f.line(166, y + 30, 180, y + 30, cls='s')
            f.path(f'M250,{y + 20} L276,{y + 20} L276,{y + 10} L300,{y + 10}', cls='s')
            f.path(f'M276,{y + 20} L276,{y + 30} L300,{y + 30}', cls='s')
            f.line(370, y + 20, 410, y + 20, cls='s')
            f.text(420, y + 20, 'A·B', cls='t-s', anchor='start')
        else:
            _gate(f, 180, y - 12, 'NAND', w=44, h=28)
            _gate(f, 180, y + 26, 'NAND', w=44, h=28)
            _gate(f, 300, y, 'NAND')
            f.text(160, y + 2, 'A', cls='t-s', anchor='end')
            f.text(160, y + 40, 'B', cls='t-s', anchor='end')
            for yy in (y - 6, y + 2, y + 32, y + 40):
                f.line(166, yy, 180, yy, cls='s')
            f.line(236, y + 2, 300, y + 10, cls='s')
            f.line(236, y + 40, 300, y + 30, cls='s')
            f.line(370, y + 20, 410, y + 20, cls='s')
            f.text(420, y + 20, 'A+B', cls='t-s', anchor='start')
        f.text(560, y + 20, 'NAND だけで作れる', cls='t-xs lbl')
    f.text(330, 316, 'すべての論理関数が NAND 1種類で構成できる（NAND完全性）', cls='t-s b')
    return f


def f0303():
    """全加算器と4ビット加算器"""
    f = Fig(700, 400)
    # 上段：全加算器の内部
    f.text(190, 28, '全加算器の内部', cls='b')
    f.box(120, 46, 90, 46, ['半加算器'], cls='tint s', tcls='t-s')
    f.box(250, 46, 90, 46, ['半加算器'], cls='tint s', tcls='t-s')
    _gate(f, 380, 52, 'OR', w=44, h=34)
    f.text(104, 58, 'A', cls='t-s', anchor='end')
    f.text(104, 80, 'B', cls='t-s', anchor='end')
    f.line(110, 58, 120, 58, cls='s')
    f.line(110, 80, 120, 80, cls='s')
    f.text(234, 104, 'Cin', cls='t-s', anchor='end')
    f.path('M240,104 L250,104 L250,80', cls='s')
    f.line(210, 58, 250, 58, cls='s')
    f.line(340, 58, 470, 58, cls='s')
    f.text(480, 58, 'S', cls='t-s b', anchor='start')
    f.path('M340,80 L360,80 L360,62 L380,62', cls='s')
    f.path('M210,80 L226,80 L226,140 L360,140 L360,78 L380,78', cls='s')
    f.path('M430,70 L452,70 L452,96 L470,96', cls='s')
    f.text(480, 96, 'Cout', cls='t-s b', anchor='start')

    # 下段：4ビット
    f.text(350, 200, '全加算器を4個つないだ4ビット加算器', cls='b')
    for i in range(4):
        x = 500 - i * 130
        f.box(x, 224, 96, 66, ['全加算器', f'第{i}桁'], cls='bg s', tcls='t-s', lh=15)
        f.text(x + 22, 212, f'A{i}', cls='t-xs lbl')
        f.text(x + 72, 212, f'B{i}', cls='t-xs lbl')
        f.line(x + 22, 216, x + 22, 224, cls='s')
        f.line(x + 72, 216, x + 72, 224, cls='s')
        f.line(x + 48, 290, x + 48, 316, cls='s')
        f.text(x + 48, 328, f'S{i}', cls='t-s b')
        if i < 3:
            f.arrow(x, 258, x - 34, 258, cls='sa')
    f.text(596, 258, 'Cin=0', cls='t-xs lbl', anchor='start')
    f.line(560, 258, 596, 258, cls='s')
    f.arrow(110, 258, 76, 258, cls='sa')
    f.text(70, 258, 'Cout', cls='t-xs lbl', anchor='end')
    f.text(350, 366, '桁上がりが右から左へ順に伝わる（この伝播が遅延になる）', cls='t-s')
    return f


def f0304():
    """SRラッチ"""
    f = Fig(600, 300)
    _gate(f, 250, 60, 'NOR', w=64, h=48)
    _gate(f, 250, 170, 'NOR', w=64, h=48)
    f.text(240, 200, 'NOR', cls='t-xs lbl', anchor='end')
    f.text(160, 74, 'S（セット）', cls='t-s', anchor='end')
    f.text(160, 214, 'R（リセット）', cls='t-s', anchor='end')
    f.line(166, 74, 250, 74, cls='s')
    f.line(166, 214, 250, 214, cls='s')
    # たすきがけ
    f.line(320, 84, 400, 84, cls='s')
    f.text(412, 84, 'Q', cls='b', anchor='start')
    f.line(320, 194, 400, 194, cls='s')
    f.text(412, 194, '¬Q', cls='b', anchor='start')
    f.path('M360,84 L360,140 L230,140 L230,204 L250,204', cls='sa')
    f.path('M360,194 L360,152 L218,152 L218,94 L250,94', cls='sa')
    f.circle(360, 84, 3.5, cls='ink')
    f.circle(360, 194, 3.5, cls='ink')

    f.rect(430, 40, 150, 120, cls='none sm', rx=6)
    f.text(505, 58, 'S  R   Q', cls='t-s b m')
    for i, r in enumerate(['1  0   1  にする', '0  1   0  にする',
                           '0  0   直前のまま', '1  1   禁止']):
        f.text(448, 80 + i * 20, r, cls='t-xs m', anchor='start')
    f.text(300, 268, 'S=R=0 で直前の値を保つ ＝ 1ビットを記憶している', cls='t-s b')
    return f


def f0305():
    """[旧 slide 40] ノイマン型計算機の構成"""
    f = Fig(700, 420)
    # CPU
    f.rect(230, 36, 250, 172, cls='tint s', rx=10)
    f.text(355, 52, '中央処理装置（CPU）', cls='b')
    f.box(268, 74, 174, 40, ['制御装置'], cls='bg s', tcls='t-s')
    f.box(268, 148, 174, 40, ['演算装置（ALU）'], cls='bg s', tcls='t-s')
    f.box(268, 114, 174, 30, ['レジスタ  PC / IR / 汎用'], cls='none sm dash', tcls='t-xs')
    # 主記憶
    f.box(250, 258, 210, 56, ['主記憶装置'], cls='bg s')
    f.text(60, 330, '命令とデータを区別せず、同じ番地空間に置く', cls='t-xs lbl', anchor='start')
    # 二次記憶
    f.box(210, 358, 290, 46, ['二次記憶装置'], cls='bg s')
    # 入出力
    f.box(24, 258, 150, 56, ['入力装置'], cls='bg s')
    f.box(536, 258, 150, 56, ['出力装置'], cls='bg s')
    # バス
    f.arrow(324, 208, 324, 254, cls='sa', label='データ', lcls='t-xs lbl', dy=4)
    f.arrow(400, 254, 400, 208, cls='sa', label='命令', lcls='t-xs lbl', dy=4)
    f.arrow(174, 286, 246, 286, cls='sa')
    f.arrow(536, 286, 464, 286, cls='sa')
    f.arrow(324, 318, 324, 354, cls='sa')
    f.arrow(400, 354, 400, 318, cls='sa')
    f.text(210, 274, 'データ', cls='t-xs lbl')
    f.text(500, 274, 'データ', cls='t-xs lbl')
    f.text(362, 340, 'データ', cls='t-xs lbl')
    return f


def f0306():
    """命令実行サイクル"""
    f = Fig(660, 360)
    cx, cy, r = 200, 180, 108
    steps = [('フェッチ', 'PC の指す番地から\n命令を読む', -90),
             ('デコード', '命令を解読する', 30),
             ('実行', '演算・読み書き\nPC を更新', 150)]
    import math
    for name, desc, ang in steps:
        a = math.radians(ang)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        f.circle(x, y, 46, cls='tint s')
        f.text(x, y, name, cls='t-s b')
    for a0, a1 in [(-90, 30), (30, 150), (150, 270)]:
        s, e = math.radians(a0 + 26), math.radians(a1 - 26)
        f.path(f'M{cx + r * math.cos(s):.1f},{cy + r * math.sin(s):.1f} '
               f'A{r},{r} 0 0 1 {cx + r * math.cos(e):.1f},{cy + r * math.sin(e):.1f}',
               cls='sa', arrow='aa')
    f.text(cx, cy, 'くり返す', cls='t-s lbl')

    f.rect(390, 56, 250, 250, cls='none sm', rx=6)
    f.text(515, 76, 'そのとき動く部品', cls='t-s b')
    items = [('フェッチ', 'PC → 主記憶 → 命令レジスタ'),
             ('デコード', '制御装置が命令を解読'),
             ('実行', 'ALU・レジスタ・主記憶')]
    for i, (a, b) in enumerate(items):
        f.text(408, 106 + i * 58, a, cls='t-s b', anchor='start')
        f.text(408, 126 + i * 58, b, cls='t-xs lbl', anchor='start')
    f.text(330, 336, 'CPU がしているのは「読む・計算する・書く・PC を進める」だけ', cls='t-s b')
    return f


def f0307():
    """集積度とクロックの推移"""
    import math
    f = Fig(680, 400)
    L, R, T, B = 80, 600, 50, 320
    f.line(L, B, R, B, cls='s', arrow='a')
    f.line(L, B, L, T, cls='s', arrow='a')
    for i, yr in enumerate(range(1970, 2031, 10)):
        x = L + (yr - 1970) / 60.0 * (R - L)
        f.line(x, B, x, B + 5, cls='sm')
        f.text(x, B + 18, str(yr), cls='t-xs lbl')
    f.text(L - 56, T - 6, '対数目盛', cls='t-xs lbl', anchor='start')

    def plot(fn, cls, name, at, dy=-12):
        pts = []
        for i in range(0, 61):
            yr = 1970 + i
            v = fn(yr)
            if v is None:
                continue
            pts.append((L + i / 60.0 * (R - L), B - v * (B - T)))
        f.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts), cls=cls)
        px, py = pts[min(at, len(pts) - 1)]
        f.text(px, py + dy, name, cls='t-xs b')

    # トランジスタ数：2年で倍 → log は直線。近年やや鈍る
    def tr(yr):
        n = (yr - 1970) / 2.0
        if yr > 2015:
            n = (2015 - 1970) / 2.0 + (yr - 2015) / 3.2
        return min(n / 30.0, 1.0) * 0.94

    # クロック：2005年ごろ頭打ち
    def clk(yr):
        if yr <= 2005:
            return (yr - 1970) / 35.0 * 0.62
        return 0.62 + (yr - 2005) * 0.0015

    def cores(yr):
        if yr < 2004:
            return 0.06
        return 0.06 + math.log2(1 + (yr - 2004) * 0.9) / 8.0 * 0.62

    plot(tr, 's2', 'トランジスタ数', 44, -14)
    plot(clk, 'sa', 'クロック周波数', 52, 16)
    plot(cores, 's dash', 'コア数', 52, -14)
    f.line(L + (2005 - 1970) / 60.0 * (R - L), T, L + (2005 - 1970) / 60.0 * (R - L), B,
           cls='sm dash')
    f.text(L + (2005 - 1970) / 60.0 * (R - L), T - 14, '2005年ごろ', cls='t-xs lbl')
    f.text(340, 366, 'クロックは電力の壁で頭打ちになり、代わりにコア数が増えた', cls='t-s b')
    f.text(340, 386, '（公開されている仕様値をもとに描いた模式図）', cls='t-xs lbl')
    return f


# ---------------------------------------------------------------- 第4回
def f0401():
    """アセンブリ言語と機械語の対応"""
    f = Fig(700, 320)
    f.text(160, 34, 'アセンブリ言語', cls='b')
    f.text(400, 34, '番地', cls='t-s b')
    f.text(560, 34, '機械語（主記憶の中身）', cls='b')
    rows = [('loop:', '', ''),
            ('  mov  rax, 5', '0100', '48 C7 C0 05 00 00 00'),
            ('  add  rax, rbx', '0107', '48 01 D8'),
            ('  jne  loop', '010A', '75 F4'),
            ('  ret', '010C', 'C3')]
    for i, (asm, addr, code) in enumerate(rows):
        y = 60 + i * 40
        f.rect(40, y, 250, 32, cls='accT s' if i == 0 else 'tint s')
        f.text(52, y + 16, asm, cls='t-s m', anchor='start')
        if addr:
            f.text(400, y + 16, addr, cls='t-xs m lbl')       # 矢印と重ならない中央の列
            f.rect(440, y, 240, 32, cls='bg s')
            f.text(452, y + 16, code, cls='t-xs m', anchor='start')
            f.arrow(292, y + 16, 372, y + 16, cls='sm', marker='am')
    # ラベルが番地に化けることを示す
    f.text(120, 292, 'ラベル', cls='t-xs acc b', anchor='start')
    f.path('M116,284 L84,96', cls='sa dot', arrow='aa')
    f.path('M180,292 C300,292 380,240 398,196', cls='sa dot', arrow='aa')
    f.text(300, 306, 'アセンブラが番地に直す', cls='t-xs acc b', anchor='start')
    f.text(690, 292, '命令を挿入しても、人間が番地を', cls='t-s', anchor='end')
    f.text(690, 310, '付け替えなくてよい', cls='t-s', anchor='end')
    return f


def f0402():
    """処理系の3方式"""
    f = Fig(700, 350)
    f.line(330, 40, 330, 320, cls='sm dash')
    f.text(240, 34, '← 実行前（開発時）', cls='t-xs lbl', anchor='end')
    f.text(420, 34, '実行時 →', cls='t-xs lbl', anchor='start')
    rows = [
        ('コンパイラ方式', [('ソース', 60, 110), ('コンパイラ', 150, 110),
                            ('機械語', 260, 110), ('実行', 400, 110)], 3),
        ('インタプリタ方式', [('ソース', 60, 190), ('インタプリタが読みながら実行', 360, 190)], 1),
        ('仮想機械方式', [('ソース', 60, 270), ('コンパイラ', 150, 270),
                          ('中間表現', 260, 270), ('VM が実行', 400, 270)], 3),
    ]
    for name, boxes, split in rows:
        y = boxes[0][2]
        f.text(40, y - 34, name, cls='b', anchor='start')
        prev = None
        for i, (label, x, yy) in enumerate(boxes):
            w = 190 if len(label) > 12 else 84
            cls = 'accT s' if i >= split else 'tint s'
            f.box(x, yy - 18, w, 36, [label], cls=cls, tcls='t-s')
            if prev:
                f.arrow(prev, yy, x - 6, yy, cls='sm', marker='am')
            prev = x + w + 6
    f.text(350, 328, 'どこまでを実行前に済ませるかが違う。JIT は実行中に熱い箇所だけ翻訳する',
           cls='t-s b')
    return f


def f0403():
    """ビルドの各段階"""
    f = Fig(700, 320)
    stages = [('前処理', '#include を展開'), ('コンパイル', '.s を出力'),
              ('アセンブル', '.o を出力'), ('リンク', '実行ファイル'), ('ロード', 'メモリ上へ')]
    y = 130
    for i, (name, desc) in enumerate(stages):
        x = 46 + i * 132
        f.box(x, y, 104, 52, [name], cls='tint s', tcls='t-s')
        f.text(x + 52, y + 66, desc, cls='t-xs lbl')
        if i:
            f.arrow(x - 26, y + 26, x - 4, y + 26, cls='s')
    # 2つのソースが合流
    f.box(46, 40, 104, 32, ['main.c'], cls='bg s', tcls='t-xs m')
    f.box(46, 82, 104, 32, ['util.c'], cls='bg s', tcls='t-xs m')
    f.arrow(98, 74, 98, 126, cls='sm', marker='am')
    f.box(430, 40, 130, 32, ['ライブラリ'], cls='bg s', tcls='t-xs')
    f.path('M495,72 L495,100 L494,126', cls='sm', arrow='am')
    f.text(494, 112, '', cls='t-xs')
    f.text(350, 246, 'リンクの段階で、複数の .o とライブラリが1つに合流する', cls='t-s b')
    f.text(350, 274, '未解決だった関数の番地が、ここで初めて埋まる', cls='t-s lbl')
    return f


def f0404():
    """プロセスのメモリ配置"""
    f = Fig(620, 400)
    x, w = 180, 200
    segs = [('スタック', 40, 62, 'tint2 s', '局所変数・戻り番地・引数'),
            ('（空き）', 102, 96, 'none sm dash', ''),
            ('ヒープ', 198, 62, 'tint2 s', 'malloc などで確保'),
            ('BSS', 260, 34, 'tint s', '初期値のない大域変数'),
            ('データ', 294, 34, 'tint s', '初期値のある大域変数'),
            ('テキスト', 328, 40, 'accT s', '機械語の命令列（書込み禁止）')]
    for name, y, h, cls, desc in segs:
        f.rect(x, y, w, h, cls=cls)
        f.text(x + w / 2, y + h / 2, name, cls='t-s b' if name != '（空き）' else 't-s lbl')
        if desc:
            f.text(x + w + 18, y + h / 2, desc, cls='t-xs lbl', anchor='start')
    f.arrow(x + w / 2, 190, x + w / 2, 152, cls='sa')
    f.arrow(x + w / 2, 110, x + w / 2, 148, cls='sa')
    f.text(x - 16, 66, '高位番地', cls='t-xs lbl', anchor='end')
    f.text(x - 16, 344, '低位番地', cls='t-xs lbl', anchor='end')
    f.line(x - 10, 40, x - 10, 368, cls='sm', arrow='am')
    f.text(310, 386, 'ヒープとスタックは互いに向かって伸びる', cls='t-s b')
    return f


FIGURES = {
    '01-01': f0101, '01-02': f0102, '01-03': f0103, '01-04': f0104,
    '02-01': f0201, '02-02': f0202, '02-03': f0203,
    '03-01': f0301, '03-02': f0302, '03-03': f0303, '03-04': f0304,
    '03-05': f0305, '03-06': f0306, '03-07': f0307,
    '04-01': f0401, '04-02': f0402, '04-03': f0403, '04-04': f0404,
}
