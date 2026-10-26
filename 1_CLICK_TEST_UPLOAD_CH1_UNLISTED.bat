@echo off
title Autonomous YouTube Uploader - Demo Test Run
color 0A
cls
echo ======================================================================
echo 🤖 LIVE DEMO UPLOAD: CHANNEL 1 (DIVYA GITA VANI) - UNLISTED
echo ======================================================================
echo.
echo Video:   32.74 Min Full-HD Master Documentary (No Subtitles)
echo Thumb:   24K Gold 3-Word Safe-Zone UHD Thumbnail
echo SEO:     10 Chapters Clickable Timestamps + 500-char Tags
echo Privacy: UNLISTED (Safe Test Mode)
echo.
echo Launching visible Chrome window so you can watch live...
echo ======================================================================
cd /d "%~dp0"
python youtube_human_uploader.py --upload --visible --channel ch_01 --privacy unlisted
echo.
echo ======================================================================
echo Upload completed! Press any key to close.
echo ======================================================================
pause
