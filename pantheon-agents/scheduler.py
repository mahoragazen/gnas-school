#!/usr/bin/env python3
"""
Scheduler · ผู้จัดคิว — Bridge Pantheon → state.json
สแกน task ที่ bezalel_done แต่ยังไม่อยู่ใน state.json
→ เพิ่ม entry + กำหนดวันถัดจากวันสุดท้ายในคิว
→ Reminder จะเห็นและส่ง Telegram อัตโนมัติ

Cron: ทุก 6 ชม. (เดียวกับ sync_queue)
"""
import json, re
from datetime import datetime, timezone, timedelta, date
from pathlib import Path

HOME = Path.home()
ROOT = Path(__file__).parent
TASKS_DIR = HOME / "internalMac/Obsidian/Obsidian Vault/wiki/tasks"
STATE_FILE = HOME / "internalMac/bots/mahoraga-content/automation/state.json"
PANTHEON_OUT = HOME / "internalMac/assets/pantheon-carousels"
FEED_FILE = ROOT / "feed.ndjson"
LOG = Path("/tmp/scheduler.log")
ICT = timezone(timedelta(hours=7))


def log(msg):
    line = f"[{datetime.now(timezone.utc).isoformat()}] {msg}"
    print(line)
    with LOG.open("a") as f:
        f.write(line + "\n")


def feed(msg):
    try:
        with FEED_FILE.open("a") as f:
            f.write(json.dumps({"t": datetime.now(timezone.utc).isoformat(),
                                "d": "scheduler", "m": msg}, ensure_ascii=False) + "\n")
    except Exception:
        pass


def extract_task_content(task_text):
    """Extract series number, theme, hook, emoji from a bezalel_done task."""
    json_match = re.search(r'```json\n(.*?)\n```', task_text, re.DOTALL)
    if not json_match:
        return None
    try:
        content = json.loads(json_match.group(1))
    except (json.JSONDecodeError, ValueError):
        return None

    series = content.get("series")
    if not series or not isinstance(series, int):
        return None

    theme = content.get("theme_name", "")
    hook_text = ""
    slides = content.get("slides", [])
    if slides and isinstance(slides[0], dict):
        raw = slides[0].get("quote", "")
        hook_text = re.sub(r'<[^>]+>', '', raw).strip()[:60]
    elif slides and isinstance(slides[0], str):
        hook_text = slides[0][:60]

    icon = content.get("slides", [{}])
    emoji_map = {
        "แมงมุม": "🕷️", "ใยแมงมุม": "🕸️", "ค้างคาว": "🦇",
        "ลำธาร": "💧", "เกลือ": "🧂", "หอยทาก": "🐚",
    }
    topic = re.sub(r'^7 ข้อคิดจาก', '', theme).strip()
    topic = re.sub(r'\s*[✨🌊💧🦉🕸️]+$', '', topic).strip()
    emoji = "🌿"
    for k, v in emoji_map.items():
        if k in theme:
            emoji = v
            break

    seal = content.get("seal", "")
    if isinstance(seal, str) and len(seal) == 1:
        pass

    return {
        "series": series,
        "topic": topic or theme,
        "emoji": emoji,
        "hook": hook_text + "..." if hook_text else "",
        "theme_name": theme,
        "extra_tag": f"#{topic}" if topic else "",
        "sound_note": "🎵 archangel - Slowed",
    }


def find_slides_dir(series_num):
    """Find the best slides directory for a series."""
    pantheon = PANTHEON_OUT / f"series-{series_num}"
    if pantheon.exists():
        slides = list(pantheon.glob("slide-*.png"))
        if len(slides) >= 7:
            return str(pantheon)

    legacy = HOME / f"internalMac/assets/carousel-{series_num}-slides"
    if legacy.exists():
        slides = list(legacy.glob("slide-*.jpg")) + list(legacy.glob("slide-*.png"))
        if slides:
            return str(legacy)

    return None


def main():
    from _lock import single_instance
    if not single_instance("scheduler"):
        log("another Scheduler is running — skipping")
        return

    log("Scheduler wakes")

    state = json.loads(STATE_FILE.read_text())
    state_series = {p["series"] for p in state["produced"]}

    scheduled_dates = []
    for p in state["produced"]:
        if p.get("scheduled_post_date"):
            try:
                scheduled_dates.append(
                    datetime.strptime(p["scheduled_post_date"], "%Y-%m-%d").date()
                )
            except ValueError:
                pass

    last_date = max(scheduled_dates) if scheduled_dates else date.today()

    # 🩹 backfill: entry ที่ bezalel.sync_state_json() เติมเข้า state โดยไม่ลงวัน (scheduled_post_date=None)
    # จะถูก scheduler ข้ามตลอด (อยู่ใน state_series แล้ว) → reminder เลือกไม่ได้ = ไม่มีโพสต์รายวัน.
    # ลงวันต่อท้ายคิวให้ entry พวกนี้ (ที่ slides พร้อมจริง) เพื่อให้ reminder ส่งได้
    backfilled = []
    for p in state["produced"]:
        if p.get("scheduled_post_date") or p.get("tg_sent") or p.get("posted"):
            continue
        sd = p.get("slides_dir")
        if not sd or not list(Path(sd).glob("slide-*.png")) + list(Path(sd).glob("slide-*.jpg")):
            continue
        last_date += timedelta(days=1)
        p["scheduled_post_date"] = last_date.isoformat()
        backfilled.append(f"#{p.get('series')} {p.get('topic')} ({p['scheduled_post_date']})")
    if backfilled:
        log(f"backfilled dates for {len(backfilled)}: {', '.join(backfilled)}")

    new_entries = []
    for task_file in sorted(TASKS_DIR.glob("task-*.md")):
        text = task_file.read_text()
        if "bezalel_done" not in text:
            continue
        if "carousel_content" not in text and "carousel" not in text.lower():
            continue

        info = extract_task_content(text)
        if not info:
            continue
        if info["series"] in state_series:
            continue
        # QA gate: ลงคิวเฉพาะที่ Baozheng "ผ่าน" — กัน content ที่ถูกตีกลับหลุดเข้าคิวโพสต์/reminder
        if "qa_verdict: pass" not in text:
            log(f"  skip #{info['series']} — รอ Baozheng ผ่านก่อน (qa_verdict != pass)")
            continue

        slides_dir = find_slides_dir(info["series"])
        if not slides_dir:
            log(f"  skip #{info['series']} — no slides found")
            continue

        last_date += timedelta(days=1)

        entry = {
            "series": info["series"],
            "topic": info["topic"],
            "emoji": info["emoji"],
            "scheduled_post_date": last_date.isoformat(),
            "posted": False,
            "slides_dir": slides_dir,
            "hook": info["hook"],
            "extra_tag": info["extra_tag"],
            "sound_note": info["sound_note"],
            "views": None,
            "likes": None,
            "saves": None,
            "shares": None,
        }
        new_entries.append(entry)
        state_series.add(info["series"])

    if not new_entries and not backfilled:
        log("nothing new to schedule")
        return

    if new_entries:
        state["produced"].extend(new_entries)
        next_s = max(e["series"] for e in new_entries) + 1
        if next_s > state.get("next_series", 0):
            state["next_series"] = next_s

    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))

    if new_entries:
        summary = ", ".join(f"#{e['series']} {e['topic']} ({e['scheduled_post_date']})"
                            for e in new_entries)
        log(f"added {len(new_entries)}: {summary}")
        feed(f"📅 เพิ่ม {len(new_entries)} series เข้าคิว: {summary}")


if __name__ == "__main__":
    main()
