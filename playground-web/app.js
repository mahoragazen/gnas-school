// ============================================================
// BUSINESS PLAYGROUND — Pantheon HQ runtime
// ============================================================

const DEITIES = {
  hermes: {
    name: 'เฮอร์มีส', en: 'Hermes', role: 'Orchestrator', emoji: '✨',
    pantheon: 'กรีก',
    desc: 'เทพผู้ส่งสารและกลยุทธ์ — รับคำสั่งจากเก้าแล้วกระจายงานให้เทพคนอื่นๆ ทั้งหมด อยู่ตรงกลางวิหารเหมือนใจกลางจักรวาล',
    stats: [{ v: '9', l: 'เทพในสังกัด' }, { v: '24h', l: 'ทำงาน' }, { v: '∞', l: 'speed' }],
    tasks: [
      'ส่งคำสั่งให้นาฏราชเตรียม live 19:00',
      'แจ้งนารทเขียน carousel หัวข้อ #43',
      '✓ ส่งสรุปยอดวันนี้ให้กุเวร'
    ]
  },
  nataraja: {
    name: 'นาฏราช', en: 'Nataraja', role: 'TikTok Live Producer', emoji: '🎭',
    pantheon: 'ฮินดู',
    desc: 'พระศิวะปางเจ้าแห่งนาฏกรรม — รับผิดชอบ live ทุกครั้ง เขียน script, หาสินค้า, เตรียม OBS preset, สรุปสถิติ',
    stats: [{ v: '19:00', l: 'live ถัดไป' }, { v: '127', l: 'avg viewer' }, { v: '12', l: 'live เดือนนี้' }],
    tasks: [
      'เตรียม script สำหรับ live 19:00',
      'หา top 5 product สำหรับ live',
      '✓ เปิด OBS preset ไว้แล้ว'
    ]
  },
  narada: {
    name: 'นารท', en: 'Narada', role: 'Content Carousel', emoji: '📿',
    pantheon: 'ฮินดู',
    desc: 'นารทมุนี เทพบุตรนักดนตรีผู้ส่งผ่านความรู้ระหว่างโลก — เขียน carousel "7 ข้อคิดจากธรรมชาติ" + ออกแบบ + โพสต์',
    stats: [{ v: '#43', l: 'หัวข้อล่าสุด' }, { v: '827', l: 'follower' }, { v: '6am', l: 'โพสต์พรุ่งนี้' }],
    tasks: [
      'เขียน carousel หัวข้อ #43 (พระอาทิตย์)',
      'ส่งภาพให้ Telegram bot gen',
      '✓ โพสต์ #42 → 234 view'
    ]
  },
  lakshmi: {
    name: 'ลักษมี', en: 'Lakshmi', role: 'Product Hunter', emoji: '💰',
    pantheon: 'ฮินดู',
    desc: 'พระเทวีแห่งความมั่งคั่ง — crawl Shopee/Lazada/1688/TikTok Shop หา product trend ที่ทำกำไรได้สูง',
    stats: [{ v: '5', l: 'lead ใหม่' }, { v: '38%', l: 'avg margin' }, { v: '247', l: 'product tracked' }],
    tasks: [
      'review 5 product lead จาก TikTok Shop',
      'คำนวณ margin + shipping',
      'ส่ง shortlist เข้า Telegram'
    ]
  },
  kamadeva: {
    name: 'กามเทพ', en: 'Kamadeva', role: 'Facebook Ads', emoji: '💘',
    pantheon: 'ฮินดู',
    desc: 'เทพแห่งความรักและความปรารถนา ยิงธนูดอกไม้เข้าหัวใจลูกค้า — จัดการ Facebook ads ทุก campaign',
    stats: [{ v: '2.3x', l: 'ROAS' }, { v: '฿8,400', l: 'spend วันนี้' }, { v: '3', l: 'active' }],
    tasks: [
      'เสนอ creative ใหม่ 3 ชิ้น',
      'หยุด campaign B (ROAS 1.2)',
      '✓ สรุป weekly report'
    ]
  },
  vishvakarma: {
    name: 'วิศวกรรม', en: 'Vishvakarma', role: 'Inventory Keeper', emoji: '🔧',
    pantheon: 'ฮินดู',
    desc: 'เทพช่างศิลปะ ผู้สร้างเครื่องมือของเทพ — ดูแลสต็อกร้านและคลังบ้าน เตือนเมื่อสต็อกต่ำ',
    stats: [{ v: '247', l: 'SKU ทั้งหมด' }, { v: '2', l: 'low stock' }, { v: '฿128k', l: 'inventory value' }],
    tasks: [
      '⚠ สั่ง yogurt cup 100ml (เหลือ 18)',
      '⚠ สั่ง straw biodegradable (เหลือ 50)',
      'นับสต็อกประจำสัปดาห์ (วันอาทิตย์)'
    ]
  },
  kubera: {
    name: 'กุเวร', en: 'Kubera', role: 'Accountant', emoji: '💎',
    pantheon: 'ฮินดู',
    desc: 'ท้าวกุเวร เจ้าคลังทรัพย์ของเทพ — บันทึกรายรับรายจ่ายแยก ledger ทุกธุรกิจ + สรุปกำไรรายวัน/เดือน',
    stats: [{ v: '฿42,580', l: 'รายได้วันนี้' }, { v: '฿18,200', l: 'ค่าใช้จ่าย' }, { v: '+฿24,380', l: 'กำไรสุทธิ' }],
    tasks: [
      'บันทึกรายรับจาก Grab order',
      'export ledger ไป Google Sheet',
      'review รายจ่ายของ Kamadeva'
    ]
  },
  annapurna: {
    name: 'อันนปุรณา', en: 'Annapurna', role: 'Delivery Dispatcher', emoji: '🍱',
    pantheon: 'ฮินดู',
    desc: 'เทพีแห่งอาหารและการเลี้ยงดู — รับ order จาก LINE OA / Grab / LineMan, จัดคิวครัว, แจ้งไรเดอร์',
    stats: [{ v: '12', l: 'order รอ' }, { v: '8', l: 'อยู่ครัว' }, { v: '23 min', l: 'avg time' }],
    tasks: [
      'แจ้งครัวเตรียม 3 order Grab',
      'ติดต่อไรเดอร์ LineMan',
      '✓ ส่ง 8 order สำเร็จเช้านี้'
    ]
  },
  saraswati: {
    name: 'สรัสวดี', en: 'Saraswati', role: 'GNAS School Ops', emoji: '📚',
    pantheon: 'ฮินดู',
    desc: 'เทพีแห่งความรู้ ศิลปะ และการศึกษา — ดูแลตารางครู Tsuguji & Erina + visa + student intake pipeline',
    stats: [{ v: '12 ก.ค.', l: 'visa ต่อ' }, { v: '18', l: 'นักเรียน' }, { v: '4', l: 'ห้องเรียน' }],
    tasks: [
      'เตรียมเอกสาร visa Tsuguji (ครบ 12 ก.ค.)',
      'review student application 3 คน',
      'ออก invoice เดือน มิ.ย.'
    ]
  },
  krishna: {
    name: 'กฤษณะ', en: 'Krishna', role: 'North14 Yogurt Liaison', emoji: '🐄',
    pantheon: 'ฮินดู',
    desc: 'พระกฤษณะ เทพคนเลี้ยงโคผู้รักนมเปรี้ยว — ประสานพี่ป้องเรื่อง Greek Yogurt ที่โคราช + content',
    stats: [{ v: '฿14,200', l: 'ยอดสัปดาห์' }, { v: '0', l: 'งานค้าง' }, { v: '7', l: 'TikTok โพสต์' }],
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
  { d: 'nataraja', m: 'เตรียม script สำหรับ live 19:00 เสร็จแล้ว' },
  { d: 'narada', m: 'โพสต์ carousel #42 สำเร็จ → 234 view ใน 30 นาที' },
  { d: 'lakshmi', m: 'เจอ product trend ใหม่ 5 ตัวจาก TikTok Shop' },
  { d: 'kamadeva', m: 'campaign A: ROAS 2.3 — ขออนุญาตเพิ่ม budget' },
  { d: 'vishvakarma', m: '⚠ yogurt cup เหลือ 18 หน่วย — แนะนำสั่งใหม่' },
  { d: 'kubera', m: 'บันทึก +฿1,200 จาก Grab order #4821' },
  { d: 'annapurna', m: 'รับ order ใหม่ 3 รายการจาก LINE OA' },
  { d: 'saraswati', m: 'เตือน: visa Tsuguji ครบ 12 ก.ค. (33 วัน)' },
  { d: 'krishna', m: 'พี่ป้องส่ง content ใหม่ 2 reel มาให้' },
  { d: 'hermes', m: 'สรุปยอด 9 เทพ → ส่งเข้า Telegram ของเก้า' },
  { d: 'nataraja', m: 'top product live: นาฬิกาลายกระดูก, มู่ลี่ผ้า, หินสี' },
  { d: 'narada', m: 'เริ่มเขียน carousel #43 หัวข้อพระอาทิตย์' },
  { d: 'kubera', m: 'รายได้วันนี้แตะ ฿42,580 (เกินเป้า 18%)' },
  { d: 'kamadeva', m: 'หยุด campaign B อัตโนมัติ (ROAS 1.2)' },
  { d: 'annapurna', m: 'ส่ง order สำเร็จ 8 จาก 12 รายการเช้านี้' }
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
  if (animate) {
    feed.insertBefore(entry, feed.firstChild);
  } else {
    feed.appendChild(entry);
  }
  // limit to 20 entries
  while (feed.children.length > 20) feed.removeChild(feed.lastChild);
}

// seed initial 6 entries
for (let i = 0; i < 6; i++) {
  addLogEntry(LOG_MESSAGES[i], false);
  logIdx = i + 1;
}

// add new entry every 4-7 seconds
function streamLog() {
  const next = LOG_MESSAGES[logIdx % LOG_MESSAGES.length];
  addLogEntry(next);
  logIdx++;
  const delay = 4000 + Math.random() * 3000;
  setTimeout(streamLog, delay);
}
setTimeout(streamLog, 3000);

// ===== Modal handling =====
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
  btn.addEventListener('click', () => openDeityModal(btn.dataset.deity));
});

