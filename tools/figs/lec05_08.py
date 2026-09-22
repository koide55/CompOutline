"""第5〜8回の図。

[旧] と注記したものは CompOutline2024.pptx の該当スライドから
図形の座標を取り出して引き継いだもの。
"""
import math

from svgkit import Fig


# ---------------------------------------------------------------- 第5回
def f0501():
    """SRAM セルと DRAM セル"""
    f = Fig(660, 330)

    def tr(x, y, s=1.0, label=None):
        """トランジスタの記号（簡略）"""
        f.line(x, y - 14 * s, x, y + 14 * s, cls='s')
        f.line(x - 10 * s, y, x, y, cls='s')
        f.line(x + 4 * s, y - 12 * s, x + 4 * s, y + 12 * s, cls='s')
        f.line(x + 4 * s, y - 8 * s, x + 18 * s, y - 16 * s, cls='s')
        f.line(x + 4 * s, y + 8 * s, x + 18 * s, y + 16 * s, cls='s')
        if label:
            f.text(x + 4, y + 26 * s, label, cls='t-xs lbl')

    # SRAM
    f.rect(40, 60, 260, 200, cls='none s', rx=6)
    f.text(170, 40, 'SRAM セル', cls='b')
    f.text(170, 282, 'トランジスタ 6個', cls='t-s')
    f.text(170, 302, '安定して保持する。速いが面積を食う', cls='t-xs lbl')
    f.box(92, 112, 72, 40, ['インバータ'], cls='tint s', tcls='t-xs')
    f.box(176, 176, 72, 40, ['インバータ'], cls='tint s', tcls='t-xs')
    f.path('M164,132 L266,132 L266,196 L248,196', cls='s', arrow='a')
    f.path('M176,196 L74,196 L74,132 L92,132', cls='s', arrow='a')
    tr(78, 88, 0.6)
    tr(240, 88, 0.6)
    f.text(159, 74, 'アクセス用トランジスタ ×2', cls='t-xs lbl')

    # DRAM
    f.rect(360, 60, 260, 200, cls='none s', rx=6)
    f.text(490, 40, 'DRAM セル', cls='b')
    f.text(490, 282, 'トランジスタ 1個 ＋ コンデンサ 1個', cls='t-s')
    f.text(490, 302, '面積は 1/6 以下。ただし電荷が漏れる', cls='t-xs lbl')
    tr(452, 150, 1.0, 'トランジスタ')
    f.line(490, 142, 490, 158, cls='s2')
    f.line(490, 166, 490, 182, cls='s2')
    f.line(470, 150, 490, 150, cls='s')
    f.text(524, 162, 'コンデンサ', cls='t-xs lbl', anchor='start')
    f.line(490, 182, 490, 206, cls='s')
    f.line(474, 206, 506, 206, cls='s')
    f.text(400, 110, 'ワード線', cls='t-xs lbl', anchor='start')
    f.line(400, 120, 452, 120, cls='sm')
    f.line(452, 120, 452, 136, cls='sm')

    f.text(330, 322, '電荷は漏れるので、定期的に読み直して書き戻す（リフレッシュ）',
           cls='t-s b')
    return f


def f0502():
    """記憶階層のピラミッド"""
    f = Fig(700, 400)
    rows = [('レジスタ', '数百 B', '0.3 ns', 'コンパイラ'),
            ('L1 キャッシュ', '数十 KB', '1 ns', 'ハードウェア'),
            ('L2 / L3 キャッシュ', '数 MB〜数十 MB', '4〜15 ns', 'ハードウェア'),
            ('主記憶 (DRAM)', '数 GB〜数百 GB', '80 ns', 'OS'),
            ('SSD', '数百 GB〜数十 TB', '20 µs', 'OS'),
            ('ネットワーク上', '事実上無限', '数十 ms〜', 'アプリケーション')]
    top_w, bot_w, h = 150, 470, 48
    cx = 300
    for i, (name, cap, spd, mgr) in enumerate(rows):
        w = top_w + (bot_w - top_w) * i / (len(rows) - 1)
        w2 = top_w + (bot_w - top_w) * (i + 1) / (len(rows) - 1)
        y = 40 + i * h
        f.poly([(cx - w / 2, y), (cx + w / 2, y), (cx + w2 / 2, y + h), (cx - w2 / 2, y + h)],
               cls=('accT s' if i < 3 else 'tint s'))
        f.text(cx, y + h / 2 - 8, name, cls='t-s b')
        f.text(cx, y + h / 2 + 9, f'{cap}   /   {spd}', cls='t-xs lbl')
        f.text(cx + bot_w / 2 + 26, y + h / 2, mgr, cls='t-xs lbl', anchor='start')
    f.text(cx + bot_w / 2 + 26, 26, '管理する主体', cls='t-xs b', anchor='start')
    f.line(70, 44, 70, 40 + 6 * h - 4, cls='sm', arrow='am')
    f.text(64, 60, '速い・高い・小さい', cls='t-xs lbl', anchor='end')
    f.text(64, 300, '遅い・安い・大きい', cls='t-xs lbl', anchor='end')
    f.text(350, 368, '段をまたぐごとに、速度も容量も桁が変わる', cls='t-s b')
    f.text(350, 388, '（2026年時点の代表的な桁。世代で変わるが、桁の差は変わらない）',
           cls='t-xs lbl')
    return f


