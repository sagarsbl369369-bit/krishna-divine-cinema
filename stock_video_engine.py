"""
Stock Video Engine (Pexels, Pixabay & Open HD B-Roll)
Fetches real cinematic 16:9 MP4 video clips matching spiritual & philosophical themes.
Normalizes all clips to 1280x720 16:9 @ 30fps.
"""

import os
import sys
import json
import urllib.parse
import subprocess
import requests

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

# Curated direct public domain high-definition stock video sources (fallback if no API key set)
FALLBACK_CLIPS = [
    # 1. Sunset over sacred horizon
    "https://upload.wikimedia.org/wikipedia/commons/2/2e/Grand_Canyon_National_Park_B-roll_Video-_Cape_Royal_Sunset_-_Time-lapse_%288661965788%29.webm",
    # 2. Relaxing nature sunrise and mist
    "https://upload.wikimedia.org/wikipedia/commons/5/57/%E2%99%A5%E2%99%A5_Relaxing_Sunrise%2C_Waterfall%2C_and_Birds_at_Grand_Canyon_of_the_Yellowstone_%282_hours%29.webm",
    # 3. Meditation and inner contemplation
    "https://upload.wikimedia.org/wikipedia/commons/2/20/Meditation_New_AGE_Movement.webm",
    # 4. Sacred ritual ambience
    "https://upload.wikimedia.org/wikipedia/commons/d/d4/Meditation_Ritual_AGE.webm"
]

def search_pexels_video(query: str, target_file: str) -> bool:
    """Queries Pexels Video API for 16:9 landscape video."""
    if not PEXELS_API_KEY:
        return False
    try:
        url = f"https://api.pexels.com/v1/videos/search?query={urllib.parse.quote(query)}&per_page=3&orientation=landscape"
        headers = {"Authorization": PEXELS_API_KEY}
        r = requests.get(url, headers=headers, timeout=15)
        if r.status_code == 200:
            data = r.json()
            videos = data.get("videos", [])
            for vid in videos:
                for file_info in vid.get("video_files", []):
                    if file_info.get("width", 0) >= 1280 and file_info.get("file_type") == "video/mp4":
                        download_url = file_info["link"]
                        res = requests.get(download_url, stream=True, timeout=30)
                        if res.status_code == 200:
                            with open(target_file, "wb") as f:
                                for chunk in res.iter_content(chunk_size=1024*1024):
                                    if chunk:
                                        f.write(chunk)
                            print(f"[✓] Downloaded Pexels Clip: {target_file}")
                            return True
    except Exception as e:
        print(f"[!] Pexels search error: {e}")
    return False

def search_pixabay_video(query: str, target_file: str) -> bool:
    """Queries Pixabay Video API for 16:9 video."""
    if not PIXABAY_API_KEY:
        return False
    try:
        url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={urllib.parse.quote(query)}&video_type=film&per_page=3"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            hits = data.get("hits", [])
            for hit in hits:
                v_url = hit.get("videos", {}).get("medium", {}).get("url") or hit.get("videos", {}).get("large", {}).get("url")
                if v_url:
                    res = requests.get(v_url, stream=True, timeout=30)
                    if res.status_code == 200:
                        with open(target_file, "wb") as f:
                            for chunk in res.iter_content(chunk_size=1024*1024):
                                if chunk:
                                    f.write(chunk)
                        print(f"[✓] Downloaded Pixabay Clip: {target_file}")
                        return True
    except Exception as e:
        print(f"[!] Pixabay search error: {e}")
    return False

def fetch_cinematic_clip(query: str, target_file: str, fallback_idx: int = 0) -> str:
    """
    Tries Pexels -> Pixabay -> Direct High-Res Stock Video Fallback.
    Returns normalized 1280x720 16:9 MP4 path.
    """
    raw_file = target_file.replace(".mp4", "_raw.mp4")
    success = False

    # 1. Try Pexels
    if PEXELS_API_KEY:
        success = search_pexels_video(query, raw_file)

    # 2. Try Pixabay
    if not success and PIXABAY_API_KEY:
        success = search_pixabay_video(query, raw_file)

    # 3. Fallback to Direct High-Res Open Video
    if not success:
        fb_url = FALLBACK_CLIPS[fallback_idx % len(FALLBACK_CLIPS)]
        print(f"[*] Downloading Open Stock B-Roll Video for '{query}'...")
        headers = {'User-Agent': 'GeetaVideoBot/1.0 (info@antigravity.dev)'}
        res = requests.get(fb_url, headers=headers, stream=True, timeout=30)
        with open(raw_file, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                if f.tell() > 8 * 1024 * 1024:  # 8MB max per clip
                    break
        print(f"[✓] Downloaded Open B-Roll Clip: {target_file}")

    # 4. Normalize to 1280x720 16:9 @ 30fps with setsar=1
    cmd = [
        "ffmpeg", "-y", "-i", raw_file,
        "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=30",
        "-c:v", "libx264", "-preset", "faster", "-crf", "22", "-pix_fmt", "yuv420p",
        "-an",
        target_file
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(raw_file):
        os.remove(raw_file)

    return target_file
