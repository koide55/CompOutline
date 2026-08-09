// 第1回「計算とは何か」のスライド。lectures/01-what-is-computation.md から起こす。
const PptxGenJS = require('pptxgenjs');
const path = require('path');
const fs = require('fs');

const PNG = path.join(__dirname, 'png');
const img = (n) => ({ path: path.join(PNG, n) });

// 図の SVG と同じ配色にそろえる。スライドと図が別物に見えないようにするため
const INK = '16191D';
const PAPER = 'FFFFFF';
const TINT = 'EEF1F5';
const ACC = '0B5CAD';
const MUT = '5F6672';
const LIGHTINK = 'E8EBEF';

const JA = 'Yu Gothic';
const MONO = 'Courier New';

const pres = new PptxGenJS();
pres.layout = 'LAYOUT_WIDE'; // 13.3 x 7.5 inch
pres.author = '九州大学 コンピュータシステム通論';
pres.title = '第1回 計算とは何か';

// --- 共通部品 -------------------------------------------------------

// テープのマス目。チューリングマシンの回なので、これを通しの意匠にする
function tape(s, { y = 6.75, cells = 26, hi = 9, color = ACC } = {}) {
  const w = 0.33, h = 0.2, x0 = 0.6;
  for (let i = 0; i < cells; i++) {
    s.addShape(pres.ShapeType.rect, {
      x: x0 + i * w, y, w: w - 0.04, h,
      fill: { color: i === hi ? color : 'FFFFFF', transparency: i === hi ? 0 : 88 },
      line: { color, width: 0.6, transparency: 55 },
    });
  }
}

function darkSlide() {
  const s = pres.addSlide();
  s.background = { color: INK };
  return s;
}

function contentSlide(title, kicker) {
  const s = pres.addSlide();
  s.background = { color: PAPER };
  if (kicker) {
    s.addText(kicker, {
      x: 0.62, y: 0.34, w: 3, h: 0.28,
      fontFace: JA, fontSize: 12, color: ACC, bold: true, margin: 0,
    });
  }
  s.addText(title, {
    x: 0.6, y: kicker ? 0.66 : 0.5, w: 12.1, h: 0.8,
    fontFace: JA, fontSize: 30, bold: true, color: INK, margin: 0, valign: 'top',
  });
  return s;
}

function bullets(s, items, o = {}) {
  const rows = items.map((t, i) => {
    const [text, lvl] = Array.isArray(t) ? t : [t, 0];
    return {
      text,
      options: {
        bullet: true, indentLevel: lvl,
        breakLine: i !== items.length - 1,
        fontSize: lvl ? (o.sub || 14) : (o.size || 16),
        color: lvl ? MUT : INK,
        paraSpaceAfter: lvl ? 4 : 8,
      },
    };
  });
  s.addText(rows, {
    x: o.x ?? 0.75, y: o.y ?? 1.75, w: o.w ?? 6.1, h: o.h ?? 4.6,
    fontFace: JA, valign: 'top', margin: 0,
  });
}

function card(s, x, y, w, h, head, body, { accent = false } = {}) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.06,
    fill: { color: accent ? 'D9E6F4' : TINT },
    line: { color: accent ? ACC : 'DDE4EC', width: 1 },
  });
  s.addText(head, {
    x: x + 0.22, y: y + 0.16, w: w - 0.44, h: 0.32,
    fontFace: JA, fontSize: 14, bold: true, color: accent ? ACC : INK, margin: 0,
  });
  if (body) {
    s.addText(body, {
      x: x + 0.22, y: y + 0.52, w: w - 0.44, h: h - 0.72,
      fontFace: JA, fontSize: 12, color: MUT, margin: 0, valign: 'top',
    });
  }
}

function code(s, lines, { x = 0.75, y = 2.0, w = 6.0, h = 2.2, size = 12.5 } = {}) {
  s.addShape(pres.ShapeType.roundRect, {
    x, y, w, h, rectRadius: 0.04,
    fill: { color: 'F5F7FA' }, line: { color: 'DDE4EC', width: 1 },
  });
  s.addText(lines.join('\n'), {
    x: x + 0.24, y: y + 0.18, w: w - 0.48, h: h - 0.36,
    fontFace: MONO, fontSize: size, color: INK, margin: 0, valign: 'top', lineSpacing: size * 1.5,
  });
}

function note(s, text, y = 6.55) {
  s.addText(text, {
    x: 0.75, y, w: 11.8, h: 0.4,
    fontFace: JA, fontSize: 13, color: ACC, bold: true, margin: 0,
  });
}

function pageNum(s, n) {
  s.addText(String(n), {
    x: 12.3, y: 6.95, w: 0.6, h: 0.3,
    fontFace: JA, fontSize: 10, color: MUT, align: 'right', margin: 0,
  });
}

