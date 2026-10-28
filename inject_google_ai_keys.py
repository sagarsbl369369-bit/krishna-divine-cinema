"""
Google Gemini & Google AI Studio Multi-Account Key Injector
===========================================================
- Allows adding multiple Google AI Studio & Gemini API Keys from multiple accounts.
- Tests each key live against Google GenAI API endpoint.
- Automatically encrypts and syncs keys to GitHub Secrets (GEMINI_API_KEYS) via GitHub API.
- Updates local config.json and credentials/gemini_keys.json.
"""

import os
import sys
import json
import base64
import requests
from typing import List, Dict, Any

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
GH_CONFIG_PATH = os.path.join(CREDENTIALS_DIR, "github_cloud_config.json")
KEYS_FILE = os.path.join(CREDENTIALS_DIR, "gemini_keys.json")

os.makedirs(CREDENTIALS_DIR, exist_ok=True)

def load_local_keys() -> List[str]:
    keys = []
    # 1. From gemini_keys.json
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    keys.extend(data)
                elif isinstance(data, dict):
                    keys.extend(data.get("keys", []))
        except Exception:
            pass
    # 2. From config.json
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                keys.extend(cfg.get("GEMINI_API_KEYS", []))
                single = cfg.get("GEMINI_API_KEY", "")
                if single:
                    keys.append(single)
        except Exception:
            pass
    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for k in keys:
        clean = k.strip()
        if clean and clean not in seen and not clean.startswith("YOUR_"):
            seen.add(clean)
            deduped.append(clean)
    return deduped

def save_local_keys(keys: List[str]):
    # Save to gemini_keys.json
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump({"keys": keys, "updated_at": os.times()[4]}, f, indent=2)
    # Save to config.json
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            cfg["GEMINI_API_KEYS"] = keys
            if keys:
                cfg["GEMINI_API_KEY"] = keys[0]
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

def test_gemini_key(api_key: str) -> bool:
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'OK' in one word."
        )
        return bool(resp and resp.text)
    except Exception as e:
        print(f"   ⚠️ Test failed for key ...{api_key[-6:]}: {e}")
        return False

def sync_secret_to_github(secret_name: str, secret_value: str) -> bool:
    """Uses PyNaCl to encrypt and upload secret directly to GitHub Secrets."""
    if not os.path.exists(GH_CONFIG_PATH):
        print("   ❌ GitHub Cloud config not found!")
        return False

    with open(GH_CONFIG_PATH, "r", encoding="utf-8") as f:
        gh_cfg = json.load(f)

    repo = gh_cfg.get("github_repo", "").strip()
    token = gh_cfg.get("github_token", "").strip()

    if not repo or not token:
        print("   ❌ GitHub repo or token missing in github_cloud_config.json")
        return False

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    # 1. Get repository public key
    pk_url = f"https://api.github.com/repos/{repo}/actions/secrets/public-key"
    r_pk = requests.get(pk_url, headers=headers, timeout=15)
    if r_pk.status_code != 200:
        print(f"   ❌ Failed to get GitHub public key: {r_pk.status_code} {r_pk.text}")
        return False

    pk_data = r_pk.json()
    key_id = pk_data["key_id"]
    public_key_b64 = pk_data["key"]

    # 2. Encrypt using PyNaCl SealedBox
    try:
        from nacl import encoding, public
        pk = public.PublicKey(public_key_b64.encode("utf-8"), encoding.Base64Encoder)
        sealed_box = public.SealedBox(pk)
        encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
        encrypted_b64 = base64.b64encode(encrypted).decode("utf-8")
    except Exception as e:
        print(f"   ❌ PyNaCl encryption failed: {e}")
        return False

    # 3. Put secret to GitHub
    sec_url = f"https://api.github.com/repos/{repo}/actions/secrets/{secret_name}"
    payload = {
        "encrypted_value": encrypted_b64,
        "key_id": key_id
    }
    r_put = requests.put(sec_url, headers=headers, json=payload, timeout=15)
    if r_put.status_code in [201, 204]:
        print(f"   ✓ Successfully synced '{secret_name}' to GitHub Secrets for {repo}!")
        return True
    else:
        print(f"   ❌ Failed to set secret '{secret_name}': {r_put.status_code} {r_put.text}")
        return False

def interactive_injection():
    print("=" * 80)
    print("🔑 GOOGLE GEMINI & GOOGLE AI STUDIO MULTI-ACCOUNT KEY INJECTOR")
    print("=" * 80)
    current_keys = load_local_keys()
    print(f"[*] Found {len(current_keys)} active Google AI Studio / Gemini keys in pool:")
    for idx, k in enumerate(current_keys, 1):
        print(f"    [{idx}] AIza...{k[-6:]}")
    print("=" * 80)

    print("\nOptions:")
    print(" [1] Add New Google AI Studio Key(s)")
    print(" [2] Test All Keys Live")
    print(" [3] Sync Current Keys to GitHub Actions Secrets")
    print(" [4] Clear and Replace All Keys")
    print(" [0] Exit")
    print("-" * 80)

    choice = input("👉 Enter choice [0-4]: ").strip()

    if choice == "1":
        print("\nEnter API Keys (one per line, or comma-separated). Type 'DONE' when finished:")
        new_keys = []
        while True:
            line = input().strip()
            if not line or line.upper() == "DONE":
                break
            for part in line.replace(",", " ").split():
                clean_k = part.strip()
                if clean_k and clean_k.startswith("AIza") and clean_k not in current_keys and clean_k not in new_keys:
                    new_keys.append(clean_k)
                    print(f"   + Added AIza...{clean_k[-6:]}")

        if new_keys:
            all_keys = current_keys + new_keys
            save_local_keys(all_keys)
            print(f"\n✓ Saved {len(all_keys)} keys to local configuration.")
            sync_choice = input("Sync to GitHub Secrets right now? (y/n) [default: y]: ").strip().lower()
            if sync_choice in ["", "y", "yes"]:
                sync_secret_to_github("GEMINI_API_KEYS", json.dumps(all_keys))
        else:
            print("No new valid keys entered.")

    elif choice == "2":
        print("\n[*] Testing all keys live with Google Gemini 2.5 Flash...")
        for idx, k in enumerate(current_keys, 1):
            print(f"Testing [{idx}/{len(current_keys)}] AIza...{k[-6:]}...", end=" ", flush=True)
            ok = test_gemini_key(k)
            if ok:
                print("✅ WORKING!")
            else:
                print("❌ FAILED")

    elif choice == "3":
        print("\n[*] Syncing local keys to GitHub Secrets...")
        if current_keys:
            sync_secret_to_github("GEMINI_API_KEYS", json.dumps(current_keys))
        else:
            print("⚠️ No keys to sync.")

    elif choice == "4":
        confirm = input("⚠️ Are you sure you want to clear all existing keys? (y/n): ").strip().lower()
        if confirm == "y":
            save_local_keys([])
            print("✓ Cleared all keys.")

if __name__ == "__main__":
    interactive_injection()
