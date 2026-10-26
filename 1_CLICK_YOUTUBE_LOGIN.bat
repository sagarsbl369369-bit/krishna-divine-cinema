@echo off
title YouTube Studio One-Time Login
color 0E
cls
echo ======================================================================
echo 🕉️ YOUTUBE STUDIO HUMAN-MIMICRY ONE-TIME LOGIN
echo ======================================================================
echo.
echo Opening Google Chrome directly to studio.youtube.com...
echo.
echo 👉 Please sign in to your YouTube channel in the opened Chrome window.
echo.
echo 💾 Your login session will be permanently saved in:
echo    credentials\youtube_browser_profile
echo.
echo ======================================================================
cd /d "%~dp0"
start chrome.exe --user-data-dir="%~dp0credentials\youtube_browser_profile" "https://studio.youtube.com"
echo Chrome launched successfully!
echo.
echo When you finish logging in to YouTube Studio, press any key to verify session:
pause
python youtube_human_uploader.py --check
pause
