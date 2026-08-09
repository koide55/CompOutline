#!/usr/bin/env node
// スライドを組む。  node slides/tools/build.js [回番号 …]
const path = require('path');
const { Deck, warnings } = require('./kit');

const want = process.argv.slice(2).map((v) => parseInt(v, 10));
const nums = want.length ? want : Array.from({ length: 13 }, (_, i) => i + 1);

(async () => {
  for (const n of nums) {
    const f = path.join(__dirname, '..', 'decks', `lec${String(n).padStart(2, '0')}.js`);
    let spec;
    try { spec = require(f); } catch (e) {
      if (e.code === 'MODULE_NOT_FOUND') { console.log(`第${n}回: 未作成`); continue; }
      throw e;
    }
    const { out, n: pages } = await new Deck(spec).build();
    console.log(`第${n}回  ${pages} 枚  ${path.basename(out)}`);
  }
  if (warnings.length) {
    console.log(`\n--- 溢れの疑い ${warnings.length} 件 ---`);
    warnings.forEach((w) => console.log('  ' + w));
  } else {
    console.log('\n溢れの疑いなし');
  }
})();
