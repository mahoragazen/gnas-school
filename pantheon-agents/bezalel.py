#!/usr/bin/env python3
"""
Bezalel · เบซาเลล — Visual Designer agent
Picks up Raphael's carousel content tasks, renders 7 slides via the
auto_carousel.py template (per-slide bg + NatGeo photo style + matched colors),
sends Telegram preview, marks task done.
"""
import os, sys, re, json, uuid, urllib.request, subprocess, shutil
from datetime import datetime, timezone
from pathlib import Path

HOME = Path.home()
ROOT = Path(__file__).parent

# resolve node แบบ absolute — กัน "[Errno 2] No such file: 'node'" เวลาถูก trigger
# จาก cron/Hermes ที่ PATH ไม่มี node (launchd มี PATH ใน plist แต่ trigger อื่นไม่มี)
def _resolve_node():
    n = shutil.which("node")
    if n:
        return n
    for c in (HOME / ".local/bin/node", Path("/opt/homebrew/bin/node"),
              Path("/usr/local/bin/node")):
        if c.exists():
            return str(c)
    return "node"  # fallback (จะ error ชัดเจนถ้าไม่เจอจริง)
NODE_BIN = _resolve_node()
VAULT = HOME / "internalMac/Obsidian/Obsidian Vault/wiki"
TASKS_DIR = VAULT / "tasks"
BG_DIR = HOME / "internalMac/NatGeo Backgrounds"
OUT_BASE = HOME / "internalMac/assets/pantheon-carousels"
MLX_GEN = HOME / "internalMac/bots/mahoraga-content/mlx_gen.py"
# NatGeo bg ต่อหัวข้อ: 7 อารมณ์แสง (ให้ภาพ 7 ใบไม่ซ้ำกัน)
BG_LIGHT = ["soft dawn light", "golden hour glow", "misty morning haze",
            "dramatic sunset", "bright clear daylight", "blue hour twilight",
            "warm backlight"]
# 7 มุม/ระยะ ตายตัว — ความหลากหลายมาจาก framing ไม่ใช่จากการให้ gemma คิด subject ใหม่
# (กัน gemma "ไหล" จากหัวข้อเดียวไปเป็นพืชคนละชนิด เช่น ผักบุ้ง→watercress/spinach/bok choy)
BG_ANGLE = ["extreme close-up macro shot", "wide sweeping landscape",
            "aerial drone view from above", "intricate texture detail",
            "dramatic silhouette against the sky", "soft-focus portrait at dawn",
            "backlit shot"]

LOG = Path("/tmp/bezalel.log")
AUTOMATION_STATE = HOME / "internalMac/bots/mahoraga-content/automation/state.json"

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
    if not m: return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta, m.group(2)

def find_pending():
    out = []
    for f in sorted(TASKS_DIR.glob("task-*.md")):
        text = f.read_text()
        meta, body = parse_frontmatter(text)
        if (meta.get("assignee") == "bezalel"
            and meta.get("status") == "pending_qa"
            and meta.get("type") == "carousel_content"
            and meta.get("next_stage") != "bezalel_done"):
            out.append((f, meta, body))
    return out

def extract_json(body):
    m = re.search(r'```json\n(.*?)\n```', body, re.DOTALL)
    if not m: return None
    try:
        # loads_json ซ่อม missing-comma ของ gemma3:4b — ไม่งั้น task ที่ JSON เพี้ยน
        # เด้ง "no JSON" ค้างคิวถาวร (เคสกาฝาก #92 c1e320, 25 มิ.ย.)
        from llm import loads_json
        return loads_json(m.group(1))
    except Exception:
        try: return json.loads(m.group(1))
        except: return None

def bg_uri(name):
    p = BG_DIR / f"{name}.png"
    if not p.exists():
        # fallback
        for f in BG_DIR.glob("*.png"):
            if f.stem.strip() == name.strip():
                return f.as_uri()
        return (BG_DIR / "หุบเขา.png").as_uri()
    return p.as_uri()

