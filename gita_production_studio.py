import os
import sys
import time
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "geeta wala")

import gita_downloader_core
import gita_studio_publisher
import gita_catalog_generator

def clear_screen():
    os.system("cls" if sys.platform == "win32" else "clear")

def print_banner():
    clear_screen()
    print("""
==================================================================================
                 🕉️ GITA PRODUCTION STUDIO v1.0 (OFFICIAL)
              Dual-Channel Autonomous Video & Publishing Suite
==================================================================================
 [Channels Configured]
  1. Geeta Gyan 60 Sec      (@GeetaGyan60Sec | UCw-3CNwReOnBF7__N6S4DQw)
  2. Geeta Jeevan Sutra     (@GeetaJeevanSutraHindi | UClptLNgnB7fxcmmgzuTXwvA)

 [Local Vault]: C:\\Users\\janar\\Downloads\\geeta wala
==================================================================================
""")

def menu():
    while True:
        print_banner()
        print(" [0] 🕉️ GENERATE HYPNOTIC MASTER VIDEO (Locked Prompt + AI Studio + Edge-TTS + Outro)")
        print(" [1] 🚀 FULL AUTOPILOT (Download 10 Videos + Upload 5-5 to Both Channels)")
        print(" [2] 📥 DOWNLOAD ONLY (Save 10 Master Packages to Downloads\\geeta wala)")
        print(" [3] 🎬 UPLOAD ONLY -> Channel 1 (Geeta Gyan 60 Sec - 5 Videos)")
        print(" [4] 🎬 UPLOAD ONLY -> Channel 2 (Geeta Jeevan Sutra - 5 Videos)")
        print(" [5] 📁 OPEN VAULT FOLDER in Windows Explorer")
        print(" [6] 🌐 OPEN VISUAL CATALOG (catalog.html in Web Browser)")
        print(" [7] ⚡ DISPATCH 10-VIDEO CLOUD BEAST (10 Parallel GitHub Actions Runners)")
        print(" [8] 🔑 INJECT & SYNC GOOGLE AI STUDIO API KEYS (Multi-Account Pool)")
        print(" [9] ❌ EXIT")
        print("=" * 82)
        
        choice = input(" 👉 Enter Choice [0-9]: ").strip()

        if choice == "0":
            import hypnotic_autonomous_pipeline
            ch_choice = input(" Choose target channel ([1] Geeta Gyan 60 Sec / [2] Geeta Jeevan Sutra): ").strip()
            target_ch = "ch_02" if ch_choice == "2" else "ch_01"
            custom_t = input(" Enter topic (or press Enter for autonomous wound selector): ").strip()
            topic = custom_t if custom_t else None
            hypnotic_autonomous_pipeline.run_hypnotic_pipeline(custom_topic=topic, target_channel=target_ch)
            input("\nPress Enter to return to menu...")

        if choice == "1":
            print("\n[*] Starting Step 1: Downloading all 10 packages to Downloads\\geeta wala...")
            gita_downloader_core.download_all_packages()
            print("\n[*] Starting Step 2: Uploading 5 videos to Ch1 and 5 videos to Ch2...")
            gita_studio_publisher.publish_both_channels()
            input("\nPress Enter to return to menu...")

        elif choice == "2":
            gita_downloader_core.download_all_packages()
            input("\nPress Enter to return to menu...")

        elif choice == "3":
            gita_studio_publisher.publish_channel("ch_01")
            input("\nPress Enter to return to menu...")

        elif choice == "4":
            gita_studio_publisher.publish_channel("ch_02")
            input("\nPress Enter to return to menu...")

        elif choice == "5":
            os.makedirs(TARGET_BASE_DIR, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(TARGET_BASE_DIR)
            print(f"✓ Opened {TARGET_BASE_DIR}")
            time.sleep(1)

        elif choice == "6":
            cat_path = os.path.join(TARGET_BASE_DIR, "catalog.html")
            if not os.path.exists(cat_path):
                gita_catalog_generator.generate_catalog()
            if sys.platform == "win32" and os.path.exists(cat_path):
                os.startfile(cat_path)
            print(f"✓ Opened {cat_path}")
            time.sleep(1)

        elif choice == "7":
            import master_cloud_10_orchestrator; master_cloud_10_orchestrator.run_10_video_pipeline()
            pass




            input("\nPress Enter to return to menu...")

        elif choice == "8":
            import inject_google_ai_keys; inject_google_ai_keys.interactive_injection()
            pass






            input("\nPress Enter to return to menu...")

        elif choice == "9":
            print("\n🕉️ Hare Krishna! Exiting Gita Production Studio.")
            break
        else:
            print("Invalid option. Please choose 1-9.")
            time.sleep(1)

if __name__ == "__main__":
    menu()
