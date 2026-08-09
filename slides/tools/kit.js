// スライドの体裁。13回ぶんの見た目をここ1箇所で決める。
// 各回は decks/lecNN.js に「何を並べるか」だけを書き、配置はここが引き受ける。
const PptxGenJS = require('pptxgenjs');
const path = require('path');
const fs = require('fs');

const ROOT = path.join(__dirname, '..', '..');       // リポジトリの根
const PNG = path.join(ROOT, 'slides', 'png');

// 図の SVG と同じ配色。スライドと図が別物に見えないようにするため
const C = {
  ink: '16191D',
  paper: 'FFFFFF',
  tint: 'EEF1F5',
  tint2: 'DDE4EC',
  acc: '0B5CAD',
  accT: 'D9E6F4',
  mut: '5F6672',        // 明色の地の上でのみ使う
  dim: '9AA3B0',        // 濃色の地の上で使う。mut は暗すぎて読めない
  lightInk: 'E8EBEF',
  accLight: '6AB0F3',
  code: 'F5F7FA',
  ghost: '2E3A4A',
};
const JA = 'Yu Gothic';
const MONO = 'Courier New';
const W = 13.3, H = 7.5;
const M = 0.75, CW = 11.8;       // 左余白と本文幅

// --- 文字があふれないかの見積もり -----------------------------------
// 実際に描くまで分からないのが本当だが、明らかな溢れはここで捕まえる。
const warnings = [];
function fit(text, w, h, size, where) {
  if (!text) return;
  const s = String(text);
  let units = 0;
  for (const ch of s) units += /[\x20-\x7E]/.test(ch) ? 0.52 : 1.0;
  const perLine = Math.max(1, Math.floor((w * 72) / (size * 1.0)));
  const lines = s.split('\n').reduce((a, l) => {
    let u = 0;
    for (const ch of l) u += /[\x20-\x7E]/.test(ch) ? 0.52 : 1.0;
    return a + Math.max(1, Math.ceil(u / perLine));
  }, 0);
  const need = (lines * size * 1.45) / 72;
  if (need > h + 0.02) {
    warnings.push(`${where}: 高さ ${h.toFixed(2)}" に ${lines}行（約 ${need.toFixed(2)}"）`);
  }
}

// --- 意匠 -------------------------------------------------------------
// 濃色スライドの下端に並ぶマス目。回ごとに埋まり方を変えて見分けをつける。
function motif(pres, s, no, y = 6.4) {
  const cells = 26, w = 0.33, h = 0.2, x0 = 0.6;
  for (let i = 0; i < cells; i++) {
    const on = ((i * 7 + no * 5) % (no + 3)) === 0;
    s.addShape(pres.ShapeType.rect, {
      x: x0 + i * w, y, w: w - 0.04, h,
      fill: { color: on ? C.accLight : 'FFFFFF', transparency: on ? 0 : 88 },
      line: { color: C.accLight, width: 0.6, transparency: 55 },
    });
  }
}

// =====================================================================
class Deck {
  constructor(spec) {
    this.spec = spec;
    this.pres = new PptxGenJS();
    this.pres.layout = 'LAYOUT_WIDE';
    this.pres.author = '九州大学 コンピュータシステム通論';
    this.pres.title = `第${spec.no}回 ${spec.title}`;
    this.page = 0;      // 実際の通し番号。区切りスライドも数える
  }

  get S() { return this.pres.ShapeType; }

  dark() {
    const s = this.pres.addSlide();
    s.background = { color: C.ink };
    this.page += 1;     // 番号は振らないが、通し番号は進める
    return s;
  }

  page_(s) {
    s.addText(String(this.page), {
      x: 12.3, y: 6.95, w: 0.6, h: 0.3,
      fontFace: JA, fontSize: 10, color: C.mut, align: 'right', margin: 0,
    });
  }

