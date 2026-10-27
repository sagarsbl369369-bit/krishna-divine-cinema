import os
import shutil

master_file = r"C:\Users\janar\.gemini\antigravity\scratch\geeta_automation_engine\renders\demo_5min_hyperrealistic_master.mp3"

desktops = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]

for d in desktops:
    if os.path.exists(d):
        clean_mp3 = os.path.join(d, '5MIN_HYPERREALISTIC_VOICE_DEMO.mp3')
        shutil.copy2(master_file, clean_mp3)
        bat_file = os.path.join(d, 'PLAY_5MIN_VOICE_DEMO.bat')
        with open(bat_file, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write('echo ====================================================\n')
            f.write('echo    PLAYING 10X HYPER-REALISTIC 5-MIN VOICE DEMO\n')
            f.write('echo ====================================================\n')
            f.write(f'start "" "{clean_mp3}"\n')

print("Clean batch and MP3 deployed!")