# override ชื่อไทย→อังกฤษ สำหรับพืชที่ gemma3:4b แปลผิดซ้ำ (เช็คกับ bg จริงแล้ว) — กัน mistranslate
# (gemma เคยให้ กระดังงา→orchid/frangipani ทั้งที่จริงคือ ylang-ylang) เติมเคสใหม่ได้เรื่อยๆ
ANCHOR_OVERRIDE = {
    "ดอกกระดังงา": "ylang-ylang flower",
    "กระดังงา": "ylang-ylang flower",
    "เกสรดอกไม้": "flower stamen with pollen grains",   # gemma แปลเป็น frangipani (มั่ว)
    "เกสร": "flower stamen with pollen grains",
}

def topic_anchor(topic_th):
    """ขอ 'ชื่ออังกฤษเดียว' ของหัวข้อไทย (กัน drift) — คืน noun phrase สั้น หรือ None → fall back pool.

    เดิมขอ gemma เขียน subject อิสระ 7 บรรทัด → มันแปลพืชหายากผิด (กระดังงา→orchid) และ
    ไหลข้ามซับเจกต์ (ผักบุ้ง→watercress/spinach...). ขอชื่อเดียวแล้วประกอบมุมเองตายตัว ตรงหัวข้อแน่กว่า."""
    key = (topic_th or "").strip()
    if key in ANCHOR_OVERRIDE:
        log(f"  ⚓ anchor override: '{key}' → '{ANCHOR_OVERRIDE[key]}'")
        return ANCHOR_OVERRIDE[key]
    from llm import call_llm
    prompt = (f'หัวข้อภาษาไทย: "{topic_th}"\n'
              f'ตอบ "ชื่อภาษาอังกฤษ/พฤกษศาสตร์" ของสิ่งนี้ บรรทัดเดียว เป็น noun phrase สั้นๆ '
              f'(เช่น "frangipani flower", "water spinach plant", "ylang-ylang flower"). '
              f'ถ้าไม่แน่ใจชื่อสากล ให้ทับศัพท์ตามด้วยประเภท (เช่น "krachiao flower"). '
              f'ห้ามมีคำอธิบาย ห้ามมีเลข ตอบอังกฤษล้วนบรรทัดเดียว.')
    for attempt in range(2):
        try:
            raw = call_llm(prompt,
                           system="You translate a Thai nature subject into ONE concise English "
                                  "botanical/common noun phrase. Output one line, English only, no extra text.",
                           temperature=0.3, expect_json=False, log_fn=log)
            for ln in (raw or "").splitlines():
                ln = re.sub(r'^\s*(?:[-*•]|\d+[\.\)])\s*', '', ln.strip())
                ln = ln.strip(' "\'`.-:')
                # อังกฤษล้วน ความยาวเหมาะ ไม่มีอักษรไทย
                if (3 <= len(ln) <= 60 and not re.search(r'[ก-๙]', ln)
                        and sum(c.isascii() and c.isalpha() for c in ln) >= len(ln) * 0.7):
                    return ln
            log(f"  anchor attempt {attempt+1}: parse ไม่ได้ → retry")
        except Exception as e:
            log(f"  anchor attempt {attempt+1} fail: {e}")
    return None

