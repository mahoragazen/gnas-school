#!/usr/bin/env python3
"""
Raphael · ราฟาเอล — Content Strategist agent
Picks up approved Cangjie themes, generates full carousel JSON schema
(matching auto_carousel.py spec) via DeepSeek, writes child task for Bezalel.

Schema includes: theme_name, theme_subtitle, source, highlight_color,
and 7 slides with per-slide bg/icon/quote/sub. NatGeo photography style.
"""
import os, sys, re, json, uuid, urllib.request
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
ROOT = Path(__file__).parent
VAULT = HOME / "internalMac/Obsidian/Obsidian Vault/wiki"
TASKS_DIR = VAULT / "tasks"
BG_DIR = HOME / "internalMac/NatGeo Backgrounds"
STATE_FILE = ROOT / "carousel_state.json"

LOG = Path("/tmp/raphael.log")

FEED_FILE = Path(__file__).parent / "feed.ndjson"
def feed(deity, msg):
    try:
        with FEED_FILE.open("a") as f:
            f.write(json.dumps({"t": datetime.now(timezone.utc).isoformat(), "d": deity, "m": msg}, ensure_ascii=False) + "\n")
    except Exception:
        pass

def log(msg):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)
    with LOG.open("a") as f:
        f.write(line + "\n")

def load_env():
    for line in (ROOT / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

def parse_frontmatter(text):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', text, re.DOTALL)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, m.group(2)

def find_approved_topics():
    out = []
    for f in sorted(TASKS_DIR.glob("task-*.md")):
        text = f.read_text()
        meta, body = parse_frontmatter(text)
        if (meta.get("assignee") == "cangjie"
            and meta.get("status") == "approved"
            and meta.get("next_stage") not in ("raphael_done", "raphael_quarantine")):
            out.append((f, meta, body))
    return out

# จำนวนครั้งสูงสุดที่ยอมให้ task ล้ม quality gate ก่อน quarantine (กันวนหยิบซ้ำทุกชั่วโมง = TG spam)
MAX_RAPHAEL_FAILS = 3

def bump_fail(parent_file):
    """เพิ่มตัวนับ raphael_fail_count ใน frontmatter ของ parent task.
    คืน (count, quarantined): ถ้าครบ MAX → set next_stage: raphael_quarantine (find_approved_topics ข้าม)."""
    text = parent_file.read_text()
    m = re.search(r'\nraphael_fail_count:\s*(\d+)', text)
    count = (int(m.group(1)) if m else 0) + 1
    if m:
        text = re.sub(r'(\nraphael_fail_count:\s*)\d+', f'\\g<1>{count}', text)
    else:
        text = re.sub(r'(\nupdated: [^\n]+)', f'\\1\nraphael_fail_count: {count}', text)
    quarantined = count >= MAX_RAPHAEL_FAILS
    if quarantined and "next_stage:" not in text:
        text = re.sub(r'(\nupdated: [^\n]+)', '\\1\nnext_stage: raphael_quarantine', text)
    elif quarantined:
        text = re.sub(r'(\nnext_stage:\s*)\S+', '\\1raphael_quarantine', text)
    parent_file.write_text(text)
    return count, quarantined

# SSOT กันเลข series ชนระบบเก่า: เลข series ใช้ร่วมกับ mahoraga-content/state.json
# (เคยมี 2 counter เดินอิสระ → pantheon ปั๊มทับ #45-52 ยุค test) ดู [[project_pantheon_pipeline]]
MAHORAGA_STATE = Path.home() / "internalMac/bots/mahoraga-content/automation/state.json"

def _highest_assigned_series():
    """เลข series สูงสุดที่ "ถูกจองแล้ว" จาก mahoraga state.json (produced + next_series-1)."""
    try:
        st = json.loads(MAHORAGA_STATE.read_text())
    except Exception as e:
        log(f"⚠ อ่าน state.json ไม่ได้ ({e}) — ใช้ carousel_state.last_series แทน")
        return 0
    nums = []
    for p in st.get("produced", []):
        try:
            nums.append(int(p.get("series")))
        except (TypeError, ValueError):
            pass
    nums.append(int(st.get("next_series", 1)) - 1)
    return max(nums) if nums else 0

def load_state():
    if STATE_FILE.exists():
        state = json.loads(STATE_FILE.read_text())
    else:
        # bootstrap from carousel queue
        state = {"last_series": 44, "used_themes": [], "used_sources": []}
    # reconcile: อย่าให้ last_series ต่ำกว่าเลขที่ระบบเก่าจองไปแล้ว (กันปั๊มเลขทับ)
    base = state.get("last_series", 0)
    hi = _highest_assigned_series()
    # ⚠ divergence guard: ถ้า state.json ดันเลขกระโดดผิดปกติ (เช่น phantom entries — เหตุ #52-251)
    # ให้เตือนดังๆ ก่อน (ไม่ cap เพราะ cap = เสี่ยงเลขซ้ำ) เพื่อจับ drift ตั้งแต่ต้น
    if hi - base > 50:
        msg = f"⚠️ Raphael: series counter กระโดดผิดปกติ {base}→{hi} (+{hi-base}) — ตรวจ state.json มี phantom entries?"
        log(msg)
        try:
            telegram_notify(msg)
        except Exception:
            pass
    state["last_series"] = max(base, hi)
    return state

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))

