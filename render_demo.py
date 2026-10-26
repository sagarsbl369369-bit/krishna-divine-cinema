import asyncio
import json
import os
import sys

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

from engine import produce_shloka_video

async def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_file = os.path.join(base_dir, "shlokas_db.json")
    output_dir = os.path.join(base_dir, "renders")

    with open(db_file, "r", encoding="utf-8") as f:
        shlokas = json.load(f)

    # Pick the first shloka (Chapter 2, Verse 47 - Karma Shloka)
    shloka = shlokas[0]
    print(f"[>] Starting Production: {shloka['title']}\n")
    
    video_path = await produce_shloka_video(shloka, output_dir)
    print(f"\n[DONE] Demo Video Completed!")
    print(f"[PATH] Output File: {video_path}")

if __name__ == "__main__":
    asyncio.run(main())
