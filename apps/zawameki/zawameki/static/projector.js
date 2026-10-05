// 投影画面。何を出すかは教員の操作画面から切り替える（キーボードの 1 2 3 でも切り替わる）
'use strict';
(function () {
  const $ = Z.$, el = Z.el;
  const code = location.pathname.split('/')[2];
  const key = new URLSearchParams(location.hash.slice(1)).get('key') || '';
  const posts = new Map();
  let mode = 'join', ready = false;
  const lanes = [];   // 流れるコメントの段ごとの「空く時刻」

  $('#code').textContent = code;
  $('#qr').src = '/qr/' + code + '.svg';

  Z.socket('/ws/teacher', {
    onOpen: (send) => send({ type: 'hello', code, key }),
    onMessage: handle,
  });

  function handle(m) {
    switch (m.type) {
      case 'welcome':
        $('#title').textContent = m.title;
        $('#url').textContent = m.join_url;
        posts.clear();
        for (const p of m.posts) posts.set(p.id, p);
        show(m.projector);
        applyTick(m.tick);
        ready = true;
        break;
      case 'tick': applyTick(m); break;
      case 'projector': show(m.mode); break;
      case 'post': {
        const isNew = !posts.has(m.p.id);
        posts.set(m.p.id, m.p);
        if (isNew && ready && m.p.status !== 'hidden') fly(m.p);
        renderBoard();
        break;
      }
      case 'fireworks': Z.fireworks('💡 いまの説明で ' + m.count + '人が わかった！'); break;
      case 'closed': $('#title').textContent = 'この部屋は閉じました'; show('join'); break;
      case 'error': if (m.fatal) { document.body.replaceChildren(el('p', { style: 'padding:5vh;font-size:4vh', text: m.message })); } break;
    }
  }

  function applyTick(c) {
    const w = Z.WEATHER[c.weather];
    $('#wIcon').textContent = w.icon;
    $('#wText').textContent = w.label;
    $('#present').textContent = '在室 ' + c.present + '人';
  }

  function show(m) {
    mode = m;
    for (const id of ['join', 'board', 'stream']) $('#' + id).classList.toggle('hidden', id !== m);
    $('#streamHint').textContent = '💬 コメントがここを流れます（部屋 ' + code + '）';
    if (m === 'board') renderBoard();
  }

  function renderBoard() {
    if (mode !== 'board') return;
    const list = [...posts.values()]
      .filter((p) => Z.KINDS[p.kind].votable && p.status === 'open')
      .sort((a, b) => b.votes - a.votes || a.id - b.id).slice(0, 6);
    $('#boardList').replaceChildren(...list.map((p) => el('li', {},
      el('div', { class: 'v' }, String(p.votes), el('small', { text: Z.KINDS[p.kind].metoo })),
      el('div', { class: 't' }, Z.kindBadge(p.kind),
        p.kind === 'naive' ? el('span', { class: 'naive-lead', text: '素人質問で恐縮ですが、' }) : null,
        p.text))));
    if (!list.length) $('#boardList').append(el('li', { class: 'muted' }, el('div', { class: 't', text: 'まだありません。気軽にどうぞ。' })));
  }

  // 流れるコメント。重ならないよう空いている段に流す
  function fly(p) {
    if (mode !== 'stream') return;
    const n = Math.max(4, Math.floor((innerHeight * 0.8) / (innerHeight * 0.08)));
    const now = Date.now();
    let lane = 0;
    for (let i = 0; i < n; i++) { if ((lanes[i] || 0) <= now) { lane = i; break; } if ((lanes[i] || 0) < (lanes[lane] || 0)) lane = i; }
    const prefix = p.kind === 'comment' ? '' : Z.KINDS[p.kind].icon + ' ';
    const d = el('div', { class: 'fly k-' + p.kind }, prefix + p.text);
    d.style.top = (8 + lane * 8) + 'vh';
    const secs = 9 + Math.random() * 2;
    d.style.animationDuration = secs + 's';
    $('#stream').append(d);
    lanes[lane] = now + secs * 1000 * 0.45;
    d.addEventListener('animationend', () => d.remove());
  }

  addEventListener('keydown', (e) => {
    if (e.key === '1') show('join');
    if (e.key === '2') show('board');
    if (e.key === '3') show('stream');
    if (e.key === 'f') document.documentElement.requestFullscreen && document.documentElement.requestFullscreen();
  });
})();
