import requests

key = '48724139-1fbe7e777966fce52b390343f'
queries = ['chariot', 'temple', 'meditation', 'sunrise mountain', 'warrior sword', 'sacred fire', 'divine light']
for q in queries:
    r = requests.get(f'https://pixabay.com/api/videos/?key={key}&q={q}&video_type=film&per_page=5')
    if r.status_code == 200:
        data = r.json()
        hits = data.get('hits', [])
        print(f"Query: '{q}' -> Hits: {data.get('totalHits', 0)}")
        for h in hits[:2]:
            print(f"   ID: {h['id']}, Tags: {h.get('tags')}, Duration: {h.get('duration')}s")
    else:
        print(f"Query: '{q}' failed: {r.status_code}")
