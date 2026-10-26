"""
Shure SM7B DSP + Edge-TTS Studio Audio Production Engine
---------------------------------------------------------
Hardware Emulation & Digital Signal Processing (DSP) Chain:
1. 48,000 Hz Studio Broadcast Resampling (aresample=48000)
2. 75Hz Low-Cut Filter (Highpass) - Eliminates sub-bass rumble & plosive wind
3. 180Hz Proximity Effect Warm Chest Resonance (+3.5 dB, Q=1.2) - Classic Shure SM7B radio intimacy
4. 450Hz Mud & Boxiness De-clutter (-1.8 dB, Q=1.5) - Transparent speech clarity
5. 3.2kHz Presence Boost (+2.5 dB, Q=1.1) - Enhances vocal articulation & spiritual presence
6. 6.8kHz Studio De-Esser (-3.0 dB, Q=2.0) - Tames harsh sibilance ('स', 'श', 'ष', 'च')
7. 13.5kHz Dynamic Capsule Roll-Off (Lowpass) - Eliminates digital hiss and synthetic high-end
8. Studio Optical Compression & Leveling (compand) - LA-2A / dbx 286s vocal upfront thickness
9. EBU R128 Broadcast Loudness Normalization (-14 LUFS, True Peak -1.0 dB, LRA 9)
"""

import os
import sys
import json
import re
import subprocess
import asyncio
import edge_tts

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

CONFIG = load_config()
VOICE_NAME = CONFIG.get("EDGE_TTS_VOICE", "hi-IN-MadhurNeural")
VOICE_RATE = CONFIG.get("EDGE_TTS_RATE", "+0%")
VOICE_PITCH = CONFIG.get("EDGE_TTS_PITCH", "-2Hz")

SHURE_SM7B_DSP_CHAIN = CONFIG.get(
    "SHURE_SM7B_DSP_CHAIN",
    (
        "aresample=48000,"
        "highpass=f=75,"
        "equalizer=f=180:t=q:w=1.2:g=3.5,"
        "equalizer=f=450:t=q:w=1.5:g=-1.8,"
        "equalizer=f=3200:t=q:w=1.1:g=2.5,"
        "equalizer=f=6800:t=q:w=2.0:g=-3.0,"
        "lowpass=f=13500,"
        "compand=attacks=0.015:decays=0.12:points=-80/-80|-45/-32|-24/-17|-12/-10|0/-7:gain=2.5,"
        "loudnorm=I=-14:TP=-1.0:LRA=9"
    )
)

def format_timestamp(seconds: float) -> str:
    millis = int((seconds % 1) * 1000)
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    return f"{hours:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def generate_proportional_subtitles(text: str, total_duration: float, srt_path: str):
    """Splits plain Hindi text into synchronized 3-6 word fast subtitle cards."""
    raw_lines = [l.strip() for l in re.split(r'[\n।!?]+', text) if l.strip()]
    if not raw_lines:
        raw_lines = [text.strip()]

    chunks = []
    for line in raw_lines:
        words = line.split()
        for i in range(0, len(words), 5):
            chunk = " ".join(words[i:i+5])
            if chunk:
                chunks.append(chunk)

    total_chars = sum(len(c) for c in chunks)
    current_time = 0.5
    available_duration = max(total_duration - 1.0, 1.0)

    entries = []
    for i, c in enumerate(chunks, start=1):
        dur = (len(c) / total_chars) * available_duration
        end_time = min(current_time + dur, total_duration)
        start_str = format_timestamp(current_time)
        end_str = format_timestamp(end_time)
        entries.append(f"{i}\n{start_str} --> {end_str}\n{c}\n")
        current_time = end_time

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(entries))

def synthesize_shure_sm7b_audio(plain_hindi_text: str, output_path: str) -> float:
    """
    100% Locked Edge-TTS + Shure SM7B DSP pipeline.
    Zero quotas, 100% reliable 24x7 production across sync, async & multi-process.
    """
    raw_mp3 = output_path.replace(".mp3", "_raw.mp3")

    tts_ok = False
    try:
        import asyncio, edge_tts
        async def _synth_direct():
            comm = edge_tts.Communicate(plain_hindi_text.strip(), VOICE_NAME, rate=VOICE_RATE, pitch=VOICE_PITCH)
            await comm.save(raw_mp3)
        asyncio.run(_synth_direct())
        if os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 1000:
            tts_ok = True
    except Exception as e_direct:
        pass

    if not tts_ok:
        cmd_tts = [
            sys.executable, "-m", "edge_tts",
            "--voice", VOICE_NAME,
            "--rate", VOICE_RATE,
            "--pitch", VOICE_PITCH,
            "--text", plain_hindi_text.strip(),
            "--write-media", raw_mp3
        ]
        subprocess.run(cmd_tts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Master with Studio Shure SM7B DSP Hardware Chain
    cmd = [
        "ffmpeg", "-y", "-i", raw_mp3,
        "-af", SHURE_SM7B_DSP_CHAIN,
        "-c:a", "libmp3lame", "-b:a", "192k",
        output_path
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(raw_mp3):
        os.remove(raw_mp3)

    probe = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", output_path
    ], capture_output=True, text=True, check=True)
    return float(probe.stdout.strip())

if __name__ == "__main__":
    test_text = "सीदन्ति मम गात्राणि मुखं च परिशुष्यति। कुरुक्षेत्र के विशाल रणक्षेत्र में अर्जुन का मन मोह और विषाद से घिर गया।"
    out_audio = os.path.join(BASE_DIR, "renders", "test_dsp_standalone.mp3")
    out_srt = os.path.join(BASE_DIR, "renders", "test_dsp_standalone.srt")
    dur = synthesize_shure_sm7b_audio(test_text, out_audio)
    generate_proportional_subtitles(test_text, dur, out_srt)
    print(f"Mastered Shure SM7B DSP Audio: {out_audio} ({dur:.2f}s)")
