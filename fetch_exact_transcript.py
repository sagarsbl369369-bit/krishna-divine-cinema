from youtube_transcript_api import YouTubeTranscriptApi
import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

video_id = "4aCwWUoh_i0"

try:
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    t = transcript_list.find_transcript(['hi', 'hi-IN', 'en', 'en-IN'])
    data = t.fetch()
    
    print(f"Total Transcript Segments: {len(data)}")
    total_words = sum(len(x['text'].split()) for x in data)
    print(f"Total Words in Original Video: {total_words}")

    # Print first 20 segments
    print("\n--- FIRST 20 SEGMENTS OF ORIGINAL VIDEO ---")
    for s in data[:20]:
        print(f"[{s['start']:.1f}s]: {s['text']}")

    # Print middle segments (around 10 mins and 20 mins)
    print("\n--- SAMPLE SEGMENTS AT 10 MINS ---")
    mid_10 = [s for s in data if 580 <= s['start'] <= 650]
    for s in mid_10[:10]:
        print(f"[{s['start']:.1f}s]: {s['text']}")

    # Save full transcript for analysis
    with open("scanned_original_transcript.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

except Exception as e:
    print(f"Error fetching transcript: {e}")