def list_backgrounds():
    return sorted([p.stem for p in BG_DIR.glob("*.png") if not p.stem.startswith("Gemini_Generated")])

def writer_soul():
    """อ่านเสียงของตัวเอง (soul/raphael.md) + บทเรียนสไตล์จากปรัชญา.
    จิตวิญญาณนักเขียนที่พัฒนาจาก data จริง."""
    parts = []
    try:
        parts.append((ROOT / "soul" / "raphael.md").read_text(encoding="utf-8")[:1500])
    except Exception:
        pass
    try:
        from prajna_reflect import recent_lessons
        L = recent_lessons(for_whom="raphael", n=4)
        if L:
            parts.append("## บทเรียนสไตล์ล่าสุด (จากปรัชญา)\n" + L)
    except Exception:
        pass
    return ("\n## ✍️ เสียงของคุณ (อ่านก่อนเขียน)\n" + "\n\n".join(parts) + "\n") if parts else ""

def call_deepseek(prompt):
    from llm import call_llm
    return call_llm(
        prompt,
        system="คุณคือ Raphael เทพเจ้าผู้เขียน TikTok carousel ภาษาไทยให้ Mahoraga ZEN (ภาพถ่ายธรรมชาติสไตล์ National Geographic + ปรัชญาตะวันออก) ตอบเป็น JSON เท่านั้น ไม่มี markdown ไม่มีข้อความอื่น",
        temperature=0.8,
        expect_json=True,
        log_fn=log,
    )

def telegram_notify(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token: return
    body = json.dumps({"chat_id": chat, "text": text}).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body, headers={"Content-Type": "application/json"},
    )
    try: urllib.request.urlopen(req, timeout=10).read()
    except: pass

def mark_parent_done(parent_file, child_id):
    text = parent_file.read_text()
    if "next_stage:" not in text:
        text = re.sub(r'(\nupdated: [^\n]+)',
                      f'\\1\nnext_stage: raphael_done\nchild_task: {child_id}', text)
    parent_file.write_text(text)

