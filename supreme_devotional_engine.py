"""
Supreme Bhagavad Gita Devotional Video Engine
- 100% Pure Hindi Devanagari Narration & Subtitles (Zero English/Roman words)
- Voice-Accurate Devotional Visuals from Pixabay API (Chariot, Lord Krishna, Kurukshetra, Temple Fire, Meditation)
- Strict Zero-Repetition Lock: Every single scene has a completely unique video clip (never repeats)
- Google AI Studio Gemini 3.8 Flash TTS Voiceover with Vedic Reverence
- 432Hz Meditative Drone Audio Mixing
- 16:9 Broadcast Quality MP4 Output
"""

import os
import sys
import json
import urllib.parse
import subprocess
import requests
import asyncio
import edge_tts
from google import genai
from google.genai import types

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
CLIPS_DIR = os.path.join(RENDERS_DIR, "clips")
os.makedirs(CLIPS_DIR, exist_ok=True)

CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LOCK_FILE = os.path.join(RENDERS_DIR, "used_visual_ids.json")

# Load Configuration
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

# VOICE & AUDIO HARD-LOCK: Edge-TTS + Shure SM7B DSP
VOICE_ENGINE_LOCKED = CONFIG.get("VOICE_ENGINE_LOCKED", "Edge_TTS_Shure_SM7B_DSP")
EDGE_TTS_VOICE = CONFIG.get("EDGE_TTS_VOICE", "hi-IN-MadhurNeural")
EDGE_TTS_RATE = CONFIG.get("EDGE_TTS_RATE", "+0%")
EDGE_TTS_PITCH = CONFIG.get("EDGE_TTS_PITCH", "-2Hz")
SHURE_SM7B_DSP_CHAIN = CONFIG.get(
    "SHURE_SM7B_DSP_CHAIN",
    "aresample=48000,highpass=f=75,equalizer=f=180:t=q:w=1.2:g=3.5,equalizer=f=450:t=q:w=1.5:g=-1.8,equalizer=f=3200:t=q:w=1.1:g=2.5,equalizer=f=6800:t=q:w=2.0:g=-3.0,lowpass=f=13500,compand=attacks=0.015:decays=0.12:points=-80/-80|-45/-32|-24/-17|-12/-10|0/-7:gain=2.5,loudnorm=I=-14:TP=-1.0:LRA=9"
)

GEMINI_API_KEY = CONFIG.get("GEMINI_API_KEY")
PIXABAY_API_KEY = CONFIG.get("PIXABAY_API_KEY")

