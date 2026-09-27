# -*- coding: utf-8 -*-
"""Generate a concise, publication-grade technical roadmap."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
from matplotlib.path import Path
from matplotlib.patches import PathPatch

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "SimSun", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 300


def card(ax, x, y, w, h, face, edge, radius=0.008, lw=1.0, z=2):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.003,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=lw, zorder=z,
    )
    ax.add_patch(p)
    return p


def text(ax, x, y, s, size=10, color="#24465F", weight="normal", ha="left", va="center", z=5, **kwargs):
    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
            ha=ha, va=va, zorder=z, **kwargs)


def draw_stage(ax, y, h, num, title, subtitle, accent, tint, modules):
    x, w = 0.03, 0.94
    card(ax, x, y, w, h, tint, accent, radius=0.010, lw=1.25, z=2)
    side_x, side_w = x + 0.008, 0.150
    card(ax, side_x, y + 0.008, side_w, h - 0.016, accent, accent, radius=0.008, lw=0, z=3)
    text(ax, side_x + side_w / 2, y + h * 0.75, num, 23, "#FFFFFF", "bold", "center", z=5)
    text(ax, side_x + side_w / 2, y + h * 0.50, title, 12.5, "#FFFFFF", "bold", "center", z=5)
    text(ax, side_x + side_w / 2, y + h * 0.31, subtitle, 8.2, "#EAF6FA", "normal", "center", z=5)

    sx = side_x + side_w + 0.015
    total_w = x + w - sx - 0.012
    gap = 0.013
    bw = (total_w - 2 * gap) / 3.0
    by, bh = y + 0.010, h - 0.020

    for i, (module_title, module_line) in enumerate(modules):
        bx = sx + i * (bw + gap)
        card(ax, bx, by, bw, bh, "#FFFFFF", accent, radius=0.006, lw=1.0, z=3)
        card(ax, bx, by + bh * 0.70, bw, bh * 0.30, accent, accent, radius=0.005, lw=0, z=4)
        text(ax, bx + bw / 2, by + bh * 0.85, module_title, 10.3, "#FFFFFF", "bold", "center", z=5)
        text(ax, bx + 0.014, by + bh * 0.38, "▪", 10.0, accent, "bold", "left", z=5)
        text(ax, bx + 0.028, by + bh * 0.38, module_line, 9.2, "#36566A", "normal", "left", z=5)


def draw_connector(ax, y_top, y_bottom, label, color):
    x = 0.50
    arrow = patches.FancyArrowPatch(
        (x, y_top), (x, y_bottom),
        arrowstyle="-|>,head_length=5,head_width=3.5",
        color=color, linewidth=1.7, zorder=7,
    )
    ax.add_patch(arrow)
    y_mid = (y_top + y_bottom) / 2
    text(ax, x, y_mid, label, 8.6, "#294E63", "bold", "center",
         bbox=dict(boxstyle="round,pad=0.27,rounding_size=0.005",
                   facecolor="#FFFFFF", edgecolor=color, linewidth=1.0), z=8)


def generate(output_path):
    fig, ax = plt.subplots(figsize=(18, 25.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    card(ax, 0, 0, 1, 1, "#F7FBFC", "#F7FBFC", radius=0, lw=0, z=0)

    # Header
    card(ax, 0.03, 0.932, 0.94, 0.053, "#FFFFFF", "#7CCCE7", radius=0.012, lw=1.6, z=2)
    text(ax, 0.50, 0.969, "京枢智网·畅达末端 —— 总体技术路线图", 21, "#0B3150", "bold", "center", z=4)
    text(ax, 0.50, 0.946, "从社区多源数据到四端协同平台的末端配送智能决策闭环", 11, "#5D7D90", "normal", "center", z=4)

    # Flow strip
    flow = ["数据与约束", "需求与情景", "网络与定容", "人机与调度", "推演与校验", "评价与平台"]
    colors = ["#176B96", "#168AA6", "#138F80", "#2F8B5A", "#C98418", "#315A72"]
    start, chip_w, chip_gap, chip_h, chip_y = 0.050, 0.142, 0.014, 0.023, 0.900
    for i, name in enumerate(flow):
        x = start + i * (chip_w + chip_gap)
        card(ax, x, chip_y, chip_w, chip_h, "#FFFFFF", colors[i], radius=0.006, lw=0.9, z=2)
        text(ax, x + chip_w / 2, chip_y + chip_h / 2, name, 9.2, colors[i], "bold", "center", z=4)
        if i < len(flow) - 1:
            ax.add_patch(patches.FancyArrowPatch(
                (x + chip_w + 0.003, chip_y + chip_h / 2),
                (x + chip_w + chip_gap - 0.003, chip_y + chip_h / 2),
                arrowstyle="-|>", mutation_scale=8, color="#8DB6C7", lw=1.0, zorder=3,
            ))

    stages = [
        dict(
            num="01", title="数据底座", subtitle="问题识别与样本构建", accent="#176B96", tint="#F2F9FC",
            modules=[
                ("空间数据", "5 个社区 WGS84 边界、路网与节点"),
                ("行为数据", "4316 户、六时段到件与服务方式"),
                ("约束数据", "HUB、接驳点、柜机与无人车参数"),
            ],
        ),
        dict(
            num="02", title="需求推演", subtitle="多尺度概率生成", accent="#168AA6", tint="#F1FAFB",
            modules=[
                ("需求概率", "Gamma-Poisson / 负二项分布"),
                ("时空分解", "Dirichlet-Multinomial 六时段分配"),
                ("情景输出", "P50 / P80 / P90 与促销峰值"),
            ],
        ),
        dict(
            num="03", title="网络规划", subtitle="三级协同选址定容", accent="#138F80", tint="#F0FAF8",
            modules=[
                ("规模确定", "覆盖、容量与新增设施下限"),
                ("选址分配", "Capacitated P-Median"),
                ("定容连网", "MIP 扩容与三级网络拓扑"),
            ],
        ),
        dict(
            num="04", title="人机协同", subtitle="路径优化与双算法求解", accent="#2F8B5A", tint="#F2FBF5",
            modules=[
                ("M1 干线巡回", "2-Opt TSP + MTZ 子回路约束"),
                ("M2/M3 双层协同", "无人车投柜补货 + 快递员上门"),
                ("智能求解", "K-Means + ISA / 改进 NSGA-II"),
            ],
        ),
        dict(
            num="05", title="情景校验", subtitle="动态推演与硬约束", accent="#C98418", tint="#FFFAED",
            modules=[
                ("M8 状态转移", "08:00—21:00 柜体占用动态演化"),
                ("多情景测试", "N / P15 / P20 / D-R / D-V / D-L"),
                ("硬约束校核", "覆盖、容量、工时与时间窗"),
            ],
        ),
        dict(
            num="06", title="评价与平台", subtitle="效益评价与四端落地", accent="#315A72", tint="#F5F9FB",
            modules=[
                ("统一评价", "S0 / S1 / S2 多维指标同口径比较"),
                ("平台底座", "FastAPI + 高德 WebGIS + ECharts"),
                ("四端协同", "运营 / 企业 / 配送员 / 居民"),
            ],
        ),
    ]

    h, gap = 0.118, 0.021
    y_starts = [0.795 - i * (h + gap) for i in range(len(stages))]
    for i, item in enumerate(stages):
        draw_stage(ax, y_starts[i], h, **{k: v for k, v in item.items() if k != "flow"})
        if i < len(stages) - 1:
            draw_connector(ax, y_starts[i], y_starts[i + 1] + h,
                           ["标准化数据", "需求分位数", "网络拓扑", "调度方案", "验证结果"][i],
                           item["accent"])

    text(ax, 0.035, 0.034,
         "技术口径：样本数据包含 C/D 类假设参数，路线图展示模型方法闭环，数值不代表现场实测。",
         7.8, "#6C8796", "normal", "left", z=5)
    text(ax, 0.965, 0.034, "JINGSHU INTELLIGENT NETWORK · SEAMLESS LAST-MILE",
         7.2, "#7B98A8", "normal", "right", z=5)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches="tight", pad_inches=0.08, facecolor="#F7FBFC")
    plt.close(fig)
    print(f"Concise technical roadmap generated: {output_path}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))
    generate(os.path.join(base, "output", "roadmap", "technical_roadmap_concise.png"))
