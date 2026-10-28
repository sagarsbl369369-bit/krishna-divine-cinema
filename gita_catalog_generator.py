import os
import sys
import json

TARGET_BASE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "geeta wala")

def generate_catalog():
    if not os.path.exists(TARGET_BASE_DIR):
        return

    items_ch1 = []
    items_ch2 = []

    for ch_folder, item_list in [
        ("Channel_01_GeetaGyan60Sec", items_ch1),
        ("Channel_02_GeetaJeevanSutra", items_ch2)
    ]:
        p = os.path.join(TARGET_BASE_DIR, ch_folder)
        if not os.path.exists(p):
            continue
        for sub in sorted(os.listdir(p)):
            sub_p = os.path.join(p, sub)
            if not os.path.isdir(sub_p):
                continue
            mp4_p = os.path.join(sub_p, "master_1080p_documentary.mp4")
            thumb_p = os.path.join(sub_p, "thumbnail_uhd.jpg")
            seo_p = os.path.join(sub_p, "seo_package.json")

            title = sub.replace("_", " ")
            desc = ""
            tags = []
            if os.path.exists(seo_p):
                try:
                    with open(seo_p, "r", encoding="utf-8") as sf:
                        s_data = json.load(sf)
                        title = s_data.get("title", title)
                        desc = s_data.get("description", "")
                        tags = s_data.get("tags", [])
                except Exception:
                    pass

            size_mb = os.path.getsize(mp4_p) / (1024 * 1024) if os.path.exists(mp4_p) else 0

            # relative path for web
            rel_thumb = os.path.relpath(thumb_p, TARGET_BASE_DIR).replace("\\", "/") if os.path.exists(thumb_p) else ""
            rel_mp4 = os.path.relpath(mp4_p, TARGET_BASE_DIR).replace("\\", "/") if os.path.exists(mp4_p) else ""

            item_list.append({
                "folder": sub,
                "title": title,
                "desc": desc,
                "tags": tags,
                "size_mb": f"{size_mb:.1f} MB",
                "has_video": os.path.exists(mp4_p),
                "thumb_src": rel_thumb,
                "video_src": rel_mp4
            })

    def render_cards(items):
        cards = []
        for it in items:
            tag_badges = "".join([f'<span class="badge">#{t}</span>' for t in it["tags"][:4]])
            thumb_tag = f'<img src="{it["thumb_src"]}" alt="Thumbnail" />' if it["thumb_src"] else '<div class="no-thumb">🖼️ No Thumbnail</div>'
            cards.append(f"""
            <div class="card">
                <div class="thumb-container">
                    {thumb_tag}
                    <span class="size-pill">{it["size_mb"]}</span>
                </div>
                <div class="card-body">
                    <h3 class="title">{it["title"]}</h3>
                    <p class="desc">{it["desc"][:160]}...</p>
                    <div class="tags-container">{tag_badges}</div>
                    <div class="actions">
                        <a href="{it["video_src"]}" class="btn-play" target="_blank">▶ Play Master Video</a>
                    </div>
                </div>
            </div>
            """)
        return "\n".join(cards)

    html_content = f"""<!DOCTYPE html>
<html lang="hi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🕉️ Gita Production Studio — Master Video Vault</title>
    <style>
        :root {{
            --bg-primary: #0a0e17;
            --bg-secondary: #131c2e;
            --accent-gold: #f59e0b;
            --accent-cyan: #06b6d4;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --card-bg: #1e293b;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: var(--bg-primary);
            color: var(--text-main);
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            padding: 2rem;
            line-height: 1.6;
        }}
        .header {{
            text-align: center;
            margin-bottom: 2.5rem;
            padding: 2rem;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(6, 182, 212, 0.1));
            border-radius: 16px;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}
        .header h1 {{
            font-size: 2.2rem;
            background: linear-gradient(to right, #fbbf24, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        .header p {{ color: var(--text-muted); font-size: 1.05rem; }}
        .channel-section {{
            margin-bottom: 3rem;
        }}
        .channel-title {{
            font-size: 1.5rem;
            color: var(--accent-gold);
            margin-bottom: 1.2rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            border-bottom: 2px solid rgba(245, 158, 11, 0.3);
            padding-bottom: 0.5rem;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.5rem;
        }}
        .card {{
            background: var(--card-bg);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.08);
            transition: transform 0.2s, box-shadow 0.2s;
            display: flex;
            flex-direction: column;
        }}
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.4);
            border-color: rgba(245, 158, 11, 0.4);
        }}
        .thumb-container {{
            position: relative;
            aspect-ratio: 16 / 9;
            background: #0f172a;
        }}
        .thumb-container img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}
        .size-pill {{
            position: absolute;
            bottom: 8px;
            right: 8px;
            background: rgba(0, 0, 0, 0.75);
            color: #fbbf24;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: bold;
        }}
        .card-body {{
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            flex-grow: 1;
        }}
        .title {{
            font-size: 1.05rem;
            font-weight: 600;
            margin-bottom: 0.6rem;
            color: #f1f5f9;
        }}
        .desc {{
            font-size: 0.85rem;
            color: var(--text-muted);
            margin-bottom: 1rem;
            flex-grow: 1;
        }}
        .tags-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-bottom: 1rem;
        }}
        .badge {{
            background: rgba(6, 182, 212, 0.15);
            color: var(--accent-cyan);
            font-size: 0.7rem;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }}
        .btn-play {{
            display: inline-block;
            width: 100%;
            text-align: center;
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: #000;
            font-weight: bold;
            padding: 0.6rem;
            border-radius: 6px;
            text-decoration: none;
            transition: opacity 0.2s;
        }}
        .btn-play:hover {{ opacity: 0.9; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🕉️ GITA PRODUCTION STUDIO</h1>
        <p>10 Master Documentary Packages (1080p + 173.25s Blue Laser Outro + UHD Thumbnails + SEO)</p>
    </div>

    <div class="channel-section">
        <h2 class="channel-title">🎬 Channel 1: Geeta Gyan 60 Sec (@GeetaGyan60Sec) — 5 Master Videos</h2>
        <div class="grid">
            {render_cards(items_ch1)}
        </div>
    </div>

    <div class="channel-section">
        <h2 class="channel-title">🎬 Channel 2: Geeta Jeevan Sutra (@GeetaJeevanSutraHindi) — 5 Master Videos</h2>
        <div class="grid">
            {render_cards(items_ch2)}
        </div>
    </div>
</body>
</html>
"""
    out_html = os.path.join(TARGET_BASE_DIR, "catalog.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✓ Generated offline visual catalog: {out_html}")

if __name__ == "__main__":
    generate_catalog()
