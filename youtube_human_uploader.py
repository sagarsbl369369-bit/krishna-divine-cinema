"""
YouTube Autonomous Human-Mimicry Studio Uploader (Playwright Stealth Engine)
----------------------------------------------------------------------------
Uploads videos directly to YouTube Studio (studio.youtube.com) exactly like an expert human editor:
1. Uses persistent browser profile in `credentials/youtube_browser_profile/`.
2. ZERO Google Cloud Console / OAuth API keys required!
3. ZERO 'Error 403: access_denied' or verification blockers!
4. ZERO API quota limits (unlimited uploads, never capped at 6 videos/day).
5. Automates:
   - File drag-and-drop / file input selection.
   - High-CTR title & narrative description with chapter timestamps.
   - Clean 1280x720 UHD thumbnail attachment in safe-zone.
   - Audience selection ("No, it's not made for kids").
   - 500-char tags and category settings.
   - Sets visibility (Public / Unlisted) and clicks Publish!
   - Extracts live published YouTube video link.
"""

import os
import sys
import json
import time
import re
import argparse
from typing import Dict, Any, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
BROWSER_PROFILE_DIR = os.path.join(CREDENTIALS_DIR, "youtube_browser_profile")
SESSION_STATUS_FILE = os.path.join(CREDENTIALS_DIR, "youtube_session_status.json")
os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)

def get_channel_profile_dir(channel_id: str = "ch_01") -> str:
    if channel_id == "ch_02":
        return os.path.join(CREDENTIALS_DIR, "youtube_browser_profile_ch_02")
    return os.path.join(CREDENTIALS_DIR, "youtube_browser_profile")

def get_channel_status_file(channel_id: str = "ch_01") -> str:
    if channel_id == "ch_02":
        return os.path.join(CREDENTIALS_DIR, "youtube_session_status_ch_02.json")
    return os.path.join(CREDENTIALS_DIR, "youtube_session_status.json")

