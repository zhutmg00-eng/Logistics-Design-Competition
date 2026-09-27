import json

with open('chapter7_platform_frontend/assets/communities_gis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for cid, cinfo in data.items():
    info = cinfo.get('info', {})
    dnodes = cinfo.get('demand_nodes', [])
    facilities = cinfo.get('facilities', [])
    roads = cinfo.get('roads', [])
    name = info.get('name')
    center = info.get('center')
    print(f"{cid}: {name} | Nodes: {len(dnodes)} | Facilities: {len(facilities)} | Roads: {len(roads)} | Center: {center}")