// =====================================================================
// 1. タイトル
{
  const s = darkSlide();
  s.addText('コンピュータシステム通論', {
    x: 0.9, y: 2.0, w: 11, h: 0.5,
    fontFace: JA, fontSize: 17, color: '9AA3B0', charSpacing: 2, margin: 0,
  });
  s.addText('第1回　計算とは何か', {
    x: 0.9, y: 2.6, w: 11, h: 1.2,
    fontFace: JA, fontSize: 48, bold: true, color: PAPER, margin: 0,
  });
  s.addText('「計算できる」とはどういうことか。計算できないことはあるか。', {
    x: 0.9, y: 4.0, w: 11, h: 0.5,
    fontFace: JA, fontSize: 18, color: '6AB0F3', margin: 0,
  });
  tape(s, { y: 5.4, hi: 9, color: '6AB0F3' });
  s.addText('九州大学', {
    x: 0.9, y: 6.4, w: 6, h: 0.3, fontFace: JA, fontSize: 12, color: MUT, margin: 0,
  });
}

// 2. 今回の問い
{
  const s = darkSlide();
  s.addText('今回の問い', {
    x: 0.9, y: 1.5, w: 11, h: 0.4,
    fontFace: JA, fontSize: 14, color: '6AB0F3', bold: true, margin: 0,
  });
  s.addText('「計算できる」とは\nどういうことか。', {
    x: 0.9, y: 2.1, w: 11, h: 1.8,
    fontFace: JA, fontSize: 40, bold: true, color: PAPER, margin: 0, lineSpacing: 52,
  });
  s.addText('そして、計算できないことはあるか。', {
    x: 0.9, y: 4.2, w: 11, h: 0.6,
    fontFace: JA, fontSize: 24, color: LIGHTINK, margin: 0,
  });
  s.addText('この90分で、この1つの問いに答えを出す。', {
    x: 0.9, y: 5.3, w: 11, h: 0.4,
    fontFace: JA, fontSize: 14, color: MUT, margin: 0,
  });
  tape(s, { y: 6.4, hi: 4, color: '6AB0F3' });
}

// 3. この講義の見取り図
{
  const s = contentSlide('この講義の見取り図', '1.0　ガイダンス');
  s.addText('この講義は、機器のカタログを読むための科目ではない。', {
    x: 0.75, y: 1.66, w: 11.8, h: 0.35, fontFace: JA, fontSize: 15, color: INK, margin: 0,
  });
  s.addText('CPU の型番も、通信規格の数字も、数年で入れ替わる。追いかけても意味が薄い。', {
    x: 0.75, y: 2.02, w: 11.8, h: 0.35, fontFace: JA, fontSize: 13, color: MUT, margin: 0,
  });

  const steps = [
    ['第1回', '計算の定義'], ['第2回', '情報と計算量'], ['第3–4回', '回路と言語'],
    ['第5–6回', '記憶の階層'], ['第7–8回', '資源の管理'], ['第9–10回', 'つなぐ'],
    ['第11–12回', '溜めて守る'], ['第13回', '学習する機械'],
  ];
  const w = 1.42, gap = 0.055;
  steps.forEach(([n, t], i) => {
    const x = 0.75 + i * (w + gap);
    const first = i === 0;
    s.addShape(pres.ShapeType.roundRect, {
      x, y: 2.75, w, h: 1.5, rectRadius: 0.06,
      fill: { color: first ? 'D9E6F4' : TINT },
      line: { color: first ? ACC : 'DDE4EC', width: first ? 1.5 : 1 },
    });
    s.addText(n, {
      x, y: 2.92, w, h: 0.3, fontFace: JA, fontSize: 11,
      color: first ? ACC : MUT, bold: true, align: 'center', margin: 0,
    });
    s.addText(t, {
      x: x + 0.08, y: 3.3, w: w - 0.16, h: 0.7, fontFace: JA, fontSize: 13,
      color: INK, bold: first, align: 'center', valign: 'top', margin: 0,
    });
  });

  s.addText('計算機は1940年代から性能で1兆倍近く変わった。しかし「何をする機械か」という定義は、'
    + '1936年にアラン・チューリングが書いた論文からほとんど変わっていない。', {
    x: 0.75, y: 4.65, w: 11.8, h: 0.6, fontFace: JA, fontSize: 15, color: INK, margin: 0,
  });
  note(s, '生成AIも、その定義の内側にある。だから第1回は1936年から始める。', 5.4);
  pageNum(s, 3);
}

