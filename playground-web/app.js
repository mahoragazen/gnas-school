// ============================================================
// BUSINESS PLAYGROUND v3 — Eden Pantheon
// Roman × Japanese × Chinese deity roster
// ============================================================

const DEITIES = {
  mercury: {
    name: 'เมอร์คิวรี', en: 'Mercury · Mercurius', role: 'Orchestrator', emoji: '⚡',
    pantheon: 'โรมัน',
    desc: 'เทพผู้ส่งสารและกลยุทธ์ — รับคำสั่งจากเก้าแล้วกระจายงานให้เทพทั้ง 9 องค์ สวมปีกที่หมวกและรองเท้า ถือคทาแห่งงู (caduceus) อยู่ใต้ torii gate กลางสวน',
    stats: [{ v: '9', l: 'เทพในสังกัด' }, { v: '24h', l: 'ทำงาน' }, { v: '∞', l: 'speed' }],
    tasks: [
      'ส่งคำสั่งให้อูซูเมะเตรียม live 19:00',
      'แจ้งฉางเจี๋ยเขียน carousel หัวข้อ #43',
      '✓ ส่งสรุปยอดวันนี้ให้ไฉเสิน'
    ]
  },
  uzume: {
    name: 'อูซูเมะ', en: 'Ame-no-Uzume 天鈿女命', role: 'TikTok Live', emoji: '🎭',
    pantheon: 'ญี่ปุ่น',
    desc: 'เทพีญี่ปุ่นแห่งการเต้นรำและความสนุก — เคยเต้นจนเทพีอามาเทราซุออกจากถ้ำ ทำให้โลกกลับมามีแสง ตอนนี้รับผิดชอบ live ทุกครั้ง ดึงคนดูด้วยพลังเดียวกัน',
    stats: [{ v: '19:00', l: 'live ถัดไป' }, { v: '127', l: 'avg viewer' }, { v: '12', l: 'live เดือนนี้' }],
    tasks: [
      'เตรียม script สำหรับ live 19:00',
      'หา top 5 product สำหรับ live',
      '✓ เปิด OBS preset ไว้แล้ว'
    ]
  },
  cangjie: {
    name: 'ฉางเจี๋ย', en: 'Cangjie 倉頡', role: 'Content Carousel', emoji: '📿',
    pantheon: 'จีน',
    desc: 'เทพจีนผู้คิดอักษรจีนทั้งหมด มี 4 ตาเห็นทุกอย่างในจักรวาล — ใช้พรสวรรค์เขียน carousel "7 ข้อคิดจากธรรมชาติ" ทุกสัปดาห์',
    stats: [{ v: '#43', l: 'หัวข้อล่าสุด' }, { v: '827', l: 'follower' }, { v: '6am', l: 'โพสต์พรุ่งนี้' }],
    tasks: [
      'เขียน carousel #43 หัวข้อพระอาทิตย์',
      'ส่งภาพให้ Telegram bot gen',
      '✓ โพสต์ #42 → 234 view'
    ]
  },
  ebisu: {
    name: 'เอบิสุ', en: 'Ebisu 恵比寿', role: 'Product Hunter', emoji: '💰',
    pantheon: 'ญี่ปุ่น',
    desc: '1 ใน 7 เทพแห่งโชคลาภญี่ปุ่น เทพแห่งพ่อค้าและชาวประมง ยิ้มเสมอ ถือปลาตาเดียว — หา product trend ใน Shopee/Lazada/1688/TikTok Shop ที่ทำกำไรสูง',
    stats: [{ v: '5', l: 'lead ใหม่' }, { v: '38%', l: 'avg margin' }, { v: '247', l: 'product tracked' }],
    tasks: [
      'review 5 product lead จาก TikTok Shop',
      'คำนวณ margin + shipping',
      'ส่ง shortlist เข้า Telegram'
    ]
  },
  cupid: {
    name: 'คิวปิด', en: 'Cupid · Cupido', role: 'Facebook Ads', emoji: '💘',
    pantheon: 'โรมัน',
    desc: 'บุตรของ Venus ยิงธนูแห่งความรัก ใครถูกยิงตกหลุมรักทันที — ผูกกับ Facebook ads, ยิง creative เข้าหัวใจลูกค้า, คำนวณ ROAS',
    stats: [{ v: '2.3x', l: 'ROAS' }, { v: '฿8,400', l: 'spend วันนี้' }, { v: '3', l: 'active' }],
    tasks: [
      'เสนอ creative ใหม่ 3 ชิ้น',
      'หยุด campaign B (ROAS 1.2)',
      '✓ สรุป weekly report'
    ]
  },
  vulcan: {
    name: 'วัลแคน', en: 'Vulcan · Vulcanus', role: 'Inventory', emoji: '🔧',
    pantheon: 'โรมัน',
    desc: 'เทพช่างตีเหล็กโรมัน ผู้สร้างอาวุธของเทพทั้งหมด มีโรงตีเหล็กในภูเขาไฟ — ดูแลสต็อกร้านและคลังบ้าน เตือนเมื่อ stock ต่ำ',
    stats: [{ v: '247', l: 'SKU' }, { v: '2', l: 'low stock' }, { v: '฿128k', l: 'value' }],
    tasks: [
      '⚠ สั่ง yogurt cup 100ml (เหลือ 18)',
      '⚠ สั่ง straw biodegradable (เหลือ 50)',
      'นับสต็อกประจำสัปดาห์'
    ]
  },
  caishen: {
    name: 'ไฉเสิน', en: 'Caishen 財神', role: 'Accountant', emoji: '💎',
    pantheon: 'จีน',
    desc: 'เทพจีนแห่งทรัพย์สิน ขี่เสือ ถือทองคำแท่ง (yuanbao) ผู้บันดาลความร่ำรวยให้คนทำธุรกิจ — บันทึก ledger ทุกธุรกิจ + สรุปกำไรขาดทุน',
    stats: [{ v: '฿42,580', l: 'รายได้' }, { v: '฿18,200', l: 'ค่าใช้จ่าย' }, { v: '+฿24,380', l: 'กำไร' }],
    tasks: [
      'บันทึกรายรับจาก Grab order',
      'export ledger ไป Google Sheet',
      'review รายจ่ายของคิวปิด'
    ]
  },
  ceres: {
    name: 'เซเรส', en: 'Ceres', role: 'Delivery', emoji: '🍱',
    pantheon: 'โรมัน',
    desc: 'เทพีโรมันแห่งธัญพืชและความอุดมสมบูรณ์ สวมมงกุฎข้าวสาลี ถือ cornucopia (เขาแห่งความอุดมสมบูรณ์) — รับ order จาก LINE/Grab/LineMan + จัดคิวครัว',
    stats: [{ v: '12', l: 'order รอ' }, { v: '8', l: 'อยู่ครัว' }, { v: '23 นาที', l: 'avg time' }],
    tasks: [
      'แจ้งครัวเตรียม 3 order Grab',
      'ติดต่อไรเดอร์ LineMan',
      '✓ ส่ง 8 order สำเร็จเช้านี้'
    ]
  },
  tenjin: {
    name: 'เทนจิน', en: 'Tenjin 天神', role: 'GNAS School', emoji: '📚',
    pantheon: 'ญี่ปุ่น',
    desc: 'Sugawara Michizane นักวิชาการเอกในประวัติศาสตร์ที่ถูกบูชาเป็นเทพแห่งการศึกษา นักเรียนญี่ปุ่นไหว้ก่อนสอบ — ดูแลตารางครู Tsuguji & Erina + visa + student intake',
    stats: [{ v: '12 ก.ค.', l: 'visa' }, { v: '18', l: 'นักเรียน' }, { v: '4', l: 'ห้อง' }],
    tasks: [
      'เตรียมเอกสาร visa Tsuguji',
      'review student application 3 คน',
      'ออก invoice เดือน มิ.ย.'
    ]
  },
  niuwang: {
    name: 'หนิวหวัง', en: 'Niu Wang 牛王', role: 'North14 Yogurt', emoji: '🐄',
    pantheon: 'จีน',
    desc: 'ราชาวัวในตำนานจีน เทพคุ้มครองโคและฟาร์มเลี้ยงสัตว์ มีเขาวัวสีขาวสง่างาม — ประสานพี่ป้องเรื่อง Greek Yogurt ที่โคราช + content ใหม่',
    stats: [{ v: '฿14,200', l: 'ยอดสัปดาห์' }, { v: '0', l: 'งานค้าง' }, { v: '7', l: 'โพสต์' }],
    tasks: [
      'รอ update content ใหม่จากพี่ป้อง',
      'review ยอดขายโคราชวีคนี้'
    ]
  }
};

