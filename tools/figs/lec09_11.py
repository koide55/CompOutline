"""第9〜11回の図。

[旧] と注記したものは CompOutline2024.pptx の該当スライドから
図形の座標を取り出して引き継いだもの。
"""
from svgkit import Fig


# ---------------------------------------------------------------- 第9回
def f0901():
    """回線交換とパケット交換"""
    f = Fig(700, 440)
    # 網の形は上下で共通。相対座標で持ち、パネルごとにずらす
    shape = [(60, 60), (180, 20), (180, 110), (300, 60), (300, 150), (420, 90)]
    edges = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5), (1, 2)]
    for k, (title, circuit) in enumerate([('回線交換', True), ('パケット交換', False)]):
        oy = 60 + k * 210
        f.text(250, oy - 26, title, cls='b')
        pos = [(x + 20, y + oy) for x, y in shape]
        for i, j in edges:
            f.line(*pos[i], *pos[j], cls='sm')
        if circuit:
            f.path(f'M{pos[0][0]},{pos[0][1]} L{pos[1][0]},{pos[1][1]} '
                   f'L{pos[3][0]},{pos[3][1]} L{pos[5][0]},{pos[5][1]}',
                   cls='sa', stroke_width=7)
            notes = ['経路を確保して占有する', '他の通信はこの線を使えない',
                     '話していない間も空けられない']
        else:
            for idx, p in enumerate([[0, 1, 3, 5], [0, 2, 3, 5], [0, 2, 4, 5]]):
                d = 'M' + ' L'.join(f'{pos[i][0]},{pos[i][1] + (idx - 1) * 6}' for i in p)
                f.path(d, cls='sa dash' if idx else 'sa', arrow='aa')
            for idx, (px, py) in enumerate([(120, oy + 24), (230, oy + 112),
                                            (350, oy + 30)]):
                f.rect(px, py, 20, 15, cls='accT sa')
                f.text(px + 10, py + 8, str(idx + 1), cls='t-xs')
            notes = ['パケットが別々の経路を通る', '同じ線を多数の通信で共有できる',
                     '宛先で番号順に並べ直す']
        for x, y in pos:
            f.circle(x, y, 13, cls='tint s')
        f.text(pos[0][0], pos[0][1] - 26, '送信元', cls='t-xs lbl')
        f.text(pos[5][0], pos[5][1] + 28, '宛先', cls='t-xs lbl')
        for i, n in enumerate(notes):
            f.text(500, oy + 46 + i * 20, n,
                   cls='t-xs acc b' if i == 0 else 't-xs lbl', anchor='start')
    f.line(40, 250, 660, 250, cls='sm dot')
    return f


def f0902():
    """カプセル化"""
    f = Fig(700, 340)
    rows = [(['HTTP メッセージ'], 'アプリケーション層'),
            (['TCP ヘッダ', 'HTTP メッセージ'], 'トランスポート層'),
            (['IP ヘッダ', 'TCP ヘッダ', 'HTTP メッセージ'], 'インターネット層'),
            (['Ethernet ヘッダ', 'IP ヘッダ', 'TCP ヘッダ', 'HTTP メッセージ', 'FCS'],
             'データリンク層')]
    widths = {'HTTP メッセージ': 200, 'TCP ヘッダ': 84, 'IP ヘッダ': 76,
              'Ethernet ヘッダ': 104, 'FCS': 44}
    for i, (parts, layer) in enumerate(rows):
        y = 56 + i * 62
        total = sum(widths[p] for p in parts)
        x = 430 - total / 2          # 一番長い行でも層の名前と重ならない位置に寄せる
        for p in parts:
            w = widths[p]
            cls = 'accT s' if p == 'HTTP メッセージ' else 'tint s'
            f.rect(x, y, w, 38, cls=cls)
            f.text(x + w / 2, y + 19, p, cls='t-xs')
            x += w
        f.text(160, y + 19, layer, cls='t-s b', anchor='end')
        if i:
            f.arrow(170, y - 16, 170, y - 2, cls='sm', marker='am')
    f.text(400, 306, '層を降りるごとに、その層のヘッダで包まれる。受信側では逆順に剥がす',
           cls='t-s b')
    f.text(400, 328, '各層は自分のヘッダしか見ない', cls='t-xs lbl')
    return f


