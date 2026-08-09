# コンピュータシステム通論 (An Outline of Computer System)

九州大学 学部講義「コンピュータシステム通論」の講義資料。

90分 × 全13回。計算の原理（チューリングマシン）から、
大規模言語モデルとエージェントAIまでを一本の線でつなぐ構成。

## 講義一覧

| 回 | 題目 | 今回の問い |
| ---: | --- | --- |
| 1 | [計算とは何か](lectures/01-what-is-computation.md) | 「計算できる」とはどういうことか。計算できないことはあるか |
| 2 | [情報の表現と計算量](lectures/02-information-and-complexity.md) | 情報を2進数で表すと何が嬉しいのか。「速いアルゴリズム」とは何か |
| 3 | [論理回路からプロセッサへ](lectures/03-logic-to-processor.md) | 数学的なモデルを、どうやって電気で作るのか |
| 4 | [プログラムが動くまで](lectures/04-how-programs-run.md) | 人間が書いた文字列が、なぜ機械の動作になるのか |
| 5 | [記憶階層とプロセッサの並列性](lectures/05-memory-hierarchy-and-parallelism.md) | なぜ計算機の速度は「メモリ待ち」で決まるのか |
| 6 | [ストレージとファイルシステム](lectures/06-storage-and-filesystems.md) | 電源を切っても消えないデータは、どう置かれているのか |
| 7 | [OSとプロセス](lectures/07-os-and-processes.md) | 1台の計算機を、なぜ何十ものプログラムで同時に使えるのか |
| 8 | [入出力・仮想化・クラウド](lectures/08-io-virtualization-cloud.md) | 100万倍遅い装置と、どうやって折り合いをつけるのか |
| 9 | [ネットワークの基礎](lectures/09-network-fundamentals.md) | 世界中の計算機が、なぜ1つの網としてつながるのか |
| 10 | [インターネットとWeb](lectures/10-internet-and-web.md) | アドレスしか知らない相手に、どうやってデータを届けるのか |
| 11 | [データベースとデータ処理](lectures/11-databases.md) | 壊れずに、矛盾なくデータを溜めるにはどうするか |
| 12 | [情報セキュリティ](lectures/12-information-security.md) | 顔の見えない相手を、どうやって信用するのか |
| 13 | [機械学習からLLM・エージェントAIへ](lectures/13-machine-learning-llm-agents.md) | 計算機が「学習する」とはどういう計算か |

各回は 到達目標 → 時間配分 → 本文 → 演習 → まとめ の構成。
本文中の図は**仕様のみ**を引用ブロックで記述しており、作図はこれから行う。

## 構成

| パス | 内容 |
| --- | --- |
| `lectures/` | 全13回の講義ノート |
| `docs/curriculum.md` | 13回の設計方針、旧スライドとの対応表、執筆上の約束 |
| `docs/findings.md` | 旧版 `CompOutline2024.pptx`（663枚）の調査結果 |
| `docs/inventory.md` | 旧版のセクション別スライド一覧 |
| `figures/README.md` | 図の作成方針とスタイル |
| `figures/INDEX.md` | 全図の一覧（自動生成） |
| `tools/dump_pptx.py` | `.pptx` から構成・本文・ノートを JSON に抽出 |
| `tools/collect_figures.py` | 講義ノートから図の仕様を集めて一覧を生成 |

## ツール

図の一覧を更新する（講義ノートに図を追記したあと実行する）:

```bash
python3 tools/collect_figures.py
```

旧スライドの内容を抽出する:

```bash
python3 tools/dump_pptx.py CompOutline2024.pptx out.json
```

## 執筆上の約束

- **第三者著作物は使わない。** 図はすべて自作する。製品写真・報道写真・
  Web からの引用図は載せない
- **具体的な数値には時点を書く。**「2026年時点で」と明記する
- **個人情報を例に使わない。** メールアドレスは `example.com`、
  IPアドレスは RFC 5737 の文書用アドレスを使う

## 旧版について

旧版 `CompOutline2024.pptx`（663枚 / 24セクション / 148MB）は、
GitHub の100MB制限を超えるため `.gitignore` に入れており、追跡していない。
調査結果は [docs/findings.md](docs/findings.md) を参照。

## 公開前チェック

GitHub Public にする前に確認すること。

- [ ] 100MB を超えるファイルが履歴に入っていないこと（`git count-objects -vH`）
- [ ] 図が第三者著作物になっていないこと
- [ ] 個人情報・学内限定情報（試験問題、履修者情報など）が含まれていないこと
