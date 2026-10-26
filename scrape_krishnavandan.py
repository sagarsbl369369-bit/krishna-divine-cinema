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
    page.wait_for_timeout(4000)

    # Scrape video items
    items = page.locator("ytd-rich-item-renderer").all()
    print(f"Total video elements found: {len(items)}")

    results = []
    for el in items[:15]:
        try:
            title_el = el.locator("#video-title")
            title = title_el.inner_text().strip() if title_el.count() > 0 else ""
            
            meta_el = el.locator("#metadata-line")
            meta = meta_el.inner_text().strip().replace("\n", " • ") if meta_el.count() > 0 else ""

            time_el = el.locator("ytd-thumbnail-overlay-time-status-renderer span#text")
            dur = time_el.inner_text().strip() if time_el.count() > 0 else ""

            results.append({"title": title, "meta": meta, "duration": dur})
        except Exception:
            continue

    print(json.dumps(results, indent=2, ensure_ascii=False))
    browser.close()
