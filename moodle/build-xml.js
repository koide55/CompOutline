#!/usr/bin/env node
// moodle/numeric.js の定義と lectures/*.md の設問文から、
// Moodle にインポートできる問題 XML を書き出す。
//
//   node moodle/build-xml.js
//   → moodle/数値問題.xml
//
// 解答欄が1個で数値なら numerical（数値問題）、
// それ以外は cloze（穴埋め問題）にする。Moodle の数値問題は
// 1問1答なので、複数の値を答える問題は穴埋めにするしかない。

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { questions } from './numeric.js';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

// ---------------------------------------------------------------- 設問文
// ノートの演習節から **N-M.** で始まる1問を取り出す。
function statement(id) {
  const lec = id.split('-')[0].padStart(2, '0');
  const file = fs.readdirSync(path.join(root, 'lectures'))
                 .find(f => f.startsWith(lec + '-'));
  if (!file) throw new Error(`第${lec}回のノートが見つからない`);
  const src = fs.readFileSync(path.join(root, 'lectures', file), 'utf8');
  const body = src.slice(src.indexOf('\n## 演習'));
  const head = `**${id}.**`;
  const from = body.indexOf(head);
  if (from < 0) throw new Error(`${id} がノートに無い`);
  const rest = body.slice(from + head.length);
  // 次の問題、または演習節の終わり（---）まで
  const end = rest.search(/\n\*\*\d+-\d+\.\*\*|\n---\n/);
  return rest.slice(0, end < 0 ? undefined : end).trim();
}

// ---------------------------------------------------------------- Markdown
const esc = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

function toHtml(md) {
  const paras = md.split(/\n\s*\n/).map(p => {
    // 字下げや (a) で始まる行は、行として残す
    const lines = p.split('\n').map(l => l.trimEnd());
    let html = '';
    lines.forEach((l, i) => {
      const keep = /^\s{2,}/.test(l) || /^\(?[a-c]\)/.test(l.trim());
      if (i > 0) html += keep ? '<br>' : '';
      html += esc(l.trim());
    });
    return '<p>' + html
      .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
      .replace(/`(.+?)`/g, '<code>$1</code>') + '</p>';
  });
  return paras.join('\n');
}

// ---------------------------------------------------------------- 解答欄
function cloze(b) {
  if (b.type === 'num') {
    const a = b.tol ? `${b.answer}:${b.tol}` : `${b.answer}:0`;
    return `{1:NUMERICAL:=${a}}`;
  }
  if (b.type === 'text') return `{1:SHORTANSWER:=${b.answer}}`;
  const alts = [`=${b.answer}`, ...b.others.map(o => `~${o}`)].join('');
  return `{1:MULTICHOICE:${alts}}`;
}

// この問題で答える範囲。指定があるものは残りを作文問題として別に出す
function partNote(q) {
  return q.part
    ? `<p><em>この問題では ${esc(q.part)} を答える。残りは別の作文問題で答えること。</em></p>`
    : '';
}

function answerBox(q) {
  const rows = q.blanks.map(b =>
    `<tr><td style="padding:4px 12px 4px 0">${esc(b.label)}</td>` +
    `<td style="padding:4px 0">${cloze(b)}${b.unit ? ' ' + esc(b.unit) : ''}</td></tr>`
  ).join('\n');
  return `${partNote(q)}<p><strong>解答欄</strong></p>\n<table>\n${rows}\n</table>`;
}

// ---------------------------------------------------------------- XML
const cdata = s => `<![CDATA[${s}]]>`;

function numericalXml(q, text) {
  const b = q.blanks[0];
  return `  <question type="numerical">
    <name><text>${q.id} ${q.name}</text></name>
    <questiontext format="html"><text>${cdata(text)}</text></questiontext>
    <defaultgrade>1.0000000</defaultgrade>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <answer fraction="100" format="moodle_auto_format">
      <text>${b.answer}</text>
      <tolerance>${b.tol}</tolerance>
      <feedback format="html"><text></text></feedback>
    </answer>
    <unitgradingtype>0</unitgradingtype>
    <unitpenalty>0.1000000</unitpenalty>
    <showunits>3</showunits>
    <unitsleft>0</unitsleft>
  </question>`;
}

function clozeXml(q, text) {
  return `  <question type="cloze">
    <name><text>${q.id} ${q.name}</text></name>
    <questiontext format="html"><text>${cdata(text)}</text></questiontext>
    <generalfeedback format="html"><text></text></generalfeedback>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
  </question>`;
}

const out = [];
out.push('<?xml version="1.0" encoding="UTF-8"?>');
out.push('<!-- コンピュータシステム通論 自動採点に載せる演習');
out.push('     moodle/build-xml.js が生成。手で直さないこと -->');
out.push('<quiz>');

let nNum = 0, nCloze = 0;
for (const q of questions) {
  const text = toHtml(statement(q.id)) + '\n' + answerBox(q);
  const single = q.blanks.length === 1 && q.blanks[0].type === 'num';
  if (single) { out.push(numericalXml(q, toHtml(statement(q.id)) + partNote(q))); nNum++; }
  else { out.push(clozeXml(q, text)); nCloze++; }
}
out.push('</quiz>');

const dest = path.join(root, 'moodle', '数値問題.xml');
fs.writeFileSync(dest, out.join('\n') + '\n');
const blanks = questions.reduce((s, q) => s + q.blanks.length, 0);
console.log(`${questions.length}問（数値問題 ${nNum} / 穴埋め問題 ${nCloze}）`);
console.log(`解答欄 ${blanks}個 = 満点 ${blanks}点`);
console.log(path.relative(root, dest));