// 4. 到達目標
{
  const s = contentSlide('到達目標', '第1回');
  const goals = [
    ['アルゴリズム', 'が満たすべき条件を挙げられる'],
    ['チューリングマシン', 'の動作を追跡し、簡単な機械を設計できる'],
    ['チャーチ＝チューリングのテーゼ', 'が何を主張しているか説明できる'],
    ['計算できない問題が存在する', 'ことの意味を説明できる'],
  ];
  goals.forEach(([h, b], i) => {
    const y = 1.9 + i * 1.15;
    s.addShape(pres.ShapeType.ellipse, {
      x: 0.85, y: y + 0.12, w: 0.52, h: 0.52,
      fill: { color: 'D9E6F4' }, line: { color: ACC, width: 1.2 },
    });
    s.addText(String(i + 1), {
      x: 0.85, y: y + 0.12, w: 0.52, h: 0.52,
      fontFace: JA, fontSize: 15, bold: true, color: ACC, align: 'center', valign: 'middle', margin: 0,
    });
    s.addText([
      { text: h, options: { bold: true, color: INK, fontSize: 17 } },
      { text: '　' + b, options: { color: MUT, fontSize: 15 } },
    ], { x: 1.6, y: y + 0.16, w: 10.8, h: 0.5, fontFace: JA, valign: 'middle', margin: 0 });
  });
  pageNum(s, 4);
}

// 5. セクション 1.1
{
  const s = darkSlide();
  s.addText('1.1', {
    x: 0.9, y: 2.4, w: 3, h: 0.9,
    fontFace: JA, fontSize: 56, bold: true, color: '2E3A4A', margin: 0,
  });
  s.addText('アルゴリズム', {
    x: 0.9, y: 3.35, w: 11, h: 0.9,
    fontFace: JA, fontSize: 40, bold: true, color: PAPER, margin: 0,
  });
  s.addText('手順を、曖昧さなく書き下すとはどういうことか', {
    x: 0.9, y: 4.35, w: 11, h: 0.5,
    fontFace: JA, fontSize: 17, color: '9AA3B0', margin: 0,
  });
  tape(s, { y: 6.4, hi: 1, color: '6AB0F3' });
}

// 6. 定義
{
  const s = contentSlide('アルゴリズムの定義', '1.1　アルゴリズム');
  const items = [
    ['有限性', '有限の手数で必ず終わる'],
    ['明確性', '各ステップが曖昧さなく定まっている'],
    ['入力', '0個以上の入力を受け取る'],
    ['出力', '1個以上の出力を返す'],
    ['実行可能性', '各ステップが機械的に実行できる'],
  ];
  items.forEach(([h, b], i) => {
    const x = 0.75 + (i % 3) * 4.05;
    const y = 1.85 + Math.floor(i / 3) * 1.5;
    card(s, x, y, 3.8, 1.28, `${i + 1}. ${h}`, b, { accent: i < 2 });
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 4.8, y: 4.85, w: 7.75, h: 1.4, rectRadius: 0.06,
    fill: { color: 'FFFFFF' }, line: { color: ACC, width: 1.5, dashType: 'dash' },
  });
  s.addText('「明確さ」の要求は、思っているより厳しい', {
    x: 5.05, y: 5.0, w: 7.3, h: 0.35, fontFace: JA, fontSize: 15, bold: true, color: ACC, margin: 0,
  });
  s.addText('料理のレシピにある「塩少々」は、アルゴリズムの条件を満たさない。\n'
    + '実行する人の判断が入る余地があってはならない。', {
    x: 5.05, y: 5.42, w: 7.3, h: 0.7, fontFace: JA, fontSize: 13, color: MUT, margin: 0, lineSpacing: 18,
  });
  pageNum(s, 6);
}

// 7. 互除法
{
  const s = contentSlide('例：ユークリッドの互除法', '1.1　アルゴリズム');
  s.addText('2つの自然数 a, b の最大公約数を求める。紀元前300年ごろの記述が残っている。', {
    x: 0.75, y: 1.66, w: 11.8, h: 0.35, fontFace: JA, fontSize: 14, color: MUT, margin: 0,
  });
  code(s, [
    '入力: 自然数 a, b   (a >= b > 0)',
    '',
    '1. a を b で割った余りを r とする',
    '2. r = 0 なら b を出力して終了',
    '3. a <- b,  b <- r  として 1 に戻る',
  ], { x: 0.75, y: 2.1, w: 5.6, h: 2.3 });

  s.addTable([
    [{ text: '回', options: { bold: true } }, { text: 'a', options: { bold: true } },
     { text: 'b', options: { bold: true } }, { text: 'r', options: { bold: true } }],
    ['1', '1071', '462', '147'],
    ['2', '462', '147', '21'],
    ['3', '147', '21', '0'],
  ], {
    x: 6.75, y: 2.1, w: 5.8, colW: [0.9, 1.7, 1.6, 1.6],
    fontFace: MONO, fontSize: 14, align: 'center', valign: 'middle',
    border: { type: 'solid', color: 'DDE4EC', pt: 1 },
    fill: { color: 'FFFFFF' }, rowH: 0.42,
  });
  s.addText('答えは 21。3回で終わった。', {
    x: 6.75, y: 4.05, w: 5.8, h: 0.35, fontFace: JA, fontSize: 15, bold: true, color: INK, margin: 0,
  });
  s.addText('素因数分解して共通因数を探す方法だと、はるかに手間がかかる。\n'
    + 'そして大きな数では現実的な時間で終わらない ——\nこの事実は第12回の公開鍵暗号で効いてくる。', {
    x: 6.75, y: 4.45, w: 5.8, h: 1.1, fontFace: JA, fontSize: 13, color: MUT, margin: 0, lineSpacing: 19,
  });
  note(s, 'この手順のどこにも「計算機」は出てこない。アルゴリズムは紙と鉛筆で実行できる。', 5.75);
  pageNum(s, 7);
}

