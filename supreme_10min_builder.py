import asyncio
import os
import sys
import json
import subprocess
import edge_tts

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

VOICE = "hi-IN-MadhurNeural"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
ASSETS_DIR = os.path.join(RENDERS_DIR, "assets")

os.makedirs(RENDERS_DIR, exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)

async def generate_chapter_audio(text: str, audio_path: str, srt_path: str):
    """Generates divine speech with word-accurate subtitles and audio FX."""
    raw_mp3 = audio_path.replace(".mp3", "_raw.mp3")
    communicate = edge_tts.Communicate(text, VOICE, pitch="-3Hz", rate="-5%")
    
    sub_maker = edge_tts.SubMaker()
    with open(raw_mp3, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                sub_maker.feed(chunk)
                
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(sub_maker.get_srt())
        
    # FFmpeg Audio FX: Cathedral Reverb + 120Hz Bass Boost + Loudnorm
    ffmpeg_cmd = [
        "ffmpeg", "-y", "-i", raw_mp3,
        "-af", "equalizer=f=120:t=q:w=1:g=5,aecho=0.8:0.85:50:0.35,loudnorm=I=-16:TP=-1.5:LRA=11",
        "-c:a", "libmp3lame", "-b:a", "192k",
        audio_path
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(raw_mp3):
        os.remove(raw_mp3)

def get_audio_duration(audio_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(result.stdout.strip())

def render_chapter_video(chapter_num: int, images: list, audio_path: str, srt_path: str, output_video: str):
    """Renders a chapter video cycling through 3 images with continuous motion and gold subtitles."""
    duration = get_audio_duration(audio_path)
    num_imgs = len(images)
    dur_per_img = duration / num_imgs
    frames_per_img = int(dur_per_img * 30)

    work_dir = os.path.abspath(RENDERS_DIR)
    audio_rel = os.path.relpath(audio_path, work_dir)
    srt_rel = os.path.relpath(srt_path, work_dir)
    output_rel = os.path.relpath(output_video, work_dir)

    input_args = []
    filter_chains = []

    for idx, img in enumerate(images):
        img_rel = os.path.relpath(img, work_dir)
        input_args.extend(["-i", img_rel])
        # Alternating zoom-in and zoom-out with exact setsar=1 to ensure identical SAR
        if idx % 2 == 0:
            zoom_expr = "min(zoom+0.0004,1.15)"
        else:
            zoom_expr = "max(1.15-0.0004*on,1.0)"
            
        filter_chains.append(
            f"[{idx}:v]zoompan=z='{zoom_expr}':d={frames_per_img}:s=1280x720:fps=30,setsar=1[v{idx}]"
        )

    # Concat video streams
    concat_inputs = "".join(f"[v{i}]" for i in range(num_imgs))
    concat_filter = f"{concat_inputs}concat=n={num_imgs}:v=1:a=0[v_base]"
    
    # Subtitle Style: Devanagari Gold (#FFD700) with elegant black outline
    sub_style = (
        "force_style='Fontname=Segoe UI,FontSize=20,"
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

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        *input_args,
        "-filter_complex", full_filter,
        "-map", "[v_final]", "-map", "[a_final]",
        "-c:v", "libx264", "-preset", "faster", "-crf", "22", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_rel
    ]

    subprocess.run(ffmpeg_cmd, check=True, cwd=work_dir)

def concatenate_master(chapter_videos: list, master_output: str):
    """Concatenates all rendered chapters into the final 10-minute master video in seconds."""
    list_file = os.path.join(RENDERS_DIR, "chapters_list.txt")
    with open(list_file, "w", encoding="utf-8") as f:
        for vid in chapter_videos:
            f.write(f"file '{os.path.basename(vid)}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", os.path.basename(list_file),
        "-c", "copy",
        os.path.basename(master_output)
    ]
    subprocess.run(cmd, check=True, cwd=RENDERS_DIR)
    print(f"\n[DONE] 10-Minute Master Video Ready: {master_output}")

async def build_10min_masterpiece():
    script_file = os.path.join(BASE_DIR, "supreme_10min_script.json")
    with open(script_file, "r", encoding="utf-8") as f:
        chapters = json.load(f)

    # Gather available downloaded scenes
    assets = [os.path.join(ASSETS_DIR, f) for f in sorted(os.listdir(ASSETS_DIR)) if f.endswith(('.jpg', '.png'))]
    if len(assets) < 3:
        assets = [os.path.join(RENDERS_DIR, "gita_02_47_visual.jpg")] * 15

    chapter_videos = []
    print("=" * 60)
    print("🕉️  STARTING SUPREME 10-MINUTE BHAGAVAD GITA MASTER PRODUCTION")
    print("=" * 60)

    for i, ch in enumerate(chapters):
        ch_num = ch["chapter_num"]
        print(f"\n[>>] Processing Chapter {ch_num}/5: {ch['chapter_title']}...")
        
        audio_path = os.path.join(RENDERS_DIR, f"ch_{ch_num}_audio.mp3")
        srt_path = os.path.join(RENDERS_DIR, f"ch_{ch_num}_sub.srt")
        video_path = os.path.join(RENDERS_DIR, f"ch_{ch_num}_video.mp4")

        # 1. Voice & Subtitles
        if not os.path.exists(audio_path) or not os.path.exists(srt_path):
            print(f"  [1/2] Generating Divine Voice & Subtitles...")
            await generate_chapter_audio(ch["text"], audio_path, srt_path)
        else:
            print(f"  [1/2] Voice & Subtitles cached.")

        # 2. Select 3 distinct images for this chapter
        start_idx = (i * 3) % len(assets)
        ch_images = [assets[(start_idx + k) % len(assets)] for k in range(3)]
        
        # 3. Render Chapter Video
        print(f"  [2/2] Rendering Chapter {ch_num} Video (Multi-Scene Motion)...")
        render_chapter_video(ch_num, ch_images, audio_path, srt_path, video_path)
        chapter_videos.append(video_path)
        print(f"  [+] Chapter {ch_num} Rendered Successfully!")

    # 4. Concatenate into Master 10-Minute Video
    print("\n[>>] Concatenating 5 Chapters into 10-Minute Master Video...")
    master_path = os.path.join(RENDERS_DIR, "bhagavad_gita_10_minute_supreme_master.mp4")
    concatenate_master(chapter_videos, master_path)

if __name__ == "__main__":
    asyncio.run(build_10min_masterpiece())
