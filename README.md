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
本文には図の**仕様**（引用ブロック）と**図そのもの**（SVG）の両方を置いてある。
仕様を残してあるのは、描き直すときに意図が失われないようにするため。

図は全59点、すべて自作の SVG（`figures/fig-NN-MM.svg`）。

## 構成

| パス | 内容 |
| --- | --- |
| `lectures/` | 全13回の講義ノート |
| `figures/` | 図 59点（SVG） |
| `docs/curriculum.md` | 13回の設計方針、旧スライドとの対応表、執筆上の約束 |
| `docs/findings.md` | 旧版 `CompOutline2024.pptx`（663枚）の調査結果 |
| `docs/inventory.md` | 旧版のセクション別スライド一覧 |
| `docs/legacy-slides-2024.json` | 旧版の全文（タイトル・本文・ノート）の控え |
| `tools/` | 下記のツール群 |

## ツール

図をすべて描き出す:

```bash
python3 tools/build_figures.py
```

| ツール | 用途 |
| --- | --- |
| `tools/build_figures.py` | 図を `figures/` に書き出す（`tools/figs/` に定義） |
| `tools/svgkit.py` | 図の共通スタイルと描画部品 |
| `tools/collect_figures.py` | 講義ノートから図の仕様を集めて `figures/INDEX.md` を生成 |
| `tools/preview.py` | 図を PNG のコンタクトシートにまとめる（目視確認用） |
| `tools/pptx_shapes.py` | `.pptx` からベクタ図形を座標つきで取り出す |
| `tools/pptx_to_svg.py` | 取り出した図形を統一スタイルの SVG に描き直す |
| `tools/dump_pptx.py` | `.pptx` から構成・本文・ノートを JSON に抽出 |

`preview.py` だけ `cairosvg` と `Pillow` が要る。仮想環境を作って入れる:

```bash
python3 -m venv .venv && .venv/bin/pip install cairosvg pillow
```

## 旧スライドから引き継いだ図

小出先生が PowerPoint 上で**図形として描いた**図は、写真や引用画像と違って
自作物なので素材として使える。`tools/pptx_shapes.py` で座標を取り出し、
統一スタイルで描き直した。該当する図には講義ノート側に `[旧 slide N]` と注記してある。

| 図 | 引き継いだ元 |
| --- | --- |
| 図 1-2 チューリングマシンの構成 | 旧 slide 21 |
| 図 3-5 ノイマン型計算機の構成 | 旧 slide 40 |
| 図 6-3 RAID のデータ配置 | 旧 slide 343–357 |
| 図 9-3 階層を降りて上がる | 旧 slide 191 |
| 図 11-1 正規化の前と後 | 旧 slide 547–550 |

別講義の `network2026.pptx`（通信工学概論）からは、
本講義に欠けていた「システムコールを実際に呼ぶ」話を要点だけ移した。

| 移行先 | 内容 | 元 |
| --- | --- | --- |
| 第7回 7.2 | ファイル記述子、pipe、dup、シェルの `\|` の仕組み（図 7-6） | network2026 slide 537–550 |
| 第10回 10.2 | socket / bind / listen / accept / connect の順序（図 10-6） | network2026 slide 551–570 |

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
