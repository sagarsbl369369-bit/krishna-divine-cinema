import os
import sys
import asyncio
import subprocess
import edge_tts

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(BASE_DIR, "music_vault", "ch_01_gita_meditative")

async def synthesize_edge_tts(text: str, output_raw_mp3: str, voice: str = "hi-IN-MadhurNeural"):
    """Synthesizes Devanagari text into voice with edge-tts."""
    print(f"[*] Synthesizing voice with Edge-TTS ({voice}, rate=-5%, pitch=-6Hz)...")
    comm = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate="-5%",
        pitch="-6Hz"
    )
    await comm.save(output_raw_mp3)
    print(f"✓ Voice synthesized: {output_raw_mp3} ({os.path.getsize(output_raw_mp3)/1024:.1f} KB)")

def apply_shure_sm7b_dsp(raw_voice_mp3: str, mastered_mp3: str, bg_music_path: str = None):
    """
    Applies broadcast-grade audio DSP:
    1. Highpass at 75 Hz (removes rumble)
    2. Warmth boost at 220 Hz (+2.5 dB)
    3. Clarity boost at 3200 Hz (+2 dB)
    4. Compression (3:1 ratio)
    5. Amix background music at -22 dB
    """
    print("[*] Applying Shure SM7B Studio DSP & 432 Hz background mixdown...")

    # Find background music track
    if not bg_music_path or not os.path.exists(bg_music_path):
        if os.path.exists(MUSIC_DIR):
            tracks = [os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR) if f.endswith(".mp3")]
            if tracks:
                bg_music_path = tracks[0]

    # Audio filter chain for vocal
    vocal_filter = "highpass=f=75,equalizer=f=220:t=q:w=1:g=2.5,equalizer=f=3200:t=q:w=1:g=2.0,acompressor=threshold=-18dB:ratio=3:attack=5:release=50"

    if bg_music_path and os.path.exists(bg_music_path):
        # Mix voice and looped background music (ducked at -22dB)
        # Stream 0: voice (apply filter, volume=1.0)
        # Stream 1: music (loop, volume=0.08)
        filter_complex = f"[0:a]{vocal_filter},volume=1.1[v];[1:a]aloop=loop=-1:size=2e+09,volume=0.07[bg];[v][bg]amix=inputs=2:duration=first:dropout_transition=2[out]"
        cmd = [
            "ffmpeg", "-y",
            "-i", raw_voice_mp3,
            "-i", bg_music_path,
            "-filter_complex", filter_complex,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            mastered_mp3
        ]
    else:
        # Vocal only with filter
        cmd = [
            "ffmpeg", "-y",
            "-i", raw_voice_mp3,
            "-af", vocal_filter,
            "-c:a", "libmp3lame",
            "-b:a", "192k",
            mastered_mp3
        ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    print(f"✓ Mastered audio created: {mastered_mp3} ({os.path.getsize(mastered_mp3)/1024:.1f} KB)")

def generate_hypnotic_voiceover(text: str, output_path: str, voice: str = "hi-IN-MadhurNeural") -> str:
    """Full pipeline: TTS + Shure SM7B DSP + 432 Hz music bed."""
    temp_raw = output_path.replace(".mp3", "_raw.mp3")
    asyncio.run(synthesize_edge_tts(text, temp_raw, voice=voice))
    apply_shure_sm7b_dsp(temp_raw, output_path)
    if os.path.exists(temp_raw):
        try:
            os.remove(temp_raw)
        except Exception:
            pass
    return output_path

if __name__ == "__main__":
    sample_text = "सुनो... क्या तुम्हें कभी ऐसा लगा है कि इस भरी दुनिया में... अपने ही घर में तुम बिल्कुल अकेले हो..."
    out_f = os.path.join(BASE_DIR, "test_hypnotic_audio.mp3")
    generate_hypnotic_voiceover(sample_text, out_f)
