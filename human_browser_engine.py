"""
Human-Like Browser Automation Engine (100% Zero-API)
====================================================
Automates video production through a real visible Google Chrome browser:
1. Launches real Google Chrome with persistent login (no API keys needed).
2. Navigates to Google Gemini (gemini.google.com) or Google AI Studio (aistudio.google.com).
3. Types the Supreme Hypnotic Spoken Text Directive with human pacing.
4. Waits for complete generation, extracts clean text.
5. Synthesizes studio-quality voiceover with Shure SM7B Broadcast DSP.
6. Assembles 1080p master video & hard-stitches 173.25s Blue Laser Outro (ORIGINAL SONG HU-BA-HU).
7. Delivers to C:\\Users\\janar\\Downloads\\geeta wala\\ and updates catalog.html.
"""

import os
import sys
import time
import json
import re
import subprocess
from typing import Optional, Tuple
from playwright.sync_api import sync_playwright

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
HUMAN_PROFILE_DIR = os.path.join(CREDENTIALS_DIR, "human_chrome_profile")
TARGET_BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "geeta wala")

os.makedirs(CREDENTIALS_DIR, exist_ok=True)
os.makedirs(HUMAN_PROFILE_DIR, exist_ok=True)
os.makedirs(TARGET_BASE_DIR, exist_ok=True)

import hypnotic_tts_master
import hypnotic_video_composer
import gita_catalog_generator

SUPREME_PROMPT_TEMPLATE = """# SUPREME DIRECTIVE: 100% PURE SPOKEN TEXT ENGINE WITH HYPNOTIC ENGAGEMENT (FOR TTS)

तुम्हें विश्व के सबसे गहन आध्यात्मिक कथावाचक और भगवान श्री कृष्ण के दिव्य सखा के रूप में बोलना है। यह टेक्स्ट सीधे AI Text-to-Speech सॉफ्टवेयर में डाला जाएगा।

## CRITICAL TTS CONSTRAINTS (सख्त नियम):
1. NO BRACKETS / NO DIRECTIONS: कोई भी ब्रैकेट [ ], ( ) या निर्देश नहीं होगा। [संगीत], [ठहराव] जैसा एक भी शब्द नहीं आना चाहिए।
2. NO MARKDOWN: कोई हेडिंग (#), कोई बोल्ड (**), कोई इटैलिक, कोई नंबरिंग या बुलेट पॉइंट नहीं।
3. NO META TALK: मुझसे कोई बात नहीं करनी (जैसे: "यहाँ स्क्रिप्ट है...")। आउटपुट का पहला अक्षर ही बोले जाने वाले संवाद की शुरुआत होगा।
4. PUNCTUATION AS PACING: गहरे सांस और ठहराव के लिए (...) का उपयोग करो। भाव बदलने के लिए (—) का उपयोग करो। केवल शुद्ध, मधुर और वजनदार हिंदी देवनागरी।

## THE HYPNOTIC ENGAGEMENT ENGINE (चैनल ग्रोथ का गुप्त मनोविज्ञान):
स्क्रिप्ट के प्रवाह को तोड़े बिना, तुम्हें बहुत ही स्वाभाविक, रूहानी और विवश कर देने वाले अंदाज में श्रोता से 4 कार्य करवाने हैं:

1. COMMENT TRIGGER (मन का बोझ उतारना):
श्रोता से सिर्फ "जय श्री कृष्णा" मत कहलवाओ, उससे कहो: "आज अपने उस अनकहे दर्द को... उस घुटन को कमेंट में लिखकर यहीं छोड़ जाओ जिसे तुम वर्षों से अकेले सीने में दबाए घूम रहे हो... क्योंकि जब तुम अपने सच को स्वीकार कर लेते हो, तो माधव तुम्हारा हाथ थाम लेते हैं..."

2. LIKE TRIGGER (आत्मा की हाजिरी):
"यदि इस वाणी ने तुम्हारी रूह के किसी बंद कमरे को खोला हो... तो अपनी उपस्थिति की एक मौन गवाही इस संवाद को समर्पित कर देना... ताकि यह सत्य तुम्हारे हृदय में सदा के लिए अंकित हो जाए..."

3. SHARE TRIGGER (पुण्य और कर्म का कर्तव्य):
"इस संसार में कोई एक ऐसा व्यक्ति अवश्य होगा जो आज इसी क्षण... कमरे के किसी अंधेरे कोने में अपनी टूटी हुई उम्मीदों के साथ रो रहा होगा... यह वाणी उस तक पहुँचा देना... हो सकता है आज तुम्हारी एक कोशिश किसी को आत्महत्या या अवसाद के दलदल से बाहर खींच ले..."

4. SUBSCRIBE TRIGGER (आध्यात्मिक आश्रय):
"यदि यह संसार तुम्हें बार-बार थकाता है... और तुम्हें हर दिन कृष्ण के इस शांत सान्निध्य की आवश्यकता है... तो इस पवित्र परिवार से अपनी आत्मा का नाता जोड़ लेना... ताकि जब भी तुम्हारा हौसला डगमगाए, तुम्हें माधव का स्वर सुनाई दे..."

## ASSIGNED THEME & SOUL SURGERY:
विषय: {THEME}

## OUTPUT INSTRUCTION (FOR LONG-FORM MASTER EPISODE):
- 100% शुद्ध स्पोकन प्लेन टेक्स्ट में दो।
- शब्द पूरे विस्तार से, गहरी लय और सम्मोहन के साथ लिखे होने चाहिए (लगभग 3,500 से 4,500 शब्द)। कोई शॉर्टकट नहीं।
- पहले खंड के आखिरी वाक्य पर बात को ऐसे रोंगटे खड़े कर देने वाले मोड़ पर छोड़ना कि श्रोता तड़प उठे आगे सुनने के लिए।
"""

