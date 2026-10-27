import os
import sys
import json
import time
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "credentials", "github_cloud_config.json")

def trigger_batch(run_id="40514508384"):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    
    repo = cfg.get("github_repo", "sagarsbl369369-bit/krishna-divine-cinema")
    token = cfg.get("github_token", "")
    
    url = f"https://api.github.com/repos/{repo}/actions/workflows/cloud_batch_uploader.yml/dispatches"
    payload = json.dumps({
        "ref": "main",
        "inputs": {
            "run_id": str(run_id)
        }
    }).encode("utf-8")
    
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "Antigravity-Uploader-Trigger"
        },
        method="POST"
    )
    
    print(f"[*] Dispatching Cloud Batch Uploader for Artifact Run ID: {run_id}...")
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status == 204:
                print("✓ Successfully triggered Cloud Batch Uploader workflow on GitHub Actions!")
    except urllib.error.HTTPError as e:
        print(f"❌ Failed to dispatch workflow: {e.code} {e.reason}")
        print(e.read().decode())
        return None

    # Wait for the run to appear
    print("[*] Waiting for runner to pick up dispatch...")
    time.sleep(6)
    
    runs_url = f"https://api.github.com/repos/{repo}/actions/workflows/cloud_batch_uploader.yml/runs?per_page=1"
    req_runs = urllib.request.Request(
        runs_url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Antigravity-Monitor"
        }
    )
    
    with urllib.request.urlopen(req_runs) as resp_runs:
        data = json.loads(resp_runs.read().decode())
        if data.get("workflow_runs"):
            latest = data["workflow_runs"][0]
            print(f"🚀 RUN DISPATCHED!")
            print(f"   ID: {latest['id']}")
            print(f"   Status: {latest['status']}")
            print(f"   URL: {latest['html_url']}")
            return latest['id']
    return None

if __name__ == "__main__":
    target_id = sys.argv[1] if len(sys.argv) > 1 else "40514508384"
    trigger_batch(target_id)
