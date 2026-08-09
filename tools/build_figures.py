#!/usr/bin/env python3
"""図をすべて描き出す。

    python3 tools/build_figures.py            # 全部
    python3 tools/build_figures.py 05 09      # 第5回と第9回だけ
"""
import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, 'figs'))

MODULES = ['lec01_04', 'lec05_08', 'lec09_11', 'lec12_13']


def all_figures():
    out = {}
    for m in MODULES:
        try:
            mod = importlib.import_module(f'figs.{m}')
        except ModuleNotFoundError:
            continue
        out.update(mod.FIGURES)
    return dict(sorted(out.items()))


def main():
    want = sys.argv[1:]
    figs = all_figures()
    os.makedirs(os.path.join(ROOT, 'figures'), exist_ok=True)
    n = 0
    for key, fn in figs.items():
        if want and key.split('-')[0] not in want:
            continue
        path = os.path.join(ROOT, 'figures', f'fig-{key}.svg')
        fn().save(path)
        n += 1
    print(f'{n} 図を figures/ に書き出した（定義は全 {len(figs)} 図）')


if __name__ == '__main__':
    main()
