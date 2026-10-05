// 教員の操作画面（講義中）
'use strict';
(function () {
  const $ = Z.$, el = Z.el;
  const code = location.pathname.split('/')[2];
  const LEVEL = { sunny: 0, fair: 1, cloudy: 2, rain: 3, storm: 4 };
  const STATUS = { open: '未対応', answered: '答えた', later: 'あとで', hidden: '隠した' };
  let sock = null, slide = 1, history = [], settings = {}, badSince = 0, alerted = false;
  const posts = new Map();
  let kindFilter = 'all', onlyOpen = true;

  $('#code').textContent = code;
  $('#reportLink').href = '/teacher/' + code + '/report';

  fetch('/api/teacher/rooms/' + code).then((r) => {
    if (!r.ok) throw new Error('closed');
    return r.json();
  }).then((room) => {
    $('#title').textContent = room.title;
    document.title = room.title + ' — 操作画面';
    $('#joinUrl').textContent = room.join_url;
    // 鍵は # の後ろに置く（サーバのログにも Referer にも出ない）
    $('#projLink').href = '/projector/' + code + '#key=' + encodeURIComponent(room.key);
    sock = Z.socket('/ws/teacher', {
      onOpen: (send) => send({ type: 'hello', code, key: room.key }),
      onMessage: handle,
      onState: (on) => { $('#conn').textContent = on ? '● 接続中' : '再接続中…'; $('#conn').classList.toggle('off', !on); },
    });
  }).catch(() => {
    $('#title').textContent = 'この部屋は閉じています';
    $('#conn').textContent = '';
  });

  function send(obj) { if (!sock || !sock.send(obj)) Z.toast('接続し直しています'); }

  function handle(m) {
    switch (m.type) {
      case 'welcome':
        history = m.history || [];
        applySettings(m.settings);
        applyProjector(m.projector);
        posts.clear();
        for (const p of m.posts) posts.set(p.id, p);
        applyTick(m.tick);
        render();
        break;
      case 'tick': applyTick(m); break;
      case 'post': posts.set(m.p.id, m.p); render(); break;
      case 'settings': applySettings(m.settings); break;
      case 'projector': applyProjector(m.mode); break;
      case 'slide': setSlideView(m.no); break;
      case 'fireworks': Z.fireworks('💡 いまの説明で ' + m.count + '人が わかった！'); break;
      case 'closed': $('#title').textContent = '部屋を閉じました'; sock && sock.stop(); break;
      case 'error': Z.toast(m.message); if (m.fatal) $('#title').textContent = m.message; break;
    }
  }

  // ---- 教室の様子 ----
  function applyTick(c) {
    const w = Z.WEATHER[c.weather];
    $('#wIcon').textContent = w.icon;
    $('#wLabel').textContent = w.label;
    $('#wLabel').className = 'label w-' + c.weather;
    const rate = c.present ? Math.round((c.lost / c.present) * 100) : 0;
    $('#wNums').textContent = '迷子 ' + c.lost + '人 / 在室 ' + c.present + '人（' + rate + '%）';
    $('#wJoined').textContent = '入室 累計 ' + c.joined + '人・経過 ' + Z.mmss(c.t);
    $('#nSlow').textContent = c.slow; $('#nFast').textContent = c.fast;
    const tot = Math.max(1, c.present);
    $('#tugS').style.width = Math.min(50, (c.slow / tot) * 100) + '%';
    $('#tugF').style.width = Math.min(50, (c.fast / tot) * 100) + '%';
    if (c.slide && c.slide !== slide) setSlideView(c.slide);
    if (c.type === 'tick') {
      history.push([c.t, c.present, c.lost]);
      while (history.length && history[0][0] < c.t - 600) history.shift();
    }
    drawSpark();
    // くもり以上が30秒続いたら1回だけ知らせる
    const now = Date.now();
    if (LEVEL[c.weather] >= 2) {
      if (!badSince) badSince = now;
      if (!alerted && now - badSince > 30000 && $('#sAlert').checked) {
        alerted = true;
        $('#wx').classList.remove('alert'); void $('#wx').offsetWidth; $('#wx').classList.add('alert');
        navigator.vibrate && navigator.vibrate([200, 100, 200]);
      }
    } else { badSince = 0; alerted = false; }
  }

  function drawSpark() {
    const cv = $('#spark'), g = cv.getContext('2d');
    const W = cv.width, H = cv.height;
    g.clearRect(0, 0, W, H);
    const css = getComputedStyle(document.documentElement);
    const line = css.getPropertyValue('--line'), storm = css.getPropertyValue('--storm'), muted = css.getPropertyValue('--muted');
    g.font = '18px system-ui'; g.fillStyle = muted; g.strokeStyle = line; g.lineWidth = 1;
    const y = (r) => H - 8 - (H - 16) * Math.min(r, 0.5) / 0.5;
    for (const [r, lab] of [[0.2, '20%'], [0.35, '35%']]) {
      g.beginPath(); g.moveTo(0, y(r)); g.lineTo(W, y(r)); g.stroke(); g.fillText(lab, 4, y(r) - 4);
    }
    if (history.length < 2) return;
    const t1 = history[history.length - 1][0], t0 = t1 - 600;
    g.strokeStyle = storm; g.lineWidth = 3; g.beginPath();
    history.forEach(([t, present, lost], i) => {
      const x = ((t - t0) / 600) * W, yy = y(present ? lost / present : 0);
      i ? g.lineTo(x, yy) : g.moveTo(x, yy);
    });
    g.stroke();
  }

  // ---- スライド ----
  function setSlideView(no) { slide = no; $('#slideNo').value = no; }
  function goSlide(no) {
    if (!Number.isInteger(no) || no < 1 || no > 999) return;
    setSlideView(no);
    send({ type: 'slide', no });
  }
  $('#prev').addEventListener('click', () => goSlide(slide - 1));
  $('#next').addEventListener('click', () => goSlide(slide + 1));
  $('#slideNo').addEventListener('change', () => goSlide(parseInt($('#slideNo').value, 10)));
  addEventListener('keydown', (e) => {
    if (e.target.matches('input, textarea, select')) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); goSlide(slide + 1); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); goSlide(slide - 1); }
  });

  // ---- 投影 ----
  function applyProjector(mode) {
    for (const b of document.querySelectorAll('#projModes button')) b.classList.toggle('on', b.dataset.mode === mode);
  }
  $('#projModes').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (b) send({ type: 'projector', mode: b.dataset.mode });
  });

  // ---- 設定 ----
  function applySettings(s) {
    settings = s;
    $('#sComments').checked = s.comments_open;
    $('#sInterval').value = String(s.comment_interval);
    $('#sWeather').checked = s.show_weather;
  }
  $('#sComments').addEventListener('change', (e) => send({ type: 'settings', settings: { comments_open: e.target.checked } }));
  $('#sInterval').addEventListener('change', (e) => send({ type: 'settings', settings: { comment_interval: Number(e.target.value) } }));
  $('#sWeather').addEventListener('change', (e) => send({ type: 'settings', settings: { show_weather: e.target.checked } }));

  $('#close').addEventListener('click', async () => {
    if (!confirm('部屋を閉じますか？ 学生は入れなくなります。')) return;
    const r = await fetch('/api/teacher/rooms/' + code + '/close', { method: 'POST' });
    if (r.ok) location.href = '/teacher/' + code + '/report';
  });

  // ---- 投稿 ----
  $('#filters').addEventListener('click', (e) => {
    const b = e.target.closest('button'); if (!b) return;
    if (b.dataset.k === 'open') { onlyOpen = !onlyOpen; b.classList.toggle('on', onlyOpen); }
    else {
      kindFilter = b.dataset.k;
      for (const x of document.querySelectorAll('#filters button:not(#onlyOpen)')) x.classList.toggle('on', x === b);
    }
    render();
  });

  function acts(p) {
    const mark = (status) => () => send({ type: 'mark', id: p.id, status });
    if (p.status === 'hidden') return el('div', { class: 'acts' }, el('button', { type: 'button', onclick: mark('open'), text: '戻す' }));
    if (p.kind === 'comment') return el('div', { class: 'acts' }, el('button', { type: 'button', onclick: mark('hidden'), text: '隠す' }));
    return el('div', { class: 'acts' },
      p.status !== 'answered' ? el('button', { type: 'button', onclick: mark('answered'), text: '✓ 答えた' }) : null,
      p.status !== 'later' ? el('button', { type: 'button', onclick: mark('later'), text: 'あとで' }) : null,
      p.status !== 'open' ? el('button', { type: 'button', onclick: mark('open'), text: '未対応に' }) : null,
      el('button', { type: 'button', onclick: mark('hidden'), text: '隠す' }));
  }
  function meta(p) {
    return el('div', { class: 'meta' }, Z.mmss(p.t) + '・スライド ' + p.slide
      + (p.status !== 'open' ? '・' + STATUS[p.status] : '') + (p.named ? '・記名 ' + p.named : '・匿名'));
  }

  let pending = false;
  function render() {
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {
      pending = false;
      const all = [...posts.values()];
      const voices = all.filter((p) => Z.KINDS[p.kind].votable)
        .filter((p) => kindFilter === 'all' || p.kind === kindFilter)
        .filter((p) => !onlyOpen || p.status === 'open');
      voices.sort((a, b) => (a.status !== 'open') - (b.status !== 'open') || b.votes - a.votes || a.id - b.id);
      $('#voices').replaceChildren(...voices.map((p) => el('li', { class: p.status === 'hidden' ? 'hid' : p.status !== 'open' ? 'done' : null },
        el('div', { class: 'votes' }, String(p.votes), el('small', { text: Z.KINDS[p.kind].metoo })),
        el('div', { class: 'body' }, Z.kindBadge(p.kind), ' ', p.text, meta(p)),
        acts(p))));
      if (!voices.length) $('#voices').append(el('li', { class: 'muted', text: 'まだありません' }));
      const open = all.filter((p) => Z.KINDS[p.kind].votable && p.status === 'open').length;
      $('#nOpen').textContent = '未対応 ' + open;
      const comments = all.filter((p) => p.kind === 'comment').sort((a, b) => b.id - a.id).slice(0, 200);
      $('#comments').replaceChildren(...comments.map((p) => el('li', { class: p.status === 'hidden' ? 'hid' : null },
        el('div', { class: 'body' }, p.text, meta(p)), acts(p))));
      $('#nComments').textContent = comments.length;
    });
  }
})();