DEFAULT_THEMES = [
    "जब अपने ही सबसे बड़ा विश्वासघात करें — छल के बाद अंतर्मन की मौन संप्रभुता और कर्ण की व्यथा",
    "रात के ३ बजे का सन्नाटा — दिमाग के उस अनवरत शोर और अकेलेपन को शांत करने का शाश्वत सत्य",
    "सबको खुश रखने की बीमारी (People Pleasing Trap) — जब त्याग का बदला सिर्फ अपमान मिले",
    "करियर की घुटन और पीछे छूट जाने का खौफ — जब मेहनत का कोई फल न मिले और किस्मत हंसती दिखे",
    "अकेलेपन को अपनी सबसे घातक शक्ति बनाओ — जब दुनिया साथ छोड़ दे, तब आत्मा का साम्राज्य"
]

def sanitize_script_text(raw_text: str) -> str:
    """Removes stray markdown, brackets, or meta talk."""
    text = re.sub(r'\[.*?\]', '', raw_text)
    text = re.sub(r'\(.*?\)', '', text)
    text = text.replace('**', '').replace('##', '').replace('*', '')
    text = text.replace('आगे', '').strip()
    return text

def launch_human_login():
    """Opens visible Chrome for the user to log in to their Google account once."""
    print("=" * 80)
    print("🌐 LAUNCHING HUMAN BROWSER FOR 1-TIME GOOGLE LOGIN")
    print("=" * 80)
    print("1. Real Chrome will open on your screen.")
    print("2. Log in to your Google Account (Gmail / Google Gemini / AI Studio).")
    print("3. Once logged in, your session is saved permanently in your local profile.")
    print("4. Close the browser window when done.")
    print("=" * 80)

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=HUMAN_PROFILE_DIR,
            channel="chrome",
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = browser.new_page()
        page.goto("https://accounts.google.com/ServiceLogin?continue=https://gemini.google.com/")
        print("\n[*] Waiting for you to complete login... Close Chrome when finished.")
        page.wait_for_timeout(300000) # 5 minutes wait
        browser.close()
    print("✓ Login session stored.")

