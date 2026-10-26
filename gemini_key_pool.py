"""
Gemini Key Pool Manager
-----------------------
Autonomous multi-key management engine for Google AI Studio Gemini API:
- Smart Round-Robin Key Rotation
- Real-time Rate Limit & Quota Telemetry (Tracks 429 RESOURCE_EXHAUSTED)
- Auto-cooling & 24h reset recovery
- 0% API Bottleneck for 24x7 multi-instance rendering
"""

import os
import sys
import json
import time
from typing import List, Optional, Tuple
from google import genai
from google.genai import types

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
POOL_STATE_FILE = os.path.join(BASE_DIR, "renders", "gemini_pool_state.json")

class GeminiKeyPool:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self.keys = []
        self.key_states = {}  # {key_str: {"status": "active"|"exhausted", "calls": int, "last_exhausted": float}}
        self.current_idx = 0
        self.load_keys()
        self.load_state()

    def load_keys(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    raw_keys = cfg.get("GEMINI_API_KEYS", [])
                    single_key = cfg.get("GEMINI_API_KEY", "")
                    if single_key and single_key not in raw_keys:
                        raw_keys.insert(0, single_key)
                    self.keys = [k.strip() for k in raw_keys if k.strip() and not k.startswith("YOUR_")]
            except Exception as e:
                print(f"[!] Error loading Gemini keys: {e}")

    def load_state(self):
        if os.path.exists(POOL_STATE_FILE):
            try:
                with open(POOL_STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.key_states = data.get("states", {})
            except Exception:
                self.key_states = {}

        now = time.time()
        for k in self.keys:
            if k not in self.key_states:
                self.key_states[k] = {"status": "active", "calls": 0, "last_exhausted": 0, "failures": 0}
            else:
                # Auto-recovery: If exhausted more than 20 hours ago, reset to active
                if self.key_states[k]["status"] == "exhausted":
                    if now - self.key_states[k].get("last_exhausted", 0) > 20 * 3600:
                        self.key_states[k]["status"] = "active"
                        print(f"[*] Quota Cooldown Expired for Key ...{k[-6:]}. Marked ACTIVE.")

        self.save_state()

    def save_state(self):
        os.makedirs(os.path.dirname(POOL_STATE_FILE), exist_ok=True)
        try:
            with open(POOL_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({"states": self.key_states, "last_updated": time.time()}, f, indent=2)
        except Exception:
            pass

    def add_key(self, api_key: str):
        api_key = api_key.strip()
        if api_key and api_key not in self.keys:
            self.keys.append(api_key)
            self.key_states[api_key] = {"status": "active", "calls": 0, "last_exhausted": 0, "failures": 0}
            # Save to config.json
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if "GEMINI_API_KEYS" not in cfg:
                    cfg["GEMINI_API_KEYS"] = []
                if api_key not in cfg["GEMINI_API_KEYS"]:
                    cfg["GEMINI_API_KEYS"].append(api_key)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2)
            except Exception:
                pass
            self.save_state()

    def mark_exhausted(self, api_key: str):
        if api_key in self.key_states:
            self.key_states[api_key]["status"] = "exhausted"
            self.key_states[api_key]["last_exhausted"] = time.time()
            self.key_states[api_key]["failures"] = self.key_states[api_key].get("failures", 0) + 1
            print(f"   [!] Gemini Key ...{api_key[-6:]} marked EXHAUSTED (429/Quota). Rotating to next...")
            self.save_state()

    def mark_success(self, api_key: str):
        if api_key in self.key_states:
            self.key_states[api_key]["status"] = "active"
            self.key_states[api_key]["calls"] = self.key_states[api_key].get("calls", 0) + 1
            self.save_state()

    def get_active_client(self) -> Tuple[genai.Client, str]:
        """
        Returns an active genai.Client and the corresponding API key.
        Cycles round-robin through non-exhausted keys.
        """
        self.load_keys()
        self.load_state()

        if not self.keys:
            raise RuntimeError("No Gemini API keys found in config.json! Please add at least one Gemini key.")

        active_keys = [k for k in self.keys if self.key_states.get(k, {}).get("status") == "active"]
        if not active_keys:
            # If all are marked exhausted, try the one exhausted longest ago
            sorted_keys = sorted(self.keys, key=lambda k: self.key_states.get(k, {}).get("last_exhausted", 0))
            best_key = sorted_keys[0]
            print(f"   [!] All keys currently marked exhausted. Attempting oldest key ...{best_key[-6:]}")
            client = genai.Client(api_key=best_key)
            return client, best_key

        self.current_idx = (self.current_idx + 1) % len(active_keys)
        chosen_key = active_keys[self.current_idx]
        client = genai.Client(api_key=chosen_key)
        return client, chosen_key

    def generate_content_with_retry(self, model: str, contents, config=None, max_retries: int = 5):
        """
        Executes generate_content with automatic key rotation upon rate-limit errors.
        """
        attempts = 0
        tried_keys = set()

        while attempts < max_retries:
            client, key = self.get_active_client()
            tried_keys.add(key)
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
                self.mark_success(key)
                return resp
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                    self.mark_exhausted(key)
                    attempts += 1
                else:
                    # Non-quota error (invalid argument, etc.)
                    raise e

        raise RuntimeError(f"All available Gemini keys ({len(tried_keys)}) in pool have been exhausted.")

    def get_pool_telemetry(self) -> dict:
        total = len(self.keys)
        active = sum(1 for k in self.keys if self.key_states.get(k, {}).get("status") == "active")
        exhausted = total - active
        return {
            "total_keys": total,
            "active_keys": active,
            "exhausted_keys": exhausted,
            "keys_summary": [
                {
                    "masked_key": f"...{k[-6:]}" if len(k) > 6 else k,
                    "status": self.key_states.get(k, {}).get("status", "unknown"),
                    "calls": self.key_states.get(k, {}).get("calls", 0),
                    "last_exhausted_hrs_ago": round((time.time() - self.key_states.get(k, {}).get("last_exhausted", 0)) / 3600, 1) if self.key_states.get(k, {}).get("last_exhausted") else None
                }
                for k in self.keys
            ]
        }

# Global singleton
gemini_pool = GeminiKeyPool()

if __name__ == "__main__":
    status = gemini_pool.get_pool_telemetry()
    print("Gemini Key Pool Telemetry:")
    print(json.dumps(status, indent=2))
