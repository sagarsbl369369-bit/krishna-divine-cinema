"""
Groq Deep Research Agent for Shrimad Bhagavad Gita Production Engine
-------------------------------------------------------------------
Autonomous deep research and philosophical intelligence engine:
- Powered by Groq Cloud API (Llama 3.3 70B Versatile / DeepSeek R1 Distill)
- 300+ Tokens/Sec Free Tier Throughput
- In-depth investigation of:
    1. Classical Commentaries (Adi Shankara Advaita, Ramanujacharya, Abhinavagupta)
    2. Psychological Diagnostics (Arjuna's Grief, Clinical Burnout, Cognitive Dissonance, Carl Jung)
    3. Scientific & Cosmic Parallels (Quantum Theory, Entropy, Determinism vs Free Will)
    4. 0-5 Second Visceral Hook Formulation (Shocking premise, sonic sting, visual impact)
- Compiles structured intelligence dossiers for Gemini Script Architect.
"""

import os
import sys
import json
import time
from typing import Dict, Any, Optional
import requests

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
DOSSIER_DIR = os.path.join(BASE_DIR, "renders", "research_dossiers")
os.makedirs(DOSSIER_DIR, exist_ok=True)

DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
REASONING_GROQ_MODEL = "deepseek-r1-distill-llama-70b"

def get_groq_key() -> Optional[str]:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                key = cfg.get("GROQ_API_KEY")
                if key and not key.startswith("YOUR_"):
                    return key.strip()
        except Exception:
            pass
    return os.environ.get("GROQ_API_KEY")

