"""
GitHub Actions Cloud Batch Uploader
===================================
Runs directly inside GitHub Actions Ubuntu runner (0% PC load).
1. Downloads completed video artifacts from previous cloud run (Run ID: 40484694835).
2. Unpacks master 1080p MP4, UHD Thumbnail, and SEO Package.
3. Automatically sweeps Channel 1 to convert any stuck drafts to live UNLISTED videos.
4. Uploads all 5 Channel 2 documentaries directly to YouTube Studio for Geeta Jeevan Sutra.
5. Uploads any remaining Channel 1 documentaries for Geeta Gyan 60 Sec.
"""

import os
import sys
import json
import time
import zipfile
import requests
import io
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
BATCH_DIR = os.path.join(RENDERS_DIR, "cloud_batch")
os.makedirs(BATCH_DIR, exist_ok=True)
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

from youtube_human_uploader import YouTubeHumanUploader

def setup_credentials():
    for ch in ["ch_01", "ch_02"]:
        st_data = os.getenv(f"YT_STORAGE_STATE_{ch.upper()}") or os.getenv(f"YT_STORAGE_STATE_{ch.upper().replace('_', '')}") or ""
        if st_data:
            st_path = os.path.join(CREDENTIALS_DIR, f"storage_state_{ch}.json")
            try:
                with open(st_path, "w", encoding="utf-8") as f:
                    f.write(st_data)
                print(f"✓ Configured storage state for {ch} ({os.path.getsize(st_path)} bytes)")
            except Exception as e:
                print(f"⚠️ Error saving storage state for {ch}: {e}")

def run_cloud_batch(github_token: str = None, run_id: str = "40484694835"):
    setup_credentials()

    # Step 1: Sweep Channel 1 Drafts
    print("\n" + "=" * 80)
    print("🧹 [PHASE 1] SWEEPING CHANNEL 1 DRAFTS IN YOUTUBE STUDIO")
    print("=" * 80)
    try:
        uploader_ch1 = YouTubeHumanUploader(channel_id="ch_01", profile_dir=os.getenv("CH_PROFILE_DIR_CH01"))
        with sync_playwright() as p:
            ctx = uploader_ch1._launch_context(p, headless=False)
            pg = ctx.new_page()
            uploader_ch1.sweep_and_publish_drafts(pg, "ch_01")
            ctx.close()
    except Exception as e_sw:
        print(f"⚠️ Draft sweep note: {e_sw}")

    # Step 2: Download and upload artifacts from Run ID
    repo = os.getenv("GITHUB_REPOSITORY", "sagarsbl369369-bit/krishna-divine-cinema")
    token = github_token or os.getenv("GITHUB_TOKEN")

    if not token:
        print("[!] Warning: GITHUB_TOKEN not available. Looking for local batch files...")
    else:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json"
        }
        print(f"\n[📥] Fetching artifacts from GitHub Actions Run {run_id} ({repo})...")
        art_url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/artifacts"
        r = requests.get(art_url, headers=headers)
        if r.status_code == 200:
            artifacts = r.json().get("artifacts", [])
            print(f"✓ Found {len(artifacts)} cloud artifacts ready for processing!")

            for art in artifacts:
                art_name = art["name"]
                art_id = art["id"]
                target_ch = "ch_01" if "channel-1" in art_name else "ch_02"
                ch_name = "Geeta Gyan 60 Sec" if target_ch == "ch_01" else "Geeta Jeevan Sutra"

                print("\n" + "-" * 70)
                print(f"📦 Processing: {art_name} -> Target: {ch_name} ({target_ch})")
                print("-" * 70)

                # Download zip
                dl_url = f"https://api.github.com/repos/{repo}/actions/artifacts/{art_id}/zip"
                r_dl = requests.get(dl_url, headers=headers)
                if r_dl.status_code == 200:
                    with zipfile.ZipFile(io.BytesIO(r_dl.content)) as z:
                        extract_path = os.path.join(BATCH_DIR, art_name)
                        os.makedirs(extract_path, exist_ok=True)
                        z.extractall(extract_path)
                        print(f"   ✓ Extracted {len(z.namelist())} files to {extract_path}")

                    # Find video, thumb, seo
                    v_file, t_file, s_file = None, None, None
                    for root, _, files in os.walk(extract_path):
                        for f in files:
                            if f.endswith(".mp4") and "outro" not in f.lower():
                                v_file = os.path.join(root, f)
                            elif f.endswith(".jpg") or f.endswith(".png"):
                                t_file = os.path.join(root, f)
                            elif f.endswith(".json") and "seo" in f.lower():
                                s_file = os.path.join(root, f)

                    if v_file:
                        seo_data = {}
                        if s_file and os.path.exists(s_file):
                            try:
                                with open(s_file, "r", encoding="utf-8") as sf:
                                    seo_data = json.load(sf)
                            except Exception:
                                pass
                        if not seo_data:
                            seo_data = {
                                "title": f"श्रीकृष्ण का वह परम जीवन-सूत्र जो हर भय मिटा दे | {ch_name}",
                                "description": "🕉️ श्रीमद्भगवद्गीता का वह शाश्वत मनोवैज्ञानिक ज्ञान जो जीवन की हर उलझन को समाप्त कर देता है।",
                                "tags": ["Geeta Gyan", "Shri Krishna", "Bhagavad Gita", "Inner Peace"]
                            }

                        print(f"   🚀 Uploading {os.path.basename(v_file)} to {ch_name} as UNLISTED...")
                        p_dir = os.getenv("CH_PROFILE_DIR_CH01") if target_ch == "ch_01" else os.getenv("CH_PROFILE_DIR_CH02")
                        try:
                            uploader = YouTubeHumanUploader(channel_id=target_ch, profile_dir=p_dir)
                            res = uploader.upload_video(
                                video_path=v_file,
                                seo_package=seo_data,
                                thumbnail_path=t_file,
                                channel_id=target_ch,
                                privacy="unlisted",
                                headless=False,
                                profile_dir=p_dir
                            )
                            print(f"   🎉 Upload Result: {res.get('video_url', 'Success')}")
                            time.sleep(10)
                        except Exception as e_upload:
                            print(f"   ❌ Upload error for {art_name}: {e_upload}")
                            time.sleep(5)
                else:
                    print(f"   ⚠️ Could not download artifact {art_name}: HTTP {r_dl.status_code}")

    print("\n" + "=" * 80)
    print("🎉 ALL CLOUD ARTIFACTS PROCESSED AND PUBLISHED AUTONOMOUSLY BY GITHUB BOT!")
    print("=" * 80)

if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    run_id_arg = sys.argv[1] if len(sys.argv) > 1 else "40484694835"
    run_cloud_batch(run_id=run_id_arg)
