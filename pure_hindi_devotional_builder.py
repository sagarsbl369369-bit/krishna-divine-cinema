"""
Pure Hindi Devotional Video Builder
- 100% Pure Hindi Devanagari Script & Subtitles
- Strictly Devotional & Voice-Accurate Visuals (Lord Krishna, Arjuna Chariot, Kurukshetra)
- Google AI Studio Gemini 3.8 Flash TTS Voiceover
- 432Hz Meditative Binaural Drone
"""

import asyncio
import os
import sys
import re
import subprocess
from google import genai
from google.genai import types

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(RENDERS_DIR, exist_ok=True)

# User's provided Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

def format_timestamp(seconds: float) -> str:
    millis = int((seconds % 1) * 1000)
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def generate_hindi_devanagari_subtitles(script_segments: list, total_duration: float, srt_path: str):
    """Generates 100% pure Devanagari Hindi subtitles proportionally mapped to audio."""
    total_chars = sum(len(seg) for seg in script_segments)
    current_time = 0.5  # delay before voice
    available_duration = max(total_duration - 1.2, 1.0)

    entries = []
    for i, seg in enumerate(script_segments, start=1):
        seg_duration = (len(seg) / total_chars) * available_duration
        end_time = min(current_time + seg_duration, total_duration)

        start_str = format_timestamp(current_time)
        end_str = format_timestamp(end_time)
        entries.append(f"{i}\n{start_str} --> {end_str}\n{seg.strip()}\n")
        current_time = end_time

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))
    print(f"[✓] Pure Hindi Subtitles generated: {srt_path}")

async def generate_gemini_voice(full_text: str, audio_path: str) -> float:
    """Generates divine speech with Google AI Studio Gemini 3.8 Flash TTS."""
    print("[🎙️] Calling Google AI Studio (gemini-3.8-flash-tts)...")
    client = genai.Client(api_key=GEMINI_API_KEY)

    prompt = (
        "You are an ancient divine orator reciting the sacred words of Shrimad Bhagavad Gita. "
        "Speak in pure, crystal-clear Hindi with deep spiritual gravitas, warmth, and natural Vedic pauses. "
        "Pronounce holy Sanskrit shlokas with deep reverence and resonance.\n\n"
        f"{full_text}"
    )

    resp = client.models.generate_content(
        model="gemini-3.8-flash-tts",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
                )
            )
        )
    )

    audio_bytes = None
    for part in resp.candidates[0].content.parts:
        if part.inline_data and part.inline_data.data:
            audio_bytes = part.inline_data.data
            break

    if not audio_bytes:
        raise RuntimeError("No audio returned by Gemini TTS!")

    raw_wav = audio_path.replace(".mp3", "_raw.wav")
    with open(raw_wav, "wb") as f:
        f.write(audio_bytes)

    # Master audio with Cathedral Reverb + 120Hz Bass Boost + Loudnorm
    cmd = [
        "ffmpeg", "-y", "-i", raw_wav,
        "-af", "equalizer=f=120:t=q:w=1:g=5,aecho=0.8:0.85:50:0.35,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "libmp3lame", "-b:a", "192k",
        audio_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(raw_wav):
        os.remove(raw_wav)

    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    dur = float(subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout.strip())
    print(f"[✓] Google Gemini Audio Mastered: {audio_path} (Duration: {dur:.2f}s)")
    return dur

def render_devotional_master_video(devotional_images: list, audio_path: str, srt_path: str, total_duration: float, output_video: str):
    """Renders 100% devotional video with Ken Burns motion, glowing Devanagari gold subtitles & meditative drone."""
    print("\n[3/3] Rendering Devotional 16:9 Master Video...")
    work_dir = os.path.abspath(RENDERS_DIR)
    audio_rel = os.path.relpath(audio_path, work_dir)
    srt_rel = os.path.relpath(srt_path, work_dir)
    output_rel = os.path.relpath(output_video, work_dir)

    num_imgs = len(devotional_images)
    dur_per_img = total_duration / num_imgs
    frames_per_img = int(dur_per_img * 30)

    input_args = []
    filter_chains = []

    for idx, img in enumerate(devotional_images):
        img_rel = os.path.relpath(img, work_dir)
        input_args.extend(["-i", img_rel])
        # Alternating zoom-in and zoom-out for devotional dynamism
        if idx % 2 == 0:
            zoom_expr = "min(zoom+0.0004,1.15)"
        else:
            zoom_expr = "max(1.15-0.0004*on,1.0)"
        filter_chains.append(
            f"[{idx}:v]zoompan=z='{zoom_expr}':d={frames_per_img}:s=1280x720:fps=30,setsar=1[v{idx}]"
        )

    concat_inputs = "".join(f"[v{i}]" for i in range(num_imgs))
    concat_filter = f"{concat_inputs}concat=n={num_imgs}:v=1:a=0[v_base]"

    # Subtitle Style: Devanagari Gold (#FFD700), Bold Black Outline, Centered Bottom
    sub_style = (
        "force_style='Fontname=Nirmala UI,FontSize=22,"
        "PrimaryColour=&H0000D7FF,OutlineColour=&H00000000,BorderStyle=1,"
        "Outline=2,Shadow=1,Alignment=2,MarginV=35'"
    )
    sub_filter = f"[v_base]subtitles='{srt_rel}':{sub_style}[v_final]"

    # Meditative 108Hz + 216Hz Binaural Drone
    audio_idx = num_imgs
    drone1_idx = num_imgs + 1
    drone2_idx = num_imgs + 2

    input_args.extend([
        "-i", audio_rel,
        "-f", "lavfi", "-i", "sine=frequency=108",
        "-f", "lavfi", "-i", "sine=frequency=216"
    ])

    audio_filter = (
        f"[{drone1_idx}:a][{drone2_idx}:a]amix=inputs=2,volume=0.035[drone];"
        f"[{audio_idx}:a]volume=1.0[voice];"
        f"[voice][drone]amix=inputs=2:duration=first:dropout_transition=2[a_final]"
    )

    full_filter = f"{';'.join(filter_chains)};{concat_filter};{sub_filter};{audio_filter}"

    cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", full_filter,
        "-map", "[v_final]", "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "faster", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_rel
    ]

    subprocess.run(cmd, check=True, cwd=work_dir)
    print(f"\n[✨ SUCCESS] Pure Hindi Devotional Master Video Ready: {output_video}")

