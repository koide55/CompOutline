// 学生の画面
'use strict';
(function () {
  const $ = Z.$, el = Z.el;
  const STORE = 'zawameki.student';
  const pathCode = (location.pathname.match(/^\/r\/(\d{4})/) || [])[1] || '';
  let saved = {};
  try { saved = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { saved = {}; }

  let sock = null, settings = {}, lostUntil = 0, pace = null, paceUntil = 0;
  const posts = new Map();       // id → 投稿（id の順）
  const mine = new Set();        // 自分が「同じく」を押した投稿
  const myPosts = new Set();     // 自分が書いた投稿（この端末で送ったもの）
  let view = 'stream', sentText = '';
  let sidPattern = /^[0-9A-Z]{5,12}$/;

  fetch('/api/config').then((r) => r.json()).then((c) => { sidPattern = new RegExp(c.student_id_pattern); }).catch(() => {});

  function show(id) {
    for (const s of ['join', 'live', 'ended']) $('#' + s).classList.toggle('hidden', s !== id);
  }
  function normalizeSid(s) { return s.trim().toUpperCase().replace(/[-\s　]/g, ''); }
  function save(obj) { try { localStorage.setItem(STORE, JSON.stringify(obj)); } catch (e) { /* 保存できなくても動く */ } }

  // ---- 入室 ----
  function joinForm(message) {
    if (sock) { sock.stop(); sock = null; }
    show('join');
    $('#code').value = pathCode || saved.code || '';
    $('#sid').value = saved.sid || '';
    $('#joinError').textContent = message || '';
    ($('#code').value ? $('#sid') : $('#code')).focus();
  }
  $('#joinForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const code = $('#code').value.trim();
    const sid = normalizeSid($('#sid').value);
    if (!/^\d{4}$/.test(code)) { $('#joinError').textContent = '部屋コードは4桁の数字です'; return; }
    if (!sidPattern.test(sid)) { $('#joinError').textContent = '学生番号の形が正しくありません'; return; }
    saved = { code, sid }; save(saved);
    start();
  });

  function start() {
    show('live');
    $('#who').textContent = saved.sid + ' で入室中';
    posts.clear(); mine.clear();
    $('#stream').replaceChildren(); $('#board').replaceChildren();
    sock = Z.socket('/ws', {
      onOpen: (send) => send({ type: 'hello', code: saved.code, sid: saved.sid }),
      onMessage: handle,
      onState: (on) => { $('#conn').textContent = on ? '' : '再接続中…'; $('#conn').classList.toggle('off', !on); },
    });
  }

  // ---- サーバからの出来事 ----
  function handle(m) {
    switch (m.type) {
      case 'welcome':
        $('#title').textContent = m.title;
        document.title = m.title + ' — ざわめき';
        applySettings(m.settings);
        applyYou(m.you);
        posts.clear(); mine.clear();
        for (const p of m.posts) { posts.set(p.id, p); if (p.mine) mine.add(p.id); }
        render(true);
        break;
      case 'tick': applyTick(m); break;
      case 'you': applyYou(m); break;
      case 'settings': applySettings(m.settings); break;
      case 'slide': $('#slideNo').textContent = 'スライド ' + m.no; break;
      case 'post': {
        const old = posts.get(m.p.id);
        posts.set(m.p.id, m.p);
        if (!old) sortPosts();
        render();
        break;
      }
      case 'post_removed': posts.delete(m.id); render(); break;
      case 'metoo': if (m.mine) mine.add(m.id); else mine.delete(m.id); render(); break;
      case 'ok':
        if (m.what === 'post') {
          myPosts.add(m.id);
          if ($('#postText').value.trim() === sentText) $('#postText').value = '';
          $('#postNamed').checked = false;   // 記名は1回ごと。うっかり続けて記名しないように
          Z.toast(Z.KINDS[m.kind].icon + ' ' + Z.KINDS[m.kind].label + 'を送りました');
          render();
        }
        break;
      case 'fireworks': Z.fireworks('💡 いまの説明で ' + m.count + '人が わかった！'); break;
      case 'closed': if (sock) sock.stop(); show('ended'); break;
      case 'error':
        if (m.fatal) { joinForm(m.message); return; }
        Z.toast(m.message);
        break;
    }
  }

  function applyTick(m) {
    const w = Z.WEATHER[m.weather];
    $('#weather').classList.toggle('hidden', !w && !m.slide);
    if (w) {
      $('#wIcon').textContent = w.icon;
      $('#wLabel').textContent = w.label;
      $('#wLabel').className = 'label w-' + m.weather;
      $('#wSub').textContent = '在室 ' + m.present + '人' + (m.lost ? '・迷子 ' + m.lost + '人' : '');
    } else {
      $('#wIcon').textContent = '🏫';
      $('#wLabel').textContent = '在室 ' + m.present + '人';
      $('#wLabel').className = 'label';
      $('#wSub').textContent = '';
    }
    if (m.slide) $('#slideNo').textContent = 'スライド ' + m.slide;
  }

  function applySettings(s) {
    settings = s;
    $('#commentsClosed').classList.toggle('hidden', s.comments_open);
    $('#postForm button[value="comment"]').disabled = !s.comments_open;
  }

  function applyYou(y) {
    const now = Date.now();
    lostUntil = y.lost_left ? now + y.lost_left * 1000 : 0;
    pace = y.pace; paceUntil = y.pace ? now + y.pace_left * 1000 : 0;
    renderButtons();
  }

  // ---- ボタン ----
  function renderButtons() {
    const now = Date.now();
    const left = Math.max(0, (lostUntil - now) / 1000);
    const on = left > 0;
    $('#lost').classList.toggle('on', on);
    $('#lost').setAttribute('aria-pressed', on);
    $('#lostSub').textContent = !on ? 'わからなくなったら'
      : left < 15 ? 'まだ迷子？ もう一度押す' : 'あと ' + Math.ceil(left) + '秒で消えます';
    const p = paceUntil > now ? pace : null;
    $('#slow').classList.toggle('on', p === 'slow'); $('#slow').setAttribute('aria-pressed', p === 'slow');
    $('#fast').classList.toggle('on', p === 'fast'); $('#fast').setAttribute('aria-pressed', p === 'fast');
  }
  setInterval(renderButtons, 500);

  function sendOrWarn(obj) {
    if (!sock || !sock.send(obj)) { Z.toast('接続し直しています。少し待ってください'); return false; }
    return true;
  }
  $('#lost').addEventListener('click', () => { if (sendOrWarn({ type: 'lost' })) navigator.vibrate && navigator.vibrate(20); });
  $('#got').addEventListener('click', () => {
    if (!(lostUntil > Date.now())) { Z.toast('よかった！（迷子のときに押すと、教員に届きます）'); return; }
    sendOrWarn({ type: 'got' });
  });
  $('#slow').addEventListener('click', () => sendOrWarn({ type: 'pace', dir: 'slow' }));
  $('#fast').addEventListener('click', () => sendOrWarn({ type: 'pace', dir: 'fast' }));

  // ---- タブ ----
  function tab(which) {
    view = which;
    $('#tabStream').classList.toggle('on', which === 'stream');
    $('#tabBoard').classList.toggle('on', which === 'board');
    $('#stream').classList.toggle('hidden', which !== 'stream');
    $('#boardPane').classList.toggle('hidden', which !== 'board');
    render(true);
  }
  $('#tabStream').addEventListener('click', () => tab('stream'));
  $('#tabBoard').addEventListener('click', () => tab('board'));

  // ---- 投稿の一覧 ----
  function sortPosts() {
    // 隠された投稿が戻ってきたときも id の順に並ぶよう、入れ直す
    const list = [...posts.values()].sort((a, b) => a.id - b.id);
    posts.clear();
    for (const p of list.slice(-300)) posts.set(p.id, p);
  }
  function item(p) {
    const k = Z.KINDS[p.kind];
    const cls = [myPosts.has(p.id) ? 'me' : '', p.status !== 'open' && k.votable ? 'done' : ''].join(' ').trim();
    return el('li', { 'data-id': p.id, class: cls || null },
      el('div', { class: 'text' }, p.kind !== 'comment' ? Z.kindBadge(p.kind) : null, p.text, ' ',
        p.status === 'answered' ? el('span', { class: 'badge answered', text: '答えた' }) : null,
        p.status === 'later' ? el('span', { class: 'badge later', text: 'あとで' }) : null),
      k.votable ? el('button', { type: 'button', class: 'metoo' + (mine.has(p.id) ? ' on' : ''), 'aria-pressed': mine.has(p.id),
        onclick: () => sendOrWarn({ type: 'metoo', id: p.id }) }, el('b', { text: p.votes }), k.metoo) : null);
  }
  let pending = false, forceBottom = false;
  function render(bottom) {
    forceBottom = forceBottom || !!bottom;
    if (pending) return;
    pending = true;
    requestAnimationFrame(() => {
      pending = false;
      const all = [...posts.values()];
      const voices = all.filter((p) => Z.KINDS[p.kind].votable);
      if (view === 'stream') {
        const ul = $('#stream');
        const atBottom = forceBottom || ul.scrollHeight - ul.scrollTop - ul.clientHeight < 40;
        ul.replaceChildren(...all.slice(-150).map(item));
        if (atBottom) ul.scrollTop = ul.scrollHeight;
      } else {
        voices.sort((a, b) => (a.status !== 'open') - (b.status !== 'open') || b.votes - a.votes || a.id - b.id);
        $('#board').replaceChildren(...voices.map(item));
      }
      forceBottom = false;
      $('#nAll').textContent = all.length || '';
      const open = voices.filter((p) => p.status === 'open').length;
      $('#nVoices').textContent = open || '';
    });
  }

  // ---- 投稿する ----
  $('#postForm').addEventListener('submit', (e) => {
    e.preventDefault();
    const kind = (e.submitter && e.submitter.value) || 'comment';
    const text = $('#postText').value.trim();
    if (!text) { Z.toast('先に本文を書いてください'); $('#postText').focus(); return; }
    if (text.length > Z.KINDS[kind].limit) { Z.toast(Z.KINDS[kind].label + 'は' + Z.KINDS[kind].limit + '字までです'); return; }
    sentText = text;   // 消すのは届いたとき（待ち時間で断られたら書いた文を残す）
    sendOrWarn({ type: 'post', kind, text, named: $('#postNamed').checked });
  });

  // ---- 退出 ----
  $('#leave').addEventListener('click', () => {
    if (!confirm('退出しますか？（学生番号の記憶も消します）')) return;
    saved = {}; save(saved);
    joinForm();
  });
  $('#again').addEventListener('click', () => { saved.code = ''; save(saved); joinForm(); });

  // 前回の部屋と同じなら、そのまま入り直す（再読み込み・再起動のあと）
  if (saved.sid && saved.code && (!pathCode || pathCode === saved.code)) start();
  else joinForm();
})();
