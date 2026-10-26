"""
Autonomous 24/7 Krishna Studio Autopilot Daemon Engine
======================================================
Continuous, Zero-Touch Dual-Channel Publishing Beast:
- Hard-Locked Target: 5 Videos Daily on Channel 1 (चैनल १: दिव्य गीता वाणी)
- Hard-Locked Target: 5 Videos Daily on Channel 2 (चैनल २: परम कृष्ण चेतना)
- Total: 10 Epic Long-Form Videos / Day (Each strictly > 30 to 45 Minutes)
- Strict 50/50 Alternating Cadence ("har ek-ek pe ek-ek pe"): ch_01 -> ch_02 -> ch_01 -> ch_02
- Voice: Google AI Studio Free Realistic Gemini TTS ('Charon') + Shure SM7B DSP
- Voice Volume: 150% Mastered Broadcast Level (volume=1.50)
- Subtitles: Smart 24K Gold Fast Devanagari Cards (MarginV=50, Outline=2.8, Shadow=2.0)
- Music: Channel-curated royalty-free devotional soundscape from music_vault
- Delay / Cadence: ~115 to 135 minutes per cycle with organic human jitter
- Daily Counter: Automatically resets to 0/5 every midnight at 00:00:00 IST
- 100% Autonomous, Self-Healing, Non-Stop 24x7 Execution
"""

import os
import sys
import json
import time
import random
import traceback
import subprocess
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)
        sys.stderr.reconfigure(encoding='utf-8', line_buffering=True)
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
os.makedirs(RENDERS_DIR, exist_ok=True)

CONTROL_FILE = os.path.join(RENDERS_DIR, "autopilot_control.json")
DAILY_STATE_FILE = os.path.join(RENDERS_DIR, "autopilot_daily_state.json")
LIVE_STATUS_FILE = os.path.join(RENDERS_DIR, "autopilot_live_status.json")
ROTATION_STATE_FILE = os.path.join(RENDERS_DIR, "channel_rotation_state.json")

IST = timezone(timedelta(hours=5, minutes=30))
DAILY_TARGET_PER_CHANNEL = 5
DEFAULT_DELAY_MINUTES = 115  # Base delay between video runs (~1.9 to 2.2 hrs)
JITTER_MINUTES = 15          # Random human variation (-10 to +15 mins)

def get_current_ist() -> datetime:
    return datetime.now(IST)

def get_today_ist_str() -> str:
    return get_current_ist().strftime("%Y-%m-%d")

