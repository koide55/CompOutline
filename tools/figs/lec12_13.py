"""第12〜13回の図。"""
import math

from svgkit import Fig


# ---------------------------------------------------------------- 第12回
def _lock(f, x, y, closed=True, cls='accT s'):
    """南京錠。閉じていれば施錠、開いていれば公開鍵で誰でも掛けられる状態。"""
    f.rect(x - 13, y, 26, 22, cls=cls, rx=3)
    if closed:
        f.path(f'M{x - 8},{y} L{x - 8},{y - 9} A8,8 0 0 1 {x + 8},{y - 9} L{x + 8},{y}',
               cls='s')
    else:
        f.path(f'M{x - 8},{y} L{x - 8},{y - 9} A8,8 0 0 1 {x + 8},{y - 9} L{x + 8},{y - 5}',
               cls='s')


def f1201():
    """公開鍵暗号による秘密の送信"""
    f = Fig(700, 400)
    f.box(40, 90, 130, 60, ['送信者'], cls='tint s', tcls='t-s')
    f.box(530, 90, 130, 60, ['受信者'], cls='tint s', tcls='t-s')

    # ① 公開鍵を配る
    f.arrow(526, 76, 174, 76, cls='sm', marker='am')
    f.text(350, 58, '① 公開鍵を配る（盗まれてよい）', cls='t-xs lbl')
    _lock(f, 350, 84, closed=False)

    # ② 暗号化して ③ 送る
    f.rect(210, 172, 110, 34, cls='bg s')
    f.text(265, 189, '平文', cls='t-xs')
    f.arrow(170, 120, 206, 168, cls='sa')
    f.text(150, 168, '② 公開鍵で', cls='t-xs lbl', anchor='end')
    f.text(150, 184, '   暗号化', cls='t-xs lbl', anchor='end')
    f.rect(380, 172, 110, 34, cls='tint2 s')
    f.text(435, 189, '暗号文', cls='t-xs')
    _lock(f, 350, 178)
    f.arrow(320, 189, 376, 189, cls='sa')
    f.arrow(490, 189, 526, 148, cls='sa')
    f.text(560, 178, '④ 秘密鍵で復号', cls='t-xs lbl', anchor='start')

    # 盗聴者
    f.box(300, 250, 130, 46, ['盗聴者'], cls='none s dash', tcls='t-s')
    f.arrow(400, 214, 400, 246, cls='sm', marker='am')
    f.text(446, 274, '暗号文は読めるが、秘密鍵がないので復号できない',
           cls='t-xs acc b', anchor='start')

    f.text(350, 336, '錠は誰でも掛けられるが、開けられるのは鍵を持つ本人だけ', cls='t-s b')
    f.text(350, 360, 'n 人が通信するのに必要な鍵は 2n 個（共通鍵なら n(n−1)/2 個）',
           cls='t-xs lbl')
    f.text(350, 384, '公開鍵暗号は遅いので、実際は共通鍵を渡すのに使う（ハイブリッド方式）',
           cls='t-xs lbl')
    return f


def f1202():
    """ディジタル署名の生成と検証"""
    f = Fig(700, 430)
    # 生成
    f.text(350, 34, '署名する側', cls='b')
    f.box(40, 56, 110, 44, ['文書'], cls='bg s', tcls='t-s')
    f.box(220, 56, 120, 44, ['ハッシュ関数'], cls='tint s', tcls='t-xs')
    f.box(400, 56, 110, 44, ['ハッシュ値'], cls='tint2 s', tcls='t-xs')
    f.box(570, 56, 90, 44, ['署名'], cls='accT s', tcls='t-s')
    f.arrow(150, 78, 216, 78, cls='sm', marker='am')
    f.arrow(340, 78, 396, 78, cls='sm', marker='am')
    f.arrow(510, 78, 566, 78, cls='sa', label='秘密鍵', lcls='t-xs lbl', dy=-8)

    f.line(40, 136, 660, 136, cls='sm dot')

    # 検証
    f.text(350, 166, '検証する側', cls='b')
    f.box(40, 190, 110, 44, ['受け取った文書'], cls='bg s', tcls='t-xs')
    f.box(220, 190, 120, 44, ['ハッシュ関数'], cls='tint s', tcls='t-xs')
    f.box(400, 190, 110, 44, ['ハッシュ値 A'], cls='tint2 s', tcls='t-xs')
    f.arrow(150, 212, 216, 212, cls='sm', marker='am')
    f.arrow(340, 212, 396, 212, cls='sm', marker='am')

    f.box(40, 262, 110, 44, ['受け取った署名'], cls='accT s', tcls='t-xs')
    f.box(400, 262, 110, 44, ['ハッシュ値 B'], cls='tint2 s', tcls='t-xs')
    f.arrow(150, 284, 396, 284, cls='sa', label='公開鍵で処理', lcls='t-xs lbl', dy=-8)

    f.box(560, 222, 100, 62, ['A と B を', '比べる'], cls='tint s', tcls='t-xs', lh=16)
    f.arrow(510, 212, 556, 240, cls='sm', marker='am')
    f.arrow(510, 284, 556, 268, cls='sm', marker='am')
    f.text(350, 332, '一致 → 本人が署名し、改竄もされていない', cls='t-xs b')
    f.text(350, 350, '不一致 → 改竄されたか、偽の署名', cls='t-xs lbl')

    f.text(350, 386, '秘密鍵を持つのは本人だけなので、それを作れたのは本人しかいない',
           cls='t-s b')
    f.text(350, 410, '署名は文書を秘密にしない。秘密にしたければ暗号化も併せて行う',
           cls='t-xs lbl')
    return f


