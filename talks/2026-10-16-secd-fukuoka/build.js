#!/usr/bin/env node
// 講演スライドを組む。  node talks/2026-10-16-secd-fukuoka/build.js
//
// 体裁は過去の講演資料「沈まないための備え」に合わせた（深緑・墨・琥珀、Yu Gothic、16:9）。
// pptxgenjs は slides/node_modules から読む（cd slides && npm install pptxgenjs）。
const path = require('path');
const PptxGenJS = require(path.join(__dirname, '..', '..', 'slides', 'node_modules', 'pptxgenjs'));
const spec = require('./deck');

const C = {
  ink: '16211F', deep: '0E2E2A', acc: '2E7D6B', mut: '5E6E6A', dim: '9FB2AD',
  tint: 'EDF3F1', tint2: 'C9D5D1', pale: 'F4F7F6', paper: 'FFFFFF',
  amber: 'C9821A', amberT: 'F6EBD8', light: 'E8F0EC',
};
const JA = 'Yu Gothic';
const W = 13.333, M = 0.7, CW = W - 2 * M;

// --- 文字があふれないかの見積もり（slides/tools/kit.js と同じ式）-------
const warnings = [];
function fit(text, w, h, size, where) {
  if (!text) return;
  const perLine = Math.max(1, Math.floor((w * 72) / size));
  const lines = String(text).split('\n').reduce((a, l) => {
    let u = 0;
    for (const ch of l) u += /[\x20-\x7E]/.test(ch) ? 0.52 : 1.0;
    return a + Math.max(1, Math.ceil(u / perLine));
  }, 0);
  const need = (lines * size * 1.4) / 72;
  if (need > h + 0.02) warnings.push(`${where}: 高さ ${h.toFixed(2)}" に ${lines}行（約 ${need.toFixed(2)}"）`);
}

const pres = new PptxGenJS();
pres.layout = 'LAYOUT_WIDE';
pres.author = spec.speaker;
pres.title = spec.title.replace('\n', '');
const S = pres.ShapeType;
const TOTAL = spec.slides.length + 2;
let page = 0;

function txt(s, text, o) {
  s.addText(text, { fontFace: JA, margin: 0, ...o });
  if (o.h && o.fontSize) fit(text, o.w, o.h, o.fontSize, `p${page} 「${String(text).slice(0, 14)}…」`);
}

function dark() {
  const s = pres.addSlide();
  s.background = { color: C.deep };
  page += 1;
  return s;
}

function content(sl) {
  const s = pres.addSlide();
  s.background = { color: C.paper };
  page += 1;
  s.addShape(S.rect, { x: 0, y: 0, w: 0.14, h: 7.5, fill: { color: C.acc }, line: { type: 'none' } });
  txt(s, sl.part || '', { x: M, y: 0.32, w: 8.5, h: 0.3, fontSize: 12, bold: true, color: C.acc });
  if (sl.min) txt(s, sl.min, { x: W - M - 2, y: 0.32, w: 2, h: 0.3, fontSize: 11, color: C.mut, align: 'right' });
  txt(s, sl.title, { x: M, y: 0.68, w: CW, h: 0.75, fontSize: 26, bold: true, color: C.ink, valign: 'top' });
  txt(s, `${page} / ${TOTAL}`, { x: W - M - 1.5, y: 7.05, w: 1.5, h: 0.25, fontSize: 9, color: C.mut, align: 'right' });
  txt(s, 'Security Days Fall 2026 Fukuoka　FB-05　小出 洋（九州大学）', { x: M, y: 7.05, w: 7, h: 0.25, fontSize: 9, color: C.dim });
  return s;
}

function note(s, text, y) {
  if (!text) return;
  s.addShape(S.rect, { x: M, y, w: CW, h: 0.72, fill: { color: C.amberT }, line: { type: 'none' } });
  s.addShape(S.rect, { x: M, y, w: 0.08, h: 0.72, fill: { color: C.amber }, line: { type: 'none' } });
  txt(s, text, { x: M + 0.3, y: y + 0.08, w: CW - 0.5, h: 0.56, fontSize: 14, bold: true, color: C.ink, valign: 'middle' });
}

