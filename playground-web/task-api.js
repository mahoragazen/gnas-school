#!/usr/bin/env node
// PANTHEON Task API — bridges PANTHEON UI ↔ Obsidian wiki/tasks/*.md
// Port 8766. Reads/writes markdown files with YAML frontmatter.

const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const https = require('https');

// Load .env from same directory
const envPath = path.join(__dirname, '.env');
if (fs.existsSync(envPath)) {
  fs.readFileSync(envPath, 'utf8').split('\n').forEach(line => {
    const [k, ...v] = line.split('=');
    if (k && v.length) process.env[k.trim()] = v.join('=').trim();
  });
}

const TASKS_DIR = path.join(
  process.env.HOME,
  'internalMac/Obsidian/Obsidian Vault/wiki/tasks'
);
const PORT = 8766;

// ── Telegram notify ───────────────────────────────────────────────────────────
const TG_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TG_CHAT  = process.env.TELEGRAM_CHAT_ID;

const DEITY_EMOJI = {
  mercury:'⚡', uzume:'🎭', cangjie:'📿', cupid:'💘', ebisu:'🎣',
  vulcan:'🔨', caishen:'💰', ceres:'🌾', tenjin:'📚', niuwang:'🐄',
  konohana:'🌸', baozheng:'⚖',
};
const STATUS_TH = {
  todo:'⬜ ยังไม่เริ่ม', in_progress:'🔵 กำลังทำ',
  pending_qa:'🟡 รอ QA', approved:'✅ อนุมัติ', rejected:'🔴 ตีกลับ',
};

function tgSend(text) {
  if (!TG_TOKEN || !TG_CHAT) return;
  const body = JSON.stringify({ chat_id: TG_CHAT, text, parse_mode: 'HTML' });
  const req = https.request({
    hostname: 'api.telegram.org',
    path: `/bot${TG_TOKEN}/sendMessage`,
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Content-Length': Buffer.byteLength(body) },
  }, () => {});
  req.on('error', () => {});
  req.write(body);
  req.end();
}

function notifyCreate(task) {
  const e = DEITY_EMOJI[task.assignee] || '🔔';
  tgSend(
    `🏛 <b>PANTHEON · งานใหม่</b>\n` +
    `📋 ${task.title}\n` +
    `${e} มอบหมาย → <b>${task.assignee}</b> [${task.type}]\n` +
    `<i>ID: ${task.id}</i>`
  );
}

function notifyStatusChange(task, oldStatus) {
  if (oldStatus === task.status) return;
  const e = DEITY_EMOJI[task.assignee] || '🔔';
  const st = STATUS_TH[task.status] || task.status;
  let extra = '';
  if (task.status === 'pending_qa') {
    extra = `\n⚖ เปาเจิ้งต้องตรวจสอบ`;
  } else if (task.status === 'rejected') {
    const note = (task.qa_note || '').replace(/^"|"$/g, '');
    extra = `\n💬 เหตุผล: ${note || '-'}`;
  } else if (task.status === 'approved') {
    extra = `\n🎉 ผ่านการตรวจสอบแล้ว`;
  }
  tgSend(
    `🏛 <b>PANTHEON · อัปเดตงาน</b>\n` +
    `📋 ${task.title}\n` +
    `${e} ${task.assignee} · ${st}${extra}\n` +
    `<i>ID: ${task.id}</i>`
  );
}

// ── YAML frontmatter helpers ──────────────────────────────────────────────────
function parseFrontmatter(content) {
  const m = content.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  if (!m) return { meta: {}, body: content };
  const meta = {};
  m[1].split('\n').forEach(line => {
    const [k, ...v] = line.split(':');
    if (k) meta[k.trim()] = v.join(':').trim().replace(/^"(.*)"$/, '$1');
  });
  return { meta, body: m[2].trim() };
}

function buildFrontmatter(meta, body) {
  const fm = Object.entries(meta).map(([k, v]) => `${k}: ${v}`).join('\n');
  return `---\n${fm}\n---\n${body ? '\n' + body : ''}`;
}

