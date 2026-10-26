"""
🕉️ Supreme Bhagavad Gita Video Production Engine - Professional Mission Control Dashboard
Full-stack FastAPI + Modern Glassmorphism Dark UI with Real-Time SSE Log Streaming,
Shure SM7B DSP Sound Studio, Video Previewer, 10-Agent Groq Swarm Deep Research & Multi-Key Pool Manager.
"""

import os
import sys
import json
import time
import asyncio
import subprocess
from typing import Optional
from fastapi import FastAPI, Request, BackgroundTasks, Body
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from gemini_key_pool import gemini_pool
from groq_key_pool import groq_pool
from groq_swarm_researcher import groq_swarm
from scalable_script_architect import script_architect
from hook_engine import hook_engine
from youtube_channel_manager import channel_manager

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RENDERS_DIR = os.path.join(BASE_DIR, "renders")
CLIPS_DIR = os.path.join(RENDERS_DIR, "clips")
CHAPTERS_DIR = os.path.join(RENDERS_DIR, "chapters")
CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
LOCK_FILE = os.path.join(RENDERS_DIR, "used_visual_ids.json")
MASTER_VIDEO_PATH = os.path.join(RENDERS_DIR, "epic_bhagavad_gita_documentary_master.mp4")

app = FastAPI(title="Bhagavad Gita Production Studio Dashboard")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global State for Live Engine Execution
current_process: Optional[subprocess.Popen] = None
log_lines = []
is_rendering = False
render_mode = "idle"

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(cfg: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)

def get_used_clips_count() -> int:
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return len(data.get("used_ids", []))
        except Exception:
            pass
    return 0

def get_video_info(path: str) -> dict:
    if not os.path.exists(path):
        return {"exists": False}
    try:
        cmd = [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration,size,bit_rate:stream=codec_name,width,height,r_frame_rate,channels,sample_rate",
            "-of", "json", path
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(res.stdout)
        dur = float(data.get("format", {}).get("duration", 0))
        size_bytes = int(data.get("format", {}).get("size", os.path.getsize(path)))
        v_stream = next((s for s in data.get("streams", []) if s.get("codec_name") in ["h264", "hevc", "vp9"]), {})
        a_stream = next((s for s in data.get("streams", []) if s.get("codec_name") in ["aac", "mp3", "opus"]), {})
        return {
            "exists": True,
            "duration_sec": dur,
            "duration_fmt": f"{int(dur // 60)}m {int(dur % 60)}s",
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "width": v_stream.get("width", 1280),
            "height": v_stream.get("height", 720),
            "video_codec": v_stream.get("codec_name", "h264"),
            "audio_codec": a_stream.get("codec_name", "aac"),
            "channels": a_stream.get("channels", 1),
            "sample_rate": a_stream.get("sample_rate", "48000"),
            "mtime": time.ctime(os.path.getmtime(path))
        }
    except Exception as e:
        return {"exists": True, "error": str(e), "size_mb": round(os.path.getsize(path)/(1024*1024), 2)}

def run_engine_process(script_name: str, mode_name: str, extra_args: list = None):
    global current_process, is_rendering, render_mode, log_lines
    is_rendering = True
    render_mode = mode_name
    log_lines.clear()
    log_lines.append(f"⚡ [DASHBOARD] Launching {mode_name} ({script_name})...\n")

    script_path = os.path.join(BASE_DIR, script_name)
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    cmd = [sys.executable, "-u", script_path]
    if extra_args:
        cmd.extend(extra_args)

    current_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
        env=env
    )

    try:
        for line in iter(current_process.stdout.readline, ''):
            if line:
                log_lines.append(line)
        current_process.stdout.close()
        current_process.wait()
        ret = current_process.returncode
        if ret == 0:
            log_lines.append(f"\n🎉 [DASHBOARD] {mode_name} Completed Successfully!\n")
        else:
            log_lines.append(f"\n⚠️ [DASHBOARD] {mode_name} exited with code {ret}\n")
    except Exception as e:
        log_lines.append(f"\n❌ [DASHBOARD] Error: {e}\n")
    finally:
        is_rendering = False
        render_mode = "idle"
        current_process = None

# -------------------------------------------------------------
# REST API Endpoints
# -------------------------------------------------------------
@app.get("/api/status")
def api_status():
    cfg = load_config()
    used_clips = get_used_clips_count()
    video_info = get_video_info(MASTER_VIDEO_PATH)
    outro_norm = cfg.get("CONTENT_ID_OUTRO_NORMALIZED", "")
    outro_exists = os.path.exists(outro_norm) if outro_norm else False
    
    return {
        "status": "online",
        "is_rendering": is_rendering,
        "render_mode": render_mode,
        "locked_clips_count": used_clips,
        "master_video": video_info,
        "outro_status": {
            "locked": cfg.get("CONTENT_ID_OUTRO_LOCKED", True),
            "exists": outro_exists,
            "path": outro_norm
        },
        "voice_engine": {
            "name": cfg.get("VOICE_ENGINE_LOCKED", "Edge_TTS_Shure_SM7B_DSP"),
            "voice": cfg.get("EDGE_TTS_VOICE", "hi-IN-MadhurNeural"),
            "rate": cfg.get("EDGE_TTS_RATE", "+0%"),
            "pitch": cfg.get("EDGE_TTS_PITCH", "-2Hz"),
            "dsp_locked": cfg.get("SHURE_SM7B_DSP_LOCKED", True)
        },
        "pixabay_status": "Active (5,000 req/hr quota)" if cfg.get("PIXABAY_API_KEY") else "Not configured",
        "gemini_pool": gemini_pool.get_pool_telemetry(),
        "groq_pool": groq_pool.get_pool_telemetry(),
        "client_secret_ready": channel_manager.has_client_secret(),
        "youtube_channels": channel_manager.get_all_channels_status()
    }

@app.post("/api/render/start")
def api_render_start(data: dict, bg_tasks: BackgroundTasks):
    global is_rendering
    if is_rendering:
        return JSONResponse(status_code=400, content={"error": "Another render job is already running!"})
    
    mode = data.get("mode", "autonomous")
    topic = data.get("topic", "").strip()
    duration = int(data.get("duration", 35))
    research_mins = float(data.get("research_mins", 10.0))
    target_channel = data.get("target_channel", "auto")

    privacy = data.get("privacy", "unlisted")

    if mode == "autonomous":
        extra = ["--duration", str(duration), "--research_mins", str(research_mins), "--channel", target_channel, "--privacy", privacy]
        if topic:
            extra.extend(["--topic", topic])
        bg_tasks.add_task(run_engine_process, "autonomous_master_loop.py", f"1-Click Full Autonomous [{target_channel.upper()}] (Topic AI + 10m Swarm + 30m+ Clean Cinema + SEO + Upload)", extra)
    elif mode == "epic":
        bg_tasks.add_task(run_engine_process, "epic_geeta_documentary_engine.py", "Epic Bhagavad Gita Documentary (30-100 Min)")
    elif mode == "supreme":
        bg_tasks.add_task(run_engine_process, "supreme_devotional_engine.py", "Supreme Devotional Engine (Fast Mode)")
    else:
        return JSONResponse(status_code=400, content={"error": "Invalid engine mode"})

    return {"message": f"Launched {mode} render engine successfully"}

@app.post("/api/render/stop")
def api_render_stop():
    global current_process, is_rendering
    if current_process and current_process.poll() is None:
        current_process.terminate()
        is_rendering = False
        log_lines.append("\n🛑 [DASHBOARD] Render process manually terminated by user.\n")
        return {"message": "Render process terminated"}
    return {"message": "No active process to stop"}

@app.get("/api/render/logs")
async def api_render_logs():
    async def log_stream():
        idx = 0
        while True:
            if idx < len(log_lines):
                new_logs = "".join(log_lines[idx:])
                idx = len(log_lines)
                yield f"data: {json.dumps({'log': new_logs, 'is_rendering': is_rendering, 'mode': render_mode})}\n\n"
            else:
                yield f"data: {json.dumps({'keepalive': True, 'is_rendering': is_rendering, 'mode': render_mode})}\n\n"
            await asyncio.sleep(0.5)

    return StreamingResponse(log_stream(), media_type="text/event-stream")

@app.post("/api/research/swarm")
def api_research_swarm(data: dict):
    """Executes the 10-Agent Groq Swarm Deep Research (5-10 Mins) and generates the Scalable Gemini Script."""
    topic = data.get("topic", "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन")
    duration = int(data.get("duration", 35))
    research_mins = float(data.get("research_mins", 5.0))

    try:
        # Step 1: 10-Agent Swarm Deep Research (5-10 Mins on YouTube Viral Psychology)
        log_lines.append(f"\n🐝 [SWARM] Launching {research_mins} Minute Deep Research on YouTube Viral Krishna Gyan: '{topic}'...\n")
        dossier = groq_swarm.conduct_deep_research(topic, duration, research_duration_mins=research_mins)
        log_lines.append(f"✓ [SWARM] Completed {dossier.get('research_rounds_completed', 1)} rounds of deep research!\n")
        
        # Step 2: Gemini Script Architect (Zero Sanskrit Chaupai, 4,400+ Words)
        chapters = script_architect.generate_scalable_script(topic, duration, dossier)
        log_lines.append(f"✓ [ARCHITECT] Script Generated: {len(chapters)} Chapters for > 30 Mins Runtime!\n")
        
        return {
            "success": True,
            "topic": topic,
            "duration": duration,
            "research_mins": research_mins,
            "chapters_count": len(chapters),
            "hook_strategy": dossier.get("hook_strategy", {}),
            "chapters": chapters
        }
    except Exception as e:
        log_lines.append(f"[!] Swarm Research Error: {str(e)}\n")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/keys/add")
def api_add_key(data: dict):
    provider = data.get("provider", "gemini")
    key = data.get("key", "").strip()
    if not key:
        return JSONResponse(status_code=400, content={"error": "API key cannot be empty"})

    if provider == "gemini":
        gemini_pool.add_key(key)
        return {"success": True, "message": "Gemini key added to pool successfully", "telemetry": gemini_pool.get_pool_telemetry()}
    elif provider == "groq":
        groq_pool.add_key(key)
        return {"success": True, "message": "Groq key added to pool successfully", "telemetry": groq_pool.get_pool_telemetry()}
    return JSONResponse(status_code=400, content={"error": "Invalid provider"})

@app.post("/api/voice/test")
def api_voice_test(data: dict):
    from shure_sm7b_dsp_engine import synthesize_shure_sm7b_audio
    text = data.get("text", "कर्मण्येवाधिकारस्ते मा फलेषु कदाचन।")
    out_name = f"preview_sm7b_{int(time.time())}.mp3"
    out_path = os.path.join(RENDERS_DIR, out_name)
    dur = synthesize_shure_sm7b_audio(text, out_path)
    return {
        "success": True,
        "duration": round(dur, 2),
        "url": f"/media/{out_name}"
    }

@app.post("/api/config/update")
def api_config_update(data: dict):
    cfg = load_config()
    if "pitch" in data:
        cfg["EDGE_TTS_PITCH"] = data["pitch"]
    if "rate" in data:
        cfg["EDGE_TTS_RATE"] = data["rate"]
    save_config(cfg)
    return {"success": True, "config": cfg}

@app.post("/api/lock/reset")
def api_reset_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    return {"success": True, "message": "Visual lock registry reset. All clips are now reusable."}

# YouTube Dual-Channel Studio Endpoints
@app.get("/api/youtube/channels")
def api_get_youtube_channels():
    return {"channels": channel_manager.get_all_channels_status()}

@app.post("/api/youtube/token/save")
def api_save_youtube_token(data: dict):
    channel_id = data.get("channel_id", "ch_01")
    token_json = data.get("token_json", "")
    if not token_json:
        return JSONResponse(status_code=400, content={"error": "Token content cannot be empty"})
    success = channel_manager.save_channel_token_direct(channel_id, token_json)
    if success:
        return {"success": True, "channel_info": channel_manager.get_channel_status(channel_id)}
    return JSONResponse(status_code=500, content={"error": "Failed to save token JSON"})

@app.post("/api/youtube/client-secret/save")
def api_save_client_secret(data: dict):
    secret_json = data.get("secret_json", "")
    if not secret_json:
        return JSONResponse(status_code=400, content={"error": "Client secret content cannot be empty"})
    success = channel_manager.save_client_secret(secret_json)
    if success:
        return {"success": True, "message": "Saved client_secret.json successfully"}
    return JSONResponse(status_code=500, content={"error": "Failed to parse/save client_secret.json"})

@app.post("/api/youtube/channels/add")
def api_add_channel(data: dict):
    channel_name = data.get("channel_name", "").strip()
    niche = data.get("niche", "भगवद्गीता ज्ञान, आध्यात्मिक संदेश").strip()
    if not channel_name:
        return JSONResponse(status_code=400, content={"error": "Channel name cannot be empty"})
    existing = channel_manager.get_all_channels_status()
    new_id = f"ch_{len(existing) + 1:02d}"
    res = channel_manager.add_channel(new_id, channel_name, niche)
    return res

active_oauth_flows = {}

@app.get("/api/youtube/auth/redirect")
def api_auth_redirect(channel_id: str = "ch_01"):
    if not channel_manager.has_client_secret():
        return HTMLResponse(
            """<!DOCTYPE html><html><body style="background:#0a0b10;color:#f87171;font-family:sans-serif;text-align:center;padding:50px;">
            <h2>⚠️ client_secret.json Missing!</h2>
            <p style="color:#94a3b8;">कृपया पहले डैशबोर्ड पर अपनी client_secret.json फ़ाइल अपलोड या पेस्ट करें।</p>
            <a href="/" style="color:#f59e0b;">Return to Dashboard</a>
            </body></html>""",
            status_code=400
        )
    redirect_uri = "http://localhost:8000/oauth2callback"
    auth_url, state, flow = channel_manager.create_oauth_flow(channel_id, redirect_uri)
    active_oauth_flows[state] = {
        "flow": flow,
        "channel_id": channel_id,
        "redirect_uri": redirect_uri,
        "created_at": time.time()
    }
    print(f"\n[🚀 1-CLICK REDIRECT] Redirecting browser to Google Sign-In for '{channel_id}'...")
    return RedirectResponse(auth_url, status_code=307)

