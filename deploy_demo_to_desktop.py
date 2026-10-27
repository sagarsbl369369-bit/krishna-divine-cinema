import os
import shutil

src = os.path.join(os.getcwd(), 'renders', 'demo_krishnavandan_voice_2min.mp3')
dest_dirs = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop')
]

for d in dest_dirs:
    if os.path.exists(d):
        target_mp3 = os.path.join(d, '🎵 2-MIN_VOICE_DEMO.mp3')
        shutil.copy2(src, target_mp3)
        print('Copied to:', target_mp3)
        bat_path = os.path.join(d, '▶️ PLAY_2MIN_VOICE_DEMO.bat')
        with open(bat_path, 'w', encoding='utf-8') as f:
            f.write('@echo off\n')
            f.write(f'start "" "{target_mp3}"\n')
        print('Created batch launcher:', bat_path)
