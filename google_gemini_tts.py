"""
Google Gemini Free TTS Audio Engine with Shure SM7B Studio DSP
--------------------------------------------------------------
- Leverages Google AI Studio Free Tier Gemini TTS models (gemini-2.5-flash-preview-tts, gemini-3.8-flash-tts)
- High-authority, resonant divine voice: 'Charon' (or 'Fenrir')
- Rotates across multi-key pool (gemini_key_pool.py) with auto-retry
- Splits long chapter exposition into natural paragraphs for zero truncation
- Decodes raw 24kHz PCM to 48kHz Broadcast Studio Master
- Masters through Shure SM7B DSP Chain + EBU R128 (-14 LUFS)
- Resilient fallback to Edge-TTS (hi-IN-MadhurNeural) if Gemini quota is busy
"""

import os
import sys
import re
import json
import time
import subprocess
from typing import List, Tuple
from google import genai
from google.genai import types
from gemini_key_pool import gemini_pool

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
TEMP_DIR = os.path.join(BASE_DIR, "renders", "temp_tts")
os.makedirs(TEMP_DIR, exist_ok=True)

# Load config for voice settings
SHURE_SM7B_DSP_CHAIN = (
    "aresample=48000,"
    "aformat=channel_layouts=stereo,"
    "highpass=f=70,"
    "equalizer=f=160:t=q:w=1.2:g=5.0,"   # Deep chest warmth / Shure SM7B proximity
    "equalizer=f=420:t=q:w=1.5:g=-3.0,"  # Eliminates nasal / boxy mud
    "equalizer=f=2800:t=q:w=1.0:g=3.2,"  # Clear vocal intimacy & presence
    "equalizer=f=6500:t=q:w=2.0:g=-3.5,"  # Smooth de-esser for sibilants
    "lowpass=f=14500,"                    # Silky vintage broadcast top end
    "compand=attacks=0.012:decays=0.15:points=-80/-80|-45/-28|-24/-14|-12/-8|0/-5:gain=4.2,"
    "loudnorm=I=-14:TP=-1.0:LRA=9"       # EBU R128 YouTube broadcast standard
)

CANDIDATE_TTS_MODELS = [
    "gemini-2.5-flash-preview-tts",
    "gemini-3.8-flash-tts",
    "gemini-3.1-flash-tts-preview"
]

def split_into_natural_chunks(text: str, max_words: int = 70) -> List[str]:
    """Splits Hindi text into natural sentence groups of ~50-70 words."""
    sentences = re.split(r'([।!\?\n]+)', text)
    chunks = []
    current_chunk = ""

    for i in range(0, len(sentences), 2):
        s = sentences[i].strip()
        delim = sentences[i+1] if i+1 < len(sentences) else "।"
        if not s:
            continue
        full_sentence = f"{s}{delim} "
        if len((current_chunk + full_sentence).split()) > max_words and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = full_sentence
        else:
            current_chunk += full_sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text.strip()]


def synthesize_gemini_chunk(client: genai.Client, text: str, voice_name: str = "Charon") -> bytes:
    """Synthesizes a single text chunk to raw PCM bytes using Google Gemini TTS."""
    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name=voice_name
                )
            )
        )
    )

    last_err = None
    for model_name in CANDIDATE_TTS_MODELS:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=text,
                config=config
            )
            for part in resp.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    return part.inline_data.data
        except Exception as e:
            last_err = e
            continue

    raise RuntimeError(f"Gemini TTS failed across all candidate models: {last_err}")