def gen_topic_bgs(topic_th, series, out_dir, n=7):
    """gen พื้นหลัง NatGeo ตรงหัวข้อ n ภาพ (idempotent). คืน list[Path] หรือ None → fall back pool."""
    bgdir = out_dir / "bg"
    cached = sorted(bgdir.glob("bg_*.png"))
    if len(cached) >= n:
        log(f"  bg cache hit: {len(cached)} ภาพ")
        return cached[:n]
    anchor = topic_anchor(topic_th)
    if not anchor:
        log("  ⚠ ขอ anchor ไม่ได้ → fall back BG pool")
        return None
    log(f"  ⚓ anchor='{anchor}' (หัวข้อ '{topic_th}') — ทั้ง {n} ใบใช้ subject เดียวกัน")
    bgdir.mkdir(parents=True, exist_ok=True)
    batch = []
    for i in range(n):
        # subject เดียว (anchor) + มุม/แสงต่างกัน → 7 ใบไม่ซ้ำแต่ตรงหัวข้อ 100%
        prompt = (f"{BG_ANGLE[i % len(BG_ANGLE)]} of {anchor}, {BG_LIGHT[i % len(BG_LIGHT)]}, "
                  f"National Geographic nature photography, photorealistic, ultra detailed, "
                  f"cinematic depth, vertical 9:16")
        batch.append({"prompt": prompt, "output": str(bgdir / f"bg_{i+1}.png"),
                      "seed": series * 100 + i})
    bf = bgdir / "batch.json"
    bf.write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
    log(f"  🎨 gen NatGeo bg {n} ภาพ ธีม '{topic_th}' (mlx ~8-10 นาที)...")
    try:
        r = subprocess.run([sys.executable, str(MLX_GEN), "--batch", str(bf),
                            "--size", "576", "1024", "--steps", "18"],
                           capture_output=True, text=True, timeout=1500)
        if r.returncode != 0:
            log(f"  mlx_gen exit {r.returncode}: {(r.stderr or r.stdout)[-400:]}")
    except Exception as e:
        log(f"  mlx_gen error: {e}")
    pngs = sorted(bgdir.glob("bg_*.png"))
    if len(pngs) < n:
        log(f"  ⚠ bg gen ไม่ครบ {len(pngs)}/{n} → fall back pool")
        return None
    log(f"  ✅ bg gen ครบ {len(pngs)} ภาพ")
    return pngs[:n]

def build_html(content, bg_paths=None):
    highlight = content.get("highlight_color", "#f0d878")
    series = content["series"]
    subtitle = content.get("theme_subtitle", "")

    slides_html = []
    for i, s in enumerate(content["slides"]):
        if bg_paths and i < len(bg_paths):
            bg_url = Path(bg_paths[i]).as_uri()      # NatGeo bg ตรงหัวข้อ (gen)
        else:
            bg_url = bg_uri(s["bg"])                 # fallback: BG pool
        quote = s["quote"].replace("<hl>", '<span class="hl">').replace("</hl>", "</span>")
        active = "active" if i == 0 else ""
        slides_html.append(f"""
<div class="slide {active}" id="slide{i+1}">
  <div class="bg-image" style="background-image: url('{bg_url}');"></div>
  <div class="overlay"></div>
  <div class="accent-bar"></div>
  <div class="icon-circle">{s['icon']}</div>
  <div class="number-badge">{i+1} / 7</div>
  <div class="series-tag">SERIES #{series} · {subtitle}</div>
  <div class="main-text">
    <p>"{quote}"<span class="sub-line">{s['sub']}</span></p>
  </div>
  <div class="watermark">@mahoraga_zen</div>
</div>""")

    return f"""<!DOCTYPE html>
<html lang="th"><head><meta charset="UTF-8">
<title>Mahoraga ZEN Series #{series}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;600;700&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:720px; height:1280px; background:#0a0a0a; font-family:'Sarabun','Noto Sans Thai',sans-serif; overflow:hidden; position:relative; }}
.slide {{ position:absolute; inset:0; width:720px; height:1280px; display:none; }}
.slide.active {{ display:block; }}
.bg-image {{ position:absolute; inset:0; background-size:cover; background-position:center; z-index:1; filter:brightness(0.75) contrast(1.1) saturate(1.15); }}
.overlay {{ position:absolute; inset:0; z-index:2; background:linear-gradient(180deg,rgba(0,0,0,0.6) 0%,rgba(0,0,0,0.15) 30%,rgba(0,0,0,0.1) 50%,rgba(0,0,0,0.15) 70%,rgba(0,0,0,0.65) 100%); }}
.accent-bar {{ position:absolute; bottom:0; left:0; right:0; height:5px; z-index:5; background:{highlight}; }}
.icon-circle {{ position:absolute; top:120px; left:50%; transform:translateX(-50%); width:72px; height:72px; border-radius:50%; background:rgba(0,0,0,0.35); backdrop-filter:blur(8px); border:2px solid rgba(255,255,255,0.25); display:flex; align-items:center; justify-content:center; font-size:36px; z-index:7; }}
.number-badge {{ position:absolute; top:210px; left:50%; transform:translateX(-50%); font-size:20px; color:rgba(255,255,255,0.5); font-weight:400; z-index:7; letter-spacing:0.12em; }}
.series-tag {{ position:absolute; top:42px; left:50%; transform:translateX(-50%); font-size:15px; color:rgba(255,255,255,0.45); font-weight:600; letter-spacing:0.15em; text-transform:uppercase; z-index:8; white-space:nowrap; }}
.main-text {{ position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; z-index:8; width:86%; }}
.main-text p {{ font-size:46px; font-weight:700; color:#FFF; line-height:1.7; text-shadow:0 2px 8px rgba(0,0,0,0.9),0 0 40px rgba(0,0,0,0.5); }}
.hl {{ color:{highlight}; font-weight:700; }}
.sub-line {{ display:block; font-size:24px; font-weight:400; color:rgba(255,255,255,0.65); margin-top:20px; letter-spacing:0.02em; text-shadow:0 1px 6px rgba(0,0,0,0.8); }}
.watermark {{ position:absolute; bottom:28px; left:50%; transform:translateX(-50%); font-size:17px; color:rgba(255,255,255,0.3); z-index:9; letter-spacing:0.08em; font-weight:600; }}
</style></head><body>
{''.join(slides_html)}
</body></html>"""

