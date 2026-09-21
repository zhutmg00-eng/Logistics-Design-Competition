# -*- coding: utf-8 -*-
"""
Chapter 7: Autonomous Delivery and Human Collaborative Operation Optimization
Publication-Grade Figures Generator (Nature/SCI Standard, Okabe-Ito Colors, 300 DPI + SVG)
Refined version: Eliminates missing glyphs (bullets, ceilings, double arrows) and layout overlaps.
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# --- Matplotlib Global Style Configuration ---
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 9.5
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.titlesize'] = 11
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.titlesize'] = 13

# --- Okabe-Ito Color Palette (Colorblind Friendly) ---
COLOR_BLACK = '#000000'
COLOR_ORANGE = '#E69F00'
COLOR_SKY_BLUE = '#56B4E9'
COLOR_BLUISH_GREEN = '#009E73'
COLOR_YELLOW = '#F0E442'
COLOR_BLUE = '#0072B2'
COLOR_VERMILLION = '#D55E00'
COLOR_REDDISH_PURPLE = '#CC79A7'
COLOR_GRAY = '#7F7F7F'
COLOR_LIGHT_GRAY = '#E0E0E0'
COLOR_DARK_GRAY = '#333333'
COLOR_CARD_BG = '#F8FAFC'

# Output directories
OUTPUT_DIRS = [
    os.path.join('docs', 'images', 'operation'),
    os.path.join('demo', 'static', 'images', 'operation')
]

for d in OUTPUT_DIRS:
    os.makedirs(d, exist_ok=True)

def save_fig(fig, base_name):
    for d in OUTPUT_DIRS:
        png_path = os.path.join(d, f"{base_name}.png")
        svg_path = os.path.join(d, f"{base_name}.svg")
        fig.savefig(png_path, dpi=300, bbox_inches='tight')
        fig.savefig(svg_path, format='svg', bbox_inches='tight')
        print(f"Saved: {png_path} and {svg_path}")
    plt.close(fig)


# ==============================================================================
# Figure 7-1: Framework and Collaborative Workflow Swimlane
# ==============================================================================
def generate_fig7_1():
    print("Generating Fig 7-1: Framework and Swimlane...")
    fig = plt.figure(figsize=(15, 10.5))
    gs = fig.add_gridspec(2, 1, height_ratios=[1.1, 1.25], hspace=0.30)

    # --- Panel (a): Optimization Framework ---
    ax_a = fig.add_subplot(gs[0])
    ax_a.set_title("(a) 基于网络模型输出的无人配送与人工协同运行优化总体框架", loc='left', fontweight='bold', pad=12)
    ax_a.axis('off')

    stages = [
        ("第4章网络输出", "- 设施选址结果\n- 住宅服务归属\n- 设施包裹负荷\n- 节点供货连接", COLOR_GRAY),
        ("加权图网络构建", "- 336条道路边\n- 路网节点挂接\n- 道路限速 (1.5/1.0m/s)\n- 通行方向控制", COLOR_BLUE),
        ("最短通行时间矩阵", "- Dijkstra 算法\n- 最短通行时间 T\n- 对应行驶距离 D\n- 路网可达性检验", COLOR_SKY_BLUE),
        ("共同配送路径优化", "- 字典序两阶段优化\n- Stage 1: 最小批次 K*\n- Stage 2: 最小时间\n- 450件单车载荷限制", COLOR_ORANGE),
        ("运力与班次配置", "- 静态任务编排\n- 动态滚动波次发车\n- 5辆车基准驻点\n- 8h工作日余量核算", COLOR_BLUISH_GREEN),
        ("资源与协同保障", "- 人车任务分工\n- 智能柜动态库存\n- 集中补能与备用换电\n- 8类异常处置兜底", COLOR_VERMILLION)
    ]

    box_w, box_h = 0.138, 0.65
    spacing = (1.0 - len(stages) * box_w) / (len(stages) + 1)

    for i, (st_title, st_desc, st_color) in enumerate(stages):
        x = spacing + i * (box_w + spacing)
        y = 0.18
        # Card box
        rect = patches.FancyBboxPatch((x, y), box_w, box_h, boxstyle="round,pad=0.015,rounding_size=0.025",
                                     linewidth=1.8, edgecolor=st_color, facecolor=COLOR_CARD_BG, transform=ax_a.transAxes)
        ax_a.add_patch(rect)
        # Header banner
        rect_hdr = patches.FancyBboxPatch((x, y + box_h - 0.16), box_w, 0.16, boxstyle="round,pad=0.015,rounding_size=0.02",
                                         linewidth=0, facecolor=st_color, transform=ax_a.transAxes)
        ax_a.add_patch(rect_hdr)
        ax_a.text(x + box_w / 2, y + box_h - 0.08, f"Step {i+1}\n{st_title}", color='white', fontweight='bold',
                  ha='center', va='center', fontsize=9.2, transform=ax_a.transAxes)
        # Body text
        ax_a.text(x + 0.012, y + 0.22, st_desc, color=COLOR_DARK_GRAY, fontsize=8.2, va='center',
                  linespacing=1.45, transform=ax_a.transAxes)
        # Arrow to next
        if i < len(stages) - 1:
            arr_x = x + box_w + spacing * 0.15
            arr_w = spacing * 0.7
            ax_a.annotate('', xy=(arr_x + arr_w, y + box_h / 2), xytext=(arr_x, y + box_h / 2),
                          arrowprops=dict(arrowstyle="-|>", color=COLOR_DARK_GRAY, lw=2.0, mutation_scale=14),
                          xycoords='axes fraction')

    # Feedback loop arrow (Step 6 -> Step 4)
    ax_a.annotate('动态扰动/异常重规划反馈 (Re-optimization)', xy=(spacing + 3.5 * (box_w + spacing), 0.12),
                  xytext=(spacing + 5.5 * (box_w + spacing), 0.12),
                  arrowprops=dict(arrowstyle="->", color=COLOR_VERMILLION, lw=1.6, ls='--', connectionstyle="arc3,rad=-0.18"),
                  ha='center', va='top', fontsize=8.5, color=COLOR_VERMILLION, fontweight='bold', xycoords='axes fraction')

    # --- Panel (b): Swimlane Diagram ---
    ax_b = fig.add_subplot(gs[1])
    ax_b.set_title("(b) 无人车—人工配送员—智能柜多主体协同作业流程泳道图", loc='left', fontweight='bold', pad=12)
    ax_b.axis('off')

    lanes = [
        ("接驳点 / 驿站", COLOR_BLUE, 0.75),
        ("无人配送车 (X3)", COLOR_ORANGE, 0.50),
        ("智能快递柜 / 楼栋", COLOR_BLUISH_GREEN, 0.25),
        ("人工配送员 (弹性)", COLOR_VERMILLION, 0.00)
    ]
    lane_h = 0.23

    # Draw swimlanes
    for lname, lcolor, ly in lanes:
        rect = patches.Rectangle((0.02, ly), 0.96, lane_h, linewidth=1.2, edgecolor=lcolor,
                                 facecolor=lcolor, alpha=0.07, transform=ax_b.transAxes)
        ax_b.add_patch(rect)
        # Lane label
        lbl_rect = patches.Rectangle((0.02, ly), 0.13, lane_h, linewidth=1.2, edgecolor=lcolor,
                                     facecolor=lcolor, transform=ax_b.transAxes)
        ax_b.add_patch(lbl_rect)
        ax_b.text(0.085, ly + lane_h / 2, lname, color='white', fontweight='bold', ha='center', va='center',
                  fontsize=9.2, transform=ax_b.transAxes)

    # Swimlane nodes with adjusted non-overlapping coordinates
    nodes = [
        # Lane 1 (Hub/Station)
        ("N1", 0.20, 0.75 + lane_h/2, "上游包裹到达\n任务汇集分拣", COLOR_BLUE),
        ("N2", 0.39, 0.75 + lane_h/2, "批次装载触发\n(达阈值/超时)", COLOR_BLUE),
        # Lane 2 (Autonomous Vehicle)
        ("N3", 0.53, 0.50 + lane_h/2, "CVRP最优路线\n巡航批量运输", COLOR_ORANGE),
        ("N4", 0.70, 0.50 + lane_h/2, "末端交接/投柜\n状态实时回传", COLOR_ORANGE),
        ("N5", 0.89, 0.50 + lane_h/2, "返回接驳点\n换电/补能/待命", COLOR_ORANGE),
        # Lane 3 (Locker / Building)
        ("N6", 0.70, 0.25 + lane_h/2, "智能柜暂存\n居民就近自提", COLOR_BLUISH_GREEN),
        # Lane 4 (Courier / Flexible)
        ("N7", 0.70, 0.00 + lane_h/2, "送货上门/特殊群体\n最后100m柔性交付", COLOR_VERMILLION),
        ("N8", 0.35, 0.00 + lane_h/2, "异常接管/受阻重置\n兜底保障回流", COLOR_VERMILLION)
    ]

    node_dict = {}
    for nid, nx, ny, ntext, ncolor in nodes:
        w, h = 0.125, 0.155
        rect = patches.FancyBboxPatch((nx - w/2, ny - h/2), w, h, boxstyle="round,pad=0.015,rounding_size=0.02",
                                     linewidth=1.5, edgecolor=ncolor, facecolor='white', transform=ax_b.transAxes)
        ax_b.add_patch(rect)
        ax_b.text(nx, ny, ntext, ha='center', va='center', fontsize=8.0, color=COLOR_DARK_GRAY,
                  fontweight='bold', transform=ax_b.transAxes)
        node_dict[nid] = (nx, ny)

    # Workflow arrows
    flow_arrows = [
        ("N1", "N2", "->", "", (0.295, 0.88)),
        ("N2", "N3", "->", "装载出车", (0.46, 0.73)),
        ("N3", "N4", "->", "按序到达", (0.615, 0.64)),
        ("N4", "N6", "->", "自提件投柜 (1-alpha)", (0.71, 0.44)),
        ("N4", "N7", "->", "上门件交接 (alpha)", (0.77, 0.23)),
        ("N4", "N5", "->", "任务完成", (0.795, 0.64)),
        ("N6", "N8", "-->", "满柜溢流", (0.50, 0.26)),
        ("N3", "N8", "-->", "车辆/道路故障", (0.42, 0.40)),
        ("N8", "N2", "-->", "任务重排回流", (0.31, 0.50))
    ]

    for start_id, end_id, style, text, txt_pos in flow_arrows:
        sx, sy = node_dict[start_id]
        ex, ey = node_dict[end_id]
        ls = '--' if '--' in style else '-'
        col = COLOR_VERMILLION if '--' in style else COLOR_DARK_GRAY
        ax_b.annotate('', xy=(ex, ey), xytext=(sx, sy),
                      arrowprops=dict(arrowstyle="-|>", color=col, lw=1.6, ls=ls, mutation_scale=12),
                      xycoords='axes fraction')
        ax_b.text(txt_pos[0], txt_pos[1], text, fontsize=7.6, color=col, fontweight='bold', ha='center', va='center', transform=ax_b.transAxes)

    # Legend
    legend_elements = [
        patches.Patch(facecolor='white', edgecolor=COLOR_DARK_GRAY, lw=1.5, label='正常业务流 (Normal Flow)'),
        patches.Patch(facecolor='white', edgecolor=COLOR_VERMILLION, lw=1.5, linestyle='--', label='异常回流/柔性兜底 (Contingency Loop)')
    ]
    ax_b.legend(handles=legend_elements, loc='upper right', framealpha=0.95, edgecolor=COLOR_LIGHT_GRAY)

    save_fig(fig, 'fig7_1_collaborative_framework_and_swimlane')


# ==============================================================================
# Figure 7-2: Decentralized vs Joint Distribution & C02 Dijkstra Heatmap
# ==============================================================================
def generate_fig7_2():
    print("Generating Fig 7-2: Decentralized vs Joint & C02 Heatmap...")
    fig = plt.figure(figsize=(15, 6))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 0.95, 1.25], wspace=0.28)

    # --- Panel (a): Decentralized vs Joint Distribution Mechanism ---
    ax_a = fig.add_subplot(gs[0])
    ax_a.set_title("(a) 多主体分散配送 vs 共同配送运行机制", loc='left', fontweight='bold', pad=10)
    ax_a.axis('off')

    # Left: Decentralized
    ax_a.text(0.24, 0.93, "分散独立配送模式 (As-Is)", color=COLOR_VERMILLION, fontweight='bold', ha='center', transform=ax_a.transAxes)
    rect_dec = patches.Rectangle((0.02, 0.05), 0.44, 0.83, linewidth=1.5, edgecolor=COLOR_VERMILLION,
                                 facecolor='#FFF5F5', transform=ax_a.transAxes)
    ax_a.add_patch(rect_dec)
    
    # 3 companies entering independently
    companies = [("企业 A", COLOR_VERMILLION, 0.72), ("企业 B", COLOR_ORANGE, 0.52), ("企业 C", COLOR_REDDISH_PURPLE, 0.32)]
    for cname, ccol, cy in companies:
        ax_a.text(0.06, cy, cname, color=ccol, fontweight='bold', fontsize=8.5, transform=ax_a.transAxes)
        # Arrow into community
        ax_a.annotate('', xy=(0.28, cy), xytext=(0.17, cy),
                      arrowprops=dict(arrowstyle="-|>", color=ccol, lw=2.0, mutation_scale=11),
                      xycoords='axes fraction')
        ax_a.text(0.30, cy, "独立路线\n重复进区", color=ccol, fontsize=7.5, va='center', transform=ax_a.transAxes)
    
    ax_a.text(0.24, 0.13, "重复运行里程:\n" + r"$L_{\mathrm{dup}} = \sum_{e} (K_e - 1) l_e$" + "\n装载率低下 · 道路拥堵",
              color=COLOR_VERMILLION, fontsize=8.2, ha='center', va='center', transform=ax_a.transAxes)

    # Right: Joint
    ax_a.text(0.74, 0.93, "共同配送协同模式 (To-Be)", color=COLOR_BLUISH_GREEN, fontweight='bold', ha='center', transform=ax_a.transAxes)
    rect_jnt = patches.Rectangle((0.52, 0.05), 0.45, 0.83, linewidth=1.5, edgecolor=COLOR_BLUISH_GREEN,
                                 facecolor='#F0FDF4', transform=ax_a.transAxes)
    ax_a.add_patch(rect_jnt)

    # Aggregated task pool
    rect_pool = patches.FancyBboxPatch((0.55, 0.48), 0.39, 0.33, boxstyle="round,pad=0.015,rounding_size=0.02",
                                       linewidth=1.2, edgecolor=COLOR_BLUE, facecolor='white', transform=ax_a.transAxes)
    ax_a.add_patch(rect_pool)
    ax_a.text(0.745, 0.73, "末端任务集约池\n(Unified Task Pool)", color=COLOR_BLUE, fontweight='bold', ha='center', fontsize=8.5, transform=ax_a.transAxes)
    ax_a.text(0.745, 0.58, "统一编码 · 责任保留\n共同排程 · 载荷优化", color=COLOR_DARK_GRAY, ha='center', fontsize=7.8, transform=ax_a.transAxes)

    # Unified route arrow
    ax_a.annotate('', xy=(0.745, 0.26), xytext=(0.745, 0.46),
                  arrowprops=dict(arrowstyle="-|>", color=COLOR_BLUISH_GREEN, lw=3.0, mutation_scale=14),
                  xycoords='axes fraction')
    ax_a.text(0.745, 0.33, "集约化单一车次", color=COLOR_BLUISH_GREEN, fontweight='bold', ha='center', fontsize=8.2, transform=ax_a.transAxes)
    ax_a.text(0.745, 0.13, "消除跨主体重复进区\n高装载率 (90%~98%)\n道路资源集约化",
              color=COLOR_BLUISH_GREEN, fontsize=8.2, ha='center', va='center', transform=ax_a.transAxes)

    # --- Panel (b): C02 Lumingyuan Spatial Node Mapping ---
    ax_b = fig.add_subplot(gs[1])
    ax_b.set_title("(b) 鹿鸣苑 (C02) 节点与路网拓扑映射", loc='left', fontweight='bold', pad=10)
    
    nodes_c02 = {
        'F01/02 (北门)': (0.50, 0.92, COLOR_ORANGE, 's', 120),
        'F03 (3号楼柜)': (0.52, 0.50, COLOR_BLUISH_GREEN, 's', 120),
        'D01': (0.36, 0.80, COLOR_BLUE, 'o', 80),
        'D02': (0.35, 0.32, COLOR_BLUE, 'o', 80),
        'D03': (0.68, 0.35, COLOR_BLUE, 'o', 80),
        'D04': (0.26, 0.65, COLOR_BLUE, 'o', 80),
        'D05': (0.74, 0.72, COLOR_BLUE, 'o', 80),
        'D06': (0.28, 0.48, COLOR_BLUE, 'o', 80),
        'D07': (0.50, 0.14, COLOR_BLUE, 'o', 80)
    }

    edges_c02 = [
        ('F01/02 (北门)', 'D01'), ('F01/02 (北门)', 'D05'), ('D01', 'D04'),
        ('D04', 'D06'), ('D05', 'F03 (3号楼柜)'), ('D06', 'F03 (3号楼柜)'),
        ('F03 (3号楼柜)', 'D02'), ('F03 (3号楼柜)', 'D03'),
        ('D02', 'D07'), ('D03', 'D07')
    ]

    for n1, n2 in edges_c02:
        x1, y1 = nodes_c02[n1][0], nodes_c02[n1][1]
        x2, y2 = nodes_c02[n2][0], nodes_c02[n2][1]
        ax_b.plot([x1, x2], [y1, y2], color=COLOR_LIGHT_GRAY, lw=2.5, zorder=1)

    for nname, (nx, ny, ncol, nmarker, nsize) in nodes_c02.items():
        ax_b.scatter(nx, ny, c=ncol, marker=nmarker, s=nsize, edgecolors=COLOR_BLACK, lw=1.2, zorder=3)
        offset_y = 0.05 if ny < 0.85 else -0.05
        ax_b.text(nx, ny + offset_y, nname, fontsize=8.0, ha='center', va='center', fontweight='bold',
                  bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.85, edgecolor='none'))

    ax_b.set_xlim(0.12, 0.88)
    ax_b.set_ylim(0.04, 0.99)
    ax_b.set_xlabel("相对经度坐标 (X)")
    ax_b.set_ylabel("相对纬度坐标 (Y)")
    ax_b.grid(True, linestyle=':', alpha=0.4)

    # --- Panel (c): C02 Dijkstra Travel Time Matrix Heatmap ---
    ax_c = fig.add_subplot(gs[2])
    ax_c.set_title("(c) 鹿鸣苑节点间最短通行时间热力矩阵 (Dijkstra)", loc='left', fontweight='bold', pad=10)

    labels = ['F(接驳)', 'D01', 'D02', 'D03', 'D04', 'D05', 'D06', 'D07']
    base_dist = np.array([
        [0.0, 1.8, 4.5, 4.2, 2.6, 2.1, 3.4, 5.8],
        [1.8, 0.0, 3.8, 3.9, 1.5, 2.4, 2.8, 5.1],
        [4.5, 3.8, 0.0, 1.4, 2.9, 4.6, 1.9, 1.8],
        [4.2, 3.9, 1.4, 0.0, 3.2, 3.7, 2.2, 1.6],
        [2.6, 1.5, 2.9, 3.2, 0.0, 3.1, 1.6, 4.2],
        [2.1, 2.4, 4.6, 3.7, 3.1, 0.0, 3.5, 5.2],
        [3.4, 2.8, 1.9, 2.2, 1.6, 3.5, 0.0, 3.1],
        [5.8, 5.1, 1.8, 1.6, 4.2, 5.2, 3.1, 0.0]
    ])

    im = ax_c.imshow(base_dist, cmap='YlGnBu', vmin=0, vmax=6.0)
    cbar = plt.colorbar(im, ax=ax_c, fraction=0.046, pad=0.04)
    cbar.set_label("最短路网通行时间 $t_{ij}$ (min)", fontsize=8.5)

    ax_c.set_xticks(range(len(labels)))
    ax_c.set_yticks(range(len(labels)))
    ax_c.set_xticklabels(labels, fontsize=8.5)
    ax_c.set_yticklabels(labels, fontsize=8.5)

    for i in range(len(labels)):
        for j in range(len(labels)):
            val = base_dist[i, j]
            text_color = 'white' if val > 3.8 else 'black'
            ax_c.text(j, i, f"{val:.1f}", ha='center', va='center', color=text_color, fontsize=7.8)

    save_fig(fig, 'fig7_2_decentralized_vs_joint_and_c02_dijkstra')


# ==============================================================================
# Figure 7-3: Routing Batches, Loads, and Sensitivity Analysis (2x2 Grid)
# ==============================================================================
def generate_fig7_3():
    print("Generating Fig 7-3: Routing Batches, Loads, and Sensitivity...")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    plt.subplots_adjust(hspace=0.34, wspace=0.26)

    # --- Panel (a): Normal vs Peak Batches Comparison (Table 5-1) ---
    ax_a = axes[0, 0]
    ax_a.set_title("(a) 五社区普通日与高峰日无人配送批次数对比", loc='left', fontweight='bold', pad=10)
    
    comms = ['梅园 (C01)', '鹿鸣苑 (C02)', '天华园 (C03)', '亦城茗苑 (C04)', '听涛雅苑 (C05)']
    normal_batches = [1, 1, 1, 3, 2]
    peak_batches = [1, 2, 2, 7, 3]
    
    x = np.arange(len(comms))
    width = 0.35

    rects1 = ax_a.bar(x - width/2, normal_batches, width, label='普通日批次数 (Normal: 8批)', color=COLOR_SKY_BLUE, edgecolor=COLOR_BLACK, lw=0.8)
    rects2 = ax_a.bar(x + width/2, peak_batches, width, label='高峰日批次数 (Peak: 15批)', color=COLOR_ORANGE, edgecolor=COLOR_BLACK, lw=0.8)

    ax_a.set_ylabel("配送批次数 (Batches)")
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(comms, rotation=15, ha='right')
    ax_a.set_ylim(0, 8.8)
    ax_a.grid(True, axis='y', linestyle=':', alpha=0.5)
    ax_a.legend(loc='upper left', framealpha=0.9)

    # Bar labels
    for rect in rects1:
        h = rect.get_height()
        ax_a.text(rect.get_x() + rect.get_width()/2., h + 0.15, f"{int(h)}批", ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    for rect in rects2:
        h = rect.get_height()
        ax_a.text(rect.get_x() + rect.get_width()/2., h + 0.15, f"{int(h)}批", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color=COLOR_VERMILLION)

    # Annotation for C04 shifted left and up to avoid collision
    ax_a.annotate('C04 规模翻倍\n批次增至 7 批', xy=(3 + width/2, 7.2), xytext=(2.2, 7.8),
                  arrowprops=dict(arrowstyle="->", color=COLOR_VERMILLION, lw=1.5),
                  fontsize=8.5, fontweight='bold', color=COLOR_VERMILLION)

    # --- Panel (b): Normal Day 8 Batches Vehicle Load Rate (Table 5-2) ---
    ax_b = axes[0, 1]
    ax_b.set_title("(b) 普通日各配送批次车辆装载率与容量基准线", loc='left', fontweight='bold', pad=10)

    batches = ['C01-R1', 'C02-R1', 'C03-R1', 'C04-R1', 'C04-R2', 'C04-R3', 'C05-R1', 'C05-R2']
    load_rates = [36.3, 57.7, 56.0, 96.9, 90.4, 98.1, 98.0, 42.0]
    bar_colors = [COLOR_SKY_BLUE if lr < 70 else COLOR_BLUISH_GREEN for lr in load_rates]

    x_b = np.arange(len(batches))
    bars = ax_b.bar(x_b, load_rates, color=bar_colors, edgecolor=COLOR_BLACK, lw=0.8, width=0.55)
    ax_b.axhline(100.0, color=COLOR_VERMILLION, linestyle='--', lw=1.8, label='额定装载容量上限 (100% = 450件)')
    ax_b.axhline(np.mean(load_rates), color=COLOR_BLUE, linestyle=':', lw=1.6, label=f'全网平均装载率 ({np.mean(load_rates):.1f}%)')

    ax_b.set_ylabel("车辆装载率 (%)")
    ax_b.set_ylim(0, 118)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels(batches, rotation=25, ha='right')
    ax_b.grid(True, axis='y', linestyle=':', alpha=0.5)
    ax_b.legend(loc='lower right', framealpha=0.9, fontsize=8.5)

    for bar, lr in zip(bars, load_rates):
        ax_b.text(bar.get_x() + bar.get_width()/2., lr + 2.0, f"{lr:.1f}%", ha='center', va='bottom', fontsize=8.2, fontweight='bold')

    # --- Panel (c): C04 Peak Day 7 Batches Load vs 450 Capacity (Table 5-3) ---
    ax_c = axes[1, 0]
    ax_c.set_title("(c) 亦城茗苑 (C04) 高峰日 7 批次载货量与不可拆分性验证", loc='left', fontweight='bold', pad=10)

    c04_batches = ['R1 (D01)', 'R2 (D02)', 'R3 (D05,09,03)', 'R4 (D06,04)', 'R5 (D07)', 'R6 (D08)', 'R7 (D10,11,12)']
    c04_loads = [380.4, 392.4, 445.2, 280.8, 322.8, 327.6, 420.0]

    x_c = np.arange(len(c04_batches))
    bars_c = ax_c.bar(x_c, c04_loads, color=COLOR_ORANGE, edgecolor=COLOR_BLACK, lw=0.8, width=0.55)
    ax_c.axhline(450.0, color=COLOR_VERMILLION, linestyle='--', lw=1.8, label='X3 车辆额定容量 (450件)')

    ax_c.set_ylabel("单批次装载件数 (件)")
    ax_c.set_ylim(0, 520)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(c04_batches, rotation=25, ha='right')
    ax_c.grid(True, axis='y', linestyle=':', alpha=0.5)
    ax_c.legend(loc='upper right', framealpha=0.9)

    for bar, ld in zip(bars_c, c04_loads):
        ax_c.text(bar.get_x() + bar.get_width()/2., ld + 8.0, f"{ld:.1f}件", ha='center', va='bottom', fontsize=8.2, fontweight='bold')

    # Theoretical vs Actual annotation (without missing ceiling glyphs)
    ax_c.text(0.04, 0.85, "理论总需求: 2569.2 件\n理论下界: ceil(2569.2 / 450) = 6 批\n实际求解: 7 批 (因大节点单体不可拆分)",
              transform=ax_c.transAxes, fontsize=8.5, fontweight='bold',
              bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor=COLOR_VERMILLION, lw=1.2))

    # --- Panel (d): Vehicle Capacity Sensitivity Analysis (Table 5-4) ---
    ax_d = axes[1, 1]
    ax_d.set_title("(d) 车辆单次容量灵敏度分析 (400件 vs 450件 vs 500件)", loc='left', fontweight='bold', pad=10)

    caps = [400, 450, 500]
    norm_b = [9, 8, 8]
    peak_b = [17, 15, 14]
    peak_km = [17.632, 16.529, 16.082]

    ax_d1 = ax_d
    ax_d2 = ax_d.twinx()

    line1, = ax_d1.plot(caps, peak_b, marker='o', color=COLOR_VERMILLION, lw=2.0, ms=7, label='高峰日批次数 (Batches)')
    line2, = ax_d1.plot(caps, norm_b, marker='s', color=COLOR_SKY_BLUE, lw=2.0, ms=7, label='普通日批次数 (Batches)')
    line3, = ax_d2.plot(caps, peak_km, marker='^', color=COLOR_BLUISH_GREEN, lw=2.0, ms=7, ls='--', label='高峰日总里程 (km)')

    ax_d1.set_xlabel(r"车辆额定容量 $Q_{\mathrm{veh}}$ (件/车次)")
    ax_d1.set_ylabel("配送批次数 (Batches)")
    ax_d2.set_ylabel("高峰日总行驶里程 (km)")

    ax_d1.set_xticks(caps)
    ax_d1.set_ylim(5, 20)
    ax_d2.set_ylim(15.0, 18.5)
    ax_d1.grid(True, linestyle=':', alpha=0.5)

    # Combined legend
    lines = [line1, line2, line3]
    labels_d = [l.get_label() for l in lines]
    ax_d1.legend(lines, labels_d, loc='upper right', framealpha=0.9, fontsize=8.5)

    # Note (without missing double arrow)
    ax_d.text(0.05, 0.15, "400->450件: 高峰批次 -11.8%, 里程 -6.3% (边际收益显著)\n450->500件: 高峰批次 -6.7%, 里程 -2.7% (边际改善衰减)\n==> 确定 450件 为系统稳健最优基准容量",
              transform=ax_d.transAxes, fontsize=8.0, fontweight='bold',
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#F0FDF4', edgecolor=COLOR_BLUISH_GREEN, lw=1.0))

    save_fig(fig, 'fig7_3_routing_batches_loads_and_sensitivity')


# ==============================================================================
# Figure 7-4: C04 Spatial Routes, Workload & Contingency Loop
# ==============================================================================
def generate_fig7_4():
    print("Generating Fig 7-4: C04 Routes, Workload, and Contingency...")
    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.1, 1.0], hspace=0.32, wspace=0.26)

    # --- Panel (a): C04 Normal Day 3 Optimal Routes ---
    ax_a = fig.add_subplot(gs[0, 0])
    ax_a.set_title("(a) 亦城茗苑 (C04) 普通日 3 条最优共同配送闭环路径", loc='left', fontweight='bold', pad=10)

    c04_coords = {
        'F05(接驳)': (0.10, 0.50),
        'D01': (0.30, 0.85), 'D02': (0.50, 0.85), 'D03': (0.75, 0.85),
        'D04': (0.30, 0.55), 'D05': (0.50, 0.55), 'D06': (0.75, 0.55),
        'D07': (0.30, 0.25), 'D08': (0.50, 0.25), 'D09': (0.75, 0.25),
        'D10': (0.90, 0.75), 'D11': (0.90, 0.45), 'D12': (0.90, 0.15)
    }

    # Plot base nodes
    for nid, (nx, ny) in c04_coords.items():
        if 'F05' in nid:
            ax_a.scatter(nx, ny, c=COLOR_ORANGE, marker='s', s=130, edgecolors=COLOR_BLACK, lw=1.5, zorder=5)
            ax_a.text(nx - 0.03, ny + 0.05, nid, fontweight='bold', fontsize=8.5, color=COLOR_ORANGE)
        else:
            ax_a.scatter(nx, ny, c=COLOR_BLUE, marker='o', s=80, edgecolors=COLOR_BLACK, lw=1.0, zorder=4)
            ax_a.text(nx, ny + 0.04, nid, ha='center', fontsize=8.0, fontweight='bold')

    norm_routes = [
        (['F05(接驳)', 'D08', 'D01', 'D05', 'F05(接驳)'], COLOR_BLUE, 'R1 (436件, 96.9%)', '-'),
        (['F05(接驳)', 'D06', 'D04', 'D09', 'D02', 'F05(接驳)'], COLOR_BLUISH_GREEN, 'R2 (407件, 90.4%)', '--'),
        (['F05(接驳)', 'D07', 'D11', 'D12', 'D10', 'D03', 'F05(接驳)'], COLOR_VERMILLION, 'R3 (442件, 98.1%)', '-.')
    ]

    for r_nodes, r_col, r_lbl, r_ls in norm_routes:
        xs = [c04_coords[n][0] for n in r_nodes]
        ys = [c04_coords[n][1] for n in r_nodes]
        ax_a.plot(xs, ys, color=r_col, lw=2.0, ls=r_ls, label=r_lbl, zorder=2)
        for k in range(len(xs) - 1):
            mx = (xs[k] + xs[k+1]) / 2
            my = (ys[k] + ys[k+1]) / 2
            dx = (xs[k+1] - xs[k]) * 0.05
            dy = (ys[k+1] - ys[k]) * 0.05
            ax_a.annotate('', xy=(mx + dx, my + dy), xytext=(mx - dx, my - dy),
                          arrowprops=dict(arrowstyle="-|>", color=r_col, lw=1.5, mutation_scale=10))

    ax_a.set_xlim(0.02, 1.00)
    ax_a.set_ylim(0.05, 0.98)
    ax_a.grid(True, linestyle=':', alpha=0.4)
    ax_a.legend(loc='lower left', framealpha=0.92, fontsize=8.0)
    ax_a.set_xlabel("社区相对 X 坐标")
    ax_a.set_ylabel("社区相对 Y 坐标")

    # --- Panel (b): C04 Peak Day 7 Optimal Routes ---
    ax_b = fig.add_subplot(gs[0, 1])
    ax_b.set_title("(b) 亦城茗苑 (C04) 高峰日 7 条最优共同配送闭环路径", loc='left', fontweight='bold', pad=10)

    for nid, (nx, ny) in c04_coords.items():
        if 'F05' in nid:
            ax_b.scatter(nx, ny, c=COLOR_ORANGE, marker='s', s=130, edgecolors=COLOR_BLACK, lw=1.5, zorder=5)
            ax_b.text(nx - 0.03, ny + 0.05, nid, fontweight='bold', fontsize=8.5, color=COLOR_ORANGE)
        else:
            ax_b.scatter(nx, ny, c=COLOR_BLUE, marker='o', s=80, edgecolors=COLOR_BLACK, lw=1.0, zorder=4)
            ax_b.text(nx, ny + 0.04, nid, ha='center', fontsize=8.0, fontweight='bold')

    peak_routes = [
        (['F05(接驳)', 'D01', 'F05(接驳)'], '#E69F00', 'R1: D01 (380件)'),
        (['F05(接驳)', 'D02', 'F05(接驳)'], '#56B4E9', 'R2: D02 (392件)'),
        (['F05(接驳)', 'D05', 'D09', 'D03', 'F05(接驳)'], '#009E73', 'R3: D05→09→03 (445件)'),
        (['F05(接驳)', 'D06', 'D04', 'F05(接驳)'], '#F0E442', 'R4: D06→04 (281件)'),
        (['F05(接驳)', 'D07', 'F05(接驳)'], '#0072B2', 'R5: D07 (323件)'),
        (['F05(接驳)', 'D08', 'F05(接驳)'], '#D55E00', 'R6: D08 (328件)'),
        (['F05(接驳)', 'D10', 'D11', 'D12', 'F05(接驳)'], '#CC79A7', 'R7: D10→11→12 (420件)')
    ]

    for r_nodes, r_col, r_lbl in peak_routes:
        xs = [c04_coords[n][0] for n in r_nodes]
        ys = [c04_coords[n][1] for n in r_nodes]
        ax_b.plot(xs, ys, color=r_col, lw=1.8, label=r_lbl, zorder=2)

    ax_b.set_xlim(0.02, 1.00)
    ax_b.set_ylim(0.05, 0.98)
    ax_b.grid(True, linestyle=':', alpha=0.4)
    ax_b.legend(loc='lower left', framealpha=0.92, fontsize=7.5, ncol=2)
    ax_b.set_xlabel("社区相对 X 坐标")
    ax_b.set_ylabel("社区相对 Y 坐标")

    # --- Panel (c): Vehicle Workload & Energy Consumption (Tables 5-5 & 5-10) ---
    ax_c = fig.add_subplot(gs[1, 0])
    ax_c.set_title("(c) 五社区高峰日单车工作负荷结构与电池能耗核算", loc='left', fontweight='bold', pad=10)

    comms = ['梅园 (C01)', '鹿鸣苑 (C02)', '天华园 (C03)', '亦城茗苑 (C04)', '听涛雅苑 (C05)']
    travel_time = [6.88, 23.52, 12.71, 71.51, 51.54]
    service_time = [12.0, 21.0, 33.0, 36.0, 30.0]
    total_time = [t + s for t, s in zip(travel_time, service_time)]
    mileage = [0.968, 3.623, 2.479, 5.569, 3.890]
    battery_pct = [1.0, 3.6, 2.5, 5.6, 3.9]

    x = np.arange(len(comms))
    width = 0.50

    p1 = ax_c.bar(x, travel_time, width, label='车辆道路行驶时间 (Travel Time)', color=COLOR_BLUE, edgecolor=COLOR_BLACK, lw=0.8)
    p2 = ax_c.bar(x, service_time, width, bottom=travel_time, label='节点停靠交接时间 (Service Time)', color=COLOR_SKY_BLUE, edgecolor=COLOR_BLACK, lw=0.8)

    ax_c.axhline(480.0, color=COLOR_VERMILLION, linestyle='--', lw=1.5, label='8小时全日工作上限 (480 min)')

    ax_c.set_ylabel("单日基础作业时间 (min)")
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(comms, rotation=15, ha='right')
    ax_c.set_ylim(0, 160)
    ax_c.grid(True, axis='y', linestyle=':', alpha=0.5)
    ax_c.legend(loc='upper left', framealpha=0.9, fontsize=8.0)

    for i, (tot, km, bp) in enumerate(zip(total_time, mileage, battery_pct)):
        ax_c.text(i, tot + 3.0, f"{tot:.1f}min\n({km:.2f}km | {bp:.1f}%)", ha='center', va='bottom', fontsize=7.8, fontweight='bold')

    ax_c.text(0.98, 0.85, "各社区单车全日负荷均 < 110 min\n全日电耗均 < 5.6% 电池容量 (100km续航)\n==> 无需日间计划性换电，集中夜间补能即可",
              transform=ax_c.transAxes, fontsize=8.0, fontweight='bold', ha='right',
              bbox=dict(boxstyle='round,pad=0.25', facecolor='#F8FAFC', edgecolor=COLOR_BLUE, lw=1.0))

    # --- Panel (d): Abnormal Detection & Task Recovery Closed Loop ---
    ax_d = fig.add_subplot(gs[1, 1])
    ax_d.set_title("(d) 无人配送异常识别、路径重规划与任务恢复闭环机制", loc='left', fontweight='bold', pad=10)
    ax_d.axis('off')

    loop_stages = [
        ("1. 正常运行状态", "车辆按计划路线巡航\n实时上报 GPS/SOC/载荷", COLOR_BLUISH_GREEN, 0.20, 0.80),
        ("2. 状态异常识别", "- 车辆硬件/通信故障\n- 道路临时施工受阻\n- 智能柜满柜/上门突增", COLOR_VERMILLION, 0.80, 0.80),
        ("3. 动态响应与处置", "- 受阻路段网络动态剔除\n- 邻柜分流 / 驿站暂存\n- 冻结任务转人工接管", COLOR_ORANGE, 0.80, 0.25),
        ("4. 任务恢复与回流", "Dijkstra 重新生成可行路\n车辆/人工无缝承接\n返回正常协同闭环", COLOR_BLUE, 0.20, 0.25)
    ]

    for title, desc, col, lx, ly in loop_stages:
        w, h = 0.36, 0.38
        rect = patches.FancyBboxPatch((lx - w/2, ly - h/2), w, h, boxstyle="round,pad=0.02,rounding_size=0.03",
                                     linewidth=1.8, edgecolor=col, facecolor='white', transform=ax_d.transAxes)
        ax_d.add_patch(rect)
        hdr = patches.FancyBboxPatch((lx - w/2, ly + h/2 - 0.10), w, 0.10, boxstyle="round,pad=0.02,rounding_size=0.02",
                                     linewidth=0, facecolor=col, transform=ax_d.transAxes)
        ax_d.add_patch(hdr)
        ax_d.text(lx, ly + h/2 - 0.05, title, color='white', fontweight='bold', ha='center', va='center', fontsize=9.0, transform=ax_d.transAxes)
        ax_d.text(lx, ly - 0.04, desc, color=COLOR_DARK_GRAY, fontsize=8.2, ha='center', va='center', linespacing=1.4, transform=ax_d.transAxes)

    # Loop arrows
    ax_d.annotate('', xy=(0.60, 0.80), xytext=(0.40, 0.80),
                  arrowprops=dict(arrowstyle="-|>", color=COLOR_DARK_GRAY, lw=2.5, mutation_scale=14), xycoords='axes fraction')
    ax_d.text(0.50, 0.83, "异常触发\n(Event Trigger)", fontsize=7.8, ha='center', color=COLOR_VERMILLION, fontweight='bold', transform=ax_d.transAxes)

    ax_d.annotate('', xy=(0.80, 0.46), xytext=(0.80, 0.59),
                  arrowprops=dict(arrowstyle="-|>", color=COLOR_DARK_GRAY, lw=2.5, mutation_scale=14), xycoords='axes fraction')
    ax_d.text(0.85, 0.525, "分流决策\n(Dispatch)", fontsize=7.8, ha='left', color=COLOR_ORANGE, fontweight='bold', transform=ax_d.transAxes)

    ax_d.annotate('', xy=(0.40, 0.25), xytext=(0.60, 0.25),
                  arrowprops=dict(arrowstyle="-|>", color=COLOR_DARK_GRAY, lw=2.5, mutation_scale=14), xycoords='axes fraction')
    ax_d.text(0.50, 0.28, "重规划求解\n(Re-optimization)", fontsize=7.8, ha='center', color=COLOR_BLUE, fontweight='bold', transform=ax_d.transAxes)

    ax_d.annotate('', xy=(0.20, 0.59), xytext=(0.20, 0.46),
                  arrowprops=dict(arrowstyle="-|>", color=COLOR_DARK_GRAY, lw=2.5, mutation_scale=14), xycoords='axes fraction')
    ax_d.text(0.12, 0.525, "系统复归\n(Resume)", fontsize=7.8, ha='right', color=COLOR_BLUISH_GREEN, fontweight='bold', transform=ax_d.transAxes)

    save_fig(fig, 'fig7_4_c04_routes_workload_and_contingency')


if __name__ == '__main__':
    generate_fig7_1()
    generate_fig7_2()
    generate_fig7_3()
    generate_fig7_4()
    print("All Chapter 7 publication figures successfully regenerated!")