// ===== Live clock + phase =====
function updateClock() {
  const now = new Date();
  const hh = String(now.getHours()).padStart(2, '0');
  const mm = String(now.getMinutes()).padStart(2, '0');
  document.getElementById('clock').textContent = `${hh}:${mm}`;
  const hour = now.getHours();
  let phase, icon;
  if (hour >= 5 && hour < 12) { phase = 'เช้า'; icon = '☀'; }
  else if (hour >= 12 && hour < 17) { phase = 'บ่าย'; icon = '🌤'; }
  else if (hour >= 17 && hour < 20) { phase = 'เย็น'; icon = '🌅'; }
  else { phase = 'ค่ำ'; icon = '🌙'; }
  const el = document.getElementById('phaseIndicator');
  el.querySelector('.phase-icon').textContent = icon;
  el.querySelector('.phase-text').textContent = phase;
}
updateClock();
setInterval(updateClock, 30000);

// ===== Activity log =====
const LOG_MESSAGES = [
  { d: 'uzume', m: 'เตรียม script สำหรับ live 19:00 เสร็จแล้ว' },
  { d: 'cangjie', m: 'โพสต์ carousel #42 สำเร็จ → 234 view ใน 30 นาที' },
  { d: 'ebisu', m: 'เจอ product trend ใหม่ 5 ตัวจาก TikTok Shop' },
  { d: 'cupid', m: 'campaign A: ROAS 2.3 — ขออนุญาตเพิ่ม budget' },
  { d: 'vulcan', m: '⚠ yogurt cup เหลือ 18 หน่วย — แนะนำสั่งใหม่' },
  { d: 'caishen', m: 'บันทึก +฿1,200 จาก Grab order #4821' },
  { d: 'ceres', m: 'รับ order ใหม่ 3 รายการจาก LINE OA' },
  { d: 'tenjin', m: 'เตือน: visa Tsuguji ครบ 12 ก.ค. (33 วัน)' },
  { d: 'niuwang', m: 'พี่ป้องส่ง content ใหม่ 2 reel มาให้' },
  { d: 'mercury', m: 'สรุปยอด 9 เทพ → ส่งเข้า Telegram ของเก้า' },
  { d: 'uzume', m: 'top product live: นาฬิกาลายกระดูก, มู่ลี่ผ้า, หินสี' },
  { d: 'cangjie', m: 'เริ่มเขียน carousel #43 หัวข้อพระอาทิตย์' },
  { d: 'caishen', m: 'รายได้วันนี้แตะ ฿42,580 (เกินเป้า 18%)' },
  { d: 'cupid', m: 'หยุด campaign B อัตโนมัติ (ROAS 1.2)' },
  { d: 'ceres', m: 'ส่ง order สำเร็จ 8 จาก 12 รายการเช้านี้' }
];