// 8. 図 1-1
{
  const s = contentSlide('互除法を図で見る', '1.1　アルゴリズム');
  s.addImage({ ...img('fig-01-01.png'), x: 2.35, y: 1.6, w: 8.6, h: 3.81 });
  s.addText('長方形から正方形を切り取っていくと、最後に残る正方形の一辺が最大公約数になる。', {
    x: 0.75, y: 5.65, w: 11.8, h: 0.4, fontFace: JA, fontSize: 15, color: INK, align: 'center', margin: 0,
  });
  s.addText('余りが毎回真に小さくなり、0以上の整数は無限に減り続けられないので、必ず終わる。', {
    x: 0.75, y: 6.1, w: 11.8, h: 0.4, fontFace: JA, fontSize: 13, color: MUT, align: 'center', margin: 0,
  });
  pageNum(s, 8);
}

// 9. 有限性は自明ではない
{
  const s = contentSlide('「必ず終わる」は自明ではない', '1.1　アルゴリズム');
  code(s, [
    '入力: 自然数 n',
    '',
    '1. n = 1 なら終了',
    '2. n が偶数なら n <- n/2',
    '   奇数なら       n <- 3n+1',
    '3. 1 に戻る',
  ], { x: 0.75, y: 1.95, w: 5.2, h: 2.5 });
  s.addText('コラッツの手順', {
    x: 0.75, y: 1.6, w: 5.2, h: 0.3, fontFace: JA, fontSize: 14, bold: true, color: INK, margin: 0,
  });

  s.addText('n = 7 から始めると', {
    x: 6.4, y: 1.6, w: 6.1, h: 0.3, fontFace: JA, fontSize: 14, bold: true, color: INK, margin: 0,
  });
  s.addText('7 → 22 → 11 → 34 → 17 → 52 → 26 → 13 → 40\n→ 20 → 10 → 5 → 16 → 8 → 4 → 2 → 1', {
    x: 6.4, y: 1.98, w: 6.1, h: 0.9, fontFace: MONO, fontSize: 13, color: INK, margin: 0, lineSpacing: 22,
  });
  s.addText('16ステップで終わった。', {
    x: 6.4, y: 2.95, w: 6.1, h: 0.3, fontFace: JA, fontSize: 13, color: MUT, margin: 0,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 6.4, y: 3.45, w: 6.15, h: 1.0, rectRadius: 0.06,
    fill: { color: 'D9E6F4' }, line: { color: ACC, width: 1.5 },
  });
  s.addText('すべての n について終わるかは、2026年現在も証明されていない', {
    x: 6.62, y: 3.6, w: 5.7, h: 0.35, fontFace: JA, fontSize: 14, bold: true, color: ACC, margin: 0,
  });
  s.addText('1937年に提起されて以来、未解決。', {
    x: 6.62, y: 3.98, w: 5.7, h: 0.3, fontFace: JA, fontSize: 12, color: MUT, margin: 0,
  });
  note(s, '「終わるかどうか分からない手順」が、こうも簡単に書けてしまう。この感覚が 1.3 で効いてくる。', 5.0);
  pageNum(s, 9);
}

// 10. セクション 1.2
{
  const s = darkSlide();
  s.addText('1.2', {
    x: 0.9, y: 2.4, w: 3, h: 0.9,
    fontFace: JA, fontSize: 56, bold: true, color: '2E3A4A', margin: 0,
  });
  s.addText('チューリングマシン', {
    x: 0.9, y: 3.35, w: 11, h: 0.9,
    fontFace: JA, fontSize: 40, bold: true, color: PAPER, margin: 0,
  });
  s.addText('紙と鉛筆で計算する人を、極限まで単純化する', {
    x: 0.9, y: 4.35, w: 11, h: 0.5,
    fontFace: JA, fontSize: 17, color: '9AA3B0', margin: 0,
  });
  tape(s, { y: 6.4, hi: 12, color: '6AB0F3' });
}

