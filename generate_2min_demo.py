import os
import sys
import time
import json
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(RENDERS_DIR, exist_ok=True)

# 2-Minute Pure Hindi Master Narration (Zero modern English, Zero Sanskrit chanting)
DEMO_SCRIPT = (
    "जब आधी रात को पूरा संसार सो रहा होता है, और तुम अपने ही विचारों की आग में जल रहे होते हो... "
    "जब कोई अपना तुम्हारा विश्वास तोड़ दे, और तुम्हारी आत्मा चीत्कार कर उठे कि मेरे साथ ही ऐसा क्यों हुआ... "
    "तब कुरुक्षेत्र की उस धूल भरी भूमि पर खड़े श्रीकृष्ण की वह एक दृष्टि याद कर लेना। "
    "अर्जुन ने भी कांपते हाथों से अपना गांडीव धनुष रथ के फर्श पर डाल दिया था। उसकी आंखों में आंसू थे और छाती में वही असहनीय दर्द था जो आज तुम्हारे सीने में जल रहा है। "
    "लेकिन श्रीकृष्ण ने उसे कोई मीठी या झूठी सांत्वना नहीं दी। उन्होंने यह नहीं कहा कि सब ठीक हो जाएगा। "
    "श्रीकृष्ण ने मुस्कुराते हुए कहा—हे पार्थ! तू जिसे अपना कह रहा है, वह केवल तेरे मोह की एक छाया है। "
    "तू दुख से नहीं, बल्कि सुख की अपनी झूठी अपेक्षाओं से पीड़ित है। "
    "जो बीत गया, वह काल के गर्भ में विलीन हो चुका है; और जो आने वाला है, उस पर तेरी किसी चिंता का कोई अधिकार नहीं है। "
    "तेरा अधिकार केवल इस वर्तमान क्षण के कर्म पर है। जब तक तू फल की भीख मांगता रहेगा, तब तक तू इस संसार का दास बना रहेगा। "
    "जिस क्षण तूने परिणाम की चिंता छोड़ दी, उसी क्षण तू काल का भी स्वामी बन जाएगा। उठ पार्थ! और अपने भीतर के इस भय का संहार कर।"
)

raw_voice = os.path.join(RENDERS_DIR, "demo_raw_voice.mp3")
dsp_voice = os.path.join(RENDERS_DIR, "demo_dsp_voice.mp3")
bgm_source = os.path.join(BASE_DIR, "music_vault", "ch_01_gita_meditative", "output001.mp3")
master_out = os.path.join(RENDERS_DIR, "demo_krishnavandan_voice_2min.mp3")

print("==================================================================")
print("🎙️ GENERATING 2-MINUTE KRISHNA VANDAN 10X VOICE DEMO")
print("==================================================================")
print(f"Words: {len(DEMO_SCRIPT.split())} words")

# 1. Synthesize Voice with Edge-TTS (Madhur Neural -3Hz pitch, -5% rate for deep gravitas)
print("\n[1/3] Synthesizing Deep Divine Voiceover...")
import asyncio, edge_tts
async def synth():
    comm = edge_tts.Communicate(DEMO_SCRIPT, "hi-IN-MadhurNeural", rate="-5%", pitch="-3Hz")
    await comm.save(raw_voice)
asyncio.run(synth())

if not os.path.exists(raw_voice) or os.path.getsize(raw_voice) < 1000:
    raise RuntimeError("Voice synthesis failed!")

# 2. Shure SM7B DSP Mastering (48kHz Stereo + Low-end Warmth + High Presence + Optical Compression)
print("[2/3] Mastering through Shure SM7B Broadcast DSP Chain (-14 LUFS)...")
SHURE_SM7B_CHAIN = (
    "aresample=48000,"
    "aformat=channel_layouts=stereo,"
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.2:g=4.2,"
    "equalizer=f=450:t=q:w=1.5:g=-2.4,"
    "equalizer=f=3200:t=q:w=1.1:g=3.0,"
    "equalizer=f=6800:t=q:w=2.0:g=-3.0,"
    "lowpass=f=14000,"
    "compand=attacks=0.015:decays=0.12:points=-80/-80|-45/-30|-24/-16|-12/-8|0/-6:gain=3.5,"
    "loudnorm=I=-14:TP=-1.0:LRA=9"
)
cmd_dsp = [
    "ffmpeg", "-y", "-i", raw_voice,
    "-af", SHURE_SM7B_CHAIN,
    "-c:a", "libmp3lame", "-b:a", "320k",
    dsp_voice
]
subprocess.run(cmd_dsp, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Measure duration
probe_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", dsp_voice]
dur = float(subprocess.run(probe_cmd, capture_output=True, text=True, check=True).stdout.strip())
print(f"   ✓ Mastered Voice Duration: {dur:.2f} seconds ({dur/60:.2f} minutes)")

# 3. Blend with Devotional Background Music + Dynamic Ducking + 150% Voice Dominance
print("[3/3] Mixing 150% Voice Amplitude + Sidechain Ducked Devotional Soundscape...")
final_cmd = [
    "ffmpeg", "-y",
    "-i", dsp_voice,
    "-stream_loop", "-1", "-i", bgm_source,
    "-filter_complex",
    "[0:a]volume=1.50[vocal];"
    "[1:a]volume=0.12,lowpass=f=2200[bgm];"
    "[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=0[mixed];"
    "[mixed]alimiter=limit=-0.8:attack=5:release=50[out]",
    "-map", "[out]",
    "-t", f"{dur:.2f}",
    "-c:a", "libmp3lame", "-b:a", "320k",
    master_out
]
subprocess.run(final_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

print(f"\n🎉 [SUCCESS] Demo Mastered Successfully! -> {master_out}")

# Copy to Desktop
desktop_targets = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]
for d in desktop_targets:
    if os.path.exists(d):
        dest_mp3 = os.path.join(d, "🎵 2-MIN_VOICE_DEMO.mp3")
        shutil.copy2(master_out, dest_mp3)
        print(f"   ✓ Copied demo to Desktop: {dest_mp3}")
        
        # Create 1-click batch launcher to play it
        bat_p = os.path.join(d, "▶️ PLAY_2MIN_VOICE_DEMO.bat")
        with open(bat_p, "w", encoding="utf-8") as bf:
            bf.write('@echo off\nstart "" "🎵 2-MIN_VOICE_DEMO.mp3"\n')
        print(f"   ✓ Created 1-Click Player on Desktop: {bat_p}")

if os.path.exists(raw_voice): os.remove(raw_voice)
if os.path.exists(dsp_voice): os.remove(dsp_voice)