def generate_google_realistic_voice(text: str, audio_path: str, voice_name: str = "Charon") -> float:
    """
    Synthesizes long Hindi exposition using Google AI Studio Free Gemini TTS (Voice: Charon).
    Processes text in chunks with auto-key rotation and masters through Shure SM7B DSP chain.
    """
    out_dir = os.path.dirname(os.path.abspath(audio_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    clean_text = text.strip()
    chunks = split_into_natural_chunks(clean_text, max_words=65)
    print(f"   [🎙️] Google Gemini Free TTS ('{voice_name}'): {len(chunks)} chunks, ~{len(clean_text.split())} words...")

    chunk_files = []
    use_fallback = False

    for idx, chunk in enumerate(chunks, start=1):
        raw_pcm_path = os.path.join(TEMP_DIR, f"gemini_chunk_{idx}_{int(time.time()*1000)}.pcm")
        chunk_mp3 = os.path.join(TEMP_DIR, f"gemini_chunk_{idx}_{int(time.time()*1000)}.mp3")

        # Try Google Gemini TTS via key pool
        success = False
        for attempt in range(len(gemini_pool.keys) + 1):
            try:
                client, key = gemini_pool.get_active_client()
                pcm_data = synthesize_gemini_chunk(client, chunk, voice_name)
                with open(raw_pcm_path, "wb") as f:
                    f.write(pcm_data)
                
                # Convert raw 24kHz PCM to standard MP3
                cmd_pcm = [
                    "ffmpeg", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
                    "-i", raw_pcm_path,
                    "-c:a", "libmp3lame", "-b:a", "192k",
                    chunk_mp3
                ]
                subprocess.run(cmd_pcm, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                gemini_pool.mark_success(key)
                if os.path.exists(raw_pcm_path):
                    os.remove(raw_pcm_path)
                chunk_files.append(chunk_mp3)
                success = True
                print(f"      [✓] Chunk {idx}/{len(chunks)} rendered with Google TTS ({voice_name}).")
                break
            except Exception as e:
                err_s = str(e)
                if "429" in err_s or "quota" in err_s.lower() or "RESOURCE_EXHAUSTED" in err_s:
                    gemini_pool.mark_exhausted(key)
                else:
                    time.sleep(0.5)

        if not success:
            print(f"      [!] Gemini TTS temporary quota limit on chunk {idx}. Utilizing Edge-TTS fallback.")
            use_fallback = True
            break

    # If any error in Google TTS, fallback to Edge-TTS + Shure SM7B DSP
    if use_fallback or not chunk_files:
        print("   [🔄] Executing Edge-TTS (hi-IN-MadhurNeural) with Studio Shure SM7B DSP...")
        raw_mp3 = audio_path.replace(".mp3", "_raw.mp3")
        tts_ok = False
        try:
            import asyncio, edge_tts
            from pydub import AudioSegment

            # Split clean text by natural sentence markers and stitch with real audio silence
            raw_sents = re.split(r'([।!\?\n]+)', clean_text)
            stitched_audio = AudioSegment.empty()
            temp_seg_dir = os.path.join(TEMP_DIR, f"stitch_{int(time.time()*1000)}")
            os.makedirs(temp_seg_dir, exist_ok=True)

            async def _synth_sentence(s_text, s_path):
                comm = edge_tts.Communicate(s_text, "hi-IN-MadhurNeural", rate="-7%", pitch="-4Hz")
                await comm.save(s_path)

            seg_idx = 0
            for i in range(0, len(raw_sents), 2):
                s = raw_sents[i].strip()
                delim = raw_sents[i+1] if i+1 < len(raw_sents) else "।"
                if not s:
                    continue
                full_sent = f"{s}{delim}"
                pause_ms = 1100 if "?" in delim else 750
                s_file = os.path.join(temp_seg_dir, f"s_{seg_idx:03d}.mp3")
                asyncio.run(_synth_sentence(full_sent, s_file))
                if os.path.exists(s_file):
                    seg_aud = AudioSegment.from_file(s_file)
                    stitched_audio += seg_aud + AudioSegment.silent(duration=pause_ms)
                    try: os.remove(s_file)
                    except Exception: pass
                seg_idx += 1

            try: os.rmdir(temp_seg_dir)
            except Exception: pass

            stitched_audio.export(raw_mp3, format="mp3", bitrate="320k")
            if os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 1000:
                tts_ok = True
        except Exception as e_direct:
            print(f"      [!] Python sentence-stitched fallback error: {e_direct}, attempting single call...")
            cmd_tts = [
                sys.executable, "-m", "edge_tts",
                "--voice", "hi-IN-MadhurNeural",
                "--rate", "-7%",
                "--pitch", "-4Hz",
                "--text", clean_text,
                "--write-media", raw_mp3
            ]
            subprocess.run(cmd_tts, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if os.path.exists(raw_mp3) and os.path.getsize(raw_mp3) > 1000:
                tts_ok = True
        unmastered_audio = raw_mp3
    else:
        # Concatenate all rendered Gemini TTS chunks
        concat_list = os.path.join(TEMP_DIR, f"tts_concat_{int(time.time()*1000)}.txt")
        with open(concat_list, "w", encoding="utf-8") as f:
            for cf in chunk_files:
                f.write(f"file '{cf.replace(chr(92), '/')}'\n")

        unmastered_audio = os.path.join(TEMP_DIR, f"unmastered_{int(time.time()*1000)}.mp3")
        cmd_cat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", unmastered_audio]
        subprocess.run(cmd_cat, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Cleanup chunk files
        for cf in chunk_files:
            if os.path.exists(cf):
                os.remove(cf)
        if os.path.exists(concat_list):
            os.remove(concat_list)

    # Master through Shure SM7B Studio DSP Chain
    print("   [🎛️] Mastering Voiceover through Shure SM7B DSP & -14 LUFS Loudness Normalization...")
    cmd_dsp = [
        "ffmpeg", "-y", "-i", unmastered_audio,
        "-af", SHURE_SM7B_DSP_CHAIN,
        "-c:a", "libmp3lame", "-b:a", "192k",
        audio_path
    ]
    subprocess.run(cmd_dsp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if os.path.exists(unmastered_audio):
        os.remove(unmastered_audio)

    # Measure exact duration with ffprobe
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", audio_path
    ]
    dur = float(subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout.strip())
    print(f"   [✓] Voiceover Studio Mastered: {dur:.2f} seconds ({dur/60:.2f} minutes)")
    return dur


if __name__ == "__main__":
    test_text = (
        "जब दुनिया के सबसे महान धनुर्धर ने युद्धभूमि में शस्त्र डाल दिए, तब श्रीकृष्ण ने कोई मीठी सांत्वna नहीं दी, "
        "बल्कि वो अंतिम और क्रूर सत्य कहा जो मृत्यु को भी थरथरा दे। कुरुक्षेत्र का यह युद्ध केवल बाहर का नहीं, "
        "यह हर इंसान के भीतर चलने वाला शाश्वत महासंग्राम है।"
    )
    out_p = os.path.join(BASE_DIR, "renders", "test_gemini_charon_voice.mp3")
    dur = generate_google_realistic_voice(test_text, out_p, "Charon")
    print(f"Test Voice Mastered Successfully: {dur:.2f}s -> {out_p}")
