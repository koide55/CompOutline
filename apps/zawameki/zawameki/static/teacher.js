// 教員の部屋一覧
'use strict';
(function () {
  const $ = Z.$, el = Z.el;
  function when(ts) {
    const d = new Date(ts * 1000);
    return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
      + ' ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
  }
  async function load() {
    const r = await fetch('/api/teacher/rooms');
    const { rooms } = await r.json();
    $('#rooms').replaceChildren(...rooms.map((x) => el('tr', {},
      el('td', { class: 'code', text: x.code }),
      el('td', {}, x.title, ' ', x.open ? el('span', { class: 'badge open', text: '開いている' }) : null),
      el('td', { class: 'wide', text: when(x.opened_at) }),
      el('td', { text: x.joined }),
      el('td', { class: 'wide', text: x.questions }),
      el('td', { class: 'wide', text: x.comments }),
      el('td', {}, x.open ? el('a', { href: '/teacher/' + x.code, text: '操作画面' }) : null, ' ',
        el('a', { href: '/teacher/' + x.code + '/report', text: 'レポート' })))));
  }
  $('#create').addEventListener('submit', async (e) => {
    e.preventDefault();
    const r = await fetch('/api/teacher/rooms', {
      method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Zawameki': '1' },
      body: JSON.stringify({ title: $('#title').value }),
    });
    if (!r.ok) { Z.toast('部屋を開けませんでした'); return; }
    const { code } = await r.json();
    location.href = '/teacher/' + code;
  });
  const n = new Date();
  $('#title').value = (n.getMonth() + 1) + '/' + n.getDate() + ' の講義';
  load();
})();
