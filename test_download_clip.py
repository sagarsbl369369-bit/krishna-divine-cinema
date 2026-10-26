import os
import requests
import subprocess

key = "48724139-1fbe7e777966fce52b390343f"
renders_dir = r"C:\Users\janar\.gemini\antigravity\scratch\geeta_automation_engine\renders\clips"
os.makedirs(renders_dir, exist_ok=True)

# Test downloading chariot clip (ID: 48683)
r = requests.get(f"https://pixabay.com/api/videos/?key={key}&id=48683")
data = r.json()
hits = data.get("hits", [])
if hits:
    url = hits[0]["videos"]["medium"]["url"]
    dest_raw = os.path.join(renders_dir, "test_chariot_raw.mp4")
    dest_norm = os.path.join(renders_dir, "test_chariot_norm.mp4")
    
    print(f"Downloading clip {hits[0]['id']}...")
    with requests.get(url, stream=True) as resp:
        with open(dest_raw, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1024*512):
                f.write(chunk)
    print(f"Downloaded {os.path.getsize(dest_raw)} bytes.")
    
    # Normalize with FFmpeg
    cmd = [
        "ffmpeg", "-y", "-i", dest_raw,
        "-t", "5",
        "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,setsar=1,fps=30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22", "-pix_fmt", "yuv420p",
        "-an", dest_norm
    ]
    subprocess.run(cmd, check=True)
    print(f"Normalized clip successfully: {dest_norm} ({os.path.getsize(dest_norm)} bytes)")