def f0503():
    """走査順とキャッシュライン"""
    f = Fig(700, 420)
    n, c = 8, 26
    for k, (bx, title, rowwise) in enumerate([(50, '(a) 行を内側で回す', True),
                                              (390, '(b) 列を内側で回す', False)]):
        f.text(bx + n * c / 2, 34, title, cls='b')
        for i in range(n):
            for j in range(n):
                f.rect(bx + j * c, 54 + i * c, c, c, cls='bg s')
        # 走査の矢印
        if rowwise:
            for i in range(3):
                y = 54 + i * c + c / 2
                f.arrow(bx + 4, y, bx + n * c - 4, y, cls='sa')
        else:
            for j in range(3):
                x = bx + j * c + c / 2
                f.arrow(x, 58, x, 54 + n * c - 4, cls='sa')
        # メモリ上の並び（行優先）
        f.text(bx + n * c / 2, 54 + n * c + 26, 'メモリ上の並び（行優先）', cls='t-xs lbl')
        my = 54 + n * c + 40
        for i in range(16):
            f.rect(bx + i * 13, my, 13, 20, cls='bg s')
        for g in range(2):
            f.rect(bx + g * 8 * 13, my, 8 * 13, 20, cls='none s2')
        f.text(bx + n * c / 2, my + 32, '太枠が1キャッシュライン（64バイト＝8要素）',
               cls='t-xs lbl')
        if rowwise:
            for i in range(8):
                f.rect(bx + i * 13 + 2, my + 2, 9, 16, cls='accT')
            f.text(bx + n * c / 2, my + 58, '1回のミスで8要素使える', cls='t-s b acc')
        else:
            for i in (0, 8):
                f.rect(bx + i * 13 + 2, my + 2, 9, 16, cls='accT')
            f.text(bx + n * c / 2, my + 58, 'ほぼ毎回ミスする', cls='t-s b acc')
    f.text(350, 404, '計算量はどちらも O(N²)。それでも実測は数倍から10倍以上ちがう',
           cls='t-s b')
    return f


def f0504():
    """仮想アドレスから物理アドレスへの変換"""
    f = Fig(700, 410)
    # 2つのプロセスの仮想空間
    for k, (bx, name) in enumerate([(40, 'プロセス A'), (190, 'プロセス B')]):
        f.text(bx + 50, 34, name, cls='t-s b')
        for i in range(6):
            f.rect(bx, 50 + i * 34, 100, 34, cls='tint s')
            f.text(bx + 50, 67 + i * 34, f'ページ {i}', cls='t-xs')
        f.text(bx + 50, 272, '仮想アドレス空間', cls='t-xs lbl')

    # ページテーブル。矢印が貫通しないよう、経路の下に置く
    f.box(300, 300, 170, 40, ['ページテーブル'], cls='accT s', tcls='t-s')
    f.text(385, 358, 'OS が管理し、MMU がこれを引く', cls='t-xs lbl')

    # 物理メモリ
    f.text(560, 34, '物理メモリ', cls='t-s b')
    f.text(560, 274, '物理的には飛び飛びでよい', cls='t-xs lbl')
    frames = ['B0', '', 'A0', 'A2', '', 'B1', 'A1', '']
    for i, lab in enumerate(frames):
        f.rect(510, 50 + i * 30, 100, 30, cls='bg s' if not lab else 'tint2 s')
        if lab:
            f.text(560, 65 + i * 30, lab, cls='t-xs')


    # 対応の矢印
    # 箱の右端から出す（文字の上を通さない）
    pairs = [(140, 67, 2), (140, 101, 6), (140, 135, 3), (290, 67, 0), (290, 101, 5)]
    for x, y, fr in pairs:
        f.path(f'M{x + 4},{y} C{340},{y} {440},{65 + fr * 30} {506},{65 + fr * 30}',
               cls='sm', arrow='am')

    # スワップ
    f.box(510, 296, 100, 36, ['スワップ領域'], cls='none s dash', tcls='t-xs')
    f.path('M290,203 C420,203 470,314 506,314', cls='sa dash', arrow='aa')
    f.text(560, 344, '主記憶にないページは SSD へ', cls='t-xs acc')
    f.text(350, 392, '対応表を1枚挟むだけで、保護・連続性・容量の拡張がまとめて得られる',
           cls='t-s b')
    return f


def f0505():
    """パイプラインの動作"""
    f = Fig(800, 350)
    stages = ['F', 'D', 'E', 'M', 'W']
    x0, y0, cw, ch = 130, 70, 74, 34
    for t in range(9):
        f.text(x0 + t * cw + cw / 2, y0 - 16, f'{t + 1}', cls='t-xs lbl')
    f.text(x0 + 4.5 * cw, y0 - 38, 'クロックサイクル', cls='t-s lbl')
    for i in range(5):
        f.text(x0 - 14, y0 + i * ch + ch / 2, f'命令 I{i + 1}', cls='t-s', anchor='end')
        for j, s in enumerate(stages):
            x = x0 + (i + j) * cw
            f.rect(x, y0 + i * ch, cw, ch, cls='accT s' if s == 'E' else 'tint s')
            f.text(x + cw / 2, y0 + i * ch + ch / 2, s, cls='t-s b')
    f.line(x0 + 4 * cw, y0 - 6, x0 + 4 * cw, y0 + 5 * ch + 10, cls='sm dash')
    f.text(x0 + 4 * cw, y0 + 5 * ch + 26, 'ここから毎サイクル1命令が完了する', cls='t-s b')
    f.text(x0 + 4 * cw, y0 + 5 * ch + 48,
           'F フェッチ　D デコード　E 実行　M メモリ　W 書き戻し', cls='t-xs lbl')
    f.text(430, 318, '1命令の所要時間は変わらないが、単位時間あたりの完了数が5倍になる',
           cls='t-s b')
    return f


