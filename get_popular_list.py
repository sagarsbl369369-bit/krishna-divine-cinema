from playwright.sync_api import sync_playwright
import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.youtube.com/@Krishnavandan14/videos", timeout=30000)
    page.wait_for_timeout(3000)

    # Click Popular
    chips = page.locator("yt-chip-cloud-chip-renderer").all()
    for c in chips:
        txt = c.inner_text().strip()
        if "Popular" in txt or "लोकप्रिय" in txt:
            c.click()
            page.wait_for_timeout(3000)
            break

    cards = page.locator("ytd-rich-item-renderer").all()
    videos = []
    for c in cards[:10]:
        lines = [l.strip() for l in c.inner_text().split("\n") if l.strip()]
        link_el = c.locator("a#thumbnail, a#video-title-link, a[href*='watch']").first
        href = link_el.get_attribute("href") if link_el.count() > 0 else ""
        full_url = f"https://www.youtube.com{href}" if href.startswith("/") else href
        videos.append({
            "lines": lines,
            "url": full_url
        })

    print(json.dumps(videos, indent=2, ensure_ascii=False))
    browser.close()
