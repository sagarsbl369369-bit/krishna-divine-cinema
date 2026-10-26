import requests

key = "48724139-1fbe7e777966fce52b390343f"
test_queries = [
    "warrior ancient",
    "chariot horses",
    "hindu temple",
    "sacred fire",
    "meditation mountain",
    "divine rays sun",
    "lotus flower",
    "ancient temple"
]

for q in test_queries:
    r = requests.get(f"https://pixabay.com/api/videos/?key={key}&q={q}&video_type=all&per_page=5")
    if r.status_code == 200:
        hits = r.json().get("hits", [])
        print(f"=== Query: '{q}' ({len(hits)} hits) ===")
        for h in hits[:2]:
            print(f"   ID: {h['id']}, Tags: {h.get('tags')}")
            med_url = h["videos"].get("medium", {}).get("url", "")
            print(f"   URL: {med_url[:70]}...")
    else:
        print(f"Error for {q}: {r.status_code}")
