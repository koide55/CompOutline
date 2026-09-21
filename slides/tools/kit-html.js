// HTML スライドの体裁。13回ぶんの見た目をここ1箇所で決める。
//
// 入力は decks/lecNN.js —— pptx を組む kit.js とまったく同じデータである。
// 各回は「何を並べるか」だけを書き、配置はここが引き受ける。
//
// pptx 版との違い:
//   - 座標の微調整（cardH, noteY, codeH …）は読み飛ばす。CSS が高さを決めるため
//   - 図は SVG を data URI で埋め込む。PNG への変換が要らない
//   - 出力は1ファイルで完結する。教室の計算機に持って行くのが楽
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, '..', '..');
const FIG = path.join(ROOT, 'figures');

// 図の SVG と同じ配色。スライドと図が別物に見えないようにするため
const C = {
  ink: '#16191D',
  paper: '#FFFFFF',
  tint: '#EEF1F5',
  tint2: '#DDE4EC',
  acc: '#0B5CAD',
  accT: '#D9E6F4',
  mut: '#5F6672',        // 明色の地の上でのみ使う
  dim: '#9AA3B0',        // 濃色の地の上で使う。mut は暗すぎて読めない
  lightInk: '#E8EBEF',
  accLight: '#6AB0F3',
  code: '#F5F7FA',
  ghost: '#2E3A4A',
};

// 書体。Windows は pptx と同じ Yu Gothic になり、macOS はヒラギノに落ちる。
// pptx では「ヒラギノは macOS 専用だから使わない」としたが、
// HTML は環境ごとに落とせるので、その制約が要らない。
const JA = '"Yu Gothic Medium", "Yu Gothic", YuGothic, "Hiragino Sans", ' +
           '"Noto Sans JP", system-ui, sans-serif';
const MONO = '"SFMono-Regular", Menlo, Consolas, "Courier New", monospace';

const STAGE_W = 1280, STAGE_H = 720;   // 16:9。pptx の 13.3×7.5 インチに対応する