function card(s, x, y, w, h, head, body, o = {}) {
  const fill = o.dark ? C.acc : (o.pale ? C.pale : C.tint);
  s.addShape(S.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: fill }, line: { color: o.dark ? C.acc : C.tint2, width: 0.75 } });
  txt(s, head, { x: x + 0.2, y: y + 0.16, w: w - 0.4, h: o.headH || 0.45, fontSize: o.headSize || 16, bold: true, color: o.dark ? C.paper : C.acc, valign: 'top' });
  if (body) {
    const by = y + 0.18 + (o.headH || 0.45) + 0.08;
    txt(s, body, { x: x + 0.2, y: by, w: w - 0.4, h: y + h - by - 0.12, fontSize: o.bodySize || 13, color: o.dark ? C.light : C.ink, valign: 'top', lineSpacingMultiple: 1.15 });
  }
}

// ------------------------------------------------------------------ 定型
function titleSlide() {
  const s = dark();
  s.addShape(S.rect, { x: 0, y: 0, w: 0.22, h: 7.5, fill: { color: C.acc }, line: { type: 'none' } });
  txt(s, spec.event, { x: 0.9, y: 1.1, w: 11.8, h: 0.35, fontSize: 14, color: C.dim });
  txt(s, spec.title, { x: 0.9, y: 1.8, w: 11.8, h: 2.1, fontSize: 40, bold: true, color: C.paper, lineSpacingMultiple: 1.1 });
  txt(s, spec.subtitle, { x: 0.9, y: 4.05, w: 11.8, h: 0.6, fontSize: 24, color: C.amber });
  txt(s, spec.speaker, { x: 0.9, y: 5.6, w: 11.8, h: 0.4, fontSize: 16, color: C.light });
  if (spec.titleNotes) s.addNotes(spec.titleNotes);
}

