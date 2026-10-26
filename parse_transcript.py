import youtube_transcript_api
import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

video_id = "4aCwWUoh_i0"
y = youtube_transcript_api.YouTubeTranscriptApi()
data = y.fetch(video_id)

print(f"Total Transcript Segments: {len(data)}")
all_text = " ".join(item.text for item in data)
print(f"Total Spoken Words: {len(all_text.split())}")

print("\n--- FIRST 20 SEGMENTS (0 to 60s HOOK) ---")
for s in data[:20]:
    print(f"[{s.start:.1f}s]: {s.text}")

print("\n--- SAMPLE SEGMENTS AT 10 MINS (600s) ---")
mid_10 = [s for s in data if 600 <= s.start <= 660]
for s in mid_10[:10]:
    print(f"[{s.start:.1f}s]: {s.text}")

print("\n--- SAMPLE SEGMENTS AT 25 MINS (1500s) ---")
mid_25 = [s for s in data if 1500 <= s.start <= 1560]
for s in mid_25[:10]:
    print(f"[{s.start:.1f}s]: {s.text}")

# Save full transcript
with open("scanned_original_transcript.json", "w", encoding="utf-8") as f:
    json.dump([{"start": s.start, "duration": s.duration, "text": s.text} for s in data], f, indent=2, ensure_ascii=False)

print("\nFull transcript saved to scanned_original_transcript.json")