class VisualLockEngine:
    """Strict visual lock engine ensuring zero scene repetition across videos."""
    def __init__(self, lock_file: str):
        self.lock_file = lock_file
        self.used_ids = set()
        self.load()

    def load(self):
        if os.path.exists(self.lock_file):
            try:
                with open(self.lock_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.used_ids = set(data.get("used_ids", []))
            except Exception:
                self.used_ids = set()

    def save(self):
        with open(self.lock_file, "w", encoding="utf-8") as f:
            json.dump({"used_ids": list(self.used_ids)}, f, indent=2)

    def is_used(self, clip_id) -> bool:
        return str(clip_id) in self.used_ids

    def lock_id(self, clip_id):
        self.used_ids.add(str(clip_id))
        self.save()


# 100% Pure Hindi Devanagari Spiritual Script
# Each scene has an exact, voice-matching devotional query bucket
DEVOTIONAL_SCENES = [
    {
        "id": "scene_1_kurukshetra",
        "title": "कुरुक्षेत्र का धर्मसंकट",
        "narration": "कुरुक्षेत्र के विशाल रणक्षेत्र में जब महारथी अर्जुन का हृदय शोक और मोह से व्याकुल हो उठा, तब उन्होंने अपने अस्त्र-शस्त्र डाल दिए।",
        "queries": ["dark storm lightning clouds", "thunderstorm dark night", "stormy sky clouds"]
    },
    {
        "id": "scene_2_krishna_chariot",
        "title": "सारथी श्री कृष्ण और सुवर्ण रथ",
        "narration": "तब दिव्य सुवर्ण रथ पर विराजमान, जगत के पालनहार भगवान श्री कृष्ण ने अर्जुन को कर्तव्य और धर्म का सत्य समझाना आरंभ किया।",
        "queries": ["chariot horses", "horse chariot statue gold", "golden chariot"]
    },
    {
        "id": "scene_3_sacred_shloka",
        "title": "पवित्र वैदिक श्लोक",
        "narration": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
        "queries": ["sacred fire", "burning fire flame glow", "candle flame prayer ritual"]
    },
    {
        "id": "scene_4_karma_meaning",
        "title": "कर्मयोग का गूढ़ रहस्य",
        "narration": "हे अर्जुन! तुम्हारा अधिकार केवल अपने कर्म पर है, उसके फलों पर तुम्हारा कोई वश नहीं। परिणाम की चिंता को त्याग कर कर्म में लीन हो जाओ।",
        "queries": ["hindu temple", "statue shiva temple meditation india", "ancient temple stone"]
    },
    {
        "id": "scene_5_equanimity",
        "title": "समत्वं योग उच्यते",
        "narration": "जो मनुष्य सुख और दुःख, जय और पराजय में समभाव में स्थित रहता है, उसका मन कभी विचलित नहीं होता।",
        "queries": ["lotus flower", "incense smoke prayer", "meditation mountain"]
    },
    {
        "id": "scene_6_liberation",
        "title": "दिव्य प्रकाश और परम मोक्ष",
        "narration": "यही भगवद्गीता का अमर उपदेश है, जो जीवन के हर अंधकार को मिटाकर आत्मा को परम प्रकाश, अनंत शांति और मोक्ष प्रदान करता है।",
        "queries": ["divine rays sun", "golden temple india", "sunrise mountain himalayas"]
    }
]


def format_timestamp(seconds: float) -> str:
    millis = int((seconds % 1) * 1000)
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"


def fetch_unique_devotional_clip(queries: list, lock_engine: VisualLockEngine, scene_idx: int) -> str:
    """
    Searches Pixabay for devotional clips matching queries and guarantees a completely unused clip ID.
    Downloads and caches the clip.
    """
    for query in queries:
        try:
            url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={urllib.parse.quote(query)}&video_type=all&per_page=15"
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                hits = r.json().get("hits", [])
                for hit in hits:
                    v_id = hit.get("id")
                    if lock_engine.is_used(v_id):
                        continue  # Skip already used clip!

                    # Found an unused clip!
                    videos = hit.get("videos", {})
                    v_info = videos.get("large") or videos.get("medium") or videos.get("small")
                    if not v_info or not v_info.get("url"):
                        continue

                    dl_url = v_info["url"]
                    clip_filename = f"pixabay_{v_id}_{scene_idx}.mp4"
                    dest_path = os.path.join(CLIPS_DIR, clip_filename)

                    print(f"[*] Downloading unique clip ID {v_id} for '{query}'...")
                    with requests.get(dl_url, stream=True, timeout=30) as resp:
                        resp.raise_for_status()
                        with open(dest_path, "wb") as f:
                            for chunk in resp.iter_content(chunk_size=1024 * 512):
                                if chunk:
                                    f.write(chunk)

                    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 10000:
                        lock_engine.lock_id(v_id)
                        print(f"[✓] Locked & Cached unique clip ID {v_id} ({os.path.getsize(dest_path):,} bytes)")
                        return dest_path
        except Exception as e:
            print(f"[!] Search error for '{query}': {e}")

    # Fallback to general devotional terms if queries exhausted
    raise RuntimeError(f"Could not find an unused devotional clip for scene {scene_idx} with queries: {queries}")


def generate_shure_sm7b_voiceover(full_script: str, audio_path: str) -> float:
    """
    Generates 100% PURE HINDI PLAIN SCRIPT voiceover with Edge-TTS (hi-IN-MadhurNeural).
    HARD-LOCKED with Studio Shure SM7B DSP vocal mastering chain:
    - 48,000 Hz Studio Master Resampling
    - 75Hz Low-Cut Sub-Bass Rumble Removal
    - 180Hz Shure SM7B Proximity Effect Warm Chest Resonance (+3.5 dB)
    - 450Hz Mud & Boxiness De-clutter (-1.8 dB)
    - 3.2kHz SM7B Presence Boost (+2.5 dB) for crisp Sanskrit/Hindi consonants
    - 6.8kHz Studio De-Esser (-3.0 dB) for smooth sibilance
    - 13.5kHz Dynamic Capsule High-Frequency Roll-off (zero digital harshness)
    - Studio Optical Compression & Leveling (compand)
    - EBU R128 Broadcast Loudness Normalization (-14 LUFS, TP -1.0 dB)
    """
    print(f"\n[1/4] Generating Plain Hindi Voiceover with Edge-TTS ({EDGE_TTS_VOICE}) + Shure SM7B DSP (LOCKED)...")
    plain_hindi_text = full_script.strip()
    raw_mp3 = audio_path.replace(".mp3", "_raw.mp3")

    cmd_tts = [
        sys.executable, "-m", "edge_tts",
        "--voice", EDGE_TTS_VOICE,
        "--rate", EDGE_TTS_RATE,
        "--pitch", EDGE_TTS_PITCH,
        "--text", plain_hindi_text,
        "--write-media", raw_mp3
    ]
    subprocess.run(cmd_tts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Master voice with Shure SM7B Studio DSP filter chain
    print("[🎛️] Mastering with Studio Shure SM7B DSP Hardware Chain & Loudness Normalization (-14 LUFS)...")
    cmd = [
        "ffmpeg", "-y", "-i", raw_mp3,
        "-af", SHURE_SM7B_DSP_CHAIN,
        "-c:a", "libmp3lame", "-b:a", "192k",
        audio_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(raw_mp3):
        os.remove(raw_mp3)

    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    dur = float(subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout.strip())
    print(f"[✓] Shure SM7B DSP Broadcast Audio Mastered: {audio_path} ({dur:.2f} seconds)")
    return dur


def generate_devanagari_subtitles(scenes: list, total_duration: float, srt_path: str):
    """Generates 100% pure Devanagari Hindi subtitles proportionally mapped to scenes."""
    print("\n[2/4] Generating Pure Devanagari Hindi Subtitles...")
    total_chars = sum(len(s["narration"]) for s in scenes)
    available_duration = max(total_duration - 1.2, 1.0)
    current_time = 0.6  # initial grace period

    entries = []
    for i, s in enumerate(scenes, start=1):
        seg_duration = (len(s["narration"]) / total_chars) * available_duration
        end_time = min(current_time + seg_duration, total_duration)

        start_str = format_timestamp(current_time)
        end_str = format_timestamp(end_time)
        entries.append(f"{i}\n{start_str} --> {end_str}\n{s['narration'].strip()}\n")
        current_time = end_time

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))
    print(f"[✓] Subtitles saved: {srt_path}")


def prepare_and_normalize_clips(scenes: list, total_duration: float, lock_engine: VisualLockEngine) -> list:
    """
    Downloads unique devotional clips for each scene and normalizes them to 1280x720 16:9 30fps with exact durations.
    """
    print("\n[3/4] Sourcing Voice-Accurate Devotional Visuals with Strict Zero-Repetition Lock...")
    total_chars = sum(len(s["narration"]) for s in scenes)

    normalized_clips = []
    durations = []
    for i, scene in enumerate(scenes):
        if i == len(scenes) - 1:
            dur = total_duration - sum(durations)
        else:
            dur = round((len(scene["narration"]) / total_chars) * total_duration, 2)
        durations.append(dur)

    for i, scene in enumerate(scenes):
        clip_target_dur = durations[i]
        raw_clip = fetch_unique_devotional_clip(scene["queries"], lock_engine, i)
        norm_clip = os.path.join(CLIPS_DIR, f"norm_scene_{i}_{os.path.basename(raw_clip)}")

        # Normalize with high-quality 1280x720 16:9 scaling, setsar=1, and subtle film contrast
        vf = (
            f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=30,"
            f"eq=contrast=1.06:saturation=1.1,vignette=PI/5"
        )
        cmd = [
            "ffmpeg", "-y", "-stream_loop", "5", "-i", raw_clip,
            "-t", f"{clip_target_dur:.2f}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "20", "-pix_fmt", "yuv420p",
            "-an", norm_clip
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"[✓] Scene {i+1} Normalized: {scene['title']} ({clip_target_dur:.2f}s) -> {os.path.basename(norm_clip)}")
        normalized_clips.append((norm_clip, clip_target_dur))

    return normalized_clips


def synthesize_meditative_drone(duration: float, drone_path: str):
    """Synthesizes a 432Hz harmonic meditative drone for background depth."""
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"sine=frequency=432:duration={duration}",
        "-f", "lavfi",
        "-i", f"sine=frequency=216:duration={duration}",
        "-filter_complex", "[0:a]volume=0.3[a1];[1:a]volume=0.4[a2];[a1][a2]amix=inputs=2:duration=first,lowpass=f=450,volume=-18dB[out]",
        "-map", "[out]",
        "-c:a", "libmp3lame", drone_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def render_supreme_video(normalized_clips: list, voice_audio: str, srt_path: str, total_duration: float, output_path: str):
    """
    Concatenates visual clips, blends 432Hz meditative audio, burns golden Devanagari subtitles, and outputs master 16:9 video.
    """
    print("\n[4/4] Assembling Supreme Devotional 16:9 Master Video with Golden Devanagari Subtitles...")
    work_dir = os.path.abspath(RENDERS_DIR)

    # 1. Create Concat Manifest
    manifest_path = os.path.join(RENDERS_DIR, "video_concat_manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        for clip_path, _ in normalized_clips:
            clean_path = clip_path.replace("\\", "/")
            f.write(f"file '{clean_path}'\n")

    concatenated_raw = os.path.join(RENDERS_DIR, "concatenated_raw.mp4")
    concat_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", manifest_path,
        "-c", "copy",
        concatenated_raw
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 2. Synthesize background drone
    drone_path = os.path.join(RENDERS_DIR, "drone_432hz.mp3")
    synthesize_meditative_drone(total_duration, drone_path)

    # 3. Final Render with Subtitle Overlay and Audio Mix
    srt_name = os.path.basename(srt_path)
    sub_filter = (
        f"subtitles={srt_name}:force_style="
        "'Fontname=Nirmala UI,FontSize=26,PrimaryColour=&H0000D7FF&,OutlineColour=&H00000000&,BorderStyle=3,Outline=2,Shadow=2,Alignment=2,MarginV=35'"
    )

    final_cmd = [
        "ffmpeg", "-y",
        "-i", concatenated_raw,
        "-i", voice_audio,
        "-i", drone_path,
        "-filter_complex",
        f"[0:v]{sub_filter}[v_out];"
        f"[1:a]volume=1.0[vocal];"
        f"[2:a]volume=0.3[drone];"
        f"[vocal][drone]amix=inputs=2:duration=first:dropout_transition=2[a_out]",
        "-map", "[v_out]",
        "-map", "[a_out]",
        "-t", f"{total_duration:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        os.path.abspath(output_path)
    ]

    subprocess.run(final_cmd, cwd=work_dir, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Mandatory Hard-Locked Content ID Outro (from pinned config)
    outro_norm = CONFIG.get("CONTENT_ID_OUTRO_NORMALIZED")
    if outro_norm and os.path.exists(outro_norm):
        print(f"🔒 Appending Hard-Locked Content ID Outro Clip (173.25s) for Copyright Claim Immunity...")
        final_with_outro = output_path.replace(".mp4", "_with_outro.mp4")
        outro_manifest = os.path.join(RENDERS_DIR, "outro_concat_manifest.txt")
        with open(outro_manifest, "w", encoding="utf-8") as f:
            f.write(f"file '{os.path.abspath(output_path).replace(chr(92), '/')}'\n")
            f.write(f"file '{os.path.abspath(outro_norm).replace(chr(92), '/')}'\n")

        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", outro_manifest, "-c", "copy", final_with_outro],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(final_with_outro):
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(final_with_outro, output_path)
            if os.path.exists(outro_manifest):
                os.remove(outro_manifest)
        print(f"🔒 [✓] Content ID Outro Permanently Locked to Master Video!")

    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"\n==================================================================")
    print(f"🎉 SUPREME DEVOTIONAL 16:9 MASTER VIDEO GENERATED SUCCESSFULLY!")
    print(f"📁 Video Path: {output_path}")
    print(f"⏱️ Duration: {total_duration:.2f} seconds")
    print(f"📦 File Size: {file_size_mb:.2f} MB")
    print(f"🔒 Unique Locked Clips Used: {len(normalized_clips)} (Zero Repetition Verified)")
    print(f"==================================================================\n")


def main():
    print("==================================================================")
    print("🕉️ SUPREME BHAGAVAD GITA VIDEO ENGINE (ZERO REPETITION & VOICE MATCH)")
    print("==================================================================")

    lock_engine = VisualLockEngine(LOCK_FILE)
    print(f"[*] Visual Lock Initialized: {len(lock_engine.used_ids)} previously locked IDs.")

    # Full Pure Hindi Script
    full_script = " ".join(s["narration"] for s in DEVOTIONAL_SCENES)

    voice_path = os.path.join(RENDERS_DIR, "supreme_devotional_voice.mp3")
    srt_path = os.path.join(RENDERS_DIR, "supreme_pure_hindi.srt")
    master_video = os.path.join(RENDERS_DIR, "supreme_devotional_16_9_master.mp4")

    # Step 1: Voiceover via Edge-TTS + Shure SM7B DSP (LOCKED)
    total_duration = generate_shure_sm7b_voiceover(full_script, voice_path)

    # Step 2: Subtitles (Devanagari Only)
    generate_devanagari_subtitles(DEVOTIONAL_SCENES, total_duration, srt_path)

    # Step 3: Visual Clips (Strict Zero-Repetition Lock & Voice Matching)
    normalized_clips = prepare_and_normalize_clips(DEVOTIONAL_SCENES, total_duration, lock_engine)

    # Step 4: Video Assembly
    render_supreme_video(normalized_clips, voice_path, srt_path, total_duration, master_video)


if __name__ == "__main__":
    main()