// 11. なぜこんなものを考えるのか
{
  const s = contentSlide('なぜこんなものを考えるのか', '1.2　チューリングマシン');
  s.addText('「計算できる」を「アルゴリズムがある」で定義すると、'
    + '今度は「機械的に実行できる」という曖昧な言葉が残る。堂々巡りになる。', {
    x: 0.75, y: 1.68, w: 11.8, h: 0.6, fontFace: JA, fontSize: 15, color: INK, margin: 0, lineSpacing: 22,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.75, y: 2.45, w: 11.8, h: 0.95, rectRadius: 0.06,
    fill: { color: TINT }, line: { color: 'DDE4EC', width: 1 },
  });
  s.addText('人間が紙と鉛筆で計算しているとき、その人は実際には何をしているのか。\n'
    + 'それを極限まで単純化した機械を作れば、その機械ができることが「計算」である。', {
    x: 1.05, y: 2.6, w: 11.2, h: 0.7, fontFace: JA, fontSize: 15, italic: true, color: INK,
    margin: 0, lineSpacing: 22,
  });
  s.addText('アラン・チューリング（1912–1954）が1936年にとった方針', {
    x: 0.75, y: 3.48, w: 11.8, h: 0.3, fontFace: JA, fontSize: 12, color: MUT, margin: 0,
  });

  const obs = [
    ['読む', '紙のどこか1箇所を見て、書いてある記号を読む'],
    ['決める', '頭の中の「今どういうつもりか」と、読んだ記号から次にすることを決める'],
    ['書く', 'そこに記号を書く。消して書き直すこともある'],
    ['動く', '視線を隣に移す'],
  ];
  obs.forEach(([h, b], i) => {
    const x = 0.75 + i * 3.03;
    card(s, x, 4.05, 2.85, 1.75, h, b, { accent: false });
  });
  note(s, 'これを機械にしたものがチューリングマシン。部品はテープ・ヘッド・有限個の状態しかない。', 6.1);
  pageNum(s, 11);
}

// 12. 図 1-2
{
  const s = contentSlide('チューリングマシンの構成', '1.2　チューリングマシン');
  s.addImage({ ...img('fig-01-02.png'), x: 1.85, y: 1.55, w: 9.6, h: 4.53 });
  note(s, '遷移規則は (現在の状態, 読んだ記号) → (書く記号, 移動方向, 次の状態) の表で完全に決まる。', 6.3);
  pageNum(s, 12);
}

// 13. 1を足す機械
{
  const s = contentSlide('例：1を足す機械', '1.2　チューリングマシン');
  s.addText('2進数が書かれたテープを受け取り、その数に1を足す。筆算と同じで、右端から見ていく。', {
    x: 0.75, y: 1.58, w: 11.8, h: 0.35, fontFace: JA, fontSize: 14, color: MUT, margin: 0,
  });
  s.addTable([
    [{ text: '状態' }, { text: '読んだ' }, { text: '書く' }, { text: '移動' }, { text: '次の状態' }]
      .map((c) => ({ ...c, options: { bold: true, fill: { color: TINT } } })),
    ['carry', '1', '0', '左', 'carry'],
    ['carry', '0', '1', '—', 'halt'],
    ['carry', '␣', '1', '—', 'halt'],
  ], {
    x: 0.75, y: 2.15, w: 5.6, colW: [1.3, 1.0, 0.9, 0.9, 1.5],
    fontFace: MONO, fontSize: 13, align: 'center', valign: 'middle',
    border: { type: 'solid', color: 'DDE4EC', pt: 1 }, fill: { color: 'FFFFFF' }, rowH: 0.42,
  });
  s.addText('状態は2つ、規則は3行しかない', {
    x: 0.75, y: 4.05, w: 5.6, h: 0.3, fontFace: JA, fontSize: 13, bold: true, color: ACC, margin: 0,
  });

  s.addText('1011 で追いかける（下線がヘッド位置）', {
    x: 6.75, y: 2.02, w: 5.8, h: 0.3, fontFace: JA, fontSize: 13, bold: true, color: INK, margin: 0,
  });
  s.addTable([
    [{ text: 'ステップ' }, { text: 'テープ' }, { text: '状態' }]
      .map((c) => ({ ...c, options: { bold: true, fill: { color: TINT } } })),
    ['0', '1 0 1 [1]', 'carry'],
    ['1', '1 0 [1] 0', 'carry'],
    ['2', '1 [0] 0 0', 'carry'],
    ['3', '1 [1] 0 0', 'halt'],
  ], {
    x: 6.75, y: 2.4, w: 5.8, colW: [1.5, 2.6, 1.7],
    fontFace: MONO, fontSize: 13, align: 'center', valign: 'middle',
    border: { type: 'solid', color: 'DDE4EC', pt: 1 }, fill: { color: 'FFFFFF' }, rowH: 0.4,
  });
  s.addText('1100 = 12。正しい。', {
    x: 6.75, y: 4.62, w: 5.8, h: 0.3, fontFace: JA, fontSize: 14, bold: true, color: ACC, margin: 0,
  });
  note(s, 'この機械は何桁の2進数でも動く。111 なら空白を読んで 1000 になる。', 5.1);
  pageNum(s, 13);
}