  content(title, kicker) {
    const s = this.pres.addSlide();
    s.background = { color: C.paper };
    this.page += 1;
    if (kicker) {
      s.addText(kicker, {
        x: M - 0.13, y: 0.34, w: 5, h: 0.28,
        fontFace: JA, fontSize: 12, color: C.acc, bold: true, margin: 0,
      });
    }
    s.addText(title, {
      x: M - 0.15, y: kicker ? 0.66 : 0.5, w: 12.1, h: 0.8,
      fontFace: JA, fontSize: 30, bold: true, color: C.ink, margin: 0, valign: 'top',
    });
    fit(title, 12.1, 0.8, 30, `第${this.spec.no}回 見出し「${title}」`);
    this.page_(s);
    return s;
  }

  note(s, text, y = 6.5) {
    if (!text) return;
    s.addText(text, {
      x: M, y, w: CW, h: 0.56,
      fontFace: JA, fontSize: 13, color: C.acc, bold: true, margin: 0, lineSpacing: 19,
    });
    fit(text, CW, 0.56, 13, `第${this.spec.no}回 p${this.page} 注記`);
  }

  sub(s, text, y) {
    if (!text) return;
    s.addText(text, {
      x: M, y, w: CW, h: 0.5,
      fontFace: JA, fontSize: 13, color: C.mut, margin: 0, lineSpacing: 20,
    });
  }

  card(s, x, y, w, h, head, body, accent) {
    s.addShape(this.S.roundRect, {
      x, y, w, h, rectRadius: 0.06,
      fill: { color: accent ? C.accT : C.tint },
      line: { color: accent ? C.acc : C.tint2, width: 1 },
    });
    s.addText(head, {
      x: x + 0.2, y: y + 0.15, w: w - 0.4, h: 0.34,
      fontFace: JA, fontSize: 14, bold: true, color: accent ? C.acc : C.ink, margin: 0,
    });
    fit(head, w - 0.4, 0.34, 14, `第${this.spec.no}回 p${this.page} カード見出し「${head}」`);
    if (body) {
      s.addText(body, {
        x: x + 0.2, y: y + 0.53, w: w - 0.4, h: h - 0.7,
        fontFace: JA, fontSize: 12, color: C.mut, margin: 0, valign: 'top', lineSpacing: 16,
      });
      fit(body, w - 0.4, h - 0.7, 12, `第${this.spec.no}回 p${this.page} カード本文「${head}」`);
    }
  }

  codeBox(s, lines, o = {}) {
    const x = o.x ?? M, y = o.y ?? 2.0, w = o.w ?? 6.0, h = o.h ?? 2.2, size = o.size ?? 12.5;
    s.addShape(this.S.roundRect, {
      x, y, w, h, rectRadius: 0.04,
      fill: { color: C.code }, line: { color: C.tint2, width: 1 },
    });
    s.addText(lines.join('\n'), {
      x: x + 0.22, y: y + 0.16, w: w - 0.44, h: h - 0.32,
      fontFace: MONO, fontSize: size, color: C.ink, margin: 0, valign: 'top',
      lineSpacing: size * 1.5,
    });
  }

  table(s, rows, o = {}) {
    const head = rows[0].map((c) => ({
      text: String(c), options: { bold: true, fill: { color: C.tint } },
    }));
    const body = rows.slice(1).map((r) => r.map((c) => String(c)));
    s.addTable([head, ...body], {
      x: o.x ?? M, y: o.y ?? 2.0, w: o.w ?? CW, colW: o.colW,
      fontFace: o.mono ? MONO : JA, fontSize: o.size ?? 13,
      align: o.align ?? 'left', valign: 'middle',
      border: { type: 'solid', color: C.tint2, pt: 1 },
      fill: { color: C.paper }, rowH: o.rowH ?? 0.38,
    });
  }

  figure(s, name, o = {}) {
    const p = path.join(PNG, `fig-${name}.png`);
    if (!fs.existsSync(p)) {
      warnings.push(`第${this.spec.no}回 p${this.page}: 図 ${name} の PNG が無い`);
      return;
    }
    // 元の縦横比を保ったまま、与えられた枠に収める
    const dim = pngSize(p);
    const boxW = o.w ?? 9.0, boxH = o.h ?? 3.9;
    const r = Math.min(boxW / dim.w, boxH / dim.h);
    const w = dim.w * r, h = dim.h * r;
    s.addImage({ path: p, x: (W - w) / 2, y: o.y ?? 1.55, w, h });
    return h;
  }

