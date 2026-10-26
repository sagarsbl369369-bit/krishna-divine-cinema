import requests

key = "48724139-1fbe7e777966fce52b390343f"
queries = [
    "war battle smoke",
    "dark storm lightning clouds",
    "burning fire",
    "golden temple india",
    "incense smoke prayer",
    "sunset meditation silhouette"
]

for q in queries:
    r = requests.get(f"https://pixabay.com/api/videos/?key={key}&q={q}&video_type=all&per_page=5")
    if r.status_code == 200:
        hits = r.json().get("hits", [])
        print(f"=== Query: '{q}' ({len(hits)} hits) ===")
        for h in hits[:2]:
            print(f"   ID: {h['id']}, Tags: {h.get('tags')}")
