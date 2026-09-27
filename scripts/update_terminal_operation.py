# -*- coding: utf-8 -*-
import json
import os

# Load extracted communities summary
with open('chapter7_platform_frontend/assets/all_communities_summary.json', 'r', encoding='utf-8') as f:
    comm_data = json.load(f)

# Enhance C04 with detailed operational routes, blockage, detour, vehicles, couriers
comm_data['C04']['roads'] = [
    [[39.7626874, 116.5063436], [39.76185, 116.50435]],
    [[39.7634032, 116.5036026], [39.76185, 116.50435]],
    [[39.76185, 116.50435], [39.76065, 116.5042]],
    [[39.76185, 116.50435], [39.7612, 116.5026]],
    [[39.7629409, 116.5035636], [39.7634032, 116.5036026]],
    [[39.7626409, 116.5045614], [39.76185, 116.50435]],
    [[39.762507, 116.5058885], [39.7626874, 116.5063436]],
    [[39.7624745, 116.5052605], [39.7626874, 116.5063436]],
    [[39.7623759, 116.5030145], [39.7634032, 116.5036026]],
    [[39.7620254, 116.5056648], [39.7626874, 116.5063436]],
    [[39.7619434, 116.5035326], [39.76185, 116.50435]],
    [[39.7618585, 116.5045629], [39.76185, 116.50435]],
    [[39.7614241, 116.504142], [39.76185, 116.50435]],
    [[39.7610251, 116.5047081], [39.76065, 116.5042]],
    [[39.7607256, 116.5042844], [39.76065, 116.5042]],
    [[39.7606746, 116.5051148], [39.76065, 116.5042]]
]

comm_data['C04']['activeRoute'] = [
    [39.76265, 116.5062],      # Hub A-01
    [39.762507, 116.5058885],  # D03 (120件)
    [39.7624745, 116.5052605],  # D04 (45件)
    [39.7618585, 116.5045629],  # Detour via D08
    [39.7620254, 116.5056648],  # D06 (146件)
    [39.7623759, 116.5030145],  # D05 (85件人车交接)
    [39.7629409, 116.5035636],  # D01 (投递)
    [39.76265, 116.5062]       # Return Hub
]

comm_data['C04']['blockedRoad'] = [
    [39.7624745, 116.5052605],  # D04
    [39.7620254, 116.5056648]   # D06 direct
]

comm_data['C04']['detourRoad'] = [
    [39.7624745, 116.5052605],  # D04
    [39.7618585, 116.5045629],  # D08
    [39.7620254, 116.5056648]   # D06
]

comm_data['C04']['ugvs'] = [
    {
        'id': 'C04-V1',
        'name': 'C04-V1 (载重800kg/基准450件)',
        'lat': 39.76215,
        'lng': 116.50385,
        'load': '396件 (94.2%)',
        'batch': 'C04-R2',
        'status': '执行 C04-R2 批次中 · 趋向 D05 交接点',
        'soc': '78%'
    },
    {
        'id': 'C04-V2',
        'name': 'C04-V2 (载重800kg)',
        'lat': 39.76280,
        'lng': 116.50410,
        'load': '210件',
        'batch': 'C04-R1',
        'status': 'D01-D02 投柜派送中',
        'soc': '64%'
    }
]

comm_data['C04']['couriers'] = [
    {
        'id': 'C-0407',
        'name': '配送员 张伟 (工号C-0407)',
        'lat': 39.76240,
        'lng': 116.50260,
        'task': '在 D05 专用泊位等待 C04-V1 交接 (85件上门预约件)',
        'status': '就位等待中 (预计3分钟后到达)'
    },
    {
        'id': 'C-0412',
        'name': '配送员 李强 (工号C-0412)',
        'lat': 39.76265,
        'lng': 116.50480,
        'task': 'D02 单元开展入户交付 (预约件)',
        'status': '上门作业中'
    }
]

# Set specific locker details for C04 to match project documentation
comm_data['C04']['lockers'] = [
    { 'id': 'S01', 'name': 'S01 柜 (1-2号楼北)', 'lat': 39.76280, 'lng': 116.50330, 'cap': '104格', 'util': '68%', 'status': 'normal' },
    { 'id': 'S02', 'name': 'S02 柜 (3-4号楼中心)', 'lat': 39.76245, 'lng': 116.50410, 'cap': '104格', 'util': '74%', 'status': 'normal' },
    { 'id': 'S03', 'name': 'S03 柜 (5-6号楼南·高负荷)', 'lat': 39.76210, 'lng': 116.50570, 'cap': '104格', 'util': '92%', 'status': 'warn' },
    { 'id': 'S04', 'name': 'S04 柜 (7-8号楼东)', 'lat': 39.76235, 'lng': 116.50530, 'cap': '104格', 'util': '55%', 'status': 'normal' }
]
comm_data['C04']['hub'] = {
    'id': 'C04-HUB',
    'name': '中央接驳站 A-01 (入口级枢纽)',
    'lat': 39.76265,
    'lng': 116.5062
}

# Ensure building names are crisp
for b in comm_data['C04']['buildings']:
    b_id = b['id'].replace('C04-', '')
    b['short_name'] = f"{b_id} ({b['name'].split('（')[0].replace('住宅建筑簇', '')}号楼)"

