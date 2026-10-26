import asyncio
import os
import sys
import urllib.parse
import subprocess
import requests
import edge_tts

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

VOICE = "hi-IN-MadhurNeural"

async def generate_divine_speech(text: str, output_audio: str, output_srt: str):
    """Generates Hindi voice with Edge-TTS and divine audio DSP enhancement."""
    raw_mp3 = output_audio.replace(".mp3", "_raw.mp3")
    
    print("[1/4] Generating Edge-TTS Neural Voice & Subtitles...")
    communicate = edge_tts.Communicate(text, VOICE, pitch="-3Hz", rate="-5%")
    
    sub_maker = edge_tts.SubMaker()
    with open(raw_mp3, "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sub_maker.feed(chunk)
                
    srt_content = sub_maker.get_srt()
    with open(output_srt, "w", encoding="utf-8") as file:
        file.write(srt_content)
        
    print(f"[+] Raw Audio & Subtitles generated: {output_srt} (bytes: {len(srt_content)})")

    # FFmpeg DSP: Divine Bass Boost + Soft Ambient Reverb + Loudness Normalization
    print("[2/4] Applying Divine Audio FX (Bass Boost, Cathedral Reverb)...")
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", raw_mp3,
        "-af", "equalizer=f=120:t=q:w=1:g=5,aecho=0.8:0.85:50:0.35,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "libmp3lame", "-b:a", "192k",
        output_audio
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(raw_mp3):
        os.remove(raw_mp3)
    print(f"[+] Divine Audio Mastered: {output_audio}")

def download_visual(prompt: str, output_image: str):
    """Generates/fetches 16:9 cinematic artwork via Pollinations AI."""
    print("[3/4] Generating 16:9 AI Visual...")
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1280&height=720&nologo=true"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    
    resp = requests.get(url, headers=headers, timeout=60)
    if resp.status_code == 200 and len(resp.content) > 5000:
        with open(output_image, "wb") as f:
            f.write(resp.content)
        print(f"[+] 16:9 AI Visual Downloaded: {output_image}")
    else:
        raise RuntimeError(f"Failed to fetch image: Status {resp.status_code}")

def render_final_16x9_video(image_path: str, audio_path: str, srt_path: str, output_video: str):
    """Renders 16:9 YouTube video with Ken Burns zoom, 432Hz ambient drone, and glowing gold subtitles."""
    print("[4/4] Rendering Master 16:9 Video with Ken Burns motion & Gold Subtitles...")
    
    work_dir = os.path.abspath(os.path.dirname(output_video))
    img_rel = os.path.basename(image_path)
    audio_rel = os.path.basename(audio_path)
    srt_rel = os.path.basename(srt_path)
    output_rel = os.path.basename(output_video)

    # Subtitle Style: Rich Devanagari Gold (#FFD700), Elegant Black Outline, Centered Bottom
    sub_style = (
        "force_style='Fontname=Segoe UI,FontSize=20,"
        "PrimaryColour=&H0000D7FF,OutlineColour=&H00000000,BorderStyle=1,"
        "Outline=2,Shadow=1,Alignment=2,MarginV=35'"
    )

    # Complex FFmpeg pipeline:
    # 0: Image with smooth 16:9 Ken Burns zoompan
    # 1: Speech voiceover
    # 2 & 3: Synthetic 108Hz & 216Hz Meditative Binaural Drone
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", img_rel,
        "-i", audio_rel,
        "-f", "lavfi", "-i", "sine=frequency=108",
        "-f", "lavfi", "-i", "sine=frequency=216",
        "-filter_complex",
        f"[0:v]zoompan=z='min(zoom+0.0005,1.15)':d=125:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1280x720:fps=30,"
        f"subtitles='{srt_rel}':{sub_style}[v];"
        "[2:a][3:a]amix=inputs=2,volume=0.03[drone];"
        "[1:a]volume=1.0[voice];"
        "[voice][drone]amix=inputs=2:duration=first:dropout_transition=2[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_rel
    ]
    
    subprocess.run(ffmpeg_cmd, check=True, cwd=work_dir)
    print(f"\n[SUCCESS] 16:9 Video Ready: {output_video}")

async def produce_shloka_video(shloka_data: dict, output_dir: str):
    """End-to-end production pipeline for a single shloka."""
    os.makedirs(output_dir, exist_ok=True)
    shloka_id = shloka_data["id"]
    
    # Combined narrator script: Hook + Sanskrit Shloka + Vyakhya
    full_script = f"{shloka_data['hook']}\n\n{shloka_data['sanskrit']}\n\n{shloka_data['vyakhya']}"
    
    audio_path = os.path.join(output_dir, f"{shloka_id}_audio.mp3")
    srt_path = os.path.join(output_dir, f"{shloka_id}_sub.srt")
    img_path = os.path.join(output_dir, f"{shloka_id}_visual.jpg")
    final_video = os.path.join(output_dir, f"{shloka_id}_master_16x9.mp4")

    # 1. Voice & Subtitles
    if not os.path.exists(audio_path) or not os.path.exists(srt_path) or os.path.getsize(srt_path) == 0:
        await generate_divine_speech(full_script, audio_path, srt_path)
    else:
        print("[+] Audio & Subtitles already cached.")
    
    # 2. AI Visual
    if not os.path.exists(img_path) or os.path.getsize(img_path) == 0:
        download_visual(shloka_data["visual_prompt"], img_path)
    else:
        print("[+] Visual already cached.")
    
    # 3. Master Video Render
    render_final_16x9_video(img_path, audio_path, srt_path, final_video)
    
    return final_video
