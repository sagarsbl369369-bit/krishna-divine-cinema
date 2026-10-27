import os
import sys
import re
import asyncio
import subprocess
import shutil
import edge_tts
import edge_tts.communicate

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(RENDERS_DIR, exist_ok=True)

# 1. Unescape SSML break tags so the neural engine adds natural dramatic pauses
orig_escape = edge_tts.communicate.escape
def smart_escape(text):
    res = orig_escape(text)
    res = re.sub(r'&lt;break\s+time=&quot;(\d+m?s)&quot;\s*/&gt;', r'<break time="\1" />', res)
    return res

edge_tts.communicate.escape = smart_escape

from script_5min_raw import CHAPTER_1, CHAPTER_2, CHAPTER_3, CHAPTER_4, CHAPTER_5

FULL_5MIN_SCRIPT = f"{CHAPTER_1} {CHAPTER_2} {CHAPTER_3} {CHAPTER_4} {CHAPTER_5}"

# Clean word count (excluding XML tags)
clean_text = re.sub(r'<[^>]+>', '', FULL_5MIN_SCRIPT)
words = clean_text.split()
print("==================================================================")
print("🎙️ GENERATING 10X HYPER-REALISTIC 5-MINUTE PSYCHOLOGY MASTER VOICE")
print("==================================================================")
print(f"Spoken Hindi Words: {len(words)}")

raw_audio = os.path.join(RENDERS_DIR, "demo_5min_raw.mp3")
dsp_audio = os.path.join(RENDERS_DIR, "demo_5min_dsp.mp3")
bgm_audio = os.path.join(BASE_DIR, "music_vault", "ch_01_gita_meditative", "output001.mp3")
final_master = os.path.join(RENDERS_DIR, "demo_5min_hyperrealistic_master.mp3")

# Step 1: Synthesize with deep, measured pacing (-7% rate, -4Hz pitch for gravitas)
print("[1/4] Synthesizing Neural Voice with Cinematic SSML Pauses...")
async def synthesize():
    comm = edge_tts.Communicate(
        FULL_5MIN_SCRIPT,
        "hi-IN-MadhurNeural",
        rate="-7%",
        pitch="-4Hz"
    )
    await comm.save(raw_audio)

asyncio.run(synthesize())
print("Raw Neural Audio Synthesized!")

# Step 2: Measure raw duration
probe = subprocess.run([
    "ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "default=noprint_wrappers=1:nokey=1", raw_audio
], capture_output=True, text=True, check=True)
raw_dur = float(probe.stdout.strip())
print(f"Raw Voice Duration: {raw_dur:.2f} seconds ({raw_dur/60:.2f} mins)")

# Step 3: Upgraded 10X Shure SM7B Broadcast + Studio Ambience DSP Chain
print("[2/4] Applying 10X Broadcast DSP Mastering (Chest Resonance + De-Essing + Studio Warmth)...")
SHURE_SM7B_10X_CHAIN = (
    "aresample=48000,"
    "aformat=channel_layouts=stereo,"
    "highpass=f=70,"
    "equalizer=f=160:t=q:w=1.2:g=5.0,"   # Deep chest warmth / proximity effect
    "equalizer=f=420:t=q:w=1.5:g=-3.0,"  # Clean boxy nasal mud
    "equalizer=f=2800:t=q:w=1.0:g=3.2,"  # Clear vocal intimacy & presence
    "equalizer=f=6500:t=q:w=2.0:g=-3.5,"  # De-essing (softens harsh 'sa/sha' sibilants)
    "lowpass=f=14500,"                    # Silky vintage acoustic cutoff
    "compand=attacks=0.012:decays=0.15:points=-80/-80|-45/-28|-24/-14|-12/-8|0/-5:gain=4.2," # Studio dynamic leveling
    "loudnorm=I=-14:TP=-1.0:LRA=9"       # YouTube Broadcast standard loudness
)

subprocess.run([
    "ffmpeg", "-y", "-i", raw_audio,
    "-af", SHURE_SM7B_10X_CHAIN,
    "-c:a", "libmp3lame", "-b:a", "320k",
    dsp_audio
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("DSP Mastering Completed!")

# Step 4: Mix with Devotional Drone & Soulful Flute BGM (Sidechain Ducking)
print("[3/4] Mixing with Ethereal Meditative Soundscape (Binaural Drone + Bansuri)...")
mix_cmd = [
    "ffmpeg", "-y",
    "-i", dsp_audio,
    "-stream_loop", "-1", "-i", bgm_audio,
    "-filter_complex",
    "[0:a]volume=1.55[vocal];"                                # Voice is supreme, commanding and clear
    "[1:a]volume=0.11,lowpass=f=2200[bgm];"                   # BGM is velvety, warm, resting behind voice
    "[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=false[mixed];"
    "[mixed]alimiter=limit=0.96:attack=5:release=50[out]",
    "-map", "[out]",
    "-t", f"{raw_dur:.2f}",
    "-c:a", "libmp3lame", "-b:a", "320k",
    final_master
]
subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print(f"Master Soundscape Rendered! Total Time: {raw_dur:.2f}s ({raw_dur/60:.2f} mins)")

# Step 5: Deploy to Desktop
print("[4/4] Deploying to Desktop...")
dest_dirs = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]

for d in dest_dirs:
    if os.path.exists(d):
        target_mp3 = os.path.join(d, '🎵 5-MIN_HYPERREALISTIC_VOICE_DEMO.mp3')
        shutil.copy2(final_master, target_mp3)
        bat_path = os.path.join(d, 'PLAY_5MIN_VOICE_DEMO.bat')
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('echo ====================================================\n')
            f.write('echo    PLAYING 10X HYPERREALISTIC 5-MIN VOICE DEMO\n')
            f.write('echo ====================================================\n')
            f.write(f'start "" "{target_mp3}"\n')

print("DEMO DEPLOYED TO DESKTOP SUCCESSFULLY!")