// 14. 図 1-3
{
  const s = contentSlide('状態遷移図で見る', '1.2　チューリングマシン');
  s.addImage({ ...img('fig-01-03.png'), x: 3.15, y: 1.7, w: 7.0, h: 3.13 });
  s.addText('表と同じ内容を図にしただけ。制御部の正体は「有限個の状態と、それを結ぶ矢印」である。', {
    x: 0.75, y: 5.25, w: 11.8, h: 0.4, fontFace: JA, fontSize: 15, color: INK, align: 'center', margin: 0,
  });
  pageNum(s, 14);
}

// 15. 万能チューリングマシン
{
  const s = contentSlide('万能チューリングマシン', '1.2　チューリングマシン');
  s.addText('ここまでの機械は「1を足す」専用だった。ところがチューリングは、'
    + '他のチューリングマシンの遷移規則表そのものをテープに書いて渡すと、'
    + 'それを解釈して真似する機械が作れることを示した。', {
    x: 0.75, y: 1.68, w: 11.8, h: 0.75, fontFace: JA, fontSize: 15, color: INK, margin: 0, lineSpacing: 23,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.75, y: 2.6, w: 11.8, h: 0.7, rectRadius: 0.06,
    fill: { color: 'D9E6F4' }, line: { color: ACC, width: 1.5 },
  });
  s.addText('専用機を作り分けるのではなく、1台の機械に「何をするか」をデータとして与える', {
    x: 1.0, y: 2.75, w: 11.3, h: 0.4, fontFace: JA, fontSize: 17, bold: true, color: ACC, margin: 0,
  });

  const map = [
    ['テープに書かれた規則表', 'プログラム'],
    ['それを解釈して実行する万能機', 'CPU'],
    ['同じテープに置かれる入力', 'データ'],
  ];
  map.forEach(([a, b], i) => {
    const y = 3.65 + i * 0.72;
    s.addText(a, {
      x: 1.4, y, w: 5.0, h: 0.5, fontFace: JA, fontSize: 15, color: INK,
      align: 'right', valign: 'middle', margin: 0,
    });
    s.addShape(pres.ShapeType.rightArrow, {
      x: 6.55, y: y + 0.14, w: 0.7, h: 0.22, fill: { color: ACC },
    });
    s.addText(b, {
      x: 7.45, y, w: 4.0, h: 0.5, fontFace: JA, fontSize: 17, bold: true, color: ACC,
      valign: 'middle', margin: 0,
    });
  });
  note(s, 'プログラムとデータが同じ場所に同じ形式で置かれる ——'
    + ' 現在の計算機の基本設計（第3回のノイマン型）の原型が、ここにある。', 6.0);
  s.addText('1936年、まだ電子計算機が1台も存在しない時点での話である。', {
    x: 0.75, y: 6.45, w: 11.8, h: 0.35, fontFace: JA, fontSize: 13, color: MUT, margin: 0,
  });
  pageNum(s, 15);
}

// 16. セクション 1.3
{
  const s = darkSlide();
  s.addText('1.3', {
    x: 0.9, y: 2.4, w: 3, h: 0.9,
    fontFace: JA, fontSize: 56, bold: true, color: '2E3A4A', margin: 0,
  });
  s.addText('計算の限界', {
    x: 0.9, y: 3.35, w: 11, h: 0.9,
    fontFace: JA, fontSize: 40, bold: true, color: PAPER, margin: 0,
  });
  s.addText('計算できないことは、ある。しかも自然な問題で', {
    x: 0.9, y: 4.35, w: 11, h: 0.5,
    fontFace: JA, fontSize: 17, color: '9AA3B0', margin: 0,
  });
  tape(s, { y: 6.4, hi: 20, color: '6AB0F3' });
}

