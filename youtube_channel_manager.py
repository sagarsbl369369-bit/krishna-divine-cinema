"""
YouTube Dual-Channel Studio Manager & OAuth2 Authentication Engine
------------------------------------------------------------------
Manages multi-channel authentication, studio token verification, and automated channel rotation:
- Channel 1 (ch_01): Focuses on Mind Control, Overthinking & Daily Karma Motivation
- Channel 2 (ch_02): Focuses on Cosmic Truth, Death of Death, Maya & Supreme Awakening
Supports:
1. Interactive OAuth2 Localhost Login (Port 8085)
2. Manual Auth URL + Verification Code flow (for remote/headless setups)
3. Direct Token JSON / Client Secret paste in Dashboard
4. Live Channel Status (Channel Name, Avatar, Subscriber Count verification)
5. Autonomous Channel Alternation / Round-Robin Scheduling
"""

import os
import sys
import json
import time
import threading
import webbrowser
import wsgiref.simple_server
from typing import Dict, Any, List, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import (
    InstalledAppFlow,
    _RedirectWSGIApp,
    _ExclusiveWSGIServer,
    _WSGIRequestHandler
)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

CHANNELS_CONFIG_PATH = os.path.join(BASE_DIR, "channels.json")
CLIENT_SECRET_PATH = os.path.join(CREDENTIALS_DIR, "client_secret.json")
ROTATION_STATE_PATH = os.path.join(BASE_DIR, "renders", "channel_rotation_state.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

_active_oauth = {
    "server": None,
    "thread": None,
    "channel_id": None,
    "auth_url": None,
    "status": "idle"
}

DEFAULT_CHANNELS = [
    {
        "channel_id": "ch_01",
        "channel_name": "चैनल १: दिव्य गीता वाणी",
        "niche": "चित्त की शांति, अति-विचार से मुक्ति, जीवन प्रबंधन व कर्मयोग",
        "archetype_focus": ["चित्त की चंचलता और अति-विचार", "विषाद, अकेलापन और जीवन में सब खत्म हो जाना", "कर्म की निर्दयी नियति और फल की आसक्ति"],
        "token_file": "ch_01_token.json",
        "tags": ["Bhagavad Gita", "Krishna Vani", "Geeta Updesh", "Mind Control", "Karma Yoga", "Inner Peace"]
    },
    {
        "channel_id": "ch_02",
        "channel_name": "चैनल २: परम कृष्ण चेतना",
        "niche": "मृत्यु-बोध, माया का संहार, ब्रह्मांडीय विराट रूप, आत्म-साक्षात्कार",
        "archetype_focus": ["मृत्यु का भय, काल का संहार और चेतना की अमरता", "अहंकार का विनाश और आत्म-साक्षात्कार", "विश्वरूप दर्शन और काल का यथार्थ"],
        "token_file": "ch_02_token.json",
        "tags": ["Shri Krishna Gyan", "Vishwaroop", "Advaita Vedanta", "Spiritual Awakening", "Sanatan Dharma", "Death Illusion"]
    }
]

def load_channels_config() -> List[Dict[str, Any]]:
    if os.path.exists(CHANNELS_CONFIG_PATH):
        try:
            with open(CHANNELS_CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Save default if not present
    with open(CHANNELS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CHANNELS, f, indent=2, ensure_ascii=False)
    return DEFAULT_CHANNELS

class YouTubeChannelManager:
    def __init__(self):
        self.channels = load_channels_config()

    def get_token_path(self, channel_id: str) -> str:
        return os.path.join(CREDENTIALS_DIR, f"{channel_id}_token.json")

    def get_channel_status(self, channel_id: str) -> Dict[str, Any]:
        """Verifies if token exists and queries YouTube API for live channel title & subscriber count."""
        token_p = self.get_token_path(channel_id)
        c_meta = next((c for c in self.channels if c["channel_id"] == channel_id), {"channel_name": channel_id})

        # Check Human-Mimicry browser session status
        human_sf = os.path.join(CREDENTIALS_DIR, "youtube_session_status.json" if channel_id == "ch_01" else "youtube_session_status_ch_02.json")
        human_logged = False
        if os.path.exists(human_sf):
            try:
                with open(human_sf, "r", encoding="utf-8") as hf:
                    human_logged = json.load(hf).get("logged_in", False)
            except Exception:
                pass

        if not os.path.exists(token_p):
            if human_logged:
                return {
                    "channel_id": channel_id,
                    "configured_name": c_meta.get("channel_name"),
                    "niche": c_meta.get("niche"),
                    "connected": True,
                    "status_badge": "Active (Human Bot 🟢)",
                    "subscribers": "Connected",
                    "message": "Human-Mimicry Browser Profile Active & Ready"
                }
            return {
                "channel_id": channel_id,
                "configured_name": c_meta.get("channel_name"),
                "niche": c_meta.get("niche"),
                "connected": False,
                "status_badge": "Not Connected",
                "message": "Session or OAuth2 Token Required"
            }

        try:
            with open(token_p, "r", encoding="utf-8") as f:
                token_data = json.load(f)

            credentials = Credentials.from_authorized_user_info(token_data)
            youtube = build("youtube", "v3", credentials=credentials)
            res = youtube.channels().list(part="snippet,statistics", mine=True).execute()

            items = res.get("items", [])
            if items:
                snippet = items[0].get("snippet", {})
                stats = items[0].get("statistics", {})
                return {
                    "channel_id": channel_id,
                    "configured_name": c_meta.get("channel_name"),
                    "live_title": snippet.get("title"),
                    "custom_url": snippet.get("customUrl"),
                    "avatar_url": snippet.get("thumbnails", {}).get("default", {}).get("url"),
                    "subscribers": stats.get("subscriberCount", "0"),
                    "video_count": stats.get("videoCount", "0"),
                    "connected": True,
                    "status_badge": "Connected & Active",
                    "niche": c_meta.get("niche")
                }
            return {
                "channel_id": channel_id,
                "configured_name": c_meta.get("channel_name"),
                "connected": True,
                "status_badge": "Connected",
                "niche": c_meta.get("niche")
            }
        except Exception as e:
            return {
                "channel_id": channel_id,
                "configured_name": c_meta.get("channel_name"),
                "connected": False,
                "status_badge": "Token Expired / Error",
                "error": str(e),
                "niche": c_meta.get("niche")
            }

    def get_all_channels_status(self) -> List[Dict[str, Any]]:
        self.channels = load_channels_config()
        return [self.get_channel_status(c["channel_id"]) for c in self.channels]

    def add_channel(self, channel_id: str, channel_name: str, niche: str, tags: list = None) -> Dict[str, Any]:
        """Adds a new channel to channels.json dynamically."""
        self.channels = load_channels_config()
        if any(c["channel_id"] == channel_id for c in self.channels):
            return {"success": False, "error": f"Channel ID {channel_id} already exists"}
        new_ch = {
            "channel_id": channel_id,
            "channel_name": channel_name,
            "niche": niche,
            "token_file": f"{channel_id}_token.json",
            "tags": tags or ["Shri Krishna", "Bhagavad Gita", "Spiritual"]
        }
        self.channels.append(new_ch)
        with open(CHANNELS_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(self.channels, f, indent=2, ensure_ascii=False)
        return {"success": True, "channel": new_ch}

    def has_client_secret(self) -> bool:
        """Returns True if client_secret.json is installed."""
        return os.path.exists(CLIENT_SECRET_PATH)

    def save_client_secret(self, secret_json: str) -> bool:
        """Saves Google Cloud OAuth client_secret.json or service_account.json."""
        try:
            parsed = json.loads(secret_json) if isinstance(secret_json, str) else secret_json
            if isinstance(parsed, dict) and parsed.get("type") == "service_account":
                sa_path = os.path.join(CREDENTIALS_DIR, "service_account.json")
                with open(sa_path, "w", encoding="utf-8") as f:
                    json.dump(parsed, f, indent=2)
                print(f"[✓] Saved service_account.json successfully at {sa_path}!")
                return True

            if isinstance(parsed, dict) and "client_id" in parsed and "installed" not in parsed and "web" not in parsed:
                parsed = {
                    "installed": {
                        "client_id": parsed.get("client_id", "").strip(),
                        "project_id": parsed.get("project_id", "geeta-channel"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_secret": parsed.get("client_secret", "").strip(),
                        "redirect_uris": ["http://localhost", "http://localhost:8085"]
                    }
                }
            with open(CLIENT_SECRET_PATH, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
            return True
        except Exception as e:
            print(f"[!] Error saving client_secret.json: {e}")
            return False

    def save_channel_token_direct(self, channel_id: str, token_json: str) -> bool:
        """Allows direct paste of authorized OAuth token in dashboard."""
        try:
            parsed = json.loads(token_json) if isinstance(token_json, str) else token_json
            token_p = self.get_token_path(channel_id)
            with open(token_p, "w", encoding="utf-8") as f:
                json.dump(parsed, f, indent=2)
            return True
        except Exception:
            return False

    def create_oauth_flow(self, channel_id: str, redirect_uri: str = "http://localhost:8000/oauth2callback") -> tuple:
        """
        Creates an OAuth flow instance configured for the FastAPI server callback
        and returns (auth_url, state, flow).
        """
        if not os.path.exists(CLIENT_SECRET_PATH):
            raise FileNotFoundError(f"client_secret.json not found in {CREDENTIALS_DIR}")

        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_PATH,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        auth_url, state = flow.authorization_url(prompt="consent", access_type="offline")
        return auth_url, state, flow

    def complete_oauth_flow(self, flow: InstalledAppFlow, channel_id: str, authorization_response: str) -> Dict[str, Any]:
        """
        Exchanges code for token using authorization_response and saves token.
        """
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        flow.fetch_token(authorization_response=authorization_response)
        creds = flow.credentials
        token_data = {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes
        }
        token_p = self.get_token_path(channel_id)
        with open(token_p, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)
        print(f"[✓ GOOGLE OAUTH] Successfully saved token for {channel_id} at {token_p}!")
        return self.get_channel_status(channel_id)

    def start_oauth_server(self, channel_id: str, port: int = 8085) -> str:
        """
        Starts the redirect receiver on localhost:8085 in a background daemon thread
        and returns the EXACT Google authorization URL immediately.
        """
        global _active_oauth

        # Safely shut down previous server if still running
        if _active_oauth.get("server"):
            try:
                _active_oauth["server"].server_close()
            except Exception:
                pass
            _active_oauth["server"] = None

        if not os.path.exists(CLIENT_SECRET_PATH):
            raise FileNotFoundError(f"client_secret.json not found in {CREDENTIALS_DIR}")

        flow = InstalledAppFlow.from_client_secrets_file(
            CLIENT_SECRET_PATH,
            scopes=SCOPES
        )
        flow.redirect_uri = f"http://localhost:{port}/"
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")

        success_html = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>YouTube Connected — Gita Studio</title>
  <style>
    body { background: #0b0f19; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; text-align: center; padding: 60px 20px; }
    .card { max-width: 500px; margin: 0 auto; background: #131b2e; border: 1px solid #10b981; border-radius: 16px; padding: 32px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
    h1 { color: #10b981; font-size: 24px; margin-bottom: 12px; }
    p { color: #94a3b8; font-size: 14px; line-height: 1.6; }
    .badge { display: inline-block; padding: 6px 14px; background: rgba(16,185,129,0.15); color: #34d399; border-radius: 9999px; font-weight: 600; font-size: 13px; margin-top: 16px; }
  </style>
</head>
<body>
  <div class="card">
    <div style="font-size: 48px; margin-bottom: 16px;">🕉️</div>
    <h1>🎉 YouTube Channel Connected!</h1>
    <p>आपका YouTube चैनल सफलतापूर्वक <strong>Gita Production Studio</strong> से जुड़ चुका है।</p>
    <div class="badge">✓ Access Token Saved Successfully</div>
    <p style="margin-top: 20px; font-size: 12px; color: #64748b;">अब आप इस विंडो को बंद कर सकते हैं और डैशबोर्ड पर लौट सकते हैं।</p>
  </div>
  <script>
    setTimeout(function() { window.close(); }, 3500);
  </script>
</body>
</html>"""

        wsgi_app = _RedirectWSGIApp(success_html)
        local_server = wsgiref.simple_server.make_server(
            "localhost",
            port,
            wsgi_app,
            server_class=_ExclusiveWSGIServer,
            handler_class=_WSGIRequestHandler
        )

        def _worker():
            try:
                print(f"\n[🔑 GOOGLE OAUTH] Local server listening on http://localhost:{port}/ for channel '{channel_id}'...")
                local_server.handle_request()
                auth_resp = wsgi_app.last_request_uri.replace("http", "https")
                flow.fetch_token(authorization_response=auth_resp)
                creds = flow.credentials
                token_data = {
                    "token": creds.token,
                    "refresh_token": creds.refresh_token,
                    "token_uri": creds.token_uri,
                    "client_id": creds.client_id,
                    "client_secret": creds.client_secret,
                    "scopes": creds.scopes
                }
                token_p = self.get_token_path(channel_id)
                with open(token_p, "w", encoding="utf-8") as f:
                    json.dump(token_data, f, indent=2)
                print(f"[✓ GOOGLE OAUTH] Successfully saved token for {channel_id} at {token_p}!")
                _active_oauth["status"] = "success"
            except Exception as err:
                print(f"[!] OAuth worker error for {channel_id}: {err}")
                _active_oauth["status"] = f"error: {err}"
            finally:
                try:
                    local_server.server_close()
                except Exception:
                    pass

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

        _active_oauth["server"] = local_server
        _active_oauth["thread"] = t
        _active_oauth["channel_id"] = channel_id
        _active_oauth["auth_url"] = auth_url
        _active_oauth["status"] = "waiting"

        print(f"\n=======================================================")
        print(f"👉 GOOGLE SIGN-IN URL FOR CHANNEL {channel_id}:")
        print(auth_url)
        print(f"=======================================================\n")

        try:
            webbrowser.open(auth_url, new=1, autoraise=True)
        except Exception:
            pass

        return auth_url

    def get_oauth_status(self) -> Dict[str, Any]:
        global _active_oauth
        return {
            "channel_id": _active_oauth.get("channel_id"),
            "status": _active_oauth.get("status", "idle"),
            "auth_url": _active_oauth.get("auth_url")
        }

    def start_oauth_flow_interactive(self, channel_id: str, port: int = 8085) -> Dict[str, Any]:
        """
        Interactive helper for CLI authentication.
        """
        try:
            auth_url = self.start_oauth_server(channel_id, port)
            print(f"Please authorize here:\n{auth_url}\nWaiting for authorization on localhost:{port}...")
            # Wait up to 120s
            for _ in range(60):
                time.sleep(2)
                if self.get_token_path(channel_id) and os.path.exists(self.get_token_path(channel_id)):
                    return {
                        "success": True,
                        "message": f"Successfully authorized {channel_id}!",
                        "channel_info": self.get_channel_status(channel_id)
                    }
            return {"success": False, "error": "Timed out waiting for authorization"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_next_rotation_channel(self) -> Dict[str, Any]:
        """
        Alternates publishing across all configured channels in round-robin sequence.
        Supports 2, 3, or unlimited channels seamlessly.
        """
        self.channels = load_channels_config()
        if not self.channels:
            return {}

        channel_ids = [c["channel_id"] for c in self.channels]
        state = {"last_channel": "", "upload_counts": {}}
        if os.path.exists(ROTATION_STATE_PATH):
            try:
                with open(ROTATION_STATE_PATH, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                pass

        last = state.get("last_channel", "")
        try:
            idx = channel_ids.index(last)
            next_idx = (idx + 1) % len(channel_ids)
        except ValueError:
            next_idx = 0

        next_ch_id = channel_ids[next_idx]
        chosen = next((c for c in self.channels if c["channel_id"] == next_ch_id), self.channels[0])

        # Update state
        state["last_channel"] = next_ch_id
        counts = state.get("upload_counts", {})
        counts[next_ch_id] = counts.get(next_ch_id, 0) + 1
        state["upload_counts"] = counts
        state["last_rotation_time"] = time.time()

        os.makedirs(os.path.dirname(ROTATION_STATE_PATH), exist_ok=True)
        with open(ROTATION_STATE_PATH, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)

        print(f"[*] YouTube Multi-Channel Rotation ({len(self.channels)} Channels): Selected '{chosen['channel_name']}' ({chosen['channel_id']})")
        return chosen

channel_manager = YouTubeChannelManager()

if __name__ == "__main__":
    statuses = channel_manager.get_all_channels_status()
    print("Dual YouTube Channels Status:")
    print(json.dumps(statuses, indent=2, ensure_ascii=False))