def f0903():
    """[旧 slide 191] 階層を降りて上がる"""
    f = Fig(700, 380)
    layers = ['アプリケーション層', 'トランスポート層', 'インターネット層',
              'データリンク層', '物理層']
    cols = [(40, 'ホスト', 5), (208, 'ルータ', 3), (376, 'ルータ', 3), (544, 'ホスト', 5)]
    lh, top = 38, 96
    for bx, name, depth in cols:
        f.text(bx + 58, 76, name, cls='b')
        for i, lab in enumerate(layers):
            if i < 5 - depth:
                continue
            y = top + i * lh
            f.rect(bx, y, 116, lh, cls='tint s' if depth == 5 else 'tint2 s')
            f.text(bx + 58, y + lh / 2, lab, cls='t-xs')
        if depth == 3:
            f.text(bx + 58, top + 1.4 * lh, '下から3層だけ', cls='t-xs lbl')
    # 論理的な会話（両端のホストの最上層どうし）
    y = top + lh / 2
    f.path(f'M156,{y} L544,{y}', cls='sm dot')
    f.text(350, 60, '論理的には、同じ層どうしが会話しているように見える', cls='t-xs lbl')
    # 実際のデータの流れ。箱を突き抜けないよう、列の外側と列間のすき間を通す
    bot = top + 5 * lh          # 物理層の下端
    f.path(f'M30,{top + lh / 2} L30,{bot + 8} L152,{bot + 8}', cls='sa', arrow='aa')
    f.text(30, top - 4, '降りる', cls='t-xs acc b')
    for gap, a, b in [(182, 156, 208), (350, 324, 376), (518, 492, 544)]:
        f.line(a, bot + 8, b, bot + 8, cls='sa')
    f.path(f'M556,{bot + 8} L670,{bot + 8} L670,{top + lh / 2}', cls='sa', arrow='aa')
    f.text(670, top - 4, '上がる', cls='t-xs acc b')
    # 中継機器は L3 まで上がって、また降りる
    for bx in (266, 434):
        f.path(f'M{bx},{bot + 8} L{bx},{top + 2 * lh + lh}', cls='sa dash', arrow='aa')
    f.text(350, 332, 'スイッチは L2、ルータは L3 までしか上がらない。だから中継は速い',
           cls='t-s b')
    f.text(350, 358, '（旧スライドの構成をそのまま引き継いだ）', cls='t-xs lbl')
    return f


