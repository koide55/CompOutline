#!/usr/bin/env python3
"""対話ログから、教員が見る所見を作る。

  python3 assessment/tools/dryrun.py assessment/samples/lec01-mid.json

学生に配る前に、所見が「読むに値するか」を先生自身で確かめるための道具。
本番では arena の中で同じことをするが、ここでは切り離して試せるようにしてある。

設計上の要点:
  - 点数は付けない。A / B / C の3段階と、根拠となる引用だけを出す。
  - **観点ごとに個別に呼ぶ。** 8観点を1回でまとめて書かせると、
    判定が甘くなり、字数制限も守られなかった（実測）。
  - 観点に questions が指定されていれば、その問だけを見て判定する。
  - 引用が学生の発言に実在するかを機械で検査する。
    実在しない引用は表示しない。教員の判断を誤らせるため。
"""
import argparse
import json
import os
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..')
OLLAMA = "http://127.0.0.1:11434/api/chat"
MODEL = os.environ.get("ASSESS_MODEL", "gemma4:latest")

SYS = ("あなたは大学の講義の採点補助です。指定された1観点だけを判定します。"
       "点数は付けません。A（十分）B（一部不足）C（不足）で示し、"
       "根拠を学生の発言からそのまま引用してください。"
       "引用は学生が書いた文字列を一字も変えずに写すこと。創作は禁止です。"
       "comment は50字以内の日本語1文で書いてください。2文以上書いてはいけません。"
       "学生を励ますことは目的ではありません。教員が見落としを防げるように、"
       "不足している点を具体的に書いてください。")

SCHEMA = {
    "type": "object",
    "properties": {
        "grade": {"type": "string", "enum": ["A", "B", "C"]},
        "quote": {"type": "string"},
        "comment": {"type": "string"},
    },
    "required": ["grade", "quote", "comment"],
}


def judge(item, turns, model, timeout=600):
    talk = "\n\n".join(f"問: {t['q']}\n答: {t['a']}" for t in turns)
    prompt = (f"観点: {item['label']}\n"
              f"判定基準: {item['description']}\n"
              f"十分と言える例: {item['excellent']}\n\n"
              f"対話:\n---\n{talk}\n---")
    payload = {
        "model": model, "stream": False, "think": False, "format": SCHEMA,
        "messages": [{"role": "system", "content": SYS},
                     {"role": "user", "content": prompt}],
        # 成績の参考資料にするので、同じ入力には必ず同じ所見が出るようにする
        "options": {"num_predict": 400, "temperature": 0.0, "seed": 42, "top_p": 1.0},
    }
    req = urllib.request.Request(OLLAMA, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read())
    return time.time() - t0, json.loads(d["message"]["content"])


def flags(transcript, results):
    """教員が必ず目を通すべきものを浮かせる。"""
    out = []
    answers = "".join(t["a"] for t in transcript["turns"])
    n = len(answers)
    if n < 300:
        out.append(f"回答が短い（{n}字）")
    if n > 4000:
        out.append(f"回答が長い（{n}字）")
    terms = ["チューリング", "停止問題", "決定不能", "対角線", "テーゼ", "万能", "アルゴリズム"]
    hit = sum(1 for t in terms if t in answers)
    if hit < 3:
        out.append(f"講義固有語が少ない（{hit}/{len(terms)}）")
    grades = [r["grade"] for _, r, _ in results]
    if "A" in grades and "C" in grades:
        out.append("観点により評価が割れている")
    if sum(1 for _, _, real in results if not real) >= 2:
        out.append("引用の裏取りができない観点が複数")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("transcript")
    ap.add_argument("--scenario")
    ap.add_argument("--model", default=MODEL)
    a = ap.parse_args()

    tr = json.load(open(a.transcript, encoding="utf-8"))
    sc_path = a.scenario or os.path.join(
        ROOT, "scenarios", tr["scenario_id"].split("_")[0] + ".json")
    sc = json.load(open(sc_path, encoding="utf-8"))

    answers = "\n".join(t["a"] for t in tr["turns"])
    results, total = [], 0.0
    for item in sc["rubric"]["items"]:
        idx = item.get("questions")
        turns = [tr["turns"][i - 1] for i in idx] if idx else tr["turns"]
        dt, r = judge(item, turns, a.model)
        total += dt
        # 引用は「学生の発言」に実在しなければならない。
        # 質問文を引用してくることがあるので、答だけと照合する。
        results.append((item, r, bool(r.get("quote")) and r["quote"] in answers))

    st = tr.get("student", {})
    print(f"\n{'=' * 74}")
    print(f" {sc['title']}")
    print(f" {st.get('id','')}  {st.get('name','')}"
          f"    （{a.model} / {total:.1f}秒 / 回答 {len(answers)}字）")
    print(f"{'=' * 74}")
    for item, r, real in results:
        scope = f"  ← 問{','.join(map(str, item['questions']))}" if item.get("questions") else ""
        print(f"\n  [{r['grade']}] {item['label']}{scope}")
        print(f"      {r['comment']}")
        print(f"      根拠「{r['quote'][:64]}」" if real
              else "      根拠なし（引用が実在しないため表示しない）")

    fl = flags(tr, results)
    print(f"\n{'-' * 74}")
    if fl:
        print(f"  要確認: {' / '.join(fl)}")
    else:
        print("  要確認: なし")
    print(f"{'-' * 74}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