// 17. チャーチ＝チューリングのテーゼ
{
  const s = contentSlide('チャーチ＝チューリングのテーゼ', '1.3　計算の限界');
  s.addText('発想はばらばらなのに、計算できる関数の集合はぴったり一致する。', {
    x: 0.75, y: 1.66, w: 11.8, h: 0.35, fontFace: JA, fontSize: 14, color: MUT, margin: 0,
  });
  s.addTable([
    [{ text: 'モデル' }, { text: '提案' }, { text: '発想' }]
      .map((c) => ({ ...c, options: { bold: true, fill: { color: TINT } } })),
    ['チューリングマシン', 'Turing, 1936', '紙と鉛筆の計算を機械化する'],
    ['λ計算', 'Church, 1936', '関数の適用だけで計算を表す'],
    ['帰納的関数', 'Gödel, Kleene, 1930s', '基本関数と再帰から組み立てる'],
    ['レジスタマシン', 'Shepherdson–Sturgis, 1963', '無限個のレジスタを操作する'],
    ['セルオートマトン', 'von Neumann, 1940s', '単純な規則で更新される格子'],
  ], {
    x: 0.75, y: 2.1, w: 11.8, colW: [3.1, 3.4, 5.3],
    fontFace: JA, fontSize: 13, valign: 'middle',
    border: { type: 'solid', color: 'DDE4EC', pt: 1 }, fill: { color: 'FFFFFF' }, rowH: 0.4,
  });
  s.addShape(pres.ShapeType.roundRect, {
    x: 0.75, y: 4.85, w: 11.8, h: 0.8, rectRadius: 0.06,
    fill: { color: 'D9E6F4' }, line: { color: ACC, width: 1.5 },
  });
  s.addText('「直観的に計算可能」な関数は、チューリングマシンで計算可能な関数と一致する', {
    x: 1.0, y: 5.02, w: 11.3, h: 0.45, fontFace: JA, fontSize: 16, bold: true, color: ACC, margin: 0,
  });
  s.addText('使う言語やハードウェアを変えても、計算できる問題の範囲は広がらない。'
    + 'GPU を1万個並べても同じ。量子計算機も範囲は同じで、一部を速く解けるだけである。', {
    x: 0.75, y: 5.85, w: 11.8, h: 0.6, fontFace: JA, fontSize: 13, color: MUT, margin: 0, lineSpacing: 20,
  });
  pageNum(s, 17);
}

// 18. 停止問題
{
  const s = contentSlide('停止問題', '1.3　計算の限界');
  s.addText('プログラム P と入力 x が与えられたとき、「P に x を入力して実行すると、'
    + 'いつか停止するか」を判定せよ。', {
    x: 0.75, y: 1.66, w: 11.8, h: 0.35, fontFace: JA, fontSize: 15, color: INK, margin: 0,
  });
  s.addText('これを判定する halts(P, x) は存在しない。証明は短い。', {
    x: 0.75, y: 2.05, w: 11.8, h: 0.3, fontFace: JA, fontSize: 14, bold: true, color: ACC, margin: 0,
  });
  code(s, [
    'trouble(P):',
    '    if halts(P, P):        # P に P 自身を入力すると停止するか',
    '        while True: pass   # 停止するなら、わざと無限ループする',
    '    else:',
    '        return             # 停止しないなら、さっさと停止する',
  ], { x: 0.75, y: 2.5, w: 11.8, h: 1.85, size: 13 });

  s.addText('trouble(trouble) を考える', {
    x: 0.75, y: 4.55, w: 11.8, h: 0.3, fontFace: JA, fontSize: 14, bold: true, color: INK, margin: 0,
  });
  const cases = [
    ['停止する とすると', 'halts は真を返す → trouble は無限ループに入る → 停止しない。矛盾'],
    ['停止しない とすると', 'halts は偽を返す → trouble はすぐ return する → 停止する。矛盾'],
  ];
  cases.forEach(([h, b], i) => {
    card(s, 0.75 + i * 6.05, 4.95, 5.75, 1.05, h, b, { accent: true });
  });
  note(s, 'どちらでも矛盾する。よって仮定が誤りで、halts は存在しない。', 6.25);
  pageNum(s, 18);
}

// 19. 図 1-4
{
  const s = contentSlide('対角線論法', '1.3　計算の限界');
  s.addImage({ ...img('fig-01-04.png'), x: 4.05, y: 1.5, w: 5.2, h: 3.34 });
  s.addText('対角線をすべて反転させたものが trouble の振る舞い。'
    + 'どの行とも1マス以上食い違うため、表のどこにも存在しえない。', {
    x: 0.75, y: 5.1, w: 11.8, h: 0.4, fontFace: JA, fontSize: 15, color: INK, align: 'center', margin: 0,
  });
  s.addText('1.1 で見たコラッツの手順が、なぜ90年も未解決なのかが、これで少し見える。\n'
    + '停止するかどうかを機械的に判定する一般的な方法が、そもそも存在しない。', {
    x: 0.75, y: 5.6, w: 11.8, h: 0.7, fontFace: JA, fontSize: 13, color: MUT, align: 'center',
    margin: 0, lineSpacing: 20,
  });
  pageNum(s, 19);
}

