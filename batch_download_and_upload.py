"""
Autonomous Batch Downloader & PC Human-Mimicry Uploader
======================================================
1. Downloads completed video artifacts from GitHub Actions Run 40354494907.
2. Unzips each video, thumbnail, and SEO package.
3. Appends the 173.25s Blue Laser Shield Outro (norm_content_id_outro.mp4) via FFmpeg copy.
4. Uploads to YouTube Studio via Playwright Stealth Bot:
   - Workers 1 to 5  -> Channel 1 (चैनल १: दिव्य गीता वाणी) [100% UNLISTED]
   - Workers 6 to 10 -> Channel 2 (चैनल २: परम कृष्ण चेतना) [100% UNLISTED]
5. Logs all live YouTube URLs to `renders/uploaded_videos_log.json`.
"""

import os
import sys
import json
import time
import zipfile
import io
import subprocess
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
BATCH_DIR = os.path.join(RENDERS_DIR, "cloud_batch")
OUTRO_PATH = os.path.join(BASE_DIR, "assets", "outro", "norm_content_id_outro.mp4")
LOG_PATH = os.path.join(RENDERS_DIR, "uploaded_videos_log.json")
CONFIG_PATH = os.path.join(BASE_DIR, "credentials", "github_cloud_config.json")

os.makedirs(BATCH_DIR, exist_ok=True)

from youtube_human_uploader import YouTubeHumanUploader

def load_upload_log():
    if os.path.exists(LOG_PATH):
        try:
            with open(LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_upload_log(log_data):
    with open(LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log_data, f, indent=2, ensure_ascii=False)

def append_outro_if_needed(video_path: str) -> str:
    """Appends 173.25s outro via FFmpeg stream copy if video does not already have it."""
    if not os.path.exists(OUTRO_PATH):
        return video_path

    # Check duration with ffprobe
    try:
        probe = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ], capture_output=True, text=True, check=True)
        dur = float(probe.stdout.strip())
        if dur > 1650:
            print(f"   ✓ Video already has full duration ({dur:.2f}s). Outro already included.")
            return video_path
    except Exception:
        pass

    print(f"   🔒 Appending 173.25s Blue Laser Shield Outro to {os.path.basename(video_path)}...")
    v_out = video_path.replace(".mp4", "_with_outro.mp4")
    manifest = video_path.replace(".mp4", "_concat.txt")
    with open(manifest, "w", encoding="utf-8") as f:
        f.write(f"file '{video_path.replace(chr(92), '/')}'\n")
        f.write(f"file '{OUTRO_PATH.replace(chr(92), '/')}'\n")

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", manifest, "-c", "copy", v_out]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if os.path.exists(manifest):
        os.remove(manifest)

    if res.returncode == 0 and os.path.exists(v_out) and os.path.getsize(v_out) > os.path.getsize(video_path):
        os.replace(v_out, video_path)
        print(f"   ✓ Outro appended successfully! Updated size: {round(os.path.getsize(video_path)/(1024*1024), 2)} MB")
    elif os.path.exists(v_out):
        os.remove(v_out)
    return video_path

def download_artifact(cfg, artifact_id: int, target_dir: str) -> bool:
    """Streams and extracts artifact zip into target_dir."""
    headers = {
        "Authorization": f"Bearer {cfg['github_token']}",
        "Accept": "application/vnd.github+json"
    }
    url = f"https://api.github.com/repos/{cfg['github_repo']}/actions/artifacts/{artifact_id}/zip"
    print(f"   📥 Downloading Artifact {artifact_id}...")
    try:
        r = requests.get(url, headers=headers, stream=True, timeout=120)
        if r.status_code == 200:
            os.makedirs(target_dir, exist_ok=True)
            zip_data = io.BytesIO(r.content)
            with zipfile.ZipFile(zip_data) as z:
                z.extractall(target_dir)
            print(f"   ✓ Extracted files to: {target_dir}")
            return True
        else:
            print(f"   ❌ HTTP {r.status_code} while downloading artifact: {r.text}")
            return False
    except Exception as e:
        print(f"   ❌ Download error: {e}")
        return False