def f0506():
    """投機実行のサイドチャネル：時間差が秘密を漏らす"""
    # 塗りは svgkit の .s（fill:none）に負けるので、線の色で区別する
    f = Fig(700, 450)

    # ① キャッシュに当たるか外れるかで、アクセス時間が桁で違う
    f.text(24, 24, '① キャッシュに当たるか外れるかで、アクセス時間が桁で違う',
           cls='t-s b', anchor='start')
    bx, sc = 196, 356 / 80.0
    for lbl, ns, cls, y in [('当たる（ヒット）', 1, 'sa', 44),
                            ('外れる（ミス）', 80, 's', 74)]:
        f.text(bx - 10, y + 10, lbl, cls='t-s', anchor='end')
        w = max(6, ns * sc)
        f.rect(bx, y, w, 20, cls=cls)
        f.text(bx + w + 8, y + 10, f'約 {ns} ns', cls='t-xs b', anchor='start')
    f.text(bx, 124, 'この差は測れる。だから「キャッシュにあったか」が分かる',
           cls='t-s b acc', anchor='start')

    # ② 投機実行のあと array2 を順に読んで時間を測る
    f.text(24, 162, '② 投機実行のあと、array2 を順に読んで時間を測る',
           cls='t-s b', anchor='start')
    L, T, B, n, secret = 96, 224, 352, 16, 6
    cw = 552.0 / n
    f.line(L, T - 8, L, B, cls='s')
    f.line(L, B, L + 552 + 8, B, cls='s')
    f.text(L - 8, T - 4, 'アクセス時間', cls='t-xs lbl', anchor='end')
    for k in range(n):
        x = L + k * cw + 4
        hit = (k == secret)
        f.rect(x, B - (18 if hit else 108), cw - 8, 18 if hit else 108,
               cls='sa' if hit else 's')
        f.text(x + (cw - 8) / 2, B + 15, str(k), cls='t-xs lbl')
    f.text(L + 276, B + 34, 'array2 の添字', cls='t-xs lbl')

    # 短い1本を指す
    sx = L + secret * cw + 4 + (cw - 8) / 2
    f.line(sx, T + 2, sx, B - 26, cls='sa dash', arrow='a')
    f.text(sx + 10, T - 6, '1つだけ速い ＝ この添字が秘密の値',
           cls='t-s b acc', anchor='start')

    f.text(350, 412, '取り消された実行でも、キャッシュに載せた痕跡は残る', cls='t-s b')
    f.text(350, 434, '計算の結果ではなく、副作用から情報を取る —— サイドチャネル攻撃',
           cls='t-xs lbl')
    return f