  // --- 定型のスライド ------------------------------------------------
  titleSlide() {
    const sp = this.spec, s = this.dark();
    s.addText('コンピュータシステム通論', {
      x: 0.9, y: 2.0, w: 11, h: 0.5,
      fontFace: JA, fontSize: 17, color: C.dim, charSpacing: 2, margin: 0,
    });
    const t = `第${sp.no}回　${sp.title}`;
    const tsize = t.length > 15 ? 34 : (t.length > 12 ? 38 : 44);
    s.addText(t, {
      x: 0.9, y: 2.6, w: 11.6, h: 1.2,
      fontFace: JA, fontSize: tsize, bold: true, color: C.paper, margin: 0,
    });
    fit(t, 11.6, 1.2, tsize, `第${sp.no}回 表紙`);
    s.addText(sp.question, {
      x: 0.9, y: 4.05, w: 11.6, h: 0.6,
      fontFace: JA, fontSize: 18, color: C.accLight, margin: 0, lineSpacing: 26,
    });
    motif(this.pres, s, sp.no, 5.5);
    s.addText('九州大学', {
      x: 0.9, y: 6.4, w: 6, h: 0.3, fontFace: JA, fontSize: 12, color: C.dim, margin: 0,
    });
  }

  questionSlide() {
    const sp = this.spec, s = this.dark();
    s.addText('今回の問い', {
      x: 0.9, y: 1.5, w: 11, h: 0.4,
      fontFace: JA, fontSize: 14, color: C.accLight, bold: true, margin: 0,
    });
    s.addText(sp.bigQuestion || sp.question, {
      x: 0.9, y: 2.1, w: 11.6, h: 2.2,
      fontFace: JA, fontSize: 36, bold: true, color: C.paper, margin: 0, lineSpacing: 48,
    });
    if (sp.questionSub) {
      s.addText(sp.questionSub, {
        x: 0.9, y: 4.5, w: 11.6, h: 0.6,
        fontFace: JA, fontSize: 20, color: C.lightInk, margin: 0,
      });
    }
    s.addText('この90分で、この問いに答えを出す。', {
      x: 0.9, y: 5.4, w: 11, h: 0.4,
      fontFace: JA, fontSize: 14, color: C.dim, margin: 0,
    });
    motif(this.pres, s, sp.no);
  }

  goalsSlide() {
    const sp = this.spec;
    const s = this.content('到達目標', `第${sp.no}回`);
    const n = sp.goals.length;
    const gap = n <= 4 ? 1.15 : (n === 5 ? 0.94 : 0.8);
    sp.goals.forEach(([h, b], i) => {
      const y = 1.85 + i * gap;
      s.addShape(this.S.ellipse, {
        x: 0.85, y: y + 0.08, w: 0.5, h: 0.5,
        fill: { color: C.accT }, line: { color: C.acc, width: 1.2 },
      });
      s.addText(String(i + 1), {
        x: 0.85, y: y + 0.08, w: 0.5, h: 0.5,
        fontFace: JA, fontSize: 14, bold: true, color: C.acc,
        align: 'center', valign: 'middle', margin: 0,
      });
      s.addText([
        { text: h, options: { bold: true, color: C.ink, fontSize: n > 5 ? 15 : 16 } },
        { text: '　' + b, options: { color: C.mut, fontSize: n > 5 ? 13 : 14 } },
      ], { x: 1.55, y: y + 0.1, w: 10.9, h: 0.5, fontFace: JA, valign: 'middle', margin: 0 });
      fit(h + b, 10.9, 0.5, 15, `第${sp.no}回 到達目標 ${i + 1}`);
    });
  }

