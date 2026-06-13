# PANTHEON · เทวาลัย — Business Command Center

Pixel-art command center สำหรับสั่งงานทีม agent (12 เทพ โรมัน × ญี่ปุ่น × จีน)
**Live:** https://gnasschool.com/playground

> ไฟล์ในโฟลเดอร์นี้คือ **source of truth** ของหน้า PANTHEON — sync แล้วกับตัว deploy จริง (2026-06-13)

---

## สถาปัตยกรรม

**Frontend (โฟลเดอร์นี้)** — static, ไม่มี build step
- `index.html` · `app.js` · `styles.css`
- `assets/characters/` — 12 เทพ + prajna · `assets/zones/` · `assets/sounds/`
- `data/stats.json` — followers/revenue (อัปเดตอัตโนมัติทุก 6 ชม. โดย `playground-update.sh`)

**Backend** — `~/internalMac/pantheon-agents/task-api.cjs` (localhost:8766, **local-only**)
- `GET /api/stats` · `GET/POST/PUT/DELETE /api/tasks` — task board ↔ Obsidian `wiki/tasks/*.md`
- `GET /api/feed` — activity log จริง (อ่าน `feed.ndjson` ที่ agent เขียน)
- `POST /api/run/:agent` — **สั่งรัน python agent จริง** (cangjie/raphael/bezalel/mercury/prajna)
- `GET /api/queue` — content calendar จาก Obsidian kanban

**Agents** — `~/internalMac/pantheon-agents/*.py`
- `cangjie.py` เสนอหัวข้อ → `raphael.py` เขียน 7 slides → `bezalel.py` render → Telegram
- `prajna.py` scrape สถิติ TikTok (scrape-creators) · `mercury_briefing.py` สรุปรายวัน

> เมื่อ backend ไม่ได้รัน (เช่นเปิดจากมือถือ/เว็บ production) ปุ่มสั่งงาน + board จะถูกซ่อนอัตโนมัติ
> เหลือเฉพาะ stats จาก `data/stats.json` — graceful degradation

---

## Deploy

```bash
cd ~/internalMac/gnas/website && ./node_modules/.bin/wrangler deploy   # → Cloudflare
```
อัตโนมัติ: `gnas/website/playground-update.sh` รันทุก 6 ชม. (launchd) — scrape followers → อัปเดต `stats.json` → deploy ถ้าตัวเลขเปลี่ยน

> ⚠️ ปัจจุบัน deploy มาจาก `gnas/website/playground/` (ไม่ได้ track ใน git) โฟลเดอร์นี้คือสำเนาที่ version-controlled — ควรรวมให้ deploy ดึงจาก git ในอนาคต
