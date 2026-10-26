@echo off
title YouTube Studio Channel 2 Login (Premanand Ji Vichar)
color 0B
cls
echo ======================================================================
echo 🕉️ YOUTUBE STUDIO CHANNEL 2 (PREMANAND JI VICHAR) ONE-TIME LOGIN
echo ======================================================================
echo.
echo Opening Google Chrome for Channel 2...
echo 👉 Please sign in to your SECOND YouTube channel in the opened Chrome window.
echo.
echo 💾 Your session for Channel 2 will be permanently saved in:
echo    credentials\youtube_browser_profile_ch_02
echo ======================================================================
cd /d "%~dp0"
start chrome.exe --user-data-dir="%~dp0credentials\youtube_browser_profile_ch_02" "https://studio.youtube.com"
echo.
echo Chrome for Channel 2 launched successfully!
echo.
echo When you finish logging in to Channel 2, press any key to verify:
pause
python youtube_human_uploader.py --check --channel ch_02
pause
