# スライド

講義ノート（`lectures/`）と図（`figures/`）から `.pptx` を組み立てる。

**現在は第1回のみの見本である。** 体裁を決めてから残り12回に展開する。

| ファイル | 内容 |
| --- | --- |
| `第01回_計算とは何か.pptx` | 見本（22枚） |
| `tools/lec01.js` | その生成スクリプト |

## 作り直す

```bash
cd slides && npm install pptxgenjs && node tools/lec01.js
```

図は SVG のままでは PowerPoint が確実に描けないので、
`figures/*.svg` を 3倍解像度の PNG にしてから貼る。

```bash
.venv/bin/python - <<'PY'
import cairosvg, glob, os, re
for p in sorted(glob.glob('figures/fig-01-*.svg')):
    s = re.sub(r'font-family:[^;}]*;?', '', open(p, encoding='utf-8').read())
    s = s.replace('<svg ', '<svg font-family="Arial Unicode MS" ', 1)
    cairosvg.svg2png(bytestring=s.encode(),
                     write_to='slides/png/' + os.path.basename(p)[:-4] + '.png', scale=3.0)
PY
```

## 体裁

図の SVG と**同じ配色**を使っている。スライドと図が別物に見えないようにするため。

| 用途 | 色 |
| --- | --- |
| 濃色スライドの地 / 本文 | `#16191D` |
| 明色スライドの地 | `#FFFFFF` |
| 補助の面 | `#EEF1F5` |
| 強調 | `#0B5CAD` |
| 補足の文字 | `#5F6672` |

- **濃色と明色を挟む** — タイトル・節の区切り・まとめを濃色、本文を明色にする
- **意匠はテープのマス目** — 濃色スライドの下端に、チューリングマシンのテープを模した
  マス目を並べ、1マスだけ塗る。回ごとに意匠は変える
- **見出しの下に飾り線を引かない** — 余白と地色で区切る
- 書体は `Yu Gothic`（Windows 8.1+ と macOS 10.9+ の両方にある）。
  等幅は `Courier New`

## 検証

```bash
# 構造（スキーマ・関連付け・コンテンツタイプ）
.venv/bin/python <pptxスキルの>scripts/office/validate.py slides/第01回_計算とは何か.pptx

# 幾何（枠外へのはみ出し、文字どうしの重なり）
python3 tools/pptx_shapes.py slides/第01回_計算とは何か.pptx <スライド番号>
```

**この環境では画面に描画しての確認ができない**（LibreOffice が無い）。
構造と座標は機械的に確かめられるが、実際の見た目、とくに
**日本語の折り返しによる溢れ**は確認できていない。
一度 PowerPoint で開いて確かめること。