def render_slides(html_path, out_dir):
    script = f"""
const {{ chromium }} = require('/Users/kaw/internalMac/node_modules/playwright');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage({{ viewport: {{ width: 720, height: 1280 }} }});
  await page.goto('file://{html_path}');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1200);
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {{
    await page.evaluate(() => {{ document.querySelectorAll('.slide').forEach(s => s.style.display='none'); }});
    await page.evaluate((i) => {{ document.querySelectorAll('.slide')[i].style.display='block'; }}, i);
    await page.waitForTimeout(350);
    await slides[i].screenshot({{ path: '{out_dir}/slide-' + String(i+1).padStart(2,'0') + '.png' }});
  }}
  await browser.close();
  console.log('rendered ' + slides.length);
}})();
"""
    r = subprocess.run([NODE_BIN, "-e", script], capture_output=True, text=True, timeout=180)
    if r.returncode != 0:
        log(f"playwright fail: {r.stderr[:500]}")
        return 0
    log(r.stdout.strip())
    return len(list(Path(out_dir).glob("slide-*.png")))

def telegram_photo(image_path, caption=""):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID")
    if not token: return
    import io
    from PIL import Image
    img = Image.open(image_path)
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=85)
    fdata = buf.getvalue()
    fname = image_path.stem + ".jpg"

    boundary = "----PantheonBoundary" + uuid.uuid4().hex
    body = b""
    for field, val in [("chat_id", chat), ("caption", caption)]:
        body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"{field}\"\r\n\r\n{val}\r\n".encode()
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"photo\"; filename=\"{fname}\"\r\nContent-Type: image/jpeg\r\n\r\n".encode()
    body += fdata + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendPhoto",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    import time
    for attempt in range(2):
        try:
            urllib.request.urlopen(req, timeout=30).read()
            return True
        except Exception as e:
            if attempt == 0:
                time.sleep(2)
            else:
                log(f"telegram photo fail: {e}")
    return False

def telegram_text(text):
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