def f0904():
    """インターネットの構造"""
    f = Fig(700, 380)
    # Tier 1
    t1 = [(200, 70), (350, 60), (500, 70)]
    for x, y in t1:
        f.circle(x, y, 26, cls='accT s')
        f.text(x, y, 'Tier 1', cls='t-xs b')
    for i in range(3):
        for j in range(i + 1, 3):
            f.line(*t1[i], *t1[j], cls='s2')
    f.text(600, 62, 'ピアリング', cls='t-xs lbl', anchor='start')
    f.text(600, 78, '（対等・無料）', cls='t-xs lbl', anchor='start')

    # 地域 ISP
    t2 = [(140, 180), (300, 180), (460, 180)]
    for x, y in t2:
        f.circle(x, y, 24, cls='tint s')
        f.text(x, y, '地域ISP', cls='t-xs')
    for a, b in [(0, 0), (1, 1), (2, 2), (0, 1), (2, 1)]:
        f.line(t2[a][0], t2[a][1] - 22, t1[b][0], t1[b][1] + 24, cls='sm')

    # IX
    f.rect(500, 156, 130, 48, cls='tint2 s', rx=6)
    f.text(565, 172, 'IX', cls='b')
    f.text(565, 190, '（相互接続点）', cls='t-xs')
    for x, y in t2[1:]:
        f.line(x + 22, y, 498, 180, cls='sm')
    f.line(565, 154, 500, 92, cls='sm')

    # アクセス ISP と末端
    t3 = [(90, 268), (200, 268), (320, 268), (440, 268)]
    for x, y in t3:
        f.circle(x, y, 20, cls='bg s')
        f.text(x, y, 'ISP', cls='t-xs')
    for i, (x, y) in enumerate(t3):
        f.line(x, y - 18, t2[min(i // 2, 2)][0], t2[min(i // 2, 2)][1] + 22, cls='sm')
        f.box(x - 44, 316, 88, 32, [['大学', '企業', '家庭', '家庭'][i]],
              cls='tint s', tcls='t-xs')
        f.line(x, 288, x, 314, cls='sm')
    f.text(600, 268, 'トランジット', cls='t-xs lbl', anchor='start')
    f.text(600, 284, '（費用を払って', cls='t-xs lbl', anchor='start')
    f.text(600, 300, '  到達性を買う）', cls='t-xs lbl', anchor='start')
    f.text(350, 372, '中央の管理者はいない。独立した多数の AS が相互接続している', cls='t-s b')
    return f


def f0905():
    """スイッチの学習と転送"""
    f = Fig(700, 450)
    for step in range(3):
        oy = 30 + step * 130
        f.text(40, oy + 10, f'({step + 1})', cls='b', anchor='start')
        f.rect(190, oy + 22, 130, 56, cls='tint s', rx=6)
        f.text(255, oy + 50, 'スイッチ', cls='t-s b')
        ports = [('A', 120, oy + 10), ('B', 120, oy + 90), ('C', 390, oy + 10),
                 ('D', 390, oy + 90)]
        for name, x, y in ports:
            f.circle(x, y, 16, cls='bg s')
            f.text(x, y, name, cls='t-s')
            if x < 200:
                f.line(x + 16, y, 190, oy + (36 if y < oy + 50 else 64), cls='sm')
            else:
                f.line(x - 16, y, 320, oy + (36 if y < oy + 50 else 64), cls='sm')
        # 転送の様子
        if step == 0:
            f.arrow(136, oy + 14, 186, oy + 34, cls='sa')      # A が送る
            f.arrow(324, oy + 36, 374, oy + 16, cls='sm')      # C へ
            f.arrow(324, oy + 64, 374, oy + 84, cls='sm')      # D へ
            f.arrow(186, oy + 64, 138, oy + 84, cls='sm')      # B へ
            note = 'B の位置を知らないので、受信ポート以外の全ポートへ（フラッディング）'
            tbl = ['A → ポート1']
        elif step == 1:
            f.arrow(136, oy + 86, 186, oy + 64, cls='sa')      # B が返す
            f.arrow(186, oy + 36, 138, oy + 16, cls='sa')      # A へだけ
            note = '表を見て、ポート1にだけ転送する'
            tbl = ['A → ポート1', 'B → ポート2']
        else:
            f.arrow(136, oy + 14, 186, oy + 34, cls='sa')
            f.arrow(186, oy + 64, 138, oy + 84, cls='sa')
            f.text(408, oy + 50, 'C, D には流れない', cls='t-xs lbl')
            note = '以後 A↔B の通信はポート1と2の間だけで完結する'
            tbl = ['A → ポート1', 'B → ポート2']
        f.text(60, oy + 118, note, cls='t-xs', anchor='start')
        f.rect(500, oy + 14, 160, 24 + len(tbl) * 18, cls='none sm', rx=4)
        f.text(580, oy + 28, 'MAC アドレステーブル', cls='t-xs b')
        for i, r in enumerate(tbl):
            f.text(580, oy + 46 + i * 18, r, cls='t-xs m')
    f.text(350, 438, '送信元 MAC を観察するだけで、転送表が自律的に埋まっていく', cls='t-s b')
    return f


# ---------------------------------------------------------------- 第10回
def f1001():
    """パケットの中継"""
    f = Fig(760, 360)
    nodes = [('送信元\n192.0.2.10', 68), ('ルータ1', 232), ('ルータ2', 380),
             ('ルータ3', 528), ('宛先\n198.51.100.5', 692)]
    y = 60
    for name, x in nodes:
        parts = name.split('\n')
        w = 120 if len(parts) > 1 else 88
        f.box(x - w / 2, y, w, 52, parts, cls='tint s' if len(parts) > 1 else 'tint2 s',
              tcls='t-xs', lh=15)
    segs = [(68, 232), (232, 380), (380, 528), (528, 692)]
    for i, (a, b) in enumerate(segs):
        f.arrow(a + 52, y + 26, b - 52, y + 26, cls='sa')
        mid = (a + b) / 2
        f.rect(mid - 68, y + 78, 136, 66, cls='bg s')
        f.text(mid, y + 94, '送信元IP 192.0.2.10', cls='t-xs')
        f.text(mid, y + 110, '宛先IP 198.51.100.5', cls='t-xs')
        f.line(mid - 68, y + 120, mid + 68, y + 120, cls='sm')
        f.text(mid, y + 133, f'MAC：区間{i + 1}用', cls='t-xs acc b')
        f.line(mid, y + 52, mid, y + 76, cls='sm dot')
    f.text(60, y + 102, 'IP は\n変わらない'.split('\n')[0], cls='t-xs lbl', anchor='end')
    f.text(60, y + 118, '変わらない', cls='t-xs lbl', anchor='end')
    f.text(60, y + 136, 'MAC は毎回', cls='t-xs acc b', anchor='end')
    f.text(60, y + 152, '書き換わる', cls='t-xs acc b', anchor='end')
    f.text(380, 272, 'IP は最終目的地、MAC は次の1ホップを表す', cls='t-s b')
    f.text(380, 298, '中継のたびに MAC は書き換わるが、IP は最初から最後まで変わらない',
           cls='t-xs lbl')
    f.text(380, 324, 'TTL はルータを通るたびに1減り、0で破棄される（経路が輪でも回り続けない）',
           cls='t-xs lbl')
    return f


def f1002():
    """NAPT による変換"""
    f = Fig(700, 360)
    f.text(130, 34, '内部ネットワーク', cls='b')
    hosts = [('192.168.1.10 : 50001', 70), ('192.168.1.11 : 50002', 150)]
    for lab, y in hosts:
        f.box(40, y, 190, 44, [lab], cls='tint s', tcls='t-xs m')
        f.arrow(230, y + 22, 288, y + 22, cls='sa')
    f.box(290, 56, 140, 152, [], cls='tint2 s')
    f.text(360, 72, 'NAT ルータ', cls='t-s b')
    f.rect(300, 86, 120, 96, cls='bg s')
    f.text(360, 102, '変換表', cls='t-xs b')
    f.text(360, 124, '50001 ↔ 40001', cls='t-xs m')
    f.text(360, 142, '50002 ↔ 40002', cls='t-xs m')
    f.text(360, 166, '（ポートで区別）', cls='t-xs lbl')
    f.arrow(430, 96, 496, 96, cls='sa')
    f.text(463, 74, '203.0.113.7 : 40001', cls='t-xs m lbl')
    f.arrow(496, 160, 430, 160, cls='sa')
    f.text(496, 186, '戻りは表を逆引きする', cls='t-xs lbl')
    f.box(500, 92, 160, 76, ['インターネット上', 'のサーバ'], cls='tint s', tcls='t-s', lh=18)
    f.text(355, 236, 'グローバルアドレス1個を、多数の機器で共有できる', cls='t-s b')
    f.rect(90, 264, 520, 74, cls='none sm dash', rx=6)
    f.text(350, 284, '副作用', cls='t-s b')
    f.text(350, 304, '外部から内部の機器に接続を「開始」できない。内部から出た通信の戻りしか通せない',
           cls='t-xs')
    f.text(350, 322, '簡易なファイアウォールとして働く一方、P2P や直接通信を難しくした',
           cls='t-xs lbl')
    return f


def f1003():
    """3ウェイハンドシェイクと切断"""
    f = Fig(660, 420)
    lx, rx = 170, 490
    f.text(lx, 36, 'クライアント', cls='b')
    f.text(rx, 36, 'サーバ', cls='b')
    f.line(lx, 50, lx, 384, cls='sm')
    f.line(rx, 50, rx, 384, cls='sm')
    msgs = [('SYN  seq=x', 70, 1), ('SYN+ACK  seq=y, ack=x+1', 108, -1),
            ('ACK  ack=y+1', 146, 1)]
    for text, y, d in msgs:
        f.arrow(lx if d > 0 else rx, y, rx if d > 0 else lx, y + 22, cls='sa')
        f.text(330, y + 4 if d > 0 else y + 4, text, cls='t-xs m')
    f.brace_v(112, 66, 172, '確立に1往復', side=-1)
    f.rect(230, 190, 200, 44, cls='accT s', rx=4)
    f.text(330, 212, 'データ転送', cls='t-s b')
    f.line(lx, 212, 228, 212, cls='sm dot')
    f.line(432, 212, rx, 212, cls='sm dot')
    fin = [('FIN', 258, 1), ('ACK', 292, -1), ('FIN', 326, -1), ('ACK', 360, 1)]
    for text, y, d in fin:
        f.arrow(lx if d > 0 else rx, y, rx if d > 0 else lx, y + 16, cls='s')
        f.text(330, y + 2, text, cls='t-xs m')
    f.brace_v(112, 254, 380, '切断は4ウェイ', side=-1)
    f.text(330, 400, '双方が「自分の開始番号」と「相手の番号を受け取った」を伝える最小の回数',
           cls='t-s b')
    return f


def f1004():
    """反復問い合わせによる名前解決"""
    f = Fig(700, 420)
    f.box(40, 150, 110, 56, ['クライアント'], cls='tint s', tcls='t-s')
    f.box(220, 150, 130, 56, ['キャッシュ', 'DNS サーバ'], cls='accT s', tcls='t-xs', lh=16)
    f.arrow(150, 168, 216, 168, cls='sa', label='① 問い合わせ', lcls='t-xs lbl')
    f.arrow(216, 192, 152, 192, cls='sa', label='⑤ 203.0.113.42', lcls='t-xs lbl', dy=16)
    servers = [('ルート DNS', 46, '② 「.com はあちらに聞け」'),
               ('.com の DNS', 136, '③ 「example.com はあちらに聞け」'),
               ('example.com の DNS', 226, '④ 「www は 203.0.113.42」')]
    for name, y, reply in servers:
        f.box(452, y, 200, 42, [name], cls='tint s', tcls='t-s')
        f.arrow(354, 172, 448, y + 14, cls='sm', marker='am')
        f.path(f'M448,{y + 30} L354,182', cls='sm', arrow='am')
        f.text(552, y + 58, reply, cls='t-xs lbl')   # 箱の下に置いて重ならないように
    f.text(285, 236, 'TTL の間キャッシュする', cls='t-xs lbl')
    f.text(350, 348, '誰も全体を知らないが、階層をたどれば必ず答えに着く', cls='t-s b')
    f.text(350, 374, 'キャッシュがあるので、実際はほとんどが1〜2段階で終わる', cls='t-xs lbl')
    f.text(350, 400, '名前とアドレスを分けたので、サーバを移しても同じ名前で届く', cls='t-xs lbl')
    return f


def f1005():
    """Web アプリケーションの三層構成"""
    f = Fig(700, 380)
    f.box(40, 140, 110, 60, ['ブラウザ'], cls='tint s', tcls='t-s')
    f.text(95, 216, 'プレゼンテーション層', cls='t-xs lbl')
    f.box(40, 56, 110, 44, ['CDN'], cls='tint2 s', tcls='t-s')
    f.path('M95,138 L95,102', cls='sm dash', arrow='am')
    f.text(160, 78, '近くから返せるものは', cls='t-xs lbl', anchor='start')
    f.text(160, 94, 'ここで返す', cls='t-xs lbl', anchor='start')

    f.box(210, 140, 100, 60, ['ロード', 'バランサ'], cls='tint s', tcls='t-xs', lh=16)
    f.arrow(150, 170, 206, 170, cls='sa', label='HTTP', lcls='t-xs lbl')
    for i in range(3):
        y = 96 + i * 62
        f.box(370, y, 130, 46, ['アプリケーション', 'サーバ'], cls='tint s', tcls='t-xs', lh=15)
        f.arrow(310, 170, 366, y + 23, cls='sm', marker='am')
        f.arrow(500, y + 23, 556, 178, cls='sm', marker='am')
    f.text(435, 300, 'アプリケーション層', cls='t-xs lbl')
    f.box(560, 150, 110, 56, ['データベース'], cls='accT s', tcls='t-s')
    f.box(560, 224, 110, 40, ['レプリカ'], cls='bg s dash', tcls='t-xs')
    f.line(615, 206, 615, 222, cls='sm dash')
    f.text(615, 288, 'データ層', cls='t-xs lbl')
    f.text(350, 336, 'HTTP がステートレスだから、アプリケーションサーバは何台に増やしてもよい',
           cls='t-s b')
    f.text(350, 360, 'ログイン状態などは Cookie やトークンとしてクライアント側に持たせる',
           cls='t-xs lbl')
    return f


# ---------------------------------------------------------------- 第11回
def _table(f, x, y, cols, rows, cw=None, ch=26, head='tint2 s', body='bg s',
           title=None, tcls='t-xs'):
    cw = cw or [86] * len(cols)
    if title:
        f.text(x + sum(cw) / 2, y - 14, title, cls='t-s b')
    cx = x
    for i, c in enumerate(cols):
        f.rect(cx, y, cw[i], ch, cls=head)
        f.text(cx + cw[i] / 2, y + ch / 2, c, cls=tcls + ' b')
        cx += cw[i]
    for r, row in enumerate(rows):
        cx = x
        for i, v in enumerate(row):
            f.rect(cx, y + (r + 1) * ch, cw[i], ch, cls=body)
            f.text(cx + cw[i] / 2, y + (r + 1) * ch + ch / 2, v, cls=tcls)
            cx += cw[i]
    return y + (len(rows) + 1) * ch


def f1101():
    """[旧 slide 547-550] 正規化の前と後"""
    f = Fig(720, 462)
    _table(f, 60, 56,
           ['学籍番号', '氏名', '学部', '科目', '担当教員', '成績'],
           [['2S001', '山田', '工学部', '情報基礎', '佐藤', '85'],
            ['2S001', '山田', '工学部', '数学', '鈴木', '90'],
            ['2S002', '田中', '理学部', '情報基礎', '佐藤', '78']],
           cw=[92, 68, 78, 92, 86, 60], title='正規化していない表')
    # 冗長なセルを破線で囲む
    f.rect(152, 82, 146, 52, cls='none sa dash')
    f.rect(298, 82, 178, 26, cls='none sa dash')
    f.rect(298, 134, 178, 26, cls='none sa dash')
    f.text(556, 108, '同じ事実が', cls='t-xs acc b', anchor='start')
    f.text(556, 124, '何度も書かれている', cls='t-xs acc b', anchor='start')

    f.arrow(360, 176, 360, 200, cls='sa')
    f.text(376, 190, '正規化', cls='t-s b', anchor='start')

    _table(f, 40, 232, ['学籍番号', '氏名', '学部'],
           [['2S001', '山田', '工学部'], ['2S002', '田中', '理学部']],
           cw=[76, 56, 68], title='学生')
    _table(f, 268, 232, ['科目コード', '科目名', '担当教員'],
           [['C001', '情報基礎', '佐藤'], ['C002', '数学', '鈴木']],
           cw=[80, 76, 74], title='科目')
    _table(f, 512, 232, ['学籍番号', '科目コード', '成績'],
           [['2S001', 'C001', '85'], ['2S001', 'C002', '90'], ['2S002', 'C001', '78']],
           cw=[72, 76, 52], title='履修')
    # 外部キーの参照
    f.path('M548,362 C480,392 240,392 120,362', cls='sm', arrow='am')
    f.path('M624,362 C600,404 400,404 344,362', cls='sm', arrow='am')
    f.text(120, 336, '外部キーが参照する', cls='t-xs lbl')
    f.text(360, 424, '1つの事実は、1箇所にだけ書く', cls='t-s b')
    f.text(360, 446, 'こうすれば変更する場所も1箇所になり、矛盾が生じない', cls='t-xs lbl')
    return f


def f1102():
    """内部結合の仕組み"""
    f = Fig(700, 400)
    _table(f, 40, 60, ['学籍番号', '科目コード', '成績'],
           [['2S001', 'C001', '85'], ['2S001', 'C002', '90'],
            ['2S002', 'C001', '78'], ['2S009', 'C001', '60']],
           cw=[72, 76, 52], title='履修')
    _table(f, 320, 60, ['学籍番号', '氏名', '学部'],
           [['2S001', '山田', '工学部'], ['2S002', '田中', '理学部']],
           cw=[72, 56, 68], title='学生')
    # 一致する行を結ぶ
    for sy, ty in [(99, 99), (125, 99), (151, 125)]:
        f.path(f'M240,{sy} C280,{sy} 290,{ty} 318,{ty}', cls='sm', arrow='am')
    f.text(268, 190, '×', cls='b acc')
    f.text(268, 208, '相手がいない', cls='t-xs acc', anchor='middle')
    f.line(240, 177, 258, 186, cls='sa dot')

    _table(f, 190, 262, ['氏名', '科目コード', '成績'],
           [['山田', 'C001', '85'], ['山田', 'C002', '90'], ['田中', 'C001', '78']],
           cw=[76, 88, 60], title='結合の結果')
    f.text(350, 380, '内部結合では、一致する相手がない行（2S009）は結果に現れない',
           cls='t-s b')
    return f


def f1103():
    """レプリケーションとシャーディング"""
    f = Fig(700, 400)
    # レプリケーション
    f.text(350, 34, 'レプリケーション', cls='b')
    f.box(80, 56, 120, 50, ['プライマリ'], cls='accT s', tcls='t-s')
    for i in range(3):
        bx = 300 + i * 130
        f.box(bx, 56, 110, 50, [f'レプリカ{i + 1}'], cls='tint s', tcls='t-xs')
        # プライマリの右端から、各レプリカの上辺へ扇形に引く
        f.path(f'M200,74 C{240 + i * 20},{40 - i * 6} {bx - 20},{34} {bx + 55},52',
               cls='sm', arrow='am')
    f.text(140, 126, '書き込みはここだけ', cls='t-xs acc b')
    f.text(455, 126, '読み出しはどこからでも', cls='t-xs lbl')
    f.text(350, 150, '読み出しは分散できるが、書き込みは分散しない。複製には遅れが生じる',
           cls='t-xs lbl')

    f.line(40, 180, 660, 180, cls='sm dot')

    # シャーディング
    f.text(350, 212, 'シャーディング', cls='b')
    ranges = ['学籍番号\n1〜999', '学籍番号\n1000〜1999', '学籍番号\n2000〜2999',
              '学籍番号\n3000〜3999']
    for i, r in enumerate(ranges):
        x = 60 + i * 155
        f.box(x, 236, 140, 56, r.split('\n'), cls='tint s', tcls='t-xs', lh=16)
        f.box(x + 20, 306, 100, 36, [f'サーバ{i + 1}'], cls='tint2 s', tcls='t-xs')
        f.line(x + 70, 292, x + 70, 304, cls='sm')
    f.text(350, 366, '書き込みも分散できる。ただし複数シャードにまたがる結合と',
           cls='t-s b')
    f.text(350, 388, 'トランザクションが難しくなる', cls='t-s b')
    return f


FIGURES = {
    '09-01': f0901, '09-02': f0902, '09-03': f0903, '09-04': f0904, '09-05': f0905,
    '10-01': f1001, '10-02': f1002, '10-03': f1003, '10-04': f1004, '10-05': f1005,
    '11-01': f1101, '11-02': f1102, '11-03': f1103,
}


def f1006():
    """[旧 network2026 slide 555] ソケットの呼び出し順序（TCP）"""
    f = Fig(700, 470)
    f.text(180, 36, 'サーバ', cls='b')
    f.text(500, 36, 'クライアント', cls='b')

    srv = [('socket', 62), ('bind', 118), ('listen', 174), ('accept', 230)]
    cli = [('socket', 62), ('connect', 230)]
    for name, y in srv:
        f.box(110, y, 140, 42, [name], cls='tint s', tcls='t-s m b')
    for name, y in cli:
        f.box(430, y, 140, 42, [name], cls='tint s', tcls='t-s m b')
    for y in (104, 160, 216):
        f.line(180, y, 180, y + 14, cls='sm', arrow='am')
    f.line(500, 104, 500, 228, cls='sm', arrow='am')
    f.text(578, 166, 'サーバが待ち受けて', cls='t-xs lbl', anchor='start')
    f.text(578, 182, 'いれば、いつでも', cls='t-xs lbl', anchor='start')
    f.text(578, 198, '接続を要求できる', cls='t-xs lbl', anchor='start')

    # 接続の確立
    f.path('M430,251 L254,251', cls='sa', arrow='aa')
    f.text(342, 236, '接続の確立（3ウェイハンドシェイク）', cls='t-xs acc b')

    # データ転送
    f.box(110, 308, 140, 42, ['read / write'], cls='accT s', tcls='t-s m')
    f.box(430, 308, 140, 42, ['write / read'], cls='accT s', tcls='t-s m')
    f.arrow(254, 320, 426, 320, cls='sa')
    f.arrow(426, 340, 254, 340, cls='sa')
    f.text(342, 298, 'ファイルと同じ操作でやりとりする', cls='t-xs lbl')
    f.line(180, 272, 180, 304, cls='sm', arrow='am')
    f.line(500, 272, 500, 304, cls='sm', arrow='am')

    f.box(110, 380, 140, 42, ['close'], cls='tint s', tcls='t-s m b')
    f.box(430, 380, 140, 42, ['close'], cls='tint s', tcls='t-s m b')
    f.line(180, 350, 180, 376, cls='sm', arrow='am')
    f.line(500, 350, 500, 376, cls='sm', arrow='am')

    # accept の注記。2列の間の空きに置き、どの矢印とも交差させない
    f.rect(268, 62, 144, 118, cls='none sm dash', rx=6)
    f.text(340, 82, 'accept は', cls='t-xs b')
    f.lines(340, 104, ['新しいソケットを返す。', '元のソケットは受付', '専用として残るので、',
                       '次の接続を待ち続け', 'られる'], cls='t-xs', lh=15)
    f.path('M300,184 L268,224', cls='sm', arrow='am')

    f.text(342, 444, '接続してしまえば、あとはファイルと同じ read / write で済む',
           cls='t-s b')
    f.text(342, 464, '相手がファイルかパイプか地球の裏側かを、プログラムは意識しなくてよい',
           cls='t-xs lbl')
    return f


FIGURES['10-06'] = f1006
