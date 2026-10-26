# 🕉️ Bhagavad Gita 1000x Automation Engine (16:9 4K)

Automated YouTube Long-form and Shorts generation pipeline specialized in Shrimad Bhagavad Gita, Krishna Updesh, and philosophical life guidance.

## 🚀 Features
- **Voice of God Audio:** Neural Hindi Voice (`hi-IN-MadhurNeural`) with dynamic pitch, cathedral reverb, bass boost, and integrated 432Hz meditative drone.
- **Cinematic 16:9 Motion:** Ken Burns slow zoompan dynamic rendering via FFmpeg.
- **Glowing Gold Subtitles:** Auto-timed Sanskrit and Hindi subtitles styled in divine gold (`#FFD700`) with Nirmala UI / Segoe UI typography.
- **Zero Cost AI:** Free Azure Neural TTS + Free Pollinations/Flux AI artwork + zero external subscription fees.
- **Multi-Channel Scalability:** Ready for 20-instance concurrent execution on GitHub Actions.

## 📁 Project Structure
```
geeta_automation_engine/
│
├── engine.py                 # Core production pipeline (TTS + FX + AI Art + FFmpeg)
├── render_demo.py            # Local demo runner for testing
├── shlokas_db.json           # Curated database of Bhagavad Gita shlokas & hooks
├── channels.json             # Configuration for multiple YouTube channels
├── uploader.py               # Auto-upload engine via YouTube Data API
└── renders/                  # Output directory for generated MP4 videos
```

## ⚡ Quick Start
1. Run demo video:
   ```bash
   python render_demo.py
   ```
2. Video will be saved in `renders/gita_02_47_master_16x9.mp4`.
