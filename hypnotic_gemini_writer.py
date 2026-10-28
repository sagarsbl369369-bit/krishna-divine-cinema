import os
import sys
import json
import re
import time
import urllib.request
import urllib.error

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
PROMPT_PATH = os.path.join(BASE_DIR, "credentials", "hypnotic_master_prompt.txt")

def clean_for_tts(text: str) -> str:
    """Strict post-processor to ensure 100% pure spoken Devanagari text for TTS."""
    text = re.sub(r'#+\s*', '', text)
    text = re.sub(r'[*_`]', '', text)
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'\(.*?\)', '', text)
    
    lines = text.splitlines()
    cleaned_lines = []
    started = False
    for l in lines:
        stripped = l.strip()
        if not stripped:
            if started:
                cleaned_lines.append("")
            continue
        if not started and any(k in stripped for k in ["यहाँ", "स्क्रिप्ट", "प्रस्तुत", "भाग 1", "खंड", "Title", "Part"]):
            continue
        started = True
        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines).strip()

def generate_hypnotic_script(custom_topic: str = None) -> tuple[str, str]:
    """
    Calls Google AI Studio (Gemini Free API) with multi-key rotation and retry.
    Fallback to Groq if Google has temporary 503/429 limits.
    Returns: (cleaned_script_text, topic_title)
    """
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    gemini_keys = cfg.get("GEMINI_API_KEYS", [])
    groq_keys = cfg.get("GROQ_API_KEYS", [])

    with open(PROMPT_PATH, "r", encoding="utf-8") as pf:
        master_prompt = pf.read()

    user_instruction = master_prompt + "\n\n"
    if custom_topic:
        user_instruction += f"तुम्हारा मुख्य विषय यह है: {custom_topic}\n"
    else:
        user_instruction += "मनुष्य के अंतर्मन के सबसे गहरे दर्द और घाव को स्वयं चुनकर, उस पर लगभग 1,200 से 1,800 शब्दों का अत्यंत सम्मोहक, शुद्ध और गहरा संवाद लिखो।\n"

    user_instruction += "याद रहे: केवल शुद्ध बोले जाने वाले संवाद लिखो। पहला अक्षर ही संवाद की शुरुआत हो। कोई ब्रैकेट, कोई निर्देश, कोई हेडिंग नहीं।"

    # Primary model is gemini-flash-lite-latest (Super fast & stable)
    models = ["gemini-flash-lite-latest", "gemini-3.8-flash", "gemini-flash-latest"]
    
    for key in gemini_keys:
        for model_name in models:
            for attempt in range(2):
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={key}"
                payload = json.dumps({
                    "contents": [{
                        "parts": [{"text": user_instruction}]
                    }],
                    "generationConfig": {
                        "temperature": 0.85,
                        "topP": 0.95,
                        "maxOutputTokens": 3000
                    }
                }).encode("utf-8")

                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={"Content-Type": "application/json"}
                )

                print(f"[*] Calling Google AI Studio API ({model_name})...")
                try:
                    with urllib.request.urlopen(req, timeout=60) as resp:
                        data = json.loads(resp.read().decode("utf-8"))
                        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
                        cleaned_text = clean_for_tts(raw_text)

                        first_few_words = " ".join(cleaned_text.split()[:8])
                        title = custom_topic if custom_topic else f"श्रीकृष्ण वाणी — {first_few_words}..."

                        print(f"✓ Successfully generated script ({len(cleaned_text.split())} words) via {model_name}!")
                        return cleaned_text, title
                except urllib.error.HTTPError as e:
                    print(f"⚠️ {model_name} attempt {attempt+1} failed ({e.code} {e.reason}).")
                    time.sleep(2)
                except Exception as e:
                    print(f"⚠️ Error with {model_name}: {e}.")
                    time.sleep(2)

    # 2. Fallback to Groq API if Gemini is temporarily rate limited
    if groq_keys:
        print("[*] Gemini busy. Activating Groq high-speed fallback engine...")
        for gkey in groq_keys:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                payload = json.dumps({
                    "model": "llama-3.3-70b-versatile",
                    "messages": [
                        {"role": "system", "content": master_prompt},
                        {"role": "user", "content": user_instruction}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 3000
                }).encode("utf-8")

                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {gkey}",
                        "Content-Type": "application/json"
                    }
                )
                with urllib.request.urlopen(req, timeout=45) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    raw_text = data["choices"][0]["message"]["content"]
                    cleaned_text = clean_for_tts(raw_text)
                    first_few_words = " ".join(cleaned_text.split()[:8])
                    title = custom_topic if custom_topic else f"श्रीकृष्ण वाणी — {first_few_words}..."
                    print(f"✓ Successfully generated script ({len(cleaned_text.split())} words) via Groq Llama 3.3 70B!")
                    return cleaned_text, title
            except Exception as e:
                print(f"⚠️ Groq error: {e}")

    raise RuntimeError("Failed to generate script across all available AI engines.")

if __name__ == "__main__":
    script, title = generate_hypnotic_script()
    print("\n--- SCRIPT PREVIEW (FIRST 250 CHARS) ---")
    print(script[:250])
