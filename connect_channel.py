"""
🕉️ Direct YouTube Channel CLI Connector
========================================
Run this script to connect YouTube channels via Google OAuth:
Usage:
  python connect_channel.py ch_01
  python connect_channel.py ch_02
"""

import os
import sys
import json
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
CLIENT_SECRET_PATH = os.path.join(CREDENTIALS_DIR, "client_secret.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def main():
    print("=" * 65)
    print("🕉️ GITA STUDIO — DIRECT YOUTUBE CHANNEL CONNECTOR")
    print("=" * 65)

    if not os.path.exists(CLIENT_SECRET_PATH):
        print(f"[❌ ERROR] client_secret.json not found in:\n  {CLIENT_SECRET_PATH}")
        print("Please ensure your Google Cloud OAuth client_secret.json is installed.")
        return

    try:
        with open(CLIENT_SECRET_PATH, "r", encoding="utf-8") as f:
            sec = json.load(f)
            client_id = sec.get("installed", {}).get("client_id") or sec.get("web", {}).get("client_id")
            print(f"[✓] client_secret.json Verified!")
            print(f"    Client ID: {client_id[:40]}...")
    except Exception as e:
        print(f"[❌ ERROR] Invalid client_secret.json: {e}")
        return

    # Determine channel
    channel_id = "ch_01"
    if len(sys.argv) > 1 and sys.argv[1].strip() in ["ch_01", "ch_02"]:
        channel_id = sys.argv[1].strip()
    else:
        print("\nचैनल चुनें जिसे आप Google से कनेक्ट करना चाहते हैं:")
        print("  [1] Channel 1: दिव्य गीता वाणी (ch_01)")
        print("  [2] Channel 2: परम कृष्ण चेतना (ch_02)")
        choice = input("Enter 1 or 2 [Default 1]: ").strip()
        if choice == "2":
            channel_id = "ch_02"

    ch_label = "चैनल १: दिव्य गीता वाणी" if channel_id == "ch_01" else "चैनल २: परम कृष्ण चेतना"
    print(f"\n🚀 Connecting: {ch_label} ({channel_id})...")
    print("🌐 Opening Google Sign-in in your default browser...")
    print("👉 If Google displays 'Google hasn't verified this app':")
    print("   Click: 'Advanced' ➔ 'Go to geeta-channel (unsafe)' ➔ 'Continue / Allow'")
    print("-" * 65)

    from google_auth_oauthlib.flow import InstalledAppFlow

    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_PATH,
            scopes=SCOPES
        )
        credentials = flow.run_local_server(
            port=8085,
            prompt="consent",
            authorization_prompt_message="Waiting for authorization in browser...",
            success_message="Authentication Successful! You can close this tab and return to the terminal."
        )

        token_data = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token,
            "token_uri": credentials.token_uri,
            "client_id": credentials.client_id,
            "client_secret": credentials.client_secret,
            "scopes": credentials.scopes
        }

        token_path = os.path.join(CREDENTIALS_DIR, f"{channel_id}_token.json")
        with open(token_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

        print(f"\n🎉 [SUCCESS] Token saved successfully at:\n  {token_path}")

        # Live verification with YouTube API
        from googleapiclient.discovery import build
        youtube = build("youtube", "v3", credentials=credentials)
        res = youtube.channels().list(part="snippet,statistics", mine=True).execute()
        items = res.get("items", [])
        if items:
            title = items[0].get("snippet", {}).get("title")
            subs = items[0].get("statistics", {}).get("subscriberCount", "0")
            vids = items[0].get("statistics", {}).get("videoCount", "0")
            print("=" * 65)
            print(f"📺 LIVE CHANNEL VERIFIED:")
            print(f"   Name:        {title}")
            print(f"   Subscribers: {int(subs):,}")
            print(f"   Total Videos: {vids}")
            print(f"   Status:      ✅ CONNECTED & ACTIVE")
            print("=" * 65)
        else:
            print("[✓] Connected! (No public channel metadata found)")

    except Exception as e:
        print(f"\n[❌ ERROR] Connection failed: {e}")
        if "access_denied" in str(e).lower():
            print("\n💡 HOW TO FIX 'Access Denied / App in Testing':")
            print("1. Go to: https://console.cloud.google.com/apis/credentials/consent")
            print("2. Under 'Test users', click '+ ADD USERS'")
            print("3. Enter your YouTube channel Gmail and click SAVE.")
            print("4. Re-run: python connect_channel.py")

if __name__ == "__main__":
    main()