def f1203():
    """証明書の信頼の連鎖"""
    f = Fig(700, 420)
    certs = [('サーバ証明書', 'www.example.com', 300),
             ('中間 CA 証明書', '中間認証局', 200),
             ('ルート CA 証明書', 'ルート認証局（自己署名）', 100)]
    for name, subj, y in certs:
        f.box(180, y, 240, 62, [name, subj], cls='tint s' if y > 100 else 'accT s',
              tcls='t-s', lh=20)
    for y in (300, 200):
        f.arrow(300, y, 300, y - 38, cls='sa')
        f.text(316, y - 20, '上の秘密鍵で署名されている', cls='t-xs lbl', anchor='start')
    # 自己署名のループ
    f.path('M180,120 C140,120 140,160 180,150', cls='sa', arrow='aa')
    f.text(126, 136, '自己署名', cls='t-xs lbl', anchor='end')

    # トラストストア
    f.rect(150, 74, 300, 114, cls='none s dash', rx=8)
    f.text(300, 62, 'ブラウザ／OS に組み込まれたトラストストア', cls='t-s b')

    f.text(300, 386, '最終的な信頼の根拠は「ブラウザや OS の開発元がこの CA を信頼した」こと',
           cls='t-s b')

    f.rect(470, 200, 200, 150, cls='none sm', rx=6)
    f.text(570, 222, '検証は下から上へ', cls='t-s b')
    f.lines(486, 246, ['① 名前がアクセス先と一致するか',
                       '② 有効期限内か',
                       '③ 発行者の署名が正しいか',
                       '④ 失効していないか',
                       '⑤ トラストストアに到達したか'],
            cls='t-xs', anchor='start', lh=19)
    f.text(570, 366, 'どれか1つでも欠ければ警告', cls='t-xs acc b')
    f.text(300, 410, '起点が数百の CA に分散していることが、この仕組みの弱点でもある',
           cls='t-xs lbl')
    return f


# ---------------------------------------------------------------- 第13回
def f1301():
    """プログラミングと機械学習の違い"""
    f = Fig(680, 340)
    for k, (oy, title, ins, out) in enumerate([
            (56, '従来のプログラミング', ['規則（人間が書く）', '入力データ'], '答え'),
            (196, '機械学習', ['入力データ', '答え（正解ラベル）'], '規則（モデル）')]):
        f.text(340, oy - 22, title, cls='b')
        for i, lab in enumerate(ins):
            f.box(40, oy + i * 46, 190, 38, [lab], cls='tint s', tcls='t-xs')
            f.arrow(230, oy + i * 46 + 19, 286, oy + 42, cls='sm', marker='am')
        f.box(290, oy + 20, 120, 44, ['計算機'], cls='tint2 s', tcls='t-s')
        f.arrow(410, oy + 42, 466, oy + 42, cls='sa')
        f.box(470, oy + 20, 180, 44, [out], cls='accT s', tcls='t-s')
    f.text(340, 322, '与えるものと出てくるものが入れ替わっている', cls='t-s b')
    return f


def f1302():
    """ニューラルネットワークの構造"""
    f = Fig(700, 420)
    layers = [(120, 4, '入力層'), (260, 6, '隠れ層1'), (400, 6, '隠れ層2'), (540, 3, '出力層')]
    pos = []
    for x, n, name in layers:
        col = []
        for i in range(n):
            y = 178 - (n - 1) * 30 / 2 + i * 30
            col.append((x, y))
        pos.append(col)
        f.text(x, 330, name, cls='t-s b')
    for a in range(len(pos) - 1):
        for (x1, y1) in pos[a]:
            for (x2, y2) in pos[a + 1]:
                f.line(x1 + 11, y1, x2 - 11, y2, cls='sm')
    for a, col in enumerate(pos):
        for (x, y) in col:
            f.circle(x, y, 11, cls='tint s' if a else 'accT s')
    f.text(180, 80, '重み w', cls='t-xs acc b')
    f.line(176, 88, 168, 116, cls='sa')

    # 1ユニットの中身
    f.rect(430, 40, 250, 96, cls='none sm dash', rx=6)
    f.text(555, 58, '1つのユニットの中身', cls='t-s b')
    f.text(555, 82, '入力の重み付き和', cls='t-xs')
    f.arrow(555, 92, 555, 104, cls='sm', marker='am')
    f.text(555, 118, '活性化関数（非線形）→ 出力', cls='t-xs')

    f.text(350, 366, '非線形の活性化関数がないと、何層重ねても1つの線形変換にしかならない',
           cls='t-s b')
    f.text(350, 392, '重みを少しずつ動かして誤差を小さくしていく（勾配降下法）', cls='t-xs lbl')
    f.arrow(560, 292, 120, 292, cls='sa dash')
    f.text(340, 308, '誤差逆伝播（出力側から逆にたどる）', cls='t-xs acc b')
    return f