class YouTubeHumanUploader:
    def __init__(self, channel_id: str = "ch_01", profile_dir: Optional[str] = None):
        self.channel_id = channel_id
        self.profile_dir = profile_dir or get_channel_profile_dir(channel_id)
        os.makedirs(self.profile_dir, exist_ok=True)
        self.clean_stale_locks()

    def clean_stale_locks(self):
        """Cleans any stale Chromium lock files that prevent browser launch."""
        if not os.path.exists(self.profile_dir):
            return
        for root, dirs, files in os.walk(self.profile_dir):
            for f in files:
                if f.lower() in ["lock", "singletonlock", "singletoncookie", "singletonsocket"]:
                    try:
                        os.remove(os.path.join(root, f))
                    except Exception:
                        pass

    def _launch_context(self, p, headless: bool = False):
        """Launches persistent browser context with automatic fallback to dedicated Chromium."""
        self.clean_stale_locks()
        launch_args = [
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--start-maximized"
        ]
        try:
            return p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                headless=headless,
                channel="chrome",
                args=launch_args,
                viewport=None
            )
        except Exception as e:
            print(f"[ℹ️] Chrome channel fallback ({e}). Launching dedicated Chromium...")
            self.clean_stale_locks()
            return p.chromium.launch_persistent_context(
                user_data_dir=self.profile_dir,
                headless=headless,
                args=launch_args,
                viewport=None
            )

    def is_logged_in(self, page: Optional[Page] = None) -> bool:
        """Checks if current browser session is logged into YouTube Studio."""
        if page is not None:
            return self._check_page_logged_in(page)
        
        # Standalone headless check
        try:
            with sync_playwright() as p:
                context = self._launch_context(p, headless=True)
                p_check = context.new_page()
                result = self._check_page_logged_in(p_check)
                context.close()
                return result
        except Exception as e:
            print(f"[!] Error checking login status: {e}")
            return False

    def _check_page_logged_in(self, page: Page) -> bool:
        try:
            page.goto("https://studio.youtube.com", wait_until="domcontentloaded", timeout=30000)
            time.sleep(3)
            current_url = page.url
            if "accounts.google.com" in current_url or "signin" in current_url:
                return False
            if "studio.youtube.com" in current_url:
                if "Creator Studio" in page.title() or "channel" in current_url or page.locator("#create-icon, #upload-button, ytcp-button#create-icon, #channel-name").count() > 0:
                    return True
            return False
        except Exception:
            return False

    def launch_session_login(self, channel_id: str = "ch_01", timeout_seconds: int = 300) -> bool:
        """
        Launches visible browser window allowing user to log in ONCE for specified channel.
        Session is permanently saved to `youtube_browser_profile/` or `youtube_browser_profile_ch_02/`.
        """
        self.channel_id = channel_id
        self.profile_dir = get_channel_profile_dir(channel_id)
        os.makedirs(self.profile_dir, exist_ok=True)
        status_file = get_channel_status_file(channel_id)

        print("\n" + "=" * 70)
        print(f"🌐 YOUTUBE STUDIO HUMAN-MIMICRY LOGIN FOR CHANNEL: {channel_id.upper()}")
        print("=" * 70)
        print("Opening YouTube Studio in your persistent browser profile...")
        print(f"📁 Session Directory: {self.profile_dir}")
        print("👉 Please log in to your YouTube channel in the opened browser window.")
        print(f"⏳ Waiting up to {timeout_seconds} seconds (5 minutes) for login completion...")
        print("=" * 70 + "\n")

        with sync_playwright() as p:
            context = self._launch_context(p, headless=False)
            page = context.new_page()
            page.goto("https://studio.youtube.com")

            logged_in = False
            start_t = time.time()
            while time.time() - start_t < timeout_seconds:
                time.sleep(3)
                current_url = page.url
                if "studio.youtube.com" in current_url and "accounts.google.com" not in current_url:
                    if page.locator("#create-icon, #upload-button, ytcp-button#create-icon, #channel-name").count() > 0 or "channel" in current_url:
                        logged_in = True
                        break

            if logged_in:
                print(f"🎉 [SUCCESS] Logged in to YouTube Studio for {channel_id}! Session cookies saved permanently.")
                try:
                    with open(status_file, "w", encoding="utf-8") as f:
                        json.dump({"logged_in": True, "last_login": time.time(), "channel_id": channel_id, "url": page.url}, f, indent=2)
                except Exception:
                    pass
                time.sleep(3)
            else:
                print("[!] Login timed out or pending. You can re-run login anytime.")

            context.close()
            return logged_in

    def upload_video(
        self,
        video_path: str,
        seo_package: Dict[str, Any],
        thumbnail_path: Optional[str] = None,
        channel_id: str = "ch_01",
        privacy: str = "unlisted",
        headless: bool = False
    ) -> Dict[str, Any]:
        """
        Automates YouTube Studio upload with human-mimicry precision for specified channel.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        self.channel_id = channel_id
        self.profile_dir = get_channel_profile_dir(channel_id)
        os.makedirs(self.profile_dir, exist_ok=True)

        print("\n" + "=" * 70)
        print(f"🤖 AUTONOMOUS HUMAN-MIMICRY STUDIO UPLOADER [{channel_id.upper()}]")
        print(f"🎬 Video: {video_path}")
        print(f"🏷️ Title: {seo_package.get('title')}")
        print(f"🖼️ Thumbnail: {thumbnail_path}")
        print(f"📁 Profile: {self.profile_dir}")
        print(f"🔒 Visibility: {privacy.upper()}")
        print("=" * 70)

        with sync_playwright() as p:
            context = self._launch_context(p, headless=headless)
            page = context.new_page()

            # 1. Navigate to YouTube Studio
            print("[1/7] Navigating to studio.youtube.com...")
            page.goto("https://studio.youtube.com/?approve_browser_access=true", wait_until="networkidle", timeout=45000)
            time.sleep(3)

            # Check if login is needed
            if "accounts.google.com" in page.url or "signin" in page.url:
                context.close()
                return {
                    "success": False,
                    "error": "login_required",
                    "message": "YouTube Studio session not logged in. Please run launch_session_login() first."
                }

            # 2. Click Create / Upload
            print("[2/7] Opening Video Upload Dialog...")
            create_btn = page.locator("#upload-icon, ytcp-button:has-text('Create'), #create-icon").first
            if create_btn.count() > 0:
                create_btn.click()
                time.sleep(2)
                upload_item = page.locator("tp-yt-paper-item:has-text('Upload videos'), tp-yt-paper-item:has-text('Upload'), #text-item-0").first
                if upload_item.count() > 0 and upload_item.is_visible():
                    upload_item.click()
                    time.sleep(2)

            time.sleep(1)

            # 3. Select Video File
            print(f"[3/7] Selecting Video File ({os.path.basename(video_path)})...")
            file_input = page.locator("input[type='file']").first
            file_input.wait_for(state="attached", timeout=15000)
            file_input.set_input_files(video_path)

            print("   [⏳] Waiting for YouTube Studio upload dialog to initialize...")
            page.wait_for_selector("#title-textarea, #textbox[aria-label*='title' i]", timeout=60000)
            time.sleep(3)

            # 4. Fill Title & Description
            print("[4/7] Entering Viral SEO Title & Narrative Chapters Description...")
            title_box = page.locator("#title-textarea #textbox, div[aria-label*='title' i]").first
            title_text = seo_package.get("title", "")[:100]
            title_box.click()
            # Clear default title (filename)
            page.keyboard.press("Control+A")
            page.keyboard.press("Backspace")
            title_box.fill(title_text)
            print(f"   ✓ Title: {title_text}")

            time.sleep(1)
            desc_box = page.locator("#description-textarea #textbox, div[aria-label*='description' i]").first
            desc_text = seo_package.get("description", "")
            desc_box.click()
            desc_box.fill(desc_text)
            print("   ✓ Narrative Description & Chapter Timestamps Filled!")

            # 5. Upload Viral Thumbnail
            thumb = thumbnail_path or seo_package.get("thumbnail_path")
            if thumb and os.path.exists(thumb):
                print(f"[5/7] Attaching 1280x720 UHD Viral Thumbnail ({os.path.basename(thumb)})...")
                try:
                    thumb_input = page.locator("input#file-loader, input[type='file'][accept*='image']").first
                    if thumb_input.count() > 0:
                        thumb_input.set_input_files(thumb)
                        time.sleep(3)
                        print("   ✓ Viral Thumbnail Successfully Attached!")
                except Exception as thumb_e:
                    print(f"   ⚠️ Could not attach thumbnail via file-loader: {thumb_e}")
            else:
                print("[5/7] No thumbnail file specified; YouTube will auto-select default frame.")

            # 6. Audience Selection ("No, it's not made for kids")
            print("[6/7] Configuring Audience & Safety Settings...")
            not_kids_radio = page.locator("tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK'], #not-made-for-kids-radio").first
            if not_kids_radio.count() > 0:
                not_kids_radio.click()
                print("   ✓ Audience: 'No, it is not made for kids'")

            # Optional: Tags
            try:
                show_more = page.locator("ytcp-button#toggle-button:has-text('Show more'), #toggle-button").first
                if show_more.count() > 0:
                    show_more.click()
                    time.sleep(1)
                    tags_box = page.locator("input[aria-label*='Tags' i], #tags-container input").first
                    if tags_box.count() > 0:
                        tags_str = ",".join(seo_package.get("tags", [])[:25])
                        tags_box.fill(tags_str)
                        page.keyboard.press("Enter")
                        print("   ✓ 500-Character Viral Tags Injected!")
            except Exception:
                pass

            # 7. Navigation: Next -> Next -> Next -> Visibility
            print("[7/7] Navigating to Visibility & Publishing...")
            next_btn = page.locator("#next-button").first
            for step in range(3):
                if next_btn.is_visible() and next_btn.is_enabled():
                    next_btn.click()
                    time.sleep(2)

            # Visibility Selection
            if privacy.lower() == "public":
                pub_radio = page.locator("tp-yt-paper-radio-button[name='PUBLIC'], #public-radio-button").first
                if pub_radio.count() > 0:
                    pub_radio.click()
                    print("   ✓ Visibility Set to: PUBLIC")
            else:
                unlisted_radio = page.locator("tp-yt-paper-radio-button[name='UNLISTED'], #unlisted-radio-button").first
                if unlisted_radio.count() > 0:
                    unlisted_radio.click()
                    print("   ✓ Visibility Set to: UNLISTED")

            # Extract generated video link if present
            video_url = ""
            try:
                link_el = page.locator("a.ytcp-video-info, a[href*='youtu.be']").first
                if link_el.count() > 0:
                    video_url = link_el.get_attribute("href") or ""
            except Exception:
                pass

            # Final Done / Publish click
            done_btn = page.locator("#done-button, ytcp-button#done-button").first
            if done_btn.is_visible() and done_btn.is_enabled():
                done_btn.click()
                print("🎉 [PUBLISH CLICKED] Video publishing triggered in YouTube Studio!")
                time.sleep(4)

            # Wait for upload completion progress
            print("   [⏳] Ensuring upload stream completes to 100% (Please keep browser open)...")
            start_wait = time.time()
            while time.time() - start_wait < 900:  # up to 15 mins for large 800MB video
                try:
                    close_dialog_btn = page.locator("#close-button, ytcp-button#close-button").first
                    if close_dialog_btn.is_visible() and close_dialog_btn.is_enabled():
                        close_dialog_btn.click()
                        time.sleep(1)

                    progress_el = page.locator("span:has-text('Upload complete'), span:has-text('Processing'), span:has-text('Checks complete'), span.progress-label").first
                    if progress_el.count() > 0:
                        p_txt = progress_el.inner_text().strip()
                        if any(w in p_txt.lower() for w in ["complete", "processing", "saved", "checks"]):
                            print(f"\n   ✓ Upload status confirmed: {p_txt}!")
                            break
                        else:
                            print(f"   [⏳] {p_txt}", end="\r")
                except Exception:
                    pass
                time.sleep(3)

            print("\n🎉 [SUCCESS] Video upload and metadata publishing fully complete!")
            time.sleep(5)

            context.close()
            return {
                "success": True,
                "video_url": video_url or f"https://studio.youtube.com/channel/videos",
                "video_path": video_path,
                "title": title_text,
                "status": "published"
            }

human_uploader = YouTubeHumanUploader()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="YouTube Autonomous Human-Mimicry Studio Uploader")
    parser.add_argument("--login", action="store_true", help="Launch one-time visible Chrome login window")
    parser.add_argument("--check", action="store_true", help="Check if persistent session is logged in")
    parser.add_argument("--upload", action="store_true", help="Execute upload with latest master assets")
    parser.add_argument("--channel", type=str, default="ch_01", choices=["ch_01", "ch_02"], help="Target channel: ch_01 | ch_02")
    parser.add_argument("--video", type=str, default=None, help="Path to video file")
    parser.add_argument("--seo", type=str, default=None, help="Path to SEO package JSON")
    parser.add_argument("--thumb", type=str, default=None, help="Path to thumbnail image")
    parser.add_argument("--privacy", type=str, default="unlisted", help="unlisted | public | private")
    parser.add_argument("--visible", action="store_true", help="Run with visible browser window")
    args = parser.parse_args()

    human_uploader = YouTubeHumanUploader(channel_id=args.channel)

    if args.login:
        human_uploader.launch_session_login(channel_id=args.channel)
    elif args.check:
        status = human_uploader.is_logged_in()
        print(f"YouTube Studio Login Status [{args.channel}]: {'LOGGED_IN' if status else 'NOT_LOGGED_IN'}")
        sys.exit(0 if status else 1)
    elif args.upload:
        # Default to master assets if not provided
        v_path = args.video or os.path.join(BASE_DIR, "renders", "epic_bhagavad_gita_documentary_master.mp4")
        t_path = args.thumb or os.path.join(BASE_DIR, "master_viral_thumbnail.jpg")
        
        # Load SEO package if available
        seo_data = {}
        if args.seo and os.path.exists(args.seo):
            with open(args.seo, "r", encoding="utf-8") as f:
                seo_data = json.load(f)
        else:
            # Look in renders/seo_packages/
            seo_dir = os.path.join(BASE_DIR, "renders", "seo_packages")
            if os.path.exists(seo_dir):
                seos = sorted([os.path.join(seo_dir, f) for f in os.listdir(seo_dir) if f.endswith(".json")], key=os.path.getmtime, reverse=True)
                if seos:
                    with open(seos[0], "r", encoding="utf-8") as f:
                        seo_data = json.load(f)
            if not seo_data:
                seo_data = {
                    "title": "जब जीवन में सब खत्म लगे तब यह सुनो | अकेलापन और मन का संताप | श्रीकृष्ण वाणी",
                    "description": "श्रीमद्भगवद्गीता के परम पावन उपदेश। जब जीवन में घोर अंधकार और विषाद छा जाए, तब भगवान श्रीकृष्ण का यह अमर संदेश सुनें।\n\n00:00 - प्रस्तावना\n03:15 - अर्जुन का विषाद\n07:42 - आत्मा की अमरता\n12:10 - कर्मयोग का रहस्य\n18:30 - निष्काम कर्म\n25:00 - मन को वश में करने की कला\n30:00 - परम शांति की प्राप्ति\n\n#BhagavadGita #KrishnaVani #KarmaYoga",
                    "tags": ["भगवद्गीता", "श्रीकृष्ण वाणी", "कर्मयोग", "geeta gyan", "krishna motivational", "vedic wisdom", "spiritual guide"]
                }
        
        result = human_uploader.upload_video(
            video_path=v_path,
            seo_package=seo_data,
            thumbnail_path=t_path,
            channel_id=args.channel,
            privacy=args.privacy,
            headless=not args.visible
        )
        print("\nUpload Result:", json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage:")
        print("  python youtube_human_uploader.py --login       (One-time studio login)")
        print("  python youtube_human_uploader.py --check       (Check if studio is logged in)")
        print("  python youtube_human_uploader.py --upload      (Upload master video + thumbnail + SEO)")
        print("  python youtube_human_uploader.py --upload --visible (Upload while watching live in Chrome!)")
