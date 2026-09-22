#!/usr/bin/env node
// 演習102問を、Moodle にインポートできる問題 XML に変換する。
//
//   node moodle/build-xml.js
//   → moodle/xml/第01回_計算とは何か.xml  …  第13回まで（回ごとの小テスト用）
//   → moodle/xml/全13回.xml                （まとめて1本）
//
// 設問の文章は lectures/*.md から抜き出す（単一ソース）。
// 文面を直すのはノート側だけでよい。
//   moodle/numeric.js  自動採点にする問題の解答欄・正解・許容誤差
//   moodle/essay.js    作文問題の解答形式・添付・分割
//
// 解答欄が1個で数値なら numerical（数値問題）、複数なら cloze（穴埋め問題）、
// それ以外は essay（作文問題）にする。

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { questions as autoGraded } from './numeric.js';
import { monospaced, attachments, halves, names } from './essay.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const COURSE = 'コンピュータシステム通論';

// ---------------------------------------------------------------- ノートを読む
// 各回の 演習節から、**N-M.** ごとの設問を切り出す。
function readLectures() {
  return fs.readdirSync(path.join(root, 'lectures'))
    .filter(f => /^\d\d-.*\.md$/.test(f))
    .sort()
    .map(f => {
      const src = fs.readFileSync(path.join(root, 'lectures', f), 'utf8');
      const title = src.match(/^# (.+)$/m)[1];          // 「第1回 計算とは何か」
      const no = Number(title.match(/第(\d+)回/)[1]);
      let body = src.slice(src.indexOf('\n## 演習'));
      body = body.slice(0, body.indexOf('\n## まとめ'));
      const parts = body.split(/^\*\*(\d+-\d+)\.\*\*/m).slice(1);
      const items = [];
      for (let i = 0; i < parts.length; i += 2) {
        items.push({ id: parts[i], md: parts[i + 1].trim() });
      }
      return { no, title, name: title.replace(/^第\d+回\s*/, ''), items };
    });
}

// ---------------------------------------------------------------- Markdown
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const inline = s => esc(s)
  .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  .replace(/`(.+?)`/g, '<code>$1</code>');

function table(lines) {
  // | a | b |  の行が並んだもの。2行目は区切りなので捨てる
  const cells = l => l.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
  const head = cells(lines[0]);
  const rows = lines.slice(2).map(cells);
  const th = head.map(c => `<th style="padding:4px 10px;border:1px solid #ccc">${inline(c)}</th>`);
  const tr = rows.map(r =>
    '<tr>' + r.map(c => `<td style="padding:4px 10px;border:1px solid #ccc">${inline(c)}</td>`).join('') + '</tr>');
  return `<table style="border-collapse:collapse;margin:8px 0">\n<tr>${th.join('')}</tr>\n${tr.join('\n')}\n</table>`;
}

function toHtml(md) {
  const out = [];
  const lines = md.split('\n');
  let i = 0;
  while (i < lines.length) {
    const l = lines[i];
    if (l.trim().startsWith('```')) {                    // コードブロック
      const buf = [];
      for (i++; i < lines.length && !lines[i].trim().startsWith('```'); i++) buf.push(lines[i]);
      i++;
      out.push(`<pre style="font-family:monospace">${esc(buf.join('\n'))}</pre>`);
    } else if (/^\s*\|/.test(l)) {                       // 表
      const buf = [];
      for (; i < lines.length && /^\s*\|/.test(lines[i]); i++) buf.push(lines[i]);
      out.push(table(buf));
    } else if (/^- /.test(l.trim())) {                   // 箇条書き
      const buf = [];
      for (; i < lines.length; i++) {
        const t = lines[i].trim();
        if (/^- /.test(t)) buf.push(inline(t.slice(2)));
        else if (t && buf.length) buf[buf.length - 1] += ' ' + inline(t);   // 折り返し
        else break;
      }
      out.push('<ul>' + buf.map(b => `<li>${b}</li>`).join('') + '</ul>');
    } else if (!l.trim()) {
      i++;
    } else {                                             // 段落
      const buf = [];
      for (; i < lines.length; i++) {
        const t = lines[i];
        if (!t.trim() || t.trim().startsWith('```') || /^\s*\|/.test(t) || /^- /.test(t.trim())) break;
        // 字下げ行と (a) で始まる行は、行として残す
        const keep = buf.length && (/^\s{2,}/.test(t) || /^\(?[a-z]\)/.test(t.trim()));
        buf.push((keep ? '<br>' : buf.length ? '' : '') + inline(t.trim()));
      }
      out.push('<p>' + buf.join('') + '</p>');
    }
  }
  return out.join('\n');
}

// 問題名。moodle/essay.js の names を使う。
// 抜けていたら設問の頭で間に合わせ、最後に警告する（途中で切れて読めないので）
const unnamed = [];
function nameOf(id, md) {
  if (names[id]) return `${id} ${names[id]}`;
  unnamed.push(id);
  const head = md.replace(/```[\s\S]*?```/g, '').replace(/^\s*\|.*$/gm, '')
    .replace(/[*`]/g, '').replace(/\s+/g, ' ').trim();
  return `${id} ${head.split(/[。、（]/)[0].slice(0, 28)}`;
}

// ---------------------------------------------------------------- 解答欄
function cloze(b) {
  if (b.type === 'num') return `{1:NUMERICAL:=${b.answer}:${b.tol}}`;
  if (b.type === 'text') return `{1:SHORTANSWER:=${b.answer}}`;
  return `{1:MULTICHOICE:${[`=${b.answer}`, ...b.others.map(o => `~${o}`)].join('')}}`;
}

const partNote = part => part
  ? `<p><em>この問題では ${esc(part)} を答える。残りは別の問題で答えること。</em></p>` : '';

function answerBox(q) {
  const rows = q.blanks.map(b =>
    `<tr><td style="padding:4px 12px 4px 0">${esc(b.label)}</td>` +
    `<td style="padding:4px 0">${cloze(b)}${b.unit ? ' ' + esc(b.unit) : ''}</td></tr>`).join('\n');
  return `${partNote(q.part)}<p><strong>解答欄</strong></p>\n<table>\n${rows}\n</table>`;
}

// ---------------------------------------------------------------- XML
const cdata = s => `<![CDATA[${s}]]>`;
const el = (tag, body) => `<${tag} format="html"><text>${body ? cdata(body) : ''}</text></${tag}>`;

function categoryXml(cat) {
  return `  <question type="category">
    <category><text>$course$/top/${cat}</text></category>
    <info format="html"><text></text></info>
  </question>`;
}

function numericalXml(name, text, b) {
  return `  <question type="numerical">
    <name><text>${esc(name)}</text></name>
    ${el('questiontext', text)}
    ${el('generalfeedback')}
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <answer fraction="100" format="moodle_auto_format">
      <text>${b.answer}</text>
      <tolerance>${b.tol}</tolerance>
      ${el('feedback')}
    </answer>
    <unitgradingtype>0</unitgradingtype>
    <unitpenalty>0.1000000</unitpenalty>
    <showunits>3</showunits>
    <unitsleft>0</unitsleft>
  </question>`;
}

function clozeXml(name, text) {
  return `  <question type="cloze">
    <name><text>${esc(name)}</text></name>
    ${el('questiontext', text)}
    ${el('generalfeedback')}
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
  </question>`;
}

function essayXml(name, text, { format = 'editor', files = 0 } = {}) {
  return `  <question type="essay">
    <name><text>${esc(name)}</text></name>
    ${el('questiontext', text)}
    ${el('generalfeedback')}
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.0000000</penalty>
    <hidden>0</hidden>
    <responseformat>${format}</responseformat>
    <responserequired>1</responserequired>
    <responsefieldlines>12</responsefieldlines>
    <minwordlimit></minwordlimit>
    <maxwordlimit></maxwordlimit>
    <attachments>${files}</attachments>
    <attachmentsrequired>0</attachmentsrequired>
    <maxbytes>0</maxbytes>
    <filetypeslist></filetypeslist>
    ${el('graderinfo')}
    ${el('responsetemplate')}
  </question>`;
}

// ---------------------------------------------------------------- 組み立て
const autoById = new Map(autoGraded.map(q => [q.id, q]));
const halfById = new Map(halves.map(h => [h.id, h]));
const monoSet = new Set(monospaced);

function buildLecture(lec) {
  const cat = `${COURSE}/第${String(lec.no).padStart(2, '0')}回 ${lec.name}`;
  const out = [categoryXml(cat)];
  const tally = { numerical: 0, cloze: 0, essay: 0, grade: 0 };

  for (const it of lec.items) {
    const html = toHtml(it.md);
    const auto = autoById.get(it.id);

    if (auto) {
      const name = `${it.id} ${auto.name}`;
      if (auto.blanks.length === 1 && auto.blanks[0].type === 'num') {
        out.push(numericalXml(name, html + partNote(auto.part), auto.blanks[0]));
        tally.numerical++; tally.grade += 1;
      } else {
        out.push(clozeXml(name, html + '\n' + answerBox(auto)));
        tally.cloze++; tally.grade += auto.blanks.length;
      }
    }

    // 作文として残る側。分割された問題は auto と両方が出る
    const half = halfById.get(it.id);
    if (!auto || half) {
      const name = half ? `${it.id} ${half.name}` : nameOf(it.id, it.md);
      const text = html + (half ? partNote(half.part) : '');
      const format = half?.format || (monoSet.has(it.id) ? 'monospaced' : 'editor');
      out.push(essayXml(name, text, { format, files: attachments[it.id] || 0 }));
      tally.essay++; tally.grade += 1;
    }
  }
  return { cat, xml: out, tally };
}

const wrap = body => ['<?xml version="1.0" encoding="UTF-8"?>',
  `<!-- ${COURSE} 演習`,
  '     moodle/build-xml.js が生成。手で直さないこと -->',
  '<quiz>', ...body, '</quiz>', ''].join('\n');

const dir = path.join(root, 'moodle', 'xml');
fs.rmSync(dir, { recursive: true, force: true });
fs.mkdirSync(dir, { recursive: true });

const all = [];
const perLecture = [];
const total = { numerical: 0, cloze: 0, essay: 0, grade: 0, items: 0 };
for (const lec of readLectures()) {
  const { xml, tally } = buildLecture(lec);
  const file = `第${String(lec.no).padStart(2, '0')}回_${lec.name}.xml`;
  fs.writeFileSync(path.join(dir, file), wrap(xml));
  all.push(...xml);
  for (const k of ['numerical', 'cloze', 'essay', 'grade']) total[k] += tally[k];
  total.items += lec.items.length;
  const n = tally.numerical + tally.cloze + tally.essay;
  perLecture.push({ no: lec.no, n, ...tally });
  console.log(`第${String(lec.no).padStart(2, '0')}回  演習${String(lec.items.length).padStart(2)}問 → ${String(n).padStart(2)}問  ${tally.grade}点  ${file}`);
}
fs.writeFileSync(path.join(dir, '全13回.xml'), wrap(all));

const n = total.numerical + total.cloze + total.essay;
console.log(`\n演習 ${total.items}問 → Moodle ${n}問`);
console.log(`  数値問題 ${total.numerical} / 穴埋め問題 ${total.cloze} / 作文問題 ${total.essay}`);
console.log(`  満点 ${total.grade}点（自動採点 ${total.grade - total.essay}点・手採点 ${total.essay}点）`);
console.log(`moodle/xml/ に ${fs.readdirSync(dir).length} ファイル`);
// 最大評点を各回 MAX に揃えたときの換算。小テスト側の設定なので XML には入らない
const MAX = 10;
console.log(`\n小テストの最大評点を各回 ${MAX} 点に揃えたときの換算`);
console.log('（最大評点は小テスト（活動）の設定で、問題バンクの XML には入らない。');
console.log(' Moodle で 小テスト → 設定 → 評点 → 最大評点 に手で入れること）');
console.log('\n  回  素点  自動  手採点   係数  素点1点の価値  自動の比率');
for (const l of perLecture) {
  const f = MAX / l.grade;
  const auto = l.grade - l.essay;
  console.log(`  ${String(l.no).padStart(2)}  ${String(l.grade).padStart(4)}  ${String(auto).padStart(4)}  ${String(l.essay).padStart(6)}  ${f.toFixed(3).padStart(5)}  ${(f).toFixed(3).padStart(11)}点  ${String(Math.round(auto / l.grade * 100)).padStart(8)}%`);
}

if (unnamed.length) {
  console.log(`\n警告: moodle/essay.js の names に無い問題 ${unnamed.length}件 — ${unnamed.join(', ')}`);
  console.log('設問の頭で間に合わせたので、問題バンクの一覧で途中で切れて読めない');
}
