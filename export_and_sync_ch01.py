import os
import sys
import json
import time
import tarfile
import subprocess
from cryptography.fernet import Fernet
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
KEY_FILE = os.path.join(CREDENTIALS_DIR, "fernet_master_key.txt")
PROFILE_DIR = os.path.join(CREDENTIALS_DIR, "youtube_browser_profile")
ST_PATH = os.path.join(CREDENTIALS_DIR, "storage_state_ch_01.json")

def export_and_sync():
    print("=" * 70)
    print("🔐 SMART YOUTUBE STUDIO LOGIN & CLOUD SYNC (CHANNEL 1)")
    print("=" * 70)
    
    # 1. Kill any stray chrome using this profile
    print("[*] Ensuring profile is free...")
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["powershell", "-Command", "Get-CimInstance Win32_Process -Filter \"Name = 'chrome.exe'\" | Where-Object { $_.CommandLine -like '*youtube_browser_profile*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }"],
                capture_output=True, timeout=10
            )
        except Exception:
            pass
    time.sleep(1)

    # 2. Launch interactive Chrome with Playwright
    print("[*] Launching Chrome on your screen...")
    target_studio_url = "https://studio.youtube.com/channel/UCw-3CNwReOnBF7__N6S4DQw/videos"
    
    with sync_playwright() as p:
        try:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=False,
                channel="chrome",
                args=[
                    "--no-first-run",
                    "--no-default-browser-check",
                    "--disable-blink-features=AutomationControlled"
                ],
                viewport={"width": 1280, "height": 800}
            )
        except Exception as e:
            print(f"[!] Standard Chrome launch failed ({e}), using default Chromium...")
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                viewport={"width": 1280, "height": 800}
            )

        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(target_studio_url, timeout=45000)

        # Check if already in Studio
        def check_logged_in(u):
            return "studio.youtube.com" in u and "signin" not in u and "accountchooser" not in u

        if check_logged_in(page.url):
            print("\n🎉 ALREADY LOGGED IN! YouTube Studio is open and active.")
        else:
            print("\n" + "=" * 70)
            print("👉 GOOGLE SIGN-IN REQUIRED ON YOUR SCREEN:")
            print("   1. In the Chrome window that just opened, click on 'Sagar'")
            print("   2. Enter your password for sagarsbl369369@gmail.com")
            print("   3. Approve on phone if prompted (2FA).")
            print("   -> As soon as YouTube Studio appears, THIS SCRIPT AUTO-DETECTS IT!")
            print("=" * 70)

            # Auto-detection loop
            start_wait = time.time()
            max_wait = 300  # 5 minutes
            logged_in = False

            while time.time() - start_wait < max_wait:
                time.sleep(2)
                try:
                    current_url = page.url
                    if check_logged_in(current_url):
                        print("\n🎉 LOGIN DETECTED! YouTube Studio Dashboard is now LIVE on your screen!")
                        logged_in = True
                        time.sleep(3)  # Let cookies settle
                        break
                    else:
                        remaining = int(max_wait - (time.time() - start_wait))
                        print(f"\r[*] Waiting for you to complete sign-in... ({remaining}s remaining)", end="", flush=True)
                except Exception:
                    pass

            if not logged_in:
                print("\n❌ Sign-in timeout. Please run the script again when ready.")
                ctx.close()
                return False

        # 3. Save fresh storage state
        print("\n[*] Saving fresh storage state & active cookies...")
        ctx.storage_state(path=ST_PATH)
        ctx.close()

    print(f"✓ Saved fresh storage state to {ST_PATH} ({os.path.getsize(ST_PATH)} bytes)")

    # 4. Verify cookie freshness
    with open(ST_PATH, "r", encoding="utf-8") as f:
        st_data = json.load(f)
    cookies = st_data.get("cookies", [])
    has_sid = any("SID" in c.get("name", "") for c in cookies)
    print(f"✓ Verified {len(cookies)} cookies (Active: {has_sid})")

    # 5. Encrypt profile and storage state
    with open(KEY_FILE, "r") as kf:
        key = kf.read().strip()
    fernet = Fernet(key)

    def filter_cache(tarinfo):
        name = tarinfo.name.lower()
        if any(skip in name for skip in [
            "cache", "code cache", "dawncache", "gpucache",
            "service worker", "media cache", ".blob", ".pma", "dump"
        ]):
            return None
        return tarinfo

    print("[*] Compressing profile_ch_01.tar.gz...")
    tar_path = os.path.join(CREDENTIALS_DIR, "profile_ch_01.tar.gz")
    enc_path = os.path.join(CREDENTIALS_DIR, "profile_ch_01.tar.gz.enc")
    
    with tarfile.open(tar_path, "w:gz") as tar:
        for item in os.listdir(PROFILE_DIR):
            tar.add(os.path.join(PROFILE_DIR, item), arcname=item, filter=filter_cache)

    print("[*] Encrypting profile_ch_01.tar.gz.enc...")
    with open(tar_path, "rb") as f_in:
        enc_data = fernet.encrypt(f_in.read())
    with open(enc_path, "wb") as f_out:
        f_out.write(enc_data)
    os.remove(tar_path)
    print(f"   ✓ Encrypted profile: {len(enc_data)/1024/1024:.2f} MB")

    # Encrypt storage_state
    print("[*] Encrypting storage_state_ch_01.json.enc...")
    with open(ST_PATH, "rb") as f_in:
        enc_st = fernet.encrypt(f_in.read())
    with open(os.path.join(CREDENTIALS_DIR, "storage_state_ch_01.json.enc"), "wb") as f_out:
        f_out.write(enc_st)
    print(f"   ✓ Encrypted storage state: {len(enc_st)} bytes")

    # 6. Git Push to GitHub
    print("[*] Pushing encrypted credentials to GitHub repository (main)...")
    subprocess.run(["git", "add", "credentials/*.enc", "youtube_human_uploader.py"], cwd=BASE_DIR, check=True)
    subprocess.run(["git", "commit", "-m", "chore(auth): refresh Channel 1 verified active session and cookies"], cwd=BASE_DIR, check=True)
    subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=True)
    print("✓ Successfully synced verified credentials to GitHub!")

    # 7. Dispatch Cloud Batch Uploader
    print("[*] Triggering Cloud Batch Uploader for 9 master documentary videos...")
    import trigger_cloud_batch
    run_id = trigger_cloud_batch.trigger_batch("40514508384")
    print(f"\n🎉 SUCCESS! GitHub Actions Run ID {run_id} is now uploading all 9 videos in the cloud!")
    return True

if __name__ == "__main__":
    export_and_sync()
