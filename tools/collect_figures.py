#!/usr/bin/env python3
"""講義ノートから図の仕様を集めて figures/INDEX.md を書き出す。

本文中の

    > **[図 1-2] タイトル**
    > 説明の続き…

という引用ブロックを拾う。図が実際に描かれているか（figures/fig-01-02.svg の有無）も
あわせて表示するので、作図の進捗表にもなる。
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEAD = re.compile(r'^>\s*\*\*\[図\s*(\d+)-(\d+)\]\s*(.+?)\*\*\s*$')


def collect():
    figs = []
    for md in sorted((ROOT / 'lectures').glob('*.md')):
        lines = md.read_text(encoding='utf-8').splitlines()
        for i, line in enumerate(lines):
            m = HEAD.match(line)
            if not m:
                continue
            body = []
            for cont in lines[i + 1:]:
                if not cont.startswith('>'):
                    break
                body.append(cont.lstrip('> ').rstrip())
            figs.append(dict(
                lecture=int(m.group(1)), num=int(m.group(2)), title=m.group(3),
                spec=' '.join(body), source=md.name,
            ))
    figs.sort(key=lambda f: (f['lecture'], f['num']))
    return figs


def main():
    figs = collect()
    out = ['# 図の一覧',
           '',
           '`tools/collect_figures.py` が生成する。直接編集しないこと。',
           '',
           f'全 {len(figs)} 図。「済」は `figures/fig-NN-MM.svg` が存在するもの。',
           '']
    cur = None
    for f in figs:
        if f['lecture'] != cur:
            cur = f['lecture']
            out += ['', f'## 第{cur}回', '', '| 図 | 状態 | タイトル | 仕様 |',
                    '| --- | --- | --- | --- |']
        name = f"fig-{f['lecture']:02d}-{f['num']:02d}.svg"
        done = '済' if (ROOT / 'figures' / name).exists() else '—'
        spec = f['spec'].replace('|', '\\|')
        out.append(f"| {f['lecture']}-{f['num']} | {done} | {f['title']} | {spec} |")
    (ROOT / 'figures' / 'INDEX.md').write_text('\n'.join(out) + '\n', encoding='utf-8')
    print(f'figures/INDEX.md に {len(figs)} 図を書き出した')
    return 0


if __name__ == '__main__':
    sys.exit(main())
