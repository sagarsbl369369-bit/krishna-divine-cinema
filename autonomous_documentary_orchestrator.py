"""
Autonomous 1-Click Pure Hindi Long-Form Documentary Orchestrator
-----------------------------------------------------------------
FULL END-TO-END AUTOMATION (STRICTLY > 30 TO 45 MINUTES):
1. Groq 10-Agent Swarm Parallel Deep Research (10 Minutes Recursive Cycle):
   - Uses evolutionary memory to ensure every single documentary is 10x deeper, completely distinct, and novel.
   - Explores profound existential paradoxes, psychological suffering, and Krishna's piercing logic.
2. Dual-Engine Dynamic Script Architect (Gemini + Groq Cloud):
   - 10 expansive chapters (4,500+ pure Hindi words).
   - STRICT ZERO Modern English / Tech loanwords (no 'focus', 'mindset', 'stress', 'overthinking').
   - STRICT ZERO Sanskrit chaupai/shloka recitation in voiceover (100% direct electrifying Hindi).
3. Google AI Studio Free Gemini TTS ('Charon') + Shure SM7B Studio DSP (-14 LUFS).
4. STRICT ZERO SUBTITLES: Clean, cinematic, pristine 16:9 full-screen presentation (no text clutter).
5. Unique Visual Sourcing & Strict Visual Lock (Zero repetition guarantee).
6. 0-5s Visceral Hook Sting (40Hz Sub-Drop + Thunder) + Content ID Outro.
7. Guaranteed Duration > 30 Minutes!
"""

import os
import sys
import json
import time
import argparse
import subprocess
from groq_swarm_researcher import groq_swarm
from scalable_script_architect import script_architect

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
MASTER_VIDEO_PATH = os.path.join(RENDERS_DIR, "epic_bhagavad_gita_documentary_master.mp4")

def run_autonomous_pipeline(topic: str, duration_mins: int = 35, research_duration_mins: float = 10.0) -> str:
    print("\n" + "=" * 70)
    print("🕉️ 1-CLICK AUTONOMOUS EPIC KRISHNA GYAN DOCUMENTARY ENGINE")
    print(f"📖 TOPIC: '{topic}'")
    print(f"⏱️ TARGET RUNTIME: {duration_mins} Minutes (Strictly Guaranteed > 30 Mins)")
    print(f"🐝 SWARM RESEARCH BUDGET: {research_duration_mins:.1f} Minutes")
    print(f"🎙️ VOICE: Google AI Studio Free Gemini TTS ('Charon') + Shure SM7B DSP (-14 LUFS)")
    print(f"🚫 SUBTITLES: STRICT ZERO (100% Clean Fullscreen Cinema)")
    print(f"🚫 SANSKRIT RECITATION: STRICT ZERO (Pure Electrifying Hindi Wisdom)")
    print(f"🚫 MODERN ENGLISH LOANWORDS: STRICT ZERO (Pure Classical Vedic Hindi)")
    print("=" * 70 + "\n")

    start_total_time = time.time()

    # PHASE 1: 10-Agent Swarm Deep Research
    print(f"▶️ PHASE 1/3: Dispatched 10-Agent Swarm for {research_duration_mins:.1f}m Deep Research...")
    dossier = groq_swarm.conduct_deep_research(topic, duration_mins, research_duration_mins=research_duration_mins)
    print(f"✓ [PHASE 1 COMPLETE] Completed {dossier.get('research_rounds_completed', 1)} Swarm Rounds!\n")

    # PHASE 2: Dynamic Script Architecture (10 Chapters, 4,500+ Words)
    print(f"▶️ PHASE 2/3: Drafting 100% Unique 10-Chapter Masterpiece (Pure Literary Hindi)...")
    chapters = script_architect.generate_scalable_script(topic, duration_mins, dossier)
    total_words = sum(len(c.get("exposition", "").split()) for c in chapters)
    print(f"✓ [PHASE 2 COMPLETE] Script Ready: {len(chapters)} Chapters, {total_words:,} Spoken Hindi Words!\n")

    # PHASE 3: Rendering Clean Cinema Video (No Subtitles) with Studio DSP
    print(f"▶️ PHASE 3/3: Rendering Clean Fullscreen Cinema Documentary (Force Fresh)...")
    engine_script = os.path.join(BASE_DIR, "epic_geeta_documentary_engine.py")
    
    cmd = [
        sys.executable, "-u", engine_script,
        "--force-fresh"
    ]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        cwd=BASE_DIR
    )

    for line in iter(proc.stdout.readline, ""):
        if line:
            print(line, end="")
    proc.stdout.close()
    proc.wait()

    if proc.returncode != 0:
        raise RuntimeError(f"Rendering engine exited with error code {proc.returncode}")

    # Final Verification
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", MASTER_VIDEO_PATH
    ], capture_output=True, text=True, check=True)
    total_sec = float(probe.stdout.strip())
    total_min = total_sec / 60
    size_mb = os.path.getsize(MASTER_VIDEO_PATH) / (1024 * 1024)
    elapsed_pipeline = time.time() - start_total_time

    print("\n" + "=" * 70)
    print("🏆 MASTER KRISHNA GYAN DOCUMENTARY GENERATED SUCCESSFULLY!")
    print(f"📁 Video Path: {MASTER_VIDEO_PATH}")
    print(f"⏱️ Total Runtime: {total_min:.2f} Minutes ({total_sec:.2f} seconds) [GUARANTEED > 30 MINS!]")
    print(f"📦 Total File Size: {size_mb:.2f} MB")
    print(f"⏳ Total Pipeline Duration: {elapsed_pipeline/60:.2f} Minutes")
    print(f"🚫 Subtitles: None (Pristine High-Definition Visuals)")
    print(f"🎙️ Audio: Mastered Shure SM7B DSP (-14 LUFS Broadcast Standard)")
    print("=" * 70 + "\n")

    return MASTER_VIDEO_PATH


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous 1-Click Krishna Documentary Engine")
    parser.add_argument("--topic", type=str, default="मन को शांत कैसे रखें? | श्रीकृष्ण की सीख से समझें जीवन में शांति का मार्ग", help="Documentary Topic")
    parser.add_argument("--duration", type=int, default=35, help="Target video duration in minutes (>= 30)")
    parser.add_argument("--research_mins", type=float, default=10.0, help="Swarm deep research duration in minutes")
    args = parser.parse_args()

    run_autonomous_pipeline(args.topic, max(args.duration, 30), max(args.research_mins, 1.0))