comm_json_str = json.dumps(comm_data, ensure_ascii=False)

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>多模型驱动的社区末端共同配送运营管理中心 · 数字孪生驾驶舱 (Chapter 7.3.1)</title>
  
  <!-- Leaflet GIS Map Assets -->
  <link rel="stylesheet" href="assets/leaflet.css" />
  <script src="assets/leaflet.js"></script>

  <style>
    :root {{
      /* OpenDesign Professional Engineering Dark Palette */
      --bg-base: #090d16;
      --bg-surface: #101623;
      --bg-card: #151e30;
      --bg-card-hover: #1c273d;
      --bg-glass: rgba(16, 22, 35, 0.92);
      
      /* Crisp 1px Borders */
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-strong: rgba(255, 255, 255, 0.16);
      --border-accent: rgba(56, 189, 248, 0.35);
      
      /* Functional Semantic Colors (Restrained, No Neon Glow) */
      --sky: #0284c7;
      --sky-light: #38bdf8;
      --cyan: #06b6d4;
      --emerald: #10b981;
      --emerald-light: #34d399;
      --amber: #f59e0b;
      --amber-light: #fbbf24;
      --rose: #f43f5e;
      --rose-light: #fb7185;
      --indigo: #6366f1;
      --purple: #8b5cf6;
      
      /* High-Contrast Typography */
      --text-main: #f8fafc;
      --text-secondary: #cbd5e1;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
    }}

    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
      font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      -webkit-font-smoothing: antialiased;
    }}

    body {{
      background-color: var(--bg-base);
      color: var(--text-main);
      width: 1920px;
      height: 1080px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      background-image: 
        radial-gradient(circle at 50% -20%, rgba(30, 41, 59, 0.45) 0%, transparent 70%),
        radial-gradient(circle at 10% 100%, rgba(15, 23, 42, 0.6) 0%, transparent 50%);
    }}

    /* Tabular numbers for all stats */
    .tnum {{
      font-variant-numeric: tabular-nums;
      font-feature-settings: "tnum";
    }}

    /* Top Executive Header */
    header {{
      height: 62px;
      background: var(--bg-surface);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      position: relative;
      z-index: 1000;
    }}
    
    .header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .logo-badge {{
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, #1e293b, #0f172a);
      border: 1px solid var(--border-accent);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }}
    .title-group h1 {{
      font-size: 17px;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .title-group p {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .header-center {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .status-pill {{
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 11px;
      color: var(--emerald-light);
    }}
    .pulse-dot {{
      width: 7px;
      height: 7px;
      background: var(--emerald);
      border-radius: 50%;
      animation: pulse 2s infinite ease-in-out;
    }}
    @keyframes pulse {{
      0%, 100% {{ opacity: 1; transform: scale(1); }}
      50% {{ opacity: 0.35; transform: scale(0.85); }}
    }}

    .mode-pill {{
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(2, 132, 199, 0.1);
      border: 1px solid rgba(2, 132, 199, 0.25);
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 11px;
      color: var(--sky-light);
    }}

    .header-right {{
      display: flex;
      align-items: center;
      gap: 18px;
      font-size: 12px;
      color: var(--text-muted);
    }}
    .header-right .clock {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      color: var(--sky-light);
      font-size: 14px;
      font-weight: 600;
      background: rgba(15, 23, 42, 0.6);
      padding: 4px 10px;
      border-radius: 6px;
      border: 1px solid var(--border-subtle);
    }}

    /* Top Metrics Ribbon */
    .top-metrics {{
      display: grid;
      grid-template-columns: repeat(8, 1fr);
      gap: 10px;
      padding: 10px 24px;
    }}
    .metric-card {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      padding: 9px 12px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      position: relative;
      transition: border-color 0.2s;
    }}
    .metric-card:hover {{
      border-color: var(--border-strong);
    }}
    .metric-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      width: 3px;
      height: 100%;
      background: var(--sky);
      border-top-left-radius: 8px;
      border-bottom-left-radius: 8px;
    }}
    .metric-card.success::before {{ background: var(--emerald); }}
    .metric-card.warn::before {{ background: var(--amber); }}
    .metric-card.alert::before {{ background: var(--rose); }}
    .metric-card.purple::before {{ background: var(--purple); }}

    .metric-title {{
      font-size: 11px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .metric-title span {{
      font-size: 9px;
      color: var(--text-dim);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }}
    .metric-val {{
      font-size: 20px;
      font-weight: 700;
      color: var(--text-main);
      margin: 4px 0 2px 0;
      display: flex;
      align-items: baseline;
      gap: 4px;
    }}
    .metric-val span {{
      font-size: 11px;
      font-weight: normal;
      color: var(--text-muted);
    }}
    .metric-sub {{
      font-size: 10px;
      color: var(--emerald-light);
    }}
    .metric-sub.warn {{ color: var(--amber-light); }}
    .metric-sub.alert {{ color: var(--rose-light); }}

    /* Main Grid Layout */
    .main-body {{
      flex: 1;
      display: grid;
      grid-template-columns: 410px 1fr 420px;
      gap: 12px;
      padding: 0 24px 12px 24px;
      overflow: hidden;
    }}

    /* Panels */
    .panel {{
      background: var(--bg-surface);
      border: 1px solid var(--border-subtle);
      border-radius: 10px;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.35);
    }}
    .panel-header {{
      padding: 9px 14px;
      background: rgba(21, 30, 48, 0.75);
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .panel-title {{
      font-size: 13px;
      font-weight: 600;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .panel-title-badge {{
      width: 3px;
      height: 12px;
      background: var(--sky-light);
      border-radius: 1.5px;
    }}
    .panel-content {{
      padding: 10px;
      flex: 1;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
      justify-content: space-between;
    }}

    /* Model Chain Stack */
    .model-chain-box {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 9px;
    }}
    .model-step {{
      display: flex;
      align-items: flex-start;
      gap: 8px;
      position: relative;
      padding-bottom: 6px;
    }}
    .model-step:not(:last-child)::after {{
      content: '';
      position: absolute;
      left: 10px;
      top: 20px;
      width: 1px;
      height: calc(100% - 10px);
      background: var(--border-subtle);
    }}
    .step-idx {{
      width: 20px;
      height: 20px;
      border-radius: 4px;
      background: rgba(2, 132, 199, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.3);
      color: var(--sky-light);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 10px;
      font-weight: 700;
      flex-shrink: 0;
      z-index: 1;
    }}
    .step-info h4 {{
      font-size: 11px;
      color: var(--text-main);
      font-weight: 600;
    }}
    .step-info p {{
      font-size: 10px;
      color: var(--text-muted);
      line-height: 1.35;
      margin-top: 1px;
    }}

    /* Batch Card */
    .batch-highlight-card {{
      background: var(--bg-card);
      border: 1px solid var(--border-accent);
      border-radius: 6px;
      padding: 9px;
      position: relative;
    }}
    .batch-tag {{
      position: absolute;
      top: 8px;
      right: 9px;
      background: rgba(2, 132, 199, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: var(--sky-light);
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 10px;
      font-weight: 600;
    }}
    .batch-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 5px;
      margin-top: 6px;
    }}
    .batch-item {{
      background: rgba(10, 14, 23, 0.6);
      padding: 5px 7px;
      border-radius: 4px;
      border: 1px solid var(--border-subtle);
    }}
    .batch-item-label {{
      font-size: 9px;
      color: var(--text-muted);
    }}
    .batch-item-value {{
      font-size: 12px;
      font-weight: 600;
      color: var(--text-main);
      margin-top: 1px;
    }}

    /* Center GIS Map Container */
    .gis-container {{
      display: flex;
      flex-direction: column;
      position: relative;
      background: #080c14;
    }}
    .gis-map-wrapper {{
      flex: 1;
      position: relative;
      overflow: hidden;
      background: #080c14;
    }}
    #leafletMap {{
      width: 100%;
      height: 100%;
      z-index: 1;
      background: #080c14;
    }}

    /* Engineering Blueprint Background Grid (Visible Offline or Under Tiles) */
    .gis-map-wrapper::before {{
      content: '';
      position: absolute;
      inset: 0;
      background-image: 
        linear-gradient(rgba(30, 41, 59, 0.25) 1px, transparent 1px),
        linear-gradient(90deg, rgba(30, 41, 59, 0.25) 1px, transparent 1px),
        linear-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56, 189, 248, 0.05) 1px, transparent 1px);
      background-size: 100px 100px, 100px 100px, 20px 20px, 20px 20px;
      background-position: -1px -1px;
      pointer-events: none;
      z-index: 0;
    }}

    /* AutoNavi & OSM High-End Dark Tiles Filters (Subdued, Authentic GIS) */
    .amap-dark-tiles .leaflet-tile {{
      filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(92%) saturate(60%);
      -webkit-filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(92%) saturate(60%);
    }}
    .osm-dark-tiles .leaflet-tile {{
      filter: invert(100%) hue-rotate(180deg) brightness(80%) contrast(95%) saturate(55%);
      -webkit-filter: invert(100%) hue-rotate(180deg) brightness(80%) contrast(95%) saturate(55%);
    }}

    /* Top HUD in Map */
    .gis-top-hud {{
      position: absolute;
      top: 10px;
      left: 12px;
      right: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 500;
      pointer-events: none;
    }}
    .gis-hud-left, .gis-hud-right {{
      display: flex;
      gap: 6px;
      pointer-events: auto;
    }}
    .gis-chip {{
      background: rgba(16, 22, 35, 0.92);
      border: 1px solid var(--border-subtle);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 11px;
      display: flex;
      align-items: center;
      gap: 6px;
      color: var(--text-secondary);
      backdrop-filter: blur(8px);
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    .gis-chip .dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }}
    .gis-chip.alert {{
      background: rgba(244, 63, 94, 0.12);
      border-color: rgba(244, 63, 94, 0.3);
      color: var(--rose-light);
    }}

    /* Community Selector */
    .community-select-btn {{
      background: rgba(16, 22, 35, 0.95);
      border: 1px solid var(--border-accent);
      color: var(--sky-light);
      padding: 3px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      backdrop-filter: blur(8px);
    }}
    .community-select-btn select {{
      background: transparent;
      border: none;
      color: var(--sky-light);
      font-size: 11px;
      font-weight: 600;
      outline: none;
      cursor: pointer;
    }}
    .community-select-btn select option {{
      background: #101623;
      color: #fff;
    }}

    /* Layer Toggle Group */
    .gis-layer-toggles {{
      display: flex;
      gap: 4px;
      background: rgba(16, 22, 35, 0.92);
      border: 1px solid var(--border-subtle);
      padding: 3px;
      border-radius: 6px;
      backdrop-filter: blur(8px);
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }}
    .layer-btn {{
      background: transparent;
      border: 1px solid transparent;
      color: var(--text-muted);
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 10px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 4px;
      transition: all 0.15s;
    }}
    .layer-btn.active {{
      background: rgba(2, 132, 199, 0.2);
      border-color: rgba(56, 189, 248, 0.3);
      color: var(--sky-light);
    }}
    .layer-btn:hover:not(.active) {{
      background: rgba(255, 255, 255, 0.05);
      color: var(--text-secondary);
    }}

    /* GIS Legend */
    .gis-legend {{
      position: absolute;
      bottom: 10px;
      right: 12px;
      background: rgba(16, 22, 35, 0.94);
      border: 1px solid var(--border-subtle);
      padding: 8px 12px;
      border-radius: 6px;
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 10px;
      z-index: 500;
      backdrop-filter: blur(8px);
      box-shadow: 0 2px 10px rgba(0,0,0,0.4);
    }}
    .legend-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--text-secondary);
    }}
    .legend-color {{
      width: 12px;
      height: 4px;
      border-radius: 1px;
    }}

    /* Center Bottom KPI */
    .center-bottom {{
      height: 116px;
      background: rgba(16, 22, 35, 0.95);
      border-top: 1px solid var(--border-subtle);
      padding: 8px 12px;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
    }}
    .kpi-box {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 6px;
      padding: 7px 10px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}
    .kpi-title {{
      font-size: 10px;
      color: var(--text-muted);
    }}
    .kpi-num {{
      font-size: 17px;
      font-weight: 700;
      color: var(--sky-light);
    }}
    .kpi-desc {{
      font-size: 9px;
      color: var(--text-muted);
    }}

    /* Right Panel: Gantt & Resources */
    .gantt-item {{
      background: var(--bg-card);
      border-radius: 6px;
      padding: 6px 8px;
      border: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}
    .gantt-header {{
      display: flex;
      justify-content: space-between;
      font-size: 10px;
    }}
    .gantt-bar-bg {{
      height: 5px;
      background: rgba(255, 255, 255, 0.06);
      border-radius: 3px;
      overflow: hidden;
    }}
    .gantt-bar-fill {{
      height: 100%;
      border-radius: 3px;
      background: linear-gradient(90deg, var(--sky), var(--emerald));
    }}

    .res-list {{
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}
    .res-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: var(--bg-card);
      padding: 5px 8px;
      border-radius: 4px;
      font-size: 11px;
      border: 1px solid var(--border-subtle);
    }}

    /* Custom Leaflet Marker Styling (Clean OpenDesign) */
    .custom-marker {{
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: transform 0.15s;
    }}
    .custom-marker:hover {{
      transform: scale(1.12);
      z-index: 1000 !important;
    }}
    
    .ugv-marker-container {{
      position: relative;
    }}
    .ugv-pulse {{
      position: absolute;
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: rgba(56, 189, 248, 0.2);
      border: 1px solid rgba(56, 189, 248, 0.6);
      top: -6px;
      left: -6px;
      animation: ugvPulse 2s infinite ease-out;
      pointer-events: none;
    }}
    @keyframes ugvPulse {{
      0% {{ transform: scale(0.6); opacity: 1; }}
      100% {{ transform: scale(1.6); opacity: 0; }}
    }}
    
    .marker-label-badge {{
      background: rgba(15, 23, 42, 0.92);
      border: 1px solid var(--border-strong);
      color: #fff;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 10px;
      white-space: nowrap;
      pointer-events: none;
      box-shadow: 0 2px 6px rgba(0,0,0,0.4);
    }}

    /* Custom Tooltip Styling */
    .leaflet-popup-content-wrapper {{
      background: rgba(16, 22, 35, 0.96) !important;
      border: 1px solid var(--border-strong) !important;
      border-radius: 8px !important;
      color: var(--text-main) !important;
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5) !important;
      padding: 0 !important;
    }}
    .leaflet-popup-tip {{
      background: rgba(16, 22, 35, 0.96) !important;
      border: 1px solid var(--border-strong) !important;
    }}
    .popup-inner {{
      padding: 8px 12px;
      font-size: 11px;
    }}
    .popup-title {{
      font-weight: 700;
      color: var(--sky-light);
      margin-bottom: 4px;
      font-size: 12px;
      border-bottom: 1px solid var(--border-subtle);
      padding-bottom: 3px;
    }}
    .popup-row {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      color: var(--text-secondary);
      margin: 2px 0;
    }}
    .popup-row strong {{
      color: var(--text-main);
    }}
  </style>