  sectionSlide(sec) {
    const s = this.dark();
    s.addText(sec.n, {
      x: 0.9, y: 2.4, w: 3, h: 0.9,
      fontFace: JA, fontSize: 56, bold: true, color: C.ghost, margin: 0,
    });
    s.addText(sec.name, {
      x: 0.9, y: 3.35, w: 11.6, h: 0.9,
      fontFace: JA, fontSize: 38, bold: true, color: C.paper, margin: 0,
    });
    fit(sec.name, 11.6, 0.9, 38, `第${this.spec.no}回 節 ${sec.n}`);
    if (sec.tagline) {
      s.addText(sec.tagline, {
        x: 0.9, y: 4.35, w: 11.6, h: 0.5,
        fontFace: JA, fontSize: 17, color: C.dim, margin: 0,
      });
    }
    motif(this.pres, s, this.spec.no);
  }

  exercisesSlide() {
    const sp = this.spec;
    if (!sp.exercises || !sp.exercises.length) return;
    const s = this.content('演習', `第${sp.no}回`);
    const n = sp.exercises.length;
    const gap = n <= 4 ? 1.18 : 0.95;
    sp.exercises.forEach(([num, t], i) => {
      const y = 1.85 + i * gap;
      s.addShape(this.S.roundRect, {
        x: M, y, w: 0.95, h: 0.44, rectRadius: 0.08,
        fill: { color: C.accT }, line: { color: C.acc, width: 1 },
      });
      s.addText(num, {
        x: M, y, w: 0.95, h: 0.44, fontFace: MONO, fontSize: 13, bold: true,
        color: C.acc, align: 'center', valign: 'middle', margin: 0,
      });
      s.addText(t, {
        x: 1.95, y: y - 0.02, w: 10.6, h: gap - 0.16, fontFace: JA, fontSize: 14,
        color: C.ink, valign: 'top', margin: 0, lineSpacing: 21,
      });
      fit(t, 10.6, gap - 0.16, 14, `第${sp.no}回 演習 ${num}`);
    });
  }

  summarySlide() {
    const sp = this.spec, s = this.dark();
    s.addText('まとめ', {
      x: 0.9, y: 0.7, w: 11, h: 0.6,
      fontFace: JA, fontSize: 30, bold: true, color: C.paper, margin: 0,
    });
    const n = sp.summary.length;
    const gap = n <= 5 ? 0.95 : (n === 6 ? 0.82 : 0.72);
    sp.summary.forEach(([h, b], i) => {
      const y = 1.55 + i * gap;
      s.addText(h, {
        x: 0.9, y, w: 3.6, h: 0.35, fontFace: JA, fontSize: n > 5 ? 14 : 15,
        bold: true, color: C.accLight, margin: 0,
      });
      s.addText(b, {
        x: 4.7, y: y - 0.04, w: 7.8, h: gap - 0.12, fontFace: JA,
        fontSize: n > 5 ? 12.5 : 13.5, color: C.lightInk, margin: 0, valign: 'top',
        lineSpacing: 19,
      });
      fit(b, 7.8, gap - 0.12, 13, `第${sp.no}回 まとめ「${h}」`);
    });
    if (sp.next) {
      s.addText('次回　' + sp.next, {
        x: 0.9, y: 6.55, w: 11.6, h: 0.4, fontFace: JA, fontSize: 13, color: C.dim, margin: 0,
      });
    }
  }

  // --- 本文のスライド ------------------------------------------------
  render(sl) {
    const kick = sl.kicker || '';
    switch (sl.kind) {
      case 'section': return this.sectionSlide(sl);
      case 'cards': return this.cards(sl, kick);
      case 'bullets': return this.bulletsSlide(sl, kick);
      case 'figure': return this.figureSlide(sl, kick);
      case 'table': return this.tableSlide(sl, kick);
      case 'code': return this.codeSlide(sl, kick);
      case 'split': return this.splitSlide(sl, kick);
      case 'statement': return this.statementSlide(sl, kick);
      case 'steps': return this.stepsSlide(sl, kick);
      default: throw new Error('不明な kind: ' + sl.kind);
    }
  }

  lead(s, sl) {
    let y = 1.62;
    if (sl.lead) {
      const long = sl.lead.length > 46;
      const lh = long ? 0.68 : 0.40;
      s.addText(sl.lead, {
        x: M, y, w: CW, h: lh, fontFace: JA, fontSize: 15, color: C.ink,
        margin: 0, lineSpacing: 22,
      });
      fit(sl.lead, CW, lh, 15, `第${this.spec.no}回 p${this.page} 導入`);
      y += lh + 0.04;
    }
    return y;
  }

