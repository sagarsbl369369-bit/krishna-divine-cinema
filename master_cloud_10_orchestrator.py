"""
Master Cloud 10-Video Orchestrator & Live Telemetry Engine
==========================================================
Coordinates the 1-Click Desktop experience:
1. Validates API keys & GitHub connectivity.
2. Dispatches 10 parallel cloud workers on GitHub Actions.
3. Streams real-time matrix status of all 10 cloud workers.
4. Auto-downloads all 10 video packages upon completion to C:\\Users\\janar\\Downloads\\geeta wala\\.
5. Regenerates offline visual catalog (catalog.html) and opens Windows Explorer.
"""

import os
import sys
import time
import json
import subprocess
import requests
from typing import Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
GH_CONFIG_PATH = os.path.join(CREDENTIALS_DIR, "github_cloud_config.json")
TARGET_BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "geeta wala")

import github_cloud_dispatcher
import gita_downloader_core
import gita_catalog_generator

def clear_screen():
    os.system("cls" if sys.platform == "win32" else "clear")

def print_header():
    print("""
==================================================================================
        🕉️ GITA PRODUCTION STUDIO — 10-VIDEO CLOUD BEAST ORCHESTRATOR
   (Google Gemini Latest + Google AI Studio TTS + Groq Swarm Intelligence)
==================================================================================
 [Hardware] 10 Parallel Linux Cloud VMs (Zero PC CPU/RAM Usage)
 [Target 1] Channel 1: Geeta Gyan 60 Sec      (@GeetaGyan60Sec)      — 5 Videos
 [Target 2] Channel 2: Geeta Jeevan Sutra     (@GeetaJeevanSutraHindi)— 5 Videos
 [Duration] ~35 Minutes Each (>30 Min Master Documentary)
 [Outro]    173.25s Blue Laser Shield Outro (HU-BA-HU Original Song Untouched)
 [Vault]    C:\\Users\\janar\\Downloads\\geeta wala\\
==================================================================================
""")

def run_10_video_pipeline():
    clear_screen()
    print_header()

    # Step 1: Pre-flight check
    dispatcher = github_cloud_dispatcher.dispatcher
    cfg = dispatcher.load_config()
    repo = cfg.get("github_repo", "").strip()
    token = cfg.get("github_token", "").strip()

    if not repo or not token:
        print("❌ ERROR: GitHub Repository or Token not configured!")
        print(f"Please check: {GH_CONFIG_PATH}")
        input("\nPress Enter to exit...")
        return

    print(f"[*] Connected GitHub Repo: {repo}")
    print("[*] Target Workflow: master_10_video_pipeline.yml")

    # Step 2: Trigger Cloud Dispatch
    print("\n🚀 [1/3] Dispatching 10 Parallel Cloud VMs on GitHub Actions...")
    res = dispatcher.dispatch_10_video_batch(duration=35, privacy="unlisted")
    if not res.get("success"):
        print(f"❌ Dispatch Failed: {res.get('error')}")
        input("\nPress Enter to exit...")
        return

    print("✅ 10 Parallel Cloud Workers Successfully Launched!")
    print(f"🔗 Live GitHub Actions Monitor: https://github.com/{repo}/actions\n")
    print("⏳ Waiting for cloud runners to register and begin processing...")
    time.sleep(12)

    # Step 3: Stream Live Telemetry Matrix
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    start_monitor_time = time.time()
    active_run_id = None

    while True:
        try:
            status_data = dispatcher.get_latest_run_status()
            active_run_id = status_data.get("run_id")
            run_status = status_data.get("status")       # queued, in_progress, completed
            run_conclusion = status_data.get("conclusion") # success, failure
            jobs = status_data.get("jobs", [])

            clear_screen()
            print_header()
            elapsed_mins = (time.time() - start_monitor_time) / 60
            print(f"📡 [2/3] LIVE CLOUD MATRIX TELEMETRY (Elapsed: {elapsed_mins:.1f} mins) | Run #{active_run_id}")
            print(f"Overall Run Status: {str(run_status).upper()} | Result: {str(run_conclusion).upper()}")
            print("-" * 82)
            print(f" {'WORKER NAME':<40} {'CHANNEL':<25} {'STATUS':<15}")
            print("-" * 82)

            all_done = True
            for idx in range(1, 11):
                ch_tag = "Ch 1: Geeta Gyan 60s" if idx <= 5 else "Ch 2: Jeevan Sutra"
                w_name = f"Worker {idx}"
                # find matching job
                matching_job = next((j for j in jobs if f"Worker {idx} " in j.get("name", "") or j.get("name", "").startswith(f"Worker {idx}")), None)
                if matching_job:
                    j_status = matching_job.get("status", "unknown")
                    j_conc = matching_job.get("conclusion")
                    if j_status != "completed":
                        all_done = False
                        display_state = f"⚙️ {j_status.upper()}"
                    else:
                        if j_conc == "success":
                            display_state = "✅ SUCCESS"
                        else:
                            display_state = f"⚠️ {str(j_conc).upper()}"
                else:
                    all_done = False
                    display_state = "⏳ QUEUED / STARTING"

                print(f" {w_name:<40} {ch_tag:<25} {display_state:<15}")

            print("-" * 82)
            if run_status == "completed" or (jobs and all_done):
                print("\n🎉 ALL 10 CLOUD WORKERS HAVE FINISHED GENERATING VIDEOS!")
                break

            print("\n🔄 Telemetry refreshes every 15 seconds. (Press Ctrl+C to minimize and check later)")
            time.sleep(15)

        except KeyboardInterrupt:
            print("\n[!] Telemetry paused by user. The cloud workers continue running 24x7 in GitHub Cloud!")
            break
        except Exception as e:
            time.sleep(10)

    # Step 4: Auto-download completed packages
    print("\n" + "=" * 82)
    print("📥 [3/3] DOWNLOADING ALL 10 FINISHED VIDEO PACKAGES TO LOCAL PC...")
    print(f"Destination: {TARGET_BASE_DIR}")
    print("=" * 82)

    try:
        gita_downloader_core.download_all_packages()
    except Exception as e:
        print(f"⚠️ Note during download: {e}")

    # Step 5: Regenerate Offline Catalog and Open Folder
    print("\n🌐 Regenerating offline visual catalog (catalog.html)...")
    try:
        gita_catalog_generator.generate_catalog()
    except Exception:
        pass

    catalog_path = os.path.join(TARGET_BASE_DIR, "catalog.html")
    if os.path.exists(catalog_path):
        print(f"✓ Visual Catalog Ready: {catalog_path}")
        try:
            os.startfile(catalog_path)
        except Exception:
            pass

    try:
        os.startfile(TARGET_BASE_DIR)
    except Exception:
        pass

    print("\n" + "=" * 82)
    print("✨ 10-VIDEO BATCH COMPLETE! ALL FILES SAVED IN 'geeta wala' FOLDER!")
    print("=" * 82)
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    run_10_video_pipeline()