const feed = document.getElementById('logFeed');
let logIdx = 0;

function addLogEntry(msgObj, animate = true) {
  const d = DEITIES[msgObj.d] || { name: 'ระบบ' };
  const now = new Date();
  const time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`;
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.innerHTML = `
    <span class="log-time">${time}</span>
    <span class="log-deity">${d.name}</span>
    <span class="log-msg">${msgObj.m}</span>
  `;
  if (animate) feed.insertBefore(entry, feed.firstChild);
  else feed.appendChild(entry);
  while (feed.children.length > 20) feed.removeChild(feed.lastChild);
}

for (let i = 0; i < 6; i++) {
  addLogEntry(LOG_MESSAGES[i], false);
  logIdx = i + 1;
}

function streamLog() {
  const next = LOG_MESSAGES[logIdx % LOG_MESSAGES.length];
  addLogEntry(next);
  logIdx++;
  setTimeout(streamLog, 4000 + Math.random() * 3000);
}
setTimeout(streamLog, 3000);

// ===== Pan / Zoom world engine =====
const viewport = document.getElementById('viewport');
const world = document.getElementById('world');
const miniView = document.getElementById('miniView');
const WORLD_W = 2400, WORLD_H = 1600;
const MINI_W = 180, MINI_H = 120, MINI_SCALE = MINI_W / WORLD_W; // 0.075

let scale = 1, tx = 0, ty = 0;
const MIN_SCALE = 0.18, MAX_SCALE = 2.2;

function clampPan() {
  const vw = viewport.clientWidth, vh = viewport.clientHeight;
  const worldW = WORLD_W * scale, worldH = WORLD_H * scale;
  // allow some margin; keep world from drifting fully off-screen
  if (worldW <= vw) tx = (vw - worldW) / 2;
  else tx = Math.min(0, Math.max(vw - worldW, tx));
  if (worldH <= vh) ty = (vh - worldH) / 2;
  else ty = Math.min(0, Math.max(vh - worldH, ty));
}

function applyTransform() {
  clampPan();
  world.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;
  // minimap viewport rectangle
  const vw = viewport.clientWidth, vh = viewport.clientHeight;
  const viewWorldX = -tx / scale, viewWorldY = -ty / scale;
  const viewWorldW = vw / scale, viewWorldH = vh / scale;
  // clamp the minimap rectangle inside the minimap bounds
  let mx = Math.max(0, viewWorldX * MINI_SCALE);
  let my = Math.max(0, viewWorldY * MINI_SCALE);
  let mw = Math.min(MINI_W - mx, viewWorldW * MINI_SCALE);
  let mh = Math.min(MINI_H - my, viewWorldH * MINI_SCALE);
  miniView.style.left = mx + 'px';
  miniView.style.top = my + 'px';
  miniView.style.width = Math.max(0, mw) + 'px';
  miniView.style.height = Math.max(0, mh) + 'px';
}

function zoomAt(cx, cy, newScale) {
  newScale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, newScale));
  // keep the world point under cursor fixed
  const worldX = (cx - tx) / scale;
  const worldY = (cy - ty) / scale;
  scale = newScale;
  tx = cx - worldX * scale;
  ty = cy - worldY * scale;
  applyTransform();
}

// Fit world to viewport, centered on plaza
function fitView() {
  const vw = viewport.clientWidth, vh = viewport.clientHeight;
  // 0.86 leaves a comfortable margin so the whole garden is visible
  scale = Math.min(vw / WORLD_W, vh / WORLD_H) * 0.86;
  scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, scale));
  tx = (vw - WORLD_W * scale) / 2;
  ty = (vh - WORLD_H * scale) / 2;
  applyTransform();
}

// Focus a world coordinate at a given scale (used when opening a deity)
function focusWorld(wx, wy, targetScale) {
  const vw = viewport.clientWidth, vh = viewport.clientHeight;
  scale = Math.max(MIN_SCALE, Math.min(MAX_SCALE, targetScale));
  tx = vw / 2 - wx * scale;
  ty = vh / 2 - wy * scale;
  applyTransform();
}

// Wheel zoom
viewport.addEventListener('wheel', (e) => {
  e.preventDefault();
  const rect = viewport.getBoundingClientRect();
  const cx = e.clientX - rect.left, cy = e.clientY - rect.top;
  const factor = e.deltaY < 0 ? 1.12 : 0.89;
  zoomAt(cx, cy, scale * factor);
}, { passive: false });

// Drag to pan (pointer events) — suppress click if dragged
let dragging = false, dragMoved = false, startX = 0, startY = 0, startTx = 0, startTy = 0;
let pointers = new Map();
let pinchDist = 0;

viewport.addEventListener('pointerdown', (e) => {
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (pointers.size === 1) {
    dragging = true; dragMoved = false;
    startX = e.clientX; startY = e.clientY;
    startTx = tx; startTy = ty;
    viewport.classList.add('grabbing');
  } else if (pointers.size === 2) {
    const pts = [...pointers.values()];
    pinchDist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
  }
});

viewport.addEventListener('pointermove', (e) => {
  if (!pointers.has(e.pointerId)) return;
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });

  if (pointers.size === 2) {
    const pts = [...pointers.values()];
    const dist = Math.hypot(pts[0].x - pts[1].x, pts[0].y - pts[1].y);
    if (pinchDist > 0) {
      const rect = viewport.getBoundingClientRect();
      const midX = (pts[0].x + pts[1].x) / 2 - rect.left;
      const midY = (pts[0].y + pts[1].y) / 2 - rect.top;
      zoomAt(midX, midY, scale * (dist / pinchDist));
    }
    pinchDist = dist;
    dragMoved = true;
    return;
  }

  if (dragging) {
    const dx = e.clientX - startX, dy = e.clientY - startY;
    if (Math.abs(dx) > 4 || Math.abs(dy) > 4) dragMoved = true;
    tx = startTx + dx; ty = startTy + dy;
    applyTransform();
  }
});

function endPointer(e) {
  pointers.delete(e.pointerId);
  if (pointers.size < 2) pinchDist = 0;
  if (pointers.size === 0) { dragging = false; viewport.classList.remove('grabbing'); }
}
viewport.addEventListener('pointerup', endPointer);
viewport.addEventListener('pointercancel', endPointer);
viewport.addEventListener('pointerleave', (e) => { if (pointers.size === 0) { dragging = false; viewport.classList.remove('grabbing'); } });

// Zoom buttons
document.getElementById('zoomIn').addEventListener('click', () => {
  zoomAt(viewport.clientWidth / 2, viewport.clientHeight / 2, scale * 1.25);
});
document.getElementById('zoomOut').addEventListener('click', () => {
  zoomAt(viewport.clientWidth / 2, viewport.clientHeight / 2, scale * 0.8);
});
document.getElementById('zoomReset').addEventListener('click', fitView);

// Minimap click-to-navigate
document.getElementById('minimap').addEventListener('click', (e) => {
  const rect = e.currentTarget.getBoundingClientRect();
  const wx = (e.clientX - rect.left) / MINI_SCALE;
  const wy = (e.clientY - rect.top) / MINI_SCALE;
  focusWorld(wx, wy, Math.max(scale, 0.9));
});

window.addEventListener('resize', applyTransform);
// init after layout — fit reliably even if fonts/layout settle late
requestAnimationFrame(fitView);
window.addEventListener('load', fitView);
setTimeout(fitView, 250);

// ===== Modal =====
const modal = document.getElementById('modal');
const modalName = document.getElementById('modalName');
const modalRole = document.getElementById('modalRole');
const modalDesc = document.getElementById('modalDesc');
const modalAvatar = document.getElementById('modalAvatar');
const modalStats = document.getElementById('modalStats');
const modalTasks = document.getElementById('modalTasks');
const modalInput = document.getElementById('modalInput');
const modalSend = document.getElementById('modalSend');

function openDeityModal(key) {
  const d = DEITIES[key];
  if (!d) return;
  modalAvatar.textContent = d.emoji;
  modalName.textContent = `${d.name} · ${d.en}`;
  modalRole.textContent = `${d.role} · เทพ${d.pantheon}`;
  modalDesc.textContent = d.desc;
  modalStats.innerHTML = d.stats.map(s => `
    <div class="modal-stat">
      <div class="v">${s.v}</div>
      <div class="l">${s.l}</div>
    </div>
  `).join('');
  modalTasks.innerHTML = d.tasks.map(t => {
    const done = t.startsWith('✓');
    return `<li class="${done ? 'done' : ''}">${t}</li>`;
  }).join('');
  modalInput.value = '';
  modal.hidden = false;
  setTimeout(() => modalInput.focus(), 100);
}

document.querySelectorAll('[data-deity]').forEach(btn => {
  btn.addEventListener('click', () => {
    if (dragMoved) return; // ignore click that ended a pan/pinch
    openDeityModal(btn.dataset.deity);
  });
});

document.getElementById('modalClose').addEventListener('click', () => modal.hidden = true);
modal.addEventListener('click', (e) => { if (e.target === modal) modal.hidden = true; });
document.addEventListener('keydown', (e) => { if (e.key === 'Escape') modal.hidden = true; });

modalSend.addEventListener('click', sendCmd);
modalInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendCmd(); });

function sendCmd() {
  const text = modalInput.value.trim();
  if (!text) return;
  const deityKey = Object.keys(DEITIES).find(k => DEITIES[k].name === modalName.textContent.split(' · ')[0]);
  addLogEntry({ d: deityKey || 'mercury', m: `📨 รับคำสั่ง: "${text}"` });
  modalInput.value = '';
  modal.hidden = true;
}

// ===== Log drawer =====
const logbook = document.getElementById('logbook');
const logToggle = document.getElementById('logToggle');
const logClose = document.getElementById('logClose');
logToggle.addEventListener('click', () => logbook.classList.toggle('open'));
logClose.addEventListener('click', () => logbook.classList.remove('open'));

// ===== Tickers =====
const queueEl = document.getElementById('queueCount');
let queue = 7;
setInterval(() => {
  queue = Math.max(0, queue + (Math.random() < 0.4 ? -1 : Math.random() < 0.6 ? 0 : 1));
  queueEl.textContent = queue;
}, 5000);

const revEl = document.getElementById('todayRevenue');
let revenue = 42580;
setInterval(() => {
  if (Math.random() < 0.5) {
    revenue += Math.floor(Math.random() * 400) + 50;
    revEl.textContent = `฿${revenue.toLocaleString()}`;
    revEl.style.color = '#5ee3d8';
    setTimeout(() => revEl.style.color = '', 600);
  }
}, 6000);