def write_child_task(parent_meta, content):
    now = datetime.now(timezone.utc)
    tid = f"task-{now.strftime('%Y%m%d')}-{uuid.uuid4().hex[:6]}"
    path = TASKS_DIR / f"{tid}.md"

    series = content["series"]
    theme = content["theme_name"]

    front = f"""---
id: {tid}
title: "Carousel #{series} — {theme}"
assignee: bezalel
creator: raphael
parent_task: {parent_meta.get('id', '')}
status: pending_qa
type: carousel_content
series: {series}
created: {now.isoformat()}
updated: {now.isoformat()}
qa_note: ""
auto_generated: true
agent: deepseek
---

## Series #{series} · {theme}

**Subtitle:** {content.get('theme_subtitle', '')}
**Source:** {content.get('source', '')}
**Highlight color:** `{content.get('highlight_color', '')}`

### Slides
"""
    for i, s in enumerate(content["slides"], 1):
        front += f"\n**Slide {i}** — bg: `{s['bg']}` · icon: {s['icon']}\n"
        front += f"> {s['quote']}\n"
        front += f"_{s['sub']}_\n"

    front += f"\n### Raw JSON (for Bezalel)\n```json\n{json.dumps(content, ensure_ascii=False, indent=2)}\n```\n"

    path.write_text(front, encoding="utf-8")
    return tid

CJK_RE = re.compile(r'[一-鿿]')

# ── harden gemma3:4b (DeepSeek 402 fallback): JSON ขาด comma + theme_name echo ──
def _loads_lenient(raw):
    """json.loads ที่ทน missing-comma ของโมเดลเล็ก (gemma3:4b)."""
    try:
        return json.loads(raw)
    except Exception:
        pass
    s = raw
    # เติม comma ที่ขาดระหว่าง value-end ("/digit/]/}) กับ key/element ถัดไปบรรทัดใหม่ ({/")
    s = re.sub(r'([}\]"]|\d)\s*\n(\s*["{])', r'\1,\n\2', s)
    s = re.sub(r',\s*,', ',', s)           # กัน comma ซ้ำ
    s = re.sub(r',(\s*[}\]])', r'\1', s)   # ตัด trailing comma ก่อน } ]
    return json.loads(s)


def _locked_theme(title):
    """ดึง theme ที่ 'ล็อกไว้' จาก title ของ task (รูปแบบคลัง: '{emoji} {topic} – 7 ข้อคิดจาก{topic}').
    คืน (theme_name, theme_subtitle) หรือ (None, None) ถ้า parse ไม่ได้ → fall back ใช้ output โมเดล."""
    m = re.search(r'(7\s*ข้อคิดจาก[^–—\[\]]+)', title or "")
    if not m:
        return None, None
    subtitle = m.group(1).strip().rstrip(" ”\"'")
    if "ธีม" in subtitle or not subtitle:
        return None, None
    em = re.findall(r'[\U0001F000-\U0001FAFF☀-➿←-⇿]', title)
    theme = subtitle + (" " + em[0] if em else "")
    return theme, subtitle


