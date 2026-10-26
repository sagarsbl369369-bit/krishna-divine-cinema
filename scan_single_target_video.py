from playwright.sync_api import sync_playwright
import json
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

target_url = "https://www.youtube.com/watch?v=4aCwWUoh_i0"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto(target_url, timeout=30000)
    page.wait_for_timeout(4000)

    # Get title
    title = page.locator("h1.ytd-watch-metadata").inner_text().strip()
    
    # Click "...more" on description
    expand_btn = page.locator("#expand, tp-yt-paper-button#expand")
    if expand_btn.count() > 0:
        try:
            expand_btn.first.click()
            page.wait_for_timeout(1000)
        except Exception:
            pass

    desc = page.locator("#description-inline-expander").inner_text().strip()

    # Try to open transcript if button exists
    transcript_text = ""
    try:
        # Search for transcript button
        t_btn = page.locator("button[aria-label*='transcript' i], button[aria-label*='ट्रांसक्रिप्ट' i], ytd-video-description-transcript-section-renderer button")
        if t_btn.count() > 0:
            t_btn.first.click()
            page.wait_for_timeout(2000)
            segments = page.locator("ytd-transcript-segment-renderer").all()
            lines = [s.inner_text().strip().replace("\n", " ") for s in segments[:30]]
            transcript_text = "\n".join(lines)
    except Exception as e:
        transcript_text = f"Transcript error: {e}"

    print(json.dumps({
        "url": target_url,
        "title": title,
        "description": desc[:600],
        "sample_transcript": transcript_text
    }, indent=2, ensure_ascii=False))

    browser.close()