  cards(sl, kick) {
    const s = this.content(sl.title, kick);
    let y = this.lead(s, sl);
    const items = sl.items;
    const per = sl.per || (items.length <= 4 ? 2 : 3);
    const rows = Math.ceil(items.length / per);
    const cw = (CW - (per - 1) * 0.25) / per;
    const chh = sl.cardH || (rows > 2 ? 1.25 : 1.5);
    items.forEach(([h, b], i) => {
      const x = M + (i % per) * (cw + 0.25);
      const yy = y + Math.floor(i / per) * (chh + 0.22);
      this.card(s, x, yy, cw, chh, h, b, sl.accent ? sl.accent.includes(i) : i < 0);
    });
    const bottom = y + rows * (chh + 0.22);
    if (sl.callout) {
      s.addShape(this.S.roundRect, {
        x: M, y: bottom + 0.1, w: CW, h: 0.86, rectRadius: 0.06,
        fill: { color: C.paper }, line: { color: C.acc, width: 1.5, dashType: 'dash' },
      });
      s.addText(sl.callout[0], {
        x: M + 0.25, y: bottom + 0.24, w: CW - 0.5, h: 0.32,
        fontFace: JA, fontSize: 15, bold: true, color: C.acc, margin: 0,
      });
      s.addText(sl.callout[1], {
        x: M + 0.25, y: bottom + 0.58, w: CW - 0.5, h: 0.32,
        fontFace: JA, fontSize: 12.5, color: C.mut, margin: 0,
      });
    }
    this.note(s, sl.note, sl.noteY || (sl.callout ? bottom + 1.15 : bottom + 0.2));
  }

  bulletsSlide(sl, kick) {
    const s = this.content(sl.title, kick);
    const y = this.lead(s, sl);
    const rows = sl.items.map((t, i) => {
      const [text, lvl] = Array.isArray(t) ? t : [t, 0];
      return {
        text,
        options: {
          bullet: true, indentLevel: lvl,
          breakLine: i !== sl.items.length - 1,
          fontSize: lvl ? 13.5 : 16,
          color: lvl ? C.mut : C.ink,
          paraSpaceAfter: lvl ? 5 : 10,
        },
      };
    });
    const noteY = sl.noteY || 6.3;
    s.addText(rows, {
      x: M + 0.15, y, w: CW - 0.3, h: Math.max(1.0, noteY - y - 0.2),
      fontFace: JA, valign: 'top', margin: 0,
    });
    this.note(s, sl.note, noteY);
  }

  figureSlide(sl, kick) {
    const s = this.content(sl.title, kick);
    const y = sl.lead ? this.lead(s, sl) : 1.5;
    const h = this.figure(s, sl.fig, { y, w: sl.w || 9.6, h: sl.h || (6.0 - y) });
    const capY = y + (h || 3.6) + 0.22;
    if (sl.caption) {
      s.addText(sl.caption, {
        x: M, y: capY, w: CW, h: 0.4, fontFace: JA, fontSize: 15,
        color: C.ink, align: 'center', margin: 0,
      });
    }
    if (sl.sub) {
      s.addText(sl.sub, {
        x: M, y: capY + 0.42, w: CW, h: 0.7, fontFace: JA, fontSize: 13,
        color: C.mut, align: 'center', margin: 0, lineSpacing: 20,
      });
    }
  }

  tableSlide(sl, kick) {
    const s = this.content(sl.title, kick);
    const y = this.lead(s, sl);
    this.table(s, sl.rows, { y, colW: sl.colW, size: sl.size, mono: sl.mono, rowH: sl.rowH });
    const bottom = y + (sl.rows.length) * (sl.rowH || 0.38) + 0.25;
    if (sl.callout) {
      s.addShape(this.S.roundRect, {
        x: M, y: bottom, w: CW, h: 0.72, rectRadius: 0.06,
        fill: { color: C.accT }, line: { color: C.acc, width: 1.5 },
      });
      s.addText(sl.callout, {
        x: M + 0.25, y: bottom + 0.16, w: CW - 0.5, h: 0.4,
        fontFace: JA, fontSize: 15, bold: true, color: C.acc, margin: 0,
      });
    }
    this.sub(s, sl.sub, bottom + (sl.callout ? 0.9 : 0.05));
    this.note(s, sl.note, sl.noteY || 6.4);
  }

