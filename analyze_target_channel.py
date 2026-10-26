import urllib.request
import re
import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

url = "https://www.youtube.com/@Krishnavandan14/videos"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "hi,en-US;q=0.9,en;q=0.8"
}
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=12) as response:
        html = response.read().decode('utf-8', errors='ignore')

    # Look for ytInitialData
    m = re.search(r'var ytInitialData\s*=\s*({.*?});</script>', html)
    if not m:
        m = re.search(r'ytInitialData\s*=\s*({.*?});', html)
    
    if m:
        data = json.loads(m.group(1))
        # Traverse tabs
        tabs = data.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", [])
        videos = []
        for t in tabs:
            tab_renderer = t.get("tabRenderer", {})
            if tab_renderer.get("title") in ["Videos", "वीडियो", "वीडियोज़"]:
                content = tab_renderer.get("content", {})
                rich_grid = content.get("richGridRenderer", {})
                contents = rich_grid.get("contents", [])
                for item in contents:
                    rich_item = item.get("richItemRenderer", {}).get("content", {})
                    v_renderer = rich_item.get("videoRenderer", {})
                    if v_renderer:
                        title = v_renderer.get("title", {}).get("runs", [{}])[0].get("text", "")
                        dur = v_renderer.get("lengthText", {}).get("simpleText", "")
                        views = v_renderer.get("viewCountText", {}).get("simpleText", "")
                        time_ago = v_renderer.get("publishedTimeText", {}).get("simpleText", "")
                        v_id = v_renderer.get("videoId", "")
                        videos.append({"title": title, "duration": dur, "views": views, "time_ago": time_ago, "video_id": v_id})
        print(f"Successfully extracted {len(videos)} videos from @Krishnavandan14:")
        for idx, v in enumerate(videos[:15], 1):
            print(f"{idx}. [{v['duration']}] {v['title']} ({v['views']} • {v['time_ago']})")
    else:
        print("ytInitialData not found directly in regex.")
except Exception as e:
    print(f"Error: {e}")
