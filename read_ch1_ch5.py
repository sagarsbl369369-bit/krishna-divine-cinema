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

print("--- CHAPTER 1 FULL EXPOSITION ---")
print(chapters[0]['exposition'])

print("\n--- CHAPTER 5 FULL EXPOSITION ---")
print(chapters[4]['exposition'])