  codeSlide(sl, kick) {
    const s = this.content(sl.title, kick);
    const y = this.lead(s, sl);
    const cw = sl.side ? 5.7 : CW;
    this.codeBox(s, sl.code, { x: M, y, w: cw, h: sl.codeH || 2.4, size: sl.size || 12.5 });
    if (sl.side) {
      const sx = M + cw + 0.4;
      s.addText(sl.side.title, {
        x: sx, y, w: CW - cw - 0.4, h: 0.3,
        fontFace: JA, fontSize: 14, bold: true, color: C.ink, margin: 0,
      });
      s.addText(sl.side.body, {
        x: sx, y: y + 0.4, w: CW - cw - 0.4, h: (sl.codeH || 2.4) - 0.4,
        fontFace: JA, fontSize: 13, color: C.mut, margin: 0, valign: 'top', lineSpacing: 20,
      });
      fit(sl.side.body, CW - cw - 0.4, (sl.codeH || 2.4) - 0.4, 13,
          `第${this.spec.no}回 p${this.page} 右段`);
    }
    this.sub(s, sl.sub, y + (sl.codeH || 2.4) + 0.3);
    this.note(s, sl.note, sl.noteY || 6.3);
  }

  splitSlide(sl, kick) {
    const s = this.content(sl.title, kick);
    const y = this.lead(s, sl);
    const cw = (CW - 0.5) / 2;
    [sl.left, sl.right].forEach((col, i) => {
      const x = M + i * (cw + 0.5);
      s.addText(col.title, {
        x, y, w: cw, h: 0.32, fontFace: JA, fontSize: 15, bold: true, color: C.ink, margin: 0,
      });
      let yy = y + 0.44;
      if (col.code) {
        this.codeBox(s, col.code, { x, y: yy, w: cw, h: col.codeH || 2.0, size: col.size || 12 });
        yy += (col.codeH || 2.0) + 0.25;
      }
      if (col.rows) {
        this.table(s, col.rows, { x, y: yy, w: cw, colW: col.colW, size: col.size || 12.5,
                                  mono: col.mono, rowH: col.rowH || 0.36 });
        yy += col.rows.length * (col.rowH || 0.36) + 0.2;
      }
      if (col.items) {
        s.addText(col.items.map((t, j) => ({
          text: t,
          options: { bullet: true, breakLine: j !== col.items.length - 1,
                     fontSize: 13.5, color: C.ink, paraSpaceAfter: 7 },
        })), { x: x + 0.12, y: yy, w: cw - 0.12, h: col.items.length * 0.42 + 0.15,
               fontFace: JA, valign: 'top', margin: 0 });
        yy += col.items.length * 0.42 + 0.25;
      }
      if (col.body) {
        s.addText(col.body, {
          x, y: yy, w: cw, h: 1.7, fontFace: JA, fontSize: 13, color: C.mut,
          margin: 0, valign: 'top', lineSpacing: 20,
        });
        fit(col.body, cw, 1.7, 13, `第${this.spec.no}回 p${this.page} ${i ? '右' : '左'}段`);
      }
      if (col.note) {
        s.addText(col.note, {
          x, y: yy + (col.body ? 1.78 : 0.1), w: cw, h: 0.35,
          fontFace: JA, fontSize: 13, bold: true, color: C.acc, margin: 0,
        });
      }
    });
    this.note(s, sl.note, sl.noteY || 6.4);
  }

