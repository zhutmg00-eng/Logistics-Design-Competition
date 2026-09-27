# -*- coding: utf-8 -*-
import json

with open('chapter7_platform_frontend/assets/communities_gis.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

result = {}

for cid in ['C01', 'C02', 'C03', 'C04', 'C05']:
    c = data[cid]
    info = c['info']
    nodes = c['demand_nodes']
    facs = c['facilities']
    
    hub = None
    lockers = []
    for fc in facs:
        ftype = fc.get('type')
        fid = fc.get('id', '')
        name = fc.get('name', '')
        lat = fc.get('lat')
        lng = fc.get('lng')
        if '接驳' in name or '枢纽' in name or 'hub' in fid.lower() or ftype == 'hub':
            hub = {'id': fid, 'name': name, 'lat': lat, 'lng': lng}
        else:
            lockers.append({'id': fid, 'name': name, 'lat': lat, 'lng': lng, 'cap': fc.get('capacity', '96格'), 'util': fc.get('utilization', '65%'), 'status': fc.get('status', 'normal')})
    
    if not hub and facs:
        # Pick the first one or specific one as hub
        fc = facs[0]
        hub = {'id': fc.get('id', cid + '-HUB'), 'name': fc.get('name', '社区主接驳站'), 'lat': fc.get('lat'), 'lng': fc.get('lng')}
    
    b_list = []
    for n in nodes:
        b_list.append({
            'id': n['id'],
            'name': n['name'],
            'lat': n['lat'],
            'lng': n['lng'],
            'households': n.get('households', 100),
            'daily': n.get('daily_pkgs', 60),
            'time': n.get('time_window', '08:00—21:00')
        })
        
    result[cid] = {
        'id': cid,
        'name': info.get('name'),
        'street': info.get('street'),
        'address': info.get('address'),
        'center': info.get('center'),
        'polygon': info.get('polygon', []),
        'hub': hub,
        'buildings': b_list,
        'lockers': lockers
    }

print("Processed all 5 communities successfully:")
for cid, c in result.items():
    print(f"{cid} {c['name']}: {len(c['buildings'])} buildings, {len(c['lockers'])} lockers, hub={c['hub']['name'] if c['hub'] else 'None'}")

with open('chapter7_platform_frontend/assets/all_communities_summary.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
