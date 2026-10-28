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
OUTRO_DIR = os.path.join(BASE_DIR, "assets", "outro")
os.makedirs(OUTRO_DIR, exist_ok=True)

OUTRO_TEXT = """हे सखा... अब कुछ क्षणों के लिए अपनी आँखें बंद करो... और इस मौन को अपने भीतर उतरने दो...
जो दिव्य सत्य तुमने अभी सुना है... वह केवल शब्द नहीं... तुम्हारी आत्मा की मुक्ति का मार्ग है...
यह संसार तुम्हें बार-बार थकाएगा... लोग तुम्हें परखेंगे... परिस्थितियां तुम्हें तोड़ने का प्रयास करेंगी...
लेकिन स्मरण रखना... अर्जुन के रथ पर भी वही माधव सारथी बनकर बैठे थे... और आज तुम्हारे जीवन के रथ की डोर भी उन्हीं के हाथों में है...
जब भी तुम्हारा मन विचलित हो... जब भी हृदय में अंधकार छाने लगे... तो व्यर्थ की चिंताओं को छोड़कर... अपनी संपूर्ण चेतना को श्रीकृष्ण के चरणों में समर्पित कर देना...
क्योंकि जिसका रक्षक गोविंद हो... उसका अनिष्ट करने की शक्ति इस पूरे ब्रह्मांड में किसी के पास नहीं है...
शांत हो जाओ... गहरी सांस लो... और उस परम चेतना के साथ एक हो जाओ...
ॐ नमो भगवते वासुदेवाय...
ॐ कृष्णाय वासुदेवाय हरये परमात्मने... प्रणतः क्लेशनाशाय गोविंदाय नमो नमः...
हरे कृष्ण हरे कृष्ण... कृष्ण कृष्ण हरे हरे...
हरे राम हरे राम... राम राम हरे हरे...
ॐ शांति... शांति... शांति..."""

RAW_VOICE_MP3 = os.path.join(OUTRO_DIR, "_outro_voice_raw.mp3")
MASTER_VOICE_MP3 = os.path.join(OUTRO_DIR, "_outro_voice_dsp.mp3")
MIXED_AUDIO_M4A = os.path.join(OUTRO_DIR, "_outro_audio_final.m4a")
BG_MUSIC_PATH = os.path.join(BASE_DIR, "music_vault", "ch_01_gita_meditative", "output000.mp3")
TARGET_OUTRO_MP4 = os.path.join(OUTRO_DIR, "master_shield_outro_1080p.mp4")

# Source video (the Blue Laser animation) - prefer pristine 1080p source if present
DOWNLOADS_OUTRO = r"C:\Users\janar\Downloads\content_id_outro.mp4"
LOCAL_OUTRO = os.path.join(BASE_DIR, "assets", "outro", "norm_content_id_outro.mp4")
RAW_VIDEO_SOURCE = DOWNLOADS_OUTRO if os.path.exists(DOWNLOADS_OUTRO) else LOCAL_OUTRO

async def synthesize_voice():
    print("[1/4] Synthesizing Divine Outro Voiceover via Edge-TTS (hi-IN-MadhurNeural)...")
    comm = edge_tts.Communicate(
        text=OUTRO_TEXT,
        voice="hi-IN-MadhurNeural",
        rate="-5%",
        pitch="-6Hz"
    )
    await comm.save(RAW_VOICE_MP3)
    print(f"✓ Saved raw voice: {RAW_VOICE_MP3} ({os.path.getsize(RAW_VOICE_MP3)/1024:.1f} KB)")

def process_dsp_and_mix():
    print("[2/4] Applying Shure SM7B DSP & Mixing with 432 Hz Flute Meditation Music...")
    # Get voice duration
    cmd_dur = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", RAW_VOICE_MP3]
    v_dur = float(subprocess.check_output(cmd_dur).decode().strip())
    print(f"[*] Voice duration: {v_dur:.1f}s")

    # Target outro duration is 173.25s
    target_dur = 173.25

    # DSP filter for voice: High pass 75Hz, Warmth 220Hz +2.5dB, Presence 3200Hz +3dB, Compression
    dsp_filter = (
        "highpass=f=75,"
        "equalizer=f=220:t=q:w=1.2:g=2.5,"
        "equalizer=f=3200:t=q:w=1.5:g=3.0,"
        "acompressor=threshold=-18dB:ratio=3:attack=5:release=50:makeup=2.5dB,"
        "volume=1.4"
    )

    # Mix voice (starts at 3.0s into outro, with silence before it for smooth transition)
    # Background music loops or plays for full 173.25s at volume=0.35, fades out at end
    filter_mix = (
        f"[0:a]{dsp_filter},adelay=3000|3000[voice];"
        f"[1:a]aloop=loop=-1:size=2e+09,atrim=0:{target_dur},volume=0.38,afade=t=in:ss=0:d=2,afade=t=out:st=168:d=5[music];"
        f"[music][voice]amix=inputs=2:duration=first:dropout_transition=2,aformat=sample_rates=48000:channel_layouts=stereo[out]"
    )

    cmd_mix = [
        "ffmpeg", "-y",
        "-i", RAW_VOICE_MP3,
        "-i", BG_MUSIC_PATH,
        "-filter_complex", filter_mix,
        "-map", "[out]",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-t", str(target_dur),
        MIXED_AUDIO_M4A
    ]
    subprocess.run(cmd_mix, check=True)
    print(f"✓ Master mixed audio created: {MIXED_AUDIO_M4A} ({os.path.getsize(MIXED_AUDIO_M4A)/1024:.1f} KB)")

def bake_final_outro_video():
    print("[3/4] Baking Master 1080p Shield Outro with Guaranteed Sound...")
    # Render video stream from RAW_VIDEO_SOURCE, replace audio stream with MIXED_AUDIO_M4A
    # Ensure exact 1920x1080, 30fps, setsar=1, stereo 48000Hz
    cmd_bake = [
        "ffmpeg", "-y",
        "-i", RAW_VIDEO_SOURCE,
        "-i", MIXED_AUDIO_M4A,
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,setsar=1,fps=30,format=yuv420p",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "20",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "48000",
        "-ac", "2",
        "-shortest",
        TARGET_OUTRO_MP4
    ]
    subprocess.run(cmd_bake, check=True)
    size_mb = os.path.getsize(TARGET_OUTRO_MP4) / (1024 * 1024)
    print(f"🎉 MASTER 1080p OUTRO CREATED: {TARGET_OUTRO_MP4} ({size_mb:.1f} MB)")

    # Overwrite the standard_1080p_outro.mp4 and norm_content_id_outro.mp4 so every tool uses this!
    std_target = os.path.join(OUTRO_DIR, "standard_1080p_outro.mp4")
    norm_target = os.path.join(OUTRO_DIR, "norm_content_id_outro.mp4")
    import shutil
    shutil.copy2(TARGET_OUTRO_MP4, std_target)
    shutil.copy2(TARGET_OUTRO_MP4, norm_target)
    print(f"✓ Synchronized and hard-locked to:\n  - {std_target}\n  - {norm_target}")

def main():
    asyncio.run(synthesize_voice())
    process_dsp_and_mix()
    bake_final_outro_video()
    print("\n[4/4] COMPLETE! Outro audio is now 100% hard-locked with divine sound & music.")

if __name__ == "__main__":
    main()
