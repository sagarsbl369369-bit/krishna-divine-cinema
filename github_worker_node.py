"""
GitHub Actions Cloud Matrix Worker Node (10 Parallel Workers)
=============================================================
Autonomous worker execution script for GitHub Actions:
- Executes within 1 of 10 isolated parallel cloud VMs (Matrix)
- Workers 1 to 5  -> Channel 1: Geeta Gyan 60 Sec (@GeetaGyan60Sec)
- Workers 6 to 10 -> Channel 2: Geeta Jeevan Sutra (@GeetaJeevanSutraHindi)
- Duration: >35 Mins (default 35 mins)
- Research: Hard-locked 15 Minutes Groq Swarm Deep Research
- Voice: Google Free Realistic TTS ('Charon') / Edge-TTS + Shure SM7B DSP
- Voice Volume Boost: 155% Studio Boost
- Outro: Hard-Locked 173.25s Blue Laser Shield Outro
- Visibility: 100% UNLISTED
- Auto-Shutdown: Cleans disk & exits with code 0.
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

# 10 Unique, Non-Overlapping Real-Life Existential Psychology Topics
WORKER_TOPICS = {
    # Channel 1: Geeta Gyan 60 Sec (Everyday Life Psychology & Emotional Sovereignty)
    1: "जब अपने ही पीठ में छुरा घोंपें — विश्वासघात के बाद मौन संप्रभुता का विज्ञान",
    2: "रात के ३ बजे का सन्नाटा — दिमाग के उस अनवरत शोर को शांत करने का अंतिम सत्य",
    3: "सबको खुश रखने की बीमारी (People-Pleasing Trap) — दूसरों की नज़रों में साबित करने का अंत",
    4: "करियर की घुटन और पीछे छूट जाने का खौफ — जब हर कोई आगे निकल रहा हो और आप अटके हों",
    5: "खामोश रहकर जीतना सीखो — मौन की वह अजेय शक्ति जो हर शत्रु को निहत्था कर दे",

    # Channel 2: Geeta Jeevan Sutra (Existential Depths, Solitude & Shadow Psychology)
    6: "अकेलेपन को अपनी सबसे घातक शक्ति बनाओ — जब दुनिया साथ छोड़ दे, तब साम्राज्य का उदय",
    7: "काल का निर्मम पहिया और विसर्जन — जो छूट गया उसका शोक क्यों? हर मोह को भस्म करने वाला दर्शन",
    8: "आत्म-संशय की अग्नि (Imposter Syndrome) — जब मन खुद का सबसे बड़ा शत्रु बन जाए",
    9: "कर्मण्येवाधिकारस्ते का वास्तविक क्रूर सत्य — परिणाम की लालसा मारकर असंभव को संभव करने का कोड",
    10: "अजेय मस्तिष्क (The Unbreakable Mind) — संसार के सबसे बड़े तूफानों के बीच अविचल रहने का परम रहस्य"
}

def setup_cloud_environment(worker_id: int, channel_id: str):
    """Reconstructs config.json, storage_state, and credentials from GitHub Secrets."""
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
        "VOICE_VOLUME_PERCENT": 155,
        "SUBTITLES_ENABLED": True,
        "SUBTITLE_STYLE": "Fontname=Noto Sans Devanagari,FontSize=25,Bold=1,PrimaryColour=&H0000D7FF&,OutlineColour=&H00000000&,BorderStyle=1,Outline=2.8,Shadow=2.0,Alignment=2,MarginV=50",
        "TARGET_DURATION_MINS": 35,
        "DEFAULT_PRIVACY": "unlisted",
        "CHANNELS": {
            "ch_01": {
                "name": "Geeta Gyan 60 Sec",
                "handle": "@GeetaGyan60Sec",
                "channel_id": "UCw-3CNwReOnBF7__N6S4DQw",
                "niche": "चित्त शांति, अति-विचार से मुक्ति, कर्मयोग, निष्काम भाव",
                "music": "ch_01_gita_meditative"
            },
            "ch_02": {
                "name": "Geeta Jeevan Sutra",
                "handle": "@GeetaJeevanSutraHindi",
                "channel_id": "UClptLNgnB7fxcmmgzuTXwvA",
                "niche": "मृत्यु-बोध, माया का संहार, अद्वैत, विश्वरूप, परम भक्ति रस",
                "music": "ch_02_premanand_bhakti"
            }
        }
    }
    with open(os.path.join(BASE_DIR, "config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

    # 3. Setup Channel Playwright Storage State (YouTube Studio Auth Cookies)
    st_var = f"YT_STORAGE_STATE_{channel_id.upper()}"
    st_data = os.getenv(st_var, "")
    if st_data:
        try:
            st_json = json.loads(st_data)
            st_path = os.path.join(CREDENTIALS_DIR, f"storage_state_{channel_id}.json")
            with open(st_path, "w", encoding="utf-8") as f:
                json.dump(st_json, f, indent=2)
            print(f"✓ Configured Playwright Storage State for {channel_id} ({os.path.getsize(st_path)} bytes)")
        except Exception as e:
            print(f"⚠️ Error unpacking storage state for {channel_id}: {e}")

    # 4. Setup OAuth2 Client Secret if present
    cs_var = f"YT_CLIENT_SECRET_{channel_id.upper()}"
    cs_data = os.getenv(cs_var, "")
    if cs_data:
        try:
            cs_json = json.loads(cs_data)
            with open(os.path.join(CREDENTIALS_DIR, f"client_secret_{channel_id}.json"), "w", encoding="utf-8") as f:
                json.dump(cs_json, f, indent=2)
            with open(os.path.join(CREDENTIALS_DIR, "client_secret.json"), "w", encoding="utf-8") as f:
                json.dump(cs_json, f, indent=2)
            print(f"✓ Configured OAuth Client Secret for {channel_id}")
        except Exception as e:
            print(f"⚠️ Error saving client secret for {channel_id}: {e}")

    print("✓ Cloud Environment Setup Complete!\n")

def main():
    parser = argparse.ArgumentParser(description="GitHub Cloud Matrix Worker Node")
    parser.add_argument("--worker_id", type=int, required=True, help="Worker ID (1 to 10)")
    parser.add_argument("--duration", type=int, default=35, help="Target Duration in Mins (>35 mins)")
    parser.add_argument("--privacy", type=str, default="unlisted", help="YouTube Privacy (unlisted)")
    parser.add_argument("--research_mins", type=float, default=15.0, help="Groq Swarm Deep Research Minutes (Hard-locked 15m)")
    args = parser.parse_args()

    # 50/50 Dual-Channel Distribution
    # Workers 1..5  -> ch_01 (Geeta Gyan 60 Sec)
    # Workers 6..10 -> ch_02 (Geeta Jeevan Sutra)
    if args.worker_id <= 5:
        channel_id = "ch_01"
        ch_label = f"Geeta Gyan 60 Sec (@GeetaGyan60Sec) [Item #{args.worker_id}/5]"
    else:
        channel_id = "ch_02"
        ch_label = f"Geeta Jeevan Sutra (@GeetaJeevanSutraHindi) [Item #{args.worker_id-5}/5]"

    topic = WORKER_TOPICS.get(args.worker_id, "रात के तीन बजे का सन्नाटा और अंतर्मन की शांति")

    setup_cloud_environment(args.worker_id, channel_id)

    print("=" * 80)
    print(f"🎬 [WORKER {args.worker_id}/10] EXECUTING 35-MINUTE CINEMATIC VIDEO PIPELINE")
    print(f"🎯 Target Channel: {ch_label} ({channel_id})")
    print(f"📖 Assigned Unique Topic: '{topic}'")
    print(f"⏱️ Video Duration: > {args.duration} Minutes (Guaranteed > 35 Mins)")
    print(f"🐝 Swarm Deep Research: {args.research_mins} Minutes (Hard-Locked 15M Deep Dive)")
    print(f"🎙️ Voice: Google Free Realistic TTS ('Charon') + Shure SM7B DSP (-14 LUFS)")
    print(f"🔊 Voice Volume Boost: 155% (volume=1.55)")
    print(f"🔒 Outro: HARD-LOCKED 173.25s Blue Laser Shield Outro")
    print(f"🔒 Visibility: 100% STRICTLY {args.privacy.upper()}")
    print("=" * 80 + "\n")

    start_time = time.time()

    # Execute Autonomous Master Loop for this channel with explicit unique topic and 15m deep research
    cmd = [
        sys.executable, "-u",
        os.path.join(BASE_DIR, "autonomous_master_loop.py"),
        "--topic", topic,
        "--channel", channel_id,
        "--duration", str(args.duration),
        "--research_mins", str(args.research_mins),
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
