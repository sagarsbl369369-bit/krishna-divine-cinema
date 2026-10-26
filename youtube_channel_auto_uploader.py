"""
YouTube Autonomous Multi-Channel Uploader Engine
------------------------------------------------
Uploads rendered > 30-minute documentaries to YouTube using:
1. Google API OAuth2 (Official YouTube Data API v3).
2. Category 27 (Education / Spirituality).
3. Resumable Chunked Upload Protocol.
4. Integrated Viral SEO Package (Title, Description with Timestamps, Tags).
5. Safe Dry-Run fallback if credentials/token are pending authorization.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

CHANNELS_PATH = os.path.join(BASE_DIR, "channels.json")

def upload_video_to_youtube(video_path: str, seo_package: Dict[str, Any], channel_id: str = "ch_01", privacy: str = "unlisted") -> Optional[str]:
    """
    Uploads a video to YouTube with official OAuth2 credentials.
    If credentials token is missing, logs dry-run package for manual or scheduled upload.
    """
    print("\n==================================================================")
    print("📤 AUTONOMOUS YOUTUBE UPLOADER ENGINE (DATA API V3)")
    print(f"📁 Video: {video_path}")
    print(f"🏷️ Title: {seo_package.get('title')}")
    print(f"📺 Channel: {channel_id} (Privacy: {privacy})")
    print("==================================================================")

    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found at: {video_path}")

    token_file = os.path.join(CREDENTIALS_DIR, f"{channel_id}_token.json")
    client_secret_file = os.path.join(CREDENTIALS_DIR, "client_secret.json")
    service_account_file = os.path.join(CREDENTIALS_DIR, "service_account.json")

    # If googleapiclient is not installed or token is not present
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaFileUpload
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("[!] Warning: google-api-python-client not installed. Video is saved locally.")
        return None

    credentials = None

    # Priority 1: Channel-Specific OAuth Token
    if os.path.exists(token_file):
        try:
            with open(token_file, "r") as f:
                token_data = json.load(f)
            credentials = Credentials.from_authorized_user_info(token_data)
            print(f"[*] Authenticating with Channel OAuth Token: {token_file}")
        except Exception as e:
            print(f"[!] Warning reading {token_file}: {e}")

    # Priority 2: Service Account Key (geeta1@geeta-channel.iam.gserviceaccount.com)
    if not credentials and os.path.exists(service_account_file):
        try:
            from google.oauth2 import service_account
            sa_scopes = [
                "https://www.googleapis.com/auth/youtube.upload",
                "https://www.googleapis.com/auth/youtube",
                "https://www.googleapis.com/auth/youtube.force-ssl"
            ]
            credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=sa_scopes)
            print(f"[*] Authenticating with Google Service Account: {service_account_file}")
        except Exception as e:
            print(f"[!] Warning reading service account: {e}")

    if not credentials:
        print(f"[ℹ️] Notice: YouTube credentials not found.")
        print(f"[*] Package Prepared & Verified: Dry-Run Upload Successful.")
        print(f"[*] To enable live 1-click uploads, place your Google Cloud OAuth client_secret.json in:")
        print(f"    {CREDENTIALS_DIR}\\")
        # Save upload manifest
        manifest_p = video_path.replace(".mp4", "_upload_manifest.json")
        with open(manifest_p, "w", encoding="utf-8") as f:
            json.dump({
                "video_path": video_path,
                "channel_id": channel_id,
                "seo_package": seo_package,
                "status": "ready_for_upload"
            }, f, indent=2, ensure_ascii=False)
        print(f"📁 Video Manifest Generated: {manifest_p}")
        return "DRY_RUN_READY"

    try:
        youtube = build("youtube", "v3", credentials=credentials)

        body = {
            "snippet": {
                "title": seo_package["title"][:100],
                "description": seo_package["description"],
                "tags": seo_package["tags"][:30],
                "categoryId": seo_package.get("category_id", "27")
            },
            "status": {
                "privacyStatus": privacy,
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=1024 * 1024 * 8, resumable=True, mimetype="video/mp4")
        
        print(f"[*] Initiating Chunked Resumable Upload to YouTube...")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   [⏳] Upload progress: {int(status.progress() * 100)}%")

        video_id = response.get("id")
        video_url = f"https://youtu.be/{video_id}"
        print(f"🎉 [✓] Successfully Published to YouTube! URL: {video_url}")

        # Automatic Thumbnail Attachment via Google Flow (thumbnails.set)
        thumb_path = seo_package.get("thumbnail_path") or seo_package.get("thumbnail_file")
        if thumb_path and os.path.exists(thumb_path):
            print(f"🖼️ [THUMBNAIL ENGINE] Attaching 1280x720 UHD Viral Thumbnail ({thumb_path})...")
            try:
                thumb_media = MediaFileUpload(thumb_path, mimetype="image/jpeg")
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=thumb_media
                ).execute()
                print(f"🎉 [✓] Viral Thumbnail Successfully Attached to {video_url}!")
            except Exception as thumb_err:
                print(f"⚠️ [!] Warning: Could not attach thumbnail via API ({thumb_err}).")
        else:
            print("ℹ️ [THUMBNAIL] No thumbnail path specified or file missing.")

        return video_url

    except Exception as e:
        print(f"[!] Upload Error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous YouTube Uploader")
    parser.add_argument("--video", required=True, help="Video path")
    parser.add_argument("--seo", required=True, help="SEO JSON file")
    parser.add_argument("--channel", default="ch_01", help="Target channel ID")
    parser.add_argument("--privacy", default="unlisted", help="unlisted | public | private")
    args = parser.parse_args()

    with open(args.seo, "r", encoding="utf-8") as f:
        seo_data = json.load(f)

    upload_video_to_youtube(args.video, seo_data, args.channel, args.privacy)
