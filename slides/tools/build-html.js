#!/usr/bin/env node
// HTML スライドを組む。  node slides/tools/build-html.js [回番号 …]
//
// 入力は decks/lecNN.js。pptx を組む build.js とまったく同じデータを読む。
const path = require('path');
const fs = require('fs');
const { Deck } = require('./kit-html');

const ROOT = path.join(__dirname, '..', '..');
const OUT = path.join(ROOT, 'slides', 'html');

const want = process.argv.slice(2).map((v) => parseInt(v, 10)).filter(Number.isFinite);
const nums = want.length ? want : Array.from({ length: 13 }, (_, i) => i + 1);

fs.mkdirSync(OUT, { recursive: true });

let missingAll = [];
for (const n of nums) {
  const f = path.join(ROOT, 'slides', 'decks', `lec${String(n).padStart(2, '0')}.js`);
  let spec;
  try {
    spec = require(f);
  } catch (e) {
    if (e.code === 'MODULE_NOT_FOUND') { console.log(`第${n}回: 未作成`); continue; }
    throw e;
  }
  const { html, n: pages, missing } = new Deck(spec).build();
  const name = `第${String(n).padStart(2, '0')}回_${spec.title}.html`;
  const out = path.join(OUT, name);
  fs.writeFileSync(out, html, 'utf8');
  const kb = (Buffer.byteLength(html) / 1024).toFixed(0);
  console.log(`第${n}回  ${pages} 枚  ${kb} KB  ${name}`);
  missingAll = missingAll.concat(missing);
}

if (missingAll.length) {
  console.log(`\n--- 図が見つからない ${missingAll.length} 件 ---`);
  [...new Set(missingAll)].forEach((m) => console.log('  fig-' + m + '.svg'));
} else {
  console.log('\n図はすべて埋め込んだ');
}
console.log('組版の溢れはブラウザで開いて C キー（実際に描いた結果を測る）');
