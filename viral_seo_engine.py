"""
Viral YouTube SEO & Packaging Engine
------------------------------------
Generates high-CTR, algorithmically optimized packaging for YouTube long-form videos:
1. High-CTR Titles (Curiosity + Emotional Transformation formula).
2. Comprehensive SEO Descriptions with accurate clickable Timestamps/Chapters.
3. High-Ranking Tags (Mix of broad high-volume + niche long-tail, under 500 characters).
4. Cinematic High-Contrast Thumbnail Concept Prompt.
5. Saves SEO Package JSON for YouTube Data API v3 and dashboard 1-click copy.
"""

import os
import sys
import json
import time
from typing import Dict, Any, List
import subprocess

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SEO_DIR = os.path.join(BASE_DIR, "renders", "seo_packages")
os.makedirs(SEO_DIR, exist_ok=True)

HIGH_VOLUME_CORE_TAGS = [
    "Bhagavad Gita",
    "Krishna Vani",
    "Geeta Updesh",
    "Shri Krishna Gyan",
    "Bhagavad Gita in Hindi",
    "Geeta Saar",
    "Karma Yoga",
    "Krishna Motivation",
    "Spiritual Wisdom",
    "Lord Krishna Life Lessons",
    "Inner Peace",
    "Aadhyatmik Gyan",
    "Sanatan Dharma",
    "Mahabharat",
    "Arjuna Krishna Dialogue"
]

def format_timestamp_clock(seconds: float) -> str:
    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    if hours > 0:
        return f"{hours:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

class ViralSEOEngine:
    def __init__(self):
        pass

    def generate_seo_package(self, topic: str, chapters: List[Dict[str, Any]], chapter_durations: List[float] = None) -> Dict[str, Any]:
        """
        Generates full SEO metadata package for YouTube:
        - Click-Worthy Title
        - SEO Description with Timestamps
        - 500-Character Tag list
        - Thumbnail prompt
        """
        print("\n==================================================================")
        print("🚀 GENERATING VIRAL YOUTUBE SEO & METADATA PACKAGE")
        print("==================================================================")

        # 1. Title Formulation (Strictly < 100 characters for YouTube API)
        clean_topic = topic.split("|")[0].strip()
        if len(clean_topic) > 75:
            clean_topic = clean_topic[:72] + "..."
        final_title = f"{clean_topic} | श्रीकृष्ण के अनमोल उपदेश"
        if len(final_title) > 100:
            final_title = final_title[:97] + "..."

        # 2. Generate Chapters Timestamps
        timestamps_lines = []
        current_time = 0.0
        for idx, ch in enumerate(chapters):
            title = ch.get("title", f"अध्याय {idx+1}")
            dur = chapter_durations[idx] if (chapter_durations and idx < len(chapter_durations)) else 190.0
            t_str = format_timestamp_clock(current_time)
            timestamps_lines.append(f"{t_str} - {title}")
            current_time += dur

        if chapter_durations and len(chapter_durations) > len(chapters):
            # Outro timestamp
            t_str = format_timestamp_clock(current_time)
            timestamps_lines.append(f"{t_str} - श्रीकृष्ण महामंत्र व समापन")

        timestamps_block = "\n".join(timestamps_lines)

        # 3. Rich SEO Description
        description = (
            f"🕉️ {final_title}\n\n"
            f"श्रीमद्भगवद्गीता के इस महाकाव्य में जानिए भगवान श्रीकृष्ण के वे गुप्त व गहरे उपदेश "
            f"जो मनुष्य के अंतर्मन के समस्त भय, चिंता, विषाद और संशय को जड़ से समाप्त कर देते हैं। "
            f"कुरुक्षेत्र की रणभूमि में अर्जुन के सामने प्रकट हुआ यह सत्य केवल प्राचीन इतिहास नहीं, "
            f"बल्कि हर मनुष्य के भीतर चलने वाले दैनिक संघर्ष का अंतिम समाधान है।\n\n"
            f"⏱️ महत्वपूर्ण अध्याय और समय-सारणी (Timestamps):\n"
            f"{timestamps_block}\n\n"
            f"📌 इस वीडियो से आपको क्या प्राप्त होगा:\n"
            f"• चित्त की चंचलता और अति-विचार (Overthinking) से मुक्ति\n"
            f"• जीवन में आए संकट और असफलता के समय अटल धैर्य का विज्ञान\n"
            f"• कर्मयोग का यथार्थ स्वरूप: बिना भय और परिणाम की आसक्ति के कर्म करने की कला\n"
            f"• मृत्यु के भय का संहार और आत्मा के अमर स्वरूप का साक्षात्कार\n\n"
            f"🔔 यदि यह ज्ञान आपके हृदय को स्पर्श करे, तो वीडियो को LIKE करें और चैनल को SUBSCRIBE करके सनातन ज्ञान से जुड़ें।\n\n"
            f"#BhagavadGita #KrishnaGyan #GeetaUpdesh #ShriKrishna #SpiritualAwakening #KarmaYoga #SanatanDharma"
        )

        # 4. Tags Compilation (Target 400-480 characters)
        topic_words = [w for w in clean_topic.split() if len(w) > 3][:5]
        custom_tags = HIGH_VOLUME_CORE_TAGS + topic_words
        tags = []
        char_count = 0
        for tag in custom_tags:
            if char_count + len(tag) + 1 < 480:
                tags.append(tag)
                char_count += len(tag) + 1

        # 5. Viral Thumbnail Prompt
        thumb_prompt = (
            f"Cinematic ultra-realistic 8K YouTube thumbnail: Colossal glowing divine silhouette of Lord Krishna "
            f"with peacock feather glowing in cosmic ethereal light, standing behind dark misty battlefield of Kurukshetra. "
            f"Dramatic golden lightning strike, ancient chariot wheel in dust, photorealistic intense atmosphere, "
            f"high contrast, rule of thirds, deep cinematic colors. Text overlay space in top-left."
        )

        package = {
            "title": final_title,
            "description": description,
            "tags": tags,
            "category_id": "27",  # Education / Spirituality
            "privacy_status": "public",
            "thumbnail_prompt": thumb_prompt,
            "timestamps": timestamps_lines,
            "created_at": time.time()
        }

        # Save to file
        clean_name = "".join(c if c.isalnum() else "_" for c in topic)[:30]
        p_path = os.path.join(SEO_DIR, f"seo_{clean_name}_{int(time.time())}.json")
        with open(p_path, "w", encoding="utf-8") as f:
            json.dump(package, f, indent=2, ensure_ascii=False)

        print(f"   [✓] Title: {final_title}")
        print(f"   [✓] Description: Generated with {len(timestamps_lines)} Chapter Timestamps")
        print(f"   [✓] Tags: {len(tags)} high-volume viral tags ({char_count} chars)")
        print(f"   [📁] SEO Package Saved: {p_path}\n")

        return package

viral_seo = ViralSEOEngine()

if __name__ == "__main__":
    sample_ch = [
        {"title": "अध्याय १: जब योद्धा टूट गया"},
        {"title": "अध्याय २: मृत्यु केवल दृष्टिभ्रम है"},
        {"title": "अध्याय ३: कर्म का निर्दयी विज्ञान"}
    ]
    pkg = viral_seo.generate_seo_package("मन को शांत कैसे रखें? | श्रीकृष्ण की सीख", sample_ch, [190.0, 180.0, 195.0])
    print(pkg["title"])