def validate_and_fix(content, bg_list, series):
    """Quality gate: sanitize fields, fix what's fixable, return (ok, reasons).
    Mutates content in place. Returns ok=False if content is unsalvageable."""
    reasons = []

    # series number must match what we assigned
    content["series"] = series

    # theme_name: fix bracket echoes from smaller models, reject template echo / empty
    theme = (content.get("theme_name") or "").strip()
    theme = re.sub(r'[\[\]]', '', theme)  # strip [] from template echo (gemma3 quirk)
    # placeholder echo: gemma3 บางครั้งใส่คำว่า "ธีม" แทน topic จริง ("7 ข้อคิดจากธีม 🌱")
    # → rebuild สะอาดจาก topic-word ใน theme_subtitle (subtitle เองอาจมีเศษ ", 🌾 ปนมา)
    if re.search(r'จาก\s*ธีม', theme):
        mt = re.search(r'จาก\s*([ก-๙]+)', content.get("theme_subtitle") or "")
        if mt and mt.group(1) != "ธีม":
            em = re.findall(r'[\U0001F000-\U0001FAFF☀-➿←-⇿]', theme + (content.get("theme_subtitle") or ""))
            theme = f"7 ข้อคิดจาก{mt.group(1)}" + (" " + em[0] if em else "")
    content["theme_name"] = theme
    if "เช่น" in theme or "ชื่อ theme" in theme or re.search(r'จาก\s*ธีม', theme) or not theme:
        return False, [f"bad theme_name '{theme[:40]}'"]

    # strip brackets from subtitle/source too (smaller models echo template)
    for field in ("theme_subtitle", "source"):
        v = (content.get(field) or "").strip()
        content[field] = re.sub(r'[\[\]]', '', v)

    # highlight_color → keep only #RRGGBB
    m = re.search(r'#([0-9a-fA-F]{6})', content.get("highlight_color", ""))
    content["highlight_color"] = f"#{m.group(1)}" if m else "#c8a96e"

    # seal fields no longer used (NatGeo style) — strip if present
    content.pop("seal_color_rgb", None)

    # slides: must end up exactly 7
    slides = content.get("slides", [])
    if len(slides) > 7:
        slides = slides[:7]
    if len(slides) != 7:
        return False, [f"slide count {len(slides)}"]
    content["slides"] = slides

    # per-slide content checks (these gate quality, not just structure)
    available = [b for b in bg_list if not b.startswith("Gemini_Generated")]
    import random as _random
    pool = _random.sample(available, len(available)) if available else bg_list
    used_bgs, pool_idx = set(), 0
    hl_count = 0
    for i, s in enumerate(slides, 1):
        quote = (s.get("quote") or "").strip()
        if len(quote) < 6:
            reasons.append(f"slide{i} quote too short")
        if "<hl>" not in quote and len(quote) >= 6:
            # auto-inject <hl> on longest Thai word cluster (2-5 words)
            words = quote.split()
            if len(words) >= 3:
                longest = max(words, key=len)
                s["quote"] = quote.replace(longest, f"<hl>{longest}</hl>", 1)
                quote = s["quote"]
        if "<hl>" in quote:
            hl_count += 1
        # seals removed (NatGeo style) — clean up if LLM still generates them
        s.pop("seal_1", None)
        s.pop("seal_2", None)
        # bg must exist + be unique
        bg = s.get("bg", "")
        # gemma3:4b บางครั้งคืน string ยักษ์/หลายบรรทัดเป็นชื่อ bg → (BG_DIR/f"{bg}.png").exists()
        # โยน OSError [Errno 63] File name too long ทำทั้ง task พัง — กันด้วย sanity check ก่อน
        bg_valid = isinstance(bg, str) and 0 < len(bg) <= 120 and "\n" not in bg
        try:
            bg_exists = bg_valid and (BG_DIR / f"{bg}.png").exists()
        except OSError:
            bg_exists = False
        if not bg_exists or bg in used_bgs:
            while pool_idx < len(pool) and pool[pool_idx] in used_bgs:
                pool_idx += 1
            s["bg"] = pool[pool_idx % len(pool)]
            pool_idx += 1
        used_bgs.add(s["bg"])

    # slide 7: รับประกัน CTA hard-gate ของเปาเจิ้ง (กันวง revise ไม่จบ — gemma3 ลืม CTA บ่อย)
    # เปาเจิ้ง revise ทันทีถ้า slide 7 ขาด: คำถามเปิด / hook แชร์ / "กดไลก์ กดแชร์ กดติดตาม" ครบ 3
    s7 = slides[6]
    sub7 = (s7.get("sub") or "").strip()
    triple = ("กดไลก์", "กดแชร์", "กดติดตาม")
    has_triple = all(w in sub7 for w in triple)
    has_question = ("?" in (s7.get("quote", "") + sub7)
                    or "ไหม" in sub7 or "ข้อไหน" in sub7)
    if not (has_triple and has_question):
        parts = [sub7] if sub7 else []
        if not has_question:
            parts.append("ข้อไหนตรงใจคุณ? บอกในคอมเมนต์")
        if not has_triple:
            # ลบเศษ CTA บางส่วนก่อนเติมวลีเต็ม (กันซ้ำ)
            if parts:
                parts[0] = re.sub(r'(กดไลก์|กดแชร์|กดติดตาม)', '', parts[0]).strip(" ·—-")
            parts.append("กดไลก์ กดแชร์ กดติดตาม — พรุ่งนี้มีชุดใหม่")
        s7["sub"] = " · ".join(p for p in parts if p).strip(" ·")

    # need at least half the slides with highlight emphasis
    if hl_count < 4:
        reasons.append(f"only {hl_count}/7 slides have <hl>")

    # hard-fail if too many quality problems, else accept with warnings
    ok = len(reasons) < 4
    return ok, reasons


