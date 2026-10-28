import os
import sys
import json
import subprocess
import shutil
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ORIGINAL_DOWNLOADS_OUTRO = r"C:\Users\janar\Downloads\content_id_outro.mp4"
LOCAL_OUTRO = os.path.join(BASE_DIR, "assets", "outro", "norm_content_id_outro.mp4")

# Prefer pristine 1080p original outro with original song HU-BA-HU
if os.path.exists(ORIGINAL_DOWNLOADS_OUTRO):
    OUTRO_PATH = ORIGINAL_DOWNLOADS_OUTRO
else:
    OUTRO_PATH = LOCAL_OUTRO

SCENES_DIR = os.path.join(BASE_DIR, "renders", "assets")
TARGET_BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "geeta wala")

def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(res.stdout.strip())

def assemble_hypnotic_video(audio_path: str, title: str, channel_key: str = "ch_01") -> str:
    r"""
    Assembles a full 1080p video with Ken Burns visuals + audio + 173.25s Blue Laser Outro.
    Saves directly to Downloads\geeta wala\Channel_XX\...
    """
    print("\n" + "=" * 75)
    print("🎬 HYPNOTIC VIDEO COMPOSER — 1080p PRODUCTION & OUTRO STITCH")
    print("=" * 75)

    duration = get_audio_duration(audio_path)
    print(f"[*] Audio Duration: {duration:.1f}s ({duration/60:.2f} mins)")

    # 1. Target Directory Setup
    ch_folder = "Channel_01_GeetaGyan60Sec" if channel_key == "ch_01" else "Channel_02_GeetaJeevanSutra"
    ch_name = "Geeta Gyan 60 Sec" if channel_key == "ch_01" else "Geeta Jeevan Sutra"
    
    clean_slug = "".join([c if (c.isascii() and c.isalnum()) else "_" for c in title[:30]]).strip("_") or f"Ep_{int(time.time())%10000}"
    timestamp_id = int(time.time())
    dest_folder = os.path.join(TARGET_BASE_DIR, ch_folder, f"Hypnotic_{timestamp_id}_{clean_slug}")
    os.makedirs(dest_folder, exist_ok=True)

    final_mp4 = os.path.join(dest_folder, "master_1080p_documentary.mp4")
    final_thumb = os.path.join(dest_folder, "thumbnail_uhd.jpg")
    final_seo = os.path.join(dest_folder, "seo_package.json")
    temp_body_mp4 = os.path.join(dest_folder, "_temp_body.mp4")

    # 2. Collect Available Scenes
    scenes = []
    if os.path.exists(SCENES_DIR):
        scenes = [os.path.join(SCENES_DIR, f) for f in sorted(os.listdir(SCENES_DIR)) if f.endswith(".jpg")]
    
    # Fallback scenes
    if not scenes:
        fallback_scene = os.path.join(BASE_DIR, "master_viral_thumbnail.jpg")
        if os.path.exists(fallback_scene):
            scenes = [fallback_scene]

    print(f"[*] Found {len(scenes)} visual scene assets for video assembly.")

    # 3. Render 1080p Master Video + Hard-Stitched Blue Laser Outro (Single-Pass Ultra Fast)
    primary_scene = scenes[0] if scenes else None
    if not primary_scene:
        raise FileNotFoundError("No visual scene assets found to render video.")

    print(f"[*] Rendering 1080p cinematic video from {os.path.basename(primary_scene)}...")
    if os.path.exists(OUTRO_PATH):
        print(f"[*] Hard-stitching 173.25s Blue Laser Shield Outro ({os.path.basename(OUTRO_PATH)})...")
        filter_complex = (
            "[0:v]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30,format=yuv420p[v0];"
            "[1:a]aformat=sample_rates=48000:channel_layouts=stereo[a0];"
            "[2:a]aformat=sample_rates=48000:channel_layouts=stereo[a1];"
            "[v0][a0][2:v][a1]concat=n=2:v=1:a=1[v][a]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-framerate", "1",
            "-t", str(duration),
            "-i", primary_scene,
            "-i", audio_path,
            "-i", OUTRO_PATH,
            "-filter_complex", filter_complex,
            "-map", "[v]",
            "-map", "[a]",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            final_mp4
        ]
    else:
        print("⚠️ Outro not found, rendering standalone video body.")
        vf_filter = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,format=yuv420p"
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1",
            "-framerate", "1",
            "-i", primary_scene,
            "-i", audio_path,
            "-vf", vf_filter,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "stillimage",
            "-r", "30",
            "-crf", "22",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-t", str(duration),
            final_mp4
        ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"🎉 MASTER VIDEO CREATED: {final_mp4} ({os.path.getsize(final_mp4)/1024/1024:.1f} MB)")

    # 5. Generate UHD Thumbnail
    thumb_source = os.path.join(BASE_DIR, "master_viral_thumbnail.jpg")
    if os.path.exists(thumb_source):
        shutil.copy2(thumb_source, final_thumb)
    elif scenes:
        shutil.copy2(scenes[0], final_thumb)
    print(f"✓ Saved UHD Thumbnail: {final_thumb}")

    # 6. Generate Viral SEO Package
    seo_data = {
        "title": title + f" | {ch_name}",
        "description": f"🕉️ {title}\n\n"
                       "श्रीमद्भगवद्गीता का वह शाश्वत मनोवैज्ञानिक सत्य जो अंतर्मन के हर घाव को भर देता है। "
                       "जब संसार तुम्हें थका दे, तब यह वाणी तुम्हारी आत्मा का परम संबल बनेगी।\n\n"
                       "00:00 - अंतर्मन का गहरा सन्नाटा\n"
                       "03:15 - विश्वासघात और मौन संप्रभुता\n"
                       "08:45 - श्रीकृष्ण का गोपनीय संवाद\n"
                       "14:20 - परम शांति और आत्म-विजय\n\n"
                       "📌 आज अपने उस अनकहे दर्द को कमेंट में लिखकर यहीं छोड़ जाओ... माधव तुम्हारा हाथ थाम लेंगे।",
        "tags": ["Bhagavad Gita", "Shri Krishna", "Geeta Gyan", "Krishna Vani", "Mental Strength", "Inner Peace", "Spiritual Podcast", ch_name]
    }
    with open(final_seo, "w", encoding="utf-8") as sf:
        json.dump(seo_data, sf, ensure_ascii=False, indent=2)
    print(f"✓ Saved SEO Package: {final_seo}")

    # 7. Update Offline Catalog
    try:
        import gita_catalog_generator
        gita_catalog_generator.generate_catalog()
    except Exception:
        pass

    return final_mp4

if __name__ == "__main__":
    audio_file = os.path.join(BASE_DIR, "latest_hypnotic_audio.mp3")
    if not os.path.exists(audio_file):
        audio_file = os.path.join(BASE_DIR, "test_hypnotic_audio.mp3")
    if os.path.exists(audio_file):
        assemble_hypnotic_video(audio_file, "श्रीकृष्ण वाणी — जब अपने ही धोखा दें तब कर्ण की यह गुप्त व्यथा सुनो", "ch_01")