def f0507():
    """アムダールの法則"""
    f = Fig(680, 400)
    L, R, T, B = 90, 590, 40, 320
    f.line(L, B, R, B, cls='s', arrow='a')
    f.line(L, B, L, T, cls='s', arrow='a')
    f.text(L + 40, B + 46, 'コア数（対数目盛）', cls='t-s lbl', anchor='start')
    f.text(L - 50, T - 6, '高速化率', cls='t-s lbl', anchor='start')
    for k in range(11):
        x = L + k / 10.0 * (R - L)
        f.line(x, B, x, B + 5, cls='sm')
        f.text(x, B + 18, str(2 ** k), cls='t-xs lbl')
    for v in (1, 20, 40, 60, 80, 100):
        y = B - v / 100.0 * (B - T)
        f.line(L, y, R, y, cls='sm dot')
        f.text(L - 10, y, str(v), cls='t-xs lbl', anchor='end')

    def plot(p, cls, name):
        pts = []
        for k in range(0, 101):
            nc = 2 ** (k / 10.0)
            s = 1.0 / ((1 - p) + p / nc)
            pts.append((L + k / 100.0 * (R - L), B - min(s, 100) / 100.0 * (B - T)))
        f.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts), cls=cls)
        f.text(R + 6, pts[-1][1], name, cls='t-xs b', anchor='start')

    # 理想
    ideal = [(L + k / 100.0 * (R - L), B - min(2 ** (k / 10.0), 100) / 100.0 * (B - T))
             for k in range(101)]
    f.path('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in ideal), cls='sm dash')
    f.text(L + 250, T + 10, '理想（コア数に比例）', cls='t-xs lbl', anchor='start')
    for p, cls, name in [(0.99, 'sa', 'p=99%'), (0.95, 's', 'p=95%'),
                         (0.90, 's dash', 'p=90%'), (0.75, 'sm', 'p=75%'),
                         (0.50, 'sm dash', 'p=50%')]:
        plot(p, cls, name)
    f.text(340, 366, '逐次のまま残る部分が、高速化の上限を決める', cls='t-s b')
    f.text(340, 386, '10%が逐次なら、コアを1000個並べても10倍にしかならない', cls='t-xs lbl')
    return f


# ---------------------------------------------------------------- 第6回
def f0601():
    """磁気ディスク装置の構造"""
    f = Fig(700, 400)
    # 上面図
    f.text(160, 32, '上から見た図', cls='b')
    cx, cy = 160, 165
    f.circle(cx, cy, 100, cls='tint s')
    for r in (86, 70, 54, 38):
        f.circle(cx, cy, r, cls='none sm')
    f.circle(cx, cy, 16, cls='bg s')
    # セクタの扇形
    for a in range(0, 360, 30):
        rad = math.radians(a)
        f.line(cx + 16 * math.cos(rad), cy + 16 * math.sin(rad),
               cx + 100 * math.cos(rad), cy + 100 * math.sin(rad), cls='sm')
    # 1セクタを強調
    a0, a1 = math.radians(-30), math.radians(0)
    f.path(f'M{cx + 70 * math.cos(a0):.1f},{cy + 70 * math.sin(a0):.1f} '
           f'A70,70 0 0 1 {cx + 70 * math.cos(a1):.1f},{cy + 70 * math.sin(a1):.1f} '
           f'L{cx + 86 * math.cos(a1):.1f},{cy + 86 * math.sin(a1):.1f} '
           f'A86,86 0 0 0 {cx + 86 * math.cos(a0):.1f},{cy + 86 * math.sin(a0):.1f} Z',
           cls='accT sa')
    f.text(cx - 118, cy - 66, 'トラック', cls='t-xs lbl', anchor='end')
    f.line(cx - 114, cy - 62, cx - 62, cy - 62, cls='sm')
    f.text(cx - 118, cy - 26, 'セクタ', cls='t-xs acc b', anchor='end')
    f.line(cx - 114, cy - 22, cx - 74, cy - 22, cls='sa')
    f.line(cx - 74, cy - 22, cx + 74, cy - 48, cls='sa dot')
    # アーム
    f.path(f'M{cx + 150},{cy + 92} L{cx + 40},{cy + 26}', cls='s2')
    f.circle(cx + 150, cy + 92, 8, cls='tint2 s')

    # 側面図
    f.text(490, 32, '横から見た図', cls='b')
    bx, by = 380, 80
    for i in range(4):
        y = by + i * 42
        f.ellipse(bx + 110, y, 110, 12, cls='tint s')
        f.rect(bx, y, 220, 6, cls='tint2')
        f.ellipse(bx + 110, y, 110, 12, cls='none s')
        # ヘッド
        f.rect(bx + 40, y - 12, 14, 7, cls='ink')
        f.rect(bx + 40, y + 6, 14, 7, cls='ink')
    f.rect(bx + 104, by - 20, 12, 4 * 42 + 20, cls='tint2 s')
    f.text(bx + 110, by - 32, 'スピンドル', cls='t-xs lbl')
    # アクセスアーム（一体）
    f.rect(bx + 26, by - 16, 8, 4 * 42, cls='accT sa')
    f.text(bx + 14, by + 4 * 42 + 26, 'アクセスアーム', cls='t-xs acc b')
    f.text(bx + 14, by + 4 * 42 + 42, '（全ヘッド一体）', cls='t-xs lbl')
    # シリンダ
    f.rect(bx + 150, by - 22, 30, 4 * 42 + 24, cls='none s2 dash')
    f.text(bx + 165, by + 4 * 42 + 26, 'シリンダ', cls='t-xs b')
    f.line(bx + 110, by - 26, bx + 110, by - 12, cls='sm')

    f.text(350, 372, 'ヘッドが一体で動くので、同じシリンダ内なら腕を動かさずに読める',
           cls='t-s b')
    return f


def f0602():
    """SSD の論理・物理アドレス変換"""
    f = Fig(700, 380)
    f.text(350, 30, 'OS から見た論理ブロック番号', cls='b')
    for i in range(12):
        f.rect(80 + i * 45, 46, 45, 34, cls='tint s')
        f.text(80 + i * 45 + 22, 63, str(i), cls='t-xs')

    f.box(280, 128, 140, 44, ['対応表'], cls='accT s', tcls='t-s')
    f.text(350, 186, 'SSD のコントローラが持ち替え続ける', cls='t-xs lbl')

    f.text(350, 224, '物理的な NAND ブロック', cls='b')
    labels = ['3', '7', '', '0', '', '9', '1', '×', '5', '', '2', '×']
    for i, lab in enumerate(labels):
        cls = 'bg s' if not lab else ('tint2 s' if lab != '×' else 'none s dash')
        f.rect(80 + i * 45, 240, 45, 34, cls=cls)
        if lab and lab != '×':
            f.text(80 + i * 45 + 22, 257, lab, cls='t-xs')
        elif lab == '×':
            f.text(80 + i * 45 + 22, 257, '無効', cls='t-xs lbl')
    for a, b in [(1, 6), (3, 10), (7, 0), (9, 5), (5, 8)]:
        f.path(f'M{80 + a * 45 + 22},80 C{80 + a * 45 + 22},120 '
               f'{80 + b * 45 + 22},200 {80 + b * 45 + 22},236', cls='sm', arrow='am')

    f.text(350, 300, '上書きせず、常に新しい場所へ書いて対応表を張り替える', cls='t-s b')
    f.text(350, 322, '古いページは無効印を付け、あとでブロックごとまとめて消去する',
           cls='t-s lbl')
    f.text(350, 352, '摩耗を散らす（ウェアレベリング）／消去はブロック単位', cls='t-xs lbl')
    return f


def f0603():
    """[旧 slide 343-357] RAID 0/1/5/6 のデータ配置"""
    f = Fig(700, 460)

    def disk(x, y, w=64, h=44, cls='bg s'):
        """旧スライドと同じ「円柱」でディスクを表す"""
        f.rect(x, y, w, h, cls=cls)
        f.ellipse(x + w / 2, y + h, w / 2, 7, cls=cls)
        f.ellipse(x + w / 2, y, w / 2, 7, cls=cls)

    levels = [
        ('RAID 0', ['A1', 'A2', 'A3', 'A4'], '冗長性なし。1台でも壊れると全滅'),
        ('RAID 1', ['A1', 'A1', 'A2', 'A2'], '同じものを2台に。容量効率 50%'),
        ('RAID 5', ['A1', 'A2', 'A3', 'Ap'], 'パリティを分散。1台の故障に耐える'),
        ('RAID 6', ['A1', 'A2', 'Ap', 'Aq'], 'パリティ2種類。2台の故障に耐える'),
    ]
    for k, (name, blocks, note) in enumerate(levels):
        y = 54 + k * 100
        f.text(58, y + 22, name, cls='b', anchor='start')
        f.text(58, y + 44, note, cls='t-xs lbl', anchor='start')
        for i, b in enumerate(blocks):
            x = 250 + i * 92
            par = b.startswith('Ap') or b.startswith('Aq')
            disk(x, y, cls='accT s' if par else 'tint s')
            f.text(x + 32, y + 22, b, cls='t-s b')
            if k == 0:
                f.text(x + 32, y - 16, f'ディスク{i + 1}', cls='t-xs lbl')
        if k >= 2:
            f.text(624, y + 22, 'P', cls='t-xs acc b', anchor='start')
    f.text(350, 436, 'パリティは XOR。 A ⊕ P ⊕ C = B のように、残りから復元できる',
           cls='t-s b')
    return f


# ---------------------------------------------------------------- 第7回
def f0701():
    """特権モードとユーザモード"""
    f = Fig(680, 410)
    cx, cy = 300, 200
    f.circle(cx, cy, 176, cls='tint s')
    f.circle(cx, cy, 104, cls='accT s')
    f.text(cx, cy - 78, 'カーネル（特権モード）', cls='t-s b')
    for i, (dx, dy, lab) in enumerate([(-52, -30, 'CPU'), (52, -30, 'メモリ'),
                                       (-52, 24, 'ストレージ'), (52, 24, '装置')]):
        f.box(cx + dx - 40, cy + dy - 14, 80, 28, [lab], cls='bg s', tcls='t-xs')
    f.text(cx, cy + 66, 'ハードウェア資源', cls='t-xs lbl')
    f.text(cx, cy - 194, 'ユーザプロセス（非特権モード）', cls='t-s b')

    # 唯一の通り道
    f.rect(cx - 42, cy + 96, 84, 22, cls='bg s2')
    f.text(cx, cy + 107, 'システムコール', cls='t-xs b')
    f.arrow(cx, cy + 150, cx, cy + 122, cls='sa')
    f.text(cx + 96, cy + 107, '引数を検査してから実行', cls='t-xs lbl', anchor='start')

    # 跳ね返される矢印
    for ang in (200, 250, 300, 340):
        a = math.radians(ang)
        x1, y1 = cx + 168 * math.cos(a), cy + 168 * math.sin(a)
        x2, y2 = cx + 112 * math.cos(a), cy + 112 * math.sin(a)
        f.line(x1, y1, x2, y2, cls='sm', arrow='am')
        f.text(x2 - 6 * math.cos(a), y2 - 6 * math.sin(a), '×', cls='t-s b')
    f.text(310, 392, '入口が1つしかなく、そこで必ず検査される', cls='t-s b')
    return f


def f0702():
    """プロセスの状態遷移"""
    f = Fig(680, 330)
    pos = {'Ready': (150, 180), 'Running': (400, 100), 'Blocked': (400, 260)}
    for name, (x, y) in pos.items():
        ja = {'Ready': '実行可能', 'Running': '実行中', 'Blocked': '待機中'}[name]
        f.circle(x, y, 56, cls='tint s' if name != 'Running' else 'accT s')
        f.text(x, y - 8, ja, cls='b')
        f.text(x, y + 12, name, cls='t-xs lbl')
    f.arrow(198, 162, 348, 112, cls='s')
    f.text(250, 118, 'ディスパッチ', cls='t-xs lbl')
    f.text(250, 134, '（スケジューラが選ぶ）', cls='t-xs lbl')
    f.path('M356,128 C280,180 250,190 198,196', cls='s', arrow='a')
    f.text(286, 200, 'タイムスライス終了・横取り', cls='t-xs lbl')
    f.arrow(400, 156, 400, 202, cls='s')
    f.text(412, 180, '入出力を要求', cls='t-xs lbl', anchor='start')
    f.path('M348,244 C260,230 240,222 198,214', cls='s', arrow='a')
    f.text(268, 250, '入出力が完了', cls='t-xs lbl')
    f.rect(474, 218, 176, 84, cls='none sm dash', rx=6)
    f.text(562, 238, '待機が明けても', cls='t-s b')
    f.text(562, 258, '直接 Running には戻らない。', cls='t-xs')
    f.text(562, 276, 'いったん順番待ちの列に並ぶ', cls='t-xs')
    f.text(330, 320, 'コア数を超えたプロセスは Ready の列で待つ', cls='t-s b')
    return f


def f0703():
    """プロセスとスレッドのメモリ配置"""
    f = Fig(700, 380)
    f.text(180, 32, '3つのプロセス', cls='b')
    for k in range(3):
        x = 40 + k * 108
        f.rect(x, 52, 92, 250, cls='none s')
        for i, (lab, h, cls) in enumerate([('スタック', 44, 'tint2'), ('（空き）', 60, 'bg'),
                                           ('ヒープ', 46, 'tint2'), ('データ', 40, 'tint'),
                                           ('テキスト', 60, 'accT')]):
            y = 52 + sum(hh for _, hh, _ in
                         [('スタック', 44, ''), ('（空き）', 60, ''), ('ヒープ', 46, ''),
                          ('データ', 40, '')][:i])
            f.rect(x, y, 92, h, cls=cls + ' s')
            f.text(x + 46, y + h / 2, lab, cls='t-xs')
    f.text(180, 322, 'それぞれ独立したアドレス空間', cls='t-s')
    f.text(180, 344, '互いのメモリを見られない', cls='t-xs lbl')

    f.text(520, 32, '1プロセスの中の3スレッド', cls='b')
    x = 400
    f.rect(x, 52, 250, 250, cls='none s')
    for k in range(3):
        f.rect(x + 12 + k * 80, 52, 72, 44, cls='tint2 s')
        f.text(x + 48 + k * 80, 74, f'スタック{k + 1}', cls='t-xs')
    f.rect(x, 96, 250, 60, cls='bg s')
    f.text(x + 125, 126, '（空き）', cls='t-xs lbl')
    for i, (lab, h, cls) in enumerate([('ヒープ', 46, 'tint2'), ('データ', 40, 'tint'),
                                       ('テキスト', 60, 'accT')]):
        y = 156 + sum(hh for _, hh in [('ヒープ', 46), ('データ', 40)][:i])
        f.rect(x, y, 250, h, cls=cls + ' s')
        f.text(x + 125, y + h / 2, lab + '（共有）', cls='t-xs')
    for k in range(3):
        f.arrow(x + 48 + k * 80, 96, x + 48 + k * 80, 172, cls='sa')
    f.text(520, 322, 'スタックだけが別。ヒープ・データ・テキストは共有', cls='t-s')
    f.text(520, 344, '共有できるのは利点であり、最大の危険でもある', cls='t-xs acc b')
    return f


def f0704():
    """競合状態の時系列"""
    f = Fig(800, 400)
    # 各スロットの (実行するスレッド, 命令, 実行後の共有変数 count)
    cases = [
        (56, '正しく動く場合',
         [('A', 'LOAD', 5), ('A', 'ADD', 5), ('A', 'STORE', 6),
          ('B', 'LOAD', 6), ('B', 'ADD', 6), ('B', 'STORE', 7)],
         '7（正しい）', False),
        (216, '壊れる場合',
         [('A', 'LOAD', 5), ('B', 'LOAD', 5), ('A', 'ADD', 5),
          ('B', 'ADD', 5), ('A', 'STORE', 6), ('B', 'STORE', 6)],
         '6（更新が1つ失われた）', True),
    ]
    for y0, title, order, res, bad in cases:
        f.text(400, y0 - 22, title, cls='b')
        f.text(70, y0 + 20, 'スレッド A', cls='t-s', anchor='end')
        f.text(70, y0 + 58, 'スレッド B', cls='t-s', anchor='end')
        for yy in (4, 40, 76):
            f.line(80, y0 + yy, 620, y0 + yy, cls='sm')
        for slot, (who, op, val) in enumerate(order):
            x = 86 + slot * 88
            top = y0 + (4 if who == 'A' else 40) + 4
            f.rect(x, top, 76, 28, cls='tint s' if who == 'A' else 'accT s')
            f.text(x + 38, top + 14, op, cls='t-xs m b')
            f.text(x + 38, y0 + 100, str(val), cls='t-xs m')
        f.text(70, y0 + 100, 'count', cls='t-xs lbl', anchor='end')
        f.text(626, y0 + 100, '→ ' + res, cls='t-s b' + (' acc' if bad else ''),
               anchor='start')
    f.text(400, 378, '同じコードでも、命令の食い違い方で結果が変わる', cls='t-s b')
    return f


def f0705():
    """デッドロックの資源グラフ"""
    f = Fig(680, 350)
    for k, (bx, title, cyc) in enumerate([(40, '循環待ちがある（デッドロック）', True),
                                          (380, '取得順序を統一した（起きない）', False)]):
        f.text(bx + 130, 34, title, cls='b')
        f.circle(bx + 50, 110, 30, cls='tint s')
        f.text(bx + 50, 110, 'A', cls='b')
        f.circle(bx + 50, 230, 30, cls='tint s')
        f.text(bx + 50, 230, 'B', cls='b')
        f.rect(bx + 190, 84, 52, 52, cls='accT s')
        f.text(bx + 216, 110, 'X', cls='b')
        f.rect(bx + 190, 204, 52, 52, cls='accT s')
        f.text(bx + 216, 230, 'Y', cls='b')
        if cyc:
            f.arrow(bx + 190, 104, bx + 82, 104, cls='s')      # X 保持→A
            f.arrow(bx + 66, 138, bx + 196, 208, cls='sa')     # A 要求→Y
            f.arrow(bx + 190, 240, bx + 82, 240, cls='s')      # Y 保持→B
            f.arrow(bx + 66, 202, bx + 196, 132, cls='sa')     # B 要求→X
            f.text(bx + 130, 288, '待ちの関係が閉路をなす', cls='t-s b acc')
        else:
            f.arrow(bx + 190, 104, bx + 82, 104, cls='s')
            f.arrow(bx + 66, 138, bx + 196, 208, cls='sa')
            f.arrow(bx + 66, 218, bx + 186, 120, cls='sm dash')
            f.text(bx + 130, 282, 'B も X を先に要求するので', cls='t-xs lbl')
            f.text(bx + 130, 298, '「A が X、B が Y」の状態にならない', cls='t-xs lbl')
    f.text(340, 334, '実線＝保持、太線＝要求。閉路ができなければデッドロックしない',
           cls='t-s b')
    return f


# ---------------------------------------------------------------- 第8回
def f0801():
    """割り込み処理の流れ"""
    f = Fig(700, 340)
    y0 = 90
    f.text(60, y0 + 20, 'CPU', cls='t-s b', anchor='end')
    segs = [('プロセス A を実行', 190, 'tint'), ('退避', 50, 'tint2'),
            ('ハンドラ', 96, 'accT'), ('復元', 50, 'tint2'),
            ('プロセス A を再開', 150, 'tint')]
    x = 74
    for lab, w, cls in segs:
        f.rect(x, y0, w, 40, cls=cls + ' s')
        f.text(x + w / 2, y0 + 20, lab, cls='t-xs')
        x += w
    y1 = 216
    f.text(60, y1 + 20, '周辺装置', cls='t-s b', anchor='end')
    f.rect(150, y1, 264, 40, cls='tint s')
    f.text(282, y1 + 20, '装置が独立に動作している', cls='t-xs')
    f.arrow(150, y1, 150, y0 + 44, cls='sm', marker='am')
    f.text(146, y1 - 14, '入出力を依頼', cls='t-xs lbl', anchor='end')
    f.arrow(414, y1, 414, y0 + 44, cls='sa')
    f.text(420, y1 - 14, '完了 → 割り込み信号', cls='t-xs acc b', anchor='start')

    f.rect(74, 34, 540, 34, cls='none sm dash', rx=6)
    f.text(344, 51, 'この間 CPU と装置が同時に動いている', cls='t-s b')
    f.lines(74, 290, ['① 現在の命令を完了する　② PC・レジスタ・フラグを退避する　'
                      '③ 特権モードに切り替わる',
                      '④ 割り込みベクタ表からハンドラの番地を得る　⑤ ハンドラを実行　'
                      '⑥ 復元して中断箇所へ戻る'],
            cls='t-xs lbl', anchor='start', lh=18)
    f.text(350, 330, '割り込まれたプログラムは、中断されたことに気づかない', cls='t-s b')
    return f


def f0802():
    """CPU 経由の転送と DMA"""
    f = Fig(680, 420)

    # 上段：CPU が1ワードずつ読んでは書く
    f.text(340, 34, 'CPU が転送する', cls='b')
    f.box(60, 60, 100, 52, ['装置'], cls='tint s', tcls='t-s')
    f.box(290, 60, 100, 52, ['CPU'], cls='accT s', tcls='t-s')
    f.box(520, 60, 100, 52, ['主記憶'], cls='tint s', tcls='t-s')
    f.arrow(160, 86, 286, 86, cls='s')
    f.arrow(390, 86, 516, 86, cls='s')
    f.text(340, 134, 'CPU は転送で占有され、他のことができない', cls='t-xs acc b')

    f.line(40, 176, 640, 176, cls='sm dot')

    # 下段：DMA コントローラが直接運び、CPU は別の仕事に戻る
    f.text(340, 210, 'DMA コントローラに任せる', cls='b')
    f.box(290, 236, 100, 40, ['CPU'], cls='bg s dash', tcls='t-s')
    f.text(400, 256, '別の処理に戻っている', cls='t-xs lbl', anchor='start')
    f.box(60, 306, 100, 52, ['装置'], cls='tint s', tcls='t-s')
    f.box(520, 306, 100, 52, ['主記憶'], cls='tint s', tcls='t-s')
    f.arrow(160, 332, 516, 332, cls='sa')
    f.text(300, 320, '直接運ぶ', cls='t-xs lbl')
    f.box(276, 268, 128, 34, ['DMA コントローラ'], cls='tint2 s', tcls='t-xs')
    f.line(340, 276, 340, 268, cls='sm dash')
    f.line(340, 302, 340, 330, cls='sm dash')
    f.text(340, 396, 'CPU が関与するのは、最初の指示と最後の通知だけ', cls='t-xs acc b')
    return f


def f0803():
    """キーマトリクスによるキー検出"""
    f = Fig(700, 300)
    for step in range(3):
        bx = 40 + step * 225
        f.text(bx + 82, 34, f'{step + 1}行目を通電', cls='t-s b')
        for r in range(3):
            y = 66 + r * 46
            cls = 'sa' if r == step else 'sm'
            f.line(bx, y, bx + 164, y, cls=cls)
            f.text(bx - 8, y, f'行{r + 1}', cls='t-xs lbl', anchor='end')
        for c in range(4):
            x = bx + 16 + c * 44
            f.line(x, 52, x, 66 + 2 * 46 + 22, cls='sm')
            if step == 0:
                f.text(x, 260, f'列{c + 1}', cls='t-xs lbl')
        # スイッチ（交点）
        for r in range(3):
            for c in range(4):
                x, y = bx + 16 + c * 44, 66 + r * 46
                pressed = (r, c) == (1, 2)
                f.circle(x, y, 5, cls='ink' if pressed else 'bg s')
        if step == 1:
            x = bx + 16 + 2 * 44
            f.line(x, 66 + 46, x, 66 + 2 * 46 + 22, cls='sa')
            f.text(x, 244, '電流あり', cls='t-xs acc b')
    f.text(350, 286, '104個のキーを 8×13 に並べれば、配線は 104本ではなく21本で済む',
           cls='t-s b')
    return f


def f0804():
    """仮想機械とコンテナの構成"""
    f = Fig(700, 380)
    for k, (bx, title) in enumerate([(40, '仮想機械'), (380, 'コンテナ')]):
        f.text(bx + 140, 32, title, cls='b')
        y = 300
        f.box(bx, y, 280, 40, ['ハードウェア'], cls='tint2 s', tcls='t-s')
        y -= 44
        if k == 0:
            f.box(bx, y, 280, 40, ['ハイパーバイザ'], cls='tint s', tcls='t-s')
            y -= 44
            for i in range(3):
                x = bx + i * 94
                f.box(x, y - 84, 88, 128, [], cls='none s')
                f.box(x + 4, y - 80, 80, 34, ['アプリ'], cls='accT s', tcls='t-xs')
                f.box(x + 4, y - 42, 80, 34, ['ライブラリ'], cls='tint s', tcls='t-xs')
                f.box(x + 4, y - 4, 80, 40, ['ゲスト OS'], cls='tint2 s', tcls='t-xs')
            f.text(bx + 140, y - 104, 'カーネルが3つ動く', cls='t-xs acc b')
            f.text(bx + 140, 358, '起動に数十秒、メモリは GB 単位。分離は強い', cls='t-xs lbl')
        else:
            f.box(bx, y, 280, 40, ['ホスト OS（カーネルは1つ）'], cls='tint s', tcls='t-s')
            y -= 44
            f.box(bx, y, 280, 34, ['コンテナランタイム'], cls='tint2 s', tcls='t-xs')
            y -= 38
            for i in range(3):
                x = bx + i * 94
                f.box(x, y - 76, 88, 80, [], cls='none s')
                f.box(x + 4, y - 72, 80, 34, ['アプリ'], cls='accT s', tcls='t-xs')
                f.box(x + 4, y - 34, 80, 34, ['ライブラリ'], cls='tint s', tcls='t-xs')
            f.text(bx + 140, y - 96, 'ゲスト OS の層がない', cls='t-xs acc b')
            f.text(bx + 140, 358, '起動は1秒未満、メモリは MB 単位。分離は中程度', cls='t-xs lbl')
    return f


def f0805():
    """サービスモデルと責任分界"""
    f = Fig(700, 400)
    layers = ['アプリケーション', 'データ', 'ランタイム', 'ミドルウェア', 'OS',
              '仮想化', 'サーバ', 'ストレージ', 'ネットワーク', '施設']
    models = [('オンプレミス', 10), ('IaaS', 5), ('PaaS', 2), ('SaaS', 0)]
    cw, ch = 148, 30
    for k, (name, user_layers) in enumerate(models):
        x = 60 + k * (cw + 14)
        f.text(x + cw / 2, 40, name, cls='b')
        for i, lab in enumerate(layers):
            y = 58 + i * ch
            mine = i < user_layers
            f.rect(x, y, cw, ch, cls='accT s' if mine else 'tint s')
            if k == 0:
                f.text(x + cw / 2, y + ch / 2, lab, cls='t-xs')
            elif i == user_layers - 1 or (user_layers == 0 and i == 0):
                pass
        if user_layers:
            f.line(x - 4, 58 + user_layers * ch, x + cw + 4, 58 + user_layers * ch, cls='s2')
    f.rect(60, 368, 20, 14, cls='accT s')
    f.text(88, 375, '利用者の責任', cls='t-xs', anchor='start')
    f.rect(190, 368, 20, 14, cls='tint s')
    f.text(218, 375, '事業者の責任', cls='t-xs', anchor='start')
    f.text(500, 375, '境界が上がるほど任せる範囲が広い', cls='t-xs b')
    return f


FIGURES = {
    '05-01': f0501, '05-02': f0502, '05-03': f0503, '05-04': f0504,
    '05-05': f0505, '05-06': f0506, '05-07': f0507,
    '06-01': f0601, '06-02': f0602, '06-03': f0603,
    '07-01': f0701, '07-02': f0702, '07-03': f0703, '07-04': f0704, '07-05': f0705,
    '08-01': f0801, '08-02': f0802, '08-03': f0803, '08-04': f0804, '08-05': f0805,
}


def f0706():
    """[旧 network2026 slide 545] パイプによるプロセス間通信"""
    f = Fig(700, 420)

    def proc(x, y, w, h, name, fds):
        """プロセスの箱と、その左端に並ぶファイル記述子の枡"""
        f.rect(x, y, w, h, cls='tint s', rx=4)
        f.text(x + w / 2, y + h / 2, name, cls='t-s b m')
        for i, (num, lab) in enumerate(fds):
            fy = y + 10 + i * 26
            f.rect(x - 26, fy, 26, 22, cls='accT sa' if lab else 'bg s')
            f.text(x - 13, fy + 11, str(num), cls='t-xs m b acc' if lab else 't-xs m')
        return x - 26

    f.text(350, 32, '%  ls -l /usr/include  |  wc', cls='b m')

    # ls のプロセス
    lx = proc(150, 66, 210, 88, 'ls -l /usr/include',
              [(0, False), (1, True), (2, False)])
    f.text(112, 87, 'キーボード', cls='t-xs lbl', anchor='end')
    f.line(116, 87, 124, 87, cls='sm')
    f.text(112, 113, '（付け替えた）', cls='t-xs acc b', anchor='end')
    f.text(112, 139, '画面', cls='t-xs lbl', anchor='end')
    f.line(116, 139, 124, 139, cls='sm')

    # wc のプロセス
    proc(150, 246, 210, 88, 'wc', [(0, True), (1, False), (2, False)])
    f.text(112, 267, '（付け替えた）', cls='t-xs acc b', anchor='end')
    f.text(112, 293, '画面', cls='t-xs lbl', anchor='end')
    f.line(116, 293, 124, 293, cls='sm')
    f.text(112, 319, '画面', cls='t-xs lbl', anchor='end')
    f.line(116, 319, 124, 319, cls='sm')

    # パイプ（土管）
    f.rect(430, 150, 130, 100, cls='tint2 s', rx=8)
    f.text(495, 190, 'パイプ', cls='t-s b')
    f.text(495, 210, '（カーネル内）', cls='t-xs lbl')
    f.path('M360,102 L495,102 L495,146', cls='sa', arrow='aa')
    f.text(430, 92, '書き口へ', cls='t-xs lbl')
    f.path('M495,254 L495,282 L364,282', cls='sa', arrow='aa')
    f.text(430, 300, '読み口から', cls='t-xs lbl')

    f.text(350, 360, '付け替えたのは片側だけ。ls は「1番に書く」、wc は「0番から読む」だけ',
           cls='t-s b')
    f.text(350, 384, '互いの存在を知らない2つのプログラムが、それだけでつながる',
           cls='t-xs lbl')

    # シェルの手順
    f.rect(596, 66, 96, 268, cls='none sm dash', rx=6)
    f.text(644, 86, 'シェルの手順', cls='t-xs b')
    for i, s in enumerate(['① pipe', '② fork', '③ dup', '④ execve']):
        f.rect(608, 106 + i * 56, 72, 40, cls='bg s', rx=3)
        f.text(644, 126 + i * 56, s, cls='t-xs m')
        if i < 3:
            f.line(644, 146 + i * 56, 644, 162 + i * 56, cls='sm', arrow='am')
    return f


FIGURES['07-06'] = f0706
