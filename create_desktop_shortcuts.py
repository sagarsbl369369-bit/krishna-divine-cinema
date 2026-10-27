import os
import subprocess

desktop_dirs = [
    os.path.join(os.environ['USERPROFILE'], 'OneDrive', 'Desktop'),
    os.path.join(os.environ['USERPROFILE'], 'Desktop'),
]

engine_dir = r"C:\Users\janar\.gemini\antigravity\scratch\geeta_automation_engine"
renders_dir = os.path.join(engine_dir, "renders")

vbs_script_path = os.path.join(engine_dir, "create_shortcuts.vbs")

shortcuts = [
    {
        "name": "🎬 ALL RENDERED VIDEOS.lnk",
        "target": "explorer.exe",
        "args": f'"{renders_dir}"',
        "workdir": renders_dir,
        "desc": "Open Krishna Divine Cinema Renders Folder"
    },
    {
        "name": "🔑 1_CLICK_CONNECT_YOUTUBE_TO_CLOUD.lnk",
        "target": os.path.join(engine_dir, "1_CLICK_CONNECT_YOUTUBE_TO_CLOUD.bat"),
        "args": "",
        "workdir": engine_dir,
        "desc": "Authorize YouTube for GitHub Cloud Autonomy"
    },
    {
        "name": "🚀 1_CLICK_TRIGGER_10_VIDEOS_CLOUD.lnk",
        "target": os.path.join(engine_dir, "1_CLICK_GITHUB_DISPATCH.bat"),
        "args": "",
        "workdir": engine_dir,
        "desc": "Trigger 10 Video Generation on GitHub Cloud"
    }
]

with open(vbs_script_path, "w", encoding="utf-8") as f:
    f.write('Set oWS = WScript.CreateObject("WScript.Shell")\n')
    for d in desktop_dirs:
        if os.path.exists(d):
            # Also copy bat files directly
            for s in shortcuts:
                lnk_path = os.path.join(d, s["name"]).replace("\\", "\\\\")
                target = s["target"].replace("\\", "\\\\")
                args = s["args"].replace('"', '""')
                workdir = s["workdir"].replace("\\", "\\\\")
                desc = s["desc"]
                f.write(f'Set oLink = oWS.CreateShortcut("{lnk_path}")\n')
                f.write(f'oLink.TargetPath = "{target}"\n')
                if args:
                    f.write(f'oLink.Arguments = "{args}"\n')
                f.write(f'oLink.WorkingDirectory = "{workdir}"\n')
                f.write(f'oLink.Description = "{desc}"\n')
                f.write('oLink.Save\n')

subprocess.run(["cscript", "//Nologo", vbs_script_path], check=True)
print("Shortcuts created successfully!")
