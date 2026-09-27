# -*- coding: utf-8 -*-
"""
Generate Publication-Grade Technical Roadmap Figure for the Project
(为《京枢智网·畅达末端》竞赛方案生成出版级全景技术路线图 300 DPI)
采用顶级咨询/国家重大课题卡片流式架构 (Card-Flow Architecture)
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch

# 设置高品质中文字体与DPI
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['figure.dpi'] = 300

def draw_phase_card(ax, y_bottom, height, stage_num, stage_title, stage_sub, chapter_tag,
                    color_accent, color_bg, boxes_data):
    """
    绘制单阶段大卡片：
    - 左侧：阶段序号、主标题、定位副标题、所属章节标签 (高亮侧边栏)
    - 右侧：2-3个子系统功能框图
    """
    card_x = 0.03
    card_w = 0.94
    corner = 0.012

    # 1. 阶段外层卡片背景
    card_bg = FancyBboxPatch((card_x, y_bottom), card_w, height,
                             boxstyle=f"round,pad=0.006,rounding_size={corner}",
                             facecolor=color_bg, edgecolor=color_accent,
                             linewidth=1.4, alpha=0.96, zorder=2)
    ax.add_patch(card_bg)

    # 2. 左侧定位侧边栏
    sidebar_w = 0.155
    sidebar_x = card_x + 0.008
    sidebar_y = y_bottom + 0.008
    sidebar_h = height - 0.016
    
    sidebar = FancyBboxPatch((sidebar_x, sidebar_y), sidebar_w, sidebar_h,
                             boxstyle=f"round,pad=0.005,rounding_size={corner*0.8}",
                             facecolor=color_accent, edgecolor='none',
                             alpha=0.95, zorder=3)
    ax.add_patch(sidebar)

    # 侧边栏文字内容
    # 序号
    ax.text(sidebar_x + sidebar_w/2.0, sidebar_y + sidebar_h * 0.75, stage_num,
            ha='center', va='center', fontsize=22, fontweight='bold', color='#FFFFFF', zorder=4)
    # 阶段名称
    ax.text(sidebar_x + sidebar_w/2.0, sidebar_y + sidebar_h * 0.50, stage_title,
            ha='center', va='center', fontsize=12, fontweight='bold', color='#FFFFFF', zorder=4)
    # 副标题
    ax.text(sidebar_x + sidebar_w/2.0, sidebar_y + sidebar_h * 0.32, stage_sub,
            ha='center', va='center', fontsize=8.5, color='#E2E8F0', zorder=4)
    
    # 章节徽章
    tag_h = sidebar_h * 0.18
    tag_w = sidebar_w * 0.85
    tag_box = FancyBboxPatch((sidebar_x + (sidebar_w - tag_w)/2.0, sidebar_y + 0.006), tag_w, tag_h,
                             boxstyle=f"round,pad=0.003,rounding_size=0.006",
                             facecolor='#FFFFFF', edgecolor='none', alpha=0.95, zorder=4)
    ax.add_patch(tag_box)
    ax.text(sidebar_x + sidebar_w/2.0, sidebar_y + 0.006 + tag_h/2.0, chapter_tag,
            ha='center', va='center', fontsize=8.5, fontweight='bold', color=color_accent, zorder=5)

    # 3. 右侧子模块框图 (支持2或3个框)
    num_boxes = len(boxes_data)
    right_start_x = sidebar_x + sidebar_w + 0.015
    right_total_w = card_x + card_w - right_start_x - 0.012
    
    box_gap = 0.014
    box_w = (right_total_w - (num_boxes - 1) * box_gap) / num_boxes
    box_h = height - 0.020
    box_y = y_bottom + 0.010

    for i, b in enumerate(boxes_data):
        bx = right_start_x + i * (box_w + box_gap)
        
        # 子模块框
        bbox = FancyBboxPatch((bx, box_y), box_w, box_h,
                              boxstyle=f"round,pad=0.005,rounding_size={corner*0.7}",
                              facecolor='#FFFFFF', edgecolor=color_accent,
                              linewidth=1.0, alpha=0.98, zorder=3)
        ax.add_patch(bbox)

        # 子模块标题栏
        tb_h = box_h * 0.25
        tb_box = FancyBboxPatch((bx, box_y + box_h - tb_h), box_w, tb_h,
                                boxstyle=f"round,pad=0.004,rounding_size={corner*0.6}",
                                facecolor=color_accent, edgecolor='none',
                                alpha=0.12, zorder=4)
        ax.add_patch(tb_box)
        
        # 标题文字
        ax.text(bx + box_w/2.0, box_y + box_h - tb_h/2.0, b["title"],
                ha='center', va='center', fontsize=10.5, fontweight='bold',
                color=color_accent, zorder=5)

        # 条目文字
        items = b["items"]
        spacing = (box_h - tb_h - 0.012) / (len(items) + 0.3)
        cur_y = box_y + box_h - tb_h - 0.008 - spacing * 0.7
        for item in items:
            ax.scatter(bx + 0.014, cur_y, s=14, color=color_accent, marker='s', alpha=0.9, zorder=5)
            ax.text(bx + 0.024, cur_y, item, ha='left', va='center',
                    fontsize=8.5, color='#334155', zorder=5)
            cur_y -= spacing

def draw_stage_connector(ax, y_top, y_bottom, connectors):
    """在两层卡片之间绘制多路垂直数据流箭头与胶囊标签"""
    for c in connectors:
        x = c["x"]
        text = c["text"]
        color = c["color"]
        
        arrow = patches.FancyArrowPatch((x, y_top), (x, y_bottom),
                                       arrowstyle='-|>,head_length=5,head_width=3.5',
                                       color=color, linewidth=1.6, zorder=6)
        ax.add_patch(arrow)
        
        my = (y_top + y_bottom) / 2.0
        ax.text(x, my, text, ha='center', va='center', fontsize=8,
                color='#0F172A', fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.25,rounding_size=0.005',
                          facecolor='#FFFFFF', edgecolor=color, alpha=0.98, linewidth=0.9),
                zorder=7)

def generate_technical_roadmap(output_path):
    fig, ax = plt.subplots(figsize=(18, 25.5))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 底色
    bg = FancyBboxPatch((0, 0), 1, 1, boxstyle="square,pad=0",
                        facecolor='#F7FBFC', edgecolor='none', zorder=0)
    ax.add_patch(bg)

    # -------------------------------------------------------------
    # 顶部标题横幅 (Header Banner)
    # -------------------------------------------------------------
    title_banner = FancyBboxPatch((0.03, 0.932), 0.94, 0.053,
                                  boxstyle="round,pad=0.008,rounding_size=0.012",
                                  facecolor='#FFFFFF', edgecolor='#7CCCE7', linewidth=2, zorder=2)
    ax.add_patch(title_banner)
    
    ax.text(0.5, 0.966, "京枢智网·畅达末端 —— 总体技术路线图",
            ha='center', va='center', fontsize=21, fontweight='bold', color='#0B3150', zorder=4)
    ax.text(0.5, 0.944, "面向超大城市的末端配送三级协同网络规划与智能决策平台总体架构与技术实现闭环",
            ha='center', va='center', fontsize=11, color='#5D7D90', zorder=4)

    # 7个阶段的高度与Y坐标排布
    card_h = 0.108
    gap = 0.0215
    y_starts = [0.803 - i * (card_h + gap) for i in range(7)]

    # =============================================================
    # 阶段一：现实调研与多源数据底座 (第1~4章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[0], card_h,
        stage_num="01", stage_title="数据底座构建", stage_sub="现实调研与问题驱动", chapter_tag="第 1 ~ 4 章",
        color_accent="#176B96", color_bg="#F2F9FC",
        boxes_data=[
            {"title": "超大城市社区空间路网底座",
             "items": ["亦庄核心区 5 大典型社区 WGS84 矢量边界",
                       "社区内部人车混行微循环路网与拓扑节点",
                       "分拨中心(HUB)、社区驿站与快递柜空间点位",
                       "老旧/低密/高密/商住四类社区形态特征画像"]},
            {"title": "用户行为与多源货量实测",
             "items": ["4316 户居民末端取件习惯深度问卷调研",
                       "08:00—22:00 连续 6 时段动态到件数据",
                       "常态日 vs 大促峰值 (k=1.75~2.0) 波动样本",
                       "自提/上门服务偏好时空异质性分布规律"]},
            {"title": "智能装备与运营约束库",
             "items": ["纯电无人配送微卡巡航载重与货舱容积规格",
                       "末端智能无人配送车电池 SOC 动态消耗模型",
                       "网格快递员人工作业步巡工效与服务耗时基准",
                       "充电桩/换电站空间拓扑与供电功率硬约束"]}
        ]
    )

    # 阶段一 -> 阶段二 连线
    draw_stage_connector(ax, y_starts[0], y_starts[1] + card_h, [
        {"x": 0.32, "text": "社区画像与空间拓扑", "color": "#1E40AF"},
        {"x": 0.58, "text": "时序到件与行为问卷", "color": "#1E40AF"},
        {"x": 0.84, "text": "装备载重与工效参数", "color": "#1E40AF"}
    ])

    # =============================================================
    # 阶段二：多尺度空间与时序需求概率推演 (第5章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[1], card_h,
        stage_num="02", stage_title="需求概率推演", stage_sub="多尺度贝叶斯生成", chapter_tag="第 5 章",
        color_accent="#168AA6", color_bg="#F1FAFB",
        boxes_data=[
            {"title": "空间宏微观层次生成模型",
             "items": ["社区日需求先验: λ_i ~ Gamma(α, β) 层次分布",
                       "楼栋单元微观负荷: 泊松-Gamma 负二项超松弛",
                       "4316 户户数线性驱动机制验证 (R²=0.999)",
                       "空间需求密度梯度、聚类与异质性特征提炼"]},
            {"title": "时序与服务模式动态分解",
             "items": ["08:00-22:00 六时段 Dirichlet-Multinomial 分配",
                       "17:00—20:00 晚高峰负荷集中度校核 (峰值预警)",
                       "自提 vs 上门履约方式动态分流概率矩阵",
                       "需求率先验弹性 (E_μ=1.01) 稳健性响应检验"]},
            {"title": "蒙特卡洛情景推演引擎",
             "items": ["常态平峰 / 大促峰值多情景高保真随机生成",
                       "P50 / P80 / P90 置信分位数全域推演矩阵",
                       "瞬时超载冲击与智能柜满载溢出风险预判",
                       "输出: 四维时空需求张量 D(c, b, t, s) 底座"]}
        ]
    )

    # 阶段二 -> 阶段三 连线
    draw_stage_connector(ax, y_starts[1], y_starts[2] + card_h, [
        {"x": 0.32, "text": "分社区需求密度", "color": "#6D28D9"},
        {"x": 0.58, "text": "自提/上门服务比例", "color": "#6D28D9"},
        {"x": 0.84, "text": "P80/P90 峰值张量", "color": "#6D28D9"}
    ])

    # =============================================================
    # 阶段三：末端配送三级协同网络规划 (第6章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[2], card_h,
        stage_num="03", stage_title="协同网络规划", stage_sub="三阶段选址与定容", chapter_tag="第 6 章",
        color_accent="#138F80", color_bg="#F0FAF8",
        boxes_data=[
            {"title": "阶段一: 有效覆盖与规模定模",
             "items": ["社区出入口物理隔离与道路通行宽度筛查",
                       "80-150m 居民步行黄金自提取件服务半径",
                       "存量设施容量-货量负荷饱和度评价与诊断",
                       "确定各社区微枢纽与智能柜机规模控制上限"]},
            {"title": "阶段二: 约束P-中值选址与分配",
             "items": ["构建 Capacitated P-Median 运筹优化数学模型",
                       "综合最小化加权平均服务距离与设施改造成本",
                       "亦庄 5 大典型社区微枢纽 (Transfer Hub) 优选",
                       "楼栋单元与设施服务可行性热力空间矩阵划分"]},
            {"title": "阶段三: 拓扑互联与容量扩容",
             "items": ["分拨中心(HUB)—社区接驳点—柜机三级拓扑重塑",
                       "智能柜扩容 45% MIP 拐点决策 (彻底消灭爆柜)",
                       "入口级无人配送接驳转运站空间点位固化",
                       "输出: 三级网络物理节点清单与拓扑结构图"]}
        ]
    )

    # 阶段三 -> 阶段四 连线
    draw_stage_connector(ax, y_starts[2], y_starts[3] + card_h, [
        {"x": 0.32, "text": "微枢纽点位与路网", "color": "#0E7490"},
        {"x": 0.58, "text": "楼栋服务范围划分", "color": "#0E7490"},
        {"x": 0.84, "text": "智能柜定容与点位", "color": "#0E7490"}
    ])

    # =============================================================
    # 阶段四：两阶段人机协同运行优化 (第7章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[3], card_h,
        stage_num="04", stage_title="人机协同优化", stage_sub="TSP + 2E-MDVRPTW + ISA / NSGA-II", chapter_tag="第 7 章",
        color_accent="#2F8B5A", color_bg="#F2FBF5",
        boxes_data=[
            {"title": "M1 干线巡回: 2-Opt TSP",
             "items": ["总干线里程最小目标，引入 MTZ 消除子回路",
                       "分拨中心至五社区集约巡回替代独立往返",
                       "纯电无人微卡 SOC 与 20% 安全回航约束",
                       "普通日干线里程 24.84 降至 13.42 km/日"]},
            {"title": "M2/M3 双层人机强同步",
             "items": ["X3 无人车等效运力 400 件，快递员工时红线 480 min",
                       "容量约束 K-Means + 改进模拟退火 ISA 路径寻优",
                       "Dijkstra 真实路网通行时间 + Metropolis 接受准则",
                       "时空交接约束 T_rc^k ≥ A_sr^u + H_r^u"]},
            {"title": "多目标求解与鲁棒决策",
             "items": ["改进 NSGA-II：65 代收敛，解质量提升 17.0%",
                       "Pareto 前沿、HV=0.925 与 TOPSIS 膝点折衷",
                       "N/P15/P20/D-R/D-V/D-L 六情景与 30 固定种子",
                       "输出路径、班次、车辆规模与异常兜底策略"]}
        ]
    )

    # 阶段四 -> 阶段五 连线
    draw_stage_connector(ax, y_starts[3], y_starts[4] + card_h, [
        {"x": 0.32, "text": "干线巡回与班次", "color": "#2F8B5A"},
        {"x": 0.58, "text": "人机时空交接时刻表", "color": "#2F8B5A"},
        {"x": 0.84, "text": "多目标鲁棒运营方案", "color": "#2F8B5A"}
    ])

    # =============================================================
    # 阶段五：系统数字孪生与离散事件仿真 (第8章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[4], card_h,
        stage_num="05", stage_title="动态情景推演", stage_sub="M8 状态转移与硬约束校核", chapter_tag="第 8 章",
        color_accent="#C98418", color_bg="#FFFAED",
        boxes_data=[
            {"title": "M8 状态转移与情景参数标定",
             "items": ["08:00—21:00 按时段推进智能柜占用状态转移",
                       "冻结分时到件权重 A_j(t) 与取件释放率 D_j(t)",
                       "正式定义为确定性情景推演，不标记为随机离散事件仿真",
                       "统一接入 N / P15 / P20 / D-R / D-V / D-L 六类情景"]},
            {"title": "S0 / S1 / S2 三方案情景校核",
             "items": ["S0: 现状多主体独立配送，覆盖与容量硬约束校验",
                       "S1: 网络与设施优化后的统一配送方案",
                       "S2: 网络优化 + 两阶段人机深度协同方案 (To-Be)",
                       "30 个固定种子稳定性统计，输出可比、可追溯评价"]},
            {"title": "瓶颈识别与容量拐点分析",
             "items": ["智能柜占用率不在 100% 处截断，硬约束违反即 INFEASIBLE",
                       "P20 高峰情景驱动主柜与副柜动态定容与扩容",
                       "识别满柜风险、服务超时与设施容量瓶颈",
                       "输出负荷曲线、硬约束状态与候选运营参数包"]}
        ]
    )

    # 阶段五 -> 阶段六 连线
    draw_stage_connector(ax, y_starts[4], y_starts[5] + card_h, [
        {"x": 0.32, "text": "设备利用率与能耗", "color": "#B45309"},
        {"x": 0.58, "text": "里程削减与工时压缩", "color": "#B45309"},
        {"x": 0.84, "text": "削峰填谷与消灭爆柜", "color": "#B45309"}
    ])

    # =============================================================
    # 阶段六：多维综合效益核算与双碳评价 (第9/10章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[5], card_h,
        stage_num="06", stage_title="综合效益评价", stage_sub="降本·增效·减碳核算", chapter_tag="第 9 ~ 10 章",
        color_accent="#C85B4E", color_bg="#FFF4F1",
        boxes_data=[
            {"title": "运营成本与投资效益",
             "items": ["S0→S2 年现金运营成本 245.64 降至 128.58 万元/年",
                       "年现金运营成本改善率 47.7%，采用统一评价口径",
                       "人工总工时 123.52 降至 54.22 人时/日，改善 56.1%",
                       "S2 新增 CAPEX 44.98 万元，模型估算回收期 0.38 年"]},
            {"title": "网络覆盖与服务时效",
             "items": ["干线运输总里程 24.84 降至 13.42 km/日，改善 46.0%",
                       "150 m 服务覆盖率由 6.5% 提升至 100.0%",
                       "日终未完成件量由 1465.1 件降至 0.0 件",
                       "S0 因覆盖/容量硬约束不满足，正式判定为 INFEASIBLE"]},
            {"title": "绿色化与碳排放双口径",
             "items": ["单件碳排 0.0159 降至 0.0081 kgCO2e/件，改善 49.1%",
                       "年运营总碳排 4479.1 升至 5252.9 kgCO2e/年，增加 17.3%",
                       "不得将结果表述为总碳排与单件碳排双降",
                       "绿色评价同时报告运营总量与单位服务强度"]}
        ]
    )

    # 阶段六 -> 阶段七 连线
    draw_stage_connector(ax, y_starts[5], y_starts[6] + card_h, [
        {"x": 0.35, "text": "量化指标体系与算法模型封装", "color": "#B91C1C"},
        {"x": 0.75, "text": "推荐方案参数与分阶段落地路线", "color": "#B91C1C"}
    ])

    # =============================================================
    # 阶段七：智能决策平台研发与工程实施 (第11/12章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[6], card_h,
        stage_num="07", stage_title="系统落地推广", stage_sub="平台四端协同与工程实施", chapter_tag="第 11 ~ 12 章",
        color_accent="#315A72", color_bg="#F5F9FB",
        boxes_data=[
            {"title": "平台架构与数据接口",
             "items": ["Vue 3 + Tailwind 响应式决策控制台",
                       "Leaflet + 高德 WebGIS 数字孪生底图",
                       "FastAPI RESTful API 与统一 JSON 数据模型",
                       "ECharts 5 可视化 + KaTeX 公式渲染"]},
            {"title": "四端协同与模型调度",
             "items": ["运营 / 企业 / 配送员 / 居民四类终端",
                       "/api/overview：网络拓扑与全景指标",
                       "/api/calculate：预测、选址与路径连续求解",
                       "/api/simulation：M8 情景推演与状态回传"]},
            {"title": "工程实施与推广范式",
             "items": ["试点：亦庄 5 社区完成网络布设与流程固化",
                       "成网：沉淀老旧/低密/高密/商住四类配置范式",
                       "推广：跨企业共同配送与端到端统一调度",
                       "反馈：运营数据回流，驱动参数滚动标定"]}
        ]
    )

    # 保存高分辨率图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.08)
    plt.close()
    print(f"Publication-grade technical roadmap successfully generated at: {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    out_img = os.path.join(current_dir, "output", "roadmap", "technical_roadmap_bright.png")
    generate_technical_roadmap(out_img)
