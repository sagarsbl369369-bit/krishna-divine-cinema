"""
Autonomous Krishna Gyan Topic Brain & Viral Trend Intelligence
--------------------------------------------------------------
Autonomously generates, discovers, and selects high-CTR, deeply philosophical,
and soul-stirring Krishna Updesh topics based on:
1. Deep human existential crises (Overthinking, betrayal, failure, loneliness, death, ego).
2. YouTube search trends and high-retention viral formulas (10M-50M views).
3. Anti-repetition Evolutionary Knowledge Graph (Tracks used topics and ensures every video is 10x deeper and distinct).
"""

import os
import sys
import json
import time
import random
from typing import Dict, Any, List
from groq_key_pool import groq_pool

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOPIC_HISTORY_PATH = os.path.join(BASE_DIR, "renders", "topic_evolution_graph.json")

# Core Existential Archetypes rooted in Shrimad Bhagavad Gita
EXISTENTIAL_ARCHETYPES = [
    {
        "category": "चित्त की चंचलता और अति-विचार",
        "human_pain": "Overthinking, restlessness, mental chaos, inability to silence the mind.",
        "gita_source": "छठा अध्याय (ध्यानयोग) - चंचलं हि मनः कृष्ण प्रमाथि बलवद् दृढम्",
        "sample_angles": [
            "मन को शांत कैसे रखें? जब विचारों की आंधी दिमाग को फाड़ दे तो श्रीकृष्ण का यह एक कठोर सत्य सुन लो",
            "चित्त की चंचलता का अंत: श्रीकृष्ण ने अर्जुन को मन को वश में करने की कौन सी गुप्त विद्या दी थी?",
            "अति-विचार से मुक्ति: जब तुम्हारा ही दिमाग तुम्हारा सबसे बड़ा शत्रु बन जाए"
        ]
    },
    {
        "category": "विषाद, अकेलापन और जीवन में सब खत्म हो जाना",
        "human_pain": "Deep existential depression, betrayal by loved ones, acute loneliness, hopelessness.",
        "gita_source": "प्रथम व द्वितीय अध्याय - अर्जुनविषादयोग एवं सांख्ययोग",
        "sample_angles": [
            "जब जिंदगी में सब कुछ टूट जाए और कोई रास्ता न दिखे... श्रीकृष्ण का यह एक नियम सुन लो",
            "अपमान, असफलता और अकेलापन: जब अपनों ने ही पीठ में छुरा घोंप दिया हो तब गीता क्या कहती है?",
            "कायरता को दया मत समझो: श्रीकृष्ण का वह कठोर प्रहार जो टूटे हुए इंसान को फिर से योद्धा बना दे"
        ]
    },
    {
        "category": "कर्म की निर्दयी नियति और फल की आसक्ति",
        "human_pain": "Fear of failure, burning out in career, feeling unrewarded despite honest hard work.",
        "gita_source": "तृतीय व चतुर्थ अध्याय - कर्मयोग एवं ज्ञानकर्मसंन्यासयोग",
        "sample_angles": [
            "अच्छे लोगों के साथ ही बुरा क्यों होता है? श्रीकृष्ण ने दिया कर्मा का निर्दयी और वैज्ञानिक उत्तर",
            "फल की भीख मांगना बंद करो: श्रीकृष्ण का कर्मयोग जो मनुष्य को हर असफलता के भय से मुक्त कर दे",
            "कर्म का रहस्य: क्या तुम्हारा भाग्य पहले से तय है या तुम अपनी नियति के स्वयं विधाता हो?"
        ]
    },
    {
        "category": "मृत्यु का भय, काल का संहार और चेतना की अमरता",
        "human_pain": "Fear of aging, loss of parents/loved ones, anxiety about mortality and impermanence.",
        "gita_source": "द्वितीय व एकादश अध्याय - सांख्ययोग एवं विश्वरूपदर्शनयोग",
        "sample_angles": [
            "मृत्यु केवल एक दृष्टिभ्रम है: श्रीकृष्ण का वह अंतिम सत्य जो मृत्यु के भय को भी थरथरा दे",
            "काल का महाविनाश: जब अर्जुन ने श्रीकृष्ण का वह भयानक रूप देखा जिसने उसके होश उड़ा दिए",
            "शरीर मरता है तुम कभी नहीं मर सकते: चेतना की वह अमरता जो हर सांसारिक भय को भस्म कर दे"
        ]
    },
    {
        "category": "अहंकार का विनाश और आत्म-साक्षात्कार",
        "human_pain": "Ego battles, identity crisis, seeking validation from others, inner emptiness.",
        "gita_source": "सप्तम व नवम अध्याय - ज्ञानविज्ञानयोग एवं राजविद्याराजगुह्ययोग",
        "sample_angles": [
            "संसार के सबसे बड़े धोखे से मुक्ति: तुम वह नहीं हो जो तुम खुद को शीशे में देखते हो",
            "अहंकार की चिता पर ही शांति का जन्म होता है: श्रीकृष्ण की सीख जो इंसान की आंखें खोल दे",
            "जो मुझमें समर्पित है उसका विनाश कभी नहीं: जीवन में अंतिम निर्भयता प्राप्त करने का रहस्य"
        ]
    }
]