  statementSlide(sl, kick) {
    const s = this.content(sl.title, kick);
    const y = this.lead(s, sl);
    s.addShape(this.S.roundRect, {
      x: M, y: y + 0.05, w: CW, h: 0.78, rectRadius: 0.06,
      fill: { color: C.accT }, line: { color: C.acc, width: 1.5 },
    });
    s.addText(sl.statement, {
      x: M + 0.25, y: y + 0.22, w: CW - 0.5, h: 0.44,
      fontFace: JA, fontSize: 17, bold: true, color: C.acc, margin: 0,
    });
    fit(sl.statement, CW - 0.5, 0.44, 17, `第${this.spec.no}回 p${this.page} 主張`);
    let yy = y + 1.1;
    (sl.map || []).forEach(([a, b]) => {
      s.addText(a, {
        x: 1.3, y: yy, w: 5.0, h: 0.5, fontFace: JA, fontSize: 15, color: C.ink,
        align: 'right', valign: 'middle', margin: 0,
      });
      s.addShape(this.S.rightArrow, {
        x: 6.5, y: yy + 0.14, w: 0.7, h: 0.22, fill: { color: C.acc },
      });
      s.addText(b, {
        x: 7.4, y: yy, w: 4.6, h: 0.5, fontFace: JA, fontSize: 16, bold: true,
        color: C.acc, valign: 'middle', margin: 0,
      });
      yy += 0.68;
    });
    this.sub(s, sl.sub, yy + 0.1);
    this.note(s, sl.note, sl.noteY || 6.3);
  }

  stepsSlide(sl, kick) {
    const s = this.content(sl.title, kick);
    const y = this.lead(s, sl);
    const n = sl.steps.length;
    const cw = (CW - (n - 1) * 0.2) / n;
    sl.steps.forEach(([h, b], i) => {
      const x = M + i * (cw + 0.2);
      s.addShape(this.S.roundRect, {
        x, y: y + 0.1, w: cw, h: sl.stepH || 1.7, rectRadius: 0.06,
        fill: { color: i === 0 ? C.accT : C.tint },
        line: { color: i === 0 ? C.acc : C.tint2, width: i === 0 ? 1.5 : 1 },
      });
      s.addText(String(i + 1), {
        x: x + 0.16, y: y + 0.24, w: 0.4, h: 0.28, fontFace: MONO, fontSize: 12,
        bold: true, color: C.acc, margin: 0,
      });
      s.addText(h, {
        x: x + 0.16, y: y + 0.56, w: cw - 0.32, h: 0.34, fontFace: JA, fontSize: 14,
        bold: true, color: C.ink, margin: 0,
      });
      fit(h, cw - 0.32, 0.34, 14, `第${this.spec.no}回 p${this.page} 手順${i + 1}見出し`);
      s.addText(b, {
        x: x + 0.16, y: y + 0.94, w: cw - 0.32, h: (sl.stepH || 1.7) - 0.9,
        fontFace: JA, fontSize: 12, color: C.mut, margin: 0, valign: 'top', lineSpacing: 16,
      });
      fit(b, cw - 0.32, (sl.stepH || 1.7) - 0.9, 12, `第${this.spec.no}回 p${this.page} 手順${i + 1}`);
      if (i < n - 1) {
        s.addShape(this.S.rightArrow, {
          x: x + cw + 0.02, y: y + 0.86, w: 0.16, h: 0.16, fill: { color: C.mut },
        });
      }
    });
    this.sub(s, sl.sub, y + (sl.stepH || 1.7) + 0.4);
    this.note(s, sl.note, sl.noteY || 6.3);
  }

  build() {
    const sp = this.spec;
    this.titleSlide();
    this.questionSlide();
    this.goalsSlide();
    sp.slides.forEach((sl) => this.render(sl));
    this.exercisesSlide();
    this.summarySlide();
    const name = `第${String(sp.no).padStart(2, '0')}回_${sp.title}.pptx`;
    const out = path.join(ROOT, 'slides', name);
    return this.pres.writeFile({ fileName: out }).then(() => ({ out, n: this.page }));
  }
}

// PNG の大きさ（IHDR から読む）
function pngSize(p) {
  const b = fs.readFileSync(p);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

module.exports = { Deck, C, JA, MONO, warnings, W, H, M, CW };