// 20. 決定不能は他にもある
{
  const s = contentSlide('決定不能な問題は、他にもある', '1.3　計算の限界');
  bullets(s, [
    '2つのプログラムが同じ関数を計算するか（プログラムの同値性）',
    'あるプログラムが特定のバグ（ゼロ除算、メモリ破壊）を起こしうるか',
    'あるプログラムがウイルスとして振る舞うか',
  ], { x: 0.9, y: 1.75, w: 11.5, h: 1.4, size: 15 });
  s.addText('ライスの定理：プログラムの入出力の振る舞いに関する自明でない性質は、すべて決定不能である', {
    x: 0.75, y: 3.15, w: 11.8, h: 0.35, fontFace: JA, fontSize: 15, bold: true, color: ACC, margin: 0,
  });
  s.addText('だからコンパイラの警告は見逃すし、ウイルス対策ソフトは完璧にならないし、'
    + 'テストはバグの不在を証明できない。技術が未熟だからではなく、原理的にそうである。', {
    x: 0.75, y: 3.55, w: 11.8, h: 0.6, fontFace: JA, fontSize: 14, color: INK, margin: 0, lineSpacing: 21,
  });
  s.addText('現場ではこの限界を、こう迂回する', {
    x: 0.75, y: 4.35, w: 11.8, h: 0.3, fontFace: JA, fontSize: 13, bold: true, color: MUT, margin: 0,
  });
  const ways = [
    ['近似する', '「危ないかもしれない」を過剰に報告する（静的解析の偽陽性）'],
    ['対象を狭める', '決定可能な範囲に制限する（型システム、正規表現）'],
    ['人間を入れる', '判断を人に委ねる'],
  ];
  ways.forEach(([h, b], i) => {
    card(s, 0.75 + i * 4.05, 4.75, 3.8, 1.35, h, b, { accent: false });
  });
  pageNum(s, 20);
}

// 21. 演習
{
  const s = contentSlide('演習', '第1回');
  const q = [
    ['1-1', '互除法を a=252, b=105 で実行し、各ステップの (a, b, r) を書け。'],
    ['1-2', 'テープ上の文字列に含まれる 1 の個数が偶数なら Y、奇数なら N を書いて停止する'
      + 'チューリングマシンの遷移規則表を作れ。（ヒント：状態は2つで足りる）'],
    ['1-3', '次の主張は正しいか。理由とともに答えよ。'
      + '「量子コンピュータが実用化されれば、停止問題も解けるようになる。」'],
    ['1-4', '普段使っているソフトウェアで「決定不能性を回避するために安全側に倒している」と'
      + '思われる挙動を1つ挙げ、なぜそう考えるか説明せよ。'],
  ];
  q.forEach(([n, t], i) => {
    const y = 1.85 + i * 1.18;
    s.addShape(pres.ShapeType.roundRect, {
      x: 0.75, y, w: 0.95, h: 0.45, rectRadius: 0.08,
      fill: { color: 'D9E6F4' }, line: { color: ACC, width: 1 },
    });
    s.addText(n, {
      x: 0.75, y, w: 0.95, h: 0.45, fontFace: MONO, fontSize: 13, bold: true,
      color: ACC, align: 'center', valign: 'middle', margin: 0,
    });
    s.addText(t, {
      x: 1.95, y: y - 0.02, w: 10.6, h: 1.0, fontFace: JA, fontSize: 14,
      color: INK, valign: 'top', margin: 0, lineSpacing: 21,
    });
  });
  pageNum(s, 21);
}

// 22. まとめ
{
  const s = darkSlide();
  s.addText('まとめ', {
    x: 0.9, y: 0.75, w: 11, h: 0.6,
    fontFace: JA, fontSize: 30, bold: true, color: PAPER, margin: 0,
  });
  const pts = [
    ['アルゴリズム', '有限性・明確性・実行可能性を満たす手順。「終わること」を確かめるのは、しばしば難しい'],
    ['チューリングマシン', '紙と鉛筆の計算を極限まで単純化した機械。部品はテープ・ヘッド・有限個の状態しかない'],
    ['万能チューリングマシン', '他の機械の規則表をデータとして受け取り実行する。プログラム内蔵方式の原型'],
    ['チャーチ＝チューリングのテーゼ', '計算モデルを変えても、計算できる範囲は広がらない'],
    ['停止問題', '計算できない。プログラムの振る舞いに関する自明でない性質は、すべて計算できない'],
  ];
  pts.forEach(([h, b], i) => {
    const y = 1.6 + i * 0.95;
    s.addText(h, {
      x: 0.9, y, w: 3.5, h: 0.35, fontFace: JA, fontSize: 15, bold: true, color: '6AB0F3', margin: 0,
    });
    s.addText(b, {
      x: 4.6, y: y - 0.04, w: 7.9, h: 0.75, fontFace: JA, fontSize: 13.5, color: LIGHTINK,
      margin: 0, valign: 'top', lineSpacing: 20,
    });
  });
  s.addText('次回　計算できるとして、それは現実的な時間で終わるのか。'
    + 'そもそも情報を計算機で扱うには、どう表現すればよいのか。', {
    x: 0.9, y: 6.5, w: 11.6, h: 0.4, fontFace: JA, fontSize: 13, color: MUT, margin: 0,
  });
}

const out = path.join(__dirname, '第01回_計算とは何か.pptx');
pres.writeFile({ fileName: out }).then(() => {
  console.log('書き出した:', out, fs.statSync(out).size, 'bytes');
});
