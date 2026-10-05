// ざわめき 画面の共通部品。利用者の書いた文字は必ず textContent で入れる（innerHTML を使わない）
'use strict';

const Z = {};

Z.WEATHER = {
  sunny: { icon: '☀️', label: '快晴' },
  fair: { icon: '🌤', label: '晴れ' },
  cloudy: { icon: '☁️', label: 'くもり' },
  rain: { icon: '🌧', label: '雨' },
  storm: { icon: '⛈', label: '雷' },
};

// 投稿の種類（サーバの room.KINDS と揃える）
Z.KINDS = {
  comment: { icon: '💬', label: 'コメント', votable: false, limit: 80 },
  question: { icon: '❓', label: '質問', votable: true, limit: 200, metoo: '同じく' },
  opinion: { icon: '📣', label: 'ご意見申す', votable: true, limit: 200, metoo: '同感' },
  naive: { icon: '🔰', label: '素人質問ですが', votable: true, limit: 200, metoo: '同じく' },
};
Z.kindBadge = function (kind) {
  const k = Z.KINDS[kind];
  return Z.el('span', { class: 'badge k-' + kind, text: k.icon + ' ' + k.label });
};

Z.el = function (tag, attrs, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') e.className = v;
    else if (k === 'text') e.textContent = v;
    else if (k.startsWith('on')) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? '' : v);
  }
  for (const c of children) {
    if (c === null || c === undefined || c === false) continue;
    e.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return e;
};

Z.$ = (sel) => document.querySelector(sel);

Z.mmss = function (t) {
  t = Math.max(0, Math.round(t));
  return Math.floor(t / 60) + ':' + String(t % 60).padStart(2, '0');
};

let toastTimer = null;
Z.toast = function (msg, ms) {
  let t = Z.$('#toast');
  if (!t) { t = Z.el('div', { id: 'toast', class: 'toast', role: 'status' }); document.body.append(t); }
  t.textContent = msg;
  t.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.add('hidden'), ms || 2600);
};

// 花火（SPEC §5.2）
Z.fireworks = function (text) {
  const box = Z.el('div', { class: 'fireworks', 'aria-live': 'polite' });
  const colors = ['#f5c542', '#f06b6b', '#6cb6ff', '#5fd39a', '#c39bff', '#ffb05c'];
  for (let n = 0; n < 3; n++) {
    const cx = 20 + Math.random() * 60, cy = 20 + Math.random() * 40;
    for (let i = 0; i < 18; i++) {
      const a = (i / 18) * Math.PI * 2, r = 80 + Math.random() * 70;
      const p = Z.el('i');
      p.style.left = cx + 'vw'; p.style.top = cy + 'vh';
      p.style.background = colors[(i + n) % colors.length];
      p.style.setProperty('--dx', Math.cos(a) * r + 'px');
      p.style.setProperty('--dy', Math.sin(a) * r + 'px');
      p.style.animationDelay = n * 0.35 + 's';
      box.append(p);
    }
  }
  box.append(Z.el('div', { class: 'msg', text }));
  document.body.append(box);
  setTimeout(() => box.remove(), 4000);
};

// 再接続つきの WebSocket。教室の Wi-Fi は切れるものとして作る
Z.socket = function (path, { onOpen, onMessage, onState }) {
  let ws = null, tries = 0, stopped = false, pingTimer = null;
  const proto = location.protocol === 'https:' ? 'wss:' : 'ws:';
  function open() {
    ws = new WebSocket(proto + '//' + location.host + path);
    ws.onopen = () => {
      tries = 0;
      onState && onState(true);
      onOpen && onOpen(send);
      clearInterval(pingTimer);
      pingTimer = setInterval(() => send({ type: 'ping' }), 25000);
    };
    ws.onmessage = (ev) => {
      let msg;
      try { msg = JSON.parse(ev.data); } catch (e) { return; }
      const items = msg.type === 'batch' ? msg.items : [msg];
      for (const m of items) {
        if (m.fatal) stopped = true;
        onMessage(m);
      }
    };
    ws.onclose = () => {
      clearInterval(pingTimer);
      onState && onState(false);
      if (stopped) return;
      tries++;
      const wait = Math.min(15000, 500 * 2 ** Math.min(tries, 5)) * (0.7 + Math.random() * 0.6);
      setTimeout(open, wait);   // 200人が一斉に入り直さないよう、待ち時間をばらす
    };
  }
  function send(obj) {
    if (ws && ws.readyState === WebSocket.OPEN) { ws.send(JSON.stringify(obj)); return true; }
    return false;
  }
  open();
  return { send, stop() { stopped = true; ws && ws.close(); } };
};
