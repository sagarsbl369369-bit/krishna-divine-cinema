import os
import sys
import subprocess
import shutil

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(RENDERS_DIR, exist_ok=True)

# 100% Real-Life Human Psychology Script (ZERO Kurukshetra, ZERO Mythology)
LOGICAL_SCRIPT = (
    "तुम रात को तीन बजे छत को घूरते हुए किस बात का हिसाब लगा रहे हो? "
    "उस इंसान का, जिसने तुम्हारी अच्छाई का फायदा उठाकर तुम्हें कचरे की तरह फेंक दिया? "
    "या उस भविष्य का, जो अभी आया ही नहीं, लेकिन उसकी चिंता ने तुम्हारे आज का सुकून छीन लिया है? "
    "कड़वा सच यह है कि तुम्हें किसी दुश्मन ने बर्बाद नहीं किया। "
    "तुम्हें तुम्हारी ही उस आदत ने तोड़ा है, जिसमें तुम दूसरों से वफादारी, सम्मान और प्रेम की भीख मांगते रहे। "
    "प्रकृति का सबसे कठोर नियम समझ लो—इस पूरे ब्रह्मांड में किसी भी इंसान के पास यह शक्ति नहीं है कि वह तुम्हें दुखी कर सके, जब तक तुम खुद अपनी चाबी उसके हाथ में न सौंप दो। "
    "तुम लोगों के व्यवहार को अपने मन पर इतना भारी क्यों बना लेते हो? "
    "जो व्यक्ति आज तुम्हारे साथ हंस रहा है, कल वही तुम्हारी पीठ में खंजर घोंप सकता है—क्योंकि यह संसार प्रेम से नहीं, स्वार्थ और अपनी ज़रूरतों से चलता है। "
    "जिस दिन किसी की ज़रूरत खत्म होगी, उस दिन उसका स्वभाव बदल जाएगा। "
    "यह जानकर भी अगर तुम रो रहे हो, तो गलती उसकी नहीं, तुम्हारी नासमझी की है। "
    "अपने दिमाग को यह एक बात रटा दो: जो गया, वह तुम्हारा कभी था ही नहीं; जो रुका है, वह भी हमेशा नहीं रहेगा; और जो तुम्हारे भीतर यह सब देख रहा है, वही तुम्हारा एकमात्र शाश्वत सत्य है। "
    "बाहर की दुनिया में स्वीकृति ढूंढना बंद करो। अपनी रीढ़ सीधी करो, और अपनी शांति की बागडोर अपने हाथों में वापस लो।"
)

raw_voice = os.path.join(RENDERS_DIR, "demo_logical_raw.mp3")
dsp_voice = os.path.join(RENDERS_DIR, "demo_logical_dsp.mp3")
bgm_source = os.path.join(BASE_DIR, "music_vault", "ch_01_gita_meditative", "output001.mp3")
master_out = os.path.join(RENDERS_DIR, "demo_logical_reallife_voice_2min.mp3")

print("==================================================================")
print("🎙️ GENERATING 100% REAL-LIFE LOGICAL GOOSEBUMP-INDUCING DEMO")
print("==================================================================")
print(f"Script words: {len(LOGICAL_SCRIPT.split())} words")

# 1. Synthesize with deep authority (-3Hz pitch, -5% rate)
import asyncio, edge_tts
async def synth():
    comm = edge_tts.Communicate(LOGICAL_SCRIPT, "hi-IN-MadhurNeural", rate="-5%", pitch="-3Hz")
    await comm.save(raw_voice)
asyncio.run(synth())

# 2. Shure SM7B DSP Mastering (Stereo 48kHz + Broadcast EQ)
SHURE_SM7B_CHAIN = (
    "aresample=48000,"
    "aformat=channel_layouts=stereo,"
    "highpass=f=75,"
    "equalizer=f=180:t=q:w=1.2:g=4.5,"
    "equalizer=f=450:t=q:w=1.5:g=-2.5,"
    "equalizer=f=3200:t=q:w=1.1:g=3.2,"
    "equalizer=f=6800:t=q:w=2.0:g=-3.0,"
    "lowpass=f=14000,"
    "compand=attacks=0.015:decays=0.12:points=-80/-80|-45/-30|-24/-16|-12/-8|0/-6:gain=3.8,"
    "loudnorm=I=-14:TP=-1.0:LRA=9"
)
subprocess.run([
    "ffmpeg", "-y", "-i", raw_voice,
    "-af", SHURE_SM7B_CHAIN,
    "-c:a", "libmp3lame", "-b:a", "320k",
    dsp_voice
], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Measure duration
probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", dsp_voice], capture_output=True, text=True, check=True)
dur = float(probe.stdout.strip())
print(f"Voice Duration: {dur:.2f} seconds ({dur/60:.2f} mins)")

# 3. Mix with sidechain ducked soundscape (150% vocal power)
mix_cmd = [
    "ffmpeg", "-y",
    "-i", dsp_voice,
    "-stream_loop", "-1", "-i", bgm_source,
    "-filter_complex",
    "[0:a]volume=1.50[vocal];"
    "[1:a]volume=0.10,lowpass=f=2000[bgm];"
    "[vocal][bgm]amix=inputs=2:duration=first:dropout_transition=2:normalize=false[mixed];"
    "[mixed]alimiter=limit=0.95:attack=5:release=50[out]",
    "-map", "[out]",
    "-t", f"{dur:.2f}",
    "-c:a", "libmp3lame", "-b:a", "320k",
    master_out
]
subprocess.run(mix_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Master Audio Mixed Successfully!")

# Deploy to Desktop
dest_dirs = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]
for d in dest_dirs:
    if os.path.exists(d):
        target_mp3 = os.path.join(d, '🎵 REAL_LIFE_LOGICAL_DEMO.mp3')
        shutil.copy2(master_out, target_mp3)
        bat_path = os.path.join(d, 'PLAY_LOGICAL_DEMO.bat')
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write(f'start "" "{target_mp3}"\n')

if os.path.exists(raw_voice): os.remove(raw_voice)
if os.path.exists(dsp_voice): os.remove(dsp_voice)
print("Demo deployed to Desktop!")
