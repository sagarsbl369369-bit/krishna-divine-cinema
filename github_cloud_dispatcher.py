"""
GitHub Cloud 1-Click Dispatcher & Telemetry Engine
==================================================
Triggers the 10-Worker Parallel Cloud Beast on GitHub Actions:
- 10 Parallel Linux Cloud VMs spin up simultaneously
- 5 Videos for Channel 1 + 5 Videos for Channel 2
- Duration >30 Mins (default 35 mins)
- 100% Strictly UNLISTED
- Automatic Clean Shutdown upon completion
"""

import os
import sys
import json
import time
import requests
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
CONFIG_PATH = os.path.join(CREDENTIALS_DIR, "github_cloud_config.json")
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

class GitHubCloudDispatcher:
    def __init__(self):
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        default_cfg = {
            "github_repo": "",       # e.g., "username/krishna-ai-cinema"
            "github_token": "",      # Personal Access Token with 'repo' or 'workflow' scope
            "workflow_name": "master_10_video_pipeline.yml",
            "last_dispatched": 0,
            "last_status": "IDLE"
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    default_cfg.update(json.load(f))
            except Exception:
                pass
        return default_cfg

    def save_config(self, cfg: Optional[Dict[str, Any]] = None):
        if cfg:
            self.config.update(cfg)
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def dispatch_10_video_batch(self, duration: int = 35, privacy: str = "unlisted") -> Dict[str, Any]:
        repo = self.config.get("github_repo", "").strip()
        token = self.config.get("github_token", "").strip()
        workflow = self.config.get("workflow_name", "master_10_video_pipeline.yml")

        if not repo or not token:
            return {
                "success": False,
                "error": "GitHub Repository or Personal Access Token (PAT) not configured yet in credentials/github_cloud_config.json"
            }

        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/dispatches"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        payload = {
            "ref": "main",
            "inputs": {
                "target_duration": str(duration),
                "privacy": privacy
            }
        }

        try:
            r = requests.post(url, headers=headers, json=payload, timeout=20)
            if r.status_code in [204, 201, 200]:
                self.config["last_dispatched"] = time.time()
                self.config["last_status"] = "DISPATCHED"
                self.save_config()
                return {
                    "success": True,
                    "message": f"⚡ 10-Video Cloud Beast Launched on GitHub Actions for {repo}! 10 parallel VMs active."
                }
            else:
                return {
                    "success": False,
                    "error": f"GitHub API responded with code {r.status_code}: {r.text}"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_latest_run_status(self) -> Dict[str, Any]:
        repo = self.config.get("github_repo", "").strip()
        token = self.config.get("github_token", "").strip()
        workflow = self.config.get("workflow_name", "master_10_video_pipeline.yml")

        if not repo or not token:
            return {"configured": False, "status": "NOT_CONFIGURED"}

        url = f"https://api.github.com/repos/{repo}/actions/workflows/{workflow}/runs?per_page=1"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                runs = data.get("workflow_runs", [])
                if runs:
                    latest = runs[0]
                    return {
                        "configured": True,
                        "run_id": latest.get("id"),
                        "status": latest.get("status"),       # queued, in_progress, completed
                        "conclusion": latest.get("conclusion"), # success, failure, neutral
                        "html_url": latest.get("html_url"),
                        "created_at": latest.get("created_at"),
                        "updated_at": latest.get("updated_at")
                    }
                return {"configured": True, "status": "NO_RUNS_YET"}
            return {"configured": True, "status": f"HTTP_{r.status_code}", "error": r.text}
        except Exception as e:
            return {"configured": True, "status": "ERROR", "error": str(e)}

dispatcher = GitHubCloudDispatcher()

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 GITHUB CLOUD 1-CLICK DISPATCHER (10 PARALLEL RUNNERS)")
    print("=" * 80)
    cfg = dispatcher.load_config()
    print("Current Configuration:")
    print(f" - GitHub Repo : {cfg.get('github_repo') or '[NOT SET]'}")
    print(f" - GitHub Token: {'*' * 8 if cfg.get('github_token') else '[NOT SET]'}")
    print("=" * 80)

    if not cfg.get("github_repo") or not cfg.get("github_token"):
        print("\n👉 Please configure your GitHub Repo and Token in:")
        print(f"   {CONFIG_PATH}")
        print("   Example: {\"github_repo\": \"yourname/repo\", \"github_token\": \"ghp_xxxx\"}")
        sys.exit(1)

    print("\nDispatching 10 Parallel Cloud Workers for 10 Videos (>30 Mins, UNLISTED)...")
    res = dispatcher.dispatch_10_video_batch(duration=35, privacy="unlisted")
    if res.get("success"):
        print(f"✅ {res.get('message')}")
        print(f"🔗 Check live GitHub Actions run at: https://github.com/{cfg.get('github_repo')}/actions")
    else:
        print(f"❌ Error: {res.get('error')}")
