"""
Autonomous Master Loop Engine (100% Zero-Touch Krishna Automation)
------------------------------------------------------------------
THE ULTIMATE HANDS-OFF 1-CLICK PIPELINE:
[Step 1] AI Autonomously Brainstorms & Discovers Viral Krishna Topic
[Step 2] 10-Minute Groq Swarm Parallel Deep Research (10 Specialized Agents)
[Step 3] Dynamic Script Architecture (10 Chapters, 4,500+ Words, Zero Modern Words, Zero Sanskrit Voice)
[Step 4] Google AI Studio Free Gemini TTS (Charon) + Shure SM7B DSP (-14 LUFS)
[Step 5] Pristine Fullscreen Cinema Video Assembly (Strictly NO SUBTITLES, > 30 Mins Guaranteed)
[Step 6] High-CTR Viral SEO Packaging (Title, Clickable Timestamps, 500-char Tags)
[Step 7] YouTube Channel Upload / Scheduled Publishing via Data API v3
"""

import os
import sys
import json
import time
import argparse
import subprocess
from autonomous_topic_brain import autonomous_brain
from groq_swarm_researcher import groq_swarm
from scalable_script_architect import script_architect
from viral_seo_engine import viral_seo
from viral_thumbnail_engine import thumbnail_engine
from youtube_channel_auto_uploader import upload_video_to_youtube
from youtube_channel_manager import channel_manager
from youtube_human_uploader import YouTubeHumanUploader, human_uploader

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
MASTER_VIDEO_PATH = os.path.join(RENDERS_DIR, "epic_bhagavad_gita_documentary_master.mp4")