const render = {
  section(sl) {
    const s = dark();
    s.addShape(S.rect, { x: 0, y: 0, w: 0.22, h: 7.5, fill: { color: C.acc }, line: { type: 'none' } });
    txt(s, sl.n, { x: 0.9, y: 2.3, w: 4, h: 0.6, fontSize: 24, bold: true, color: C.amber });
    txt(s, sl.name, { x: 0.9, y: 2.95, w: 11.6, h: 0.9, fontSize: 38, bold: true, color: C.paper });
    if (sl.tagline) txt(s, sl.tagline, { x: 0.9, y: 4.0, w: 11.6, h: 0.5, fontSize: 18, color: C.dim });
    return s;
  },

  numbered(sl) {
    const s = content(sl);
    sl.items.forEach(([h, b], i) => {
      const y = 1.7 + i * 1.3;
      s.addShape(S.ellipse, { x: M, y: y + 0.05, w: 0.7, h: 0.7, fill: { color: C.acc }, line: { type: 'none' } });
      txt(s, String(i + 1), { x: M, y: y + 0.05, w: 0.7, h: 0.7, fontSize: 22, bold: true, color: C.paper, align: 'center', valign: 'middle' });
      txt(s, h, { x: M + 1.0, y, w: CW - 1.0, h: 0.5, fontSize: 19, bold: true, color: C.ink, valign: 'middle' });
      txt(s, b, { x: M + 1.0, y: y + 0.52, w: CW - 1.0, h: 0.45, fontSize: 14, color: C.mut });
    });
    note(s, sl.note, 5.75);
    return s;
  },

  steps(sl) {
    const s = content(sl);
    const n = sl.steps.length, arrow = 0.42;
    const w = (CW - arrow * (n - 1)) / n, h = 3.3, y = 1.65;
    sl.steps.forEach(([head, body], i) => {
      const x = M + i * (w + arrow);
      card(s, x, y, w, h, head, body, { dark: i === n - 1, headH: head.includes('\n') ? 0.8 : 0.45, bodySize: 14 });
      if (i < n - 1) s.addShape(S.rightArrow, { x: x + w + 0.07, y: y + h / 2 - 0.18, w: arrow - 0.14, h: 0.36, fill: { color: C.tint2 }, line: { type: 'none' } });
    });
    note(s, sl.note, 5.3);
    return s;
  },

  map(sl) {
    const s = content(sl);
    sl.rows.forEach(([min, head, body], i) => {
      const y = 1.6 + i * 0.78;
      s.addShape(S.rect, { x: M, y, w: 1.1, h: 0.62, fill: { color: C.acc }, line: { type: 'none' } });
      txt(s, min, { x: M, y, w: 1.1, h: 0.62, fontSize: 15, bold: true, color: C.paper, align: 'center', valign: 'middle' });
      s.addShape(S.rect, { x: M + 1.1, y, w: CW - 1.1, h: 0.62, fill: { color: i % 2 ? C.pale : C.tint }, line: { type: 'none' } });
      txt(s, head, { x: M + 1.35, y, w: 4.0, h: 0.62, fontSize: 16, bold: true, color: C.ink, valign: 'middle' });
      txt(s, body, { x: M + 5.4, y, w: CW - 5.6, h: 0.62, fontSize: 14, color: C.mut, valign: 'middle' });
    });
    note(s, sl.note, 5.75);
    return s;
  },

  flow(sl) {
    const s = content(sl);
    const n = sl.flow.length, arrow = 0.5, w = (CW - arrow * (n - 1)) / n, h = 1.55, y = 1.65;
    sl.flow.forEach(([head, body, tone], i) => {
      const x = M + i * (w + arrow);
      const fill = tone === 'acc' ? C.acc : tone === 'ink' ? C.ink : C.tint;
      const fg = tone === 'tint' ? C.ink : C.paper;
      s.addShape(S.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: fill }, line: { type: 'none' } });
      txt(s, head, { x: x + 0.2, y: y + 0.18, w: w - 0.4, h: 0.4, fontSize: 17, bold: true, color: fg, align: 'center' });
      txt(s, body, { x: x + 0.2, y: y + 0.62, w: w - 0.4, h: 0.8, fontSize: 14, color: fg, align: 'center', valign: 'top' });
      if (i < n - 1) s.addShape(S.rightArrow, { x: x + w + 0.08, y: y + h / 2 - 0.18, w: arrow - 0.16, h: 0.36, fill: { color: C.tint2 }, line: { type: 'none' } });
    });
    txt(s, '人と組織がこなすべき一連の処理（個々のAIツールの性能だけでは片づかない）', { x: M, y: 3.5, w: CW, h: 0.3, fontSize: 12, bold: true, color: C.mut });
    const per = 3, cw = (CW - 0.2 * (per - 1)) / per;
    sl.chips.forEach((c, i) => {
      const x = M + (i % per) * (cw + 0.2), yy = 3.9 + Math.floor(i / per) * 0.62;
      s.addShape(S.roundRect, { x, y: yy, w: cw, h: 0.5, rectRadius: 0.05, fill: { color: C.pale }, line: { color: C.tint2, width: 0.75 } });
      txt(s, c, { x, y: yy, w: cw, h: 0.5, fontSize: 14, color: C.ink, align: 'center', valign: 'middle' });
    });
    note(s, sl.note, 5.55);
    return s;
  },

  cards(sl) {
    const s = content(sl);
    const per = sl.per || sl.items.length, gap = 0.22;
    const w = (CW - gap * (per - 1)) / per, h = 3.35;
    sl.items.forEach(([head, body], i) => card(s, M + i * (w + gap), 1.7, w, h, head, body, { headSize: per >= 5 ? 17 : 16 }));
    note(s, sl.note, 5.35);
    return s;
  },

  quad(sl) {
    const s = content(sl);
    txt(s, 'AIが示した候補を、自社のシステムの構造へ戻して問い直す', { x: M, y: 1.55, w: 7.4, h: 0.3, fontSize: 13, bold: true, color: C.mut });
    const w = 3.6, h = 1.35;
    sl.items.forEach((q, i) => {
      const x = M + (i % 2) * (w + 0.2), y = 1.95 + Math.floor(i / 2) * (h + 0.2);
      s.addShape(S.roundRect, { x, y, w, h, rectRadius: 0.05, fill: { color: C.tint }, line: { color: C.tint2, width: 0.75 } });
      txt(s, q, { x: x + 0.15, y, w: w - 0.3, h, fontSize: 17, bold: true, color: C.acc, align: 'center', valign: 'middle' });
    });
    card(s, M + 7.7, 1.95, CW - 7.7, 2.9, sl.side[0], sl.side[1], { pale: true, bodySize: 13.5 });
    note(s, sl.note, 5.35);
    return s;
  },

  split(sl) {
    const s = content(sl);
    const w = (CW - 0.3) / 2, h = 3.55;
    card(s, M, 1.65, w, h, sl.left.title, sl.left.body, { bodySize: 14 });
    card(s, M + w + 0.3, 1.65, w, h, sl.right.title, sl.right.body, { dark: true, bodySize: 14 });
    note(s, sl.note, 5.45);
    return s;
  },

  table(sl) {
    const s = content(sl);
    const head = sl.rows[0].map((c, j) => ({ text: c, options: { bold: true, color: C.paper, fill: { color: j === sl.hi ? C.amber : C.acc } } }));
    const body = sl.rows.slice(1).map((r, i) => r.map((c, j) => ({
      text: c,
      options: {
        bold: j === 0, color: C.ink,
        fill: { color: j === sl.hi ? C.amberT : (i % 2 ? C.paper : C.pale) },
      },
    })));
    const rowH = sl.rowH || 0.5;
    s.addTable([head, ...body], {
      x: M, y: 1.6, w: CW, colW: sl.colW, fontFace: JA, fontSize: 13, valign: 'middle',
      border: { type: 'solid', color: C.tint2, pt: 0.75 }, rowH, margin: [0.05, 0.12, 0.05, 0.12],
    });
    sl.rows.forEach((r) => r.forEach((c, j) => fit(c, sl.colW[j] - 0.24, rowH - 0.06, 13, `p${page} 表「${String(c).slice(0, 10)}…」`)));
    if (sl.note) note(s, sl.note, Math.max(5.45, 1.6 + rowH * sl.rows.length + 0.3));
    return s;
  },
};

// ------------------------------------------------------------------ 組む
titleSlide();
for (const sl of spec.slides) {
  const fn = render[sl.kind];
  if (!fn) throw new Error(`未知の kind: ${sl.kind}`);
  const s = fn(sl);
  if (sl.notes) s.addNotes(sl.notes);
}
{
  const s = dark();
  s.addShape(S.rect, { x: 0, y: 0, w: 0.22, h: 7.5, fill: { color: C.acc }, line: { type: 'none' } });
  txt(s, 'ご清聴ありがとうございました', { x: 0.9, y: 2.6, w: 11.6, h: 0.9, fontSize: 36, bold: true, color: C.paper });
  txt(s, spec.speaker, { x: 0.9, y: 3.7, w: 11.6, h: 0.5, fontSize: 18, color: C.dim });
}

const out = path.join(__dirname, spec.file);
pres.writeFile({ fileName: out }).then(() => {
  console.log(`${page} 枚  ${path.basename(out)}`);
  if (warnings.length) {
    console.log(`\n--- 溢れの疑い ${warnings.length} 件 ---`);
    warnings.forEach((w) => console.log('  ' + w));
  } else console.log('溢れの疑いなし');
});
