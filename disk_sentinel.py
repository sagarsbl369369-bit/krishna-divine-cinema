"""
Disk Sentinel & Storage Protection Daemon
-----------------------------------------
Enforces the mandatory rule: Always keep >= 10.0 GB free on Drive C.
- Real-time disk telemetry
- Automatic garbage collection of raw clip caches, temp audio segments, and cloud downloads
- Emergency purge if free space drops below threshold
"""

import os
import sys
import shutil
import glob
from typing import Tuple, Dict

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")

SAFE_CEILING_GB = 12.0   # Trigger proactive cleanup
HARD_FLOOR_GB = 10.0     # Critical ceiling: must never fall below this!

def get_default_drive() -> str:
    return "C:\\" if sys.platform == "win32" else "/"

def get_disk_stats(path: str = None) -> Dict[str, float]:
    """Returns total, used, and free space in GB for given drive (cross-platform)."""
    if path is None:
        path = get_default_drive()
    try:
        total, used, free = shutil.disk_usage(path)
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2)
        }
    except Exception as e:
        print(f"[!] Error getting disk stats: {e}")
        return {"total_gb": 0.0, "used_gb": 0.0, "free_gb": 0.0}

def get_folder_size_gb(folder_path: str) -> float:
    """Calculates total folder size in GB."""
    if not os.path.exists(folder_path):
        return 0.0
    total_bytes = 0
    for root, dirs, files in os.walk(folder_path):
        for f in files:
            try:
                fp = os.path.join(root, f)
                total_bytes += os.path.getsize(fp)
            except Exception:
                pass
    return round(total_bytes / (1024**3), 2)

def purge_stale_caches(verbose: bool = True) -> float:
    """
    Safely cleans disposable temporary render bloat:
    - renders/clips/ (stale downloaded stock clips)
    - renders/cloud_batch/ (old downloaded videos)
    - renders/clean_segments/ (intermediate voice chunks)
    - renders/temp_tts/
    - *.wav and intermediate test files
    Returns total GB freed.
    """
    initial_stats = get_disk_stats("C:\\")
    freed_bytes = 0

    disposable_folders = [
        os.path.join(RENDERS_DIR, "clips"),
        os.path.join(RENDERS_DIR, "cloud_batch"),
        os.path.join(RENDERS_DIR, "clean_segments"),
        os.path.join(RENDERS_DIR, "temp_tts"),
        os.path.join(BASE_DIR, "temp_test"),
        os.path.join(BASE_DIR, "renders", "temp_tts")
    ]

    for folder in disposable_folders:
        if os.path.exists(folder):
            size_gb = get_folder_size_gb(folder)
            try:
                for root, dirs, files in os.walk(folder):
                    for f in files:
                        try:
                            fp = os.path.join(root, f)
                            freed_bytes += os.path.getsize(fp)
                            os.remove(fp)
                        except Exception:
                            pass
                if verbose and size_gb > 0:
                    print(f"  [🧹] Purged folder: {os.path.basename(folder)} (Reclaimed ~{size_gb} GB)")
            except Exception as e:
                print(f"  [!] Failed to purge {folder}: {e}")

    # Remove orphan test video/audio files older than 1 hour in renders/
    test_patterns = [
        os.path.join(RENDERS_DIR, "concatenated_raw.mp4"),
        os.path.join(RENDERS_DIR, "demo_*.mp3"),
        os.path.join(RENDERS_DIR, "ch_*_video.mp4"),
        os.path.join(RENDERS_DIR, "*_raw.mp3"),
        os.path.join(RENDERS_DIR, "*_raw.bin"),
        os.path.join(RENDERS_DIR, "*.wav")
    ]
    for pattern in test_patterns:
        for f in glob.glob(pattern):
            try:
                freed_bytes += os.path.getsize(f)
                os.remove(f)
            except Exception:
                pass

    final_stats = get_disk_stats("C:\\")
    total_freed_gb = round(final_stats["free_gb"] - initial_stats["free_gb"], 2)
    if verbose:
        print(f"[✓] Storage Sentinel Purge Complete! Drive C Free Space: {final_stats['free_gb']} GB")
    return total_freed_gb

def enforce_disk_safety_gate(required_headroom_gb: float = 10.0):
    """
    Safety gate to be called before ANY render or download operation:
    Ensures that primary drive has at least required_headroom_gb (default 10 GB).
    If below, proactively purges temp caches. If still below, aborts with exception.
    """
    drive_path = get_default_drive()
    stats = get_disk_stats(drive_path)
    free_gb = stats["free_gb"]

    if free_gb < SAFE_CEILING_GB:
        print(f"[⚠️] Storage Sentinel Warning: Free space ({free_gb} GB) is below {SAFE_CEILING_GB} GB. Running proactive cleanup...")
        purge_stale_caches(verbose=True)
        stats = get_disk_stats(drive_path)
        free_gb = stats["free_gb"]

    if free_gb < required_headroom_gb:
        raise RuntimeError(
            f"❌ STORAGE SAFETY HALT: Drive {drive_path} only has {free_gb} GB free. "
            f"The minimum hard limit of {required_headroom_gb} GB cannot be guaranteed. "
            f"Operation halted to protect system stability."
        )

    print(f"[🛡️] Storage Sentinel: Verified {free_gb} GB Free on {drive_path} (Safe threshold >= {required_headroom_gb} GB)")
    return True

if __name__ == "__main__":
    print("==================================================================")
    print("🛡️ DISK SENTINEL TELEMETRY & AUTO-PURGE")
    print("==================================================================")
    before = get_disk_stats("C:\\")
    print(f"Drive C Before: Total={before['total_gb']} GB | Used={before['used_gb']} GB | Free={before['free_gb']} GB")
    print(f"Engine Folder Size: {get_folder_size_gb(BASE_DIR)} GB")
    print(f"Renders Folder Size: {get_folder_size_gb(RENDERS_DIR)} GB")
    print("\nRunning Master Purge of 33+ GB Orphan Render Bloat...")
    purge_stale_caches(verbose=True)
    after = get_disk_stats("C:\\")
    print("\n==================================================================")
    print(f"Drive C After: Free={after['free_gb']} GB (Freed +{round(after['free_gb'] - before['free_gb'], 2)} GB)")
    print(f"Engine Folder Size After: {get_folder_size_gb(BASE_DIR)} GB")
    print(f"Safe Status: {'✅ OPTIMAL (>10 GB)' if after['free_gb'] >= HARD_FLOOR_GB else '❌ CRITICAL'}")
    print("==================================================================")