def generate_script_via_gemini_browser(theme: str) -> Tuple[str, str]:
    """Automates Gemini web chat like a human to generate the script."""
    print(f"\n[*] Launching Real Chrome for Human Script Generation...")
    print(f"[*] Target Theme: '{theme}'")

    prompt = SUPREME_PROMPT_TEMPLATE.replace("{THEME}", theme)
    extracted_text = ""

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=HUMAN_PROFILE_DIR,
            channel="chrome",
            headless=False,
            args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
        )
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://gemini.google.com/app", wait_until="domcontentloaded", timeout=60000)
        time.sleep(5)

        # Look for the input box
        input_selectors = [
            "div[contenteditable='true']",
            "rich-textarea div[contenteditable='true']",
            "textarea[aria-label*='prompt']",
            "textarea"
        ]

        box = None
        for sel in input_selectors:
            if page.locator(sel).count() > 0:
                box = page.locator(sel).first
                break

        if box:
            print("[*] Found Gemini prompt box. Typing supreme hypnotic directive...")
            box.click()
            time.sleep(1)
            # Use clipboard / fill for fast reliable delivery of long prompt
            box.fill(prompt)
            time.sleep(1)
            page.keyboard.press("Enter")
            print("[*] Prompt submitted! Watching Gemini generate live in browser...")

            # Wait for generation to start and finish
            time.sleep(10)
            max_wait_secs = 240
            start_wait = time.time()

            while (time.time() - start_wait) < max_wait_secs:
                # Check if stop button is gone
                stop_btn = page.locator("button[aria-label*='Stop']")
                if stop_btn.count() == 0:
                    time.sleep(4)
                    break
                time.sleep(3)

            # Extract response text
            response_selectors = [
                ".model-response-text",
                "message-content",
                ".markdown"
            ]
            for r_sel in response_selectors:
                elements = page.locator(r_sel)
                if elements.count() > 0:
                    extracted_text = elements.last.inner_text()
                    if len(extracted_text) > 300:
                        break

            print(f"✓ Extracted {len(extracted_text.split())} words from Gemini Web!")
        else:
            print("⚠️ Prompt box not found (user might need to log in first).")

        browser.close()

    if not extracted_text or len(extracted_text) < 300:
        print("[!] Fallback to backup script cache if Gemini UI was not ready.")
        cache_script = os.path.join(BASE_DIR, "latest_generated_script.txt")
        if os.path.exists(cache_script):
            with open(cache_script, "r", encoding="utf-8") as f:
                extracted_text = f.read()

    cleaned_script = sanitize_script_text(extracted_text)
    return cleaned_script, theme

def produce_human_video_pipeline(custom_theme: Optional[str] = None, target_channel: str = "ch_01"):
    print("=" * 82)
    print("🎬 100% HUMAN BROWSER VIDEO PRODUCTION ENGINE (ZERO-API)")
    print("=" * 82)

    theme = custom_theme or DEFAULT_THEMES[0]

    # 1. Generate Script via Real Chrome Browser
    script_text, title = generate_script_via_gemini_browser(theme)
    script_file = os.path.join(BASE_DIR, "latest_human_script.txt")
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"✓ Script saved: {script_file}")

    # 2. Studio Voiceover Synthesis + Shure SM7B DSP
    print("\n[STEP 2/3] Generating Studio Voiceover with Shure SM7B Broadcast DSP...")
    audio_path = os.path.join(BASE_DIR, "latest_human_audio.mp3")
    hypnotic_tts_master.generate_hypnotic_voiceover(
        text=script_text,
        output_path=audio_path,
        voice="hi-IN-MadhurNeural"
    )

    # 3. Assemble 1080p Video + Hard-Locked Original Song Outro
    print("\n[STEP 3/3] Assembling 1080p Master Video & Stitching Original Song Outro...")
    final_video = hypnotic_video_composer.assemble_hypnotic_video(
        audio_path=audio_path,
        title=f"श्रीकृष्ण वाणी — {title}",
        channel_key=target_channel
    )

    print("\n" + "=" * 82)
    print(f"🎉 MASTER VIDEO CREATED (100% HUMAN BROWSER PIPELINE):")
    print(f"🎬 {final_video}")
    print("=" * 82)

    try:
        gita_catalog_generator.generate_catalog()
    except Exception:
        pass

    return final_video

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="Launch browser for 1-time Google login")
    parser.add_argument("--channel", type=str, default="ch_01", help="Target channel (ch_01 or ch_02)")
    args = parser.parse_args()

    if args.login:
        launch_human_login()
    else:
        produce_human_video_pipeline(target_channel=args.channel)
