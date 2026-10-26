import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

p = "C:/Users/janar/.gemini/antigravity/scratch/geeta_automation_engine/counter_masterpiece_100x_script.json"
with open(p, "r", encoding="utf-8") as f:
    chapters = json.load(f)

print(f"Total Chapters: {len(chapters)}")
for c in chapters:
    w_count = len(c.get("exposition", "").split())
    print("=" * 60)
    print(f"अध्याय {c.get('chapter_num')}: {c.get('title')} ({w_count} शब्द)")
    print(f"विजुअल क्वेरीज़: {', '.join(c.get('visual_queries', [])[:4])}")
    print(f"शुरुआती पंक्तियाँ: {c.get('exposition', '')[:180]}...")
