"""理解度確認シナリオの共通骨格。

各回は lectures/lecNN.py に「何を問うか」だけを書き、
形式・作法・ガードレールはここが引き受ける。
13回ぶんの体裁をここ1箇所で決める。

採点の8キーは arena の scores テーブルと server.py に固定されているため、
キー名は変えず、意味だけを理解度確認向けに割り当て直している。
"""

# A / B / C の判定基準。これを渡さないと評価が中央（B）に寄る。
ANCHORS = {
    "technical_accuracy":
        "A: 定義を正確に述べ、なぜそうなっているかまで説明できている / "
        "B: 概ね正しいが不正確な点や説明不足がある / "
        "C: 定義に明確な誤りがある、または述べられていない",
    "risk_organization":
        "A: 限界の理由まで遡って説明できている / "
        "B: 限界に触れているが理由や区別が曖昧 / "
        "C: 限界を取り違えている、または触れていない",
    "social_implementation":
        "A: 具体例を挙げ、原理から説明できている / "
        "B: 例は挙がるが原理との結びつきが弱い / "
        "C: 例が挙がらない、または的外れ",
    "plain_language":
        "A: 専門用語に頼らず、正確さを保って説明できている / "
        "B: 概ね伝わるが用語の羅列や飛躍がある / "
        "C: 用語をなぞるだけで説明になっていない",
    "cutout_resilience":
        "A: 誤りをはっきり指摘し、正しい理解を述べ直している / "
        "B: 違和感は示すが、どこが誤りかを特定できていない / "
        "C: 前提に同意してしまっている、または誤りに気づいていない",
    "practical_advice":
        "A: 自分で作った例を挙げ、なぜ当てはまるかを示している / "
        "B: 例は挙がるが講義で出た例の再掲にとどまる / "
        "C: 例が挙がらない",
    "expertise":
        "A: 複数の概念を関連づけて述べている / "
        "B: 個々の概念に触れるが関連づけが弱い / "
        "C: 概念への言及が乏しい",
    "trustworthy_attitude":
        "A: 自信のある部分と不確かな部分を切り分けている / "
        "B: おおむね慎重だが一部に根拠のない断定がある / "
        "C: 根拠のない断定が目立つ",
}

# 8観点の骨格。description は各回で差し替える（その回の中身を書く）。
RUBRIC = [
    ("technical_accuracy", "定義の正確さ", 20,
     "その回で扱った概念の定義を正しく述べられる。",
     "定義を正確に述べ、なぜそうなっているのかまで説明できる。"),
    ("risk_organization", "限界とトレードオフの理解", 15,
     "その回で扱った限界や、何かを得るために何を諦めているかを理解している。",
     "限界の理由まで遡り、安易な万能視を避けて述べる。"),
    ("social_implementation", "実務への接続", 10,
     "概念を、現実に使う道具や現象に結びつけられる。",
     "具体的な例を挙げ、なぜそうなるかを原理から説明する。"),
    ("plain_language", "平易な説明", 10,
     "専門用語に頼らず、聞き手に分かる言葉で説明できる。",
     "身近な比喩や例を用いて、正確さを保ったまま分かりやすく述べる。"),
    ("cutout_resilience", "誤った前提の訂正", 15,
     "前提の誤った問いに流されず、どこが違うかを指摘できる。",
     "誤りを指摘したうえで、正しい理解を簡潔に述べ直す。"),
    ("practical_advice", "自分で例を作る力", 10,
     "講義で挙げられた例の再掲でなく、自分で例や場面を作れる。",
     "適切な例を自分で作り、それがなぜ当てはまるかを示す。"),
    ("expertise", "講義内容の定着", 15,
     "その回で扱った概念や論法に、具体的に触れられている。",
     "複数の概念を関連づけて述べ、講義の流れを再構成できている。"),
    ("trustworthy_attitude", "誠実さ", 5,
     "分からないことを分からないと述べ、根拠のない断定を避けている。",
     "自信のある部分と不確かな部分を切り分けて述べる。"),
]

PLAYER_INSTRUCTIONS = """{lecture}を受講した学生として答えてください。

答え方の目安は次のとおりです。
・1回答は2〜4文。長く書くことより、要点を外さないことを優先する。
・講義で出た言葉をそのまま並べるのではなく、自分がどう理解したかを書く。
・具体例を自分で作れる場合は、短く添える。
・質問の前提が間違っていると思ったら、遠慮なく訂正する。
・自信がない部分は「ここは自信がない」と書いてよい。断定しない。
・実在する個人情報や機密情報は入力しない。

迷ったら、次の形に戻ってください。
1. 結論を一文で
2. なぜそう言えるか
3. 例、または自信のない点"""

