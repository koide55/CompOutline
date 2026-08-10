#!/usr/bin/env python3
"""シナリオを機械的に検査する。13本を目で見るのは現実的でないため。"""
import glob
import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
KEYS = ["technical_accuracy", "risk_organization", "social_implementation",
        "plain_language", "cutout_resilience", "practical_advice",
        "expertise", "trustworthy_attitude"]

bad = 0
for p in sorted(glob.glob(os.path.join(ROOT, 'scenarios', '*.json'))):
    name = os.path.basename(p)
    d = json.load(open(p, encoding='utf-8'))
    e = []
    nq = len(d['question_plan'])
    if nq != 10:
        e.append(f'質問が{nq}問')
    if len(d['question_examples']) != nq:
        e.append('質問と例文の数が合わない')
    keys = [i['key'] for i in d['rubric']['items']]
    if keys != KEYS:
        e.append(f'採点キーが arena と合わない: {keys}')
    total = sum(i['max'] for i in d['rubric']['items'])
    if total != d['rubric']['max_score']:
        e.append(f'配点合計 {total} が max_score と不一致')
    for it in d['rubric']['items']:
        for q in it.get('questions', []):
            if not 1 <= q <= nq:
                e.append(f"{it['key']} の範囲指定 {q} が問の範囲外")
    # 揺さぶりの問が cutout_resilience の範囲になっているか
    cut = next(i for i in d['rubric']['items'] if i['key'] == 'cutout_resilience')
    if 'questions' not in cut:
        e.append('cutout_resilience に範囲指定がない')
    else:
        idx = cut['questions'][0]
        if '前提の確認' not in d['question_plan'][idx - 1]:
            e.append(f'cutout_resilience の指す問{idx}が揺さぶりでない')
    if not d['must_cover']:
        e.append('must_cover が空')
    for k in KEYS:
        if k not in d['fallback_keywords']:
            e.append(f'fallback_keywords に {k} がない')
    ids = d['scenario_id']
    if not ids.startswith(f"lec{name[3:5]}"):
        e.append(f'scenario_id とファイル名が対応しない: {ids}')

    if e:
        bad += 1
        print(f'✗ {name}')
        for x in e:
            print(f'    {x}')
    else:
        print(f'✓ {name}  {nq}問 / 配点{total} / 揺さぶり=問{cut["questions"][0]}')

print(f'\n{"問題なし" if not bad else f"{bad} 本に問題あり"}')
sys.exit(1 if bad else 0)