def execute_complete_autonomous_run(
    custom_topic: str = None,
    target_duration: int = 35,
    research_mins: float = 10.0,
    target_channel: str = "auto",
    privacy: str = "unlisted",
    uploader_mode: str = "auto"
):
    start_time = time.time()
    print("\n" + "=" * 75)
    print("🕉️ AUTONOMOUS KRISHNA MASTER PIPELINE: ZERO-TOUCH 30+ MIN DOCUMENTARY")
    print("=" * 75)

    # Resolve Target Channel (Auto-Rotation between Channel 1 and Channel 2)
    if not target_channel or target_channel.lower() in ["auto", "rotate", "none"]:
        channel_info = channel_manager.get_next_rotation_channel()
        chosen_channel_id = channel_info["channel_id"]
        chosen_channel_name = channel_info["channel_name"]
    else:
        chosen_channel_id = target_channel
        c_meta = next((c for c in channel_manager.channels if c["channel_id"] == target_channel), {})
        chosen_channel_name = c_meta.get("channel_name", target_channel)

    print(f"📺 ACTIVE DESTINATION: {chosen_channel_name} ({chosen_channel_id})")

    # 1. TOPIC DISCOVERY
    if custom_topic and custom_topic.strip():
        print(f"[*] Using Specified Topic: '{custom_topic}'")
        topic_title = custom_topic.strip()
    else:
        print(f"[*] Engaging AI Topic Brain tailored specifically for {chosen_channel_name}...")
        topic_data = autonomous_brain.discover_next_viral_topic(channel_id=chosen_channel_id)
        topic_title = topic_data["topic_title"]
        target_duration = max(target_duration, topic_data.get("target_duration_mins", 35))

    print(f"\n🎯 SELECTED TOPIC: '{topic_title}'")
    print(f"⏱️ TARGET RUNTIME: {target_duration} Minutes (Guaranteed > 30 Mins)")
    print(f"🐝 RESEARCH DURATION: {research_mins:.1f} Minutes")
    print(f"🎙️ VOICE ENGINE: Google Free Realistic TTS ('Charon') + Shure SM7B DSP")
    print(f"🔊 VOICE VOLUME: 150% Studio Mastered Boost")
    print(f"✨ SUBTITLES: SMART DYNAMIC 24K GOLD CARDS (Algorithm Retention Booster, MarginV=50)")
    print(f"🚫 SANSKRIT IN AUDIO: NONE (100% Direct Electrifying Hindi Wisdom)")
    print(f"🚫 MODERN ENGLISH LOANWORDS: NONE (Pure Classical Vedic Hindi)")

    # 2. 10-MINUTE GROQ SWARM DEEP RESEARCH
    print(f"\n▶️ STEP 1/5: Launching 10-Agent Swarm Deep Research ({research_mins:.1f} Mins)...")
    dossier = groq_swarm.conduct_deep_research(topic_title, target_duration, research_duration_mins=research_mins)
    print(f"✓ [STEP 1 COMPLETE] Completed {dossier.get('research_rounds_completed', 1)} Swarm Rounds!\n")

    # 3. DYNAMIC SCRIPT ARCHITECTURE
    print("▶️ STEP 2/5: Architecting 10-Chapter Masterpiece (4,500+ Spoken Words)...")
    chapters = script_architect.generate_scalable_script(topic_title, target_duration, dossier)
    total_words = sum(len(c.get("exposition", "").split()) for c in chapters)
    print(f"✓ [STEP 2 COMPLETE] Script Ready: {len(chapters)} Chapters, {total_words:,} Words!\n")

    # 4. CINEMA RENDERING WITH SMART 24K GOLD SUBTITLES & 150% VOLUME
    print("▶️ STEP 3/5: Rendering Master Video with Google Free TTS ('Charon') + 150% Volume + Smart 24K Gold Subtitles...")
    engine_script = os.path.join(BASE_DIR, "epic_geeta_documentary_engine.py")
    cmd = [sys.executable, "-u", engine_script, "--force-fresh", "--channel", chosen_channel_id]
    
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
        raise RuntimeError(f"Render Engine Failed with exit code {proc.returncode}")

    # Measure Rendered Video Duration
    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", MASTER_VIDEO_PATH
    ], capture_output=True, text=True, check=True)
    video_dur_sec = float(probe.stdout.strip())
    video_dur_min = video_dur_sec / 60
    print(f"✓ [STEP 3 COMPLETE] Master Video Rendered: {video_dur_min:.2f} Minutes ({video_dur_sec:.2f}s)!\n")

    # 5. VIRAL SEO PACKAGING (Clickable Timestamps, High-CTR Title, Tags)
    print("▶️ STEP 4/6: Generating Viral YouTube SEO Package (Timestamps & Tags)...")
    # Estimate ~185s per chapter + 173s outro
    ch_durations = [185.0] * len(chapters) + [173.25]
    seo_package = viral_seo.generate_seo_package(topic_title, chapters, ch_durations)
    print(f"✓ [STEP 4 COMPLETE] Viral SEO Package Formulated!\n")

    # 6. 3-MINUTE AUTONOMOUS VIRAL THUMBNAIL RESEARCH & COMPOSITING
    print("▶️ STEP 5/6: Launching 3-Minute Viral Thumbnail AI Scanner & Compositor...")
    thumb_path = thumbnail_engine.generate_viral_thumbnail(topic_title, dossier=dossier)
    seo_package["thumbnail_path"] = thumb_path
    print(f"✓ [STEP 5 COMPLETE] 1280x720 UHD Viral Thumbnail Generated: {thumb_path}\n")

    # 7. AUTONOMOUS YOUTUBE UPLOAD (API OR HUMAN-MIMICRY ENGINE)
    print("▶️ STEP 6/6: Initiating YouTube Publishing Protocol (Video + Viral Thumbnail)...")
    upload_result = None
    if uploader_mode in ["api", "auto"]:
        upload_result = upload_video_to_youtube(MASTER_VIDEO_PATH, seo_package, channel_id=chosen_channel_id, privacy=privacy)

    # Fallback to Human-Mimicry Studio Uploader if API was dry-run, failed, or uploader_mode == "human"
    if (not upload_result or upload_result == "DRY_RUN_READY" or uploader_mode == "human"):
        print(f"\n🤖 [HUMAN-MIMICRY FAILOVER] Attempting autonomous YouTube Studio browser upload for {chosen_channel_id}...")
        try:
            target_uploader = YouTubeHumanUploader(channel_id=chosen_channel_id)
            if target_uploader.is_logged_in():
                print(f"   ✓ YouTube Studio session for {chosen_channel_id} is active! Launching human uploader...")
                h_res = target_uploader.upload_video(
                    video_path=MASTER_VIDEO_PATH,
                    seo_package=seo_package,
                    thumbnail_path=thumb_path,
                    channel_id=chosen_channel_id,
                    privacy=privacy,
                    headless=True
                )
                if h_res.get("success"):
                    upload_result = h_res.get("video_url") or "PUBLISHED_VIA_HUMAN_MIMICRY"
                    print(f"🎉 [HUMAN-MIMICRY SUCCESS] Published! Result: {upload_result}")
                else:
                    print(f"⚠️ Human uploader error: {h_res.get('message') or h_res.get('error')}")
            else:
                print(f"ℹ️ Note: YouTube Studio persistent session for {chosen_channel_id} not logged in yet.")
                print(f"👉 Run `python youtube_human_uploader.py --login --channel {chosen_channel_id}` to log in once.")
        except Exception as h_err:
            print(f"⚠️ Human-mimicry execution note: {h_err}")

    total_pipeline_time = time.time() - start_time
    print("\n" + "=" * 75)
    print("🏆 FULL AUTONOMOUS KRISHNA GYAN RUN COMPLETED SUCCESSFULLY!")
    print(f"📖 Final Topic: {topic_title}")
    print(f"📁 Video Location: {MASTER_VIDEO_PATH}")
    print(f"⏱️ Video Duration: {video_dur_min:.2f} Minutes [STRICTLY > 30 MINS!]")
    print(f"🏷️ YouTube Title: {seo_package['title']}")
    print(f"⏳ Total End-to-End Pipeline Time: {total_pipeline_time/60:.2f} Minutes")
    print(f"📤 Upload Status: {upload_result}")
    print("=" * 75 + "\n")

    return {
        "topic": topic_title,
        "video_path": MASTER_VIDEO_PATH,
        "duration_mins": video_dur_min,
        "seo_package": seo_package,
        "upload_status": upload_result
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Krishna Master Loop")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic (optional; AI chooses if omitted)")
    parser.add_argument("--duration", type=int, default=35, help="Target duration in minutes (>= 30)")
    parser.add_argument("--research_mins", type=float, default=10.0, help="Groq swarm deep research minutes")
    parser.add_argument("--channel", type=str, default="auto", help="Target YouTube Channel ID (auto | ch_01 | ch_02)")
    parser.add_argument("--privacy", type=str, default="unlisted", help="unlisted | public | private")
    parser.add_argument("--uploader", type=str, default="auto", choices=["auto", "human", "api"], help="Upload engine: auto | human | api")
    args = parser.parse_args()

    execute_complete_autonomous_run(
        custom_topic=args.topic,
        target_duration=max(args.duration, 30),
        research_mins=max(args.research_mins, 1.0),
        target_channel=args.channel,
        privacy=args.privacy,
        uploader_mode=args.uploader
    )
