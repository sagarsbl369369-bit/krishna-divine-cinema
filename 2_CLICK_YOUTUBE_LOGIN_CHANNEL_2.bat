@echo off
title YouTube Studio Channel 2 Switcher (Geeta Jeevan Sutra)
color 0B
cls
echo ======================================================================
echo 🕉️ YOUTUBE STUDIO CHANNEL 2 (GEETA JEEVAN SUTRA) SWITCHER
echo ======================================================================
echo.
echo Opening YouTube Channel Switcher in Chrome...
echo.
echo 👉 Chrome khulega jisme aapka account pehle se logged-in hai!
echo 👉 Aapko bas 'Geeta Jeevan Sutra' channel par 1 CLICK karna hai!
echo.
echo ======================================================================
start chrome.exe --user-data-dir="%~dp0credentials\youtube_browser_profile_ch_02" "https://www.youtube.com/channel_switcher"
echo.
echo Chrome khul chuka hai!
echo 'Geeta Jeevan Sutra' par click karne ke baad Chrome window ko close kar dein aur yahan koi bhi key dabayein:
pause
cd /d "%~dp0"
python youtube_human_uploader.py --check --channel ch_02
pause