async def main():
    # 1. 100% Pure Hindi Script Segments
    script_segments = [
        "जब आप दिन-रात निष्ठा से कर्म करते हैं",
        "और बदले में केवल असफलता और निराशा मिलती है...",
        "तब मन में एक ही प्रश्न उठता है: क्या मेरा प्रयास व्यर्थ था?",
        "इस संशय को मिटाने के लिए भगवान श्री कृष्ण ने",
        "कुरुक्षेत्र के मैदान में अर्जुन को क्या दिव्य उपदेश दिया था? ध्यान से सुनिए।",
        "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।",
        "मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
        "भगवान श्री कृष्ण कहते हैं: हे अर्जुन! तुम्हारा अधिकार केवल कर्म करने पर है,",
        "उसके फलों पर कभी नहीं।",
        "इसलिए कर्म के फल की इच्छा मत करो,",
        "और कर्म न करने में भी तुम्हारी आसक्ति न हो।",
        "जब तुम परिणाम की चिंता छोड़कर केवल अपने कर्तव्य पर ध्यान केंद्रित करते हो,",
        "तभी तुम्हें सच्ची शांति, असीम शक्ति और अनंत विजय प्राप्त होती है।"
    ]

    full_text = " ".join(script_segments)

    audio_path = os.path.join(RENDERS_DIR, "pure_hindi_gemini_audio.mp3")
    srt_path = os.path.join(RENDERS_DIR, "pure_hindi_devanagari_sub.srt")
    final_video = os.path.join(RENDERS_DIR, "pure_hindi_devotional_master.mp4")

    # 4 Strictly Devotional Visuals
    devotional_scenes = [
        os.path.join(RENDERS_DIR, "devotional_scene_1.jpg"),  # Arjuna in prayer & struggle
        os.path.join(RENDERS_DIR, "devotional_scene_2.jpg"),  # Lord Krishna on chariot holding reins
        os.path.join(RENDERS_DIR, "devotional_scene_3.jpg"),  # Lord Krishna giving Gita Updesh
        os.path.join(RENDERS_DIR, "devotional_scene_4.jpg")   # Lord Krishna cosmic divine form
    ]

    print("=" * 60)
    print("🕉️  PURE HINDI DEVOTIONAL VIDEO (GOOGLE AI STUDIO GEMINI TTS)")
    print("=" * 60)

    # 1. Generate Voice with Google AI Studio
    print("\n[1/3] Generating Pure Hindi Voiceover with Google AI Studio...")
    duration = await generate_gemini_voice(full_text, audio_path)

    # 2. Generate Pure Hindi Devanagari Subtitles
    print("\n[2/3] Generating Pure Devanagari Hindi Subtitles...")
    generate_hindi_devanagari_subtitles(script_segments, duration, srt_path)

    # 3. Render Final Video
    render_devotional_master_video(devotional_scenes, audio_path, srt_path, duration, final_video)

if __name__ == "__main__":
    asyncio.run(main())
