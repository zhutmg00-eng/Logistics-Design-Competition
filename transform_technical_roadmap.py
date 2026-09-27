# -*- coding: utf-8 -*-
from pathlib import Path

src = Path(r"D:\物流设计大赛\generate_technical_roadmap.py")
dst = Path(r"D:\物流设计大赛\generate_technical_roadmap_bright.py")
code = src.read_text(encoding="utf-8")

repls = [
    ("facecolor='#F1F5F9', edgecolor='none', zorder=0", "facecolor='#F7FBFC', edgecolor='none', zorder=0"),
    ("facecolor='#0F172A', edgecolor='#38BDF8', linewidth=2, zorder=2", "facecolor='#FFFFFF', edgecolor='#7CCCE7', linewidth=2, zorder=2"),
    ("ax.text(0.5, 0.966, \"京枢智网·畅达末端 —— 总体技术路线图\",\n            ha='center', va='center', fontsize=21, fontweight='bold', color='#FFFFFF', zorder=4)", "ax.text(0.5, 0.966, \"京枢智网·畅达末端 —— 总体技术路线图\",\n            ha='center', va='center', fontsize=21, fontweight='bold', color='#0B3150', zorder=4)"),
    ("fontsize=11, color='#94A3B8', zorder=4", "fontsize=11, color='#5D7D90', zorder=4"),
    ('color_accent="#1E40AF", color_bg="#EFF6FF"', 'color_accent="#176B96", color_bg="#F2F9FC"'),
    ('color_accent="#6D28D9", color_bg="#F5F3FF"', 'color_accent="#168AA6", color_bg="#F1FAFB"'),
    ('color_accent="#0E7490", color_bg="#ECFEFF"', 'color_accent="#138F80", color_bg="#F0FAF8"'),
    ('color_accent="#15803D", color_bg="#F0FDF4"', 'color_accent="#2F8B5A", color_bg="#F2FBF5"'),
    ('color_accent="#B45309", color_bg="#FFFBEB"', 'color_accent="#C98418", color_bg="#FFFAED"'),
    ('color_accent="#B91C1C", color_bg="#FEF2F2"', 'color_accent="#C85B4E", color_bg="#FFF4F1"'),
    ('color_accent="#0F172A", color_bg="#F8FAFC"', 'color_accent="#315A72", color_bg="#F5F9FB"'),
    ('stage_num="05", stage_title="数字孪生仿真", stage_sub="SimPy 事件驱动压测", chapter_tag="第 8 章"', 'stage_num="05", stage_title="动态情景推演", stage_sub="M8 状态转移与硬约束校核", chapter_tag="第 8 章"'),
    ('{"title": "数字孪生环境与参数标定",', '{"title": "M8 状态转移与情景参数标定",'),
    ('"items": ["亦庄 5 社区真实微循环路网、障碍物与出入口标定",\n                       "车辆巡航速度、启停装卸、充换电服务时延分布",\n                       "快递员步行爬楼与住户签收交接时间经验分布",\n                       "搭建基于 SimPy 的高保真离散事件驱动仿真底座"]}', '"items": ["08:00—21:00 按时段推进智能柜占用状态转移",\n                       "冻结分时到件权重 A_j(t) 与取件释放率 D_j(t)",\n                       "正式定义为确定性情景推演，不标记为随机离散事件仿真",\n                       "统一接入 N / P15 / P20 / D-R / D-V / D-L 六类情景"]}'),
    ('{"title": "三组基准对比与极限压测",', '{"title": "S0 / S1 / S2 三方案情景校核",'),
    ('"items": ["方案 A: 现状基准粗放模式 (多主体纯人工各自往返)",\n                       "方案 B: 优化网络后纯人工步巡配送作业模式",\n                       "方案 C: 优化网络 + 两阶段人机深度协同模式 (To-Be)",\n                       "常态日 vs 大促峰值日极端到件冲击压力测试"]}', '"items": ["S0: 现状多主体独立配送，覆盖与容量硬约束校验",\n                       "S1: 网络与设施优化后的统一配送方案",\n                       "S2: 网络优化 + 两阶段人机深度协同方案 (To-Be)",\n                       "30 个固定种子稳定性统计，输出可比、可追溯评价"]}'),
    ('{"title": "动态运营瓶颈识别与调优",', '{"title": "瓶颈识别与容量拐点分析",'),
    ('"items": ["24 小时智能快件柜时序负荷与满载率实时监测",\n                       "彻底消灭 156% 严重爆柜 (压降至 64.5% 安全线)",\n                       "识别出入口换电等待时延并平滑发车发运节拍",\n                       "动态寻优无人车队规模与网格员弹性派班比例"]}', '"items": ["智能柜占用率不在 100% 处截断，硬约束违反即 INFEASIBLE",\n                       "P20 高峰情景驱动主柜与副柜动态定容与扩容",\n                       "识别满柜风险、服务超时与设施容量瓶颈",\n                       "输出负荷曲线、硬约束状态与候选运营参数包"]}'),
    ('{"title": "全流程运营降本效益",\n             "items": ["综合总运营成本大幅削减 53.6% (经济效益显著)",\n                       "年运营成本从 283.5 万元骤降至 131.4 万元",\n                       "人工薪酬支出重塑, 快递员从重体力转向高价值运维",\n                       "设施与车辆新增投资核算: 静态投资回收期 2.1 年"]}', '{"title": "运营成本与投资效益",\n             "items": ["S0→S2 年现金运营成本 245.64 降至 128.58 万元/年",\n                       "年现金运营成本改善率 47.7%，采用统一评价口径",\n                       "人工总工时 123.52 降至 54.22 人时/日，改善 56.1%",\n                       "S2 新增 CAPEX 44.98 万元，模型估算回收期 0.38 年"]}'),
    ('{"title": "系统作业时效大幅提升",\n             "items": ["干线往返运输总里程大幅削减 46.0% (集约短驳)",\n                       "社区内末端步巡配送里程削减 34.2% (就近履约)",\n                       "网格快递员单日劳动工时压缩 59.8% (有效减负)",\n                       "客户末端履约服务满意度指数跃升至 94.8 分"]}', '{"title": "网络覆盖与服务时效",\n             "items": ["干线运输总里程 24.84 降至 13.42 km/日，改善 46.0%",\n                       "150 m 服务覆盖率由 6.5% 提升至 100.0%",\n                       "日终未完成件量由 1465.1 件降至 0.0 件",\n                       "S0 因覆盖/容量硬约束不满足，正式判定为 INFEASIBLE"]}'),
    ('{"title": "绿色化与双碳减排成效",\n             "items": ["高耗能传统燃油三轮彻底替代为新能源纯电载具",\n                       "末端配送吨公里能耗强度下降 76.4% (深度脱碳)",\n                       "系统全生命周期二氧化碳减排率高达 87.2%",\n                       "有力支撑北京市现代商贸流通与低碳先导区建设"]}', '{"title": "绿色化与碳排放双口径",\n             "items": ["单件碳排 0.0159 降至 0.0081 kgCO2e/件，改善 49.1%",\n                       "年运营总碳排 4479.1 升至 5252.9 kgCO2e/年，增加 17.3%",\n                       "不得将结果表述为总碳排与单件碳排双降",\n                       "绿色评价同时报告运营总量与单位服务强度"]}'),
    ('out_img = os.path.join(current_dir, "docs", "images", "technical_roadmap.png")', 'out_img = os.path.join(current_dir, "output", "roadmap", "technical_roadmap_bright.png")'),
]

for idx, (old, new) in enumerate(repls, 1):
    if old not in code:
        raise SystemExit(f"Replacement {idx} target not found: {old[:100]!r}")
    code = code.replace(old, new, 1)

dst.write_text(code, encoding="utf-8")
print(f"Created {dst}")
