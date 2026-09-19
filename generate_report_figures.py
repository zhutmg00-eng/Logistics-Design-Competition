"""
Generate High-Resolution Publication Figures for Chapter 8 (Delivery System Simulation Verification)
(为竞赛方案第8章一键导出出版级矢量/高清图表 300 DPI)
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 设置中文字体与负号显示
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

# 导入仿真引擎获取真实数据
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from demo.core.simulation_engine import SimulationEngine

def generate_all_chapter8_figures(output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(current_dir, "docs", "images", "chapter8")
    os.makedirs(output_dir, exist_ok=True)

    sim = SimulationEngine()
    res_normal = sim.run_simulation(scenario="normal")
    res_peak = sim.run_simulation(scenario="peak")

    # 配色方案 (学术与数智蓝/绿/橙/青)
    c_blue = '#1E40AF'
    c_cyan = '#0284C7'
    c_teal = '#0D9488'
    c_emerald = '#059669'
    c_amber = '#D97706'
    c_rose = '#E11D48'
    c_slate = '#475569'

    # =========================================================================
    # 图 8-1: 普通日与高峰日需求及趟次对比
    # =========================================================================
    fig, ax1 = plt.subplots(figsize=(8, 4.8))
    comm_names = [c["name"] for c in res_normal["community_results"]]
    x = np.arange(len(comm_names))
    width = 0.35

    pkgs_normal = [c["daily_pkgs"] for c in res_normal["community_results"]]
    pkgs_peak = [c["daily_pkgs"] for c in res_peak["community_results"]]
    trips_normal = [c["trips"] for c in res_normal["community_results"]]
    trips_peak = [c["trips"] for c in res_peak["community_results"]]

    rects1 = ax1.bar(x - width/2, pkgs_normal, width, label='普通日快件需求量 (件)', color=c_cyan, alpha=0.9, edgecolor='white', linewidth=1)
    rects2 = ax1.bar(x + width/2, pkgs_peak, width, label='高峰日快件需求量 (件, 峰值k=2.0)', color=c_amber, alpha=0.9, edgecolor='white', linewidth=1)

    ax1.set_ylabel('单日快件需求总量 (件)', fontsize=11, fontweight='bold', color=c_slate)
    ax1.set_title('图8-1 普通日与大促高峰日各社区快件需求及无人车发车趟次对比', fontsize=12, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(comm_names, fontsize=10, fontweight='bold')
    ax1.grid(axis='y', linestyle='--', alpha=0.3)

    # 次坐标轴：趟次
    ax2 = ax1.twinx()
    line1 = ax2.plot(x - width/2, trips_normal, color='#1E3A8A', marker='o', markersize=6, linewidth=2, label='普通日发车趟次 (次)')
    line2 = ax2.plot(x + width/2, trips_peak, color='#B45309', marker='s', markersize=6, linewidth=2, linestyle='--', label='高峰日发车趟次 (次)')
    ax2.set_ylabel('无人车巡回发车趟次 (次)', fontsize=11, fontweight='bold', color='#1E3A8A')
    ax2.set_ylim(0, max(trips_peak) + 3)

    # 数值标签
    for rect in rects1:
        h = rect.get_height()
        ax1.annotate(f'{int(h)}', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, color=c_cyan, fontweight='bold')
    for rect in rects2:
        h = rect.get_height()
        ax1.annotate(f'{int(h)}', xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=8, color=c_amber, fontweight='bold')

    # 合并图例
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(handles1 + handles2, labels1 + labels2, loc='upper left', framealpha=0.9, fontsize=9)

    fig.tight_layout()
    p1 = os.path.join(output_dir, "图8-1_普通日与高峰日需求及趟次对比.png")
    fig.savefig(p1, bbox_inches='tight')
    plt.close(fig)
    print(f"[*] Generated: {p1}")

    # =========================================================================
    # 图 8-2: 现状方案与人机协同方案关键指标对比
    # =========================================================================
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    categories = ['干线总里程\n(km/日)', '人工步巡总里程\n(km/日)', '全网人工总工时\n(h/日)', '满柜风险社区数\n(个)']
    baseline_vals = [19.94, 13.78, 151.17, 3]
    collab_vals = [13.32, 9.07, 62.28, 0]
    savings = ['-33.2%', '-34.2%', '-58.8%', '-100%']

    x = np.arange(len(categories))
    width = 0.32

    rects_base = ax.bar(x - width/2, baseline_vals, width, label='现状方案（纯人工独立往返）', color='#94A3B8', edgecolor='white', linewidth=1)
    rects_collab = ax.bar(x + width/2, collab_vals, width, label='推荐方案（无人车+人工协同）', color=c_teal, edgecolor='white', linewidth=1)

    ax.set_title('图8-2 现状方案与人机协同方案核心运营指标仿真对比', fontsize=12, fontweight='bold', pad=15)
    ax.set_ylabel('数值（对应各指标物理单位）', fontsize=11, fontweight='bold', color=c_slate)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=10, fontweight='bold')
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9.5)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    for i, (rb, rc) in enumerate(zip(rects_base, rects_collab)):
        hb = rb.get_height()
        hc = rc.get_height()
        ax.annotate(f'{hb:.1f}' if hb != 3 else '3', xy=(rb.get_x() + rb.get_width()/2, hb), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#64748B')
        ax.annotate(f'{hc:.1f}' if hc != 0 else '0', xy=(rc.get_x() + rc.get_width()/2, hc), xytext=(0, 3), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold', color=c_teal)
        # 标注改善率徽章
        ax.annotate(f'降幅 {savings[i]}', xy=(rc.get_x() + rc.get_width()/2, max(hb, hc) * 0.55 + 5), ha='center', fontsize=9, fontweight='bold', color=c_rose,
                    bbox=dict(boxstyle="round,pad=0.2", fc="#FFF1F2", ec=c_rose, lw=1))

    fig.tight_layout()
    p2 = os.path.join(output_dir, "图8-2_现状方案与人机协同方案关键指标对比.png")
    fig.savefig(p2, bbox_inches='tight')
    plt.close(fig)
    print(f"[*] Generated: {p2}")

    # =========================================================================
    # 图 8-3: 各社区仿真完成时长与满柜风险
    # =========================================================================
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    cr_list = res_normal["community_results"]
    durations = [c["sim_duration_min"] for c in cr_list]
    c_labels = [f'{c["name"]}\n({c["community_id"]})' for c in cr_list]
    risks = [c["full_risk_baseline"] for c in cr_list]

    bar_colors = [c_rose if r == "是" else c_emerald for r in risks]
    bars = ax.bar(c_labels, durations, width=0.45, color=bar_colors, edgecolor='white', linewidth=1.2, alpha=0.9)

    # 绘制单班 480 分钟红线
    ax.axhline(y=480, color='#DC2626', linestyle='--', linewidth=2, label='单班标准工时基准 (480 min / 8h)')

    ax.set_title('图8-3 各社区专用资源下单日作业完成时长与满柜风险核验', fontsize=12, fontweight='bold', pad=15)
    ax.set_ylabel('端到端作业完成耗时 (分钟)', fontsize=11, fontweight='bold', color=c_slate)
    ax.grid(axis='y', linestyle='--', alpha=0.3)

    for bar, c, r in zip(bars, cr_list, risks):
        h = bar.get_height()
        ax.annotate(f'{h:.1f} min', xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0, 4), textcoords="offset points", ha='center', va='bottom', fontsize=9, fontweight='bold')
        risk_txt = "【基准满柜风险】" if r == "是" else "【容量安全】"
        risk_col = c_rose if r == "是" else c_emerald
        ax.annotate(risk_txt, xy=(bar.get_x() + bar.get_width()/2, h * 0.45), ha='center', fontsize=8.5, fontweight='bold', color='white',
                    bbox=dict(boxstyle="round,pad=0.25", fc=risk_col, ec="none"))

    # 自定义图例
    patch_safe = mpatches.Patch(color=c_emerald, label='单柜容量安全社区 (C01, C03)')
    patch_risk = mpatches.Patch(color=c_rose, label='未扩容满柜风险社区 (C02, TT, C04)')
    ax.legend(handles=[ax.lines[0], patch_safe, patch_risk], loc='upper left', framealpha=0.9, fontsize=9)

    fig.tight_layout()
    p3 = os.path.join(output_dir, "图8-3_各社区仿真完成时长与满柜风险.png")
    fig.savefig(p3, bbox_inches='tight')
    plt.close(fig)
    print(f"[*] Generated: {p3}")

    # =========================================================================
    # 图 8-4: 智能柜格口占用时序动态折线图 (08:00 - 21:00)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(9, 4.8))
    hours = res_normal["timeline"]["hours"]
    sat_base = res_normal["timeline"]["locker_occupancy_baseline"]
    sat_opt = res_normal["timeline"]["locker_occupancy_optimized"]

    ax.plot(hours, sat_base, color=c_rose, linewidth=2.5, linestyle='--', marker='o', label='未扩容基准单柜饱和度 (连续7时段严重溢出爆柜)')
    ax.plot(hours, sat_opt, color=c_emerald, linewidth=3.0, marker='s', label='MIP副柜扩容与分流后饱和度 (峰值平稳控制在68.5%以下)')
    ax.fill_between(hours, sat_opt, color=c_emerald, alpha=0.12)

    # 100% 满柜警戒红线
    ax.axhline(y=100, color='#991B1B', linestyle='-', linewidth=2.2, label='100% 智能柜物理容量饱和红线')

    ax.set_title('图8-4 全天 08:00—21:00 智能柜格口在存快件动态饱和度时序变化曲线', fontsize=12, fontweight='bold', pad=15)
    ax.set_xlabel('运营时段 (小时)', fontsize=11, fontweight='bold', color=c_slate)
    ax.set_ylabel('格口动态饱和度 (%)', fontsize=11, fontweight='bold', color=c_slate)
    ax.set_ylim(0, 180)
    ax.grid(True, linestyle='--', alpha=0.35)
    ax.legend(loc='upper right', framealpha=0.9, fontsize=9.5)

    # 标注爆柜区间 (使用类别索引精确定位在左侧空白区)
    ax.annotate('未扩容基准单柜\n连续7时段严重爆柜\n峰值达 152%', xy=(4, 172), xytext=(1.5, 125),
                arrowprops=dict(facecolor=c_rose, shrink=0.08, width=1.5, headwidth=6),
                fontsize=8.5, fontweight='bold', color=c_rose,
                bbox=dict(boxstyle="round,pad=0.3", fc="#FFF1F2", ec=c_rose, lw=1))

    fig.tight_layout()
    p4 = os.path.join(output_dir, "图8-4_智能柜格口占用时序动态折线图.png")
    fig.savefig(p4, bbox_inches='tight')
    plt.close(fig)
    print(f"[*] Generated: {p4}")

    # =========================================================================
    # 图 8-5: 人机协同作业时序甘特图 (Gantt Chart)
    # =========================================================================
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    gantt_tasks = res_normal["gantt_schedule"]
    entities = sorted(list(set(t["entity"] for t in gantt_tasks)), reverse=True)
    y_map = {e: idx for idx, e in enumerate(entities)}

    def to_minutes(t_str):
        h, m = map(int, t_str.split(':'))
        return (h - 8) * 60 + m

    for t in gantt_tasks:
        y_idx = y_map[t["entity"]]
        s_min = to_minutes(t["start_time"])
        dur = t["duration_min"]
        col = c_cyan if t["type"] == "UV_TRIP" else c_amber
        ax.broken_barh([(s_min, dur)], (y_idx - 0.25, 0.5), facecolors=col, edgecolor='white', linewidth=0.8)
        # 精简标签文字，避免狭长条重叠
        if t["type"] == "UV_TRIP":
            trip_lbl = t["label"].split(':')[0]
            ax.text(s_min + dur/2, y_idx, trip_lbl, ha='center', va='center', color='white', fontsize=7.5, fontweight='bold')
        elif dur >= 40:
            ax.text(s_min + dur/2, y_idx, "上门交付", ha='center', va='center', color='white', fontsize=7, fontweight='bold')

    ax.set_yticks(range(len(entities)))
    ax.set_yticklabels(entities, fontsize=9.5, fontweight='bold')
    ax.set_xlabel('全日运营时间轴 (08:00 — 21:00)', fontsize=11, fontweight='bold', color=c_slate)
    ax.set_title('图8-5 无人配送车巡航与驻点快递员上门作业时序嵌套甘特图', fontsize=12, fontweight='bold', pad=15)
    ax.set_xlim(0, 13 * 60)
    tick_locs = [i * 60 for i in range(14)]
    tick_labels = [f'{8+i:02d}:00' for i in range(14)]
    ax.set_xticks(tick_locs)
    ax.set_xticklabels(tick_labels, fontsize=9)
    ax.grid(axis='x', linestyle='--', alpha=0.4)

    patch_uv = mpatches.Patch(color=c_cyan, label='无人配送车 (X3) 干线巡回与社区投递')
    patch_courier = mpatches.Patch(color=c_amber, label='驻点快递员接驳与精细化入户上门')
    ax.legend(handles=[patch_uv, patch_courier], loc='upper right', framealpha=0.9, fontsize=9.5)

    fig.tight_layout()
    p5 = os.path.join(output_dir, "图8-5_人机协同作业时序甘特图.png")
    fig.savefig(p5, bbox_inches='tight')
    plt.close(fig)
    print(f"[*] Generated: {p5}")

    return [p1, p2, p3, p4, p5]

if __name__ == "__main__":
    generate_all_chapter8_figures()