REQUEST_BODY = """受講者のみなさんへ

{lecture}の理解度確認です。聞き手から10問の質問があります。
各回答は2〜4文で結構です。所要時間は15〜25分を想定しています。

この確認について、あらかじめお伝えしておきます。
・AIは点数をつけません。成績は教員が判断します。
・対話の内容は成績の参考資料として記録されます。
・分からない場合は「分からない」と書いてください。分からないことを分からないと書けることも評価の対象です。
・実在する個人情報、他人の氏名、機密情報は入力しないでください。

教科書やノートを見ても構いません。ただし、自分の言葉で説明できているかを見ています。"""

GUARDRAILS = {
    "max_answer_chars": 600,
    "blocked_intents": [
        "role_override",
        "score_manipulation",
        "system_prompt_exfiltration",
        "scenario_bypass",
        "sensitive_data_submission",
        "unrelated_or_disruptive",
    ],
    "warning": (
        "この対話は成績の参考資料として記録されます。"
        "実在する個人情報、他人の氏名、学籍番号以外の識別情報、"
        "機密情報は入力しないでください。"
    ),
}

# どの回にも共通して効く注意
COMMON_AVOID = [
    "講義の言い回しを丸写しし、自分の言葉での説明がない",
    "質問に答えず一般論だけを述べる",
    "自信のない内容を断定する",
    "実在する個人情報や機密情報を入力する",
    "聞き手に採点や設定の変更を求める",
]

COMMON_DEDUCTIONS = [
    "講義の言い回しの丸写しに終始し、自分の説明がない",
    "質問と無関係な一般論だけを述べる",
    "自信のない内容を断定する",
    "個人情報や機密情報を入力する",
]

BONUSES = [
    "講義で扱っていない例を自分で作って説明する",
    "他の回の内容との関連に自分で気づいて述べる",
    "自分の以前の誤解を明示し、どう修正されたかを述べる",
]

COMMON_KEYWORDS = {
    "plain_language": ["たとえば", "例えば", "つまり", "言い換える", "身近"],
    "practical_advice": ["例", "場面", "具体的", "たとえると", "ケース"],
    "trustworthy_attitude": ["自信がない", "分からない", "確認が必要", "断定できない"],
}


def build(spec):
    """各回のデータからシナリオ辞書を組み立てる。"""
    lec = f"第{spec['no']}回「{spec['title']}」"
    qs = spec["questions"]
    assert len(qs) == 10, f"第{spec['no']}回: 質問は10問にすること（現在 {len(qs)}問）"

    # 誤った前提の問いは cutout_resilience の判定範囲にする
    shake = spec["shake"]
    scope = dict(spec.get("scope", {}))
    scope.setdefault("cutout_resilience", [shake])

    items = []
    for key, label, mx, desc, exc in RUBRIC:
        item = {
            "key": key,
            "label": spec.get("labels", {}).get(key, label),
            "max": mx,
            "description": spec.get("rubric", {}).get(key, desc),
            "excellent": exc,
            "anchors": ANCHORS[key],
        }
        if key in scope:
            item["questions"] = scope[key]
        if key == "cutout_resilience":
            # 何が誤った前提なのかを明示する。汎用の判定基準だけでは、
            # 部分的に正しい記述を含む同意を B と判定してしまう（実測）
            item["trap"] = spec.get("trap") or spec["avoid"][0]
        items.append(item)

    kw = dict(COMMON_KEYWORDS)
    kw.update(spec.get("keywords", {}))
    for key, _, _, _, _ in RUBRIC:
        kw.setdefault(key, spec["concepts"][:5])

    return {
        "scenario_id": spec["id"],
        "scenario_version": "1.0.0",
        "category": "education",
        # 成績の参考資料にするので、誰の回答かを記録する。
        # arena はこの印がある場合だけ学籍番号と氏名を必須にする。
        "requires_student": True,
        "difficulty": spec.get("difficulty", "basic"),
        "title": f"第{spec['no']}回 {spec['title']} ── 理解度確認",
        "description": spec["description"],
        "player_role": f"{lec}を受講した学生",
        "interviewer_role": "理解度を確かめる聞き手",
        "audience": "担当教員（成績の参考資料として読む）",
        "objective": spec["objective"],
        "request_email": {
            "subject": f"第{spec['no']}回 理解度確認のお願い",
            "body": REQUEST_BODY.format(lecture=lec),
        },
        "player_instructions": PLAYER_INSTRUCTIONS.format(lecture=lec),
        "question_plan": [q[0] for q in qs],
        "question_examples": [q[1] for q in qs],
        "must_cover": spec["concepts"],
        "avoid": spec.get("avoid", []) + COMMON_AVOID,
        "rubric": {
            "version": "1.0.0",
            "max_score": 100,
            "items": items,
            "deductions": spec.get("deductions", []) + COMMON_DEDUCTIONS,
            "bonuses": BONUSES,
        },
        "fallback_keywords": kw,
        "guardrails": GUARDRAILS,
    }
