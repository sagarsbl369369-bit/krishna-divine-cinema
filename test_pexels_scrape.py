import requests
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
r = requests.get('https://www.pexels.com/search/videos/meditation/', headers=headers, timeout=15)
print('Pexels Status:', r.status_code)
# Search for video files or JSON data
links = set(re.findall(r'https://video-previews\.pexels\.com/[^\s"\'<>]+', r.text))
print('Found video-previews links:', len(links))
for l in list(links)[:3]:
    print('Preview link:', l)

# Also check for player or video-files
cdn_links = set(re.findall(r'https://[^\s"\'<>]+\.mp4[^\s"\'<>]*', r.text))
print('Found MP4 cdn links:', len(cdn_links))
for l in list(cdn_links)[:3]:
    print('CDN link:', l)