def revise(content, concerns, bg_list, log_fn=None):
    """แก้ content ตาม concern ของเปาเจิ้ง — เก็บส่วนที่ดี ยกระดับส่วนที่ติง.
    คืน content ที่ปรับแล้ว (ผ่าน validate_and_fix) หรือ None ถ้าแก้ไม่ได้."""
    from llm import call_llm
    concerns_txt = "\n".join(f"- {c}" for c in concerns) if concerns else "(ยกระดับความลึกโดยรวม)"
    series = content.get("series", 0)
    voice = writer_soul()
    current = json.dumps(content, ensure_ascii=False, indent=1)
    prompt = f"""คุณคือราฟาเอล นักเขียนของ Mahoraga ZEN เปาเจิ้ง (ผู้ตรวจ) ขอให้แก้ carousel นี้
{voice}
## Content ปัจจุบัน
{current[:2500]}

## สิ่งที่เปาเจิ้งขอให้แก้
{concerns_txt}

แก้เฉพาะจุดที่ถูกติง ยกระดับให้ลึกขึ้น (โยงปรัชญาให้เป็นสัจธรรม ไม่ใช่ cliché)
ห้ามเปลี่ยนธีม/สี/รูป — แก้แค่ข้อความ (quote กับ sub) ของแต่ละ slide เท่านั้น

ตอบ JSON เล็กๆ แค่นี้ (slides 7 ข้อ เรียงลำดับเหมือนเดิม ห้ามขาดห้ามเกิน):
{{
  "theme_subtitle": "(แก้ถ้าจำเป็น ไม่งั้นคงเดิม)",
  "slides": [
    {{"quote": "ข้อความใหม่ slide 1", "sub": "คำขยาย slide 1"}},
    ... (ครบ 7 ข้อ)
  ]
}}

สำคัญ: slide 7 ต้องมี CTA กระตุ้นคอมเมนต์ (คำถามเปิด) + sub ต้องมี "กดไลก์ กดแชร์ กดติดตาม" + follow hook เสมอ"""
    try:
        raw = call_llm(prompt,
                       system="คุณคือราฟาเอล แก้งานตาม feedback ตอบ JSON เท่านั้น ไม่มี markdown",
                       temperature=0.7, expect_json=True, log_fn=log_fn)
        cand = _loads_lenient(raw)
    except Exception as e:
        if log_fn:
            log_fn(f"revise parse fail: {e}")
        return None

    # Merge: แก้แค่ quote+sub (สิ่งที่เปาเจิ้งติด) คง bg/icon/สี เดิมไว้
    merged = dict(content)
    cand_slides = cand.get("slides", [])
    for i, orig in enumerate(merged.get("slides", [])):
        if i < len(cand_slides):
            c = cand_slides[i]
            if c.get("quote", "").strip():
                orig["quote"] = c["quote"]
            if c.get("sub", "").strip():
                orig["sub"] = c["sub"]
    if cand.get("theme_subtitle", "").strip():
        merged["theme_subtitle"] = cand["theme_subtitle"]

    ok, reasons = validate_and_fix(merged, bg_list, series)
    if not ok:
        if log_fn:
            log_fn(f"revised content failed validation: {reasons}")
        return None
    return merged


