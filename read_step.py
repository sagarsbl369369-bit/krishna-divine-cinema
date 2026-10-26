import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')
with open(r"C:\Users\janar\.gemini\antigravity\brain\8322042b-45e0-4c5e-acf2-d53f97ebf56e\.system_generated\logs\transcript.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("step_index") in [1342, 1343, 1344, 1345, 1346, 1347]:
            print(f"--- STEP {data.get('step_index')} [{data.get('type')}] ---")
            print(str(data.get("content") or data.get("tool_calls"))[:500])
