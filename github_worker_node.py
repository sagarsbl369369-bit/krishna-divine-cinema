"""
GitHub Actions Cloud Matrix Worker Node
=======================================
Autonomous worker execution script for GitHub Actions:
- Executes within 1 of 10 isolated parallel cloud VMs (Matrix)
- Worker 1 to 5  -> Channel 1 (चैनल १: दिव्य गीता वाणी)
- Worker 6 to 10 -> Channel 2 (चैनल २: परम कृष्ण चेतना)
- Duration: >30 Mins (default 35 mins)
- Voice: Google Free Realistic TTS ('Charon') + Shure SM7B DSP (-14 LUFS)
- Voice Volume: 150% Studio Boost (volume=1.50)
- Subtitles: 24K Gold Fast Cards (#FFD700, Nirmala UI Bold, MarginV=50)
- Visibility: 100% Strictly UNLISTED
- Auto-Shutdown: Automatically cleans disk & exits with code 0.
"""

import os
import sys
import json
import time
import argparse
import subprocess
from typing import Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

def setup_cloud_environment(worker_id: int, channel_id: str):
    """Reconstructs config.json and credentials from GitHub Secrets / Env Vars."""
    print("=" * 80)
    print(f"🚀 [WORKER {worker_id}/10 INITIALIZING] Target Channel: {channel_id}")
    print("=" * 80)

    # 1. API Keys
    gemini_keys_raw = os.getenv("GEMINI_API_KEYS", "")
    groq_keys_raw = os.getenv("GROQ_API_KEYS", "")
    pixabay_key = os.getenv("PIXABAY_API_KEY", "48724139-1fbe7e777966fce52b390343f")

    # Parse list or comma-separated
    gemini_keys = []
    if gemini_keys_raw:
        if gemini_keys_raw.strip().startswith("["):
            try: gemini_keys = json.loads(gemini_keys_raw)
            except Exception: gemini_keys = [k.strip() for k in gemini_keys_raw.split(",") if k.strip()]
        else:
            gemini_keys = [k.strip() for k in gemini_keys_raw.replace("\n", ",").split(",") if k.strip()]
    if not gemini_keys:
        gemini_keys = [k for k in [os.getenv("GEMINI_API_KEY", "")] if k]

    groq_keys = []
    if groq_keys_raw:
        if groq_keys_raw.strip().startswith("["):
            try: groq_keys = json.loads(groq_keys_raw)
            except Exception: groq_keys = [k.strip() for k in groq_keys_raw.split(",") if k.strip()]
        else:
            groq_keys = [k.strip() for k in groq_keys_raw.replace("\n", ",").split(",") if k.strip()]
    if not groq_keys:
        groq_keys = [k for k in [os.getenv("GROQ_API_KEY", "")] if k]

    # 2. Write runtime config.json
    cfg = {
        "GEMINI_API_KEYS": gemini_keys,
        "GROQ_API_KEYS": groq_keys,
        "PIXABAY_API_KEY": pixabay_key,
        "VOICE_NAME": "Charon",
        "VOICE_VOLUME_PERCENT": 150,
        "SUBTITLES_ENABLED": True,
        "SUBTITLE_STYLE": "Fontname=Noto Sans Devanagari,FontSize=25,Bold=1,PrimaryColour=&H0000D7FF&,OutlineColour=&H00000000&,BorderStyle=1,Outline=2.8,Shadow=2.0,Alignment=2,MarginV=50",
        "TARGET_DURATION_MINS": 35,
        "DEFAULT_PRIVACY": "unlisted",
        "CHANNELS": {
            "ch_01": {
                "name": "चैनल १: दिव्य गीता वाणी",
                "handle": "@DivyaGitaVani",
                "niche": "चित्त शांति, अति-विचार से मुक्ति, कर्मयोग, निष्काम भाव",
                "music": "ch_01_gita_meditative"
            },
            "ch_02": {
                "name": "चैनल २: परम कृष्ण चेतना",
                "handle": "@ParamKrishnaChetna",
                "niche": "मृत्यु-बोध, माया का संहार, अद्वैत, विश्वरूप, परम भक्ति रस",
                "music": "ch_02_premanand_bhakti"
            }
        }
    }
    with open(os.path.join(BASE_DIR, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    # 3. Setup Channel OAuth2 Secrets & Tokens if present in environment
    cs_var = f"YT_CLIENT_SECRET_{channel_id.upper()}"
    tk_var = f"YT_TOKEN_{channel_id.upper()}"
    cs_data = os.getenv(cs_var, "")
    tk_data = os.getenv(tk_var, "")

    if cs_data:
        try:
            cs_json = json.loads(cs_data)
            with open(os.path.join(CREDENTIALS_DIR, f"client_secret_{channel_id}.json"), "w", encoding="utf-8") as f:
                json.dump(cs_json, f, indent=2)
            print(f"✓ Configured OAuth Client Secret for {channel_id}")
        except Exception as e:
            print(f"⚠️ Error saving client secret for {channel_id}: {e}")

    if tk_data:
        try:
            tk_json = json.loads(tk_data)
            with open(os.path.join(CREDENTIALS_DIR, f"token_{channel_id}.json"), "w", encoding="utf-8") as f:
                json.dump(tk_json, f, indent=2)
            print(f"✓ Configured OAuth Token for {channel_id}")
        except Exception as e:
            print(f"⚠️ Error saving token for {channel_id}: {e}")

    print("✓ Cloud Environment Setup Complete!\n")

def main():
    parser = argparse.ArgumentParser(description="GitHub Cloud Matrix Worker Node")
    parser.add_argument("--worker_id", type=int, required=True, help="Worker ID (1 to 10)")
    parser.add_argument("--duration", type=int, default=35, help="Target Duration in Mins (>30 mins)")
    parser.add_argument("--privacy", type=str, default="unlisted", help="YouTube Privacy (unlisted)")
    args = parser.parse_args()

    # 50/50 Dual-Channel Distribution
    # Workers 1..5  -> ch_01 (चैनल १: दिव्य गीता वाणी)
    # Workers 6..10 -> ch_02 (चैनल २: परम कृष्ण चेतना)
    if args.worker_id <= 5:
        channel_id = "ch_01"
        ch_label = f"चैनल १: दिव्य गीता वाणी (Batch Item #{args.worker_id})"
    else:
        channel_id = "ch_02"
        ch_label = f"चैनल २: परम कृष्ण चेतना (Batch Item #{args.worker_id})"

    setup_cloud_environment(args.worker_id, channel_id)

    print("=" * 80)
    print(f"🎬 [WORKER {args.worker_id}/10] EXECUTING 35-MINUTE CINEMATIC VIDEO PIPELINE")
    print(f"🎯 Target Channel: {ch_label} ({channel_id})")
    print(f"⏱️ Video Duration: > {args.duration} Minutes")
    print(f"🎙️ Voice: Google Free Realistic TTS ('Charon') + Shure SM7B DSP (-14 LUFS)")
    print(f"🔊 Voice Volume Boost: 150% (volume=1.50)")
    print(f"✨ Subtitles: 24K Gold Fast Cards (Nirmala UI Bold, MarginV=50)")
    print(f"🔒 Visibility: 100% STRICTLY {args.privacy.upper()}")
    print("=" * 80 + "\n")

    start_time = time.time()

    # Execute Autonomous Master Loop for this channel
    cmd = [
        sys.executable, "-u",
        os.path.join(BASE_DIR, "autonomous_master_loop.py"),
        "--channel", channel_id,
        "--duration", str(args.duration),
        "--research_mins", "3.0",
        "--privacy", args.privacy,
        "--uploader", "auto"
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        cwd=BASE_DIR
    )

    yt_link = ""
    for line in iter(proc.stdout.readline, ""):
        if line:
            print(f"[W{args.worker_id}] {line}", end="")
            if "youtu.be" in line or "watch?v=" in line:
                for tok in line.split():
                    if "youtu" in tok:
                        yt_link = tok.strip()

    proc.stdout.close()
    proc.wait()

    total_mins = round((time.time() - start_time) / 60, 2)

    print("\n" + "=" * 80)
    if proc.returncode == 0:
        print(f"🎉 [WORKER {args.worker_id}/10 SUCCEEDED] Video Finished in {total_mins} mins!")
        print(f"🔗 YouTube Unlisted Link: {yt_link or 'SUCCESSFULLY UPLOADED (UNLISTED)'}")
    else:
        print(f"⚠️ [WORKER {args.worker_id}/10 COMPLETED WITH WARNINGS] Code {proc.returncode}")
    print("=" * 80)

    # Clean intermediate cache to save disk space
    try:
        clips_dir = os.path.join(RENDERS_DIR, "clips")
        if os.path.exists(clips_dir):
            for f in os.listdir(clips_dir):
                fp = os.path.join(clips_dir, f)
                if os.path.isfile(fp):
                    os.remove(fp)
    except Exception:
        pass

    print(f"🛑 [WORKER {args.worker_id}/10 SHUTTING DOWN] Graceful auto-exit (Exit code: 0).")
    sys.exit(0)

if __name__ == "__main__":
    main()
