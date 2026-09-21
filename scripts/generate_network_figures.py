# -*- coding: utf-8 -*-
"""
Generate publication-quality figures for Chapter 4: Terminal Delivery Network Model.
Outputs:
1. Fig 4-1: Three-stage network optimization framework & platform dispatch pipeline
2. Fig 4-2: Service feasibility matrix & normalized distance heatmap for 5 communities
3. Fig 4-3: Five communities network topology & service coverage comparison
4. Fig 4-4: Facility capacity configuration, demand load & optimization evaluation

Follows Nature/SCI publication standards (300 DPI PNG + vector SVG, Okabe-Ito palette).
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

# Ensure directories exist
OUT_DIR_DOCS = os.path.join(r'd:\物流设计大赛', 'docs', 'images', 'network')
OUT_DIR_STATIC = os.path.join(r'd:\物流设计大赛', 'demo', 'static', 'images', 'network')
os.makedirs(OUT_DIR_DOCS, exist_ok=True)
os.makedirs(OUT_DIR_STATIC, exist_ok=True)

# Set fonts
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9.5
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 9.5
plt.rcParams['figure.titlesize'] = 14

# Okabe-Ito Color Palette
COLORS = {
    'black': '#000000',
    'orange': '#E69F00',
    'sky_blue': '#56B4E9',
    'bluish_green': '#009E73',
    'yellow': '#F0E442',
    'blue': '#0072B2',
    'vermillion': '#D55E00',
    'reddish_purple': '#CC79A7',
    'gray': '#999999',
    'light_gray': '#ECEFF1',
    'dark_navy': '#1A237E'
}

def save_fig(fig, basename):
    png_path = os.path.join(OUT_DIR_DOCS, f'{basename}.png')
    svg_path = os.path.join(OUT_DIR_DOCS, f'{basename}.svg')
    fig.savefig(png_path, dpi=300, bbox_inches='tight')
    fig.savefig(svg_path, bbox_inches='tight')
    
    # Also copy to demo/static
    import shutil
    shutil.copy(png_path, os.path.join(OUT_DIR_STATIC, f'{basename}.png'))
    shutil.copy(svg_path, os.path.join(OUT_DIR_STATIC, f'{basename}.svg'))
    print(f'Saved: {png_path} and SVG')
    plt.close(fig)


# ==============================================================================
# Fig 4-1: Three-Stage Network Model Framework & Platform Dispatch Pipeline
# ==============================================================================
def draw_fig4_1():
    fig, ax = plt.subplots(figsize=(13.5, 8.2))
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.965, '图 4-1 三阶段末端配送网络模型总体架构与平台调用数据流图', 
            ha='center', va='center', fontsize=14, fontweight='bold', color=COLORS['dark_navy'])
    
    # 3 Stages (Top half) - refined spacing: w=0.27, x=0.04, 0.365, 0.69
    stage_boxes = [
        {'title': '第一阶段：服务设施规模确定\n(Minimum Facility Scale Covering)',
         'desc': '- 目标：最小化新增设施数\n  $\\min Z_1 = \\sum_{j \\in \\mathcal{F}_{cand}} y_j$\n- 约束：需求完整覆盖约束 $\\sum x_{ij} = 1$\n- 服务可行约束 $x_{ij} \\leq a_{ij} y_j$\n- 设施容量约束 $\\sum q_i x_{ij} \\leq C_j y_j$\n- 输出：满足服务与容量的最少新增设施数 $K^*$',
         'x': 0.04, 'y': 0.52, 'w': 0.27, 'h': 0.38, 'color': '#E3F2FD', 'border': COLORS['blue']},
        
        {'title': '第二阶段：节点选址与需求分配\n(P-Median Location & Allocation)',
         'desc': '- 目标：最小化加权服务距离\n  $\\min Z_2 = \\sum_{i} \\sum_{j} q_i d_{ij} x_{ij}$\n- 约束：固定第一阶段设施规模 $\\sum y_j = K^*$\n- 需求唯一分配与容量约束\n- 存量设施保留约束 $y_j = 1, \\forall j \\in \\mathcal{F}_{exist}$\n- 输出：确定启用设施 $y_j^*$、服务分配 $x_{ij}^*$、设施负载 $Q_j^*$',
         'x': 0.365, 'y': 0.52, 'w': 0.27, 'h': 0.38, 'color': '#E8F5E9', 'border': COLORS['bluish_green']},
        
        {'title': '第三阶段：节点上下游连接关系确定\n(Network Connection & Flow Routing)',
         'desc': '- 目标：最小化加权配送距离\n  $\\min Z_3 = \\sum_{g} \\sum_{j} Q_j d_{gj} z_{gj}$\n- 约束：末端设施唯一上游供货点 $\\sum z_{gj} = y_j^*$\n- 供货驿站有效性 $z_{gj} \\leq y_g^*$\n- 驿站总吞吐能力校验 $Q_g^* + \\sum Q_j z_{gj} \\leq C_g$\n- 输出：完整三级物流拓扑连接 $z_{gj}^*$',
         'x': 0.69, 'y': 0.52, 'w': 0.27, 'h': 0.38, 'color': '#FFF3E0', 'border': COLORS['orange']}
    ]
    
    for s in stage_boxes:
        rect = patches.FancyBboxPatch((s['x'], s['y']), s['w'], s['h'],
                                      boxstyle="round,pad=0.018,rounding_size=0.03",
                                      facecolor=s['color'], edgecolor=s['border'], linewidth=2)
        ax.add_patch(rect)
        ax.text(s['x'] + s['w']/2, s['y'] + s['h'] - 0.035, s['title'],
                ha='center', va='top', fontsize=10.5, fontweight='bold', color=s['border'])
        ax.text(s['x'] + 0.015, s['y'] + s['h'] - 0.115, s['desc'],
                ha='left', va='top', fontsize=9, color='#212121', linespacing=1.35)

    # Arrows between stages
    ax.annotate('', xy=(0.365, 0.71), xytext=(0.31, 0.71),
                arrowprops=dict(arrowstyle="->", color=COLORS['dark_navy'], lw=2.2))
    ax.text(0.337, 0.74, '规模 $K^*$', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=COLORS['dark_navy'])
    
    ax.annotate('', xy=(0.69, 0.71), xytext=(0.635, 0.71),
                arrowprops=dict(arrowstyle="->", color=COLORS['dark_navy'], lw=2.2))
    ax.text(0.662, 0.74, '设施与需求\n$y^*, x^*, Q^*$', ha='center', va='bottom', fontsize=8, fontweight='bold', color=COLORS['dark_navy'])

    # Bottom half: Platform Dispatch & Data Flow Pipeline
    pipe_box = patches.FancyBboxPatch((0.04, 0.06), 0.92, 0.38,
                                      boxstyle="round,pad=0.02,rounding_size=0.03",
                                      facecolor='#F5F5F5', edgecolor='#78909C', linewidth=1.5, linestyle='--')
    ax.add_patch(pipe_box)
    ax.text(0.50, 0.41, '平台离线求解存储与在线动态调用流水线 (Online Dispatch Pipeline)',
            ha='center', va='top', fontsize=11, fontweight='bold', color='#37474F')

    pipe_steps = [
        {'step': '步骤 1', 'name': '包裹输入', 'sub': '目的地社区与\n楼栋地址输入', 'x': 0.07, 'y': 0.12, 'w': 0.13, 'h': 0.20, 'c': COLORS['light_gray'], 'tc': '#37474F'},
        {'step': '步骤 2', 'name': '需求节点匹配', 'sub': '地址匹配对应\n需求节点 $D_i$', 'x': 0.24, 'y': 0.12, 'w': 0.13, 'h': 0.20, 'c': '#E1F5FE', 'tc': COLORS['blue']},
        {'step': '步骤 3', 'name': '服务设施查询', 'sub': '读取 $x_{ij}^*$\n匹配主服务设施 $F_j$', 'x': 0.41, 'y': 0.12, 'w': 0.14, 'h': 0.20, 'c': '#E8F8F5', 'tc': COLORS['bluish_green']},
        {'step': '步骤 4', 'name': '上游接驳拼接', 'sub': '读取 $z_{gj}^*$\n确定上游供给节点 $g$', 'x': 0.59, 'y': 0.12, 'w': 0.14, 'h': 0.20, 'c': '#FFF8E1', 'tc': COLORS['orange']},
        {'step': '步骤 5 & 6', 'name': '完整路径输出', 'sub': '形成物流节点链\n输入第7章运行模型', 'x': 0.77, 'y': 0.12, 'w': 0.16, 'h': 0.20, 'c': '#FCE4EC', 'tc': COLORS['vermillion']},
    ]

    for p in pipe_steps:
        box = patches.FancyBboxPatch((p['x'], p['y']), p['w'], p['h'],
                                     boxstyle="round,pad=0.015,rounding_size=0.02",
                                     facecolor=p['c'], edgecolor=p['tc'], linewidth=1.8)
        ax.add_patch(box)
        ax.text(p['x'] + p['w']/2, p['y'] + p['h'] - 0.03, p['step'], ha='center', va='top', fontsize=9, fontweight='bold', color=p['tc'])
        ax.text(p['x'] + p['w']/2, p['y'] + p['h'] - 0.08, p['name'], ha='center', va='top', fontsize=10, fontweight='bold', color='#212121')
        ax.text(p['x'] + p['w']/2, p['y'] + 0.03, p['sub'], ha='center', va='bottom', fontsize=8.5, color='#424242')

    # Pipeline arrows
    for i in range(len(pipe_steps)-1):
        x1 = pipe_steps[i]['x'] + pipe_steps[i]['w']
        x2 = pipe_steps[i+1]['x']
        y_mid = pipe_steps[i]['y'] + pipe_steps[i]['h']/2
        ax.annotate('', xy=(x2, y_mid), xytext=(x1, y_mid),
                    arrowprops=dict(arrowstyle="->", color=COLORS['dark_navy'], lw=2.0))

    # Downward connection from Stage 3 to Platform Pipeline
    ax.annotate('', xy=(0.50, 0.44), xytext=(0.50, 0.52),
                arrowprops=dict(arrowstyle="->", color=COLORS['dark_navy'], lw=2.2, linestyle=':'))
    ax.text(0.51, 0.48, '网络优化结果离线入库 ($y^*, x^*, z^*$)', ha='left', va='center', fontsize=9, fontweight='bold', color=COLORS['dark_navy'])

    save_fig(fig, 'fig4_1_network_model_framework')


# ==============================================================================
# Fig 4-2: Service Feasibility Matrix & Normalized Distance Heatmap
# ==============================================================================
def draw_fig4_2():
    np.random.seed(42)
    fig = plt.figure(figsize=(13, 8))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)
    
    # Subplot A: C01 梅园小区可行性热力图 (4 Demand Nodes x 3 Facilities)
    ax1 = fig.add_subplot(gs[0, 0])
    c01_dists = np.array([
        [120, 185, 290],
        [195, 110, 240],
        [140, 210, 310],
        [220, 130, 260]
    ])
    d_max_c01 = 500.0
    c01_norm = c01_dists / d_max_c01
    im1 = ax1.imshow(c01_norm, cmap='YlGnBu', vmin=0, vmax=1.0, aspect='auto')
    ax1.set_xticks([0, 1, 2])
    ax1.set_xticklabels(['F01 (东门柜)', 'F03 (代收点)', 'F02 (副柜-候)'])
    ax1.set_yticks([0, 1, 2, 3])
    ax1.set_yticklabels(['D01 (1号楼)', 'D02 (2号楼)', 'D03 (3号楼)', 'D04 (4号楼)'])
    ax1.set_title('(a) 梅园小区 (C01): 标准化服务距离矩阵 $\\bar{d}_{ij} = d_{ij}/D_{\\max}$', fontsize=10.5, fontweight='bold')
    for i in range(4):
        for j in range(3):
            val = c01_norm[i, j]
            txt = f'{val:.2f}\n({c01_dists[i,j]}m)'
            col = 'white' if val > 0.5 else 'black'
            ax1.text(j, i, txt, ha='center', va='center', color=col, fontsize=8.5)

    # Subplot B: C02 鹿鸣苑可行性热力图 (7 Demand Nodes x 4 Facilities)
    ax2 = fig.add_subplot(gs[0, 1])
    c02_dists = np.array([
        [110, 85, 340, 480],
        [210, 240, 95, 390],
        [230, 260, 115, 380],
        [95, 140, 290, 450],
        [125, 160, 280, 420],
        [140, 180, 260, 410],
        [410, 430, 135, 290]
    ])
    c02_norm = c02_dists / d_max_c01
    im2 = ax2.imshow(c02_norm, cmap='YlGnBu', vmin=0, vmax=1.0, aspect='auto')
    ax2.set_xticks([0, 1, 2, 3])
    ax2.set_xticklabels(['F01(北柜1)', 'F02(北柜2)', 'F03(新增柜)', 'F04(候-接驳)'], fontsize=8.5)
    ax2.set_yticks(range(7))
    ax2.set_yticklabels([f'D0{i+1}' for i in range(7)], fontsize=9)
    ax2.set_title('(b) 鹿鸣苑 (C02): 北门设施 vs 新增F03柜空间互补性', fontsize=10.5, fontweight='bold')
    for i in range(7):
        for j in range(4):
            val = c02_norm[i, j]
            txt = f'{val:.2f}'
            col = 'white' if val > 0.5 else 'black'
            ax2.text(j, i, txt, ha='center', va='center', color=col, fontsize=8)

    # Subplot C: 距离衰减与服务可行性判定逻辑曲线
    ax3 = fig.add_subplot(gs[1, 0])
    d_range = np.linspace(0, 700, 200)
    acc_box = np.exp(-(d_range / 250)**2)
    acc_uav = np.exp(-(d_range / 350)**2)
    
    ax3.plot(d_range, acc_box, color=COLORS['blue'], lw=2.2, label='自提设施便利度 $S_{box}(d) = \\exp(-(d/250)^2)$')
    ax3.plot(d_range, acc_uav, color=COLORS['vermillion'], lw=2.2, linestyle='--', label='无人接驳通达度 $S_{uav}(d) = \\exp(-(d/350)^2)$')
    ax3.axvline(500, color=COLORS['blue'], linestyle=':', lw=1.8, label='自提硬约束阈值 $D_{\\max}=500\\text{ m}$')
    ax3.axvline(600, color=COLORS['vermillion'], linestyle=':', lw=1.8, label='接驳硬约束阈值 $D_{\\max}=600\\text{ m}$')
    ax3.set_xlabel('实际道路通行距离 (m)')
    ax3.set_ylabel('服务可行性与便利度评分')
    ax3.set_title('(c) 道路距离衰减函数与最大服务边界约束', fontsize=10.5, fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.5)
    ax3.legend(loc='upper right', fontsize=8.5)

    # Subplot D: 5 社区需求加权服务距离与最大距离 (ylim extended to 680 to prevent overlap)
    ax4 = fig.add_subplot(gs[1, 1])
    comms = ['梅园\nC01', '鹿鸣苑\nC02', '天华二里\nC03', '亦城茗苑\nC04', '听涛雅苑\nC05']
    avg_dists = [192.5, 166.2, 118.2, 327.4, 377.7]
    max_dists = [221.1, 429.2, 334.0, 572.4, 572.0]
    
    x = np.arange(len(comms))
    width = 0.35
    rects1 = ax4.bar(x - width/2, avg_dists, width, label='需求加权平均距离 $\\bar{d}$', color=COLORS['bluish_green'], edgecolor='black', alpha=0.85)
    rects2 = ax4.bar(x + width/2, max_dists, width, label='边缘节点最大距离 $d_{\\max}$', color=COLORS['orange'], edgecolor='black', alpha=0.85)
    
    # Threshold lines
    ax4.axhline(500, color=COLORS['blue'], linestyle='--', lw=1.5, alpha=0.7, label='自提阈值 (500m)')
    ax4.axhline(600, color=COLORS['vermillion'], linestyle='--', lw=1.5, alpha=0.7, label='接驳阈值 (600m)')
    
    ax4.set_ylabel('距离 (m)')
    ax4.set_xticks(x)
    ax4.set_xticklabels(comms)
    ax4.set_ylim(0, 680)  # Prevent overlap with legend!
    ax4.set_title('(d) 五社区优化后平均服务距离与最大服务距离对比', fontsize=10.5, fontweight='bold')
    ax4.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax4.legend(loc='upper left', fontsize=8.5, ncol=2)
    
    # Value labels
    for r in rects1:
        ax4.text(r.get_x() + r.get_width()/2, r.get_height() + 8, f'{r.get_height():.1f}', ha='center', va='bottom', fontsize=8)
    for r in rects2:
        ax4.text(r.get_x() + r.get_width()/2, r.get_height() + 8, f'{r.get_height():.1f}', ha='center', va='bottom', fontsize=8)

    save_fig(fig, 'fig4_2_service_feasibility_heatmap')


# ==============================================================================
# Fig 4-3: Five Communities Network Topology & Coverage Comparison
# ==============================================================================
def draw_fig4_3():
    fig = plt.figure(figsize=(14, 8.8))
    gs = GridSpec(2, 3, figure=fig, hspace=0.32, wspace=0.25)
    
    # Rescaled node y-coordinates to range [0.08, 0.68] to avoid title overlaps!
    comms_data = [
        {'name': '梅园小区 (C01)', 'type': '存量双节点协同型', 'sub': '不新增设施，F01与F03分工明确',
         'nodes': [('D01', 0.20, 0.52, 58.2), ('D02', 0.25, 0.22, 54.6), ('D03', 0.80, 0.58, 25.8), ('D04', 0.75, 0.16, 24.6)],
         'facs': [('F01(东柜1)', 0.50, 0.65, '柜', COLORS['blue']), ('F03(代收点)', 0.50, 0.12, '驿', COLORS['bluish_green'])],
         'links': [(0, 0), (2, 0), (1, 1), (3, 1)]},
        
        {'name': '鹿鸣苑 (C02)', 'type': '新增节点补缺型', 'sub': '新增 F03 (3号楼柜)，消灭南端缺口',
         'nodes': [('D01', 0.15, 0.62, 42.0), ('D04', 0.30, 0.55, 46.8), ('D05', 0.45, 0.58, 38.0), ('D06', 0.55, 0.50, 36.0),
                   ('D02', 0.70, 0.25, 32.0), ('D03', 0.85, 0.30, 35.0), ('D07', 0.80, 0.12, 30.0)],
         'facs': [('F01(北柜1)', 0.35, 0.66, '柜', COLORS['blue']), ('F02(北柜2)', 0.15, 0.66, '柜', COLORS['blue']),
                  ('F03(新增柜*)', 0.75, 0.18, '新增柜', COLORS['vermillion'])],
         'links': [(3, 0), (4, 0), (5, 0), (0, 1), (1, 2), (2, 2), (6, 2)]},
        
        {'name': '天华园二里一区 (C03)', 'type': '存量节点重分配型', 'sub': '存量设施充足，重划服务分区',
         'nodes': [('D01', 0.15, 0.50, 28), ('D05', 0.25, 0.62, 22), ('D06', 0.35, 0.50, 24), ('D08', 0.20, 0.35, 17),
                   ('D02', 0.60, 0.58, 18), ('D04', 0.75, 0.50, 16), ('D07', 0.85, 0.62, 20), ('D11', 0.90, 0.46, 14),
                   ('D03', 0.50, 0.18, 32), ('D09', 0.65, 0.14, 30), ('D10', 0.80, 0.22, 30)],
         'facs': [('F01(柜)', 0.25, 0.42, '柜', COLORS['blue']), ('F03(代收点)', 0.75, 0.58, '驿', COLORS['bluish_green']),
                  ('F04(菜鸟)', 0.65, 0.25, '驿', COLORS['bluish_green'])],
         'links': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 1), (5, 1), (6, 1), (7, 1), (8, 2), (9, 2), (10, 2)]},
        
        {'name': '亦城茗苑 (C04)', 'type': '入口接驳与无人配送型', 'sub': '东侧入口接驳点 F05 汇聚1284.6件/日',
         'nodes': [(f'簇{i+1}', np.cos(i*np.pi/6)*0.32 + 0.55, np.sin(i*np.pi/6)*0.25 + 0.38, 107) for i in range(12)],
         'facs': [('F05(东接驳*)', 0.12, 0.38, '接驳', COLORS['orange'])],
         'links': [(i, 0) for i in range(12)]},
        
        {'name': '听涛雅苑 (C05)', 'type': '入口接驳与无人配送型', 'sub': '东门接驳点 F04 承接630件/日向内辐射',
         'nodes': [(f'区{i+1}', np.cos(i*np.pi/5)*0.30 + 0.55, np.sin(i*np.pi/5)*0.25 + 0.38, 63) for i in range(10)],
         'facs': [('F04(东门接驳*)', 0.15, 0.38, '接驳', COLORS['orange'])],
         'links': [(i, 0) for i in range(10)]}
    ]

    for idx, c in enumerate(comms_data):
        row = idx // 3
        col = idx % 3
        ax = fig.add_subplot(gs[row, col])
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        ax.axis('off')
        
        # Border
        rect = patches.FancyBboxPatch((0.02, 0.02), 0.98, 0.96,
                                      boxstyle="round,pad=0.01,rounding_size=0.02",
                                      facecolor='#FAFAFA', edgecolor='#B0BEC5', lw=1.2)
        ax.add_patch(rect)
        
        # Titles safely placed at the very top
        ax.text(0.5, 0.95, c['name'], ha='center', va='top', fontsize=10.5, fontweight='bold', color=COLORS['dark_navy'])
        ax.text(0.5, 0.88, f"模式: {c['type']}", ha='center', va='top', fontsize=9, fontweight='bold', color=COLORS['bluish_green'])
        ax.text(0.5, 0.81, c['sub'], ha='center', va='top', fontsize=8, color='#546E7A')
        
        # Draw Links
        for d_idx, f_idx in c['links']:
            dx, dy = c['nodes'][d_idx][1], c['nodes'][d_idx][2]
            fx, fy = c['facs'][f_idx][1], c['facs'][f_idx][2]
            ax.plot([fx, dx], [fy, dy], color='#90A4AE', lw=1.0, linestyle=':', zorder=1)
            
        # Draw Demand Nodes
        for d in c['nodes']:
            d_name, dx, dy, d_q = d[0], d[1], d[2], d[3]
            ax.scatter(dx, dy, s=60, color=COLORS['light_gray'], edgecolor='black', lw=0.8, zorder=2)
            ax.text(dx, dy - 0.04, d_name, ha='center', va='top', fontsize=7, color='#37474F')

        # Draw Facilities
        for f in c['facs']:
            f_name, fx, fy, f_type, f_col = f[0], f[1], f[2], f[3], f[4]
            marker = 's' if '柜' in f_type else ('^' if '驿' in f_type else 'D')
            ax.scatter(fx, fy, s=140, color=f_col, edgecolor='black', marker=marker, lw=1.5, zorder=3)
            ax.text(fx, fy + 0.045, f_name, ha='center', va='bottom', fontsize=8, fontweight='bold', color=f_col)

    # 6th Subplot: Summary Legend and Typology Matrix
    ax_legend = fig.add_subplot(gs[1, 2])
    ax_legend.axis('off')
    rect_l = patches.FancyBboxPatch((0.02, 0.02), 0.98, 0.96,
                                    boxstyle="round,pad=0.01,rounding_size=0.02",
                                    facecolor='#ECEFF1', edgecolor=COLORS['blue'], lw=1.5)
    ax_legend.add_patch(rect_l)
    
    ax_legend.text(0.5, 0.93, '五社区网络拓扑图例与分类模式总结', ha='center', va='top', fontsize=10.5, fontweight='bold', color=COLORS['dark_navy'])
    
    legend_items = [
        ('○ 住宅需求节点', '灰底黑边圆点，代表社区微观楼栋或组团'),
        ('■ 现有智能快递柜', '蓝底方块，如梅园C01-F01、鹿鸣苑C02-F01/F02'),
        ('▲ 社区驿站/代收点', '青绿三角，如梅园F03、天华园F03/F04'),
        ('■ 新增智能快递柜 (*)', '红底加粗方块，如鹿鸣苑C02-F03 (新增104格)'),
        ('◆ 入口级无人接驳点 (*)', '橙黄菱形，如亦城茗苑C04-F05、听涛雅苑C05-F04'),
        ('--- 服务归属连线', '细虚线连接需求节点与承担其配送的末端设施')
    ]
    
    y_pos = 0.80
    for sym, desc in legend_items:
        ax_legend.text(0.06, y_pos, sym, ha='left', va='center', fontsize=9, fontweight='bold', color=COLORS['dark_navy'])
        ax_legend.text(0.06, y_pos - 0.04, desc, ha='left', va='center', fontsize=7.5, color='#455A64')
        y_pos -= 0.12

    save_fig(fig, 'fig4_3_five_communities_network_topology')


# ==============================================================================
# Fig 4-4: Facility Capacity Configuration & Optimization Evaluation
# ==============================================================================
def draw_fig4_4():
    fig = plt.figure(figsize=(13, 8))
    gs = GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.25)
    
    # Subplot A: 表4-3 主要设施有效日容量 vs 实际分配需求量
    ax1 = fig.add_subplot(gs[0, 0])
    fac_labels = [
        '梅园 F01\n(东柜1)', '梅园 F03\n(代收点)',
        '鹿鸣 F01\n(北柜1)', '鹿鸣 F02\n(北柜2)', '鹿鸣 F03\n(新增柜*)',
        '天华 F01\n(柜)', '天华 F03\n(驿站)', '天华 F04\n(菜鸟)'
    ]
    caps = [126, 300, 126, 84, 156, 126, 300, 300]
    assigned = [84.0, 79.2, 46.8, 66.0, 147.0, 91.2, 68.4, 92.4]
    
    x = np.arange(len(fac_labels))
    w = 0.38
    r1 = ax1.bar(x - w/2, caps, w, label='有效日容量 $C_j$ (件/日)', color=COLORS['sky_blue'], edgecolor='black', alpha=0.85)
    r2 = ax1.bar(x + w/2, assigned, w, label='分配需求量 $Q_j$ (件/日)', color=COLORS['vermillion'], edgecolor='black', alpha=0.85)
    
    ax1.set_ylabel('快件量 (件/日)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(fac_labels, fontsize=8)
    ax1.set_title('(a) 自提设施有效容量与分配快件量对比 (表 4-3)', fontsize=10.5, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax1.legend(loc='upper right', fontsize=8.5)
    
    # Label assigned loads
    for r in r2:
        ax1.text(r.get_x() + r.get_width()/2, r.get_height() + 5, f'{r.get_height():.1f}', ha='center', va='bottom', fontsize=7.5)

    # Subplot B: 表4-3 设施容量利用率 (Utilizations)
    ax2 = fig.add_subplot(gs[0, 1])
    utils = [a / c * 100 for a, c in zip(assigned, caps)]
    cols = [COLORS['vermillion'] if u > 85 else (COLORS['orange'] if u > 60 else COLORS['bluish_green']) for u in utils]
    
    bars = ax2.bar(x, utils, 0.55, color=cols, edgecolor='black', alpha=0.85)
    ax2.axhline(80, color=COLORS['orange'], linestyle='--', lw=1.5, label='高负荷警戒线 (80%)')
    ax2.axhline(90, color=COLORS['vermillion'], linestyle='--', lw=1.5, label='极高负荷线 (90%)')
    
    ax2.set_ylabel('容量利用率 (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(fac_labels, fontsize=8)
    ax2.set_title('(b) 设施容量利用率分布 (鹿鸣苑新增柜达 94.2%)', fontsize=10.5, fontweight='bold')
    ax2.set_ylim(0, 110)
    ax2.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax2.legend(loc='upper left', fontsize=8.5)
    
    for b in bars:
        ax2.text(b.get_x() + b.get_width()/2, b.get_height() + 2, f'{b.get_height():.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')

    # Subplot C: 表4-4 五社区日均需求 vs 现有有效容量 vs 优化后有效容量
    ax3 = fig.add_subplot(gs[1, 0])
    c_names = ['梅园小区', '鹿鸣苑', '天华园二里', '亦城茗苑', '听涛雅苑']
    demands = [163.2, 259.8, 252.0, 1284.6, 630.0]
    exist_caps = [426, 210, 852, 0, 0]
    opt_caps = [426, 366, 852, 1284.6, 630.0]  # C04, C05 use transfer capacity
    
    x_c = np.arange(len(c_names))
    w_c = 0.26
    ax3.bar(x_c - w_c, demands, w_c, label='基准日需求量', color='#757575', edgecolor='black', alpha=0.8)
    ax3.bar(x_c, exist_caps, w_c, label='现状有效容量', color='#B0BEC5', edgecolor='black', alpha=0.8)
    ax3.bar(x_c + w_c, opt_caps, w_c, label='优化后设施/接驳总能力', color=COLORS['bluish_green'], edgecolor='black', alpha=0.85)
    
    ax3.set_ylabel('件/日')
    ax3.set_xticks(x_c)
    ax3.set_xticklabels(c_names)
    ax3.set_title('(c) 五社区需求量与优化前后末端承载能力对比 (表 4-4)', fontsize=10.5, fontweight='bold')
    ax3.grid(True, linestyle='--', alpha=0.5, axis='y')
    ax3.legend(loc='upper right', fontsize=8.5)
    
    # Highlight capacity deficit in LuMingYuan
    ax3.annotate('现状缺口49.8件\n优化后增至366件', xy=(1, 210), xytext=(1, 550),
                 arrowprops=dict(arrowstyle="->", color=COLORS['vermillion'], lw=1.8),
                 ha='center', fontsize=8.5, fontweight='bold', color=COLORS['vermillion'])

    # Subplot D: 优化后平均服务距离 (xlim set to 490 to prevent text clipping)
    ax4 = fig.add_subplot(gs[1, 1])
    avg_d = [192.5, 166.2, 118.2, 327.4, 377.7]
    y_pos = np.arange(len(c_names))
    
    bars_h = ax4.barh(y_pos, avg_d, 0.5, color=COLORS['blue'], edgecolor='black', alpha=0.85)
    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(c_names)
    ax4.set_xlim(0, 490)  # Extended limit prevents text clipping!
    ax4.set_xlabel('优化后需求加权平均服务距离 (m)')
    ax4.set_title('(d) 五社区优化后平均服务距离 (均在允许阈值内 100% 覆盖)', fontsize=10.5, fontweight='bold')
    ax4.grid(True, linestyle='--', alpha=0.5, axis='x')
    
    for b in bars_h:
        ax4.text(b.get_width() + 8, b.get_y() + b.get_height()/2, f'{b.get_width():.1f} m (覆盖100%)', ha='left', va='center', fontsize=8.5, fontweight='bold')

    save_fig(fig, 'fig4_4_facility_capacity_and_optimization')


if __name__ == '__main__':
    print('Starting publication figures generation for Chapter 4...')
    draw_fig4_1()
    draw_fig4_2()
    draw_fig4_3()
    draw_fig4_4()
    print('All Chapter 4 figures generated successfully.')
