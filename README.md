# コンピュータシステム通論 (An Outline of Computer System)

九州大学 学部講義「コンピュータシステム通論」の講義スライドを管理するリポジトリ。

- 講義言語: 日本語スライドと英語スライドを交互に配置（1トピック＝日英2枚）
- 現行版: `CompOutline2024.pptx`（663枚 / 24セクション）

## リポジトリの状態

現在は **調査フェーズ** です。スライド本体（`.pptx`）はまだコミットしていません。
理由は [docs/findings.md](docs/findings.md) の「配布・公開上の制約」を参照。

| パス | 内容 |
| --- | --- |
| `docs/inventory.md` | 全663枚のセクション別タイトル一覧（自動生成） |
| `docs/findings.md` | 内容の調査結果と更新候補のリスト |
| `tools/dump_pptx.py` | `.pptx` から構成・本文・ノートを JSON に抽出 |
| `slides/` | 軽量化・分割後のスライド置き場（未着手） |

## 使い方

構成と本文の抽出:

```bash
python3 tools/dump_pptx.py CompOutline2024.pptx out.json
```

`ppt/presentation.xml` の `sldIdLst` 順にスライドを走査し、PowerPoint のセクション、
タイトル・本文テキスト・ノートを JSON にまとめる。標準ライブラリのみで動作する。

## 公開前チェック

このリポジトリを GitHub Public にする前に、必ず以下を確認すること。

- [ ] 100MB を超えるファイルが履歴に入っていないこと（`git log --stat` / `git count-objects -vH`）
- [ ] 第三者著作物（新聞紙面のスキャン、報道写真、Web からの引用画像）の扱いを整理したこと
- [ ] 個人情報・学内限定情報（試験問題、履修者情報など）が含まれていないこと