// ── File I/O ──────────────────────────────────────────────────────────────────
function listTasks() {
  if (!fs.existsSync(TASKS_DIR)) return [];
  return fs.readdirSync(TASKS_DIR)
    .filter(f => f.endsWith('.md'))
    .map(f => {
      const raw = fs.readFileSync(path.join(TASKS_DIR, f), 'utf8');
      const { meta, body } = parseFrontmatter(raw);
      return { ...meta, body, _file: f };
    })
    .sort((a, b) => (b.created || '').localeCompare(a.created || ''));
}

function getTask(id) {
  const all = listTasks();
  return all.find(t => t.id === id);
}

function writeTask(meta, body = '') {
  const filename = `${meta.id}.md`;
  fs.writeFileSync(path.join(TASKS_DIR, filename), buildFrontmatter(meta, body));
}

function deleteTask(id) {
  const task = getTask(id);
  if (!task) return false;
  fs.unlinkSync(path.join(TASKS_DIR, task._file));
  return true;
}

// ── HTTP server ───────────────────────────────────────────────────────────────
function send(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
  });
  res.end(body);
}

function readBody(req) {
  return new Promise(resolve => {
    let data = '';
    req.on('data', c => data += c);
    req.on('end', () => { try { resolve(JSON.parse(data)); } catch { resolve({}); } });
  });
}

const server = http.createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const parts = url.pathname.split('/').filter(Boolean); // ['api','tasks',id?]

  if (req.method === 'OPTIONS') return send(res, 200, {});

  // GET /api/tasks[?assignee=X&status=Y]
  if (req.method === 'GET' && parts[1] === 'tasks' && !parts[2]) {
    let tasks = listTasks();
    const assignee = url.searchParams.get('assignee');
    const status = url.searchParams.get('status');
    if (assignee) tasks = tasks.filter(t => t.assignee === assignee);
    if (status) tasks = tasks.filter(t => t.status === status);
    return send(res, 200, tasks);
  }

  // GET /api/tasks/:id
  if (req.method === 'GET' && parts[1] === 'tasks' && parts[2]) {
    const task = getTask(parts[2]);
    return task ? send(res, 200, task) : send(res, 404, { error: 'not found' });
  }

  // POST /api/tasks — create
  if (req.method === 'POST' && parts[1] === 'tasks') {
    const body = await readBody(req);
    const now = new Date().toISOString();
    const id = 'task-' + now.slice(0, 10).replace(/-/g, '') + '-' + crypto.randomBytes(3).toString('hex');
    const meta = {
      id,
      title: body.title || 'งานใหม่',
      assignee: body.assignee || 'mercury',
      creator: body.creator || 'mercury',
      status: 'todo',
      type: body.type || 'general',
      created: now,
      updated: now,
      qa_note: '""',
    };
    writeTask(meta, body.body || '');
    const created = { ...meta, body: body.body || '' };
    notifyCreate(created);
    return send(res, 201, created);
  }

  // PUT /api/tasks/:id — update status/note
  if (req.method === 'PUT' && parts[1] === 'tasks' && parts[2]) {
    const existing = getTask(parts[2]);
    if (!existing) return send(res, 404, { error: 'not found' });
    const oldStatus = existing.status;
    const body = await readBody(req);
    const { _file, body: existingBody, ...meta } = existing;
    const updated = {
      ...meta,
      ...Object.fromEntries(
        Object.entries(body).filter(([k]) => !['id','created','_file','body'].includes(k))
      ),
      updated: new Date().toISOString(),
    };
    if (body.qa_note !== undefined) updated.qa_note = `"${body.qa_note}"`;
    writeTask(updated, body.body ?? existingBody);
    const result = { ...updated, body: body.body ?? existingBody };
    notifyStatusChange(result, oldStatus);
    return send(res, 200, result);
  }

  // DELETE /api/tasks/:id
  if (req.method === 'DELETE' && parts[1] === 'tasks' && parts[2]) {
    return deleteTask(parts[2])
      ? send(res, 200, { deleted: parts[2] })
      : send(res, 404, { error: 'not found' });
  }

  send(res, 404, { error: 'route not found' });
});

server.listen(PORT, () => {
  console.log(`[PANTHEON Task API] running on http://localhost:${PORT}`);
  console.log(`[PANTHEON Task API] tasks dir: ${TASKS_DIR}`);
});
