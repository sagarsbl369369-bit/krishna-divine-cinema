import os
import sys
import time
import hypnotic_gemini_writer
import hypnotic_tts_master
import hypnotic_video_composer
import gita_studio_publisher

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_hypnotic_pipeline(custom_topic: str = None, target_channel: str = "ch_01", auto_upload: bool = False):
    print("=" * 80)
    print("🕉️ HYPNOTIC GEMINI + EDGE-TTS AUTONOMOUS VIDEO PRODUCTION PIPELINE")
    print("=" * 80)
    start_time = time.time()

    # Step 1: Generate Hypnotic Script via Google AI Studio Gemini Free API
    print("\n[STEP 1/3] Generating Pure Spoken Hypnotic Script via Google AI Studio...")
    script_text, topic_title = hypnotic_gemini_writer.generate_hypnotic_script(custom_topic)
    
    script_save_path = os.path.join(BASE_DIR, "latest_generated_script.txt")
    with open(script_save_path, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"✓ Saved master script to {script_save_path}")

    # Step 2: Synthesize Voiceover with Edge-TTS & Master Audio with Shure SM7B DSP
    print("\n[STEP 2/3] Synthesizing Studio Voiceover via Edge-TTS & Shure SM7B DSP...")
    audio_save_path = os.path.join(BASE_DIR, "latest_hypnotic_audio.mp3")
    hypnotic_tts_master.generate_hypnotic_voiceover(
        text=script_text,
        output_path=audio_save_path,
        voice="hi-IN-MadhurNeural"
    )

    # Step 3: Compose 1080p Cinematic Video & Hard-Stitch 173.25s Blue Laser Outro
    print("\n[STEP 3/3] Rendering 1080p Master Video & Stitching Blue Laser Outro...")
    final_video_path = hypnotic_video_composer.assemble_hypnotic_video(
        audio_path=audio_save_path,
        title=topic_title,
        channel_key=target_channel
    )

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f"🎉 PRODUCTION COMPLETE IN {elapsed/60:.1f} MINUTES!")
    print(f"📁 Video Package Delivered to: {os.path.dirname(final_video_path)}")
    print(f"🎬 Video File: {final_video_path}")
    print("=" * 80)

    # Optional Auto-Upload via Residential Session
    if auto_upload:
        print(f"\n[*] Auto-publishing to {target_channel} as UNLISTED...")
        gita_studio_publisher.publish_channel(target_channel)

    return final_video_path

if __name__ == "__main__":
    t_ch = sys.argv[1] if len(sys.argv) > 1 else "ch_01"
    run_hypnotic_pipeline(target_channel=t_ch)
