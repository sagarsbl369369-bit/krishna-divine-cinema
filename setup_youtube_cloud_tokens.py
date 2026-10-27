"""
1-Click YouTube Cloud Authorization & Auto-Secret Syncer
=========================================================
1. Launches Google Sign-In for Channel 1 and Channel 2.
2. Exchanges authorization code for permanent refresh_token.
3. Automatically encrypts and syncs `YT_TOKEN_CH01` and `YT_TOKEN_CH02`
   directly into GitHub Actions Secrets via PyNaCl!
4. After running this ONCE, GitHub Actions will upload all 10 videos
   directly to YouTube autonomously with zero PC load!
"""

import os
import sys
import json
import time
import requests
from base64 import b64encode
from nacl import encoding, public
from google_auth_oauthlib.flow import InstalledAppFlow

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
CLIENT_SECRET_PATH = os.path.join(CREDENTIALS_DIR, "client_secret.json")
CONFIG_PATH = os.path.join(CREDENTIALS_DIR, "github_cloud_config.json")

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]

def encrypt_secret(public_key_str: str, secret_value: str) -> str:
    public_key = public.PublicKey(public_key_str.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")

def sync_secret_to_github(secret_name: str, secret_value: str) -> bool:
    cfg = json.load(open(CONFIG_PATH, "r", encoding="utf-8"))
    repo = cfg.get("github_repo")
    token = cfg.get("github_token")
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    # 1. Get Repo Public Key
    r_key = requests.get(f"https://api.github.com/repos/{repo}/actions/secrets/public-key", headers=headers)
    if r_key.status_code != 200:
        print(f"❌ Failed to fetch public key for {repo}: {r_key.text}")
        return False

    key_data = r_key.json()
    encrypted_val = encrypt_secret(key_data["key"], secret_value)

    # 2. Put Secret
    put_url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
    payload = {
        "encrypted_value": encrypted_val,
        "key_id": key_data["key_id"]
    }
    r_put = requests.put(put_url, headers=headers, json=payload)
    if r_put.status_code in [201, 204]:
        print(f"✅ [SUCCESS] Synced '{secret_name}' into GitHub Secrets for '{repo}'!")
        return True
    else:
        print(f"❌ Failed to save secret '{secret_name}': {r_put.text}")
        return False

def authorize_channel(channel_id: str, channel_label: str, port: int = 8085):
    print("\n" + "=" * 80)
    print(f"🔑 AUTHORIZING YOUTUBE CHANNEL: {channel_label} ({channel_id.upper()})")
    print("=" * 80)
    print(f"👉 A Google Sign-In window will open in your browser.")
    print(f"👉 Please select the Google account for {channel_label} and click 'Allow'.")
    print("=" * 80 + "\n")

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    flow = InstalledAppFlow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=f"http://localhost:{port}/"
    )

    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    
    # Open browser
    import webbrowser
    webbrowser.open(auth_url)

    # Run local server to catch token
    creds = flow.run_local_server(port=port, prompt="consent")
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }

    # Save locally
    token_p = os.path.join(CREDENTIALS_DIR, f"{channel_id}_token.json")
    with open(token_p, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)
    print(f"✓ Saved local token: {token_p}")

    # Sync to GitHub Secrets
    sec_name = f"YT_TOKEN_{channel_id.upper()}"
    sync_secret_to_github(sec_name, json.dumps(token_data))
    return token_data

if __name__ == "__main__":
    if not os.path.exists(CLIENT_SECRET_PATH):
        print(f"❌ Error: {CLIENT_SECRET_PATH} not found!")
        sys.exit(1)

    print("=" * 80)
    print("🕉️ GITA PRODUCTION STUDIO — YOUTUBE CLOUD AUTONOMY CONFIGURATOR")
    print("=" * 80)
    print("This 1-time setup connects your 2 YouTube channels to GitHub Actions Cloud.")
    print("After this, GitHub will upload all 10 videos automatically with ZERO PC load!\n")

    # Authorize Channel 1
    authorize_channel("ch_01", "चैनल १: दिव्य गीता वाणी", port=8085)
    
    # Authorize Channel 2
    time.sleep(2)
    authorize_channel("ch_02", "चैनल २: परम कृष्ण चेतना", port=8086)

    print("\n" + "=" * 80)
    print("🎉 YOUTUBE CLOUD AUTONOMY FULLY CONFIGURED!")
    print("From now on, GitHub Actions will directly upload all 10 videos automatically!")
    print("=" * 80)
