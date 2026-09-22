// 自動採点に載せる19問の「解答欄」の定義。
//
// 設問の文章はここに持たない。lectures/*.md から抜き出して使う
// （docs/curriculum.md の単一ソース方針。文面を直すのはノート側だけでよい）。
// ここにあるのは、ノートに書いていないもの——解答欄の並びと、正解と、許容誤差である。
//
// type: 'num'  数値。tol は絶対値での許容誤差
//       'text' 文字列の完全一致（2進数やIPアドレス）
//       'pick' 選択肢。answer が正解、others が誤答
//
// part: その問題のうち、この解答欄で答えさせる範囲。
//       指定があるものは残りを作文問題として別に出す（docs/moodle-exercises.md 参照）。

export const questions = [
  { id: '1-1', name: '互除法のステップ', blanks: [
    { label: '1回目の a', type: 'num', answer: 252, tol: 0 },
    { label: '1回目の b', type: 'num', answer: 105, tol: 0 },
    { label: '1回目の r', type: 'num', answer: 42, tol: 0 },
    { label: '2回目の a', type: 'num', answer: 105, tol: 0 },
    { label: '2回目の b', type: 'num', answer: 42, tol: 0 },
    { label: '2回目の r', type: 'num', answer: 21, tol: 0 },
    { label: '3回目の a', type: 'num', answer: 42, tol: 0 },
    { label: '3回目の b', type: 'num', answer: 21, tol: 0 },
    { label: '3回目の r', type: 'num', answer: 0, tol: 0 },
  ]},

  { id: '2-1', name: '2進数と2の補数', blanks: [
    { label: '173 を8ビットの2進数で', type: 'text', answer: '10101101' },
    { label: '−45 を8ビットの2の補数で', type: 'text', answer: '11010011' },
  ]},

  { id: '2-2', name: '容量表示のずれ', blanks: [
    { label: '表示される容量', type: 'num', answer: 1.82, tol: 0.005, unit: 'TB' },
  ]},

  { id: '2-4', name: 'オーダと実行時間', blanks: [
    { label: 'O(n²) のとき', type: 'num', answer: 100, tol: 0.5, unit: '秒' },
    { label: 'O(n log n) のとき', type: 'num', answer: 13.3, tol: 0.4, unit: '秒' },
  ]},

  { id: '3-4', name: '信号が1周期で進む距離', blanks: [
    { label: '(a) 1周期で進む距離', type: 'num', answer: 36, tol: 0.6, unit: 'mm' },
    { label: '(b) 28mm 先に届くか', type: 'pick', answer: '届く', others: ['届かない'] },
    { label: '(c) 届かなくなる周波数', type: 'num', answer: 6.43, tol: 0.15, unit: 'GHz' },
  ]},

  { id: '4-7', name: '二分探索で原因を特定する回数', part: '前半（最小の試行回数）のみ',
    blanks: [
      { label: '最小の試行回数', type: 'num', answer: 7, tol: 0, unit: '回' },
    ]},

  { id: '5-2', name: '実効アクセス時間', blanks: [
    { label: '(a) ヒット率 98%', type: 'num', answer: 3.96, tol: 0.02, unit: 'ns' },
    { label: '(b) ヒット率 90%', type: 'num', answer: 11.8, tol: 0.05, unit: 'ns' },
    { label: '(a) から (b) で何倍遅くなるか', type: 'num', answer: 2.98, tol: 0.06, unit: '倍' },
  ]},

  // 概算を求めているので、許容誤差は1割ほど取る
  { id: '5-3', name: 'ループの向きとキャッシュミス', blanks: [
    { label: '(a) 行を内側で回したとき', type: 'num', answer: 131072, tol: 13000, unit: '回' },
    { label: '(b) 列を内側で回したとき', type: 'num', answer: 1048576, tol: 105000, unit: '回' },
  ]},

  { id: '5-5', name: 'アムダールの法則', blanks: [
    { label: '(a) 4コアでの高速化率', type: 'num', answer: 2.5, tol: 0.05, unit: '倍' },
    { label: '(b) コア数を無限にしたときの上限', type: 'num', answer: 5, tol: 0.05, unit: '倍' },
  ]},

  { id: '6-1', name: 'HDD の平均アクセス時間', blanks: [
    { label: '平均アクセス時間', type: 'num', answer: 8.03, tol: 0.06, unit: 'ms' },
    { label: '転送時間の占める割合', type: 'num', answer: 0.4, tol: 0.06, unit: '%' },
  ]},

  { id: '6-2', name: 'ランダムアクセスと連続アクセス', blanks: [
    { label: '(a) ばらばらに置かれている場合', type: 'num', answer: 4.02, tol: 0.06, unit: '秒' },
    { label: '(b) 連続領域に置かれている場合', type: 'num', answer: 24, tol: 0.5, unit: 'ms' },
    { label: '(a) は (b) の何倍か', type: 'num', answer: 167, tol: 12, unit: '倍' },
  ]},

  { id: '6-3', name: 'RAID 5 と RAID 6 の容量', blanks: [
    { label: 'RAID 5 で使える容量', type: 'num', answer: 20, tol: 0, unit: 'TB' },
    { label: 'RAID 5 が耐えられる故障', type: 'num', answer: 1, tol: 0, unit: '台' },
    { label: 'RAID 6 で使える容量', type: 'num', answer: 16, tol: 0, unit: 'TB' },
    { label: 'RAID 6 が耐えられる故障', type: 'num', answer: 2, tol: 0, unit: '台' },
  ]},

  // B の値は問題文に書いてあるので、復元の答えを聞いても自動採点にならない。
  // パリティ P だけを自動採点にし、復元の計算は作文問題に残す。
  { id: '6-4', name: 'パリティの計算', part: 'パリティ P のみ', blanks: [
    { label: 'パリティ P', type: 'text', answer: '0001' },
  ]},

  { id: '6-7', name: 'イレイジャーコーディング', blanks: [
    { label: '(a) 容量効率', type: 'num', answer: 66.7, tol: 0.5, unit: '%' },
    { label: '(b) 耐えられる同時故障', type: 'num', answer: 4, tol: 0, unit: '台' },
    { label: '(c) 3重レプリケーションの何倍か', type: 'num', answer: 2, tol: 0.1, unit: '倍' },
  ]},

  { id: '8-4', name: 'キーマトリクスの配線数', part: '(a) と (b) のみ', blanks: [
    { label: '(a) n', type: 'num', answer: 16, tol: 0 },
    { label: '(a) m', type: 'num', answer: 16, tol: 0 },
    { label: '(a) 配線の本数', type: 'num', answer: 32, tol: 0, unit: '本' },
    { label: '(b) 1キー1本と比べて何分の1か', type: 'num', answer: 8, tol: 0 },
  ]},

  { id: '9-8', name: 'サブネットの計算', blanks: [
    { label: '(a) ネットワークアドレス', type: 'text', answer: '198.51.100.128' },
    { label: '(b) ブロードキャストアドレス', type: 'text', answer: '198.51.100.191' },
    { label: '(c) 割り当てられるアドレスの個数', type: 'num', answer: 62, tol: 0, unit: '個' },
  ]},

  { id: '12-2', name: '必要な鍵の数', part: 'n=1000 のときの鍵の数のみ', blanks: [
    { label: '共通鍵暗号', type: 'num', answer: 499500, tol: 0, unit: '個' },
    { label: '公開鍵暗号', type: 'num', answer: 2000, tol: 0, unit: '個' },
  ]},
];

// 数値は付随的で、本体（命令列・システムコールの列）が作文でしか採点できない2問。
// 自動採点に移すと問題が壊れるので、作文問題のまま残す。
export const keptAsEssay = [
  ['3-5', '本体は命令列を書くこと。命令数（9命令）だけを取り出しても意味がない'],
  ['7-5', '本体はシステムコールを順に挙げること。パイプの本数（2本）は付随的'],
];
