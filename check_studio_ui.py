import sys
import time
sys.path.append(r"C:\Users\janar\.gemini\antigravity\scratch\geeta_automation_engine")
from youtube_human_uploader import YouTubeHumanUploader
from playwright.sync_api import sync_playwright

u = YouTubeHumanUploader(channel_id="ch_01")
with sync_playwright() as p:
    ctx = u._launch_context(p, headless=True)
    page = ctx.new_page()
    page.goto("https://studio.youtube.com/?approve_browser_access=true", wait_until="networkidle", timeout=40000)
    time.sleep(4)
    print("Dashboard loaded:", page.title())
    
    # Click upload-icon or Create
    btn = page.locator("#upload-icon, ytcp-button:has-text('Create')").first
    print("Clicking upload/create button...")
    btn.click()
    time.sleep(2)
    
    # If Create menu opened, click 'Upload videos'
    up_item = page.locator("tp-yt-paper-item:has-text('Upload videos'), tp-yt-paper-item:has-text('Upload')").first
    if up_item.count() > 0 and up_item.is_visible():
        print("Clicking 'Upload videos' menu item...")
        up_item.click()
        time.sleep(2)
        
    file_input = page.locator("input[type='file']").first
    print("file_input count:", file_input.count())
    page.screenshot(path=r"C:\Users\janar\.gemini\antigravity\scratch\geeta_automation_engine\renders\studio_upload_dialog_verified.png")
    print("Screenshot saved to renders/studio_upload_dialog_verified.png")
    ctx.close()
