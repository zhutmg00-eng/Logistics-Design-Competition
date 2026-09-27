# -*- coding: utf-8 -*-
from pathlib import Path
p = Path(r"D:\物流设计大赛\generate_technical_roadmap_bright.py")
s = p.read_text(encoding="utf-8")
repls = [
(
'''        stage_num="04", stage_title="人机协同优化", stage_sub="2E-MDVRPTW-DC求解", chapter_tag="第 7 章",''',
'''        stage_num="04", stage_title="人机协同优化", stage_sub="TSP + 2E-MDVRPTW + ISA / NSGA-II", chapter_tag="第 7 章",'''
),
(
'''            {"title": "一级巡回: 无人微卡干线短驳",
             "items": ["纯电无人微卡从分拨中心集约循环补货接驳",
                       "动力电池荷电状态 (SOC) 连续递减与回航约束",
                       "预留 20% 安全电量余量防止途中馈电抛锚",
                       "绕行系数修正的 Dijkstra 道路通行最短时间"]},''',
'''            {"title": "M1 干线巡回: 2-Opt TSP",
             "items": ["总干线里程最小目标，引入 MTZ 消除子回路",
                       "分拨中心至五社区集约巡回替代独立往返",
                       "纯电无人微卡 SOC 与 20% 安全回航约束",
                       "普通日干线里程 24.84 降至 13.42 km/日"]},'''
),
(
'''            {"title": "二级履约: 人机强同步交接",
             "items": ["末端无人车投柜补货 vs 网格快递员上门履约",
                       "时空交接强同步约束: T_rc^k ≥ A_sr^u + H_r^u",
                       "两级载重沿途连续守恒衰减与容量约束方程",
                       "客户时间窗违约惩罚函数与非线性满意度效用"]},''',
'''            {"title": "M2/M3 双层人机强同步",
             "items": ["X3 无人车等效运力 400 件，快递员工时红线 480 min",
                       "容量约束 K-Means + 改进模拟退火 ISA 路径寻优",
                       "Dijkstra 真实路网通行时间 + Metropolis 接受准则",
                       "时空交接约束 T_rc^k ≥ A_sr^u + H_r^u"]},'''
),
(
'''            {"title": "改进多目标进化算法 (NSGA-II)",
             "items": ["65 代快速收敛, 解质量较标准遗传算法提升 17.0%",
                       "超体积指标演化 (HV=0.925) 验证 Pareto 前沿",
                       "成本-满意度 Pareto 前沿与 TOPSIS 膝点折衷解",
                       "动态班次触发、满柜溢出与故障人工兜底流程"]}''',
'''            {"title": "多目标求解与鲁棒决策",
             "items": ["改进 NSGA-II：65 代收敛，解质量提升 17.0%",
                       "Pareto 前沿、HV=0.925 与 TOPSIS 膝点折衷",
                       "N/P15/P20/D-R/D-V/D-L 六情景与 30 固定种子",
                       "输出路径、班次、车辆规模与异常兜底策略"]}'''
),
(
'''        {"x": 0.32, "text": "干线微卡发车排班", "color": "#15803D"},
        {"x": 0.58, "text": "人机时空同步时刻表", "color": "#15803D"},
        {"x": 0.84, "text": "Pareto 折衷运营解", "color": "#15803D"}''',
'''        {"x": 0.32, "text": "干线巡回与班次", "color": "#2F8B5A"},
        {"x": 0.58, "text": "人机时空交接时刻表", "color": "#2F8B5A"},
        {"x": 0.84, "text": "多目标鲁棒运营方案", "color": "#2F8B5A"}'''
),
(
'''        stage_num="07", stage_title="系统落地实施", stage_sub="平台原型与工程推广", chapter_tag="第 11 ~ 12 章",''',
'''        stage_num="07", stage_title="系统落地推广", stage_sub="平台四端协同与工程实施", chapter_tag="第 11 ~ 12 章",'''
),
(
'''            {"title": "京枢智网·智能决策支持平台原型系统 (Web 交互)",
             "items": ["空间数字孪生底座: 接入高精地图与社区指数, 支持一键自动化运筹求解",
                       "运筹算法控制台: 在线执行改进 NSGA-II 算法, 实时输出最优人机协作排班与路径",
                       "As-Is vs To-Be 全景同屏对抗: 里程/工时/成本/碳排/爆柜风险五维遥测对比大屏"]},
            {"title": "分阶段工程实施安排与超大城市推广范式",
             "items": ["第一阶段(试点实证): 亦庄 5 大社区网络布设, 固化无人微卡与无人车路权与作业流程",
                       "第二阶段(规模成网): 沉淀老旧、低密、高密、商住四类典型社区的标准化拓扑配置范式",
                       "第三阶段(全域推广): 深化跨快递企业共配机制, 赋能北京市超大城市末端治理现代化"]}'''
,
'''            {"title": "平台架构与数据接口",
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
                       "反馈：运营数据回流，驱动参数滚动标定"]}'''
),
]
for i,(a,b) in enumerate(repls,1):
    if a not in s:
        raise SystemExit(f"target {i} missing")
    s=s.replace(a,b,1)
p.write_text(s,encoding="utf-8")
print("Enhanced phase 4 and phase 7.")
