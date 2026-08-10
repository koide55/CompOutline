#!/usr/bin/env python3
"""全13回のシナリオを書き出す。

  python3 assessment/tools/build.py        # 全部
  python3 assessment/tools/build.py 1 5    # 第1回と第5回だけ
"""
import importlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, 'lectures'))

from kit import build  # noqa: E402

OUT = os.path.join(ROOT, 'scenarios')


def main():
    want = [int(v) for v in sys.argv[1:]]
    nums = want or list(range(1, 14))
    os.makedirs(OUT, exist_ok=True)
    n = 0
    for i in nums:
        try:
            mod = importlib.import_module(f'lec{i:02d}')
        except ModuleNotFoundError:
            print(f'第{i}回: 未作成')
            continue
        sc = build(mod.spec)
        path = os.path.join(OUT, f'lec{i:02d}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(sc, f, ensure_ascii=False, indent=2)
            f.write('\n')
        scoped = sum(1 for it in sc['rubric']['items'] if 'questions' in it)
        print(f"第{i:2d}回  {sc['title'][:28]:30s} "
              f"{len(sc['question_plan'])}問  範囲指定 {scoped}/8観点")
        n += 1
    print(f'\n{n} 本を {os.path.relpath(OUT)} に書き出した')


if __name__ == '__main__':
    main()
