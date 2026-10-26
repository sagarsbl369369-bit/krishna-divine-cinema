import json
import sys
import os
from scalable_script_architect import script_architect

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

topic = "जब दिमाग में विचारों की आंधी मच जाए... श्रीकृष्ण का यह एक नियम सुन लो"
dossier = {
    "viral_youtube_mechanics": {
        "core_thesis": "अति-विचार और चित्त की अशांति मनुष्य के वास्तविक संकट से नहीं, बल्कि उसकी अनियंत्रित मानसिक कल्पनाओं और नियंत्रण की तृष्णा से उत्पन्न होती है।",
        "emotional_trigger": "मानसिक विषाद, अकेलापन, और अनिद्रा की अवस्था में चित्त का भटकाव",
        "human_pain": "Overthinking, mental exhaustion, panic about the future, inability to silence the mind"
    }
}

print(f"Generating 10-Chapter Master Counter-Script for: '{topic}'...")
chapters = script_architect.generate_scalable_script(topic, target_duration_mins=36, research_dossier=dossier)

total_words = sum(len(c.get("exposition", "").split()) for c in chapters)
print(f"Generated {len(chapters)} Chapters! Total Words: {total_words}")

out_path = os.path.join(os.path.dirname(__file__), "counter_masterpiece_100x_script.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(chapters, f, indent=2, ensure_ascii=False)

print(f"Saved complete script to {out_path}")
