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
                        facecolor='#F1F5F9', edgecolor='none', zorder=0)
    ax.add_patch(bg)

    # -------------------------------------------------------------
    # 顶部标题横幅 (Header Banner)
    # -------------------------------------------------------------
    title_banner = FancyBboxPatch((0.03, 0.932), 0.94, 0.053,
                                  boxstyle="round,pad=0.008,rounding_size=0.012",
                                  facecolor='#0F172A', edgecolor='#38BDF8', linewidth=2, zorder=2)
    ax.add_patch(title_banner)
    
    ax.text(0.5, 0.966, "京枢智网·畅达末端 —— 总体技术路线图",
            ha='center', va='center', fontsize=21, fontweight='bold', color='#FFFFFF', zorder=4)
    ax.text(0.5, 0.944, "面向超大城市的末端配送三级协同网络规划与智能决策平台总体架构与技术实现闭环",
            ha='center', va='center', fontsize=11, color='#94A3B8', zorder=4)

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
        color_accent="#1E40AF", color_bg="#EFF6FF",
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
        color_accent="#6D28D9", color_bg="#F5F3FF",
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
        color_accent="#0E7490", color_bg="#ECFEFF",
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
        stage_num="04", stage_title="人机协同优化", stage_sub="2E-MDVRPTW-DC求解", chapter_tag="第 7 章",
        color_accent="#15803D", color_bg="#F0FDF4",
        boxes_data=[
            {"title": "一级巡回: 无人微卡干线短驳",
             "items": ["纯电无人微卡从分拨中心集约循环补货接驳",
                       "动力电池荷电状态 (SOC) 连续递减与回航约束",
                       "预留 20% 安全电量余量防止途中馈电抛锚",
                       "绕行系数修正的 Dijkstra 道路通行最短时间"]},
            {"title": "二级履约: 人机强同步交接",
             "items": ["末端无人车投柜补货 vs 网格快递员上门履约",
                       "时空交接强同步约束: T_rc^k ≥ A_sr^u + H_r^u",
                       "两级载重沿途连续守恒衰减与容量约束方程",
                       "客户时间窗违约惩罚函数与非线性满意度效用"]},
            {"title": "改进多目标进化算法 (NSGA-II)",
             "items": ["65 代快速收敛, 解质量较标准遗传算法提升 17.0%",
                       "超体积指标演化 (HV=0.925) 验证 Pareto 前沿",
                       "成本-满意度 Pareto 前沿与 TOPSIS 膝点折衷解",
                       "动态班次触发、满柜溢出与故障人工兜底流程"]}
        ]
    )

    # 阶段四 -> 阶段五 连线
    draw_stage_connector(ax, y_starts[3], y_starts[4] + card_h, [
        {"x": 0.32, "text": "干线微卡发车排班", "color": "#15803D"},
        {"x": 0.58, "text": "人机时空同步时刻表", "color": "#15803D"},
        {"x": 0.84, "text": "Pareto 折衷运营解", "color": "#15803D"}
    ])

    # =============================================================
    # 阶段五：系统数字孪生与离散事件仿真 (第8章)
    # =============================================================
    draw_phase_card(
        ax, y_starts[4], card_h,
        stage_num="05", stage_title="数字孪生仿真", stage_sub="SimPy 事件驱动压测", chapter_tag="第 8 章",
        color_accent="#B45309", color_bg="#FFFBEB",
        boxes_data=[
            {"title": "数字孪生环境与参数标定",
             "items": ["亦庄 5 社区真实微循环路网、障碍物与出入口标定",
                       "车辆巡航速度、启停装卸、充换电服务时延分布",
                       "快递员步行爬楼与住户签收交接时间经验分布",
                       "搭建基于 SimPy 的高保真离散事件驱动仿真底座"]},
            {"title": "三组基准对比与极限压测",
             "items": ["方案 A: 现状基准粗放模式 (多主体纯人工各自往返)",
                       "方案 B: 优化网络后纯人工步巡配送作业模式",
                       "方案 C: 优化网络 + 两阶段人机深度协同模式 (To-Be)",
                       "常态日 vs 大促峰值日极端到件冲击压力测试"]},
            {"title": "动态运营瓶颈识别与调优",
             "items": ["24 小时智能快件柜时序负荷与满载率实时监测",
                       "彻底消灭 156% 严重爆柜 (压降至 64.5% 安全线)",
                       "识别出入口换电等待时延并平滑发车发运节拍",
                       "动态寻优无人车队规模与网格员弹性派班比例"]}
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
        color_accent="#B91C1C", color_bg="#FEF2F2",
        boxes_data=[
            {"title": "全流程运营降本效益",
             "items": ["综合总运营成本大幅削减 53.6% (经济效益显著)",
                       "年运营成本从 283.5 万元骤降至 131.4 万元",
                       "人工薪酬支出重塑, 快递员从重体力转向高价值运维",
                       "设施与车辆新增投资核算: 静态投资回收期 2.1 年"]},
            {"title": "系统作业时效大幅提升",
             "items": ["干线往返运输总里程大幅削减 46.0% (集约短驳)",
                       "社区内末端步巡配送里程削减 34.2% (就近履约)",
                       "网格快递员单日劳动工时压缩 59.8% (有效减负)",
                       "客户末端履约服务满意度指数跃升至 94.8 分"]},
            {"title": "绿色化与双碳减排成效",
             "items": ["高耗能传统燃油三轮彻底替代为新能源纯电载具",
                       "末端配送吨公里能耗强度下降 76.4% (深度脱碳)",
                       "系统全生命周期二氧化碳减排率高达 87.2%",
                       "有力支撑北京市现代商贸流通与低碳先导区建设"]}
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
        stage_num="07", stage_title="系统落地实施", stage_sub="平台原型与工程推广", chapter_tag="第 11 ~ 12 章",
        color_accent="#0F172A", color_bg="#F8FAFC",
        boxes_data=[
            {"title": "京枢智网·智能决策支持平台原型系统 (Web 交互)",
             "items": ["空间数字孪生底座: 接入高精地图与社区指数, 支持一键自动化运筹求解",
                       "运筹算法控制台: 在线执行改进 NSGA-II 算法, 实时输出最优人机协作排班与路径",
                       "As-Is vs To-Be 全景同屏对抗: 里程/工时/成本/碳排/爆柜风险五维遥测对比大屏"]},
            {"title": "分阶段工程实施安排与超大城市推广范式",
             "items": ["第一阶段(试点实证): 亦庄 5 大社区网络布设, 固化无人微卡与无人车路权与作业流程",
                       "第二阶段(规模成网): 沉淀老旧、低密、高密、商住四类典型社区的标准化拓扑配置范式",
                       "第三阶段(全域推广): 深化跨快递企业共配机制, 赋能北京市超大城市末端治理现代化"]}
        ]
    )

    # 保存高分辨率图像
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight', pad_inches=0.08)
    plt.close()
    print(f"Publication-grade technical roadmap successfully generated at: {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    out_img = os.path.join(current_dir, "docs", "images", "technical_roadmap.png")
    generate_technical_roadmap(out_img)
