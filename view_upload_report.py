import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('renders/uploaded_videos_log.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total Videos in Log: {len(data)}\n")
for k, v in data.items():
    print(f"Worker {v.get('worker_id')}:")
    print(f"  Channel: {v.get('channel_id')}")
    print(f"  Status:  {v.get('status')}")
    print(f"  URL:     {v.get('video_url')}")
    print(f"  Title:   {v.get('title')}")
    print("-" * 60)