@app.post("/api/youtube/auth/start")
def api_start_youtube_auth(data: dict, request: Request):
    channel_id = data.get("channel_id", "ch_01")
    if not channel_manager.has_client_secret():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "client_secret_missing",
                "message": "client_secret.json फ़ाइल नहीं मिली! कृपया पहले Google Cloud Console से अपनी OAuth Client Secret फ़ाइल अपलोड या पेस्ट करें।"
            }
        )
    try:
        redirect_uri = "http://localhost:8000/oauth2callback"
        auth_url, state, flow = channel_manager.create_oauth_flow(channel_id, redirect_uri)
        active_oauth_flows[state] = {
            "flow": flow,
            "channel_id": channel_id,
            "redirect_uri": redirect_uri,
            "created_at": time.time()
        }

        print(f"\n=======================================================")
        print(f"👉 GOOGLE SIGN-IN URL FOR CHANNEL '{channel_id}':")
        print(auth_url)
        print(f"=======================================================\n")

        try:
            import webbrowser
            webbrowser.open(auth_url, new=1, autoraise=True)
        except Exception:
            pass

        return {
            "success": True,
            "channel_id": channel_id,
            "auth_url": auth_url,
            "state": state,
            "message": "Google Sign-In URL तैयार है! ब्राउज़र में लॉगिन विंडो खुल रही है।"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/oauth2callback", response_class=HTMLResponse)
@app.get("/api/youtube/oauth2callback", response_class=HTMLResponse)
async def oauth2callback(request: Request):
    query_params = dict(request.query_params)
    error = query_params.get("error")
    code = query_params.get("code")
    state = query_params.get("state")

    if error:
        err_desc = query_params.get("error_description", error)
        print(f"[!] Google OAuth Error callback: {error} - {err_desc}")
        guidance = ""
        if "access_denied" in str(error).lower():
            guidance = """
            <div style="background:rgba(239,68,68,0.1); border:1px solid rgba(239,68,68,0.3); border-radius:12px; padding:16px; margin:20px 0; text-align:left; font-size:13px; line-height:1.6;">
              <strong style="color:#f87171;">⚠️ यह त्रुटि क्यों आई? (Why this error?):</strong><br/>
              Google Cloud Console में आपका प्रोजेक्ट <strong>'Testing'</strong> मोड में है और आपकी यह Gmail ID <strong>'Test Users'</strong> लिस्ट में नहीं जुड़ी है।<br/><br/>
              <strong>समाधान (केवल 1 मिनट):</strong>
              <ol style="margin-left:20px; margin-top:8px;">
                <li><a href="https://console.cloud.google.com/apis/credentials/consent" target="_blank" style="color:#f59e0b; text-decoration:underline; font-weight:bold;">Google Cloud OAuth Consent Screen</a> पर जाएं।</li>
                <li>नीचे स्क्रॉल करके <strong>'Test users'</strong> सेक्शन में <strong>+ ADD USERS</strong> दबाएं।</li>
                <li>अपनी YouTube वाली Gmail ID डालें और <strong>SAVE</strong> दबाएं।</li>
                <li>इसके बाद वापस आकर 'Login / Connect' बटन दबाएं—लॉगिन तुरंत सफल हो जाएगा!</li>
              </ol>
            </div>
            """
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>OAuth Error</title></head>
        <body style="background:#0a0b10; color:#e2e8f0; font-family:system-ui, sans-serif; text-align:center; padding:50px 20px;">
          <div style="max-width:550px; margin:0 auto; background:#12141e; padding:32px; border-radius:20px; border:1px solid #ef4444; box-shadow:0 10px 40px rgba(0,0,0,0.6);">
            <div style="font-size:48px;">⚠️</div>
            <h1 style="color:#ef4444; margin:15px 0 10px 0; font-size:22px;">Google OAuth Authorization Error</h1>
            <p style="color:#94a3b8; font-size:14px;">Google ने यह संदेश दिया: <code>{error}</code></p>
            {guidance}
            <a href="/" style="display:inline-block; margin-top:20px; padding:12px 28px; background:#f59e0b; color:#0a0b10; font-weight:bold; border-radius:12px; text-decoration:none;">डैशबोर्ड पर वापस जाएं</a>
          </div>
        </body>
        </html>
        """

    if not code or not state or state not in active_oauth_flows:
        return """
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>OAuth Invalid State</title></head>
        <body style="background:#0a0b10; color:#e2e8f0; font-family:system-ui; text-align:center; padding:50px 20px;">
          <div style="max-width:500px; margin:0 auto; background:#12141e; padding:30px; border-radius:20px; border:1px solid #f59e0b;">
            <div style="font-size:48px;">⚠️</div>
            <h2 style="color:#f59e0b; margin:15px 0;">Session Expired or Invalid</h2>
            <p style="color:#94a3b8; font-size:14px;">कृपया डैशबोर्ड पर लौटें और 'Login / Connect' दोबारा दबाएं।</p>
            <a href="/" style="display:inline-block; margin-top:20px; padding:10px 24px; background:#f59e0b; color:#0a0b10; font-weight:bold; border-radius:10px; text-decoration:none;">Return to Dashboard</a>
          </div>
        </body>
        </html>
        """

    flow_info = active_oauth_flows.pop(state)
    flow = flow_info["flow"]
    channel_id = flow_info["channel_id"]

    try:
        auth_response = str(request.url)
        channel_status = channel_manager.complete_oauth_flow(flow, channel_id, auth_response)
        c_name = channel_status.get("live_title") or channel_status.get("configured_name") or channel_id
        subs = channel_status.get("subscribers", "0")
        sub_count_fmt = f"{int(subs):,}" if str(subs).isdigit() else str(subs)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <title>🎉 Channel Connected — Gita Studio</title>
          <style>
            body {{ background: #0a0b10; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; text-align: center; padding: 60px 20px; }}
            .card {{ max-width: 520px; margin: 0 auto; background: #12141e; border: 1px solid #10b981; border-radius: 24px; padding: 36px; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }}
            h1 {{ color: #10b981; font-size: 24px; margin: 16px 0 8px 0; }}
            .ch-badge {{ display: inline-block; padding: 8px 18px; background: rgba(245,158,11,0.15); border: 1px solid rgba(245,158,11,0.3); color: #f59e0b; border-radius: 9999px; font-weight: bold; font-size: 14px; margin: 12px 0; }}
            p {{ color: #94a3b8; font-size: 14px; line-height: 1.6; }}
            .btn {{ display: inline-block; margin-top: 24px; padding: 12px 30px; background: #10b981; color: #0a0b10; font-weight: bold; border-radius: 12px; text-decoration: none; font-size: 14px; transition: 0.2s; }}
            .btn:hover {{ opacity: 0.9; }}
          </style>
        </head>
        <body>
          <div class="card">
            <div style="font-size: 54px;">🕉️</div>
            <h1>🎉 YouTube Channel Connected!</h1>
            <div class="ch-badge">{c_name}</div>
            <p>आपका YouTube चैनल सफलतापूर्वक <strong>Gita Production Studio</strong> से जुड़ गया है।<br/>लाइव सब्सक्राइबर्स: <strong style="color:#e2e8f0;">{sub_count_fmt}</strong></p>
            <p style="margin-top: 16px; font-size: 12px; color: #64748b;">यह विंडो 3 सेकंड में अपने आप बंद होकर आपको डैशबोर्ड पर ले जाएगी...</p>
            <a href="/" class="btn">डैशबोर्ड पर वापस जाएं (Return to Dashboard)</a>
          </div>
          <script>
            setTimeout(function() {{
              window.location.href = '/';
            }}, 3000);
          </script>
        </body>
        </html>
        """
    except Exception as e:
        print(f"[!] Error in oauth2callback: {e}")
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><title>OAuth Error</title></head>
        <body style="background:#0a0b10; color:#e2e8f0; font-family:system-ui; text-align:center; padding:50px;">
          <div style="max-width:500px; margin:0 auto; background:#12141e; padding:30px; border-radius:20px; border:1px solid #ef4444;">
            <div style="font-size:48px;">⚠️</div>
            <h2 style="color:#ef4444;">Token Exchange Error</h2>
            <p style="color:#94a3b8; font-size:13px; font-family:monospace;">{str(e)}</p>
            <a href="/" style="display:inline-block; margin-top:20px; padding:10px 24px; background:#f59e0b; color:#0a0b10; font-weight:bold; border-radius:10px; text-decoration:none;">Return to Dashboard</a>
          </div>
        </body>
        </html>
        """

@app.get("/api/youtube/auth/status")
def api_get_youtube_auth_status():
    return channel_manager.get_oauth_status()

# -------------------------------------------------------------
# YouTube Autonomous Human-Mimicry Studio Bot Endpoints
# -------------------------------------------------------------
@app.post("/api/youtube/human/login")
def api_human_login(data: dict = Body(default={})):
    try:
        channel_id = data.get("channel_id", "ch_01")
        if channel_id == "ch_02":
            profile_dir = os.path.join(CREDENTIALS_DIR, "youtube_browser_profile_ch_02")
        else:
            profile_dir = os.path.join(CREDENTIALS_DIR, "youtube_browser_profile")
        os.makedirs(profile_dir, exist_ok=True)
        if sys.platform == "win32":
            cmd = f'start chrome.exe --user-data-dir="{profile_dir}" "https://studio.youtube.com"'
            subprocess.Popen(cmd, shell=True)
        else:
            uploader_script = os.path.join(BASE_DIR, "youtube_human_uploader.py")
            subprocess.Popen([sys.executable, uploader_script, "--login", "--channel", channel_id], cwd=BASE_DIR)
        return {
            "success": True,
            "channel_id": channel_id,
            "message": f"Google Chrome खुल गया है! कृपया खुले हुए YouTube Studio में {channel_id} से लॉगिन करें।"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/youtube/human/status")
def api_human_status():
    sf_01 = os.path.join(CREDENTIALS_DIR, "youtube_session_status.json")
    sf_02 = os.path.join(CREDENTIALS_DIR, "youtube_session_status_ch_02.json")
    ch_01_logged = os.path.exists(sf_01)
    ch_02_logged = os.path.exists(sf_02)
    return {
        "success": True,
        "is_logged_in": ch_01_logged,
        "ch_01": {"logged_in": ch_01_logged, "name": "दिव्य गीता वाणी"},
        "ch_02": {"logged_in": ch_02_logged, "name": "Premanand Ji Vichar • Fan Channel"},
        "status": "ready" if (ch_01_logged or ch_02_logged) else "login_required"
    }

@app.post("/api/youtube/human/upload")
def api_human_upload(data: dict = Body(default={})):
    try:
        visible = data.get("visible", True)
        bat_file = os.path.join(BASE_DIR, "1_CLICK_HUMAN_UPLOAD.bat")
        if visible and sys.platform == "win32" and os.path.exists(bat_file):
            os.startfile(bat_file)
        else:
            uploader_script = os.path.join(BASE_DIR, "youtube_human_uploader.py")
            cmd = [sys.executable, uploader_script, "--upload"]
            subprocess.Popen(cmd, cwd=BASE_DIR)
        return {
            "success": True,
            "message": "ह्यूमन-मिमिक्री यूट्यूब अपलोड शुरू हो गया है! क्रोम विंडो में लाइव देखें।"
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/api/open-folder")
def api_open_folder():
    if sys.platform == "win32":
        os.startfile(RENDERS_DIR)
        return {"success": True}
    return {"success": False, "error": "Not on Windows"}

@app.get("/media/{file_name}")
def serve_media(file_name: str):
    path = os.path.join(RENDERS_DIR, file_name)
    if not os.path.exists(path):
        path = os.path.join(CHAPTERS_DIR, file_name)
    if os.path.exists(path):
        return FileResponse(path)
    return JSONResponse(status_code=404, content={"error": "File not found"})

# -------------------------------------------------------------
# 24/7 Autopilot REST APIs
# -------------------------------------------------------------
autopilot_process: Optional[subprocess.Popen] = None

def is_autopilot_daemon_running() -> bool:
    global autopilot_process
    if autopilot_process and autopilot_process.poll() is None:
        return True
    try:
        import psutil
        my_pid = os.getpid()
        for p in psutil.process_iter(['pid', 'cmdline']):
            if p.pid != my_pid:
                cmd = p.info.get('cmdline') or []
                if any(str(arg).endswith('autopilot_24x7_daemon.py') for arg in cmd):
                    return True
    except Exception:
        pass
    return False

@app.get("/api/autopilot/status")
def api_autopilot_status():
    control_path = os.path.join(RENDERS_DIR, "autopilot_control.json")
    state_path = os.path.join(RENDERS_DIR, "autopilot_daily_state.json")
    live_path = os.path.join(RENDERS_DIR, "autopilot_live_status.json")

    control = {}
    if os.path.exists(control_path):
        try:
            with open(control_path, "r", encoding="utf-8") as f:
                control = json.load(f)
        except Exception:
            pass

    state = {}
    if os.path.exists(state_path):
        try:
            with open(state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
        except Exception:
            pass

    live = {}
    if os.path.exists(live_path):
        try:
            with open(live_path, "r", encoding="utf-8") as f:
                live = json.load(f)
        except Exception:
            pass

    proc_running = is_autopilot_daemon_running()

    return {
        "is_daemon_running": proc_running,
        "control": control,
        "state": state,
        "live": live
    }

@app.post("/api/autopilot/start")
def api_autopilot_start():
    global autopilot_process
    control_path = os.path.join(RENDERS_DIR, "autopilot_control.json")
    c = {}
    if os.path.exists(control_path):
        try:
            with open(control_path, "r", encoding="utf-8") as f:
                c = json.load(f)
        except Exception:
            pass
    c["enabled"] = True
    c["paused"] = False
    c["last_command"] = "start"
    try:
        with open(control_path, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2)
    except Exception:
        pass

    proc_running = is_autopilot_daemon_running()

    if not proc_running:
        daemon_script = os.path.join(BASE_DIR, "autopilot_24x7_daemon.py")
        autopilot_process = subprocess.Popen([sys.executable, "-u", daemon_script], cwd=BASE_DIR)
        return {"success": True, "message": "24/7 Autopilot Engine Started! Process running in background."}
    else:
        return {"success": True, "message": "24/7 Autopilot Resumed and Active!"}

@app.post("/api/autopilot/stop")
def api_autopilot_stop():
    control_path = os.path.join(RENDERS_DIR, "autopilot_control.json")
    c = {}
    if os.path.exists(control_path):
        try:
            with open(control_path, "r", encoding="utf-8") as f:
                c = json.load(f)
        except Exception:
            pass
    c["enabled"] = False
    c["paused"] = True
    c["last_command"] = "stop"
    try:
        with open(control_path, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2)
    except Exception:
        pass
    return {"success": True, "message": "Autopilot Standby requested. Daemon paused."}

@app.post("/api/autopilot/trigger-now")
def api_autopilot_trigger_now():
    global autopilot_process
    control_path = os.path.join(RENDERS_DIR, "autopilot_control.json")
    c = {}
    if os.path.exists(control_path):
        try:
            with open(control_path, "r", encoding="utf-8") as f:
                c = json.load(f)
        except Exception:
            pass
    c["enabled"] = True
    c["paused"] = False
    c["force_run_now"] = True
    c["last_command"] = "trigger_now"
    try:
        with open(control_path, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2)
    except Exception:
        pass

    proc_running = is_autopilot_daemon_running()

    if not proc_running:
        daemon_script = os.path.join(BASE_DIR, "autopilot_24x7_daemon.py")
        autopilot_process = subprocess.Popen([sys.executable, "-u", daemon_script], cwd=BASE_DIR)

    return {"success": True, "message": "Triggered immediate video production! Cadence timer bypassed."}

@app.post("/api/autopilot/launch-terminal")
def api_autopilot_launch_terminal():
    bat_path = os.path.join(BASE_DIR, "START_24x7_AUTOPILOT.bat")
    if sys.platform == "win32" and os.path.exists(bat_path):
        os.startfile(bat_path)
        return {"success": True, "message": "Launched 24/7 Autopilot in standalone console window!"}
    return {"success": False, "error": "Batch launcher not found"}

# -------------------------------------------------------------
# Google Colab 1-Hour HyperSpeed Engine APIs
# -------------------------------------------------------------
colab_runner_proc: Optional[subprocess.Popen] = None

@app.get("/api/colab/status")
def api_colab_status():
    global colab_runner_proc
    from colab_hyper_runner import ColabHyperRunner, LOG_FILE
    runner = ColabHyperRunner()
    state = runner.load_state()
    is_alive = False
    if colab_runner_proc is not None:
        if colab_runner_proc.poll() is None:
            is_alive = True
        else:
            colab_runner_proc = None

    logs = ""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()
                logs = "".join(lines[-80:])
        except Exception:
            pass

    return {
        "state": state,
        "is_running": is_alive or state.get("is_running", False),
        "logs": logs
    }

@app.post("/api/colab/start")
def api_colab_start():
    global colab_runner_proc
    if colab_runner_proc is not None and colab_runner_proc.poll() is None:
        return {"success": False, "message": "1-Hour Hyper-Run is already running!"}
    runner_script = os.path.join(BASE_DIR, "colab_hyper_runner.py")
    colab_runner_proc = subprocess.Popen([sys.executable, "-u", runner_script], cwd=BASE_DIR)
    return {"success": True, "message": "⚡ 1-Hour Hyper-Run (10 Videos) Launched! High-speed batch production active."}

@app.post("/api/colab/stop")
def api_colab_stop():
    global colab_runner_proc
    if colab_runner_proc is not None and colab_runner_proc.poll() is None:
        colab_runner_proc.terminate()
        colab_runner_proc = None
    from colab_hyper_runner import ColabHyperRunner
    runner = ColabHyperRunner()
    runner.state["status"] = "STOPPED"
    runner.state["is_running"] = False
    runner.state["current_action"] = "Production stopped by user."
    runner.save_state()
    return {"success": True, "message": "⏹️ 1-Hour Hyper-Run Stopped."}

@app.get("/api/colab/download-notebook")
def api_colab_download_notebook():
    nb_path = os.path.join(BASE_DIR, "Krishna_AI_Colab_HyperEngine.ipynb")
    if os.path.exists(nb_path):
        return FileResponse(nb_path, filename="Krishna_AI_Colab_HyperEngine.ipynb", media_type="application/x-ipynb+json")
    return JSONResponse(status_code=404, content={"error": "Notebook file not found"})

@app.post("/api/colab/launch-browser")
def api_colab_launch_browser():
    import webbrowser
    webbrowser.open("https://colab.research.google.com/")
    return {"success": True, "message": "Opened Google Colab in your default browser!"}

# -------------------------------------------------------------
# GitHub Actions Cloud Matrix Dispatcher APIs
# -------------------------------------------------------------
@app.get("/api/github/status")
def api_github_status():
    from github_cloud_dispatcher import dispatcher
    cfg = dispatcher.load_config()
    telemetry = dispatcher.get_latest_run_status()
    return {
        "repo": cfg.get("github_repo", ""),
        "has_token": bool(cfg.get("github_token")),
        "last_dispatched": cfg.get("last_dispatched", 0),
        "telemetry": telemetry
    }

@app.post("/api/github/config")
def api_github_config(data: dict = Body(...)):
    from github_cloud_dispatcher import dispatcher
    repo = data.get("repo", "").strip()
    token = data.get("token", "").strip()
    update = {}
    if repo: update["github_repo"] = repo
    if token: update["github_token"] = token
    dispatcher.save_config(update)
    return {"success": True, "message": "GitHub Cloud Dispatcher configuration saved!"}

@app.post("/api/github/dispatch")
def api_github_dispatch(data: dict = Body(...)):
    from github_cloud_dispatcher import dispatcher
    duration = int(data.get("duration", 35))
    privacy = data.get("privacy", "unlisted")
    res = dispatcher.dispatch_10_video_batch(duration=duration, privacy=privacy)
    return res

# -------------------------------------------------------------
# Frontend Dashboard HTML (Tailwind CSS + Glassmorphism Dark)
# -------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    return """
<!DOCTYPE html>
<html lang="hi" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🕉️ Gita Production Studio — Professional Mission Control</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              gold: '#F59E0B',
              amber: '#D97706',
              dark: '#0A0B10',
              card: '#12141E',
              border: '#1F2438'
            }
          }
        }
      }
    }
  </script>
  <style>
    body { background-color: #0A0B10; color: #E2E8F0; font-family: system-ui, -apple-system, sans-serif; }
    .glass { background: rgba(18, 20, 30, 0.75); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.08); }
    .gold-glow { box-shadow: 0 0 25px rgba(245, 158, 11, 0.25); }
    .gold-gradient { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); }
    .badge-lock { background: rgba(16, 185, 129, 0.15); border: 1px solid rgba(16, 185, 129, 0.3); color: #34D399; }
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #0A0B10; }
    ::-webkit-scrollbar-thumb { background: #262B40; border-radius: 3px; }
    .tab-pane { display: none !important; }
    .tab-pane.active { display: block !important; }
  </style>
  <script>
    function switchTab(tab) {
      console.log("Switching to tab:", tab);
      var tabs = ['control', 'autopilot', 'colab', 'youtube', 'swarm', 'voice', 'player', 'settings'];
      for (var i = 0; i < tabs.length; i++) {
        var name = tabs[i];
        var pane = document.getElementById('content-' + name);
        var btn = document.getElementById('tab-' + name);
        if (pane) {
          if (name === tab) {
            pane.style.setProperty('display', 'block', 'important');
            pane.classList.remove('hidden');
            pane.classList.add('active');
          } else {
            pane.style.setProperty('display', 'none', 'important');
            pane.classList.add('hidden');
            pane.classList.remove('active');
          }
        }
        if (btn) {
          if (name === tab) {
            btn.classList.remove('border-transparent', 'text-slate-400');
            if (tab === 'autopilot') {
              btn.classList.add('border-emerald-500', 'text-emerald-400');
            } else if (tab === 'youtube') {
              btn.classList.add('border-red-500', 'text-red-400');
            } else if (tab === 'colab') {
              btn.classList.add('border-cyan-400', 'text-cyan-300');
            } else {
              btn.classList.add('border-amber-500', 'text-amber-400');
            }
          } else {
            btn.classList.remove('border-amber-500', 'text-amber-400', 'border-red-500', 'text-red-400', 'border-emerald-500', 'text-emerald-400', 'border-cyan-400', 'text-cyan-300');
            btn.classList.add('border-transparent', 'text-slate-400');
          }
        }
      }
    }
  </script>
</head>
<body class="min-h-screen flex flex-col">

  <!-- Top Navbar -->
  <header class="glass sticky top-0 z-50 border-b border-brand-border px-6 py-3.5 flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <div class="w-10 h-10 rounded-xl gold-gradient flex items-center justify-center text-slate-900 font-bold text-xl shadow-lg">
        🕉️
      </div>
      <div>
        <h1 class="font-extrabold text-lg tracking-wide text-amber-400">GITA PRODUCTION STUDIO</h1>
        <p class="text-xs text-slate-400">10-Agent Swarm • Groq & Gemini Pool • 1–100 Min Scalable Engine</p>
      </div>
    </div>

    <!-- Active Lock Badges -->
    <div class="hidden lg:flex items-center space-x-2 text-xs font-semibold">
      <span class="badge-lock px-2.5 py-1 rounded-full flex items-center gap-1.5">
        <i class="fa-solid fa-bolt text-emerald-400"></i> 10 Groq Swarm Active
      </span>
      <span class="badge-lock px-2.5 py-1 rounded-full flex items-center gap-1.5">
        <i class="fa-solid fa-server text-emerald-400"></i> Gemini Key Pool (<span id="geminiKeysCount">2</span> Keys)
      </span>
      <span class="badge-lock px-2.5 py-1 rounded-full flex items-center gap-1.5">
        <i class="fa-solid fa-microphone-lines text-emerald-400"></i> Shure SM7B DSP Locked
      </span>
      <span class="badge-lock px-2.5 py-1 rounded-full flex items-center gap-1.5">
        <i class="fa-solid fa-shield-halved text-emerald-400"></i> 173s Outro Locked
      </span>
    </div>

    <!-- Quick Actions -->
    <div class="flex items-center space-x-3">
      <button onclick="openFolder()" class="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 flex items-center gap-1.5 transition">
        <i class="fa-solid fa-folder-open text-amber-400"></i> Open Renders
      </button>
      <div id="renderIndicator" class="flex items-center gap-2 px-3 py-1 rounded-full text-xs bg-slate-800/80 text-slate-400 border border-slate-700">
        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span> Ready
      </div>
    </div>
  </header>

  <!-- Main Content Layout -->
  <main class="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">

    <!-- Top Metrics Overview -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div class="glass p-4 rounded-xl flex items-center justify-between border-l-4 border-amber-500">
        <div>
          <p class="text-xs text-slate-400 uppercase font-semibold">Groq Swarm & Gemini</p>
          <h3 class="text-lg font-bold text-slate-100 mt-1">10-Agent Swarm</h3>
          <p class="text-xs text-emerald-400 mt-0.5">Multi-Key Pool Autonomous</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center text-xl">
          <i class="fa-solid fa-brain"></i>
        </div>
      </div>

      <div class="glass p-4 rounded-xl flex items-center justify-between border-l-4 border-blue-500">
        <div>
          <p class="text-xs text-slate-400 uppercase font-semibold">Unique Visuals Locked</p>
          <h3 id="lockedClipsVal" class="text-lg font-bold text-slate-100 mt-1">111 Clips</h3>
          <p class="text-xs text-blue-400 mt-0.5">Zero Repetition Active</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center text-xl">
          <i class="fa-solid fa-clapperboard"></i>
        </div>
      </div>

      <div class="glass p-4 rounded-xl flex items-center justify-between border-l-4 border-purple-500">
        <div>
          <p class="text-xs text-slate-400 uppercase font-semibold">0–5s Hook & Outro</p>
          <h3 class="text-lg font-bold text-slate-100 mt-1">Hook Vault Active</h3>
          <p class="text-xs text-purple-400 mt-0.5">173.25s Blue Laser Shield</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center text-xl">
          <i class="fa-solid fa-shield-virus"></i>
        </div>
      </div>

      <div class="glass p-4 rounded-xl flex items-center justify-between border-l-4 border-emerald-500">
        <div>
          <p class="text-xs text-slate-400 uppercase font-semibold">Voice Engine (Google Free TTS)</p>
          <h3 class="text-lg font-bold text-slate-100 mt-1">Google TTS (Charon)</h3>
          <p class="text-xs text-emerald-400 mt-0.5">Shure SM7B DSP • Zero Chaupais</p>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl">
          <i class="fa-solid fa-microphone-lines"></i>
        </div>
      </div>
    </div>

    <!-- Tabbed Workstation Navigation -->
    <div class="flex border-b border-brand-border space-x-6 text-sm font-medium overflow-x-auto">
      <button onclick="switchTab('control')" id="tab-control" class="pb-3 border-b-2 border-amber-500 text-amber-400 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors">
        <i class="fa-solid fa-sliders"></i> Production Mission Control
      </button>
      <button onclick="switchTab('autopilot')" id="tab-autopilot" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-emerald-400 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors">
        <i class="fa-solid fa-robot text-emerald-400"></i> 24/7 Autopilot (5+5 Daily)
      </button>
      <button onclick="switchTab('colab')" id="tab-colab" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-cyan-300 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors font-semibold">
        <span class="relative flex h-2.5 w-2.5 mr-0.5">
          <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
          <span class="relative inline-flex rounded-full h-2.5 w-2.5 bg-cyan-500"></span>
        </span>
        <i class="fa-solid fa-bolt text-cyan-400"></i> ⚡ 1-Hour Colab HyperSpeed (10 Videos)
      </button>
      <button onclick="switchTab('youtube')" id="tab-youtube" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-red-400 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors">
        <i class="fa-brands fa-youtube text-red-500"></i> YouTube Studio Hub (2 Channels)
      </button>
      <button onclick="switchTab('swarm')" id="tab-swarm" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors">
        <i class="fa-solid fa-brain"></i> 10-Agent Groq Swarm & Script (1-100m)
      </button>
      <button onclick="switchTab('voice')" id="tab-voice" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors">
        <i class="fa-solid fa-microphone-lines"></i> Shure SM7B DSP Studio
      </button>
      <button onclick="switchTab('player')" id="tab-player" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors">
        <i class="fa-solid fa-play"></i> Master Video Previewer
      </button>
      <button onclick="switchTab('settings')" id="tab-settings" class="pb-3 border-b-2 border-transparent text-slate-400 hover:text-slate-200 flex items-center gap-2 whitespace-nowrap cursor-pointer transition-colors">
        <i class="fa-solid fa-gear"></i> Pools & System Settings
      </button>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 1: PRODUCTION MISSION CONTROL -->
    <!-- ============================================================== -->
    <div id="content-control" class="tab-pane active space-y-6" style="display: block;">
      
      <!-- Cloud Matrix Live Top Banner & 1-Click Dispatch Hub -->
      <div class="glass p-5 rounded-2xl border border-indigo-500/50 bg-gradient-to-r from-slate-900/95 via-indigo-950/40 to-slate-900/95 shadow-2xl space-y-4">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 flex items-center gap-1.5">
                <i class="fa-brands fa-github text-white"></i> 10-Worker Cloud Parallel Engine (GitHub Actions)
              </span>
              <span id="ghRunStatusBadgeMain" class="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700">STANDBY</span>
              <span class="px-2.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">100% UNLISTED</span>
            </div>
            <h3 class="font-extrabold text-slate-100 text-lg flex items-center gap-2">
              <i class="fa-solid fa-cloud-bolt text-indigo-400"></i> 1-Click 10-Video Cloud Production (Zero PC Load)
            </h3>
            <p class="text-xs text-slate-300 max-w-2xl">
              1-क्लिक करते ही GitHub Actions पर <b>10 समानांतर Linux VMs</b> चालू होंगी — 5 वीडियो Ch 1 + 5 वीडियो Ch 2 (&gt;30 मिनट) बनकर YouTube पर <b>100% Unlisted</b> अपलोड होंगी, और काम पूरा होते ही VMs स्वतः बंद हो जाएंगी!
            </p>
          </div>

          <div class="flex flex-wrap items-center gap-2.5">
            <button onclick="dispatchGitHubCloudRun()" id="ghDispatchBtnMain" class="px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-600 hover:from-indigo-400 hover:to-pink-500 text-white font-black text-sm flex items-center gap-2.5 shadow-xl shadow-indigo-500/30 transition-all cursor-pointer whitespace-nowrap active:scale-95">
              <i class="fa-solid fa-rocket text-base"></i> 🚀 DISPATCH 10 CLOUD WORKERS NOW
            </button>
            <a id="ghActionLinkMain" href="https://github.com/sagarsbl369369-bit/krishna-divine-cinema/actions" target="_blank" class="px-4 py-3.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-bold text-xs flex items-center gap-2 shadow transition cursor-pointer">
              <i class="fa-solid fa-arrow-up-right-from-square text-cyan-400"></i> Watch Live on GitHub
            </a>
          </div>
        </div>

        <!-- 10 Cloud Workers Live Matrix Grid (Rendered right here on Mission Control!) -->
        <div class="pt-3 border-t border-slate-800/80">
          <div class="flex items-center justify-between mb-2">
            <span class="text-xs font-semibold text-slate-400 flex items-center gap-2">
              <i class="fa-solid fa-microchip text-indigo-400"></i> Live 10-Worker Cloud Status:
            </span>
            <span id="ghLastRunTextMain" class="text-xs font-mono text-cyan-400">Checking cloud telemetry...</span>
          </div>
          <div id="ghWorkerGridMain" class="grid grid-cols-2 sm:grid-cols-5 gap-2"></div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Left: Launch Controls -->
        <div class="glass p-5 rounded-2xl space-y-5 lg:col-span-1">
          <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
            <i class="fa-solid fa-bolt text-amber-400"></i> Video Engine Launch Pad
          </h3>

          <div class="space-y-3">
            <label class="block text-xs font-semibold text-slate-400 uppercase">Select Production Mode</label>
            <div class="space-y-2">
              <label class="flex items-start p-3 rounded-xl border border-emerald-500/50 bg-emerald-500/10 cursor-pointer hover:bg-emerald-500/20 transition">
                <input type="radio" name="engineMode" value="autonomous" checked class="mt-1 text-emerald-500 focus:ring-0">
                <div class="ml-3">
                  <span class="block text-sm font-bold text-emerald-400">⚡ 1-Click Autonomous (10m Swarm + 30m+ Clean Cinema)</span>
                  <span class="block text-xs text-slate-300 mt-0.5">10-Min Groq Deep Research • 10x Evolutionary Depth • ZERO Subtitles • 100% Pure Vedic Hindi</span>
                </div>
              </label>

              <label class="flex items-start p-3 rounded-xl border border-amber-500/40 bg-amber-500/5 cursor-pointer hover:bg-amber-500/10 transition">
                <input type="radio" name="engineMode" value="epic" class="mt-1 text-amber-500 focus:ring-0">
                <div class="ml-3">
                  <span class="block text-sm font-bold text-amber-400">👑 Epic Scalable Engine (1–100 Min)</span>
                  <span class="block text-xs text-slate-400 mt-0.5">Modular Architecture • 0-5s Hook Scene • Shure SM7B DSP • 0% OOM Memory Crash</span>
                </div>
              </label>

              <label class="flex items-start p-3 rounded-xl border border-slate-700 bg-slate-800/40 cursor-pointer hover:bg-slate-800/80 transition">
                <input type="radio" name="engineMode" value="supreme" class="mt-1 text-amber-500 focus:ring-0">
                <div class="ml-3">
                  <span class="block text-sm font-bold text-slate-200">⚡ Supreme Devotional Engine</span>
                  <span class="block text-xs text-slate-400 mt-0.5">Fast Single-Pass • Pure Hindi • Pixabay Visual Match</span>
                </div>
              </label>
            </div>
          </div>

          <div class="space-y-2 pt-2 border-t border-slate-800">
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span>0-5s Opening Scene</span>
              <span class="text-emerald-400 font-semibold">Curated Hook Vault (No Dull Scenes)</span>
            </div>
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span>Voiceover Profile</span>
              <span class="text-amber-400 font-semibold">Shure SM7B DSP (-14 LUFS)</span>
            </div>
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span>Subtitles Styling</span>
              <span class="text-amber-400 font-semibold">Radiant Gold (Nirmala UI)</span>
            </div>
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span>Outro Protection</span>
              <span class="text-purple-400 font-semibold">173.25s Blue Laser (Hard-Locked)</span>
            </div>
          </div>

          <div class="pt-3 space-y-2">
            <button id="btnLaunch" onclick="launchRender()" class="w-full py-3.5 px-4 rounded-xl gold-gradient text-slate-950 font-bold text-sm gold-glow hover:opacity-90 transition flex items-center justify-center gap-2">
              <i class="fa-solid fa-play"></i> START PRODUCTION RENDER
            </button>
            <button id="btnStop" onclick="stopRender()" class="w-full py-2.5 px-4 rounded-xl bg-rose-600/20 text-rose-400 hover:bg-rose-600/30 border border-rose-500/30 font-semibold text-xs transition hidden flex items-center justify-center gap-2">
              <i class="fa-solid fa-stop"></i> Abort / Stop Current Render
            </button>
          </div>
        </div>

        <!-- Right: Live Terminal & Render Log Stream -->
        <div class="glass p-5 rounded-2xl lg:col-span-2 flex flex-col h-[540px]">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="font-bold text-slate-200 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-terminal text-slate-400"></i> Live Terminal Output Stream
            </h3>
            <div class="flex items-center gap-2">
              <button onclick="clearConsole()" class="text-xs text-slate-400 hover:text-slate-200 bg-slate-800 px-2.5 py-1 rounded">
                Clear
              </button>
              <span id="logStatusPill" class="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400">Stream Connected</span>
            </div>
          </div>

          <!-- Console Box -->
          <div id="terminalConsole" class="flex-1 bg-black/60 rounded-xl p-4 font-mono text-xs overflow-y-auto text-emerald-400 space-y-1 mt-3 border border-slate-800/80 select-text leading-relaxed">
            <div class="text-slate-500 italic">Waiting for render launch... Live stream ready.</div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 2: 10-AGENT GROQ SWARM & SCRIPT ARCHITECT (1-100m) -->
    <!-- ============================================================== -->
    <div id="content-swarm" class="tab-pane space-y-6 hidden" style="display: none;">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Left: Swarm Controller & Duration Slider -->
        <div class="glass p-5 rounded-2xl space-y-5 lg:col-span-1">
          <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
            <i class="fa-solid fa-brain text-amber-400"></i> 10-Agent Groq Swarm Deep Research
          </h3>
          <p class="text-xs text-slate-400">
            10 specialized AI researchers analyze Shankara Bhashya, Ramanuja, Carl Jung psychology, and cosmic physics simultaneously.
          </p>

          <div class="space-y-3">
            <label class="block text-xs font-semibold text-slate-400 uppercase">Topic / Shloka / Life Problem</label>
            <input type="text" id="swarmTopic" value="कुरुक्षेत्र का विषाद और कर्मयोग की पराकाष्ठा" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500">
          </div>

          <!-- Research Duration (5 to 10 Minutes) -->
          <div class="space-y-2">
            <label class="block text-xs font-semibold text-slate-400 uppercase">Groq Swarm Deep Research Duration</label>
            <select id="swarmResearchDuration" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500">
              <option value="5" selected>⚡ 5 Minutes Deep Research (Viral YouTube Krishna Analysis)</option>
              <option value="10">🔥 10 Minutes Ultra-Deep Swarm (10x Better Script, Maximum Retention)</option>
              <option value="1">⚡ 1 Minute Quick Test</option>
            </select>
            <p class="text-[11px] text-amber-400/90 leading-relaxed">
              Researches Osho, Acharya Prashant, 10M+ view YouTube audience psychology, Carl Jung shadow, and quantum physics for literal goosebumps ("रोंगटे खड़े कर देने वाला")!
            </p>
          </div>

          <!-- Duration Slider (1 to 100 Min) -->
          <div class="space-y-2">
            <div class="flex justify-between items-center text-xs">
              <label class="font-semibold text-slate-400 uppercase">Target Video Duration</label>
              <span id="durDisplay" class="text-amber-400 font-bold text-sm">35 Minutes (Strictly > 30 Mins Guaranteed)</span>
            </div>
            <input type="range" id="durSlider" min="1" max="100" value="35" oninput="updateDurDisplay(this.value)" class="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-500">
            <div class="flex justify-between text-[11px] text-slate-500">
              <span>1m (Shorts)</span>
              <span>15m (Standard)</span>
              <span>35m (Strict > 30m)</span>
              <span>100m (Epic)</span>
            </div>
            <p id="chapterCalc" class="text-xs text-emerald-400 font-medium">Auto-Scales into: 10 Expansive Chapters (~4,400 Words, 0% Sanskrit Recited)</p>
          </div>

          <button id="btnSwarm" onclick="launchSwarmResearch()" class="w-full py-3.5 px-4 rounded-xl gold-gradient text-slate-950 font-bold text-sm gold-glow hover:opacity-90 transition flex items-center justify-center gap-2">
            <i class="fa-solid fa-wand-magic-sparkles"></i> Launch 10-Agent Swarm Research & Script
          </button>
        </div>

        <!-- Right: 10 Swarm Personas & Generated Script Review -->
        <div class="glass p-5 rounded-2xl lg:col-span-2 space-y-4 flex flex-col h-[600px] overflow-hidden">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="font-bold text-slate-200 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-microchip text-amber-400"></i> Swarm Intelligence & Script Preview
            </h3>
            <span id="swarmStatusBadge" class="text-xs px-2.5 py-1 rounded bg-slate-800 text-slate-400">10 Agents Ready</span>
          </div>

          <div id="swarmOutputContainer" class="flex-1 overflow-y-auto space-y-4 pr-1">
            
            <!-- 10 Agents Grid Preview -->
            <div class="grid grid-cols-2 sm:grid-cols-5 gap-2 text-center text-[11px]">
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-map-location-dot text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">1. Battlefield</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-om text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">2. Shankara</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-hands-praying text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">3. Ramanuja</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-eye text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">4. Allegory</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-brain text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">5. Carl Jung</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-person-burst text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">6. Burnout</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-atom text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">7. Quantum</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-bullhorn text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">8. 0-5s Hook</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-film text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">9. 4K Visual</div>
              </div>
              <div class="p-2 bg-slate-900/60 rounded-lg border border-slate-800">
                <i class="fa-solid fa-scroll text-amber-400 mb-1"></i>
                <div class="font-bold text-slate-300">10. Upanishad</div>
              </div>
            </div>

            <!-- Active Script Card Preview -->
            <div id="activeScriptView" class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 space-y-3">
              <div class="flex items-center justify-between text-xs text-slate-400">
                <span class="text-amber-400 font-bold"><i class="fa-solid fa-circle-check"></i> Current Active Script: epic_30min_script.json</span>
                <span>3 Chapters</span>
              </div>
              <div class="text-xs text-slate-300 leading-relaxed bg-black/40 p-3 rounded-lg border border-slate-800/60 font-mono">
                <span class="text-amber-400 font-bold">Chapter 1: गांडीव का पतन और अस्तित्व का संकट</span><br/>
                <span class="text-slate-400 italic">0-5s Hook: जब दुनिया के सबसे महान धनुर्धर ने युद्धभूमि में शस्त्र डाल दिए, तब कृष्ण ने सांत्वना नहीं... वो अंतिम सत्य कहा जो मृत्यु को भी झुका दे...</span>
              </div>
            </div>

          </div>
        </div>

      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 3: SHURE SM7B DSP SOUND STUDIO -->
    <!-- ============================================================== -->
    <div id="content-voice" class="tab-pane space-y-6 hidden" style="display: none;">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Voice Synthesis Box -->
        <div class="glass p-5 rounded-2xl space-y-4">
          <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
            <i class="fa-solid fa-microphone-lines text-amber-400"></i> Shure SM7B Live Voiceover Tester
          </h3>
          <p class="text-xs text-slate-400">
            Type any Sanskrit Shloka or Hindi narration. Mastered with 9-stage Shure SM7B DSP hardware emulation.
          </p>

          <textarea id="voiceTestInput" rows="5" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-amber-500" placeholder="यहाँ शुद्ध हिंदी या श्लोक लिखें...">कर्मण्येवाधिकारस्ते मा फलेषु कदाचन। मा कर्मफलहेतुर्भूर्मा ते सङ्गोऽस्त्वकर्मणि॥</textarea>

          <div class="flex items-center gap-3">
            <button id="btnTestVoice" onclick="testVoice()" class="flex-1 py-3 px-4 rounded-xl gold-gradient text-slate-950 font-bold text-sm gold-glow hover:opacity-90 transition flex items-center justify-center gap-2">
              <i class="fa-solid fa-wand-magic-sparkles"></i> Master with Shure SM7B DSP
            </button>
          </div>

          <div id="audioPlayerContainer" class="p-4 bg-slate-900/60 rounded-xl border border-slate-800 hidden space-y-2">
            <div class="flex items-center justify-between text-xs text-slate-400">
              <span class="text-emerald-400 font-semibold"><i class="fa-solid fa-circle-check"></i> Mastered Broadcast Audio</span>
              <span id="testAudioDur">--</span>
            </div>
            <audio id="audioElement" controls class="w-full"></audio>
          </div>
        </div>

        <!-- 9-Stage DSP Hardware Chain Visualizer -->
        <div class="glass p-5 rounded-2xl space-y-4">
          <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
            <i class="fa-solid fa-sliders text-amber-400"></i> Active 9-Stage Shure SM7B DSP Hardware Chain
          </h3>
          
          <div class="space-y-2.5 text-xs">
            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">1. 48kHz Studio Resampler</span>
                <p class="text-slate-400 text-[11px]">Resamples 24kHz stream to 48,000 Hz studio broadcast master.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">aresample=48000</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">2. 75Hz Low-Cut Rumble Filter</span>
                <p class="text-slate-400 text-[11px]">Cuts sub-bass handling rumble and plosive air thumps.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">highpass=f=75</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">3. 180Hz Proximity Warmth (+3.5 dB)</span>
                <p class="text-slate-400 text-[11px]">Classic close-mic Shure SM7B deep chest radio intimacy.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">equalizer=180Hz</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">4. 450Hz Mud De-clutter (-1.8 dB)</span>
                <p class="text-slate-400 text-[11px]">Surgically removes boxiness and room muddiness.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">equalizer=450Hz</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">5. 3.2kHz SM7B Presence Boost (+2.5 dB)</span>
                <p class="text-slate-400 text-[11px]">Crisp Vedic/Hindi consonant articulation & spiritual presence.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">equalizer=3.2kHz</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">6. 6.8kHz Studio De-Esser (-3.0 dB)</span>
                <p class="text-slate-400 text-[11px]">Tames harsh sibilance on 'स', 'श', 'ष', 'च'.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">equalizer=6.8kHz</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">7. 13.5kHz Dynamic Capsule Roll-Off</span>
                <p class="text-slate-400 text-[11px]">Dynamic mic smooth fall-off eliminating digital hiss.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">lowpass=13.5kHz</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">8. Optical LA-2A Leveler / Compressor</span>
                <p class="text-slate-400 text-[11px]">Upfront consistent studio vocal thickness.</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">compand=2.5x</span>
            </div>

            <div class="p-2.5 bg-slate-900/70 rounded-lg border border-slate-800 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-400">9. EBU R128 YouTube Loudness Normalization</span>
                <p class="text-slate-400 text-[11px]">Standardized broadcast loudness (-14 LUFS, TP -1.0 dB).</p>
              </div>
              <span class="badge-lock px-2 py-0.5 rounded text-[10px]">loudnorm=-14LUFS</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 4: MASTER VIDEO PREVIEWER -->
    <!-- ============================================================== -->
    <div id="content-player" class="tab-pane space-y-6 hidden" style="display: none;">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">

        <!-- Embedded Video Player -->
        <div class="glass p-5 rounded-2xl lg:col-span-2 space-y-4">
          <div class="flex items-center justify-between">
            <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
              <i class="fa-solid fa-film text-amber-400"></i> Master Video Playback
            </h3>
            <span class="text-xs text-amber-400 font-mono">epic_bhagavad_gita_documentary_master.mp4</span>
          </div>

          <div class="aspect-video bg-black rounded-xl overflow-hidden border border-slate-800 relative flex items-center justify-center">
            <video id="masterVideoPlayer" controls preload="none" class="w-full h-full object-contain" src="/media/epic_bhagavad_gita_documentary_master.mp4">
              Your browser does not support the video tag.
            </video>
          </div>
        </div>

        <!-- Video Metadata & Quick File Access -->
        <div class="glass p-5 rounded-2xl lg:col-span-1 space-y-4">
          <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
            <i class="fa-solid fa-circle-info text-amber-400"></i> File Specifications
          </h3>

          <div class="space-y-3 text-xs">
            <div class="p-3 bg-slate-900/70 rounded-xl border border-slate-800 space-y-2">
              <div class="flex justify-between">
                <span class="text-slate-400">Resolution</span>
                <span class="font-bold text-slate-200">1280x720 (16:9 HD)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Frame Rate</span>
                <span class="font-bold text-slate-200">30.00 FPS</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Total Duration</span>
                <span id="playerDurLabel" class="font-bold text-amber-400">8m 12s (492.22s)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">File Size</span>
                <span id="playerSizeLabel" class="font-bold text-emerald-400">147.97 MB</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Audio Channels</span>
                <span class="font-bold text-slate-200">1 (Mono, 48kHz AAC)</span>
              </div>
              <div class="flex justify-between">
                <span class="text-slate-400">Outro Attached</span>
                <span class="font-bold text-purple-400">Yes (173.25s Locked)</span>
              </div>
            </div>

            <div class="pt-2 space-y-2">
              <button onclick="openFolder()" class="w-full py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs transition flex items-center justify-center gap-2">
                <i class="fa-solid fa-folder-open text-amber-400"></i> Open File in Windows Explorer
              </button>
              <a href="/media/epic_bhagavad_gita_documentary_master.mp4" download class="w-full py-2.5 px-4 rounded-xl gold-gradient text-slate-950 font-bold text-xs gold-glow hover:opacity-90 transition flex items-center justify-center gap-2">
                <i class="fa-solid fa-download"></i> Direct Download Master MP4
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 5: POOLS & SYSTEM SETTINGS -->
    <!-- ============================================================== -->
    <div id="content-settings" class="tab-pane space-y-6 hidden" style="display: none;">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- Gemini & Groq Multi-Key Pools Manager -->
        <div class="glass p-5 rounded-2xl space-y-4">
          <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
            <i class="fa-solid fa-server text-amber-400"></i> Autonomous Multi-Key Pool Telemetry
          </h3>
          <p class="text-xs text-slate-400">
            Add multiple Google AI Studio (Gemini) and Groq Cloud keys. Engine automatically round-robins and bypasses rate limits.
          </p>

          <div class="grid grid-cols-2 gap-3 text-xs">
            <div class="p-3 bg-slate-900/70 rounded-xl border border-slate-800">
              <span class="text-slate-400">Gemini Key Pool</span>
              <div id="geminiPoolStatus" class="font-bold text-emerald-400 text-sm mt-1">2 Active Keys</div>
            </div>
            <div class="p-3 bg-slate-900/70 rounded-xl border border-slate-800">
              <span class="text-slate-400">Groq Key Pool</span>
              <div id="groqPoolStatus" class="font-bold text-emerald-400 text-sm mt-1">Ready for Keys</div>
            </div>
          </div>

          <!-- Add Key Form -->
          <div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 space-y-2 text-xs">
            <span class="font-bold text-slate-300">Add New Key to Pool</span>
            <div class="flex gap-2">
              <select id="keyProvider" class="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-slate-200">
                <option value="gemini">Gemini Key</option>
                <option value="groq">Groq Key</option>
              </select>
              <input type="password" id="newKeyVal" placeholder="Paste API Key here..." class="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200">
              <button onclick="addKeyToPool()" class="px-3 py-1.5 gold-gradient text-slate-950 font-bold rounded-lg hover:opacity-90">
                Add
              </button>
            </div>
          </div>
        </div>

        <!-- Visual Lock Manager -->
        <div class="glass p-5 rounded-2xl space-y-4">
          <h3 class="font-bold text-slate-200 flex items-center gap-2 text-base">
            <i class="fa-solid fa-lock text-amber-400"></i> Visual Lock Engine Monitor
          </h3>
          <p class="text-xs text-slate-400">
            Zero Repetition Guarantee: every downloaded Pixabay clip ID is permanently locked in <code class="text-amber-400">used_visual_ids.json</code>.
          </p>

          <div class="p-4 bg-slate-900/70 rounded-xl border border-slate-800 space-y-2">
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">Locked Unique Clips</span>
              <span id="settingsClipsCount" class="font-bold text-emerald-400 text-sm">111 IDs</span>
            </div>
            <div class="flex items-center justify-between text-xs">
              <span class="text-slate-400">Repetition Guard</span>
              <span class="text-emerald-400 font-semibold">100% Zero-Repetition Lock</span>
            </div>
          </div>

          <button onclick="resetVisualLock()" class="py-2.5 px-4 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 border border-rose-500/30 text-xs font-semibold transition flex items-center gap-2">
            <i class="fa-solid fa-trash-can"></i> Reset Visual Lock Registry (Allow Clip Reuse)
          </button>
        </div>

      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 2: YOUTUBE DUAL-CHANNEL STUDIO HUB -->
    <!-- ============================================================== -->
    <div id="content-youtube" class="tab-pane space-y-6 hidden" style="display: none;">
      <div class="glass p-6 rounded-2xl space-y-5 border border-red-500/20">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-red-600/20 text-red-500 flex items-center justify-center text-xl">
              <i class="fa-brands fa-youtube"></i>
            </div>
            <div>
              <h3 class="font-bold text-slate-100 text-base flex items-center gap-2">
                YouTube Studio Dual-Channel Automation Hub
                <span class="text-xs bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded-full font-semibold">2 Channels Independent</span>
              </h3>
              <p class="text-xs text-slate-400">
                AI autonomously switches between Channel 1 and Channel 2 with custom-tailored topics, pure Hindi voiceover, and viral SEO.
              </p>
            </div>
          </div>
          <button onclick="openClientSecretModal('ch_01')" class="text-xs py-1.5 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 flex items-center gap-1.5 transition">
            <i class="fa-solid fa-key text-amber-400"></i> Setup client_secret.json
          </button>
        </div>

        <!-- 🤖 HUMAN-MIMICRY BOT: ZERO OAUTH / ZERO 403 / 1-CLICK UPLOADER -->
        <div class="p-5 bg-gradient-to-r from-red-950/40 via-purple-950/30 to-slate-900/90 rounded-2xl border-2 border-red-500/40 space-y-4 shadow-xl">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div class="flex items-center gap-3">
              <div class="w-11 h-11 rounded-xl bg-red-600 text-white flex items-center justify-center text-xl shadow-lg shadow-red-600/40 shrink-0">
                <i class="fa-solid fa-robot"></i>
              </div>
              <div>
                <h4 class="font-bold text-slate-100 text-sm sm:text-base flex items-center gap-2">
                  🤖 Human-Mimicry Studio Bot (Dual-Channel Multi-Profile)
                  <span class="text-[10px] sm:text-xs bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded-full font-semibold">100% Guaranteed</span>
                </h4>
                <p class="text-xs text-slate-300 mt-0.5">
                  इंसान की तरह Chrome में YouTube Studio खोलकर 30+ मिनट वीडियो, 24K गोल्ड थंबनेल व 10-चैप्टर SEO खुद अपलोड करता है।
                </p>
              </div>
            </div>
            <div class="flex items-center gap-2 self-start sm:self-auto shrink-0 flex-wrap">
              <span id="ch01StatusPill" class="text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <i class="fa-solid fa-circle-check"></i> Ch 1: Active
              </span>
              <span id="ch02StatusPill" class="text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1">
                <i class="fa-solid fa-circle-plus"></i> Ch 2: Ready to Connect
              </span>
            </div>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 pt-1">
            <button onclick="startHumanLogin('ch_01')" class="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-amber-300 border border-amber-500/30 font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer">
              <i class="fa-brands fa-chrome text-amber-400"></i> Login Ch 1 (गीता वाणी)
            </button>
            <button onclick="startHumanLogin('ch_02')" class="py-2.5 px-3 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 text-purple-200 border border-purple-500/40 font-bold text-xs flex items-center justify-center gap-2 transition cursor-pointer shadow-md shadow-purple-500/20">
              <i class="fa-brands fa-chrome text-purple-400"></i> Login Ch 2 (प्रेमानंद जी)
            </button>
            <button onclick="checkHumanStatus()" class="py-2.5 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs flex items-center justify-center gap-2 transition cursor-pointer">
              <i class="fa-solid fa-arrows-rotate"></i> Refresh Status
            </button>
            <button onclick="startHumanUpload(true)" class="py-2.5 px-3 rounded-xl gold-gradient text-slate-950 font-bold text-xs gold-glow hover:opacity-90 flex items-center justify-center gap-2 transition cursor-pointer">
              <i class="fa-solid fa-cloud-arrow-up text-sm"></i> 1-Click Upload (Live View)
            </button>
          </div>
          <div id="humanLogBox" class="hidden p-3 bg-black/60 rounded-xl text-xs font-mono text-emerald-400 border border-slate-800"></div>
        </div>

        <!-- Dynamic Status Banner for client_secret.json -->
        <div id="clientSecretBanner" class="hidden p-3 rounded-xl text-xs flex items-center justify-between transition-all"></div>

        <!-- 1-Click Permanent Fix for Google Error 403 Access Denied -->
        <div class="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-2.5">
          <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <span class="font-bold text-amber-300 flex items-center gap-2 text-sm">
              <i class="fa-solid fa-shield-halved text-amber-400"></i>
              Google "Error 403: access_denied" को 1-क्लिक में हमेशा के लिए हल करें:
            </span>
            <a href="https://console.cloud.google.com/apis/credentials/consent?project=geeta-channel" target="_blank" class="px-3.5 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs inline-flex items-center gap-1.5 self-start sm:self-auto transition">
              <i class="fa-solid fa-arrow-up-right-from-square"></i> Open Google Consent Screen
            </a>
          </div>
          <p class="text-slate-300 text-xs leading-relaxed">
            Google Cloud में आपका प्रोजेक्ट <strong>'Testing'</strong> मोड में है, इसलिए Google नए चैनलों को रोकता है।<br/>
            <strong>स्थायी हल (100% Guaranteed):</strong> ऊपर दिए गए बटन पर क्लिक करें ➔ <strong>'PUBLISH APP'</strong> (ऐप प्रकाशित करें) ➔ <strong>CONFIRM</strong> दबाएं! इसके बाद <strong>दुनिया का कोई भी YouTube चैनल</strong> सीधे 1-क्लिक में कनेक्ट हो जाएगा!
          </p>
        </div>

        <!-- Channels Header & Dynamic Grid -->
        <div class="space-y-3">
          <div class="flex items-center justify-between">
            <span class="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <i class="fa-brands fa-youtube text-red-500"></i> Connected YouTube Channels (<span id="chCount">2</span>)
            </span>
            <button onclick="openAddChannelModal()" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-amber-400 border border-amber-500/30 rounded-lg text-xs font-semibold flex items-center gap-1.5 cursor-pointer transition">
              <i class="fa-solid fa-plus"></i> Add New Channel
            </button>
          </div>

          <div id="channelsContainer" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Dynamically populated by updateYouTubeChannelsUI -->
          </div>
        </div>

        <!-- INLINE OAuth client_secret.json Configuration Card -->
        <div class="p-5 bg-slate-900/90 rounded-2xl border border-amber-500/30 space-y-4">
          <div class="flex items-center justify-between">
            <h4 class="font-bold text-slate-100 text-sm flex items-center gap-2">
              <i class="fa-solid fa-key text-amber-400"></i>
              Google Cloud OAuth Client Secret (client_secret.json)
            </h4>
            <span id="clientSecretBadgeInline" class="text-xs px-2.5 py-0.5 rounded-full font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30">
              Not Configured
            </span>
          </div>

          <!-- Step Guide -->
          <div class="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs space-y-1.5">
            <span class="font-bold text-amber-300 flex items-center gap-1.5">
              <i class="fa-solid fa-circle-info"></i> JSON फ़ाइल कहाँ से मिलेगी? (100% Free - 4 Steps):
            </span>
            <ol class="list-decimal list-inside space-y-1 text-slate-300 text-[11px] ml-1">
              <li><a href="https://console.cloud.google.com/" target="_blank" class="text-amber-400 underline font-semibold">console.cloud.google.com</a> खोलें और प्रोजेक्ट बनाएं।</li>
              <li><strong>APIs & Services ➔ Library</strong> में <code>YouTube Data API v3</code> को <strong>Enable</strong> करें।</li>
              <li><strong>OAuth consent screen</strong> ➔ External ➔ Test Users में अपनी YouTube Gmail जोड़ें।</li>
              <li><strong>Credentials</strong> ➔ <strong>+ CREATE CREDENTIALS</strong> ➔ <strong>OAuth client ID (Desktop App)</strong> ➔ <strong>Download JSON</strong>।</li>
            </ol>
          </div>

          <!-- Direct File Upload & Paste Inputs -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <!-- Option 1: File Pick -->
            <div class="p-4 bg-slate-950/70 rounded-xl border border-slate-800 space-y-2.5">
              <span class="font-bold text-slate-200 text-xs flex items-center gap-1.5">
                <i class="fa-solid fa-file-arrow-up text-amber-400"></i> तरीका १: डाउनलोड की गई JSON फ़ाइल चुनें
              </span>
              <p class="text-[11px] text-slate-400">अपने कंप्यूटर से <code>client_secret_*.json</code> फ़ाइल सेलेक्ट करें:</p>
              <input type="file" id="inlineSecretFileInput" accept=".json" onchange="handleInlineSecretFile(this)" class="block w-full text-xs text-slate-400 file:mr-3 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-amber-500/20 file:text-amber-300 hover:file:bg-amber-500/30 cursor-pointer">
              <span id="inlineFilePickedStatus" class="text-[11px] text-emerald-400 block font-medium"></span>
            </div>

            <!-- Option 2: Paste Content -->
            <div class="p-4 bg-slate-950/70 rounded-xl border border-slate-800 space-y-2">
              <span class="font-bold text-slate-200 text-xs flex items-center gap-1.5">
                <i class="fa-solid fa-paste text-amber-400"></i> तरीका २: JSON टेक्स्ट यहाँ पेस्ट करें
              </span>
              <textarea id="inlineSecretTextInput" rows="3" placeholder='{"installed": {"client_id": "...", "client_secret": "..."}}' class="w-full bg-slate-900 border border-slate-700 rounded-lg p-2 text-slate-200 font-mono text-[11px] focus:outline-none focus:border-amber-500"></textarea>
            </div>
          </div>

          <div class="flex items-center justify-between pt-1">
            <button onclick="saveSecretInline()" class="py-2.5 px-6 gold-gradient text-slate-950 font-bold rounded-xl gold-glow hover:opacity-90 transition flex items-center gap-2 text-xs cursor-pointer">
              <i class="fa-solid fa-check"></i> Save client_secret.json & Connect Now
            </button>
            <span class="text-slate-500 text-[11px]">Saved Path: credentials/client_secret.json</span>
          </div>
        </div>

        <!-- Publishing Distribution Selector -->
        <div class="p-3 bg-slate-900/50 rounded-xl border border-slate-800/80 flex items-center justify-between text-xs">
          <span class="text-slate-400 flex items-center gap-2">
            <i class="fa-solid fa-arrows-rotate text-emerald-400"></i> Publishing Distribution Mode:
          </span>
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-1.5 cursor-pointer text-slate-300">
              <input type="radio" name="uploadTargetChannel" value="auto" checked class="text-emerald-500 focus:ring-0">
              <span class="font-semibold text-emerald-400">Auto-Alternate 50/50 (Ch 1 ➔ Ch 2)</span>
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer text-slate-400">
              <input type="radio" name="uploadTargetChannel" value="ch_01" class="text-amber-500 focus:ring-0">
              <span>Channel 1 Only</span>
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer text-slate-400">
              <input type="radio" name="uploadTargetChannel" value="ch_02" class="text-purple-500 focus:ring-0">
              <span>Channel 2 Only</span>
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB: 24/7 DUAL-CHANNEL AUTOPILOT ENGINE (5+5 DAILY) -->
    <!-- ============================================================== -->
    <div id="content-autopilot" class="tab-pane space-y-6 hidden" style="display: none;">
      <!-- Hero Banner -->
      <div class="glass p-6 rounded-2xl border border-emerald-500/30 gold-glow relative overflow-hidden">
        <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-3">
              <span id="autoStatusBadge" class="px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center gap-2">
                <span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> AUTOPILOT STANDBY
              </span>
              <span class="text-xs text-slate-400 font-mono" id="autoClock">IST Clock</span>
            </div>
            <h2 class="text-xl md:text-2xl font-black text-slate-100 flex items-center gap-2">
              <i class="fa-solid fa-robot text-emerald-400"></i> 24/7 Dual-Channel Autopilot Studio
            </h2>
            <p class="text-xs md:text-sm text-slate-300">
              5 Videos on Channel 1 + 5 Videos on Channel 2 = <strong>10 Videos / Day</strong> (Strictly &gt; 30 to 45 Mins, Alternating 50/50)
            </p>
          </div>

          <!-- Master Control Buttons -->
          <div class="flex flex-wrap items-center gap-2">
            <button id="autoToggleBtn" onclick="startAutopilot()" class="px-5 py-2.5 rounded-xl bg-emerald-600/30 text-emerald-300 border border-emerald-500/50 hover:bg-emerald-600/50 font-bold text-xs flex items-center gap-2 cursor-pointer transition shadow-lg">
              <i class="fa-solid fa-play"></i> START 24/7 AUTOPILOT
            </button>
            <button onclick="triggerAutopilotNow()" class="px-4 py-2.5 rounded-xl bg-amber-600/30 text-amber-300 border border-amber-500/50 hover:bg-amber-600/50 font-bold text-xs flex items-center gap-2 cursor-pointer transition">
              <i class="fa-solid fa-forward-step"></i> TRIGGER NOW
            </button>
            <button onclick="launchAutopilotTerminal()" class="px-3 py-2.5 rounded-xl bg-slate-800 text-slate-300 border border-slate-700 hover:bg-slate-700 text-xs flex items-center gap-1.5 transition">
              <i class="fa-solid fa-terminal text-amber-400"></i> Open Console
            </button>
          </div>
        </div>

        <!-- Telemetry Status Bar -->
        <div class="mt-5 pt-4 border-t border-slate-800/80 grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">Active Status:</span>
            <span id="autoCurrentAction" class="text-slate-200 font-medium truncate block mt-0.5">Initializing status...</span>
          </div>
          <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">Next Scheduled Run:</span>
            <span id="autoCountdown" class="text-emerald-400 font-bold font-mono block mt-0.5">Ready to Launch</span>
          </div>
          <div class="bg-slate-900/60 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">Next In Rotation:</span>
            <span id="autoNextChannel" class="text-amber-400 font-bold block mt-0.5">चैनल २: परम कृष्ण चेतना</span>
          </div>
        </div>
      </div>

      <!-- Scoreboard: 5+5 Videos Daily -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Channel 1 Card -->
        <div class="glass p-5 rounded-2xl border-l-4 border-amber-500 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <span class="text-xs uppercase font-semibold text-amber-400 tracking-wider">Channel 1</span>
              <h3 class="text-base font-bold text-slate-100">चैनल १: दिव्य गीता वाणी</h3>
              <p class="text-xs text-slate-400">चित्त की शांति, अति-विचार से मुक्ति, कर्मयोग</p>
            </div>
            <div class="text-right">
              <span id="autoCh1Count" class="text-2xl font-black text-amber-400 font-mono">1/5</span>
              <span class="text-xs text-slate-500 block">Today's Quota</span>
            </div>
          </div>
          <!-- Progress Bar -->
          <div class="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
            <div id="autoBarCh1" class="bg-gradient-to-r from-amber-500 to-amber-400 h-3 rounded-full transition-all duration-500" style="width: 20%;"></div>
          </div>
          <div class="text-xs text-slate-400 flex items-center justify-between">
            <span>Music: Meditative Flute & Tanpura Drone</span>
            <span class="text-emerald-400 font-medium"><i class="fa-solid fa-check"></i> Session Active</span>
          </div>
        </div>

        <!-- Channel 2 Card -->
        <div class="glass p-5 rounded-2xl border-l-4 border-purple-500 space-y-4">
          <div class="flex items-center justify-between">
            <div>
              <span class="text-xs uppercase font-semibold text-purple-400 tracking-wider">Channel 2</span>
              <h3 class="text-base font-bold text-slate-100">चैनल २: परम कृष्ण चेतना</h3>
              <p class="text-xs text-slate-400">मृत्यु-बोध, माया का संहार, विश्वरूप, आत्म-साक्षात्कार</p>
            </div>
            <div class="text-right">
              <span id="autoCh2Count" class="text-2xl font-black text-purple-400 font-mono">0/5</span>
              <span class="text-xs text-slate-500 block">Today's Quota</span>
            </div>
          </div>
          <!-- Progress Bar -->
          <div class="w-full bg-slate-800 rounded-full h-3 overflow-hidden">
            <div id="autoBarCh2" class="bg-gradient-to-r from-purple-500 to-pink-500 h-3 rounded-full transition-all duration-500" style="width: 0%;"></div>
          </div>
          <div class="text-xs text-slate-400 flex items-center justify-between">
            <span>Music: Vrindavan Devotional Prem Ras</span>
            <span class="text-emerald-400 font-medium"><i class="fa-solid fa-check"></i> Session Active</span>
          </div>
        </div>
      </div>

      <!-- Hard-Locked Production Standards -->
      <div class="glass p-5 rounded-2xl space-y-4">
        <h4 class="font-bold text-slate-200 text-sm flex items-center gap-2">
          <i class="fa-solid fa-shield-check text-emerald-400"></i> Hard-Locked 24/7 Cinema Production Rules
        </h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">🎙️ Voice Narration:</span>
            <span class="text-emerald-400 font-medium">Google Free Realistic ('Charon')</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">🔊 Voice Volume:</span>
            <span class="text-amber-400 font-medium">150% Studio Boosted (volume=1.50)</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">✨ Subtitles:</span>
            <span class="text-amber-300 font-medium">24K Gold Fast Cards (MarginV=50)</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">🎵 Background Music:</span>
            <span class="text-blue-400 font-medium">Channel-Curated Devotional Soundscape</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">⏱️ Video Duration:</span>
            <span class="text-purple-400 font-medium">Strictly &gt; 30 to 45 Minutes Guaranteed</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">🔄 Rotation Protocol:</span>
            <span class="text-emerald-400 font-medium">Strict 50/50 1-on-1 (ch_01 &harr; ch_02)</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">⏳ Organic Cadence:</span>
            <span class="text-slate-200 font-medium">~115 to 135 Mins Delay per Video</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">👁️ Visibility Mode:</span>
            <span class="text-amber-400 font-bold">UNLISTED (अनलिस्टेड पब्लिश)</span>
          </div>
          <div class="bg-slate-900/50 p-3 rounded-xl border border-slate-800">
            <span class="text-slate-400 block font-semibold">🌅 Quota Reset:</span>
            <span class="text-slate-200 font-medium">Auto-resets to 0/5 at 00:00:00 IST</span>
          </div>
        </div>
      </div>

      <!-- Completed Videos History Table -->
      <div class="glass p-5 rounded-2xl space-y-4">
        <div class="flex items-center justify-between">
          <h4 class="font-bold text-slate-200 text-sm flex items-center gap-2">
            <i class="fa-solid fa-list-check text-amber-400"></i> Autopilot Publishing History
          </h4>
          <span class="text-xs text-slate-400 font-mono">Total Completed Today: <strong id="autoTotalCount" class="text-amber-400">1/10</strong></span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-xs text-left text-slate-300">
            <thead class="text-slate-500 uppercase bg-slate-900/70 border-b border-slate-800">
              <tr>
                <th class="py-2.5 px-3">Time (IST)</th>
                <th class="py-2.5 px-3">Channel</th>
                <th class="py-2.5 px-3">Topic Title</th>
                <th class="py-2.5 px-3">Duration</th>
                <th class="py-2.5 px-3">Status / YouTube Link</th>
              </tr>
            </thead>
            <tbody id="autoHistoryBody" class="divide-y divide-slate-800">
              <tr>
                <td class="py-3 px-3 font-mono text-slate-400">2026-10-26 17:15 IST</td>
                <td class="py-3 px-3"><span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">ch_01</span></td>
                <td class="py-3 px-3 text-slate-200 font-medium">जब मन पूरी तरह टूट जाए... श्रीकृष्ण का यह एक कठोर सत्य सुन लो</td>
                <td class="py-3 px-3 font-mono">21.82 Mins</td>
                <td class="py-3 px-3">
                  <a href="https://youtu.be/xlZ6AkTv7y8" target="_blank" class="text-emerald-400 hover:underline flex items-center gap-1 font-semibold">
                    <i class="fa-brands fa-youtube text-red-500"></i> https://youtu.be/xlZ6AkTv7y8
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- ============================================================== -->
    <!-- TAB 8: 1-HOUR COLAB HYPERSPEED (10 VIDEOS BATCH) -->
    <!-- ============================================================== -->
    <div id="content-colab" class="tab-pane space-y-6 hidden" style="display: none;">
      
      <!-- Top Colab Beast Banner -->
      <div class="glass p-6 rounded-2xl border border-cyan-500/40 relative overflow-hidden bg-gradient-to-r from-slate-900/90 via-cyan-950/20 to-slate-900/90 shadow-2xl">
        <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 relative z-10">
          <div class="space-y-2">
            <div class="flex items-center gap-3">
              <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 flex items-center gap-1.5 shadow-sm">
                <i class="fa-solid fa-microchip text-cyan-400"></i> Free NVIDIA Tesla T4 GPU (16GB VRAM)
              </span>
              <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-500/20 text-amber-300 border border-amber-500/40">
                10 Videos in &lt; 1 Hour
              </span>
              <span class="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">
                100% Strictly UNLISTED
              </span>
            </div>
            <h2 class="text-2xl font-black text-slate-100 flex items-center gap-3">
              <span class="text-cyan-400">⚡ Google Colab Free HyperEngine:</span> 1-Hour 10-Video Cloud Production Beast
            </h2>
            <p class="text-xs text-slate-300 max-w-3xl leading-relaxed">
              Google Colab के फ्री Tesla T4 GPU (Dual Hardware NVENC) पर एक 35-मिनट का वीडियो केवल <span class="text-cyan-300 font-bold">~3.5 मिनट</span> में रेंडर होता है! 
              1 घंटे के अंदर कुल <span class="text-amber-300 font-bold">10 वीडियो (5 चैनल १ + 5 चैनल २)</span> Google Free Charon 150% Voice, 24K Gold Nirmala UI Subtitles और शुद्ध हिंदी में जनरेट होकर सीधे YouTube पर <span class="text-emerald-300 font-bold">UNLISTED</span> अपलोड होते हैं।
            </p>
          </div>

          <!-- Quick Action Buttons -->
          <div class="flex flex-wrap lg:flex-nowrap items-center gap-3 w-full lg:w-auto">
            <button onclick="startColabHyperRun()" id="colabStartBtn" class="px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-sm flex items-center gap-2 shadow-lg shadow-cyan-500/20 transition-all cursor-pointer whitespace-nowrap active:scale-95">
              <i class="fa-solid fa-play"></i> ▶️ START 1-HOUR HYPER-RUN (10 VIDEOS)
            </button>
            <button onclick="launchColabInBrowser()" class="px-4 py-3 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/50 text-purple-200 font-bold text-xs flex items-center gap-2 transition-all cursor-pointer whitespace-nowrap">
              <i class="fa-solid fa-arrow-up-right-from-square text-purple-400"></i> 📂 OPEN GOOGLE COLAB
            </button>
            <button onclick="downloadColabNotebook()" class="px-3.5 py-3 rounded-xl bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-300 font-bold text-xs flex items-center gap-2 transition-all cursor-pointer whitespace-nowrap">
              <i class="fa-solid fa-download"></i> ⬇️ .IPYNB
            </button>
            <button onclick="stopColabHyperRun()" class="px-3.5 py-3 rounded-xl bg-red-500/20 hover:bg-red-500/30 border border-red-500/40 text-red-400 font-bold text-xs flex items-center gap-2 transition-all cursor-pointer whitespace-nowrap">
              <i class="fa-solid fa-stop"></i> STOP
            </button>
          </div>
        </div>
      </div>

      <!-- Live Production Scoreboard (3 KPI Cards) -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-5">
        
        <!-- KPI 1: Overall 1-Hour Progress -->
        <div class="glass p-5 rounded-2xl border border-brand-border space-y-3 relative overflow-hidden">
          <div class="flex items-center justify-between text-xs">
            <span class="text-slate-400 font-medium">1-Hour Master Batch Progress</span>
            <span id="colabBatchStatusBadge" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700">IDLE</span>
          </div>
          <div class="flex items-baseline justify-between">
            <div class="text-3xl font-black text-cyan-400 font-mono" id="colabBatchProgressText">0 / 10</div>
            <div class="text-xs text-slate-400 font-mono">Elapsed: <span id="colabBatchElapsed" class="text-slate-200 font-bold">0m 0s</span></div>
          </div>
          <div class="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden">
            <div id="colabBatchProgressBar" class="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500" style="width: 0%;"></div>
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between">
            <span>⏱️ Target: &lt; 60 Minutes</span>
            <span id="colabCurrentActionText" class="text-slate-300 truncate max-w-[200px]">Ready to launch</span>
          </div>
        </div>

        <!-- KPI 2: Channel 1 Breakdown -->
        <div class="glass p-5 rounded-2xl border border-amber-500/30 space-y-3 relative overflow-hidden bg-amber-950/5">
          <div class="flex items-center justify-between text-xs">
            <span class="text-amber-400 font-bold flex items-center gap-1.5">
              <i class="fa-solid fa-om text-amber-500"></i> चैनल १: दिव्य गीता वाणी
            </span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30">ch_01</span>
          </div>
          <div class="flex items-baseline justify-between">
            <div class="text-3xl font-black text-amber-400 font-mono" id="colabCh1Count">0 / 5</div>
            <span class="text-xs text-slate-400">Meditative Gita</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div id="colabCh1ProgressBar" class="h-full bg-amber-500 rounded-full transition-all duration-500" style="width: 0%;"></div>
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between">
            <span>Flute BGM • 150% Voice</span>
            <span class="text-emerald-400 font-semibold">UNLISTED</span>
          </div>
        </div>

        <!-- KPI 3: Channel 2 Breakdown -->
        <div class="glass p-5 rounded-2xl border border-purple-500/30 space-y-3 relative overflow-hidden bg-purple-950/5">
          <div class="flex items-center justify-between text-xs">
            <span class="text-purple-400 font-bold flex items-center gap-1.5">
              <i class="fa-solid fa-dharmachakra text-purple-500"></i> चैनल २: परम कृष्ण चेतना
            </span>
            <span class="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30">ch_02</span>
          </div>
          <div class="flex items-baseline justify-between">
            <div class="text-3xl font-black text-purple-400 font-mono" id="colabCh2Count">0 / 5</div>
            <span class="text-xs text-slate-400">Premanand/Cosmic</span>
          </div>
          <div class="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div id="colabCh2ProgressBar" class="h-full bg-purple-500 rounded-full transition-all duration-500" style="width: 0%;"></div>
          </div>
          <div class="text-[11px] text-slate-400 flex items-center justify-between">
            <span>Vrindavan BGM • 150% Voice</span>
            <span class="text-emerald-400 font-semibold">UNLISTED</span>
          </div>
        </div>

      </div>

      <!-- 2-Way Execution Protocol Guide -->
      <div class="glass p-5 rounded-2xl border border-brand-border space-y-4">
        <h3 class="font-bold text-slate-200 text-sm flex items-center gap-2">
          <i class="fa-solid fa-circle-nodes text-cyan-400"></i> Google Colab Free Automation Protocol (Zero-Configuration)
        </h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2">
            <div class="font-bold text-cyan-300 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center text-xs">1</span>
              तरीका १: डैशबोर्ड से सीधे ऑटोमेशन (1-Click)
            </div>
            <p class="text-slate-400 leading-relaxed">
              ऊपर दिए गए <b class="text-slate-200">"▶️ START 1-HOUR HYPER-RUN"</b> बटन पर क्लिक करें। बैकएंड बिना किसी रुकावट के लगातार 10 वीडियो (5 Ch1 + 5 Ch2) का बैच शुरू कर देगा। नीचे दिए गए लाइव क्लाउड टर्मिनल में हर वीडियो की प्रगति और लिंक लाइव दिखेंगे।
            </p>
          </div>
          <div class="bg-slate-900/80 p-4 rounded-xl border border-slate-800 space-y-2">
            <div class="font-bold text-purple-300 flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-purple-500/20 text-purple-400 flex items-center justify-center text-xs">2</span>
              तरीका २: Google Colab वेब में 1-क्लिक GPU रन (Free T4 Cloud)
            </div>
            <p class="text-slate-400 leading-relaxed">
              <b class="text-slate-200">"📂 OPEN GOOGLE COLAB"</b> पर क्लिक करें। आपके ब्राउज़र में Colab खुल जाएगा (आपका Google अकाउंट पहले से लॉग-इन रहेगा)। वहाँ <code class="text-amber-300">Krishna_AI_Colab_HyperEngine.ipynb</code> अपलोड करके <b class="text-slate-200">Runtime ➔ Run all</b> दबाएं। 16GB Tesla T4 GPU 35 मिनट में सभी 10 वीडियो तैयार कर देगा!
            </p>
          </div>
        </div>
      </div>

      <!-- GitHub Actions 10-Worker Cloud Parallel Beast Card -->
      <div class="glass p-5 rounded-2xl border border-indigo-500/40 space-y-4 bg-gradient-to-r from-slate-900/90 via-indigo-950/20 to-slate-900/90 shadow-xl">
        <div class="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/40 flex items-center gap-1.5">
                <i class="fa-brands fa-github text-white"></i> GitHub Actions Matrix Concurrency
              </span>
              <span id="ghRunStatusBadge" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700">STANDBY</span>
            </div>
            <h3 class="font-extrabold text-slate-100 text-base mt-1 flex items-center gap-2">
              <i class="fa-solid fa-cloud-bolt text-indigo-400"></i> 1-Click 10-Video Parallel Cloud Dispatcher (Zero PC Load)
            </h3>
            <p class="text-xs text-slate-300">
              1-क्लिक करते ही GitHub क्लाउड पर <b>10 समानांतर Linux VMs</b> एक साथ चालू होकर 10 वीडियो (>30 मिनट, 5 Ch1 + 5 Ch2) बनाएँगी और काम पूरा होते ही <b>स्वतः शटडाउन</b> हो जाएँगी!
            </p>
          </div>
          <button onclick="dispatchGitHubCloudRun()" id="ghDispatchBtn" class="px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-400 hover:to-purple-500 text-white font-black text-xs flex items-center gap-2 shadow-lg shadow-indigo-500/25 transition-all cursor-pointer whitespace-nowrap active:scale-95">
            <i class="fa-solid fa-rocket"></i> 🚀 DISPATCH 10 PARALLEL CLOUD WORKERS
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-slate-800 text-xs">
          <div>
            <label class="block text-slate-400 mb-1 font-semibold">GitHub Repository (owner/repo):</label>
            <input type="text" id="ghRepoInput" placeholder="e.g. yourusername/krishna-ai-cinema" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none">
          </div>
          <div>
            <label class="block text-slate-400 mb-1 font-semibold">GitHub Personal Access Token (PAT with 'workflow' scope):</label>
            <div class="flex gap-2">
              <input type="password" id="ghTokenInput" placeholder="ghp_xxxxxxxxxxxxxxxxxxxx" class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 font-mono text-xs focus:border-indigo-500 outline-none">
              <button onclick="saveGitHubConfig()" class="px-3 py-2 bg-indigo-600/30 hover:bg-indigo-600/50 border border-indigo-500/50 text-indigo-200 rounded-lg font-bold text-xs whitespace-nowrap cursor-pointer">
                Save
              </button>
            </div>
          </div>
        </div>

        <div id="ghRunInfoBox" class="text-xs text-slate-400 flex items-center justify-between pt-1">
          <span>🔗 GitHub Actions URL: <a id="ghActionLink" href="#" target="_blank" class="text-indigo-400 hover:underline">Configured Repository Actions</a></span>
          <span id="ghLastRunText" class="font-mono text-slate-500">No runs triggered yet</span>
        </div>
        <div id="ghWorkerGrid" class="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-2 border-t border-slate-800"></div>
      </div>

      <!-- Live Terminal Console -->
      <div class="glass p-5 rounded-2xl border border-brand-border space-y-3">
        <div class="flex items-center justify-between">
          <h3 class="font-bold text-slate-200 text-sm flex items-center gap-2">
            <i class="fa-solid fa-terminal text-cyan-400"></i> Colab HyperSpeed Live Cloud Terminal
          </h3>
          <span class="text-[11px] text-slate-500 font-mono">Auto-streaming live stdout/telemetry</span>
        </div>
        <div id="colabTerminalLogs" class="w-full h-64 bg-black/90 p-4 rounded-xl font-mono text-xs text-emerald-400 overflow-y-auto border border-slate-800 space-y-1">
          <div class="text-slate-500">⚡ [COLAB HYPERSPEED STANDBY] Ready to launch 10-video batch in &lt; 1 hour...</div>
        </div>
      </div>

      <!-- Real-Time Uploaded YouTube Videos Table -->
      <div class="glass p-5 rounded-2xl border border-brand-border space-y-4">
        <div class="flex items-center justify-between">
          <h3 class="font-bold text-slate-200 text-sm flex items-center gap-2">
            <i class="fa-brands fa-youtube text-red-500"></i> 1-Hour Hyper-Run Completed Videos (Strictly UNLISTED)
          </h3>
          <span class="text-xs text-slate-400">Auto-refreshes as each video uploads</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs text-slate-300">
            <thead class="bg-slate-900/60 uppercase text-[10px] text-slate-400 font-bold border-b border-brand-border">
              <tr>
                <th class="py-2.5 px-3">#</th>
                <th class="py-2.5 px-3">Channel</th>
                <th class="py-2.5 px-3">Topic / Title</th>
                <th class="py-2.5 px-3">Video Duration</th>
                <th class="py-2.5 px-3">Render Time</th>
                <th class="py-2.5 px-3">YouTube Link (UNLISTED)</th>
              </tr>
            </thead>
            <tbody id="colabHistoryBody" class="divide-y divide-slate-800">
              <tr>
                <td colspan="6" class="py-6 text-center text-slate-500 italic">No videos in current hyper-batch yet. Click "START 1-HOUR HYPER-RUN" to begin!</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

  </main>

  <!-- Footer -->
  <footer class="border-t border-brand-border py-4 px-6 text-center text-xs text-slate-500 mt-auto">
    🕉️ Shrimad Bhagavad Gita Autonomous Production Studio • 10-Agent Groq Swarm • Gemini Multi-Key Pool
  </footer>

  <!-- Client Secret Setup & Google Cloud Guide Modal -->
  <div id="clientSecretModal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4 hidden">
    <div class="glass max-w-2xl w-full rounded-2xl border border-amber-500/30 p-6 space-y-5 relative max-h-[90vh] overflow-y-auto">
      <div class="flex items-start justify-between">
        <div>
          <h3 class="font-bold text-slate-100 text-lg flex items-center gap-2">
            <i class="fa-solid fa-key text-amber-400"></i> YouTube Studio API Login Setup
          </h3>
          <p class="text-xs text-slate-400 mt-1">
            Google YouTube Data API v3 OAuth2 Configuration (100% Free)
          </p>
        </div>
        <button onclick="closeClientSecretModal()" class="text-slate-400 hover:text-white p-1 text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <div class="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl space-y-2 text-xs">
        <span class="font-bold text-amber-300 flex items-center gap-1.5 text-sm">
          <i class="fa-solid fa-circle-question"></i> ब्राउज़र क्यों नहीं खुला? (Why didn't browser open?)
        </span>
        <p class="text-slate-300 leading-relaxed">
          Google सुरक्षा नियमों के अनुसार, किसी भी बॉट या डेस्कटॉप ऐप को आपके YouTube चैनल से कनेक्ट करने के लिए Google Cloud Console से एक <strong><code>client_secret.json</code></strong> फ़ाइल लगानी होती है। इसके बिना Google OAuth अनुमति लिंक नहीं बना सकता। यह 1-टाइम सेटअप केवल 2 मिनट का है।
        </p>
      </div>

      <!-- Step-by-Step Instructions -->
      <div class="space-y-3 text-xs">
        <span class="font-bold text-slate-200 uppercase tracking-wider text-[11px] flex items-center gap-1.5">
          <i class="fa-solid fa-list-check text-amber-400"></i> 4 Simple Steps to Get client_secret.json (Free):
        </span>
        <div class="space-y-2">
          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 flex items-start gap-2.5">
            <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center shrink-0 text-[11px]">1</span>
            <div>
              <span class="font-bold text-slate-200">Google Cloud Console खोलें:</span>
              <p class="text-slate-400 mt-0.5">
                <a href="https://console.cloud.google.com/" target="_blank" class="text-amber-400 underline hover:text-amber-300 font-semibold">console.cloud.google.com</a> पर जाएं (अपनी YouTube चैनल वाली Gmail ID से लॉगिन करें) और एक नया प्रोजेक्ट बनाएं (उदा. "Krishna Studio").
              </p>
            </div>
          </div>

          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 flex items-start gap-2.5">
            <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center shrink-0 text-[11px]">2</span>
            <div>
              <span class="font-bold text-slate-200">YouTube Data API v3 Enable करें:</span>
              <p class="text-slate-400 mt-0.5">
                बाईं ओर <strong>APIs & Services ➔ Library</strong> में जाएं, सर्च करें <code>YouTube Data API v3</code> और <strong>Enable</strong> बटन दबाएं।
              </p>
            </div>
          </div>

          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 flex items-start gap-2.5">
            <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center shrink-0 text-[11px]">3</span>
            <div>
              <span class="font-bold text-slate-200">OAuth Consent Screen सेट करें:</span>
              <p class="text-slate-400 mt-0.5">
                <strong>APIs & Services ➔ OAuth consent screen</strong> पर जाएं, <strong>External</strong> चुनें, App Name में <code>Geeta Bot</code> लिखें, और नीचे <strong>Test Users</strong> में अपनी YouTube वाली Gmail जोड़ें।
              </p>
            </div>
          </div>

          <div class="p-2.5 bg-slate-900/80 rounded-lg border border-slate-800 flex items-start gap-2.5">
            <span class="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 font-bold flex items-center justify-center shrink-0 text-[11px]">4</span>
            <div>
              <span class="font-bold text-slate-200">Credentials ➔ Download JSON:</span>
              <p class="text-slate-400 mt-0.5">
                <strong>APIs & Services ➔ Credentials</strong> ➔ <strong>+ CREATE CREDENTIALS</strong> ➔ <strong>OAuth client ID</strong> चुनें। Application type में <strong>Desktop App</strong> चुनें और Create दबाएं। इसके बाद <strong>Download JSON</strong> बटन दबाएं।
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- File Upload or Paste Box -->
      <div class="p-4 bg-slate-900/90 rounded-xl border border-slate-800 space-y-3 text-xs">
        <span class="font-bold text-slate-200">डाउनलोड की गई फ़ाइल यहाँ अपलोड या पेस्ट करें:</span>

        <div class="flex items-center gap-3">
          <label class="flex-1 py-2.5 px-3 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 cursor-pointer flex items-center justify-center gap-2 transition font-medium">
            <i class="fa-solid fa-file-arrow-up text-amber-400"></i>
            <span id="fileUploadLabel">Select client_secret_*.json file from computer</span>
            <input type="file" id="secretFileInput" accept=".json" class="hidden" onchange="handleSecretFileUpload(this)">
          </label>
        </div>

        <div class="relative">
          <div class="text-[11px] text-slate-500 mb-1">या नीचे JSON कोड पेस्ट करें:</div>
          <textarea id="secretPasteInput" rows="4" class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-200 font-mono text-xs focus:outline-none focus:border-amber-500" placeholder='{"installed": {"client_id": "...", "client_secret": "..."}}'></textarea>
        </div>

        <div class="flex items-center justify-between pt-1">
          <button onclick="saveSecretAndConnect()" class="py-2.5 px-5 gold-gradient text-slate-950 font-bold rounded-xl gold-glow hover:opacity-90 transition flex items-center gap-2">
            <i class="fa-solid fa-check"></i> Save client_secret.json & Connect
          </button>
          <span class="text-slate-500 text-[11px]">Location: credentials/client_secret.json</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Direct Google OAuth 1-Click Modal -->
  <div id="oauthConnectingModal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4 hidden">
    <div class="glass max-w-lg w-full rounded-2xl border border-red-500/40 p-6 space-y-5 text-center relative shadow-2xl">
      <div class="w-16 h-16 rounded-2xl bg-red-600/20 text-red-500 flex items-center justify-center text-3xl mx-auto border border-red-500/30">
        <i class="fa-brands fa-google"></i>
      </div>
      <div>
        <h3 class="font-extrabold text-slate-100 text-xl" id="oauthModalTitle">
          YouTube Studio Google Login
        </h3>
        <p class="text-xs text-slate-400 mt-1.5" id="oauthModalSub">
          ब्राउज़र में Google का आधिकारिक लॉगिन पेज खोला गया है।
        </p>
      </div>

      <!-- Main Action Button -->
      <div class="space-y-3 pt-1">
        <a id="oauthDirectLinkBtn" href="#" target="_blank" class="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-500 hover:to-rose-500 text-white font-bold flex items-center justify-center gap-2 text-sm shadow-lg shadow-red-600/30 transition transform hover:scale-[1.02]">
          <i class="fa-solid fa-arrow-up-right-from-square"></i>
          👉 Google पर लॉगिन करें (Click to Login)
        </a>
        <p class="text-[11px] text-slate-400 leading-relaxed">
          ऊपर दिए गए लाल बटन पर क्लिक करके अपने YouTube चैनल वाली Gmail ID चुनें और <strong>Allow (अनुमति दें)</strong> पर क्लिक करें।
        </p>
      </div>

      <!-- Live Waiting Status -->
      <div id="oauthWaitingBox" class="p-3 bg-slate-900/90 rounded-xl border border-slate-800 flex items-center justify-center gap-3 text-xs text-amber-400">
        <i class="fa-solid fa-spinner animate-spin text-sm"></i>
        <span>Google अनुमति (OAuth Callback) की प्रतीक्षा कर रहे हैं...</span>
      </div>

      <!-- Close / Cancel Button -->
      <div class="pt-1">
        <button onclick="closeOAuthModal()" class="text-xs text-slate-500 hover:text-slate-300 underline cursor-pointer">
          रद्द करें / बंद करें (Close)
        </button>
      </div>
    </div>
  </div>

  <!-- Add New YouTube Channel Modal -->
  <div id="addChannelModal" class="fixed inset-0 bg-black/85 backdrop-blur-md z-50 flex items-center justify-center p-4 hidden">
    <div class="glass max-w-md w-full rounded-2xl border border-amber-500/40 p-6 space-y-4 relative shadow-2xl">
      <div class="flex items-center justify-between">
        <h3 class="font-bold text-slate-100 text-base flex items-center gap-2">
          <i class="fa-brands fa-youtube text-red-500"></i> Add New YouTube Channel
        </h3>
        <button onclick="closeAddChannelModal()" class="text-slate-400 hover:text-white p-1 text-lg">
          <i class="fa-solid fa-xmark"></i>
        </button>
      </div>

      <p class="text-xs text-slate-400">
        नया YouTube चैनल जोड़ें। जोड़ने के बाद आप सीधे <strong>'Login / Connect'</strong> दबाकर इसे Google से जोड़ सकेंगे।
      </p>

      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-300 mb-1">चैनल का नाम (Channel Name)</label>
          <input type="text" id="newChName" placeholder="उदा. Premanand Ji Vichar • Fan Channel" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-slate-200 focus:outline-none focus:border-amber-500 text-xs">
        </div>

        <div>
          <label class="block font-semibold text-slate-300 mb-1">निश / विषय (Channel Focus / Niche)</label>
          <input type="text" id="newChNiche" placeholder="उदा. प्रेमानंद जी महाराज प्रवचन, भगवद्गीता सार" class="w-full bg-slate-900 border border-slate-700 rounded-xl p-3 text-slate-200 focus:outline-none focus:border-amber-500 text-xs">
        </div>
      </div>

      <div class="flex items-center gap-2 pt-2">
        <button onclick="closeAddChannelModal()" class="flex-1 py-2.5 px-4 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold text-xs transition">
          रद्द करें
        </button>
        <button onclick="submitAddChannel()" class="flex-1 py-2.5 px-4 gold-gradient text-slate-950 font-bold rounded-xl gold-glow hover:opacity-90 transition text-xs flex items-center justify-center gap-1.5 cursor-pointer">
          <i class="fa-solid fa-plus"></i> चैनल जोड़ें (Add Channel)
        </button>
      </div>
    </div>
  </div>

  <!-- Dashboard JavaScript Logic -->
  <script>
    var evtSource = null;
    var connectingChannelId = null;
    var targetChannelToConnect = 'ch_01';



    function updateDurDisplay(val) {
      const isLongForm = val >= 30;
      document.getElementById('durDisplay').innerText = isLongForm ? `${val} Minutes (Strictly > 30 Mins Guaranteed)` : `${val} Minutes`;
      let ch = 1;
      let words = val * 125;
      if (val <= 5) { ch = 1; }
      else if (val <= 15) { ch = 4; }
      else if (val <= 25) { ch = 6; }
      else if (val <= 45) { ch = 10; words = Math.max(words, 4400); }
      else if (val <= 65) { ch = 14; }
      else { ch = Math.min(20, Math.max(14, Math.floor(val / 4.5))); }
      document.getElementById('chapterCalc').innerText = `Auto-Scales into: ${ch} Expansive Chapters (~${words} Words, 0% Sanskrit Chaupai Spoken)`;
    }

    async function fetchStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        
        const lc = document.getElementById('lockedClipsVal');
        if (lc) lc.innerText = `${data.locked_clips_count} Clips`;
        const sc = document.getElementById('settingsClipsCount');
        if (sc) sc.innerText = `${data.locked_clips_count} IDs`;
        
        if (data.gemini_pool) {
          const gk = document.getElementById('geminiKeysCount');
          if (gk) gk.innerText = data.gemini_pool.active_keys;
          const gp = document.getElementById('geminiPoolStatus');
          if (gp) gp.innerText = `${data.gemini_pool.active_keys} / ${data.gemini_pool.total_keys} Active Keys`;
        }
        if (data.groq_pool) {
          const grp = document.getElementById('groqPoolStatus');
          if (grp) grp.innerText = `${data.groq_pool.active_keys} / ${data.groq_pool.total_keys} Active Keys`;
        }

        if (data.master_video && data.master_video.exists) {
          const pDur = document.getElementById('playerDurLabel');
          if (pDur) pDur.innerText = `${data.master_video.duration_fmt} (${data.master_video.duration_sec.toFixed(2)}s)`;
          const pSize = document.getElementById('playerSizeLabel');
          if (pSize) pSize.innerText = `${data.master_video.size_mb} MB`;
        }

        if (data.youtube_channels) {
          updateYouTubeChannelsUI(data.youtube_channels, data.client_secret_ready);
        }

        const pill = document.getElementById('renderIndicator');
        const btnLaunch = document.getElementById('btnLaunch');
        const btnStop = document.getElementById('btnStop');

        if (data.is_rendering) {
          pill.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-400 animate-ping"></span> Rendering...';
          pill.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs bg-amber-500/20 text-amber-300 border border-amber-500/40';
          btnLaunch.classList.add('opacity-50', 'pointer-events-none');
          btnStop.classList.remove('hidden');
        } else {
          pill.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500"></span> Ready';
          pill.className = 'flex items-center gap-2 px-3 py-1 rounded-full text-xs bg-slate-800/80 text-slate-400 border border-slate-700';
          btnLaunch.classList.remove('opacity-50', 'pointer-events-none');
          btnStop.classList.add('hidden');
        }
      } catch (e) {
        console.error("Status fetch error", e);
      }
    }

    function connectLogStream() {
      if (evtSource) evtSource.close();
      evtSource = new EventSource('/api/render/logs');
      const consoleEl = document.getElementById('terminalConsole');

      evtSource.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.log) {
          consoleEl.innerHTML += data.log.split('\n').join('<br/>');
          consoleEl.scrollTop = consoleEl.scrollHeight;
        }
      };
    }

    async function launchRender() {
      const mode = document.querySelector('input[name="engineMode"]:checked').value;
      const topic = document.getElementById('swarmTopic') ? document.getElementById('swarmTopic').value : "";
      const duration = document.getElementById('durSlider') ? parseInt(document.getElementById('durSlider').value) : 35;
      const research_mins = parseFloat(document.getElementById('swarmResearchDuration')?.value || 10.0);
      const target_channel = document.querySelector('input[name="uploadTargetChannel"]:checked')?.value || "auto";
      await fetch('/api/render/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, topic, duration, research_mins, target_channel })
      });
      fetchStatus();
    }

    async function stopRender() {
      if (confirm('Are you sure you want to stop the current render?')) {
        await fetch('/api/render/stop', { method: 'POST' });
        fetchStatus();
      }
    }

    async function launchSwarmResearch() {
      const topic = document.getElementById('swarmTopic').value;
      const duration = parseInt(document.getElementById('durSlider').value);
      const research_mins = parseFloat(document.getElementById('swarmResearchDuration')?.value || 5.0);
      const btn = document.getElementById('btnSwarm');
      const badge = document.getElementById('swarmStatusBadge');
      
      btn.innerHTML = `<i class="fa-solid fa-spinner animate-spin"></i> 10-Agent Swarm Deep Researching (${research_mins}m)...`;
      btn.disabled = true;
      badge.innerHTML = `<span class="text-amber-400 animate-pulse">🐝 10 Agents Deep Researching (${research_mins}m)...</span>`;

      try {
        const res = await fetch('/api/research/swarm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ topic, duration, research_mins })
        });
        const data = await res.json();
        if (data.success) {
          badge.innerHTML = `<span class="text-emerald-400"><i class="fa-solid fa-circle-check"></i> ${data.chapters_count} Chapters Architected!</span>`;
          let html = `<div class="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-xl space-y-2">
            <span class="text-xs font-bold text-emerald-400">🎯 0-5s Hook Premise:</span>
            <p class="text-xs text-slate-200">${data.hook_strategy.hook_premise || ''}</p>
          </div>`;
          data.chapters.forEach(c => {
            html += `<div class="p-3 bg-slate-900/80 rounded-xl border border-slate-800 space-y-1 text-xs">
              <span class="font-bold text-amber-400">Chapter ${c.chapter_num}: ${c.title}</span>
              <p class="text-slate-400 text-[11px]">${c.shloka}</p>
              <p class="text-slate-300 text-[11px]">${c.exposition.slice(0, 180)}...</p>
            </div>`;
          });
          document.getElementById('swarmOutputContainer').innerHTML = html;
          alert(`🎉 10-Agent Swarm Research Complete! Architected ${data.chapters_count} Chapters for ${duration} Minutes.`);
        }
      } catch (e) {
        alert("Swarm Error: " + e);
      } finally {
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Launch 10-Agent Swarm Research & Script';
        btn.disabled = false;
      }
    }

    async function addKeyToPool() {
      const provider = document.getElementById('keyProvider').value;
      const key = document.getElementById('newKeyVal').value;
      if (!key) return alert('Please enter key');
      const res = await fetch('/api/keys/add', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider, key })
      });
      const data = await res.json();
      if (data.success) {
        alert(data.message);
        document.getElementById('newKeyVal').value = '';
        fetchStatus();
      } else {
        alert(data.error);
      }
    }

    function clearConsole() {
      document.getElementById('terminalConsole').innerHTML = '<div class="text-slate-500 italic">Console cleared.</div>';
    }

    async function testVoice() {
      const text = document.getElementById('voiceTestInput').value;
      const btn = document.getElementById('btnTestVoice');
      btn.innerHTML = '<i class="fa-solid fa-spinner animate-spin"></i> Processing Shure SM7B DSP...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/voice/test', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text })
        });
        const data = await res.json();
        if (data.success) {
          const container = document.getElementById('audioPlayerContainer');
          const audio = document.getElementById('audioElement');
          audio.src = data.url;
          document.getElementById('testAudioDur').innerText = `${data.duration}s`;
          container.classList.remove('hidden');
          audio.play();
        }
      } catch (e) {
        alert("Error generating audio: " + e);
      } finally {
        btn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Master with Shure SM7B DSP';
        btn.disabled = false;
      }
    }

    async function resetVisualLock() {
      if (confirm('Are you sure you want to reset the visual lock registry?')) {
        await fetch('/api/lock/reset', { method: 'POST' });
        fetchStatus();
        alert('Visual lock registry reset successfully!');
      }
    }

    async function openFolder() {
      await fetch('/api/open-folder');
    }

    function updateYouTubeChannelsUI(channels, clientSecretReady) {
      try {
        const banner = document.getElementById('clientSecretBanner');
        if (banner) {
          if (!clientSecretReady) {
            banner.className = 'p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs flex items-center justify-between text-amber-300';
            banner.innerHTML = `
              <div class="flex items-center gap-2">
                <i class="fa-solid fa-triangle-exclamation text-amber-400 text-sm"></i>
                <span><strong>Google OAuth Setup Pending:</strong> ब्राउज़र लॉगिन और ऑटो-अपलोड के लिए <code>client_secret.json</code> आवश्यक है।</span>
              </div>
              <button onclick="openClientSecretModal('ch_01')" class="px-3 py-1 bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 rounded-lg font-semibold transition flex items-center gap-1.5">
                <i class="fa-solid fa-key"></i> Setup Now (2 Mins)
              </button>
            `;
            banner.classList.remove('hidden');
          } else {
            banner.className = 'p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-xs flex items-center justify-between text-emerald-300';
            banner.innerHTML = `
              <div class="flex items-center gap-2">
                <i class="fa-solid fa-circle-check text-emerald-400"></i>
                <span><strong>OAuth Client Ready:</strong> <code>client_secret.json</code> सक्रिय है। नीचे <strong>Login / Connect</strong> बटन दबाकर चैनल जोड़ें।</span>
              </div>
              <button onclick="openClientSecretModal()" class="px-2 py-0.5 bg-slate-800 text-slate-400 hover:text-slate-200 border border-slate-700 rounded text-[11px]">
                Reconfigure
              </button>
            `;
            banner.classList.remove('hidden');
          }
        }

        if (!channels || !Array.isArray(channels)) return;

        const countEl = document.getElementById('chCount');
        if (countEl) countEl.innerText = channels.length;

        const container = document.getElementById('channelsContainer');
        if (container) {
          container.innerHTML = channels.map(ch => {
            const id = ch.channel_id;
            const isConnected = !!ch.connected;
            const name = ch.live_title || ch.configured_name || id;
            const niche = ch.niche || '';
            const subs = ch.subscribers ? Number(ch.subscribers).toLocaleString() : '--';
            const badgeColor = isConnected ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-rose-500/20 text-rose-400 border-rose-500/30';
            const badgeIcon = isConnected ? 'fa-circle-check' : 'fa-circle-xmark';
            const badgeText = isConnected ? (ch.status_badge || 'Active & Ready') : 'Not Connected';
            const btnClass = isConnected
              ? 'bg-emerald-600/20 hover:bg-emerald-600/30 text-emerald-400 border border-emerald-500/30'
              : 'bg-red-600 hover:bg-red-500 text-white shadow-lg shadow-red-600/30';
            const btnText = isConnected
              ? '<i class="fa-solid fa-arrows-rotate"></i> Re-connect'
              : '<i class="fa-solid fa-arrow-up-right-from-square"></i> Login / Connect';

            return `
              <div class="p-4 bg-slate-900/80 rounded-xl border border-slate-800 space-y-3 relative overflow-hidden flex flex-col justify-between">
                <div class="flex items-start justify-between gap-2">
                  <div class="min-w-0 flex-1">
                    <span class="text-xs font-bold text-amber-400 uppercase tracking-wider">${id}</span>
                    <h4 class="text-sm font-bold text-slate-100 mt-0.5 truncate" title="${name}">${name}</h4>
                    <p class="text-xs text-slate-400 mt-1 line-clamp-2" title="${niche}">${niche}</p>
                  </div>
                  <span class="text-xs px-2.5 py-1 rounded-full font-semibold border ${badgeColor} whitespace-nowrap">
                    <i class="fa-solid ${badgeIcon}"></i> ${badgeText}
                  </span>
                </div>

                <div class="pt-2 border-t border-slate-800 space-y-2 text-xs">
                  <div class="flex items-center justify-between">
                    <span class="text-slate-500">Subscribers: <strong class="text-slate-300">${subs}</strong></span>
                    <button onclick="loginChannel('${id}')" class="px-3.5 py-1.5 rounded-lg font-bold flex items-center gap-1.5 transition text-xs cursor-pointer border ${btnClass}">
                      ${btnText}
                    </button>
                  </div>
                  <div class="flex items-center gap-1.5 pt-1">
                    <input type="text" id="tokenInput_${id}" placeholder="Or paste token.json..." class="flex-1 bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1 text-slate-300 text-[11px] font-mono focus:outline-none focus:border-amber-500">
                    <button onclick="saveTokenInline('${id}')" class="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 text-[11px] font-semibold transition cursor-pointer">
                      Save
                    </button>
                  </div>
                </div>
              </div>
            `;
          }).join('');
        }

        const inlineBadge = document.getElementById('clientSecretBadgeInline');
        if (inlineBadge) {
          if (clientSecretReady) {
            inlineBadge.className = 'text-xs px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30';
            inlineBadge.innerHTML = '<i class="fa-solid fa-circle-check"></i> Installed & Ready';
          } else {
            inlineBadge.className = 'text-xs px-2.5 py-0.5 rounded-full font-semibold bg-rose-500/20 text-rose-400 border border-rose-500/30';
            inlineBadge.innerHTML = '<i class="fa-solid fa-circle-xmark"></i> Missing client_secret.json';
          }
        }
      } catch (err) {
        console.error('updateYouTubeChannelsUI error:', err);
      }
    }

    function handleInlineSecretFile(input) {
      const file = input.files[0];
      if (!file) return;
      const statusEl = document.getElementById('inlineFilePickedStatus');
      if (statusEl) statusEl.innerText = '✓ Selected: ' + file.name;
      const reader = new FileReader();
      reader.onload = function(e) {
        const textEl = document.getElementById('inlineSecretTextInput');
        if (textEl) textEl.value = e.target.result;
      };
      reader.readAsText(file);
    }

    function saveSecretInline() {
      const textEl = document.getElementById('inlineSecretTextInput');
      const content = textEl ? textEl.value.trim() : '';

      // Immediately open the Google OAuth sign-in window synchronously
      // This guarantees Chrome/Edge NEVER blocks the popup!
      const targetUrl = '/api/youtube/auth/redirect?channel_id=ch_01';
      window.open(targetUrl, '_blank');

      // If user pasted new JSON content, save it to server in background
      if (content) {
        fetch('/api/youtube/client-secret/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ secret_json: content })
        }).then(r => r.json()).then(data => {
          fetchStatus();
        }).catch(e => console.error(e));
      }

      // Also display connecting modal with direct link
      const modal = document.getElementById('oauthConnectingModal');
      const linkBtn = document.getElementById('oauthDirectLinkBtn');
      if (linkBtn) linkBtn.href = targetUrl;
      if (modal) {
        modal.style.setProperty('display', 'flex', 'important');
        modal.classList.remove('hidden');
      }
    }


    async function saveTokenInline(channelId) {
      const inp = document.getElementById('tokenInput_' + channelId);
      const val = inp ? inp.value.trim() : '';
      if (!val) {
        alert('कृपया Token JSON डालें!');
        return;
      }
      try {
        const res = await fetch('/api/youtube/token/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel_id: channelId, token_json: val })
        });
        const data = await res.json();
        if (data.success) {
          alert('🎉 Token saved for ' + channelId + '!');
          inp.value = '';
          fetchStatus();
        } else {
          alert('Error: ' + data.error);
        }
      } catch (e) {
        alert('त्रुटि: ' + e);
      }
    }


    function openAddChannelModal() {
      const m = document.getElementById('addChannelModal');
      if (m) {
        m.style.setProperty('display', 'flex', 'important');
        m.classList.remove('hidden');
      }
    }

    function closeAddChannelModal() {
      const m = document.getElementById('addChannelModal');
      if (m) {
        m.style.setProperty('display', 'none', 'important');
        m.classList.add('hidden');
      }
    }

    async function submitAddChannel() {
      const name = document.getElementById('newChName').value.trim();
      const niche = document.getElementById('newChNiche').value.trim();
      if (!name) {
        alert('कृपया चैनल का नाम दर्ज करें!');
        return;
      }
      try {
        const res = await fetch('/api/youtube/channels/add', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel_name: name, niche: niche })
        });
        const data = await res.json();
        if (data.success) {
          closeAddChannelModal();
          document.getElementById('newChName').value = '';
          document.getElementById('newChNiche').value = '';
          fetchStatus();
          alert('🎉 चैनल सफलतापूर्वक जुड़ गया! अब आप सीधे "Login / Connect" बटन दबाकर इसे Google से लिंक कर सकते हैं।');
        } else {
          alert('त्रुटि: ' + data.error);
        }
      } catch (e) {
        alert('चैनल जोड़ने में त्रुटि: ' + e);
      }
    }

    function openClientSecretModal(channelId = 'ch_01') {
      targetChannelToConnect = channelId;
      const m = document.getElementById('clientSecretModal');
      if (m) {
        m.style.setProperty('display', 'flex', 'important');
        m.classList.remove('hidden');
      }
    }

    function closeClientSecretModal() {
      const m = document.getElementById('clientSecretModal');
      if (m) {
        m.style.setProperty('display', 'none', 'important');
        m.classList.add('hidden');
      }
    }

    function handleSecretFileUpload(input) {
      const file = input.files[0];
      if (!file) return;
      document.getElementById('fileUploadLabel').innerText = file.name;
      const reader = new FileReader();
      reader.onload = function(e) {
        document.getElementById('secretPasteInput').value = e.target.result;
      };
      reader.readAsText(file);
    }

    function saveSecretAndConnect() {
      const raw = document.getElementById('secretPasteInput').value.trim();
      const chId = targetChannelToConnect || 'ch_01';
      const targetUrl = '/api/youtube/auth/redirect?channel_id=' + encodeURIComponent(chId);

      // Immediately open Google sign in
      window.open(targetUrl, '_blank');
      closeClientSecretModal();

      if (raw) {
        fetch('/api/youtube/client-secret/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ secret_json: raw })
        }).then(r => r.json()).then(data => {
          fetchStatus();
        }).catch(e => console.error(e));
      }

      const modal = document.getElementById('oauthConnectingModal');
      const linkBtn = document.getElementById('oauthDirectLinkBtn');
      if (linkBtn) linkBtn.href = targetUrl;
      if (modal) {
        modal.style.setProperty('display', 'flex', 'important');
        modal.classList.remove('hidden');
      }
    }


    function loginChannel(channelId) {
      connectingChannelId = channelId;
      const targetUrl = '/api/youtube/auth/redirect?channel_id=' + encodeURIComponent(channelId);
      // Synchronous open on direct click: 100% bypasses browser popup blockers!
      window.open(targetUrl, '_blank');

      // Also show helper modal with fallback link
      const modal = document.getElementById('oauthConnectingModal');
      const title = document.getElementById('oauthModalTitle');
      const sub = document.getElementById('oauthModalSub');
      const linkBtn = document.getElementById('oauthDirectLinkBtn');
      const waitingBox = document.getElementById('oauthWaitingBox');

      if (title) title.innerText = channelId === 'ch_01' ? 'चैनल १: दिव्य गीता वाणी Google Login' : 'चैनल २: परम कृष्ण चेतना Google Login';
      if (sub) sub.innerText = 'ब्राउज़र में Google का आधिकारिक लॉगिन पेज खोला गया है।';
      if (linkBtn) linkBtn.href = targetUrl;
      if (waitingBox) {
        waitingBox.className = 'p-3 bg-slate-900/90 rounded-xl border border-slate-800 flex items-center justify-center gap-3 text-xs text-amber-400';
        waitingBox.innerHTML = '<i class="fa-solid fa-spinner animate-spin text-sm"></i> <span>Google अनुमति (OAuth Callback) की प्रतीक्षा कर रहे हैं...</span>';
      }
      if (modal) {
        modal.style.setProperty('display', 'flex', 'important');
        modal.classList.remove('hidden');
      }
    }

    function closeOAuthModal() {
      const modal = document.getElementById('oauthConnectingModal');
      if (modal) {
        modal.style.setProperty('display', 'none', 'important');
        modal.classList.add('hidden');
      }
      connectingChannelId = null;
    }

    async function pasteTokenModal(channelId) {
      const raw = prompt(`Paste YouTube OAuth Token JSON for ${channelId} (from OAuth or token.json):`);
      if (!raw) return;
      try {
        const res = await fetch('/api/youtube/token/save', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel_id: channelId, token_json: raw })
        });
        const data = await res.json();
        if (data.success) {
          alert(`🎉 Token for ${channelId} saved successfully!`);
          fetchStatus();
        } else {
          alert('Error: ' + data.error);
        }
      } catch (e) {
        alert('Invalid JSON: ' + e);
      }
    }

    async function checkHumanStatus() {
      try {
        const res = await fetch('/api/youtube/human/status');
        const data = await res.json();
        const b1 = document.getElementById('ch01StatusPill');
        const b2 = document.getElementById('ch02StatusPill');
        if (b1) {
          if (data.ch_01 && data.ch_01.logged_in) {
            b1.className = 'text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1';
            b1.innerHTML = '<i class="fa-solid fa-circle-check"></i> Ch 1: गीता वाणी (Active)';
          } else {
            b1.className = 'text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1';
            b1.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Ch 1: Login Needed';
          }
        }
        if (b2) {
          if (data.ch_02 && data.ch_02.logged_in) {
            b2.className = 'text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1';
            b2.innerHTML = '<i class="fa-solid fa-circle-check"></i> Ch 2: प्रेमानंद जी (Active)';
          } else {
            b2.className = 'text-[11px] px-2.5 py-0.5 rounded-full font-semibold bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1';
            b2.innerHTML = '<i class="fa-solid fa-circle-plus"></i> Ch 2: Ready to Connect';
          }
        }
      } catch (e) {
        console.error('checkHumanStatus error:', e);
      }
    }

    async function startHumanLogin(channelId = 'ch_01') {
      const logBox = document.getElementById('humanLogBox');
      if (logBox) {
        logBox.classList.remove('hidden');
        logBox.innerHTML = `<i class="fa-solid fa-spinner animate-spin text-amber-400"></i> Launching Google Chrome for ${channelId}...`;
      }
      try {
        const res = await fetch('/api/youtube/human/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ channel_id: channelId })
        });
        const data = await res.json();
        if (logBox) {
          logBox.innerHTML = `🎉 <strong>Chrome launched for ${channelId}!</strong> Please sign in in the opened Chrome window.`;
        }
        setTimeout(checkHumanStatus, 4000);
      } catch (e) {
        if (logBox) logBox.innerHTML = '<span class="text-rose-400">Error: ' + e + '</span>';
      }
    }

    async function startHumanUpload(visible = true) {
      if (!confirm('क्या आप Master Video, 24K Gold Viral Thumbnail और Einstein SEO को सीधे YouTube Studio में अपलोड करना चाहते हैं?')) return;
      const logBox = document.getElementById('humanLogBox');
      if (logBox) {
        logBox.classList.remove('hidden');
        logBox.innerHTML = '<i class="fa-solid fa-spinner animate-spin text-amber-400"></i> Autonomous Human-Mimicry Uploader is starting in Chrome...';
      }
      try {
        const res = await fetch('/api/youtube/human/upload', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ visible: visible })
        });
        const data = await res.json();
        if (logBox) {
          logBox.innerHTML = '🚀 <strong>' + (data.message || 'Upload initiated!') + '</strong><br/>आप Chrome स्क्रीन पर अपलोड प्रगति देख सकते हैं।';
        }
      } catch (e) {
        if (logBox) logBox.innerHTML = '<span class="text-rose-400">Upload error: ' + e + '</span>';
      }
    }

    async function fetchAutopilotStatus() {
      try {
        const res = await fetch('/api/autopilot/status');
        const data = await res.json();
        const live = data.live || {};
        const control = data.control || {};
        const quota = live.daily_quota || { ch_01: '1/5', ch_02: '0/5', total_today: '1/10' };

        const elClock = document.getElementById('autoClock');
        if (elClock && live.time_ist) elClock.innerText = live.time_ist;
        const elAction = document.getElementById('autoCurrentAction');
        if (elAction && live.current_action) elAction.innerText = live.current_action;

        const elCh1 = document.getElementById('autoCh1Count');
        const elCh2 = document.getElementById('autoCh2Count');
        const elTotal = document.getElementById('autoTotalCount');
        if (elCh1) elCh1.innerText = quota.ch_01 || '1/5';
        if (elCh2) elCh2.innerText = quota.ch_02 || '0/5';
        if (elTotal) elTotal.innerText = quota.total_today || '1/10';

        const c1Num = parseInt((quota.ch_01 || '1').split('/')[0]) || 0;
        const c2Num = parseInt((quota.ch_02 || '0').split('/')[0]) || 0;
        const bar1 = document.getElementById('autoBarCh1');
        const bar2 = document.getElementById('autoBarCh2');
        if (bar1) bar1.style.width = Math.min(100, Math.round((c1Num / 5) * 100)) + '%';
        if (bar2) bar2.style.width = Math.min(100, Math.round((c2Num / 5) * 100)) + '%';

        const elNextCh = document.getElementById('autoNextChannel');
        if (elNextCh) {
          const nextId = live.next_target_channel || 'ch_02';
          elNextCh.innerText = nextId === 'ch_01' ? 'चैनल १: दिव्य गीता वाणी' : 'चैनल २: परम कृष्ण चेतना';
        }

        const elCountdown = document.getElementById('autoCountdown');
        if (elCountdown) {
          if (live.next_run_countdown_seconds > 0) {
            const m = Math.floor(live.next_run_countdown_seconds / 60);
            const s = live.next_run_countdown_seconds % 60;
            elCountdown.innerText = `${m}m ${s}s (${live.next_run_ist || ''})`;
          } else {
            elCountdown.innerText = live.next_run_ist || 'Ready';
          }
        }

        const elStatus = document.getElementById('autoStatusBadge');
        const elBtn = document.getElementById('autoToggleBtn');
        const isRunning = data.is_daemon_running && control.enabled && !control.paused;

        if (elStatus) {
          if (isRunning) {
            elStatus.className = 'px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 flex items-center gap-2';
            elStatus.innerHTML = '<span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping"></span> 24/7 AUTOPILOT ACTIVE';
          } else {
            elStatus.className = 'px-3 py-1 rounded-full text-xs font-bold bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center gap-2';
            elStatus.innerHTML = '<span class="w-2.5 h-2.5 rounded-full bg-amber-500"></span> AUTOPILOT STANDBY';
          }
        }

        if (elBtn) {
          if (isRunning) {
            elBtn.className = 'px-5 py-2.5 rounded-xl bg-rose-600/30 text-rose-300 border border-rose-500/50 hover:bg-rose-600/50 font-bold text-xs flex items-center gap-2 cursor-pointer transition shadow-lg';
            elBtn.innerHTML = '<i class="fa-solid fa-pause"></i> PAUSE AUTOPILOT';
            elBtn.onclick = stopAutopilot;
          } else {
            elBtn.className = 'px-5 py-2.5 rounded-xl bg-emerald-600/30 text-emerald-300 border border-emerald-500/50 hover:bg-emerald-600/50 font-bold text-xs flex items-center gap-2 cursor-pointer transition shadow-lg';
            elBtn.innerHTML = '<i class="fa-solid fa-play"></i> START 24/7 AUTOPILOT';
            elBtn.onclick = startAutopilot;
          }
        }

        const history = (data.state && data.state.history) ? data.state.history : [];
        const tbody = document.getElementById('autoHistoryBody');
        if (tbody && history.length > 0) {
          let rowsHtml = '';
          history.slice(-10).reverse().forEach(item => {
            const chBadge = item.channel_id === 'ch_01'
              ? '<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">ch_01</span>'
              : '<span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 font-bold">ch_02</span>';
            const ytLink = item.youtube_url ? `<a href="${item.youtube_url}" target="_blank" class="text-emerald-400 hover:underline flex items-center gap-1 font-semibold"><i class="fa-brands fa-youtube text-red-500"></i> ${item.youtube_url}</a>` : '<span class="text-slate-500 font-mono">Published</span>';
            rowsHtml += `<tr>
              <td class="py-3 px-3 font-mono text-slate-400">${item.time_ist || ''}</td>
              <td class="py-3 px-3">${chBadge}</td>
              <td class="py-3 px-3 text-slate-200 font-medium">${item.topic || 'Krishna Updesh'}</td>
              <td class="py-3 px-3 font-mono">${item.duration_mins ? item.duration_mins + ' Mins' : '>30 Mins'}</td>
              <td class="py-3 px-3">${ytLink}</td>
            </tr>`;
          });
          tbody.innerHTML = rowsHtml;
        }
      } catch(e) {}
    }

    async function startAutopilot() {
      try {
        const res = await fetch('/api/autopilot/start', { method: 'POST' });
        const d = await res.json();
        alert('✅ ' + (d.message || 'Autopilot Started!'));
        fetchAutopilotStatus();
      } catch(e) { alert('Error: ' + e); }
    }

    async function stopAutopilot() {
      try {
        const res = await fetch('/api/autopilot/stop', { method: 'POST' });
        const d = await res.json();
        alert('⏸️ ' + (d.message || 'Autopilot Paused!'));
        fetchAutopilotStatus();
      } catch(e) { alert('Error: ' + e); }
    }

    async function triggerAutopilotNow() {
      if (!confirm('क्या आप तुरंत 24/7 Autopilot में अगला 30+ मिनट का वीडियो जनरेट व अपलोड करना चाहते हैं?')) return;
      try {
        const res = await fetch('/api/autopilot/trigger-now', { method: 'POST' });
        const d = await res.json();
        alert('⚡ ' + (d.message || 'Triggered!'));
        fetchAutopilotStatus();
      } catch(e) { alert('Error: ' + e); }
    }

    async function launchAutopilotTerminal() {
      try {
        const res = await fetch('/api/autopilot/launch-terminal', { method: 'POST' });
        const d = await res.json();
        alert('🖥️ ' + (d.message || 'Launched'));
      } catch(e) { alert('Error: ' + e); }
    }

    // Colab HyperSpeed Functions
    async function fetchColabStatus() {
      try {
        const res = await fetch('/api/colab/status');
        const data = await res.json();
        const state = data.state || {};
        const isRunning = data.is_running || false;

        const elBadge = document.getElementById('colabBatchStatusBadge');
        if (elBadge) {
          if (isRunning) {
            elBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 animate-pulse';
            elBadge.innerText = '⚡ RUNNING (T4 GPU)';
          } else if (state.status === 'COMPLETED') {
            elBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
            elBadge.innerText = '✅ COMPLETED';
          } else {
            elBadge.className = 'px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-slate-800 text-slate-400 border border-slate-700';
            elBadge.innerText = 'IDLE';
          }
        }

        const elProgressText = document.getElementById('colabBatchProgressText');
        const elProgressBar = document.getElementById('colabBatchProgressBar');
        const curIdx = state.current_video_idx || 0;
        const total = state.total_target || 10;
        if (elProgressText) elProgressText.innerText = `${curIdx} / ${total}`;
        if (elProgressBar) elProgressBar.style.width = `${Math.min((curIdx / total) * 100, 100)}%`;

        const elElapsed = document.getElementById('colabBatchElapsed');
        if (elElapsed && state.started_at) {
          const elSec = state.elapsed_seconds || Math.floor((Date.now() / 1000) - state.started_at);
          const m = Math.floor(elSec / 60);
          const s = elSec % 60;
          elElapsed.innerText = `${m}m ${s}s`;
        }

        const elAction = document.getElementById('colabCurrentActionText');
        if (elAction && state.current_action) elAction.innerText = state.current_action;

        // Channel breakdown
        const counts = state.counts || { ch_01: 0, ch_02: 0 };
        const elCh1 = document.getElementById('colabCh1Count');
        const elCh1Bar = document.getElementById('colabCh1ProgressBar');
        if (elCh1) elCh1.innerText = `${counts.ch_01 || 0} / 5`;
        if (elCh1Bar) elCh1Bar.style.width = `${Math.min(((counts.ch_01 || 0) / 5) * 100, 100)}%`;

        const elCh2 = document.getElementById('colabCh2Count');
        const elCh2Bar = document.getElementById('colabCh2ProgressBar');
        if (elCh2) elCh2.innerText = `${counts.ch_02 || 0} / 5`;
        if (elCh2Bar) elCh2Bar.style.width = `${Math.min(((counts.ch_02 || 0) / 5) * 100, 100)}%`;

        // Logs
        const elLogs = document.getElementById('colabTerminalLogs');
        if (elLogs && data.logs) {
          elLogs.innerHTML = data.logs.split('\n').map(l => `<div>${escapeHtml(l)}</div>`).join('');
          elLogs.scrollTop = elLogs.scrollHeight;
        }

        // Table
        const tbody = document.getElementById('colabHistoryBody');
        const completed = state.completed_videos || [];
        if (tbody && completed.length > 0) {
          let rowsHtml = '';
          completed.forEach(item => {
            const chBadge = item.channel_id === 'ch_01'
              ? '<span class="px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">ch_01</span>'
              : '<span class="px-2 py-0.5 rounded bg-purple-500/20 text-purple-400 font-bold">ch_02</span>';
            const ytLink = item.youtube_url && item.youtube_url !== 'UNLISTED_UPLOADED'
              ? `<a href="${item.youtube_url}" target="_blank" class="text-emerald-400 hover:underline flex items-center gap-1 font-semibold"><i class="fa-brands fa-youtube text-red-500"></i> ${item.youtube_url}</a>`
              : '<span class="text-emerald-400 font-semibold"><i class="fa-solid fa-check"></i> Uploaded Unlisted</span>';
            rowsHtml += `<tr>
              <td class="py-2.5 px-3 font-mono text-cyan-400 font-bold">#${item.video_num}</td>
              <td class="py-2.5 px-3">${chBadge}</td>
              <td class="py-2.5 px-3 text-slate-200 font-medium">${item.topic || 'Krishna Updesh'}</td>
              <td class="py-2.5 px-3 font-mono">${item.duration_mins || 35} Mins</td>
              <td class="py-2.5 px-3 font-mono text-cyan-300 font-bold">${item.elapsed_mins || '3.5'} mins</td>
              <td class="py-2.5 px-3">${ytLink}</td>
            </tr>`;
          });
          tbody.innerHTML = rowsHtml;
        }
      } catch(e) {}
    }

    function escapeHtml(text) {
      return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    async function startColabHyperRun() {
      if (!confirm('⚡ क्या आप 1 घंटे में 10 वीडियो (5 Ch1 + 5 Ch2) का Hyper-Speed प्रोडक्शन शुरू करना चाहते हैं?\nसभी वीडियो सीधे UNLISTED अपलोड होंगे।')) return;
      try {
        const res = await fetch('/api/colab/start', { method: 'POST' });
        const d = await res.json();
        alert('⚡ ' + (d.message || 'Started!'));
        fetchColabStatus();
      } catch(e) { alert('Error: ' + e); }
    }

    async function stopColabHyperRun() {
      if (!confirm('क्या आप 1-Hour Hyper-Run को रोकना चाहते हैं?')) return;
      try {
        const res = await fetch('/api/colab/stop', { method: 'POST' });
        const d = await res.json();
        alert('⏹️ ' + (d.message || 'Stopped'));
        fetchColabStatus();
      } catch(e) { alert('Error: ' + e); }
    }

    async function launchColabInBrowser() {
      try {
        const res = await fetch('/api/colab/launch-browser', { method: 'POST' });
        const d = await res.json();
        alert('🌐 ' + (d.message || 'Google Colab opened in browser!'));
      } catch(e) {
        window.open('https://colab.research.google.com/', '_blank');
      }
    }

    function downloadColabNotebook() {
      window.location.href = '/api/colab/download-notebook';
    }

    // Helper to log directly to the terminal console
    function appendCloudTerminalLog(html) {
      const con = document.getElementById('terminalConsole');
      if (!con) return;
      const d = document.createElement('div');
      d.className = 'font-mono text-xs select-text leading-relaxed';
      d.innerHTML = html;
      con.appendChild(d);
      con.scrollTop = con.scrollHeight;
    }

    // GitHub Actions Cloud Dispatcher Functions
    let lastKnownRunId = null;
    let lastLoggedJobStates = {};

    async function fetchGitHubStatus() {
      try {
        const res = await fetch('/api/github/status');
        const d = await res.json();
        const repoIn = document.getElementById('ghRepoInput');
        if (repoIn && d.repo && !repoIn.value) repoIn.value = d.repo;
        
        const badges = [document.getElementById('ghRunStatusBadge'), document.getElementById('ghRunStatusBadgeMain')];
        const links = [document.getElementById('ghActionLink'), document.getElementById('ghActionLinkMain')];
        const runTexts = [document.getElementById('ghLastRunText'), document.getElementById('ghLastRunTextMain')];
        const grids = [document.getElementById('ghWorkerGrid'), document.getElementById('ghWorkerGridMain')];
        
        const actionUrl = d.repo ? `https://github.com/${d.repo}/actions` : '#';
        links.forEach(l => { if (l) l.href = actionUrl; });
        
        const tele = d.telemetry || {};
        badges.forEach(b => {
          if (!b) return;
          if (tele.status === 'in_progress' || tele.status === 'queued') {
            b.className = 'px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-300 border border-amber-500/40 animate-pulse';
            b.innerText = `⚡ ${tele.status.toUpperCase()} (10 VMS ACTIVE)`;
          } else if (tele.conclusion === 'success') {
            b.className = 'px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/20 text-emerald-300 border border-emerald-500/40';
            b.innerText = '✅ SUCCESS (AUTO-SHUTDOWN)';
          } else if (d.has_token && d.repo) {
            b.className = 'px-2.5 py-0.5 rounded text-[10px] font-bold uppercase bg-indigo-500/20 text-indigo-300 border border-indigo-500/40';
            b.innerText = 'READY TO DISPATCH';
          }
        });

        if (tele.created_at) {
          const runUrl = tele.html_url || actionUrl;
          const runHtml = `<a href="${runUrl}" target="_blank" class="text-cyan-400 hover:underline font-bold flex items-center gap-1.5"><i class="fa-solid fa-arrow-up-right-from-square"></i> Live Run #${tele.run_id}: ${(tele.status || '').toUpperCase()} ${(tele.conclusion ? '(' + tele.conclusion.toUpperCase() + ')' : '')}</a>`;
          runTexts.forEach(rt => { if (rt) rt.innerHTML = runHtml; });

          // Stream worker transitions to terminal console
          if (tele.jobs && tele.jobs.length > 0) {
            tele.jobs.forEach(j => {
              const prev = lastLoggedJobStates[j.name];
              const curr = `${j.status}_${j.conclusion}`;
              if (prev !== curr) {
                lastLoggedJobStates[j.name] = curr;
                if (j.status === 'in_progress' && prev !== curr) {
                  appendCloudTerminalLog(`<span class="text-cyan-400 font-bold">[CLOUD VM ACTIVE]</span> <span class="text-slate-300">${j.name}</span>: Processing render...`);
                } else if (j.conclusion === 'success') {
                  appendCloudTerminalLog(`<span class="text-emerald-400 font-bold">[CLOUD VM DONE]</span> <span class="text-slate-300">${j.name}</span>: Render & Unlisted Upload Complete! Container Shut Down.`);
                } else if (j.conclusion === 'failure') {
                  appendCloudTerminalLog(`<span class="text-rose-400 font-bold">[CLOUD VM NOTICE]</span> <span class="text-slate-300">${j.name}</span>: Finished with warnings.`);
                }
              }
            });
          }
        }

        const jobs = (tele.jobs && tele.jobs.length > 0) ? tele.jobs : [
          {name: 'Worker 1 (Channel 1)', status: tele.status || 'queued'},
          {name: 'Worker 2 (Channel 1)', status: tele.status || 'queued'},
          {name: 'Worker 3 (Channel 1)', status: tele.status || 'queued'},
          {name: 'Worker 4 (Channel 1)', status: tele.status || 'queued'},
          {name: 'Worker 5 (Channel 1)', status: tele.status || 'queued'},
          {name: 'Worker 6 (Channel 2)', status: tele.status || 'queued'},
          {name: 'Worker 7 (Channel 2)', status: tele.status || 'queued'},
          {name: 'Worker 8 (Channel 2)', status: tele.status || 'queued'},
          {name: 'Worker 9 (Channel 2)', status: tele.status || 'queued'},
          {name: 'Worker 10 (Channel 2)', status: tele.status || 'queued'}
        ];

        let gridHtml = '';
        jobs.forEach(j => {
          let stColor = 'text-slate-400 border-slate-700 bg-slate-900/80';
          let icon = '<i class="fa-regular fa-clock text-slate-500"></i>';
          let label = (j.status || 'STANDBY').toUpperCase();
          if (j.status === 'in_progress') {
            stColor = 'text-cyan-300 border-cyan-500/50 bg-cyan-950/70 shadow-lg shadow-cyan-500/20 animate-pulse';
            icon = '<i class="fa-solid fa-gear fa-spin text-cyan-400"></i>';
            label = 'RUNNING';
          } else if (j.conclusion === 'success') {
            stColor = 'text-emerald-300 border-emerald-500/50 bg-emerald-950/70';
            icon = '<i class="fa-solid fa-check text-emerald-400"></i>';
            label = 'DONE';
          } else if (j.conclusion === 'failure') {
            stColor = 'text-rose-300 border-rose-500/50 bg-rose-950/70';
            icon = '<i class="fa-solid fa-xmark text-rose-400"></i>';
            label = 'FAILED';
          }
          gridHtml += `<div class="p-2.5 rounded-xl border ${stColor} text-[11px] font-mono flex items-center justify-between transition-all">
            <span class="truncate font-semibold">${j.name}</span>
            <span class="flex items-center gap-1 font-bold text-[10px]">${icon} ${label}</span>
          </div>`;
        });

        grids.forEach(g => { if (g) g.innerHTML = gridHtml; });
      } catch(e) {}
    }

    async function saveGitHubConfig() {
      const repo = document.getElementById('ghRepoInput').value.trim();
      const token = document.getElementById('ghTokenInput').value.trim();
      if (!repo) { alert('कृपया GitHub Repository (owner/repo) दर्ज करें!'); return; }
      try {
        const res = await fetch('/api/github/config', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({repo, token})
        });
        const d = await res.json();
        alert('✅ ' + (d.message || 'Saved!'));
        fetchGitHubStatus();
      } catch(e) { alert('Error: ' + e); }
    }

    async function dispatchGitHubCloudRun() {
      const btns = [document.getElementById('ghDispatchBtn'), document.getElementById('ghDispatchBtnMain')];
      const oldHtml = btns[0] ? btns[0].innerHTML : '';
      
      btns.forEach(b => {
        if (!b) return;
        b.disabled = true;
        b.className = 'px-6 py-3.5 rounded-xl bg-gradient-to-r from-amber-500 to-yellow-600 text-slate-950 font-black text-xs flex items-center gap-2 shadow-lg shadow-amber-500/25 transition-all whitespace-nowrap animate-pulse';
        b.innerHTML = '<i class="fa-solid fa-gear fa-spin text-sm"></i> ⚡ DISPATCHING TO 10 CLOUD VMS...';
      });

      const runTexts = [document.getElementById('ghLastRunText'), document.getElementById('ghLastRunTextMain')];
      runTexts.forEach(rt => {
        if (rt) rt.innerHTML = '<span class="text-amber-300 font-bold animate-pulse">⚡ Transmitting launch signal to GitHub Actions Cloud...</span>';
      });

      // Immediate visible terminal feedback
      appendCloudTerminalLog('<br/><span class="text-amber-400 font-bold">=================================================================================</span>');
      appendCloudTerminalLog('<span class="text-amber-300 font-bold">🚀 [1-CLICK CLOUD LAUNCH] Transmitting Matrix Signal to GitHub Actions Cloud...</span>');
      appendCloudTerminalLog('<span class="text-slate-300">🛰️ Target Repository: <b>sagarsbl369369-bit/krishna-divine-cinema</b></span>');
      appendCloudTerminalLog('<span class="text-slate-300">⚡ Fleet Size: <b>10 Dedicated Linux Runner VMs (Simultaneous)</b></span>');
      appendCloudTerminalLog('<span class="text-slate-300">🎥 Workers 1–5:  Channel 1 (दिव्य गीता वाणी) [30+ Min Videos, Strictly UNLISTED]</span>');
      appendCloudTerminalLog('<span class="text-slate-300">🎥 Workers 6–10: Channel 2 (परम कृष्ण चेतना) [30+ Min Videos, Strictly UNLISTED]</span>');
      appendCloudTerminalLog('<span class="text-amber-400 font-bold">=================================================================================</span>');

      try {
        const res = await fetch('/api/github/dispatch', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({duration: 35, privacy: 'unlisted'})
        });
        const d = await res.json();
        if (d.success) {
          appendCloudTerminalLog('<span class="text-emerald-400 font-bold">✅ [DISPATCH SUCCESS] 10 Parallel Cloud VMs Queued and Booting on GitHub Actions!</span>');
          appendCloudTerminalLog('<span class="text-cyan-300">🔗 Live Workflow URL: <a href="https://github.com/sagarsbl369369-bit/krishna-divine-cinema/actions" target="_blank" class="underline text-amber-300 font-bold">https://github.com/sagarsbl369369-bit/krishna-divine-cinema/actions</a></span>');

          runTexts.forEach(rt => {
            if (rt) rt.innerHTML = '<span class="text-emerald-400 font-bold">✅ 10 CLOUD WORKERS LAUNCHED! Refreshing telemetry...</span>';
          });

          btns.forEach(b => {
            if (!b) return;
            b.innerHTML = '<i class="fa-solid fa-check text-emerald-300"></i> ✅ 10 CLOUD WORKERS DISPATCHED!';
            b.className = 'px-6 py-3.5 rounded-xl bg-emerald-600/30 border border-emerald-500 text-emerald-300 font-black text-xs flex items-center gap-2';
            setTimeout(() => {
              b.disabled = false;
              b.className = 'px-6 py-3.5 rounded-xl bg-gradient-to-r from-indigo-500 via-purple-600 to-pink-600 hover:from-indigo-400 hover:to-pink-500 text-white font-black text-sm flex items-center gap-2.5 shadow-xl shadow-indigo-500/30 transition-all cursor-pointer whitespace-nowrap active:scale-95';
              b.innerHTML = '<i class="fa-solid fa-rocket text-base"></i> 🚀 DISPATCH 10 CLOUD WORKERS NOW';
            }, 8000);
          });

          fetchGitHubStatus();
          setTimeout(fetchGitHubStatus, 1500);
          setTimeout(fetchGitHubStatus, 3000);
          setTimeout(fetchGitHubStatus, 6000);
        } else {
          appendCloudTerminalLog(`<span class="text-rose-400 font-bold">❌ [DISPATCH FAILED] ${d.error || 'Unknown error'}</span>`);
          alert('⚠️ ' + (d.error || 'Failed to dispatch'));
          btns.forEach(b => {
            if (!b) return;
            b.disabled = false;
            b.innerHTML = oldHtml;
          });
        }
      } catch(e) {
        appendCloudTerminalLog(`<span class="text-rose-400 font-bold">❌ [NETWORK ERROR] ${e}</span>`);
        alert('Error: ' + e);
        btns.forEach(b => {
          if (!b) return;
          b.disabled = false;
          b.innerHTML = oldHtml;
        });
      }
      }
    }

    // Initialize
    fetchStatus();
    checkHumanStatus();
    connectLogStream();
    fetchAutopilotStatus();
    fetchColabStatus();
    fetchGitHubStatus();
    setInterval(fetchStatus, 3000);
    setInterval(fetchAutopilotStatus, 3000);
    setInterval(fetchColabStatus, 2500);
    setInterval(fetchGitHubStatus, 5000);
    setInterval(checkHumanStatus, 10000);
  </script>
</body>
</html>
    """

if __name__ == "__main__":
    print("==================================================================")
    print("🕉️ GITA PRODUCTION STUDIO — MISSION CONTROL DASHBOARD")
    print("==================================================================")
    print("🚀 Starting Web Dashboard at: http://127.0.0.1:8000")
    print("==================================================================")
    uvicorn.run(app, host="127.0.0.1", port=8000)
