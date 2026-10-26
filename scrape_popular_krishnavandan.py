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
    # Go directly to popular tab or videos
    page.goto("https://www.youtube.com/@Krishnavandan14/videos", timeout=30000)
    page.wait_for_timeout(4000)

    # Click on "Popular" filter chip if available
    chips = page.locator("yt-chip-cloud-chip-renderer").all()
    for chip in chips:
        text = chip.inner_text().strip()
        if "Popular" in text or "लोकप्रिय" in text:
            chip.click()
            page.wait_for_timeout(3000)
            break

    # Extract videos
    cards = page.locator("ytd-rich-item-renderer").all()
    print(f"Total cards: {len(cards)}")
    results = []

    for c in cards[:12]:
        try:
            # Video Title
            title_el = c.locator("a#video-title-link, #video-title")
            title = title_el.first.inner_text().strip() if title_el.count() > 0 else ""
            href = title_el.first.get_attribute("href") if title_el.count() > 0 else ""
            full_url = f"https://www.youtube.com{href}" if href.startswith("/") else href

            # Views and age
            meta_els = c.locator("#metadata-line span").all()
            meta_texts = [m.inner_text().strip() for m in meta_els if m.inner_text().strip()]
            views = meta_texts[0] if len(meta_texts) > 0 else "N/A"
            time_ago = meta_texts[1] if len(meta_texts) > 1 else "N/A"

            # Duration
            time_el = c.locator("ytd-thumbnail-overlay-time-status-renderer badge-shape, ytd-thumbnail-overlay-time-status-renderer span#text")
            dur = time_el.first.inner_text().strip() if time_el.count() > 0 else "N/A"

            if title:
                results.append({
                    "title": title,
                    "url": full_url,
                    "duration": dur,
                    "views": views,
                    "time_ago": time_ago
                })
        except Exception as e:
            continue

    print(json.dumps(results, indent=2, ensure_ascii=False))
    browser.close()