class Autopilot24x7Daemon:
    def __init__(self):
        self.control = self.load_control()
        self.state = self.load_state()

    def load_control(self) -> Dict[str, Any]:
        default_control = {
            "enabled": True,
            "paused": False,
            "force_run_now": False,
            "target_per_channel": DAILY_TARGET_PER_CHANNEL,
            "target_duration_mins": 35,
            "research_mins": 10.0,
            "base_delay_mins": DEFAULT_DELAY_MINUTES,
            "privacy": "unlisted",
            "last_command": "init"
        }
        if os.path.exists(CONTROL_FILE):
            try:
                with open(CONTROL_FILE, "r", encoding="utf-8") as f:
                    c = json.load(f)
                    default_control.update(c)
            except Exception:
                pass
        self.save_control(default_control)
        return default_control

    def save_control(self, c: Dict[str, Any]):
        try:
            with open(CONTROL_FILE, "w", encoding="utf-8") as f:
                json.dump(c, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def load_state(self) -> Dict[str, Any]:
        today_str = get_today_ist_str()
        default_state = {
            "date": today_str,
            "counts": {"ch_01": 0, "ch_02": 0},
            "last_channel": "ch_01",
            "total_today": 0,
            "status": "IDLE",
            "current_action": "System Initialized",
            "next_run_timestamp": 0,
            "last_run_timestamp": 0,
            "last_completed_video": {},
            "history": []
        }

        if os.path.exists(DAILY_STATE_FILE):
            try:
                with open(DAILY_STATE_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    # Check if date rolled over past midnight IST
                    if saved.get("date") == today_str:
                        default_state.update(saved)
                    else:
                        print(f"🌅 [MIDNIGHT RESET] New IST Day detected: {today_str}. Resetting daily counts (0/{DAILY_TARGET_PER_CHANNEL})...")
                        default_state["last_channel"] = saved.get("last_channel", "ch_01")
                        default_state["history"] = saved.get("history", [])[-30:]
            except Exception:
                pass

        # Also inspect channel_rotation_state.json for last channel
        if os.path.exists(ROTATION_STATE_FILE):
            try:
                with open(ROTATION_STATE_FILE, "r", encoding="utf-8") as rf:
                    rdata = json.load(rf)
                    default_state["last_channel"] = rdata.get("last_channel", default_state["last_channel"])
            except Exception:
                pass

        self.save_state(default_state)
        return default_state

    def save_state(self, s: Dict[str, Any]):
        try:
            with open(DAILY_STATE_FILE, "w", encoding="utf-8") as f:
                json.dump(s, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def update_live_status(self, action: str, status: str = "RUNNING", next_run_ts: float = 0):
        now_ts = time.time()
        c_1 = self.state["counts"].get("ch_01", 0)
        c_2 = self.state["counts"].get("ch_02", 0)
        target = self.control.get("target_per_channel", DAILY_TARGET_PER_CHANNEL)

        countdown = max(0, int(next_run_ts - now_ts)) if next_run_ts > 0 else 0
        next_run_ist = datetime.fromtimestamp(next_run_ts, tz=IST).strftime("%H:%M:%S IST") if next_run_ts > 0 else "Ready"

        live_data = {
            "enabled": self.control.get("enabled", True),
            "paused": self.control.get("paused", False),
            "status": status,
            "current_action": action,
            "date_ist": get_today_ist_str(),
            "time_ist": get_current_ist().strftime("%H:%M:%S IST"),
            "daily_quota": {
                "ch_01": f"{c_1}/{target}",
                "ch_02": f"{c_2}/{target}",
                "total_today": f"{c_1 + c_2}/{target * 2}",
                "ch_01_done": c_1 >= target,
                "ch_02_done": c_2 >= target,
                "all_done": (c_1 >= target and c_2 >= target)
            },
            "last_channel": self.state.get("last_channel", "ch_01"),
            "next_target_channel": self.determine_next_channel(),
            "next_run_timestamp": next_run_ts,
            "next_run_countdown_seconds": countdown,
            "next_run_ist": next_run_ist,
            "last_run_timestamp": self.state.get("last_run_timestamp", 0),
            "last_completed_video": self.state.get("last_completed_video", {}),
            "history_count": len(self.state.get("history", []))
        }

        try:
            with open(LIVE_STATUS_FILE, "w", encoding="utf-8") as lf:
                json.dump(live_data, lf, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def check_midnight_rollover(self):
        today_str = get_today_ist_str()
        if self.state.get("date") != today_str:
            print(f"\n=======================================================")
            print(f"🌅 [00:00 IST MIDNIGHT ROLLOVER] New Day: {today_str}")
            print(f"Resetting daily publication counters to 0/{DAILY_TARGET_PER_CHANNEL} per channel!")
            print(f"=======================================================\n")
            self.state["date"] = today_str
            self.state["counts"] = {"ch_01": 0, "ch_02": 0}
            self.state["total_today"] = 0
            self.save_state(self.state)

    def determine_next_channel(self) -> str:
        """
        Enforces strict 50/50 alternating cadence between ch_01 and ch_02.
        If one channel reached 5/5 today, the other channel takes remaining runs.
        """
        c_1 = self.state["counts"].get("ch_01", 0)
        c_2 = self.state["counts"].get("ch_02", 0)
        target = self.control.get("target_per_channel", DAILY_TARGET_PER_CHANNEL)
        last_ch = self.state.get("last_channel", "ch_01")

        # Preferred next in alternating sequence
        pref_next = "ch_02" if last_ch == "ch_01" else "ch_01"

        if pref_next == "ch_02" and c_2 < target:
            return "ch_02"
        elif pref_next == "ch_01" and c_1 < target:
            return "ch_01"
        elif c_1 < target:
            return "ch_01"
        elif c_2 < target:
            return "ch_02"
        else:
            return "ALL_COMPLETED"

    def calculate_sleep_seconds(self) -> int:
        """
        Calculates intelligent spacing between videos (~110 to 135 mins)
        with organic jitter so uploads appear human-timed to YouTube algorithms.
        """
        base_mins = self.control.get("base_delay_mins", DEFAULT_DELAY_MINUTES)
        jitter = random.randint(-8, JITTER_MINUTES)
        total_mins = max(45, base_mins + jitter)
        return total_mins * 60

    def calculate_seconds_until_midnight_ist(self) -> int:
        now_ist = get_current_ist()
        tomorrow_midnight = (now_ist + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
        diff = (tomorrow_midnight - now_ist).total_seconds()
        return max(60, int(diff))

    def run_production_cycle(self, target_ch: str) -> Optional[Dict[str, Any]]:
        """
        Executes autonomous production pipeline via autonomous_master_loop.py.
        """
        duration = max(35, self.control.get("target_duration_mins", 35))
        research_mins = max(5.0, self.control.get("research_mins", 10.0))
        privacy = self.control.get("privacy", "unlisted")

        print("\n" + "#" * 80)
        print(f"🚀 [24/7 AUTOPILOT LAUNCH] Starting Cinema Pipeline for {target_ch}")
        print(f"⏱️ Minimum Target Runtime: {duration} Mins (Guaranteed > 30 mins)")
        print(f"🐝 Deep Groq Swarm Research: {research_mins:.1f} Mins")
        print(f"🎙️ Voice Narration Engine: Google Gemini Free Realistic TTS ('Charon')")
        print(f"🔊 Narration Mastered Volume: 150% Studio Boost")
        print(f"✨ Subtitles: Smart 24K Gold Cards (MarginV=50, High Retention)")
        print(f"🎵 Devotional Music: Curated Royalty-Free Soundscape for {target_ch}")
        print(f"📤 YouTube Publishing: Auto Studio Direct UNLISTED Upload")
        print("#" * 80 + "\n")

        self.update_live_status(
            action=f"Rendering & Publishing 30+ Min Cinema Documentary for {target_ch}...",
            status="PIPELINE_ACTIVE"
        )

        cmd = [
            sys.executable, "-u",
            os.path.join(BASE_DIR, "autonomous_master_loop.py"),
            "--channel", target_ch,
            "--duration", str(duration),
            "--research_mins", str(research_mins),
            "--privacy", privacy,
            "--uploader", "auto"
        ]

        start_ts = time.time()
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            cwd=BASE_DIR
        )

        log_lines = []
        for line in iter(proc.stdout.readline, ""):
            if line:
                print(line, end="")
                log_lines.append(line)
        proc.stdout.close()
        proc.wait()

        elapsed = time.time() - start_ts
        if proc.returncode != 0:
            print(f"\n❌ [AUTOPILOT ERROR] Master loop exited with code {proc.returncode} after {elapsed/60:.2f} mins.")
            return None

        # Parse success indicators from output
        full_log = "".join(log_lines)
        yt_url = ""
        topic = ""
        for line in log_lines:
            if "🎉 [HUMAN-MIMICRY SUCCESS] Published! Result:" in line or "https://youtu.be/" in line or "https://youtube.com/watch" in line:
                for token in line.split():
                    if "youtu" in token:
                        yt_url = token.strip()
            if "🎯 SELECTED TOPIC:" in line:
                topic = line.replace("🎯 SELECTED TOPIC:", "").strip().strip("'\"")

        print(f"\n✅ [AUTOPILOT CYCLE COMPLETE] Channel {target_ch} video completed in {elapsed/60:.2f} minutes!")
        if yt_url:
            print(f"🔗 YouTube Live URL: {yt_url}")

        record = {
            "timestamp": time.time(),
            "time_ist": get_current_ist().strftime("%Y-%m-%d %H:%M:%S IST"),
            "channel_id": target_ch,
            "topic": topic,
            "youtube_url": yt_url,
            "duration_mins": round(elapsed / 60, 2),
            "status": "SUCCESS"
        }
        return record

    def start_infinite_daemon(self):
        """
        The Master 24/7 Autopilot Loop. Runs continuously without stopping.
        """
        print("\n" + "=" * 80)
        print("⚡ 24/7 DUAL-CHANNEL AUTOPILOT DAEMON ACTIVATED ⚡")
        print("Target: 5 Videos / Day on Channel 1 + 5 Videos / Day on Channel 2 (10 Daily)")
        print("Strict Alternation: 1-on-1 (ch_01 <--> ch_02) | Duration > 30 Mins | Google Free TTS")
        print("Press Ctrl+C to pause, or toggle 'enabled' in renders/autopilot_control.json")
        print("=" * 80 + "\n")

        while True:
            try:
                # 1. Reload control settings & check rollover
                self.control = self.load_control()
                self.check_midnight_rollover()

                # 2. Check if paused or disabled
                if not self.control.get("enabled", True):
                    print("⏸️ [AUTOPILOT PAUSED] Daemon is in standby ('enabled': false). Waiting 30s...")
                    self.update_live_status("Autopilot is Paused by User", status="PAUSED")
                    time.sleep(30)
                    continue

                if self.control.get("paused", False):
                    print("⏸️ [AUTOPILOT TEMPORARY PAUSE] Waiting 30s...")
                    self.update_live_status("Temporary Pause active", status="PAUSED")
                    time.sleep(30)
                    continue

                # 3. Determine next channel in sequence
                next_ch = self.determine_next_channel()

                # 4. Check if daily quotas are met
                if next_ch == "ALL_COMPLETED":
                    target = self.control.get("target_per_channel", DAILY_TARGET_PER_CHANNEL)
                    c_1 = self.state["counts"].get("ch_01", 0)
                    c_2 = self.state["counts"].get("ch_02", 0)
                    secs_to_midnight = self.calculate_seconds_until_midnight_ist()
                    wake_time = time.time() + secs_to_midnight
                    wake_ist = datetime.fromtimestamp(wake_time, tz=IST).strftime("%H:%M:%S IST")

                    msg = f"🏆 Daily Quota Reached! (ch_01: {c_1}/{target}, ch_02: {c_2}/{target}). Sleeping until {wake_ist}..."
                    print(f"\n{msg}\n")
                    self.update_live_status(msg, status="DAILY_QUOTA_REACHED", next_run_ts=wake_time)

                    # Sleep until midnight in 60s increments to allow graceful control interrupts
                    while time.time() < wake_time:
                        self.control = self.load_control()
                        if not self.control.get("enabled", True) or self.control.get("force_run_now", False):
                            break
                        self.update_live_status(msg, status="DAILY_QUOTA_REACHED", next_run_ts=wake_time)
                        time.sleep(min(60, wake_time - time.time()))
                    continue

                # 5. Check force_run_now flag
                is_forced = self.control.get("force_run_now", False)
                if is_forced:
                    print("⚡ [FORCE RUN TRIGGERED] Bypassing delay timer...")
                    self.control["force_run_now"] = False
                    self.save_control(self.control)

                # 6. Execute Production Pipeline
                print(f"\n🎯 [NEXT UP] Channel: {next_ch} (Today's count: {self.state['counts'].get(next_ch, 0)}/{DAILY_TARGET_PER_CHANNEL})")
                res = self.run_production_cycle(next_ch)

                if res and res.get("status") == "SUCCESS":
                    # Increment count for this channel
                    self.state["counts"][next_ch] = self.state["counts"].get(next_ch, 0) + 1
                    self.state["total_today"] = sum(self.state["counts"].values())
                    self.state["last_channel"] = next_ch
                    self.state["last_run_timestamp"] = time.time()
                    self.state["last_completed_video"] = res
                    self.state.setdefault("history", []).append(res)
                    self.save_state(self.state)

                    c_1 = self.state["counts"].get("ch_01", 0)
                    c_2 = self.state["counts"].get("ch_02", 0)
                    target = self.control.get("target_per_channel", DAILY_TARGET_PER_CHANNEL)
                    print(f"\n📊 [UPDATED DAILY SCOREBOARD] ch_01: {c_1}/{target} | ch_02: {c_2}/{target} (Total: {c_1+c_2}/{target*2})")

                    # Calculate intelligent delay before next video run
                    delay_seconds = self.calculate_sleep_seconds()
                    next_run_ts = time.time() + delay_seconds
                    next_run_str = datetime.fromtimestamp(next_run_ts, tz=IST).strftime("%H:%M:%S IST")

                    sleep_msg = f"Video published! Cadence sleep for {delay_seconds/60:.1f} mins (Next run at {next_run_str})..."
                    print(f"\n⏳ {sleep_msg}\n")
                    self.update_live_status(sleep_msg, status="SLEEPING_CADENCE", next_run_ts=next_run_ts)

                    # Sleep in 15s steps to listen for user toggle / stop / force_run commands
                    while time.time() < next_run_ts:
                        self.control = self.load_control()
                        if not self.control.get("enabled", True):
                            print("⏸️ Autopilot disabled during sleep. Breaking to standby...")
                            break
                        if self.control.get("force_run_now", False):
                            print("⚡ Force run flag detected during sleep! Starting next video immediately...")
                            break
                        self.update_live_status(
                            f"Resting cadence ({int((next_run_ts - time.time())/60)}m remaining). Next: {self.determine_next_channel()}",
                            status="SLEEPING_CADENCE",
                            next_run_ts=next_run_ts
                        )
                        time.sleep(min(15, max(1, next_run_ts - time.time())))
                else:
                    # Pipeline encountered an issue, wait 8 minutes before safe retry
                    err_wait = 480
                    retry_ts = time.time() + err_wait
                    err_msg = f"Pipeline retry wait ({err_wait/60:.1f} mins) following safe failover..."
                    print(f"\n⚠️ {err_msg}\n")
                    self.update_live_status(err_msg, status="RETRY_COOLDOWN", next_run_ts=retry_ts)
                    time.sleep(err_wait)

            except KeyboardInterrupt:
                print("\n🛑 [AUTOPILOT STOPPED] Daemon received interrupt signal. Exiting safely.")
                self.update_live_status("Autopilot stopped by user interrupt", status="STOPPED")
                break
            except Exception as e:
                print(f"\n💥 [CRITICAL DAEMON EXCEPTION]: {e}")
                traceback.print_exc()
                print("Self-healing in 60 seconds...")
                time.sleep(60)

if __name__ == "__main__":
    daemon = Autopilot24x7Daemon()
    daemon.start_infinite_daemon()