</head>
<body>

  <!-- Top Executive Header -->
  <header>
    <div class="header-left">
      <div class="logo-badge">🖥️</div>
      <div class="title-group">
        <h1>多模型驱动的社区末端共同配送运营管理中心 · 数字孪生驾驶舱</h1>
        <p>Multi-Model Driven Community Last-Mile Co-Delivery Operation & Decision Cockpit (Chapter 7.3.1)</p>
      </div>
    </div>
    
    <div class="header-center">
      <div class="status-pill">
        <div class="pulse-dot"></div>
        <span>系统运行正常 · 滚动调度中 (第4轮批次)</span>
      </div>
      <div class="mode-pill">
        <span style="font-weight:600; color:var(--text-muted);">决策模式:</span> 两阶段字典序优化人机协同模式 (2E-MDVRPTW-DC)
      </div>
    </div>

    <div class="header-right">
      <span>试点社区：<strong id="headerCommunityName" style="color:var(--text-main);">北京经开区·亦城茗苑示范区 (C04)</strong></span>
      <span>服务网点：<strong id="headerHubName" style="color:var(--text-main);">中央接驳站 A-01 (入口级枢纽)</strong></span>
      <div class="clock tnum" id="liveClock">15:42:19</div>
    </div>
  </header>

  <!-- Top Metrics Ribbon (Chapter 7.3.1) -->
  <div class="top-metrics">
    <div class="metric-card">
      <div class="metric-title">今日总订单量 <span>Total Orders</span></div>
      <div class="metric-val tnum">2,840 <span>件</span></div>
      <div class="metric-sub">▲ 18.5% 较昨日同期</div>
    </div>
    <div class="metric-card success">
      <div class="metric-title">已完成交付 <span>Completed</span></div>
      <div class="metric-val tnum">1,986 <span>件</span></div>
      <div class="metric-sub">履约进度 69.9%</div>
    </div>
    <div class="metric-card purple">
      <div class="metric-title">待组批任务池 <span>Task Pool</span></div>
      <div class="metric-val tnum">248 <span>件</span></div>
      <div class="metric-sub">平均等待 14.2 min</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">正在执行批次 <span>Active Batches</span></div>
      <div class="metric-val tnum">8 <span>组</span></div>
      <div class="metric-sub">覆盖8个重点服务节点</div>
    </div>
    <div class="metric-card success">
      <div class="metric-title">无人配送车运力 <span>UGV Fleet</span></div>
      <div class="metric-val tnum">12/15 <span>台在勤</span></div>
      <div class="metric-sub">平均电量 78% (健康)</div>
    </div>
    <div class="metric-card">
      <div class="metric-title">在岗人工配送员 <span>Couriers</span></div>
      <div class="metric-val tnum">18 <span>人</span></div>
      <div class="metric-sub">人车交接准时率 98.2%</div>
    </div>
    <div class="metric-card warn">
      <div class="metric-title">智能柜综合占用 <span>Lockers</span></div>
      <div class="metric-val tnum">76.5 <span>%</span></div>
      <div class="metric-sub warn">S03号柜负荷超 92% 预警</div>
    </div>
    <div class="metric-card alert">
      <div class="metric-title">跨主体异常事件 <span>Alerts</span></div>
      <div class="metric-val tnum">1 <span>起</span></div>
      <div class="metric-sub alert">D04路段施工·已重规划绕行</div>
    </div>
  </div>

  <!-- Main Body Grid -->
  <div class="main-body">

    <!-- Left Panel: Multi-Model Cascade & Task Pool Engine -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">
          <div class="panel-title-badge"></div>
          多模型协同驱动引擎与任务池
        </div>
        <span style="font-size:11px; color:var(--sky-light); font-family:monospace;">Cascade v2.4</span>
      </div>
      
      <div class="panel-content">
        <!-- 7.2.1 Multi-Model Calling Relationship -->
        <div class="model-chain-box">
          <div style="font-size: 11px; font-weight:600; color: var(--text-secondary); margin-bottom: 7px; display:flex; justify-content:space-between; align-items:center;">
            <span>五层级模型连续协同调用链</span>
            <span style="color:var(--emerald-light); font-size:10px;">● 实时在线计算</span>
          </div>

          <div class="model-step">
            <div class="step-idx">M1</div>
            <div class="step-info">
              <h4>需求估计与情景模拟模型 (第5章)</h4>
              <p>贝叶斯多尺度时空负荷分解 · 今日峰值 320件/h</p>
            </div>
          </div>

          <div class="model-step">
            <div class="step-idx">M2</div>
            <div class="step-info">
              <h4>末端配送网络规划模型 (第4章)</h4>
              <p>P-中值选址 · 匹配住宅节点 D01-D12 与设施 S01-S04</p>
            </div>
          </div>

          <div class="model-step">
            <div class="step-idx">M3</div>
            <div class="step-info">
              <h4>无人配送与人工协同调度模型 (第7章)</h4>
              <p>两阶段字典序 CVRP 组批 · 车辆路线与人车强同步计划</p>
            </div>
          </div>

          <div class="model-step">
            <div class="step-idx">M4</div>
            <div class="step-info">
              <h4>微观动态运行仿真引擎 (第6章)</h4>
              <p>Dijkstra 最短时间 · 仿真临时施工扰动与排队时延</p>
            </div>
          </div>

          <div class="model-step" style="padding-bottom:0;">
            <div class="step-idx" style="border-color:rgba(16,185,129,0.4); color:var(--emerald-light); background:rgba(16,185,129,0.15);">M5</div>
            <div class="step-info">
              <h4>碳排放与综合运营评价 (第6/7章)</h4>
              <p>核算减碳量、吨公里成本、工效提升与 SLA 履约率</p>
            </div>
          </div>
        </div>

        <!-- 7.3.1 Task Pool & Rolling Batching Details -->
        <div class="batch-highlight-card">
          <div style="font-size: 12px; font-weight:700; color: var(--text-main); margin-bottom: 2px;">
            当前执行重点批次：C04-R2
          </div>
          <div class="batch-tag">配送执行中</div>
          <div style="font-size: 10px; color: var(--text-muted); margin-bottom: 6px;">
            四家物流企业协同组批：顺丰(102件) · 京东(144件) · 中通(95件) · 韵达(55件)
          </div>

          <div class="batch-grid">
            <div class="batch-item">
              <div class="batch-item-label">承运无人车编号</div>
              <div class="batch-item-value" style="color:var(--sky-light);">C04-V1 (基准容积450件)</div>
            </div>
            <div class="batch-item">
              <div class="batch-item-label">本批次总装载量</div>
              <div class="batch-item-value tnum">396 件 <span style="font-size:9px; color:var(--emerald-light);">(满载率94.2%)</span></div>
            </div>
            <div class="batch-item">
              <div class="batch-item-label">计划发车时间</div>
              <div class="batch-item-value tnum">15:35:00 <span style="font-size:9px; color:var(--text-dim);">(已发车)</span></div>
            </div>
            <div class="batch-item">
              <div class="batch-item-label">预计返回接驳点</div>
              <div class="batch-item-value tnum">16:42:00 <span style="font-size:9px; color:var(--sky-light);">(余27min)</span></div>
            </div>
          </div>

          <div style="margin-top: 6px; background: rgba(10, 14, 23, 0.6); padding: 6px; border-radius: 4px; border: 1px solid var(--border-subtle);">
            <div style="font-size: 10px; color: var(--text-muted); margin-bottom: 3px;">服务节点访问次序与任务拆解：</div>
            <div style="font-size: 11px; color: var(--text-secondary); display:flex; align-items:center; gap:4px; flex-wrap:wrap;">
              <span style="color:var(--emerald-light);">D03 (120件)</span> → 
              <span style="color:var(--emerald-light);">D04 (45件)</span> → 
              <span style="color:var(--sky-light); font-size:10px;">[绕行D08]</span> →
              <span style="color:var(--amber-light); font-weight:600;">D06 (146件)</span> → 
              <span style="color:var(--rose-light); font-weight:700;">D05 (85件人车交接)</span>
            </div>
          </div>
        </div>

        <!-- Order Pool Aggregation Breakdown -->
        <div style="background: var(--bg-card); border-radius: 6px; padding: 8px 10px; border: 1px solid var(--border-subtle);">
          <div style="font-size: 11px; font-weight:600; margin-bottom: 6px; display:flex; justify-content:space-between; align-items:center;">
            <span>任务池待编组分布 (共 248 件)</span>
            <span style="color:var(--amber-light); font-size:10px;">预计 6 分钟后触发下一批</span>
          </div>
          <div style="display:flex; flex-direction:column; gap:5px; font-size:10px;">
            <div style="display:flex; justify-content:space-between; color:var(--text-muted);">
              <span>顺丰速运 (SF)</span><span class="tnum">96 件 (预约上门 32 件)</span>
            </div>
            <div style="height:4px; background:rgba(255,255,255,0.06); border-radius:2px; overflow:hidden;">
              <div style="width:38%; height:100%; background:var(--sky);"></div>
            </div>

            <div style="display:flex; justify-content:space-between; color:var(--text-muted);">
              <span>京东物流 (JD)</span><span class="tnum">74 件 (自提柜 50 件)</span>
            </div>
            <div style="height:4px; background:rgba(255,255,255,0.06); border-radius:2px; overflow:hidden;">
              <div style="width:30%; height:100%; background:var(--rose);"></div>
            </div>

            <div style="display:flex; justify-content:space-between; color:var(--text-muted);">
              <span>中通/圆通/韵达</span><span class="tnum">78 件 (混合需求)</span>
            </div>
            <div style="height:4px; background:rgba(255,255,255,0.06); border-radius:2px; overflow:hidden;">
              <div style="width:32%; height:100%; background:var(--emerald);"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Center Panel: GIS Operations Map & Real-Time Digital Twin -->
    <div class="panel gis-container">
      <div class="panel-header">
        <div class="panel-title">
          <div class="panel-title-badge"></div>
          <span id="centerMapTitle">社区末端微观拓扑与人车协同数字孪生 (亦城茗苑示范区)</span>
        </div>

        <div style="display:flex; align-items:center; gap:8px;">
          <!-- Community Selector Dropdown -->
          <div class="community-select-btn">
            <span>示范区:</span>
            <select id="communitySelect" onchange="switchCommunity(this.value)">
              <option value="C04" selected>C04 亦城茗苑 (重点示范区)</option>
              <option value="C01">C01 梅园小区</option>
              <option value="C02">C02 鹿鸣苑</option>
              <option value="C03">C03 天华园二里一区</option>
              <option value="C05">C05 听涛雅苑</option>
            </select>
          </div>

          <span style="font-size:11px; background:rgba(2,132,199,0.12); color:var(--sky-light); padding:3px 8px; border-radius:4px; border:1px solid rgba(56,189,248,0.25);">
            高精地理坐标孪生
          </span>
        </div>
      </div>

      <div class="gis-map-wrapper">
        <!-- Leaflet Map Container -->
        <div id="leafletMap"></div>

        <!-- Top Floating HUD -->
        <div class="gis-top-hud">
          <div class="gis-hud-left">
            <div class="gis-chip"><span class="dot" style="background:var(--sky-light);"></span> 无人车: 4台在勤</div>
            <div class="gis-chip"><span class="dot" style="background:var(--emerald);"></span> 配送员: 3人协同</div>
            <div class="gis-chip"><span class="dot" style="background:var(--amber);"></span> 智能柜: 4座 (S03预警)</div>
            <div class="gis-chip alert" id="hudAlertChip">
              <span class="dot" style="background:var(--rose);"></span> 施工预警: D04-D06干道 (动态重路由中)
            </div>
          </div>

          <div class="gis-hud-right">
            <!-- Layer Toggles -->
            <div class="gis-layer-toggles">
              <button class="layer-btn active" id="btnToggleRoads" onclick="toggleLayer('roads')">✓ 路网</button>
              <button class="layer-btn active" id="btnToggleRoute" onclick="toggleLayer('route')">✓ 配送路线</button>
              <button class="layer-btn active" id="btnToggleUgvs" onclick="toggleLayer('ugvs')">✓ 车辆</button>
              <button class="layer-btn active" id="btnToggleCouriers" onclick="toggleLayer('couriers')">✓ 配送员</button>
              <button class="layer-btn active" id="btnToggleLockers" onclick="toggleLayer('lockers')">✓ 智能柜</button>
              <button class="layer-btn active" id="btnToggleBuildings" onclick="toggleLayer('buildings')">✓ 楼栋</button>
            </div>

            <!-- Tile Theme Switcher -->
            <div class="gis-layer-toggles">
              <button class="layer-btn active" id="btnTileDark" onclick="setTileTheme('amap-dark')">🌌 高德暗色</button>
              <button class="layer-btn" id="btnTileOsm" onclick="setTileTheme('osm-dark')">🗺️ OSM暗色</button>
              <button class="layer-btn" id="btnTileSat" onclick="setTileTheme('amap-sat')">🛰️ 卫星遥感</button>
            </div>
          </div>
        </div>

        <!-- Map Floating Legend -->
        <div class="gis-legend">
          <div class="legend-row">
            <div class="legend-color" style="background:var(--sky-light);"></div>
            <span>无人车巡回路线 (C04-R2)</span>
          </div>
          <div class="legend-row">
            <div class="legend-color" style="background:var(--emerald);"></div>
            <span>配送员 (交接/上门交付)</span>
          </div>
          <div class="legend-row">
            <div class="legend-color" style="background:#6366f1;"></div>
            <span>住宅节点 (D01 ~ D12)</span>
          </div>
          <div class="legend-row">
            <div class="legend-color" style="background:#0284c7;"></div>
            <span>接驳枢纽 (A-01 / 社区主站)</span>
          </div>
          <div class="legend-row">
            <div class="legend-color" style="background:var(--amber);"></div>
            <span>智能柜 (S01~S04 负荷监控)</span>
          </div>
          <div class="legend-row">
            <div class="legend-color" style="background:var(--rose);"></div>
            <span>施工管制路段 🚧 (重规划绕行)</span>
          </div>
        </div>
      </div>

      <!-- Bottom KPI & Micro Charts of Center Panel -->
      <div class="center-bottom">
        <div class="kpi-box">
          <div class="kpi-title">综合碳减排率 (M5模型测算)</div>
          <div style="display:flex; justify-content:space-between; align-items:baseline;">
            <div class="kpi-num tnum" style="color:var(--emerald-light);">-28.4%</div>
            <div style="font-size:9px; color:var(--text-muted);">今日节约 318.6 kg CO₂</div>
          </div>
          <!-- Clean Mini SVG Bar Chart -->
          <svg width="100%" height="20" style="margin-top:2px;">
            <rect x="0" y="2" width="100%" height="6" fill="rgba(255,255,255,0.08)" rx="2"/>
            <rect x="0" y="2" width="71.6%" height="6" fill="var(--emerald)" rx="2"/>
            <rect x="0" y="11" width="100%" height="6" fill="rgba(255,255,255,0.08)" rx="2"/>
            <rect x="0" y="11" width="100%" height="6" fill="#475569" rx="2"/>
          </svg>
          <div class="kpi-desc" style="display:flex; justify-content:space-between;">
            <span>人机共配模式</span><span>传统分散配送</span>
          </div>
        </div>

        <div class="kpi-box">
          <div class="kpi-title">末端吨公里综合成本 (OPEX+CAPEX)</div>
          <div style="display:flex; justify-content:space-between; align-items:baseline;">
            <div class="kpi-num tnum" style="color:var(--sky-light);">-21.6%</div>
            <div style="font-size:9px; color:var(--text-muted);">单票降至 1.18 元</div>
          </div>
          <!-- Clean Mini SVG Sparkline -->
          <svg width="100%" height="20" style="margin-top:2px;">
            <path d="M 0 16 Q 35 12 70 8 T 140 4 T 210 2" fill="none" stroke="var(--sky-light)" stroke-width="1.8"/>
            <circle cx="210" cy="2" r="2.5" fill="var(--cyan)"/>
          </svg>
          <div class="kpi-desc">规模协同集约配送大幅削减空驶与重复巡回</div>
        </div>

        <div class="kpi-box">
          <div class="kpi-title">居民末端平均等待时延 (SLA)</div>
          <div style="display:flex; justify-content:space-between; align-items:baseline;">
            <div class="kpi-num tnum" style="color:var(--cyan);">-32.0%</div>
            <div style="font-size:9px; color:var(--emerald-light);">准时率 99.4%</div>
          </div>
          <div style="height:5px; background:rgba(255,255,255,0.08); border-radius:3px; margin-top:8px; overflow:hidden;">
            <div style="width:99.4%; height:100%; background:linear-gradient(90deg,var(--cyan),var(--emerald));"></div>
          </div>
          <div class="kpi-desc">预约时间窗履约偏离 &lt; 5分钟</div>
        </div>

        <div class="kpi-box">
          <div class="kpi-title">车辆利用率与满载系数</div>
          <div style="display:flex; justify-content:space-between; align-items:baseline;">
            <div class="kpi-num tnum" style="color:var(--purple);">91.5%</div>
            <div style="font-size:9px; color:var(--text-muted);">空驶率仅 8.5%</div>
          </div>
          <div style="height:5px; background:rgba(255,255,255,0.08); border-radius:3px; margin-top:8px; overflow:hidden;">
            <div style="width:91.5%; height:100%; background:linear-gradient(90deg,var(--indigo),var(--purple));"></div>
          </div>
          <div class="kpi-desc">较传统分散配送空驶率下降 44.8%</div>
        </div>
      </div>
    </div>

    <!-- Right Panel: Human-Vehicle Collaboration & Resource Health -->
    <div class="panel">
      <div class="panel-header">
        <div class="panel-title">
          <div class="panel-title-badge"></div>
          人车协同交接与资源健康管控
        </div>
        <span style="font-size:11px; color:var(--emerald-light);">协同响应 99.1%</span>
      </div>
      
      <div class="panel-content">
        <!-- 7.3.1 (4) Human-Vehicle Joint Gantt Timeline -->
        <div style="background: var(--bg-card); border-radius: 6px; padding: 9px; border: 1px solid var(--border-subtle);">
          <div style="font-size: 11px; font-weight:600; color: var(--text-main); margin-bottom: 6px; display:flex; justify-content:space-between; align-items:center;">
            <span>人车协同交接时间轴 (批次 C04-R2)</span>
            <span style="color:var(--sky-light); font-size:10px;">交接点：D05专用泊位</span>
          </div>

          <div style="display:flex; flex-direction:column; gap:5px;">
            <div class="gantt-item">
              <div class="gantt-header">
                <span style="color:var(--sky-light); font-weight:600;">15:35 无人车 C04-V1 接驳站发车</span>
                <span style="color:var(--emerald-light);">已完成</span>
              </div>
              <div class="gantt-bar-bg"><div class="gantt-bar-fill" style="width:100%;"></div></div>
            </div>

            <div class="gantt-item">
              <div class="gantt-header">
                <span style="color:var(--sky-light); font-weight:600;">15:48 D03 智能柜投递 (120件)</span>
                <span style="color:var(--emerald-light);">已完成</span>
              </div>
              <div class="gantt-bar-bg"><div class="gantt-bar-fill" style="width:100%;"></div></div>
            </div>

            <div class="gantt-item" style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.08);">
              <div class="gantt-header">
                <span style="color:#fff; font-weight:700;">16:02 人车交接点 (D05 节点)</span>
                <span style="color:var(--amber-light); font-weight:700;">预计3分钟后</span>
              </div>
              <div style="font-size:10px; color:var(--text-muted);">
                交接对象：配送员 张伟 (工号C-0407) · 接收包裹: 85件 (入户预约件)
              </div>
              <div class="gantt-bar-bg"><div class="gantt-bar-fill" style="width:82%; background:var(--amber);"></div></div>
            </div>

            <div class="gantt-item">
              <div class="gantt-header">
                <span style="color:var(--text-muted);">16:15 配送员张伟开展 D05 单元入户交付</span>
                <span style="color:var(--text-dim);">计划中</span>
              </div>
              <div class="gantt-bar-bg"><div class="gantt-bar-fill" style="width:0%;"></div></div>
            </div>

            <div class="gantt-item">
              <div class="gantt-header">
                <span style="color:var(--text-muted);">16:42 无人车 C04-V1 闭环返回接驳站</span>
                <span style="color:var(--text-dim);">计划中</span>
              </div>
              <div class="gantt-bar-bg"><div class="gantt-bar-fill" style="width:0%;"></div></div>
            </div>
          </div>
        </div>

        <!-- 7.3.1 (5) Smart Locker Status & 4-Tier Offloading Logic -->
        <div style="background: var(--bg-card); border-radius: 6px; padding: 9px; border: 1px solid var(--border-subtle);">
          <div style="font-size: 11px; font-weight:600; color: var(--text-main); margin-bottom: 5px; display:flex; justify-content:space-between; align-items:center;">
            <span>智能柜负荷与四级分流机制</span>
            <span style="color:var(--amber-light); font-size:10px;">S03高负荷预警</span>
          </div>

          <div class="res-list">
            <div class="res-item">
              <span>S01 柜 (1-2号楼北侧)</span>
              <span class="tnum" style="color:var(--emerald-light); font-weight:600;">68% (余38格)</span>
            </div>
            <div class="res-item">
              <span>S02 柜 (3-4号楼中心)</span>
              <span class="tnum" style="color:var(--emerald-light); font-weight:600;">74% (余31格)</span>
            </div>
            <div class="res-item" style="border-color: rgba(245, 158, 11, 0.4); background: rgba(245, 158, 11, 0.08);">
              <span style="color:#fed7aa; font-weight:600;">S03 柜 (5-6号楼南侧·高负荷)</span>
              <span class="tnum" style="color:var(--amber-light); font-weight:700;">92% (仅余9格)</span>
            </div>
            <div class="res-item">
              <span>S04 柜 (7-8号楼东侧)</span>
              <span class="tnum" style="color:var(--emerald-light); font-weight:600;">55% (余54格)</span>
            </div>
          </div>

          <div style="background: rgba(10, 14, 23, 0.6); border-radius: 4px; padding: 5px 7px; font-size: 10px; color: var(--text-muted); line-height: 1.4; border-left: 2px solid var(--amber); margin-top: 5px;">
            <strong>分流策略触发：</strong> 现有柜(S03)满载 → 自动引导邻近柜(S02) → 转入驿站暂存 → 人工配送员上门交付。
          </div>
        </div>

        <!-- Vehicle Fleet Battery & SOC Monitoring -->
        <div style="background: var(--bg-card); border-radius: 6px; padding: 9px; border: 1px solid var(--border-subtle);">
          <div style="font-size: 11px; font-weight:600; color: var(--text-main); margin-bottom: 5px; display:flex; justify-content:space-between; align-items:center;">
            <span>无人配送车 SOC 电量与运力健康</span>
            <span style="color:var(--sky-light); font-size:10px;">12台在勤 / 3台补能</span>
          </div>

          <div class="res-list">
            <div class="res-item">
              <span>C04-V1 (执行 C04-R2)</span>
              <span class="tnum" style="color:var(--emerald-light); font-weight:600;">SOC 78% (续航46km)</span>
            </div>
            <div class="res-item">
              <span>C04-V2 (执行 C04-R1)</span>
              <span class="tnum" style="color:var(--emerald-light); font-weight:600;">SOC 64% (续航38km)</span>
            </div>
            <div class="res-item" style="border-color: rgba(244, 63, 94, 0.35); background: rgba(244, 63, 94, 0.08);">
              <span style="color:#fecdd3;">C04-V4 (低电预警)</span>
              <span class="tnum" style="color:var(--rose-light); font-weight:700;">SOC 22% (快充中 · 余25min)</span>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>

  <script>
    // Live Clock
    function updateClock() {{
      const now = new Date();
      const h = String(now.getHours()).padStart(2, '0');
      const m = String(now.getMinutes()).padStart(2, '0');
      const s = String(now.getSeconds()).padStart(2, '0');
      const el = document.getElementById('liveClock');
      if (el) el.innerText = `${{h}}:${{m}}:${{s}}`;
    }}
    setInterval(updateClock, 1000);
    updateClock();

    // ==========================================
    // Real Geographic Dataset for Demonstration Communities
    // ==========================================
    const COMMUNITIES = {comm_json_str};

    // WGS-84 to GCJ-02 (Mars Coordinates) Transformer for AutoNavi Tiles
    function wgs84ToGcj02(lat, lng) {{
      const a = 6378245.0;
      const ee = 0.00669342162296594323;
      const pi = Math.PI;

      function transformLat(x, y) {{
        let ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * Math.sqrt(Math.abs(x));
        ret += (20.0 * Math.sin(6.0 * x * pi) + 20.0 * Math.sin(2.0 * x * pi)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(y * pi) + 40.0 * Math.sin(y / 3.0 * pi)) * 2.0 / 3.0;
        ret += (160.0 * Math.sin(y / 12.0 * pi) + 320 * Math.sin(y * pi / 30.0)) * 2.0 / 3.0;
        return ret;
      }}

      function transformLng(x, y) {{
        let ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * Math.sqrt(Math.abs(x));
        ret += (20.0 * Math.sin(6.0 * x * pi) + 20.0 * Math.sin(2.0 * x * pi)) * 2.0 / 3.0;
        ret += (20.0 * Math.sin(x * pi) + 40.0 * Math.sin(x / 3.0 * pi)) * 2.0 / 3.0;
        ret += (150.0 * Math.sin(x / 12.0 * pi) + 300.0 * Math.sin(x / 30.0 * pi)) * 2.0 / 3.0;
        return ret;
      }}

      const x = lng - 105.0;
      const y = lat - 35.0;
      let dLat = transformLat(x, y);
      let dLng = transformLng(x, y);
      const radLat = lat / 180.0 * pi;
      let magic = Math.sin(radLat);
      magic = 1 - ee * magic * magic;
      const sqrtMagic = Math.sqrt(magic);
      dLat = (dLat * 180.0) / ((a * (1 - ee)) / (magic * sqrtMagic) * pi);
      dLng = (dLng * 180.0) / (a / sqrtMagic * Math.cos(radLat) * pi);
      return [lat + dLat, lng + dLng];
    }}

    function projectCoords(coords, targetTheme) {{
      const isGCJ02 = (targetTheme === 'amap-dark' || targetTheme === 'amap-sat');
      if (Array.isArray(coords[0])) {{
        return coords.map(pt => projectCoords(pt, targetTheme));
      }}
      if (isGCJ02) {{
        return wgs84ToGcj02(coords[0], coords[1]);
      }}
      return [coords[0], coords[1]];
    }}

    // ==========================================
    // Map Engine Initialization & Layer Management
    // ==========================================
    let map = null;
    let tileLayers = {{}};
    let currentTileTheme = 'amap-dark';
    let currentCommunityId = 'C04';
    
    // Layer Groups
    const layerGroups = {{
      boundary: null,
      roads: null,
      route: null,
      lockers: null,
      buildings: null,
      ugvs: null,
      couriers: null,
      blockage: null
    }};

    const layerVisibility = {{
      roads: true,
      route: true,
      ugvs: true,
      couriers: true,
      lockers: true,
      buildings: true
    }};

    function initGISMap() {{
      const c = COMMUNITIES[currentCommunityId];
      const initialCenter = projectCoords(c.center, currentTileTheme);
      
      map = L.map('leafletMap', {{
        center: initialCenter,
        zoom: 18,
        zoomControl: false,
        attributionControl: false
      }});

      // Zoom control placed bottom-left above legend
      L.control.zoom({{ position: 'bottomleft' }}).addTo(map);

      // Define Tile Layers
      tileLayers['amap-dark'] = L.tileLayer(
        'https://webrd0{{s}}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={{x}}&y={{y}}&z={{z}}',
        {{
          maxZoom: 19,
          minZoom: 14,
          subdomains: ['1', '2', '3', '4'],
          className: 'amap-dark-tiles',
          attribution: '&copy; 高德地图 AutoNavi'
        }}
      );

      tileLayers['osm-dark'] = L.tileLayer(
        'https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png',
        {{
          maxZoom: 19,
          minZoom: 14,
          className: 'osm-dark-tiles',
          attribution: '&copy; OpenStreetMap'
        }}
      );

      tileLayers['amap-sat'] = L.tileLayer(
        'https://webst0{{s}}.is.autonavi.com/appmaptile?style=6&x={{x}}&y={{y}}&z={{z}}',
        {{
          maxZoom: 19,
          minZoom: 14,
          subdomains: ['1', '2', '3', '4'],
          attribution: '&copy; 高德遥感'
        }}
      );

      // Mount default dark tile
      setTileTheme('amap-dark');

      // Initialize Layer Groups
      Object.keys(layerGroups).forEach(k => {{
        layerGroups[k] = L.layerGroup().addTo(map);
      }});

      // Render Active Community
      renderCommunity(currentCommunityId);

      // Start UGV Waypoint Path Animation
      initUGVWaypointSimulation();
    }}

    function setTileTheme(theme) {{
      const themeChanged = (currentTileTheme !== theme);
      currentTileTheme = theme;
      Object.keys(tileLayers).forEach(k => {{
        if (map.hasLayer(tileLayers[k])) {{
          map.removeLayer(tileLayers[k]);
        }}
      }});

      if (tileLayers[theme]) {{
        tileLayers[theme].addTo(map);
      }}

      // Toggle UI button state
      document.getElementById('btnTileDark').classList.toggle('active', theme === 'amap-dark');
      document.getElementById('btnTileOsm').classList.toggle('active', theme === 'osm-dark');
      document.getElementById('btnTileSat').classList.toggle('active', theme === 'amap-sat');

      // If switching between GCJ02 and WGS84, re-render layers for accurate alignment
      if (themeChanged && map) {{
        renderCommunity(currentCommunityId);
      }}
    }}

    function toggleLayer(layerName) {{
      layerVisibility[layerName] = !layerVisibility[layerName];
      const btn = document.getElementById('btnToggle' + layerName.charAt(0).toUpperCase() + layerName.slice(1));
      if (btn) {{
        btn.classList.toggle('active', layerVisibility[layerName]);
        btn.innerText = (layerVisibility[layerName] ? '✓ ' : '✕ ') + btn.innerText.replace(/^[✓✕]\s*/, '');
      }}

      if (layerGroups[layerName]) {{
        if (layerVisibility[layerName]) {{
          map.addLayer(layerGroups[layerName]);
        }} else {{
          map.removeLayer(layerGroups[layerName]);
        }}
      }}
    }}

    function switchCommunity(cid) {{
      if (!COMMUNITIES[cid]) return;
      currentCommunityId = cid;
      const c = COMMUNITIES[cid];
      
      // Update titles
      document.getElementById('centerMapTitle').innerText = `社区末端微观拓扑与人车协同数字孪生 (${{c.name}}示范区)`;
      document.getElementById('headerCommunityName').innerText = `北京经开区·${{c.name}} (${{cid}})`;
      if (c.hub) {{
        document.getElementById('headerHubName').innerText = c.hub.name;
      }}

      renderCommunity(cid);
    }}

    let currentPolygonBounds = null;

    function renderCommunity(cid) {{
      const c = COMMUNITIES[cid];
      if (!c) return;
      
      // Clear previous layers
      Object.keys(layerGroups).forEach(k => layerGroups[k].clearLayers());

      // 1. Boundary Polygon with Accurate Coordinates
      if (c.polygon && c.polygon.length > 0) {{
        const projPoly = projectCoords(c.polygon, currentTileTheme);
        const poly = L.polygon(projPoly, {{
          color: '#38bdf8',
          weight: 2,
          opacity: 0.9,
          fillColor: '#0284c7',
          fillOpacity: 0.08,
          dashArray: '5, 4'
        }});
        poly.bindTooltip(`<div style="font-size:11px; font-weight:700; color:#38bdf8;">${{c.name}} 示范区红线</div>`, {{
          sticky: true,
          direction: 'top'
        }});
        layerGroups.boundary.addLayer(poly);
        currentPolygonBounds = poly.getBounds();
        map.fitBounds(currentPolygonBounds, {{ padding: [35, 35], maxZoom: 18 }});
      }} else if (c.center) {{
        const projCenter = projectCoords(c.center, currentTileTheme);
        map.setView(projCenter, 18);
      }}

      // 2. Road Network
      if (c.roads && c.roads.length > 0) {{
        c.roads.forEach(r => {{
          const projR = projectCoords(r, currentTileTheme);
          const roadLine = L.polyline(projR, {{
            color: 'rgba(148, 163, 184, 0.4)',
            weight: 3,
            lineCap: 'round'
          }});
          layerGroups.roads.addLayer(roadLine);
        }});
      }}

      // 3. Central Handover Hub
      if (c.hub) {{
        const projHub = projectCoords([c.hub.lat, c.hub.lng], currentTileTheme);
        const hubIcon = L.divIcon({{
          className: 'custom-marker',
          html: `
            <div style="background:linear-gradient(135deg, #0284c7, #0369a1); width:28px; height:28px; border-radius:6px; border:2px solid #bae6fd; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 8px rgba(0,0,0,0.5);">
              <span style="font-size:14px;">🏢</span>
            </div>
            <div class="marker-label-badge" style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); border-color:#38bdf8; color:#bae6fd;">
              ${{c.hub.name.split('（')[0]}}
            </div>
          `,
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        }});
        const hubMarker = L.marker(projHub, {{ icon: hubIcon }});
        hubMarker.bindPopup(`
          <div class="popup-inner">
            <div class="popup-title">${{c.hub.name}}</div>
            <div class="popup-row"><span>功能定位:</span> <strong>干线巡回与社区末端交接枢纽</strong></div>
            <div class="popup-row"><span>泊位容量:</span> <strong>2台无人车换电泊位 + 4托盘暂存</strong></div>
            <div class="popup-row"><span>当前状态:</span> <strong style="color:var(--emerald-light);">正常运行中</strong></div>
          </div>
        `);
        layerGroups.boundary.addLayer(hubMarker);
      }}

      // 4. Buildings (Demand Nodes) - Elegant compact badges
      if (c.buildings && c.buildings.length > 0) {{
        c.buildings.forEach(b => {{
          const isHandoff = (b.id === 'C04-D05' || b.id === 'D05');
          const projB = projectCoords([b.lat, b.lng], currentTileTheme);
          const bNum = b.id.replace('C04-', '').replace('C01-', '').replace('C02-', '').replace('C03-', '').replace('C05-', '');
          
          const bIcon = L.divIcon({{
            className: 'custom-marker',
            html: `
              <div style="background:${{isHandoff ? '#f43f5e' : '#312e81'}}; width:${{isHandoff ? 22 : 18}}px; height:${{isHandoff ? 22 : 18}}px; border-radius:50%; border:1.5px solid ${{isHandoff ? '#fecdd3' : '#a5b4fc'}}; display:flex; align-items:center; justify-content:center; color:#fff; font-size:9px; font-weight:700; box-shadow:0 2px 6px rgba(0,0,0,0.4);">
                ${{isHandoff ? '🤝' : bNum.replace('D', '')}}
              </div>
              ${{isHandoff ? `
                <div class="marker-label-badge" style="position:absolute; top:-20px; left:50%; transform:translateX(-50%); border-color:#f43f5e; color:#fecdd3; font-weight:700;">
                  D05 人车交接点
                </div>
              ` : ''}}
            `,
            iconSize: [22, 22],
            iconAnchor: [11, 11]
          }});
          const bMarker = L.marker(projB, {{ icon: bIcon }});
          bMarker.bindPopup(`
            <div class="popup-inner">
              <div class="popup-title">${{b.name}} (${{b.id}})</div>
              <div class="popup-row"><span>服务户数:</span> <strong>${{b.households}} 户</strong></div>
              <div class="popup-row"><span>日均需求:</span> <strong>${{b.daily}} 件/日</strong></div>
              <div class="popup-row"><span>服务时间窗:</span> <strong>${{b.time}}</strong></div>
              ${{isHandoff ? '<div class="popup-row" style="color:var(--rose-light);"><strong>★ 人车强同步协同交接指定泊位</strong></div>' : ''}}
            </div>
          `);
          layerGroups.buildings.addLayer(bMarker);
        }});
      }}

      // 5. Smart Lockers
      if (c.lockers && c.lockers.length > 0) {{
        c.lockers.forEach(l => {{
          const isWarn = l.status === 'warn' || (l.util && parseInt(l.util) >= 90);
          const projL = projectCoords([l.lat, l.lng], currentTileTheme);
          const lIcon = L.divIcon({{
            className: 'custom-marker',
            html: `
              <div style="background:${{isWarn ? '#d97706' : '#059669'}}; width:18px; height:18px; border-radius:4px; border:1.5px solid #fff; display:flex; align-items:center; justify-content:center; color:#fff; font-size:9px;">
                📦
              </div>
              <div class="marker-label-badge" style="position:absolute; top:-19px; left:50%; transform:translateX(-50%); border-color:${{isWarn ? '#f59e0b' : '#10b981'}}; color:${{isWarn ? '#fbbf24' : '#34d399'}};">
                ${{l.id}} (${{l.util}})
              </div>
            `,
            iconSize: [18, 18],
            iconAnchor: [9, 9]
          }});
          const lMarker = L.marker(projL, {{ icon: lIcon }});
          lMarker.bindPopup(`
            <div class="popup-inner">
              <div class="popup-title">${{l.name}}</div>
              <div class="popup-row"><span>格口容量:</span> <strong>${{l.cap}}</strong></div>
              <div class="popup-row"><span>当前利用率:</span> <strong style="color:${{isWarn ? 'var(--amber-light)' : 'var(--emerald-light)'}};">${{l.util}}</strong></div>
              <div class="popup-row"><span>运行策略:</span> <strong>${{isWarn ? '已触发四级分流至邻近S02柜' : '负荷均衡'}}</strong></div>
            </div>
          `);
          layerGroups.lockers.addLayer(lMarker);
        }});
      }}

      // 6. Active Delivery Route (C04-R2)
      if (c.activeRoute && c.activeRoute.length > 0) {{
        const projRoute = projectCoords(c.activeRoute, currentTileTheme);
        const routeLine = L.polyline(projRoute, {{
          color: '#38bdf8',
          weight: 4,
          opacity: 0.9,
          dashArray: '8, 6',
          lineJoin: 'round'
        }});
        routeLine.bindTooltip('<div style="font-size:10px; font-weight:bold; color:#38bdf8;">C04-R2 批次运行轨迹 (396件)</div>', {{ sticky: true }});
        layerGroups.route.addLayer(routeLine);
      }}

      // 7. Road Blockage & Detour
      if (c.blockedRoad && c.blockedRoad.length > 0) {{
        const projBlock = projectCoords(c.blockedRoad, currentTileTheme);
        const blockLine = L.polyline(projBlock, {{
          color: '#f43f5e',
          weight: 4,
          dashArray: '6, 6',
          opacity: 0.95
        }});
        blockLine.bindTooltip('<div style="font-size:10px; font-weight:bold; color:#f43f5e;">🚧 D04-D06干道施工管制闭合</div>', {{ sticky: true }});
        layerGroups.blockage.addLayer(blockLine);

        // Detour line via D08
        if (c.detourRoad && c.detourRoad.length > 0) {{
          const projDetour = projectCoords(c.detourRoad, currentTileTheme);
          const detourLine = L.polyline(projDetour, {{
            color: '#06b6d4',
            weight: 3.5,
            dashArray: '4, 4',
            opacity: 0.95
          }});
          detourLine.bindTooltip('<div style="font-size:10px; font-weight:bold; color:#22d3ee;">Dijkstra 动态重规划绕行路线</div>', {{ sticky: true }});
          layerGroups.blockage.addLayer(detourLine);
        }}

        // Warning Icon Marker
        const warnIcon = L.divIcon({{
          className: 'custom-marker',
          html: `<div style="font-size:16px;">🚧</div>`,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        }});
        const midPt = [
          (projBlock[0][0] + projBlock[1][0]) / 2,
          (projBlock[0][1] + projBlock[1][1]) / 2
        ];
        const warnMarker = L.marker(midPt, {{ icon: warnIcon }});
        warnMarker.bindPopup(`
          <div class="popup-inner">
            <div class="popup-title" style="color:var(--rose-light);">🚧 临时施工封闭预警</div>
            <div class="popup-row"><span>影响路段:</span> <strong>D04 至 D06 主通道</strong></div>
            <div class="popup-row"><span>调度动作:</span> <strong>已触发微观动态重规划</strong></div>
            <div class="popup-row"><span>绕行路径:</span> <strong>经 D08 中心服务点绕行 (+1.4 min)</strong></div>
          </div>
        `);
        layerGroups.blockage.addLayer(warnMarker);
      }}

      // 8. Couriers
      if (c.couriers && c.couriers.length > 0) {{
        c.couriers.forEach(cr => {{
          const projCr = projectCoords([cr.lat, cr.lng], currentTileTheme);
          const crIcon = L.divIcon({{
            className: 'custom-marker',
            html: `
              <div style="background:#059669; width:22px; height:22px; border-radius:50%; border:2px solid #fff; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 6px rgba(0,0,0,0.4);">
                <span style="font-size:11px;">👤</span>
              </div>
              <div class="marker-label-badge" style="position:absolute; top:-19px; left:50%; transform:translateX(-50%); border-color:#10b981; color:#34d399;">
                ${{cr.name.split('（')[0].split(' ')[1] || cr.name}}
              </div>
            `,
            iconSize: [22, 22],
            iconAnchor: [11, 11]
          }});
          const crMarker = L.marker(projCr, {{ icon: crIcon }});
          crMarker.bindPopup(`
            <div class="popup-inner">
              <div class="popup-title">${{cr.name}}</div>
              <div class="popup-row"><span>当前状态:</span> <strong style="color:var(--emerald-light);">${{cr.status}}</strong></div>
              <div class="popup-row"><span>执行任务:</span> <strong>${{cr.task}}</strong></div>
            </div>
          `);
          layerGroups.couriers.addLayer(crMarker);
        }});
      }}

      // 9. UGVs
      renderUGVs(c);
    }}

    let ugvMarkers = [];

    function renderUGVs(c) {{
      ugvMarkers = [];
      if (!c.ugvs || c.ugvs.length === 0) return;

      c.ugvs.forEach(v => {{
        const isFocus = (v.id === 'C04-V1');
        const projV = projectCoords([v.lat, v.lng], currentTileTheme);
        const vIcon = L.divIcon({{
          className: 'custom-marker',
          html: `
            <div class="ugv-marker-container">
              ${{isFocus ? '<div class="ugv-pulse"></div>' : ''}}
              <div style="background:linear-gradient(135deg, #0284c7, #0ea5e9); width:26px; height:18px; border-radius:4px; border:1.5px solid #fff; display:flex; align-items:center; justify-content:center; box-shadow:0 2px 6px rgba(0,0,0,0.4);">
                <span style="font-size:8px; font-weight:800; color:#fff;">UGV</span>
              </div>
              <div class="marker-label-badge" style="position:absolute; top:-19px; left:50%; transform:translateX(-50%); border-color:#38bdf8; color:#bae6fd;">
                ${{v.id}} (${{v.load.split(' ')[0]}})
              </div>
            </div>
          `,
          iconSize: [26, 18],
          iconAnchor: [13, 9]
        }});

        const vMarker = L.marker(projV, {{ icon: vIcon }});
        vMarker.bindPopup(`
          <div class="popup-inner">
            <div class="popup-title">${{v.name}}</div>
            <div class="popup-row"><span>执行批次:</span> <strong>${{v.batch}}</strong></div>
            <div class="popup-row"><span>当前荷载:</span> <strong>${{v.load}}</strong></div>
            <div class="popup-row"><span>电量健康:</span> <strong style="color:var(--emerald-light);">${{v.soc}}</strong></div>
            <div class="popup-row"><span>实时动作:</span> <strong>${{v.status}}</strong></div>
          </div>
        `);
        layerGroups.ugvs.addLayer(vMarker);
        ugvMarkers.push({{ marker: vMarker, data: v, initialLat: projV[0], initialLng: projV[1] }});
      }});
    }}

    // Smooth Real Waypoint Path Interpolation for UGV C04-V1
    function initUGVWaypointSimulation() {{
      let routeIndex = 0;
      let progress = 0;

      setInterval(() => {{
        if (currentCommunityId !== 'C04') return;
        const c = COMMUNITIES['C04'];
        if (!c || !c.activeRoute || c.activeRoute.length < 2) return;

        const projRoute = projectCoords(c.activeRoute, currentTileTheme);
        const v1Obj = ugvMarkers.find(u => u.data.id === 'C04-V1');
        if (!v1Obj) return;

        progress += 0.05;
        if (progress >= 1.0) {{
          progress = 0;
          routeIndex = (routeIndex + 1) % (projRoute.length - 1);
        }}

        const p1 = projRoute[routeIndex];
        const p2 = projRoute[routeIndex + 1];
        const curLat = p1[0] + (p2[0] - p1[0]) * progress;
        const curLng = p1[1] + (p2[1] - p1[1]) * progress;

        v1Obj.marker.setLatLng([curLat, curLng]);
      }}, 500);
    }}

    // Initialize Map on DOM Ready
    window.addEventListener('DOMContentLoaded', () => {{
      initGISMap();
    }});
  </script>
</body>
</html>
'''

with open('chapter7_platform_frontend/terminal_operation.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Updated terminal_operation.html successfully with WGS84-GCJ02 projection and all 5 communities!")
