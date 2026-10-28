import os
import sys
import json
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "geeta wala")
MANIFEST_PATH = os.path.join(TARGET_BASE_DIR, "upload_manifest_live.json")

from youtube_human_uploader import YouTubeHumanUploader

def get_channel_packages(channel_dir):
    packages = []
    if not os.path.exists(channel_dir):
        return packages
    for item in sorted(os.listdir(channel_dir)):
        p = os.path.join(channel_dir, item)
        if not os.path.isdir(p):
            continue
        v_file = os.path.join(p, "master_1080p_documentary.mp4")
        t_file = os.path.join(p, "thumbnail_uhd.jpg")
        s_file = os.path.join(p, "seo_package.json")
        if os.path.exists(v_file):
            packages.append({
                "folder": item,
                "video_path": v_file,
                "thumb_path": t_file if os.path.exists(t_file) else None,
                "seo_path": s_file if os.path.exists(s_file) else None
            })
    return packages

def publish_channel(channel_key: str = "ch_01"):
    ch_name = "Geeta Gyan 60 Sec" if channel_key == "ch_01" else "Geeta Jeevan Sutra"
    ch_folder = "Channel_01_GeetaGyan60Sec" if channel_key == "ch_01" else "Channel_02_GeetaJeevanSutra"
    full_ch_dir = os.path.join(TARGET_BASE_DIR, ch_folder)

    print("\n" + "=" * 75)
    print(f"🎬 GITA PRODUCTION STUDIO — PUBLISHING TO [{ch_name}]")
    print(f"📁 Source Folder: {full_ch_dir}")
    print("=" * 75)

    packages = get_channel_packages(full_ch_dir)
    if not packages:
        print(f"⚠️ No video packages found in {full_ch_dir}. Please run download first!")
        return False

    print(f"✓ Found {len(packages)} videos ready for upload to {ch_name}.")

    uploader = YouTubeHumanUploader(channel_id=channel_key)
    
    # Check if logged in; if not, launch interactive login
    if not uploader.is_logged_in():
        print(f"\n[*] Login required for {ch_name}. Opening interactive Chrome...")
        success = uploader.launch_session_login(channel_id=channel_key)
        if not success:
            print("❌ Login not completed. Aborting upload.")
            return False

    results = []
    for idx, pkg in enumerate(packages, 1):
        print("\n" + "-" * 70)
        print(f"🚀 [{idx}/{len(packages)}] Uploading: {pkg['folder']} -> {ch_name}")
        print("-" * 70)

        seo_data = {}
        if pkg["seo_path"] and os.path.exists(pkg["seo_path"]):
            try:
                with open(pkg["seo_path"], "r", encoding="utf-8") as sf:
                    seo_data = json.load(sf)
            except Exception:
                pass

        if not seo_data:
            seo_data = {
                "title": pkg["folder"].replace("_", " ") + " | " + ch_name,
                "description": "🕉️ श्रीमद्भगवद्गीता का वह शाश्वत मनोवैज्ञानिक ज्ञान जो जीवन की हर आंतरिक उलझन को शांत कर देता है।",
                "tags": ["Bhagavad Gita", "Shri Krishna", "Geeta Gyan", "Inner Peace", "Mental Strength"]
            }

        try:
            res = uploader.upload_video(
                video_path=pkg["video_path"],
                seo_package=seo_data,
                thumbnail_path=pkg["thumb_path"],
                channel_id=channel_key,
                privacy="unlisted",
                headless=False
            )
            v_url = res.get("video_url", "Success")
            print(f"🎉 Upload Result: {v_url}")
            results.append({
                "channel": ch_name,
                "folder": pkg["folder"],
                "video_url": v_url,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })

            # Save manifest incrementally
            existing = []
            if os.path.exists(MANIFEST_PATH):
                try:
                    with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
                        existing = json.load(mf)
                except Exception:
                    existing = []
            existing.extend(results)
            with open(MANIFEST_PATH, "w", encoding="utf-8") as mf:
                json.dump(existing, mf, ensure_ascii=False, indent=2)

            time.sleep(5)
        except Exception as e:
            print(f"❌ Upload error for {pkg['folder']}: {e}")

    print("\n" + "=" * 75)
    print(f"🎉 COMPLETED UPLOADS FOR [{ch_name}]!")
    print("=" * 75)
    return True

def publish_both_channels():
    print("\n" + "=" * 80)
    print("🕉️ GITA PRODUCTION STUDIO — DUAL CHANNEL AUTOPILOT (10 VIDEOS)")
    print("=" * 80)
    
    # 1. Channel 1 (5 videos)
    publish_channel("ch_01")
    
    # 2. Channel 2 (5 videos)
    publish_channel("ch_02")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"
    if mode == "ch_01":
        publish_channel("ch_01")
    elif mode == "ch_02":
        publish_channel("ch_02")
    else:
        publish_both_channels()
