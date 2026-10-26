"""
YouTube Multi-Channel Auto Uploader Engine
Supports:
1. Google API OAuth2 (Official YouTube Data API v3)
2. Channel rotation and metadata optimization (Tags, Description, Titles)
"""

import os
import sys
import json
import argparse
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

def upload_video_api(channel_id: str, video_path: str, title: str, description: str, tags: list):
    """
    Uploads a video to YouTube using OAuth2 credentials stored per channel.
    Credentials file: credentials/{channel_id}_token.json
    """
    token_file = os.path.join("credentials", f"{channel_id}_token.json")
    if not os.path.exists(token_file):
        print(f"[!] Warning: Token file not found for {channel_id} at {token_file}")
        print(f"[*] Skipping live upload (Dry-Run mode for testing).")
        return None

    with open(token_file, "r") as f:
        token_data = json.load(f)

    credentials = Credentials.from_authorized_user_info(token_data)
    youtube = build("youtube", "v3", credentials=credentials)

    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27"  # Education / Spirituality
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    
    print(f"[*] Uploading {video_path} to YouTube Channel: {channel_id}...")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media
    )
    
    response = request.execute()
    video_id = response.get("id")
    print(f"[✓] Successfully Uploaded! Video URL: https://youtu.be/{video_id}")
    return video_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Channel Uploader")
    parser.add_argument("--channel", required=True, help="Channel ID (e.g., ch_01)")
    parser.add_argument("--video", required=True, help="Path to MP4 file")
    parser.add_argument("--title", default="Bhagavad Gita Saar | Shri Krishna Updesh", help="Video Title")
    parser.add_argument("--desc", default="Shrimad Bhagavad Gita Anmol Gyan & Life Lessons #BhagavadGita #Krishna", help="Description")
    
    args = parser.parse_args()
    upload_video_api(args.channel, args.video, args.title, args.desc, ["Bhagavad Gita", "Krishna", "Motivation"])