def load_topic_history() -> List[str]:
    if os.path.exists(TOPIC_HISTORY_PATH):
        try:
            with open(TOPIC_HISTORY_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("used_topics", [])
        except Exception:
            return []
    return []

def save_topic_history(used_topics: List[str]):
    os.makedirs(os.path.dirname(TOPIC_HISTORY_PATH), exist_ok=True)
    with open(TOPIC_HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump({"used_topics": used_topics, "last_updated": time.time()}, f, indent=2, ensure_ascii=False)

class AutonomousTopicBrain:
    def __init__(self):
        self.used_topics = load_topic_history()

    def discover_next_viral_topic(self, channel_id: str = None) -> Dict[str, Any]:
        """
        Uses Groq AI to autonomously formulate a brand-new, high-CTR, existential Krishna Updesh topic
        tailored specifically to the target channel (ch_01 vs ch_02) that has NEVER been used before.
        """
        print("\n==================================================================")
        print("🧠 AUTONOMOUS KRISHNA TOPIC BRAIN (VIRAL SEO & HUMAN PSYCHOLOGY)")
        print(f"🎯 Target Channel: {channel_id or 'Auto-Rotation'}")
        print("==================================================================")

        # Select archetypes based on channel niche
        if channel_id == "ch_01":
            # Mind control, Overthinking, Overcoming defeat, Karma
            eligible = [EXISTENTIAL_ARCHETYPES[0], EXISTENTIAL_ARCHETYPES[1], EXISTENTIAL_ARCHETYPES[2]]
        elif channel_id == "ch_02":
            # Cosmic truth, Death, Maya, Ego dissolution, Vishwaroop
            eligible = [EXISTENTIAL_ARCHETYPES[3], EXISTENTIAL_ARCHETYPES[4]]
        else:
            eligible = EXISTENTIAL_ARCHETYPES

        archetype = random.choice(eligible)
        recent_used = self.used_topics[-20:] if len(self.used_topics) > 20 else self.used_topics

        prompt = (
            f"You are the world's greatest Vedic YouTube Content Strategist and Hindu Philosopher.\n"
            f"Target Category: {archetype['category']}\n"
            f"Core Human Pain Point: {archetype['human_pain']}\n"
            f"Gita Reference: {archetype['gita_source']}\n\n"
            f"PREVIOUSLY USED TOPICS (DO NOT REPEAT ANY OF THESE):\n"
            f"{json.dumps(recent_used, ensure_ascii=False)}\n\n"
            f"TASK: Generate 1 completely NEW, soul-shaking, high-CTR YouTube Video Topic and Core Thesis.\n"
            f"STRICT RULES:\n"
            f"1. ZERO MODERN ENGLISH WORDS: No Hinglish, no words like 'focus', 'mindset', 'overthinking', 'depression'.\n"
            f"2. ZERO SANSKRIT SHLOKA CHANTING: Spoken words will be pure profound Hindi.\n"
            f"3. ZERO KURUKSHETRA / ZERO ANCIENT WAR TROPES: Absolutely NO chariots, NO Gandiva, NO Arjun, NO battlefield references. 100% REAL-LIFE HUMAN PSYCHOLOGY that connects directly to daily human life (3 AM overthinking, fake friends, loneliness, career burnout, emotional sovereignty).\n"
            f"4. Must promise a definitive, mind-bending ('इंसान का दिमाग हिला देने वाला') logical revelation.\n"
            f"5. Output MUST be ONLY valid JSON in format:\n"
            f"{{\n"
            f"  \"topic_title\": \"जब जिंदगी में सब खत्म लगने लगे... यह एक कड़वा सत्य सुन लो\",\n"
            f"  \"core_thesis\": \"मनुष्य दुख से नहीं, बल्कि सुख और वफादारी की झूठी अपेक्षा से पीड़ित है...\",\n"
            f"  \"target_duration_mins\": 35,\n"
            f"  \"emotional_trigger\": \"गहन विषाद और आंतरिक पराजय का संहार\",\n"
            f"  \"viral_hook_line\": \"तुम रात को तीन बजे छत को घूरते हुए किस बात का मातम मना रहे हो? उस इंसान का जिसने तुम्हें कचरे की तरह फेंक दिया?\"\n"
            f"}}"
        )

        candidate_models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]
        for model in candidate_models:
            try:
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "You are a master Vedic strategist. Output ONLY valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.75,
                    "max_tokens": 800
                }
                res = groq_pool.post_chat_completion(payload)
                raw = res["choices"][0]["message"]["content"].strip()
                if raw.startswith("```"):
                    raw = raw.split("\n", 1)[1]
                if raw.endswith("```"):
                    raw = raw.rsplit("\n", 1)[0]
                start_i = raw.find("{")
                end_i = raw.rfind("}")
                if start_i != -1 and end_i != -1:
                    topic_data = json.loads(raw[start_i:end_i+1])
                    t_title = topic_data.get("topic_title", "").strip()
                    if t_title:
                        self.used_topics.append(t_title)
                        save_topic_history(self.used_topics)
                        print(f"   [✓] Discovered New Viral Topic: '{t_title}'")
                        print(f"   [📖] Category: {archetype['category']}")
                        print(f"   [🎯] Emotional Trigger: {topic_data.get('emotional_trigger')}")
                        return topic_data
            except Exception as e:
                continue

        # Fallback to curated archetype sample if offline
        fallback_title = random.choice(archetype["sample_angles"])
        self.used_topics.append(fallback_title)
        save_topic_history(self.used_topics)
        return {
            "topic_title": fallback_title,
            "core_thesis": archetype["human_pain"],
            "target_duration_mins": 35,
            "emotional_trigger": archetype["category"],
            "viral_hook_line": "जब दुनिया के सबसे बड़े योद्धा ने कांपते हाथों से गांडीव डाल दिया..."
        }

autonomous_brain = AutonomousTopicBrain()

if __name__ == "__main__":
    t = autonomous_brain.discover_next_viral_topic()
    print("\nResult Topic Data:")
    print(json.dumps(t, indent=2, ensure_ascii=False))
