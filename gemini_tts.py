"""
Voiceover Synthesis Engine Router
Automatically redirects all calls to the permanently locked Edge-TTS + Shure SM7B DSP Engine.
"""

import os
import sys
import asyncio
from shure_sm7b_dsp_engine import (
    synthesize_shure_sm7b_audio,
    generate_proportional_subtitles
)

async def generate_gemini_speech(text: str, output_audio: str, output_srt: str):
    """
    Redirects to Edge-TTS + Shure SM7B DSP (LOCKED).
    100% Plain Hindi narration with zero quotas or rate limits.
    """
    print("[🎙️] Routing to Locked Edge-TTS + Shure SM7B DSP Audio Engine...")
    dur = synthesize_shure_sm7b_audio(text, output_audio)
    generate_proportional_subtitles(text, dur, output_srt)
    print(f"[✓] Voiceover Mastered: {output_audio} ({dur:.2f}s)")
    return dur

if __name__ == "__main__":
    t = "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।"
    oa = os.path.join(os.path.dirname(__file__), "renders", "test_routed_voice.mp3")
    osrt = os.path.join(os.path.dirname(__file__), "renders", "test_routed_voice.srt")
    asyncio.run(generate_gemini_speech(t, oa, osrt))
