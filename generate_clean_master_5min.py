import os
import sys
import asyncio
import subprocess
import shutil
import edge_tts
from pydub import AudioSegment
from script_sentences_clean import SCRIPT_SECTIONS

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
SEGS_DIR = os.path.join(RENDERS_DIR, "clean_segments")
os.makedirs(SEGS_DIR, exist_ok=True)

raw_stitched = os.path.join(RENDERS_DIR, "demo_clean_stitched_raw.mp3")
dsp_audio = os.path.join(RENDERS_DIR, "demo_clean_dsp.mp3")
bgm_audio = os.path.join(BASE_DIR, "music_vault", "ch_01_gita_meditative", "output001.mp3")
final_master = os.path.join(RENDERS_DIR, "demo_clean_5min_master.mp3")

print("==================================================================")
print("🎙️ GENERATING 100X BETTER CLEAN SENTENCE-STITCHED 5-MIN AUDIO")
print("==================================================================")
print(f"Total Sentences: {len(SCRIPT_SECTIONS)}")

async def synthesize_all_segments():
    combined = AudioSegment.empty()
    for i, (text, pause_ms) in enumerate(SCRIPT_SECTIONS):
        seg_file = os.path.join(SEGS_DIR, f"seg_{i:03d}.mp3")
        # Synthesize completely clean text with zero tags
        comm = edge_tts.Communicate(text, "hi-IN-MadhurNeural", rate="-7%", pitch="-4Hz")
        await comm.save(seg_file)
        
        # Load audio and append true silence gap
        seg_audio = AudioSegment.from_file(seg_file)
        combined += seg_audio + AudioSegment.silent(duration=pause_ms)
        if (i + 1) % 5 == 0 or i == len(SCRIPT_SECTIONS) - 1:
            print(f"  [✓] Synthesized {i+1}/{len(SCRIPT_SECTIONS)} sentences ({len(combined)/1000:.1f}s)...")
            sys.stdout.flush()

    combined.export(raw_stitched, format="mp3", bitrate="320k")
    print(f"Combined Raw Voice Complete: {len(combined)/1000:.2f} seconds ({len(combined)/60000:.2f} mins)")
    return len(combined) / 1000.0

dur = asyncio.run(synthesize_all_segments())

# 2. Shure SM7B Broadcast DSP Chain
print("[2/4] Applying Shure SM7B Studio Broadcast DSP Chain...")
SHURE_SM7B_CHAIN = (
    "aresample=48000,"
    "aformat=channel_layouts=stereo,"
    "highpass=f=70,"
    "equalizer=f=160:t=q:w=1.2:g=5.0,"
    "equalizer=f=420:t=q:w=1.5:g=-3.0,"
    "equalizer=f=2800:t=q:w=1.0:g=3.2,"
    "equalizer=f=6500:t=q:w=2.0:g=-3.5,"
    "lowpass=f=14500,"
    "compand=attacks=0.012:decays=0.15:points=-80/-80|-45/-28|-24/-14|-12/-8|0/-5:gain=4.2,"
    "loudnorm=I=-14:TP=-1.0:LRA=9"
)

subprocess.run([
    "ffmpeg", "-y", "-i", raw_stitched,
    "-af", SHURE_SM7B_CHAIN,
    "-c:a", "libmp3lame", "-b:a", "320k",
    dsp_audio
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("DSP Mastering Completed!")

# 3. Mix with BGM (Sidechain Ducking)
print("[3/4] Mixing with Meditative Flute & Drone Soundscape...")
mix_cmd = [
    "ffmpeg", "-y",
    "-i", dsp_audio,
    "-stream_loop", "-1", "-i", bgm_audio,
    "-filter_complex",
    "[0:a]volume=1.55[vocal];"
    "[1:a]volume=0.11,lowpass=f=2200[bgm];"
    "[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=false[mixed];"
    "[mixed]alimiter=limit=0.96:attack=5:release=50[out]",
    "-map", "[out]",
    "-t", f"{dur:.2f}",
    "-c:a", "libmp3lame", "-b:a", "320k",
    final_master
]
subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Master Audio Mixed Successfully!")

# 4. Deploy to Desktop
print("[4/4] Deploying to Desktop...")
desktops = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]

for d in desktops:
    if os.path.exists(d):
        target_mp3 = os.path.join(d, '5MIN_HYPERREALISTIC_VOICE_DEMO.mp3')
        shutil.copy2(final_master, target_mp3)
        bat_file = os.path.join(d, 'PLAY_5MIN_VOICE_DEMO.bat')
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('echo ====================================================\n')
            f.write('echo    PLAYING 100X BETTER CLEAN 5-MIN MASTER AUDIO\n')
            f.write('echo ====================================================\n')
            f.write(f'start "" "{target_mp3}"\n')

print("DEMO DEPLOYED TO DESKTOP SUCCESSFULLY!")