def sync_state_json(series, topic_th, emoji, out_dir, hook=""):
    """กันไม่ให้ automation/state.json (อ่านโดย regen_nightly + Obsidian kanban sync)
    หลุด sync จาก pipeline จริง (topic_bank_v2) แบบที่เคยเกิดตั้งแต่ series #53"""
    try:
        if not AUTOMATION_STATE.exists():
            return
        state = json.loads(AUTOMATION_STATE.read_text(encoding="utf-8"))
        produced = state.setdefault("produced", [])
        if any(p.get("series") == series for p in produced):
            return
        produced.append({
            "series": series,
            "topic": topic_th,
            "emoji": emoji,
            "scheduled_post_date": None,
            "posted": False,
            "slides_dir": str(out_dir),
            "hook": hook,
            "tg_sent": True,
            "tg_sent_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "views": None, "likes": None, "saves": None, "shares": None,
        })
        if isinstance(state.get("next_series"), int) and series is not None:
            try:
                state["next_series"] = max(state["next_series"], int(series) + 1)
            except (TypeError, ValueError):
                pass
        AUTOMATION_STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        log(f"  sync_state_json fail: {e}")

def mark_done(task_file, html_path, out_dir, n):
    text = task_file.read_text()
    if "next_stage: bezalel_done" in text:
        return
    if "next_stage:" in text:
        text = re.sub(r'next_stage:.*', f'next_stage: bezalel_done', text)
    else:
        text = re.sub(r'(\nupdated: [^\n]+)',
                      f'\\1\nnext_stage: bezalel_done', text)
    for field, val in [("html", html_path), ("png_dir", out_dir), ("slide_count", n)]:
        if f"{field}:" not in text:
            text = re.sub(r'(next_stage: bezalel_done)',
                          f'\\1\n{field}: {val}', text)
    task_file.write_text(text)

def process(task_file, meta, body):
    content = extract_json(body)
    if not content:
        log(f"  no JSON in {task_file.name}")
        return

    series = content["series"]
    theme = content["theme_name"]
    log(f"processing series #{series}: {theme}")

    slug = f"series-{series:02d}"
    out_dir = OUT_BASE / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    # ดึงหัวข้อจาก theme_name (ตัวที่ถูก force-lock จากคลัง) ไม่ใช่ subtitle (อาจค้าง placeholder)
    topic_th = re.sub(r'^7\s*ข้อคิดจาก', '', theme)
    topic_th = re.sub(r'[\U0001F000-\U0001FAFF☀-➿←-⇿\s]+$', '', topic_th).strip()
    bg_paths = gen_topic_bgs(topic_th, series, out_dir) if topic_th and topic_th != "ธีม" else None
    html = build_html(content, bg_paths)
    html_path = out_dir / "carousel.html"
    html_path.write_text(html, encoding="utf-8")

    n = render_slides(html_path, out_dir)
    log(f"  rendered {n} slides")
    if n < 7:
        telegram_text(f"⚠️ Bezalel render ได้แค่ {n}/7 — {theme}")
        return

    mark_done(task_file, html_path, out_dir, n)
    feed("bezalel", f"🎨 render Series #{series} เสร็จ {n} slides")
    sync_state_json(series, topic_th, content.get("emoji", ""), out_dir, hook=content.get("hook", ""))

    telegram_text(f"""🎨 Bezalel render Series #{series} เสร็จ

{theme}
{content.get('theme_subtitle', '')}
— {content.get('source', '')}

7 slides — preview ด้านล่าง ✨""")
    first_ok = telegram_photo(out_dir / "slide-01.png", "Slide 1/7")
    if not first_ok:
        telegram_text(f"⚠️ photo upload ไม่ผ่าน — ดู preview ที่:\n📁 {out_dir}")
    else:
        for i in range(2, 8):
            png = out_dir / f"slide-{i:02d}.png"
            if png.exists():
                telegram_photo(png)
        telegram_text(f"📁 {out_dir}\nรออนุมัติโพสต์ TikTok")

def main():
    from _lock import single_instance
    if not single_instance("bezalel"):
        log("another Bezalel is running — skipping")
        return
    load_env()
    log("Bezalel wakes")
    pending = find_pending()
    if not pending:
        log("nothing to do")
        return
    log(f"found {len(pending)} task(s)")
    for f, meta, body in pending:
        try: process(f, meta, body)
        except Exception as e:
            log(f"FAIL: {e}")
            telegram_text(f"⚠️ Bezalel พลาด {f.name}: {str(e)[:200]}")
    log("done")

if __name__ == "__main__":
    main()