class GroqDeepResearchAgent:
    def __init__(self):
        self.api_key = get_groq_key()

    def is_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10)

    def conduct_deep_research(self, topic_or_chapter: str, target_duration_mins: int = 30) -> Dict[str, Any]:
        """
        Executes an exhaustive, multi-dimensional spiritual research protocol.
        """
        print(f"\n==================================================================")
        print(f"🔬 GROQ DEEP RESEARCH AGENT ACTIVATED")
        print(f"📖 Subject: {topic_or_chapter}")
        print(f"⏱️ Target Video Duration: {target_duration_mins} Minutes")
        print(f"==================================================================")

        if not self.is_configured():
            print("   [*] Groq API Key not detected in config.json. Generating High-Fidelity Vedantic Research Dossier...")
            return self._generate_builtin_scholar_dossier(topic_or_chapter, target_duration_mins)

        # Call Groq API via direct REST or SDK
        print(f"   [⚡] Querying Groq Cloud API ({DEFAULT_GROQ_MODEL} at 300+ tok/s)...")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        system_prompt = (
            "You are the world's foremost scholar on Shrimad Bhagavad Gita, Advaita Vedanta, "
            "comparative philosophy, and depth psychology (Carl Jung). "
            "Your mission is to perform a rigorous, 1000x deep research investigation for a cinematic documentary. "
            "Do NOT provide a shallow summary. Provide profound, intellectually piercing, emotionally gripping research. "
            "Respond in valid JSON format with the following keys:\n"
            "{\n"
            "  'topic': str,\n"
            "  'hook_strategy': {\n"
            "    'hook_premise': 'Shocking 0-5s opening question that challenges common spiritual cliches',\n"
            "    'visceral_visual_cue': 'Exact dramatic 4K visual scene description (Kurukshetra war conch, lightning, etc.)',\n"
            "    'sonic_sting': 'Sound design cue (40Hz sub-drop, war horn, conch echo)'\n"
            "  },\n"
            "  'core_shlokas': [\n"
            "    {'sanskrit': '...', 'transliteration': '...', 'deep_philosophical_meaning': '...'}\n"
            "  ],\n"
            "  'classical_commentaries': {\n"
            "    'adi_shankara': 'Advaita non-dualist perspective on illusion and true Self',\n"
            "    'ramanuja': 'Bhakti and divine surrender perspective',\n"
            "    'abhinavagupta': 'Kashmir Shaivism / dramatic existential catharsis perspective'\n"
            "  },\n"
            "  'psychological_parallels': {\n"
            "    'arjuna_condition': 'Clinical breakdown: somatic symptoms, paralysis of will',\n"
            "    'modern_burnout': 'How this matches 21st-century anxiety, career collapse, and relationship grief',\n"
            "    'jungian_shadow': 'Confronting inner demons and moral ambiguity'\n"
            "  },\n"
            "  'scientific_parallels': 'Quantum physics, observer effect, entropy, thermodynamics of Karma',\n"
            "  'narrative_chapters': [\n"
            "    {'chapter_num': 1, 'theme': '...', 'dramatic_tension': '...', 'key_exposition_hindi': '...'}\n"
            "  ]\n"
            "}"
        )

        user_prompt = (
            f"Conduct exhaustive research on: '{topic_or_chapter}'.\n"
            f"Target production runtime: {target_duration_mins} minutes.\n"
            f"Provide at least 3-5 core shlokas and detailed psychological depth."
        )

        payload = {
            "model": DEFAULT_GROQ_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.5,
            "response_format": {"type": "json_object"},
            "max_tokens": 4096
        }

        try:
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                result = r.json()
                content = result["choices"][0]["message"]["content"]
                dossier = json.loads(content)
                self._save_dossier(topic_or_chapter, dossier)
                print(f"   [✓] Groq Deep Research Complete! Dossier generated successfully.")
                return dossier
            else:
                print(f"   [!] Groq API returned status {r.status_code}: {r.text[:200]}")
                return self._generate_builtin_scholar_dossier(topic_or_chapter, target_duration_mins)
        except Exception as e:
            print(f"   [!] Groq connection notice ({e}). Falling back to internal Vedantic dossier...")
            return self._generate_builtin_scholar_dossier(topic_or_chapter, target_duration_mins)

    def _generate_builtin_scholar_dossier(self, topic: str, duration_mins: int) -> Dict[str, Any]:
        """Built-in scholar-grade research dossier when Groq key is pending."""
        dossier = {
            "topic": topic,
            "hook_strategy": {
                "hook_premise": "क्या कुरुक्षेत्र केवल एक ऐतिहासिक युद्ध था, या यह हर उस इंसान के मस्तिष्क का द्वंद्व है जो कर्तव्य और मोह के बीच टूट चुका है?",
                "visceral_visual_cue": "अंधेरे युद्धक्षेत्र पर अचानक बिजली गिरना, अर्जुन के कांपते हाथों से गांडीव का भूमि पर गिरना, और कृष्ण के रथ के पहियों के पास धूल का बवंडर।",
                "sonic_sting": "गंभीर शंखनाद + 40Hz सब-बास ड्राप + बिजली की गर्जना"
            },
            "core_shlokas": [
                {
                    "sanskrit": "सीदन्ति मम गात्राणि मुखं च परिशुष्यति। वेपथुश्च शरीरे मे रोमहर्षश्च जायते॥ गाण्डीवं स्रंसते हस्तात्त्वक्चैव परिदह्यते।",
                    "deep_philosophical_meaning": "विषादयोग: जब आत्मा अपने नश्वर संबंधों में इतनी उलझ जाती है कि उसका विवेक शून्य हो जाता है। यह क्लिनिकल डिप्रेशन और एंग्जायटी का सबसे प्राचीन दस्तावेजीकरण है।"
                },
                {
                    "sanskrit": "नैनं छिन्दन्ति शस्त्राणि नैनं दहति पावकः। न चैनं क्लेदयन्त्यापो न शोषयति मारुतः॥",
                    "deep_philosophical_meaning": "सांख्ययोग: आत्मा की अविनाशी प्रकृति। चेतना (Consciousness) कभी नष्ट नहीं होती, केवल रूप बदलती है (ऊर्जा संरक्षण का नियम - First Law of Thermodynamics)।"
                },
                {
                    "sanskrit": "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥",
                    "deep_philosophical_meaning": "कर्मयोग: परिणाम की चिंता से मुक्त कर्म ही एकमात्र मुक्ति है। जब मन भविष्य के फल में अटकता है, तो वर्तमान की एकाग्रता नष्ट हो जाती है।"
                },
                {
                    "sanskrit": "यतो यतो निश्चरति मनश्चञ्चलमस्थिरम्। ततस्ततो नियम्यैतदात्मन्येव वशं नयेत्॥",
                    "deep_philosophical_meaning": "ध्यानयोग: न्यूरोप्लास्टिसिटी और चित्त-वृत्ति निरोध। चंचल मन को बार-बार खींचकर अंतरात्मा में स्थापित करने की साधना।"
                },
                {
                    "sanskrit": "सर्वधर्मान्परित्यज्य मामेकं शरणं व्रज। अहं त्वां सर्वपापेभ्यो मोक्षयिष्यामि मा शुचः॥",
                    "deep_philosophical_meaning": "मोक्षसंन्यासयोग: पूर्ण शरणागति (Total Surrender)। जब अहं (Ego) समाप्त होता है, तब ब्रह्म से साक्षात्कार होता है।"
                }
            ],
            "classical_commentaries": {
                "adi_shankara": "आदि शंकराचार्य के अनुसार, गीता का एकमात्र लक्ष्य अविद्या (अज्ञान) का नाश करके आत्मज्ञान (अद्वैत) की प्राप्ति कराना है। कर्म केवल चित्त-शुद्धि का साधन है, अंतिम मुक्ति ज्ञान से ही है।",
                "ramanuja": "रामानुजाचार्य के अनुसार, भगवान श्रीकृष्ण की प्रेममयी भक्ति (प्रपत्ति) ही सर्वश्रेष्ठ मार्ग है। जीव और ईश्वर में शाश्वत संबंध है।",
                "abhinavagupta": "अभिनवगुप्त के अनुसार, कुरुक्षेत्र का युद्ध भीतर की चेतना और बाह्य वृत्तियों का संघर्ष है। यह आध्यात्मिक कैथार्सिस (शुद्धिकरण) है।"
            },
            "psychological_parallels": {
                "arjuna_condition": "अर्जुन का कांपना, मुख सूखना और हाथ से धनुष गिरना गंभीर पैनिक अटैक और मोरल बर्नआउट का स्पष्ट उदाहरण है।",
                "modern_burnout": "आज का युवा जब अपने करियर या रिश्तों में भारी दबाव के कारण 'क्विट' करना चाहता है, तो वह आधुनिक अर्जुन है।",
                "jungian_shadow": "कार्ल जुंग के 'शैडो' सिद्धांत के अनुसार, जब तक इंसान अपने भीतर के अंधकार और कठिन निर्णयों का सामना नहीं करता, वह परिपक्व नहीं हो सकता।"
            },
            "scientific_parallels": "क्वांटम भौतिकी के अनुसार प्रेक्षक (Observer) ही वास्तविकता को निर्धारित करता है। गीता की साक्षी चेतना (Witness Consciousness) क्वांटम ऑब्जर्वर सिद्धांत से 100% मेल खाती है।",
            "narrative_chapters": [
                {
                    "chapter_num": 1,
                    "theme": "अर्जुनविषादयोग - भीतर का महासंग्राम",
                    "dramatic_tension": "योद्धा का पतन और अस्तित्ववादी संकट",
                    "key_exposition_hindi": "कुरुक्षेत्र के विशाल रणक्षेत्र में जब शंखों की गूंज और वीरों की ललकार उठी, तब दोनों सेनाओं के मध्य में महारथी अर्जुन का मन मोह और विषाद से घिर गया..."
                },
                {
                    "chapter_num": 2,
                    "theme": "सांख्ययोग - आत्मा की अमरता और निष्काम कर्म",
                    "dramatic_tension": "मृत्यु के भय का विनाश",
                    "key_exposition_hindi": "भगवान श्री कृष्ण ने मुस्कुराते हुए कहा: हे अर्जुन, यह शरीर वस्त्र की भांति नश्वर है, किंतु आत्मा शाश्वत, अजन्मा और अविनाशी है..."
                },
                {
                    "chapter_num": 3,
                    "theme": "कर्मयोग - कर्म की पराकाष्ठा",
                    "dramatic_tension": "आलस्य बनाम कर्तव्य",
                    "key_exposition_hindi": "कर्म से कोई भी प्राणी एक क्षण भी मुक्त नहीं रह सकता। निष्काम भाव से किया गया कर्म ही जीवन का सर्वोच्च यज्ञ है..."
                },
                {
                    "chapter_num": 4,
                    "theme": "ध्यानयोग - अशांत मन की विजय",
                    "dramatic_tension": "भटकते विचारों को वश में करने की कला",
                    "key_exposition_hindi": "जैसे वायु के झोंकों में दीपक की लौ नहीं डोलती, वैसे ही एकाग्र योगी का मन परमात्मा में स्थिर हो जाता है..."
                },
                {
                    "chapter_num": 5,
                    "theme": "मोक्षसंन्यासयोग - परम समर्पण और अखंड शांति",
                    "dramatic_tension": "अहंकार का विसर्जन और विजय",
                    "key_exposition_hindi": "सभी संशयों, चिंताओं और अहंकार को त्यागकर जो परमात्मा की शरण में आता है, वह संपूर्ण भयों से मुक्त होकर परम पद को प्राप्त करता है..."
                }
            ]
        }
        self._save_dossier(topic, dossier)
        return dossier

    def _save_dossier(self, topic: str, dossier: dict):
        clean_name = "".join(c if c.isalnum() else "_" for c in topic)[:30]
        fname = f"dossier_{clean_name}_{int(time.time())}.json"
        fpath = os.path.join(DOSSIER_DIR, fname)
        try:
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(dossier, f, indent=2, ensure_ascii=False)
            print(f"   [📁] Dossier Archived: {fpath}")
        except Exception:
            pass

groq_agent = GroqDeepResearchAgent()

if __name__ == "__main__":
    res = groq_agent.conduct_deep_research("श्रीमद्भगवद्गीता: कर्मयोग और आधुनिक जीवन का तनाव", target_duration_mins=30)
    print("\nGenerated Hook Premise:")
    print(res["hook_strategy"]["hook_premise"])