def f1303():
    """自己注意の重み"""
    f = Fig(720, 400)
    words = ['昨日', '買った', '本', 'を', '図書館', 'で', '借りた', '資料', 'と', '一緒に', '返した']
    weights = [0.1, 0.2, 0.9, 0.15, 0.25, 0.05, 0.4, 0.85, 0.1, 0.2, 0]
    x0, y0 = 40, 260
    xs = []
    for i, w in enumerate(words):
        wd = 22 + len(w) * 15
        f.rect(x0, y0, wd, 34, cls='accT s' if i == len(words) - 1 else 'tint s')
        f.text(x0 + wd / 2, y0 + 17, w, cls='t-xs')
        xs.append(x0 + wd / 2)
        x0 += wd + 6
    src = xs[-1]
    for i, (x, wgt) in enumerate(zip(xs[:-1], weights[:-1])):
        sw = 0.6 + wgt * 4.4
        f.path(f'M{src},{y0} C{src},{y0 - 60 - wgt * 60} {x},{y0 - 60 - wgt * 60} {x},{y0}',
               cls='sa' if wgt > 0.5 else 'sm', stroke_width=round(sw, 1),
               stroke_opacity=round(0.25 + wgt * 0.75, 2))
    f.text(360, 46, '「返した」が、文中のどの語にどれだけ注目するか', cls='b')
    f.text(360, 70, '線の太さが注意の重み', cls='t-xs lbl')
    f.text(xs[2], y0 + 52, '↑ 強い', cls='t-xs acc b')
    f.text(xs[7], y0 + 52, '↑ 強い', cls='t-xs acc b')
    f.text(360, 338, 'すべての語の関係を一度に計算するので、GPU で完全に並列化できる',
           cls='t-s b')
    f.text(360, 362, 'RNN のように前から順に処理する必要がない。これが大規模化を可能にした',
           cls='t-xs lbl')
    f.text(360, 386, '（順序の情報は位置エンコーディングで別に与える）', cls='t-xs lbl')
    return f


def f1304():
    """エージェントの動作ループ"""
    f = Fig(720, 440)
    cx, cy, r = 280, 210, 108
    steps = [('観測', -90), ('計画', -10), ('行動', 90), ('結果を見る', 190)]
    for name, ang in steps:
        a = math.radians(ang)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        f.circle(x, y, 44, cls='tint s')
        f.text(x, y, name, cls='t-s b')
    for a0, a1 in [(-90, -10), (-10, 90), (90, 190), (190, 270)]:
        s, e = math.radians(a0 + 26), math.radians(a1 - 26)
        f.path(f'M{cx + r * math.cos(s):.1f},{cy + r * math.sin(s):.1f} '
               f'A{r},{r} 0 0 1 {cx + r * math.cos(e):.1f},{cy + r * math.sin(e):.1f}',
               cls='sa', arrow='aa')
    f.circle(cx, cy, 40, cls='accT s')
    f.text(cx, cy, 'LLM', cls='b')

    # ツール
    tools = ['検索', 'コード実行', 'ファイル操作', 'API 呼び出し']
    for i, t in enumerate(tools):
        f.box(500, 70 + i * 56, 150, 40, [t], cls='tint2 s', tcls='t-xs')
        f.arrow(396, 250, 496, 90 + i * 56, cls='sm', marker='am')
    f.text(575, 46, 'ツール', cls='t-s b')

    # 記憶
    f.box(40, 180, 110, 56, ['記憶'], cls='tint s', tcls='t-s')
    f.arrow(150, 200, 166, 200, cls='sm', marker='am')
    f.arrow(166, 220, 150, 220, cls='sm', marker='am')

    # 人間の承認
    f.rect(180, 348, 340, 42, cls='accT s', rx=6)
    f.text(350, 369, '人間による承認（不可逆な操作の前に必ず）', cls='t-s b')
    f.arrow(280, 322, 280, 344, cls='sa')

    f.text(360, 416, 'ツール利用が LLM の弱点を補う。ただし行動するがゆえに、'
                     '誤りが取り返しのつかない結果になりうる', cls='t-xs b')
    return f


FIGURES = {
    '12-01': f1201, '12-02': f1202, '12-03': f1203,
    '13-01': f1301, '13-02': f1302, '13-03': f1303, '13-04': f1304,
}