document.getElementById('modalClose').addEventListener('click', () => modal.hidden = true);
modal.addEventListener('click', (e) => {
  if (e.target === modal) modal.hidden = true;
});
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') modal.hidden = true;
});

modalSend.addEventListener('click', sendCmd);
modalInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendCmd(); });

function sendCmd() {
  const text = modalInput.value.trim();
  if (!text) return;
  const deityKey = Object.keys(DEITIES).find(k => DEITIES[k].name === modalName.textContent.split(' · ')[0]);
  addLogEntry({ d: deityKey || 'hermes', m: `📨 รับคำสั่ง: "${text}"` });
  modalInput.value = '';
  modal.hidden = true;
}

// ===== Log drawer toggle =====
const logbook = document.getElementById('logbook');
const logToggle = document.getElementById('logToggle');
const logClose = document.getElementById('logClose');
logToggle.addEventListener('click', () => logbook.classList.toggle('open'));
logClose.addEventListener('click', () => logbook.classList.remove('open'));

// ===== Queue count rotation =====
const queueEl = document.getElementById('queueCount');
let queue = 7;
setInterval(() => {
  queue = Math.max(0, queue + (Math.random() < 0.4 ? -1 : Math.random() < 0.6 ? 0 : 1));
  queueEl.textContent = queue;
}, 5000);

// ===== Revenue counter that ticks up =====
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