def process(parent_file, meta, body, state, bg_list):
    title = meta.get("title", "").replace("Series — ", "").strip()
    log(f"processing {parent_file.name}: {title}")
    locked_theme, locked_sub = _locked_theme(title)   # ฉีดจาก title (กัน gemma echo 'จากธีม')

    next_series = state["last_series"] + 1
    used_themes = ", ".join(state["used_themes"][-15:]) if state["used_themes"] else "ยังไม่มี"
    used_sources = ", ".join(state["used_sources"][-10:]) if state["used_sources"] else "ยังไม่มี"
    bg_json = json.dumps(bg_list, ensure_ascii=False)

    # Extract Cangjie's intent from body (the topic + 7-slide outline)
    cangjie_input = body[:2500]
    voice = writer_soul()

    prompt = f"""สร้าง content สำหรับ TikTok Carousel Series #{next_series} ของ Mahoraga ZEN (ภาพถ่ายธรรมชาติ National Geographic + ปรัชญาจีน/ตะวันออก)
{voice}
## Theme ที่ Cangjie เสนอ (ใช้เป็นแกน)
{cangjie_input}

## ธีมที่ใช้ไปแล้ว (ห้ามซ้ำ): {used_themes}
## แหล่งปรัชญาที่ใช้ล่าสุด: {used_sources}

## รูปพื้นหลังที่มี: {bg_json}

ตอบเป็น JSON object นี้ (7 slides พอดี ไม่มากไม่น้อย):
{{
  "series": {next_series},
  "theme_name": "7 ข้อคิดจาก[ธีม] [emoji]",
  "theme_subtitle": "7 ข้อคิดจาก[ธีม]",
  "source": "[ชื่อคัมภีร์/นักปราชญ์]",
  "highlight_color": "#[6หลัก hex — สีที่เข้ากับธีม เช่น ฟ้า/เขียว/ทอง]",
  "slides": [
    {{"bg": "[ชื่อไฟล์ไม่ใส่.png]", "icon": "[emoji]", "quote": "[คำคม <hl>คำสำคัญ</hl>]", "sub": "[ประโยคสั้น]"}},
    {{"bg": "...", "icon": "...", "quote": "...", "sub": "..."}},
    {{"bg": "...", "icon": "...", "quote": "...", "sub": "..."}},
    {{"bg": "...", "icon": "...", "quote": "...", "sub": "..."}},
    {{"bg": "...", "icon": "...", "quote": "...", "sub": "..."}},
    {{"bg": "...", "icon": "...", "quote": "...", "sub": "..."}},
    {{"bg": "...", "icon": "...", "quote": "...", "sub": "..."}}
  ]
}}

กฎ:
- theme_name ขึ้นต้นด้วย "7 ข้อคิดจาก" เสมอ ตามด้วยธีม + emoji 1 ตัว
- highlight_color = hex 6 หลักอย่างเดียว เช่น #87CEEB — เลือกสีที่เข้ากับธีม (ธรรมชาติ=เขียว ทะเล=ฟ้า พระอาทิตย์=ส้ม)
- bg แต่ละ slide ต้องต่างกัน เลือกจากลิสต์ข้างบน
- quote มี <hl>...</hl> รอบคำสำคัญ 1-3 คำ
- slide 1 = hook ทรงพลัง ทำให้คน "หยุดเลื่อน" (stop scroll) → ใช้ paradox หรือ bold statement
- slide 7 = ปิดด้วย CTA กระตุ้นคอมเมนต์ เช่น "คุณเห็นด้วยกับข้อไหนมากที่สุด?", "ข้อไหนตรงใจคุณ? บอกในคอมเมนต์", "เซฟไว้อ่านวันที่ท้อ" — ต้องเป็นคำถามเปิดที่ง่ายต่อการตอบ
- sub ของ slide 7 = วลีกระตุ้น engagement + **follow hook** เช่น "แชร์ให้คนที่ต้องอ่าน 🙏 ตามไว้ พรุ่งนี้มีชุดใหม่" หรือ "กดเซฟ ♡ แล้วกด follow — ทุกวันมีข้อคิดใหม่รอคุณ"
- **สำคัญ: sub slide 7 ต้องมี CTA สามตัว: กดไลก์ กดแชร์ กดติดตาม** + เหตุผลให้กดติดตาม เช่น "กดไลก์ กดแชร์ กดติดตาม — พรุ่งนี้มีชุดใหม่" → แก้ปัญหา follow-rate ต่ำ

## TikTok Algorithm Optimization
- ทุก slide ต้องมี "ความอยากรู้" ที่ดึงให้ swipe ต่อ (เพิ่ม watch time / completion rate)
- slide 3-4 = จุดพีค ใส่ insight ที่แรงที่สุด / ขัดกับสามัญสำนึก (paradox) → ลดการ drop-off กลาง carousel
- เนื้อหาต้อง niche-specific: ใช้คำที่กลุ่มเป้าหมาย "คนไทยสนใจปรัชญา/พัฒนาตัวเอง" ใช้ค้นหา → ช่วย algo จับ topic cluster ถูก
- หลีกเลี่ยงคำ generic เช่น "ความสำเร็จ", "ชีวิตดี" → ใช้คำเฉพาะทาง เช่น "สัจธรรม", "อนิจจัง", "เต๋า", "ปล่อยวาง" ที่เป็น signal บอก algo ว่าเนื้อหาอยู่ใน niche ไหน"""

    # Generate with up to 2 attempts; quality gate decides accept/retry
    content = None
    for attempt in range(1, 3):
        try:
            raw = call_deepseek(prompt)
            cand = _loads_lenient(raw)
        except Exception as e:
            log(f"  attempt {attempt} parse fail: {e}")
            continue
        if locked_theme:                              # ล็อกหัวข้อจากคลัง ไม่เชื่อ theme_name ของโมเดล
            cand["theme_name"] = locked_theme
            if not (cand.get("theme_subtitle") or "").strip():
                cand["theme_subtitle"] = locked_sub
        ok, reasons = validate_and_fix(cand, bg_list, next_series)
        if ok:
            if reasons:
                log(f"  attempt {attempt} accepted with warnings: {reasons}")
            content = cand
            break
        log(f"  attempt {attempt} rejected: {reasons}")

    if content is None:
        count, quarantined = bump_fail(parent_file)
        log(f"FAIL {parent_file.name}: quality gate failed (fail #{count}/{MAX_RAPHAEL_FAILS})")
        # แจ้ง Telegram แค่ตอน quarantine (ครั้งเดียว) — เลิก spam ทุกรอบที่หยิบ task เดิม
        if quarantined:
            telegram_notify(f"⛔️ Raphael: {title} ล้ม quality gate {count} ครั้ง — ตัดออกจากคิว "
                            f"(น่าจะเพราะ DeepSeek 402 + gemma3:4b ปั่น JSON พัง). re-trigger เมื่อโมเดลกลับมา")
        return None

    child_id = write_child_task(meta, content)
    mark_parent_done(parent_file, child_id)

    # update state
    state["last_series"] = content["series"]
    state["used_themes"].append(content["theme_name"])
    state["used_sources"].append(content["source"])
    save_state(state)

    feed("raphael", f"📝 เขียน Series #{content['series']} {content['theme_name']} เสร็จ → ส่งต่อ Bezalel")
    telegram_notify(f"""📝 Raphael เขียน Series #{content['series']} เสร็จ

{content['theme_name']}
{content['theme_subtitle']}
— {content['source']}

7 slides + NatGeo photo style + matched color scheme
ส่งต่อให้ Bezalel render

📁 {child_id}.md""")
    return child_id

def main():
    from _lock import single_instance
    if not single_instance("raphael"):
        log("another Raphael is running — skipping")
        return
    load_env()
    log("Raphael wakes")
    pending = find_approved_topics()
    if not pending:
        log("nothing to do")
        return
    state = load_state()
    bg_list = list_backgrounds()
    log(f"found {len(pending)} approved Cangjie task(s), BG pool={len(bg_list)}")
    for f, meta, body in pending:
        try:
            process(f, meta, body, state, bg_list)
        except Exception as e:
            # 1 task พังไม่ควรล้มทั้ง run — log + ไปต่อ (กัน fail เงียบ)
            log(f"FAIL {f.name}: {type(e).__name__}: {e}")
    log("done")

if __name__ == "__main__":
    main()