def main():
    print("=" * 80)
    print("🚀 AUTONOMOUS BATCH CLOUD DOWNLOADER & PC STUDIO UPLOADER")
    print("=" * 80)

    cfg = json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
    upload_log = load_upload_log()

    # Get list of artifacts from latest run
    run_id = 40354494907
    headers = {
        "Authorization": f"Bearer {cfg['github_token']}",
        "Accept": "application/vnd.github+json"
    }
    r = requests.get(f"https://api.github.com/repos/{cfg['github_repo']}/actions/runs/{run_id}/artifacts", headers=headers)
    artifacts = r.json().get("artifacts", [])
    print(f"Found {len(artifacts)} Ready Cloud Video Artifacts in Run #{run_id}.\n")

    # Sort artifacts by worker number 1..10
    def get_worker_num(art_name):
        import re
        m = re.search(r"worker-(\d+)", art_name)
        return int(m.group(1)) if m else 99

    artifacts = sorted(artifacts, key=lambda a: get_worker_num(a["name"]))

    for art in artifacts:
        name = art["name"]
        art_id = art["id"]
        w_num = get_worker_num(name)
        channel_id = "ch_01" if w_num <= 5 else "ch_02"
        ch_name = "चैनल १ (दिव्य गीता वाणी)" if channel_id == "ch_01" else "चैनल २ (परम कृष्ण चेतना)"

        print("\n" + "=" * 80)
        print(f"🎬 PROCESSING: {name} (Worker {w_num}) ➔ {ch_name}")
        print("=" * 80)

        # Check if already uploaded
        if upload_log.get(name, {}).get("status") == "published":
            print(f"   ✓ Already published! URL: {upload_log[name].get('video_url')}")
            continue

        worker_dir = os.path.join(BATCH_DIR, f"worker_{w_num}")
        
        # 1. Download if not present
        video_file = None
        if os.path.exists(worker_dir):
            for f in os.listdir(worker_dir):
                if f.endswith(".mp4") and not f.endswith("_with_outro.mp4"):
                    video_file = os.path.join(worker_dir, f)
                    break

        if not video_file or os.path.getsize(video_file) < 10000000:
            ok = download_artifact(cfg, art_id, worker_dir)
            if not ok:
                print(f"   ⚠️ Skipping {name} due to download failure.")
                continue
            for f in os.listdir(worker_dir):
                if f.endswith(".mp4") and not f.endswith("_with_outro.mp4"):
                    video_file = os.path.join(worker_dir, f)
                    break

        if not video_file:
            print(f"   ⚠️ No .mp4 file found in {worker_dir}")
            continue

        # 2. Append Outro if needed
        video_file = append_outro_if_needed(video_file)

        # 3. Find Manifest / SEO package
        manifest_file = None
        for f in os.listdir(worker_dir):
            if f.endswith("manifest.json") or f.endswith("seo.json"):
                manifest_file = os.path.join(worker_dir, f)
                break

        seo_package = {}
        if manifest_file and os.path.exists(manifest_file):
            try:
                with open(manifest_file, "r", encoding="utf-8") as mf:
                    m_data = json.load(mf)
                    seo_package = m_data.get("seo_package", m_data)
            except Exception:
                pass

        if not seo_package.get("title"):
            seo_package["title"] = f"श्रीमद्भगवद्गीता का दिव्य ज्ञान | भगवान श्रीकृष्ण का संदेश #{w_num} | गीता उपदेश"
            seo_package["description"] = "श्रीमद्भगवद्गीता के परम पावन उपदेश और जीवन का रहस्य।\n\n#BhagavadGita #KrishnaGyan #KarmaYoga"
            seo_package["tags"] = ["Bhagavad Gita", "Krishna Vani", "Geeta Updesh", "Karma Yoga", "Sanatan Dharma"]

        # 4. Find Thumbnail
        thumb_file = None
        for f in os.listdir(worker_dir):
            if f.lower().endswith((".jpg", ".png", ".webp")) and "thumb" in f.lower():
                thumb_file = os.path.join(worker_dir, f)
                break
        if not thumb_file:
            thumb_file = os.path.join(BASE_DIR, "master_viral_thumbnail.jpg")

        print(f"   🏷️ Title: {seo_package.get('title')}")
        print(f"   📁 Video: {video_file} ({round(os.path.getsize(video_file)/(1024*1024), 2)} MB)")
        print(f"   🖼️ Thumbnail: {thumb_file}")
        print(f"   📺 Target Channel: {channel_id} ({ch_name})")
        print(f"   🔒 Visibility: 100% UNLISTED")

        # 5. Execute PC Human-Mimicry Studio Upload
        print(f"\n   🤖 Launching YouTube Studio Human-Mimicry Bot for {channel_id}...")
        try:
            uploader = YouTubeHumanUploader(channel_id=channel_id)
            res = uploader.upload_video(
                video_path=video_file,
                seo_package=seo_package,
                thumbnail_path=thumb_file,
                channel_id=channel_id,
                privacy="unlisted",
                headless=True
            )
            print(f"\n   Upload Result for Worker {w_num}:", json.dumps(res, indent=2, ensure_ascii=False))

            if res.get("success"):
                upload_log[name] = {
                    "worker_id": w_num,
                    "channel_id": channel_id,
                    "status": "published",
                    "title": seo_package.get("title"),
                    "video_url": res.get("video_url"),
                    "published_at": time.time()
                }
                save_upload_log(upload_log)
                print(f"   🎉 SUCCESS: Worker {w_num} published to {channel_id}! Link: {res.get('video_url')}\n")
            else:
                print(f"   ⚠️ Upload finished with note: {res.get('message') or res.get('error')}\n")
        except Exception as u_err:
            print(f"   ❌ Upload execution error: {u_err}")

        # Cooldown between sequential browser uploads
        print("   ⏳ Cooldown 15 seconds before next upload...")
        time.sleep(15)

    print("\n" + "=" * 80)
    print("🎉 ALL FINISHED CLOUD VIDEOS PROCESSED & UPLOADED!")
    print("=" * 80)

if __name__ == "__main__":
    main()
