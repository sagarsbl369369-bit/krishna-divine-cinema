"""
Groq Key Pool Manager
---------------------
Autonomous multi-key pooling engine for Groq Cloud API:
- Supports pool of multiple free Groq API keys (from console.groq.com)
- Automatic rotation & load balancing across keys
- Rate limit detection (429) & instant failover
- Powers high-concurrency 10-Agent Swarm research
"""

import os
import sys
import json
import time
from typing import List, Optional, Tuple
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
GROQ_POOL_STATE_FILE = os.path.join(BASE_DIR, "renders", "groq_pool_state.json")

class GroqKeyPool:
    def __init__(self, config_path: str = CONFIG_PATH):
        self.config_path = config_path
        self.keys = []
        self.key_states = {}
        self.current_idx = 0
        self.load_keys()
        self.load_state()

    def load_keys(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    raw_keys = cfg.get("GROQ_API_KEYS", [])
                    single_key = cfg.get("GROQ_API_KEY", "")
                    if single_key and single_key not in raw_keys:
                        raw_keys.insert(0, single_key)
                    self.keys = [
                        k.strip() for k in raw_keys 
                        if k.strip() and not k.startswith("YOUR_") and not k.startswith("gsk_default_placeholder")
                    ]
            except Exception as e:
                print(f"[!] Error loading Groq keys: {e}")

    def load_state(self):
        if os.path.exists(GROQ_POOL_STATE_FILE):
            try:
                with open(GROQ_POOL_STATE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.key_states = data.get("states", {})
            except Exception:
                self.key_states = {}

        now = time.time()
        for k in self.keys:
            if k not in self.key_states:
                self.key_states[k] = {"status": "active", "calls": 0, "last_exhausted": 0, "failures": 0}
            else:
                # Auto-recovery: If exhausted more than 10 minutes ago, reset to active
                if self.key_states[k]["status"] == "exhausted":
                    if now - self.key_states[k].get("last_exhausted", 0) > 600:
                        self.key_states[k]["status"] = "active"

        self.save_state()

    def save_state(self):
        os.makedirs(os.path.dirname(GROQ_POOL_STATE_FILE), exist_ok=True)
        try:
            with open(GROQ_POOL_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump({"states": self.key_states, "last_updated": time.time()}, f, indent=2)
        except Exception:
            pass

    def add_key(self, api_key: str):
        api_key = api_key.strip()
        if api_key and api_key not in self.keys and not api_key.startswith("gsk_default_placeholder"):
            self.keys.append(api_key)
            self.key_states[api_key] = {"status": "active", "calls": 0, "last_exhausted": 0, "failures": 0}
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                if "GROQ_API_KEYS" not in cfg:
                    cfg["GROQ_API_KEYS"] = []
                if api_key not in cfg["GROQ_API_KEYS"]:
                    cfg["GROQ_API_KEYS"].append(api_key)
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(cfg, f, indent=2)
            except Exception:
                pass
            self.save_state()

    def get_active_key(self) -> Optional[str]:
        self.load_keys()
        self.load_state()
        if not self.keys:
            return None

        active_keys = [k for k in self.keys if self.key_states.get(k, {}).get("status") == "active"]
        if not active_keys:
            # Fall back to least recently exhausted key
            sorted_keys = sorted(self.keys, key=lambda k: self.key_states.get(k, {}).get("last_exhausted", 0))
            return sorted_keys[0]

        self.current_idx = (self.current_idx + 1) % len(active_keys)
        return active_keys[self.current_idx]

    def mark_exhausted(self, api_key: str):
        if api_key in self.key_states:
            self.key_states[api_key]["status"] = "exhausted"
            self.key_states[api_key]["last_exhausted"] = time.time()
            self.key_states[api_key]["failures"] = self.key_states[api_key].get("failures", 0) + 1
            print(f"   [!] Groq Key ...{api_key[-6:]} rate-limited. Auto-rotating to next key in pool...")
            self.save_state()

    def mark_success(self, api_key: str):
        if api_key in self.key_states:
            self.key_states[api_key]["status"] = "active"
            self.key_states[api_key]["calls"] = self.key_states[api_key].get("calls", 0) + 1
            self.save_state()

    def post_chat_completion(self, payload: dict, max_retries: int = 5) -> dict:
        """Dispatches an OpenAI-compatible completion request to Groq with auto-pooling."""
        attempts = 0
        tried = set()

        while attempts < max_retries:
            key = self.get_active_key()
            if not key:
                raise RuntimeError("No Groq API keys available in pool.")
            tried.add(key)

            headers = {
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json"
            }
            try:
                r = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=45
                )
                if r.status_code == 200:
                    self.mark_success(key)
                    return r.json()
                elif r.status_code == 429:
                    self.mark_exhausted(key)
                    attempts += 1
                else:
                    # other error
                    raise RuntimeError(f"Groq API error ({r.status_code}): {r.text}")
            except requests.exceptions.RequestException as e:
                attempts += 1
                time.sleep(1)

        raise RuntimeError(f"All Groq keys in pool ({len(tried)}) temporarily exhausted or unreachable.")

    def get_pool_telemetry(self) -> dict:
        self.load_keys()
        self.load_state()
        total = len(self.keys)
        active = sum(1 for k in self.keys if self.key_states.get(k, {}).get("status") == "active")
        return {
            "total_keys": total,
            "active_keys": active,
            "exhausted_keys": total - active,
            "keys_summary": [
                {
                    "masked_key": f"...{k[-6:]}" if len(k) > 6 else k,
                    "status": self.key_states.get(k, {}).get("status", "unknown"),
                    "calls": self.key_states.get(k, {}).get("calls", 0)
                }
                for k in self.keys
            ]
        }

groq_pool = GroqKeyPool()

if __name__ == "__main__":
    status = groq_pool.get_pool_telemetry()
    print("Groq Key Pool Telemetry:")
    print(json.dumps(status, indent=2))