const esc = (s) => String(s ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/"/g, '&quot;');
const br = (s) => esc(s).replace(/\n/g, '<br>');

// --- 意匠 -------------------------------------------------------------
// 濃色スライドの下端に並ぶマス目。回ごとに埋まり方を変えて見分けをつける。
// 第1回のチューリングマシンのテープに由来する。pptx 版と同じ式を使う。
function motif(no) {
  const cells = [];
  for (let i = 0; i < 26; i++) {
    const on = ((i * 7 + no * 5) % (no + 3)) === 0;
    cells.push(`<i class="${on ? 'on' : ''}"></i>`);
  }
  return `<div class="motif">${cells.join('')}</div>`;
}

// --- 図 ---------------------------------------------------------------
// SVG をそのまま貼ると、図が持つ <style>（.ink, .acc …）が
// ページ全体に漏れて他の図やスライドを壊す。img の data URI に包んで隔離する。
const missing = [];
function figure(name) {
  const p = path.join(FIG, `fig-${name}.svg`);
  if (!fs.existsSync(p)) {
    missing.push(name);
    return `<div class="fig-missing">図 ${esc(name)} が見つかりません</div>`;
  }
  const b64 = fs.readFileSync(p).toString('base64');
  return `<img class="fig" alt="図 ${esc(name)}" src="data:image/svg+xml;base64,${b64}">`;
}

// --- 部品 -------------------------------------------------------------
const lead = (sl) => (sl.lead ? `<p class="lead">${br(sl.lead)}</p>` : '');
const sub = (t) => (t ? `<p class="sub">${br(t)}</p>` : '');
const note = (t) => (t ? `<p class="note">${br(t)}</p>` : '');

function card(head, body, accent) {
  return `<div class="card${accent ? ' acc' : ''}">
      <div class="card-h">${br(head)}</div>
      ${body ? `<div class="card-b">${br(body)}</div>` : ''}
    </div>`;
}

function codeBox(lines, o = {}) {
  const cls = o.small ? ' small' : '';
  return `<pre class="code${cls}">${esc(lines.join('\n'))}</pre>`;
}

// colW はインチで手で詰めてある。比率に直せば、その配分がそのまま生きる。
function table(rows, o = {}) {
  const cols = o.colW
    ? `<colgroup>${o.colW.map((w) => {
        const pct = (w / o.colW.reduce((a, b) => a + b, 0)) * 100;
        return `<col style="width:${pct.toFixed(2)}%">`;
      }).join('')}</colgroup>`
    : '';
  const cls = ['tbl', o.mono ? 'mono' : '', o.align === 'center' ? 'center' : ''].join(' ');
  const head = `<tr>${rows[0].map((c) => `<th>${br(c)}</th>`).join('')}</tr>`;
  const body = rows.slice(1)
    .map((r) => `<tr>${r.map((c) => `<td>${br(c)}</td>`).join('')}</tr>`).join('');
  return `<table class="${cls}">${cols}<thead>${head}</thead><tbody>${body}</tbody></table>`;
}

// =====================================================================
class Deck {
  constructor(spec) {
    this.spec = spec;
    this.slides = [];
    this.page = 0;
  }

  // 濃色のスライド。番号は振らないが、通し番号は進める。
  // まとめだけマス目を出さない（pptx 版もそうしている。「次回」の行と場所が競合するため）
  dark(inner, extra = '', withMotif = true) {
    this.page += 1;
    this.slides.push(`<section class="slide dark ${extra}">${inner}`
      + `${withMotif ? motif(this.spec.no) : ''}</section>`);
  }

  // 明色の本文スライド
  content(title, kicker, inner) {
    this.page += 1;
    const head = `<header>
        ${kicker ? `<div class="kicker">${br(kicker)}</div>` : ''}
        <h2>${br(title)}</h2>
      </header>`;
    this.slides.push(`<section class="slide light">
        ${head}<div class="body">${inner}</div>
        <div class="pageno">${this.page}</div>
      </section>`);
  }

  // --- 定型のスライド ------------------------------------------------
  titleSlide() {
    const sp = this.spec;
    const t = `第${sp.no}回　${sp.title}`;
    const size = t.length > 15 ? 45 : (t.length > 12 ? 51 : 59);
    this.dark(`
      <div class="title-wrap">
        <div class="course">コンピュータシステム通論</div>
        <h1 style="font-size:${size}px">${br(t)}</h1>
        <p class="tq">${br(sp.question)}</p>
      </div>
      <div class="affil">九州大学</div>`, 'title');
  }

  questionSlide() {
    const sp = this.spec;
    this.dark(`
      <div class="q-wrap">
        <div class="q-label">今回の問い</div>
        <p class="q-big">${br(sp.bigQuestion || sp.question)}</p>
        ${sp.questionSub ? `<p class="q-sub">${br(sp.questionSub)}</p>` : ''}
        <p class="q-foot">この90分で、この問いに答えを出す。</p>
      </div>`);
  }

  goalsSlide() {
    const items = this.spec.goals.map(([h, b], i) => `
      <li><span class="num">${i + 1}</span>
        <span class="g-h">${br(h)}</span><span class="g-b">${br(b)}</span></li>`).join('');
    this.content('到達目標', `第${this.spec.no}回`, `<ol class="goals">${items}</ol>`);
  }

  sectionSlide(sec) {
    this.dark(`
      <div class="sec-wrap">
        <div class="sec-n">${br(sec.n)}</div>
        <h1 class="sec-name">${br(sec.name)}</h1>
        ${sec.tagline ? `<p class="sec-tag">${br(sec.tagline)}</p>` : ''}
      </div>`);
  }

  exercisesSlide() {
    const sp = this.spec;
    if (!sp.exercises || !sp.exercises.length) return;
    const items = sp.exercises.map(([n, t]) => `
      <li><span class="ex-n">${br(n)}</span><span class="ex-t">${br(t)}</span></li>`).join('');
    this.content('演習', `第${sp.no}回`, `<ul class="ex">${items}</ul>`);
  }

  summarySlide() {
    const sp = this.spec;
    const items = sp.summary.map(([h, b]) => `
      <li><span class="s-h">${br(h)}</span><span class="s-b">${br(b)}</span></li>`).join('');
    this.dark(`
      <div class="sum-wrap">
        <h1 class="sum-t">まとめ</h1>
        <ul class="sum">${items}</ul>
        ${sp.next ? `<p class="next"><b>次回</b>　${br(sp.next)}</p>` : ''}
      </div>`, '', false);
  }

  // --- 本文のスライド ------------------------------------------------
  render(sl) {
    const k = sl.kicker || '';
    switch (sl.kind) {
      case 'section':   return this.sectionSlide(sl);
      case 'cards':     return this.cards(sl, k);
      case 'bullets':   return this.bullets(sl, k);
      case 'figure':    return this.figureSlide(sl, k);
      case 'table':     return this.tableSlide(sl, k);
      case 'code':      return this.codeSlide(sl, k);
      case 'split':     return this.split(sl, k);
      case 'statement': return this.statement(sl, k);
      case 'steps':     return this.steps(sl, k);
      default: throw new Error('不明な kind: ' + sl.kind);
    }
  }

  cards(sl, k) {
    const per = sl.per || (sl.items.length <= 4 ? 2 : 3);
    const acc = sl.accent || [];
    const cards = sl.items.map(([h, b], i) => card(h, b, acc.includes(i))).join('');
    const callout = sl.callout ? `<div class="callout dashed">
        <div class="co-h">${br(sl.callout[0])}</div>
        <div class="co-b">${br(sl.callout[1])}</div>
      </div>` : '';
    this.content(sl.title, k, `${lead(sl)}
      <div class="cards" style="--per:${per}">${cards}</div>
      ${callout}${note(sl.note)}`);
  }

  bullets(sl, k) {
    const items = sl.items.map((t) => {
      const [text, lvl] = Array.isArray(t) ? t : [t, 0];
      return `<li class="lv${lvl || 0}">${br(text)}</li>`;
    }).join('');
    this.content(sl.title, k, `${lead(sl)}<ul class="bullets">${items}</ul>${note(sl.note)}`);
  }

  figureSlide(sl, k) {
    this.content(sl.title, k, `${lead(sl)}
      <div class="figwrap">${figure(sl.fig)}</div>
      ${sl.caption ? `<p class="caption">${br(sl.caption)}</p>` : ''}
      ${sl.sub ? `<p class="sub center">${br(sl.sub)}</p>` : ''}
      ${note(sl.note)}`);
  }

  tableSlide(sl, k) {
    const callout = sl.callout
      ? `<div class="callout solid">${br(sl.callout)}</div>` : '';
    this.content(sl.title, k, `${lead(sl)}
      ${table(sl.rows, { colW: sl.colW, mono: sl.mono })}
      ${callout}${sub(sl.sub)}${note(sl.note)}`);
  }

  codeSlide(sl, k) {
    const body = sl.side
      ? `<div class="code-split">
          ${codeBox(sl.code, { small: sl.size && sl.size < 12.5 })}
          <div class="side"><div class="side-h">${br(sl.side.title)}</div>
            <div class="side-b">${br(sl.side.body)}</div></div>
        </div>`
      : codeBox(sl.code, { small: sl.size && sl.size < 12.5 });
    this.content(sl.title, k, `${lead(sl)}${body}${sub(sl.sub)}${note(sl.note)}`);
  }

  col(c) {
    let h = `<div class="col-h">${br(c.title)}</div>`;
    if (c.code) h += codeBox(c.code, { small: true });
    if (c.rows) h += table(c.rows, { colW: c.colW, mono: c.mono, align: c.align });
    if (c.items) h += `<ul class="bullets tight">${c.items.map((t) => `<li>${br(t)}</li>`).join('')}</ul>`;
    if (c.body) h += `<p class="col-b">${br(c.body)}</p>`;
    if (c.note) h += `<p class="col-n">${br(c.note)}</p>`;
    return `<div class="col">${h}</div>`;
  }

  split(sl, k) {
    this.content(sl.title, k, `${lead(sl)}
      <div class="split">${this.col(sl.left)}${this.col(sl.right)}</div>
      ${note(sl.note)}`);
  }

  statement(sl, k) {
    const map = (sl.map || []).map(([a, b]) => `
      <li><span class="m-a">${br(a)}</span><span class="m-arrow"></span>
        <span class="m-b">${br(b)}</span></li>`).join('');
    this.content(sl.title, k, `${lead(sl)}
      <div class="callout solid big">${br(sl.statement)}</div>
      ${map ? `<ul class="map">${map}</ul>` : ''}
      ${sub(sl.sub)}${note(sl.note)}`);
  }

  steps(sl, k) {
    const n = sl.steps.length;
    const items = sl.steps.map(([h, b], i) => `
      <div class="step${i === 0 ? ' first' : ''}">
        <div class="st-n">${i + 1}</div>
        <div class="st-h">${br(h)}</div>
        <div class="st-b">${br(b)}</div>
      </div>`).join('');
    this.content(sl.title, k, `${lead(sl)}
      <div class="steps" style="--n:${n}">${items}</div>
      ${sub(sl.sub)}${note(sl.note)}`);
  }

  build() {
    const sp = this.spec;
    this.titleSlide();
    this.questionSlide();
    this.goalsSlide();
    sp.slides.forEach((sl) => this.render(sl));
    this.exercisesSlide();
    this.summarySlide();
    return { html: page(sp, this.slides), n: this.page, missing };
  }
}

// --- ページ全体 -------------------------------------------------------
function page(sp, slides) {
  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>第${sp.no}回 ${esc(sp.title)}｜コンピュータシステム通論</title>
<style>
${css()}
</style>
</head>
<body>
<div id="deck">
${slides.join('\n')}
</div>
<div id="hud"><span id="cur">1</span> / <span id="total">${slides.length}</span></div>
<div id="help" hidden>
  <h3>操作</h3>
  <table>
    <tr><td>→ ↓ Space PageDown</td><td>次へ</td></tr>
    <tr><td>← ↑ PageUp</td><td>前へ</td></tr>
    <tr><td>Home / End</td><td>最初 / 最後</td></tr>
    <tr><td>数字 + Enter</td><td>その番号へ</td></tr>
    <tr><td>O</td><td>一覧表示</td></tr>
    <tr><td>F</td><td>全画面</td></tr>
    <tr><td>C</td><td>組版チェック（溢れの検出）</td></tr>
    <tr><td>P</td><td>印刷（PDF 保存）</td></tr>
    <tr><td>?</td><td>この画面</td></tr>
  </table>
  <p>印刷は1枚1ページで出る。PDF にすれば pptx を配るのと同じことができる。</p>
</div>
<script>
${js()}
</script>
</body>
</html>`;
}

function css() {
  return `
:root{
  --ink:${C.ink}; --paper:${C.paper}; --tint:${C.tint}; --tint2:${C.tint2};
  --acc:${C.acc}; --accT:${C.accT}; --mut:${C.mut}; --dim:${C.dim};
  --lightInk:${C.lightInk}; --accLight:${C.accLight}; --code:${C.code}; --ghost:${C.ghost};
  --ja:${JA}; --mono:${MONO};
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{height:100%;background:#0b0d10;font-family:var(--ja);
  -webkit-font-smoothing:antialiased;overflow:hidden}

/* 1280x720 の板を作り、画面の大きさに合わせて拡大縮小する。
   どの画面でも同じ見た目になる —— スライドである以上これが要る。 */
#deck{position:absolute;inset:0}
.slide{
  position:absolute;top:50%;left:50%;
  width:${STAGE_W}px;height:${STAGE_H}px;
  transform:translate(-50%,-50%) scale(var(--s,1));
  transform-origin:center center;
  overflow:hidden;display:none;
}
.slide.on{display:block}
.slide.light{background:var(--paper);color:var(--ink)}
.slide.dark{background:var(--ink);color:var(--paper)}

/* --- 明色スライドの骨格 --- */
.slide.light header{position:absolute;top:33px;left:60px;right:60px}
.kicker{font-size:16px;font-weight:700;color:var(--acc);letter-spacing:.02em}
.slide.light h2{font-size:40px;font-weight:700;line-height:1.25;margin-top:6px}
/* 内容の塊ごと、見出しと下端のあいだで縦に中央へ寄せる。
   pptx では noteY を1枚ずつ手で詰めて注記を内容の直下に置いていた。
   CSS は高さを知っているので、その手当てが要らない。 */
.slide.light .body{position:absolute;top:130px;left:72px;right:72px;bottom:56px;
  display:flex;flex-direction:column;gap:14px;justify-content:center}
.pageno{position:absolute;right:60px;bottom:22px;font-size:13px;color:var(--mut)}

.lead{font-size:20px;line-height:1.55;color:var(--ink)}
.sub{font-size:17px;line-height:1.6;color:var(--mut)}
.sub.center,.caption{text-align:center}
.caption{font-size:20px;line-height:1.5;color:var(--ink)}
.note{font-size:17px;line-height:1.5;font-weight:700;color:var(--acc);margin-top:8px}

/* --- 意匠：マス目 --- */
.motif{position:absolute;left:58px;bottom:56px;display:flex;gap:4px}
.motif i{width:28px;height:19px;border:1px solid rgba(106,176,243,.45);border-radius:2px}
.motif i.on{background:var(--accLight);border-color:var(--accLight)}
.slide.title .motif{bottom:128px}

/* --- 表紙 --- */
.title-wrap{position:absolute;left:86px;top:188px;right:86px}
.course{font-size:23px;color:var(--dim);letter-spacing:.12em}
.slide.title h1{font-weight:700;line-height:1.2;margin-top:24px;color:var(--paper)}
.tq{font-size:24px;line-height:1.5;color:var(--accLight);margin-top:28px}
.affil{position:absolute;left:86px;bottom:22px;font-size:16px;color:var(--dim)}

/* --- 今回の問い --- */
.q-wrap{position:absolute;left:86px;right:86px;top:144px}
.q-label{font-size:19px;font-weight:700;color:var(--accLight)}
.q-big{font-size:48px;font-weight:700;line-height:1.35;margin-top:22px;color:var(--paper)}
.q-sub{font-size:27px;color:var(--lightInk);margin-top:22px}
.q-foot{font-size:19px;color:var(--dim);margin-top:40px}

/* --- 節の区切り --- */
.sec-wrap{position:absolute;left:86px;right:86px;top:230px}
.sec-n{font-size:75px;font-weight:700;color:var(--ghost);line-height:1}
.sec-name{font-size:51px;font-weight:700;color:var(--paper);margin-top:10px;line-height:1.2}
.sec-tag{font-size:23px;color:var(--dim);margin-top:18px}

/* --- 到達目標 --- */
.goals{list-style:none;display:flex;flex-direction:column;gap:18px;margin-top:8px}
.goals li{display:flex;align-items:center;gap:18px}
.goals .num{flex:none;width:48px;height:48px;border-radius:50%;
  background:var(--accT);border:1.5px solid var(--acc);color:var(--acc);
  font-size:19px;font-weight:700;display:grid;place-items:center}
.g-h{font-size:21px;font-weight:700;color:var(--ink)}
.g-b{font-size:19px;color:var(--mut);margin-left:12px}

/* --- カード --- */
.cards{display:grid;grid-template-columns:repeat(var(--per),1fr);gap:16px;align-content:start}
.card{background:var(--tint);border:1px solid var(--tint2);border-radius:8px;padding:16px 18px}
.card.acc{background:var(--accT);border-color:var(--acc)}
.card-h{font-size:19px;font-weight:700;color:var(--ink)}
.card.acc .card-h{color:var(--acc)}
.card-b{font-size:16px;line-height:1.55;color:var(--mut);margin-top:8px}

/* --- 囲み --- */
.callout{border-radius:8px;padding:14px 20px}
.callout.dashed{border:1.5px dashed var(--acc);background:var(--paper)}
.callout.solid{border:1.5px solid var(--acc);background:var(--accT);
  font-size:20px;font-weight:700;color:var(--acc);line-height:1.45}
.callout.big{font-size:23px}
.co-h{font-size:20px;font-weight:700;color:var(--acc)}
.co-b{font-size:16px;line-height:1.5;color:var(--mut);margin-top:6px}

/* --- 箇条書き --- */
.bullets{list-style:none;display:flex;flex-direction:column;gap:10px}
.bullets li{position:relative;padding-left:22px;font-size:21px;line-height:1.5;color:var(--ink)}
.bullets li::before{content:"";position:absolute;left:4px;top:.62em;
  width:7px;height:7px;border-radius:50%;background:var(--acc)}
.bullets li.lv1{font-size:18px;color:var(--mut);padding-left:44px}
.bullets li.lv1::before{left:26px;width:5px;height:5px;background:var(--mut)}
.bullets.tight li{font-size:18px;gap:6px}

/* --- コード --- */
.code{background:var(--code);border:1px solid var(--tint2);border-radius:6px;
  padding:16px 20px;font-family:var(--mono);font-size:17px;line-height:1.7;
  color:var(--ink);white-space:pre;overflow:hidden}
.code.small{font-size:15.5px}
.code-split{display:grid;grid-template-columns:1fr .92fr;gap:22px;align-items:start}
.side-h{font-size:19px;font-weight:700;color:var(--ink)}
.side-b{font-size:17px;line-height:1.6;color:var(--mut);margin-top:8px}

/* --- 表 --- */
.tbl{width:100%;border-collapse:collapse;table-layout:fixed}
.tbl th,.tbl td{border:1px solid var(--tint2);padding:7px 11px;font-size:17px;
  line-height:1.4;text-align:left;vertical-align:middle;word-break:break-word}
.tbl th{background:var(--tint);font-weight:700}
.tbl.mono{font-family:var(--mono);font-size:16px}
.tbl.mono th{font-family:var(--ja)}
.tbl.center th,.tbl.center td{text-align:center}

/* --- 左右2段 --- */
.split{display:grid;grid-template-columns:1fr 1fr;gap:26px;align-items:start}
.col{display:flex;flex-direction:column;gap:11px}
.col-h{font-size:20px;font-weight:700;color:var(--ink)}
.col-b{font-size:17px;line-height:1.65;color:var(--mut)}
.col-n{font-size:17px;font-weight:700;color:var(--acc)}

/* --- 主張と対応 --- */
.map{list-style:none;display:flex;flex-direction:column;gap:12px;margin-top:6px}
.map li{display:grid;grid-template-columns:1fr 60px 1fr;align-items:center;gap:8px}
.m-a{font-size:20px;color:var(--ink);text-align:right}
.m-arrow{height:3px;background:var(--acc);position:relative;border-radius:2px}
.m-arrow::after{content:"";position:absolute;right:-1px;top:-5px;
  border:7px solid transparent;border-left-color:var(--acc);border-right:0}
.m-b{font-size:21px;font-weight:700;color:var(--acc)}

/* --- 手順 --- */
.steps{display:grid;grid-template-columns:repeat(var(--n),1fr);gap:10px;align-items:stretch}
.step{background:var(--tint);border:1px solid var(--tint2);border-radius:8px;padding:12px 12px 14px}
.step.first{background:var(--accT);border-color:var(--acc)}
.st-n{font-family:var(--mono);font-size:15px;font-weight:700;color:var(--acc)}
.st-h{font-size:17px;font-weight:700;color:var(--ink);margin-top:6px;line-height:1.3}
.st-b{font-size:15px;color:var(--mut);margin-top:6px;line-height:1.45}

/* --- 図 --- */
/* 図は枠いっぱいまで伸ばす。SVG なので拡大しても粗くならない。
   pptx 版も箱に合わせて拡大していたので、そこは同じ振る舞いにしてある。 */
.figwrap{flex:1;min-height:0;display:flex}
.fig{width:100%;height:100%;object-fit:contain}
.fig-missing{color:#b00;font-size:20px;text-align:center;padding:40px}

/* --- 演習 --- */
.ex{list-style:none;display:flex;flex-direction:column;gap:16px}
.ex li{display:flex;gap:18px;align-items:flex-start}
.ex-n{flex:none;width:74px;padding:5px 0;text-align:center;border-radius:7px;
  background:var(--accT);border:1px solid var(--acc);color:var(--acc);
  font-family:var(--mono);font-size:17px;font-weight:700}
.ex-t{font-size:19px;line-height:1.55;color:var(--ink);padding-top:3px}

/* --- まとめ --- */
.sum-wrap{position:absolute;left:86px;right:86px;top:74px;bottom:74px;
  display:flex;flex-direction:column}
.sum-t{font-size:40px;font-weight:700;color:var(--paper)}
.sum{list-style:none;display:flex;flex-direction:column;gap:16px;margin-top:26px}
.sum li{display:grid;grid-template-columns:300px 1fr;gap:24px;align-items:baseline}
.s-h{font-size:20px;font-weight:700;color:var(--accLight)}
.s-b{font-size:18px;line-height:1.5;color:var(--lightInk)}
.next{font-size:17px;color:var(--dim);margin-top:auto;line-height:1.5}
.next b{color:var(--accLight)}

/* --- 画面まわり --- */
#hud{position:fixed;left:16px;bottom:12px;font-size:13px;color:#7c8694;
  font-family:var(--mono);z-index:20;user-select:none}
#help{position:fixed;inset:50% auto auto 50%;transform:translate(-50%,-50%);
  background:#fff;color:var(--ink);border-radius:12px;padding:26px 30px;z-index:30;
  box-shadow:0 20px 60px rgba(0,0,0,.5);font-size:15px;max-width:520px}
#help h3{font-size:19px;margin-bottom:14px}
#help table{border-collapse:collapse;width:100%}
#help td{padding:5px 10px 5px 0;vertical-align:top}
#help td:first-child{font-family:var(--mono);color:var(--acc);white-space:nowrap}
#help p{margin-top:14px;color:var(--mut);font-size:13.5px;line-height:1.6}

/* --- 一覧表示 --- */
body.overview{overflow:auto}
body.overview #deck{position:static;display:grid;
  grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:18px;padding:22px}
body.overview .slide{position:relative;top:auto;left:auto;display:block;
  transform:scale(var(--os));transform-origin:top left;
  width:${STAGE_W}px;height:${STAGE_H}px;cursor:pointer;
  outline:2px solid #2a3340;border-radius:2px}
body.overview .slide.on{outline:3px solid var(--accLight)}
body.overview .sl-wrap{overflow:hidden}

/* --- 組版チェック：実際に溢れた箇所だけを赤で示す --- */
body.check .slide.overflow{outline:4px solid #e0453a;outline-offset:-4px}
body.check .slide.overflow::after{content:"組版あふれ";position:absolute;
  right:0;top:0;background:#e0453a;color:#fff;font-size:13px;padding:3px 9px;
  font-weight:700;z-index:9}

/* --- 印刷：1枚1ページ。PDF にすれば配布できる --- */
@page{size:${STAGE_W}px ${STAGE_H}px;margin:0}
@media print{
  html,body{overflow:visible;background:#fff;height:auto}
  #hud,#help{display:none!important}
  #deck{position:static}
  .slide{position:relative!important;display:block!important;top:auto;left:auto;
    transform:none!important;page-break-after:always;break-after:page;
    width:${STAGE_W}px;height:${STAGE_H}px}
  .slide:last-child{page-break-after:auto;break-after:auto}
}`;
}

function js() {
  return `
(function(){
  var deck=document.getElementById('deck');
  var slides=[].slice.call(deck.querySelectorAll('.slide'));
  var cur=0, buf='';
  var hud=document.getElementById('cur'), help=document.getElementById('help');

  // 板を画面に合わせて拡大縮小する
  function fit(){
    var s=Math.min(innerWidth/${STAGE_W}, innerHeight/${STAGE_H});
    document.documentElement.style.setProperty('--s', s);
    var ow=(310)/${STAGE_W};
    slides.forEach(function(el){ el.style.setProperty('--os', ow); });
    if(document.body.classList.contains('overview')) layoutOverview();
  }
  function layoutOverview(){
    // 一覧では実寸の板を縮めて置くので、親に実際の見かけの大きさを持たせる
    var cell=deck.clientWidth/Math.max(1,Math.floor(deck.clientWidth/330));
    var s=(cell-8)/${STAGE_W};
    slides.forEach(function(el){
      el.style.setProperty('--os', s);
      el.style.marginBottom=(${STAGE_H}*s-${STAGE_H})+'px';
      el.style.marginRight=(${STAGE_W}*s-${STAGE_W})+'px';
    });
  }
  function show(i){
    cur=Math.max(0,Math.min(slides.length-1,i));
    slides.forEach(function(el,j){ el.classList.toggle('on', j===cur); });
    hud.textContent=cur+1;
    if(location.hash!=='#'+(cur+1)) history.replaceState(null,'','#'+(cur+1));
  }
  function overview(on){
    document.body.classList.toggle('overview', on);
    if(on){ slides.forEach(function(el){ el.classList.add('on'); }); layoutOverview();
            slides[cur].scrollIntoView({block:'center'}); }
    else { slides.forEach(function(el){ el.style.margin=''; }); fit(); show(cur); }
  }

  // 組版チェック。実際に描いた結果を測るので、見積もりではなく事実が分かる。
  // pptx では PowerPoint に描かせるまで分からなかった部分である。
  function check(){
    var bad=[];
    slides.forEach(function(el,i){
      var was=el.classList.contains('on');
      el.classList.add('on');
      var over=false;
      [].slice.call(el.querySelectorAll('*')).forEach(function(n){
        var r=n.getBoundingClientRect(), e=el.getBoundingClientRect();
        if(r.height&&(r.bottom>e.bottom+1||r.right>e.right+1)) over=true;
      });
      if(el.scrollHeight>el.clientHeight+1||el.scrollWidth>el.clientWidth+1) over=true;
      el.classList.toggle('overflow', over);
      if(over) bad.push(i+1);
      if(!was) el.classList.remove('on');
    });
    document.body.classList.add('check');
    slides[cur].classList.add('on');
    console.log(bad.length? '組版あふれ: '+bad.length+'枚 → '+bad.join(', ') : '組版あふれなし');
    return bad;
  }

  addEventListener('resize', fit);
  addEventListener('hashchange', function(){
    var n=parseInt(location.hash.slice(1),10); if(n) show(n-1);
  });
  addEventListener('keydown', function(e){
    if(e.metaKey||e.ctrlKey||e.altKey) return;
    var k=e.key;
    if(k>='0'&&k<='9'){ buf+=k; return; }
    if(k==='Enter'){ if(buf){ show(parseInt(buf,10)-1); buf=''; } return; }
    buf='';
    switch(k){
      case 'ArrowRight': case 'ArrowDown': case ' ': case 'PageDown':
        e.preventDefault(); show(cur+1); break;
      case 'ArrowLeft': case 'ArrowUp': case 'PageUp':
        e.preventDefault(); show(cur-1); break;
      case 'Home': show(0); break;
      case 'End': show(slides.length-1); break;
      case 'o': case 'O': overview(!document.body.classList.contains('overview')); break;
      case 'f': case 'F':
        if(document.fullscreenElement) document.exitFullscreen();
        else document.documentElement.requestFullscreen(); break;
      case 'c': case 'C':
        if(document.body.classList.contains('check')){
          document.body.classList.remove('check');
          slides.forEach(function(el){ el.classList.remove('overflow'); });
        } else check();
        break;
      case 'p': case 'P': print(); break;
      case '?': help.hidden=!help.hidden; break;
      case 'Escape': help.hidden=true; if(document.body.classList.contains('overview')) overview(false); break;
    }
  });
  deck.addEventListener('click', function(e){
    var el=e.target.closest('.slide'); if(!el) return;
    if(document.body.classList.contains('overview')){
      show(slides.indexOf(el)); overview(false);
    } else show(cur+1);
  });

  fit();
  var n=parseInt(location.hash.slice(1),10);
  show(n? n-1 : 0);
  window.__check=check;
})();`;
}

module.exports = { Deck, C, JA, MONO, STAGE_W, STAGE_H };
