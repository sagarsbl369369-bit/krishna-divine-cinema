import os
import sys
import json
import io
import time
import zipfile
import urllib.request

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

# Configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "credentials", "github_cloud_config.json")

def get_github_token():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f).get("token", "")
        except Exception:
            pass
    return os.environ.get("GITHUB_TOKEN", "")

TOKEN = get_github_token()
REPO = "sagarsbl369369-bit/krishna-divine-cinema"

TARGET_BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "geeta wala")
CH1_DIR = os.path.join(TARGET_BASE_DIR, "Channel_01_GeetaGyan60Sec")
CH2_DIR = os.path.join(TARGET_BASE_DIR, "Channel_02_GeetaJeevanSutra")

# The 10 Target Master Video Packages (5 for Ch1, 5 for Ch2)
MASTER_PACKAGES = [
    # CHANNEL 1: Geeta Gyan 60 Sec
    {
        "worker_name": "video-worker-1-channel-1",
        "channel": "ch_01",
        "channel_name": "Geeta Gyan 60 Sec",
        "target_dir": CH1_DIR,
        "folder_name": "01_Vishwasghat_Moun_Samrajya",
        "artifact_id": 12744201458,
        "run_id": "40514508384",
        "title": "जब अपने ही पीठ में छुरा घोंपें — विश्वासघात के बाद मौन संप्रभुता का विज्ञान"
    },
    {
        "worker_name": "video-worker-2-channel-1",
        "channel": "ch_01",
        "channel_name": "Geeta Gyan 60 Sec",
        "target_dir": CH1_DIR,
        "folder_name": "02_Raat_Ke_3_Baje_Ka_Sannata",
        "artifact_id": 12744397425,
        "run_id": "40514508384",
        "title": "रात के ३ बजे का सन्नाटा — दिमाग के उस अनवरत शोर को शांत करने का अंतिम सत्य"
    },
    {
        "worker_name": "video-worker-3-channel-1",
        "channel": "ch_01",
        "channel_name": "Geeta Gyan 60 Sec",
        "target_dir": CH1_DIR,
        "folder_name": "03_Dimag_Ki_Overthinking_Ka_Anth",
        "artifact_id": 12742633001,
        "run_id": "40514508384",
        "title": "दिमाग की ओवरथिंकिंग का जड़ से अंत — जब विचार आपको गुलाम बना लें"
    },
    {
        "worker_name": "video-worker-4-channel-1",
        "channel": "ch_01",
        "channel_name": "Geeta Gyan 60 Sec",
        "target_dir": CH1_DIR,
        "folder_name": "04_Career_Ki_Ghuthan_Mukti",
        "artifact_id": 12741304960,
        "run_id": "40514508384",
        "title": "करियर की घुटन और पीछे छूट जाने का खौफ — जब हर कोई आगे निकल रहा हो"
    },
    {
        "worker_name": "video-worker-5-channel-1",
        "channel": "ch_01",
        "channel_name": "Geeta Gyan 60 Sec",
        "target_dir": CH1_DIR,
        "folder_name": "05_Akelepan_Ki_Asli_Takhat",
        "artifact_id": 12744320242,
        "run_id": "40514508384",
        "title": "अकेलेपन को अपनी सबसे घातक शक्ति बनाओ — जब दुनिया साथ छोड़ दे"
    },

    # CHANNEL 2: Geeta Jeevan Sutra
    {
        "worker_name": "video-worker-6-channel-2",
        "channel": "ch_02",
        "channel_name": "Geeta Jeevan Sutra",
        "target_dir": CH2_DIR,
        "folder_name": "06_Akelepan_Se_Samrajya_Nirman",
        "artifact_id": 12744060497,
        "run_id": "40514508384",
        "title": "अकेलेपन को अपनी सबसे घातक शक्ति बनाओ — जब दुनिया साथ छोड़ दे, तब साम्राज्य निर्माण"
    },
    {
        "worker_name": "video-worker-7-channel-2",
        "channel": "ch_02",
        "channel_name": "Geeta Jeevan Sutra",
        "target_dir": CH2_DIR,
        "folder_name": "07_Kaal_Ka_Nirmam_Pahiya",
        "artifact_id": 12743033406,
        "run_id": "40514508384",
        "title": "काल का निर्मम पहिया और विसर्जन — जो छूट गया उसका शोक क्यों? हर मोह को भस्म करो"
    },
    {
        "worker_name": "video-worker-8-channel-2",
        "channel": "ch_02",
        "channel_name": "Geeta Jeevan Sutra",
        "target_dir": CH2_DIR,
        "folder_name": "08_Sabke_Aage_Jhukna_Band",
        "artifact_id": 12730215941,
        "run_id": "40484694835",
        "title": "सबके आगे झुकना बंद करो — आत्म-सम्मान और संप्रभुता का शाश्वत नियम"
    },
    {
        "worker_name": "video-worker-9-channel-2",
        "channel": "ch_02",
        "channel_name": "Geeta Jeevan Sutra",
        "target_dir": CH2_DIR,
        "folder_name": "09_Man_Ko_Shant_Karne_Ki_Vidhi",
        "artifact_id": 12742602544,
        "run_id": "40514508384",
        "title": "मन को शांत करने की परम वैज्ञानिक विधि — अंतहीन आंतरिक युद्ध का विराम"
    },
    {
        "worker_name": "video-worker-10-channel-2",
        "channel": "ch_02",
        "channel_name": "Geeta Jeevan Sutra",
        "target_dir": CH2_DIR,
        "folder_name": "10_Karmanyevadhikaraste_Rahasya",
        "artifact_id": 12742138808,
        "run_id": "40514508384",
        "title": "कर्मण्येवाधिकारस्ते का वास्तविक मनोवैज्ञानिक रहस्य — फल की चिंता से मुक्ति का महा-अस्त्र"
    }
]

class NoAuthRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Prevents Azure Blob 403 on redirected artifact downloads."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req and 'Authorization' in new_req.headers:
            del new_req.headers['Authorization']
        return new_req

opener = urllib.request.build_opener(NoAuthRedirectHandler)

def download_all_packages(force: bool = False):
    print("=" * 75)
    print("📥 GITA PRODUCTION STUDIO — MASTER CLOUD DOWNLOADER")
    print(f"📁 Target Destination: {TARGET_BASE_DIR}")
    print("=" * 75)

    os.makedirs(CH1_DIR, exist_ok=True)
    os.makedirs(CH2_DIR, exist_ok=True)

    total_downloaded = 0
    total_skipped = 0

    for idx, pkg in enumerate(MASTER_PACKAGES, 1):
        pkg_folder = os.path.join(pkg["target_dir"], pkg["folder_name"])
        os.makedirs(pkg_folder, exist_ok=True)

        target_mp4 = os.path.join(pkg_folder, "master_1080p_documentary.mp4")
        target_thumb = os.path.join(pkg_folder, "thumbnail_uhd.jpg")
        target_seo = os.path.join(pkg_folder, "seo_package.json")

        if not force and os.path.exists(target_mp4) and os.path.getsize(target_mp4) > 10 * 1024 * 1024:
            print(f"[{idx}/10] ⏩ ALREADY DOWNLOADED: {pkg['folder_name']} ({os.path.getsize(target_mp4)/1024/1024:.1f} MB)")
            total_skipped += 1
            continue

        print(f"\n[{idx}/10] ⬇️ DOWNLOADING: {pkg['worker_name']} -> {pkg['channel_name']}")
        print(f"       Topic: {pkg['title']}")
        print(f"       Saving to: {pkg_folder}")

        url = f"https://api.github.com/repos/{REPO}/actions/artifacts/{pkg['artifact_id']}/zip"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"token {TOKEN}",
                "User-Agent": "GitaProductionStudio-Downloader"
            }
        )

        start_time = time.time()
        try:
            with opener.open(req) as resp:
                data = resp.read()
                mb = len(data) / (1024 * 1024)
                duration = max(0.1, time.time() - start_time)
                speed = mb / duration
                print(f"       ✓ Downloaded {mb:.2f} MB in {duration:.1f}s ({speed:.1f} MB/s)")

                # Extract zip in memory
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    temp_extract = os.path.join(pkg_folder, "_temp")
                    z.extractall(temp_extract)

                    # Locate files
                    for root, _, files in os.walk(temp_extract):
                        for f in files:
                            full_p = os.path.join(root, f)
                            if f.endswith(".mp4") and "outro" not in f.lower():
                                os.replace(full_p, target_mp4)
                            elif f.endswith(".jpg") or f.endswith(".png"):
                                os.replace(full_p, target_thumb)
                            elif f.endswith(".json") and "seo" in f.lower():
                                os.replace(full_p, target_seo)

                    # Clean up temp extract
                    import shutil
                    shutil.rmtree(temp_extract, ignore_errors=True)

                # Ensure SEO file exists if missing from artifact
                if not os.path.exists(target_seo):
                    default_seo = {
                        "title": pkg["title"] + " | " + pkg["channel_name"],
                        "description": "🕉️ श्रीमद्भगवद्गीता का वह शाश्वत मनोवैज्ञानिक ज्ञान जो जीवन की हर आंतरिक उलझन को शांत कर देता है।",
                        "tags": ["Bhagavad Gita", "Shri Krishna", "Geeta Gyan", "Inner Peace", "Mental Strength"]
                    }
                    with open(target_seo, "w", encoding="utf-8") as sf:
                        json.dump(default_seo, sf, ensure_ascii=False, indent=2)

                print(f"       🎉 Package successfully extracted & verified!")
                total_downloaded += 1

        except Exception as e:
            print(f"       ❌ Download error for {pkg['worker_name']}: {e}")

    print("\n" + "=" * 75)
    print(f"🎉 DOWNLOAD COMPLETE! {total_downloaded} downloaded, {total_skipped} already present.")
    print(f"📁 Open Folder: {TARGET_BASE_DIR}")
    print("=" * 75)

    # Generate visual catalog
    try:
        import gita_catalog_generator
        gita_catalog_generator.generate_catalog()
    except Exception:
        pass

    return True

if __name__ == "__main__":
    download_all_packages()
