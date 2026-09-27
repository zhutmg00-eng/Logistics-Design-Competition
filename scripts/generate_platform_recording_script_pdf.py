"""Generate the standalone phone-friendly platform demo script PDF."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

OUT = Path("output/pdf/平台录屏脚本_手机版_2分55秒.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont("CN", "C:/Windows/Fonts/msyh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("CNB", "C:/Windows/Fonts/msyhbd.ttc", subfontIndex=0))

W, H = 360, 640
INK = colors.HexColor("#172A35")
MUTED = colors.HexColor("#526A76")
CYAN = colors.HexColor("#087F9C")
CYAN_DARK = colors.HexColor("#07536A")
BLUE = colors.HexColor("#1E6FA5")
GREEN = colors.HexColor("#16805D")
AMBER = colors.HexColor("#A96612")
RED = colors.HexColor("#B42318")
LINE = colors.HexColor("#C9D7DE")
SOFT = colors.HexColor("#F2F7F9")
PALE_CYAN = colors.HexColor("#E7F5F8")
PALE_GREEN = colors.HexColor("#ECF8F2")
PALE_AMBER = colors.HexColor("#FFF7E7")

ss = getSampleStyleSheet()
title = ParagraphStyle("title", fontName="CNB", fontSize=20, leading=25, textColor=INK, spaceAfter=3)
subtitle = ParagraphStyle("subtitle", fontName="CN", fontSize=8.8, leading=12.5, textColor=MUTED, spaceAfter=8)
section = ParagraphStyle("section", fontName="CNB", fontSize=12.5, leading=16, textColor=CYAN_DARK, spaceBefore=3, spaceAfter=5)
step_title = ParagraphStyle("step_title", fontName="CNB", fontSize=11, leading=14, textColor=INK)
timer = ParagraphStyle("timer", fontName="CNB", fontSize=8, leading=10, textColor=colors.white, alignment=1)
label = ParagraphStyle("label", fontName="CNB", fontSize=7.5, leading=9.5, textColor=CYAN_DARK)
body = ParagraphStyle("body", fontName="CN", fontSize=8.15, leading=11.7, textColor=INK)
small = ParagraphStyle("small", fontName="CN", fontSize=7.45, leading=10.7, textColor=MUTED)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=9, firstLineIndent=-7, spaceAfter=2)
quote = ParagraphStyle("quote", fontName="CN", fontSize=8.25, leading=12.1, textColor=CYAN_DARK)

def P(t, st=body): return Paragraph(t, st)

def box(rows, bg=colors.white, border=LINE, accent=CYAN, pad=7):
    t = Table(rows, colWidths=[324], style=TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), bg),
        ("BOX", (0,0), (-1,-1), 0.8, border),
        ("LINEBEFORE", (0,0), (0,-1), 3.2, accent),
        ("LEFTPADDING", (0,0), (-1,-1), pad), ("RIGHTPADDING", (0,0), (-1,-1), pad),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return t

def step(number, duration, title_text, purpose, action, narration, focus, accent=CYAN):
    badge = Table([[P(number, timer), P(duration, timer)]], colWidths=[26, 70], rowHeights=[17], style=TableStyle([
        ("BACKGROUND", (0,0), (0,0), accent), ("BACKGROUND", (1,0), (1,0), CYAN_DARK),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 2), ("RIGHTPADDING", (0,0), (-1,-1), 2),
    ]))
    head = Table([[badge, P(title_text, step_title)]], colWidths=[96, 216], rowHeights=[24], style=TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 2),
    ]))
    rows = [[head], [P("本段目的", label)], [P(purpose, small)], [P("操作", label)], [P(action, body)], [P("口播", label)], [P(narration, body)], [P("画面重点", label)], [P(focus, small)]]
    return KeepTogether([box(rows), Spacer(1, 6)])

def on_page(c, doc):
    c.saveState()
    c.setFillColor(colors.HexColor("#E8F4F7")); c.rect(0, H-9, W, 9, fill=1, stroke=0)
    c.setFillColor(CYAN); c.rect(0, H-9, W*min(doc.page,5)/5, 9, fill=1, stroke=0)
    c.setFont("CN", 6.7); c.setFillColor(MUTED); c.drawString(18, 14, "面向超大城市的末端配送协同决策平台")
    c.drawRightString(W-18, 14, f"{doc.page} / 5"); c.restoreState()

story=[]
# Page 1: project framing, users, value and opening narration
story += [Spacer(1,13), P("平台录屏脚本", title), P("手机竖屏版 | 建议 2 分 55 秒 | 面向谁、解决什么、展示什么", subtitle)]
story += [P("一句话定位", section), box([[P("平台面向超大城市社区末端共同配送的组织者与运营管理者，把需求预测、设施定容、人车协同、运行仿真和 AI 应急调度放进同一条决策链，回答“哪里需要多少运力、设施怎么配、异常如何重排”。", quote)]], bg=PALE_CYAN, accent=CYAN)]
story += [Spacer(1,7), P("主要用户", section)]
story += [P("1. 物流平台/共同配送运营方：统一组织 HUB、驿站、智能柜、无人车和快递员。", bullet)]
story += [P("2. 社区末端设施运营方：判断柜体是否够用、是否扩容、服务半径是否达标。", bullet)]
story += [P("3. 街道或园区规划管理者：比较现状与优化方案，评估成本、效率和风险。", bullet)]
story += [Spacer(1,5), P("视频主线", section)]
flow = Table([[P("预测需求", label), P("→", label), P("规划设施", label), P("→", label), P("调度人车", label), P("→", label), P("仿真风险", label), P("→", label), P("AI 应急", label)]], colWidths=[49,12,49,12,49,12,49,12,56], rowHeights=[25], style=TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), SOFT), ("BOX", (0,0), (-1,-1), 0.7, LINE), ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("LEFTPADDING", (0,0), (-1,-1), 2), ("RIGHTPADDING", (0,0), (-1,-1), 2),
]))
story += [flow, Spacer(1,8)]
story += [P("开场口播（第 1 步使用）", section)]
story += [P("“这是一个面向超大城市社区末端共同配送的一体化决策平台。它服务的不是单个快递柜，而是需要同时管理需求、设施、无人车和配送员的运营方。平台把需求预测、选址定容、人车协同、运行仿真和应急调度串成一条完整决策链，帮助管理者比较方案、量化效益并快速下发执行。”", quote)]
story += [PageBreak()]

# Page 2: steps 1 and 2
story += [Spacer(1,12), P("先讲价值：为什么必须优化", section)]
story += [step("01", "00:00-00:18", "项目定位与全片主线", "先让观众知道平台服务谁、解决什么问题，避免一上来只剩地图和指标。", "保持主界面 → 指向顶部平台名称和模块导航 → 不点击其他按钮", "这是一个面向超大城市社区末端共同配送的一体化决策平台。核心用户是需要同时管理需求、设施、无人车和配送员的运营方。平台把预测、规划、调度、仿真和应急放进同一条决策链，回答“运力怎么配、设施怎么建、异常怎么重排”。", "先停 2 秒，让观众看清平台名称和模块结构。", BLUE)]
story += [step("02", "00:18-00:43", "S0 与 S2 全景对比", "展示平台不是地图看板，而是能给出可量化方案比较的决策工具。", "全域(5社区) → 叠图对比 → N 普通日 → 保持左右分屏", "左边 S0 代表现有分散配送：车辆独立往返、人工负担重、爆柜风险高。右边 S2 是平台推荐的人机协同方案：HUB 巡回、设施扩容、无人车投柜、快递员精准上门。系统量化显示干线里程下降 46%，人工工时下降 56.1%，年现金成本从 245.6 万元降到 128.6 万元。", "红虚线看现状问题，青实线看优化路径；重点停在地图、干线里程、人工工时和年成本。", RED)]
story += [PageBreak()]

# Page 3: trust and planning
story += [Spacer(1,12), P("再讲方法：数据和模型如何支撑决策", section)]
story += [step("03", "00:43-01:08", "GIS 数字孪生与需求预测", "解释平台结论为何可信，以及后续设施和路径从哪里获得需求输入。", "C04 亦城茗苑 → 数字孪生 → 聚焦 → 需求预测 → P20 大促峰值", "优化首先落在真实空间上。系统接入 5 个社区的 WGS84 边界、楼栋、设施和内部路网，显示到高德底图时自动校正坐标系。需求模块再通过 P50、P80、P90 分位数描述常态与峰值需求，并拆分智能柜自提和送货上门。", "先看真实社区边界和三级网络，再看概率分位与 08:00-21:00 到达波峰。", CYAN)]
story += [step("04", "01:08-01:33", "设施选址定容", "展示从需求预测到设施方案的转化，解决“柜体够不够、建在哪里”的问题。", "保持 C04 和 P20 → 进入选址定容", "进入选址定容后，平台在容量约束和 150 米便民服务半径下，决定主柜、副柜和楼栋分配。它会优先利用存量设施，再对高风险社区进行精准扩容，避免盲目新增和局部爆柜。", "重点看有效容量、峰值饱和度、平均步行距离和投资回收。", GREEN)]
story += [PageBreak()]

# Page 4: execution and resilience
story += [Spacer(1,12), P("接着讲执行：方案如何落地并保持韧性", section)]
story += [step("05", "01:33-01:58", "两级人车协同路径", "说明无人车与快递员不是简单替代关系，而是职责重新分工。", "进入人车协同 → 保持 S2 → 查看社区路径", "无人车负责 HUB 到社区接驳点、再到柜机的微循环投柜和补货；快递员专注老年住户、大件和需要上门的楼栋。两级协同既减少重复搬运，也保留了末端服务的人文关怀。", "蓝线讲无人车巡航，橙色虚线讲适老上门；强调服务时间窗和工时红线。", CYAN)]
story += [step("06", "01:58-02:28", "动态仿真与 AI 应急调度", "展示平台不仅能做静态规划，还能验证峰值压力并处理突发扰动。", "仿真对抗 → 大促峰值 → AI 应急调度 → AI 中枢 → 暴雪极端调度重排", "仿真模块用柜体动态占用和班次甘特图验证方案在峰值下的承载能力。异常发生时，AI 中枢读取当前社区遥测数据，结合运筹模型生成扩容、分流和重排建议，并形成可下发工单。", "等待“推理中”结束，出现正式报告后再讲解；不要展示内部思考过程或 API Key。", RED)]
story += [PageBreak()]

# Page 5: wrap-up
story += [Spacer(1,12), P("最后收束：平台价值与可信结论", section)]
story += [step("07", "02:28-02:55", "算法看板与总结", "用模型严谨性收尾，并明确平台最终交付给管理者什么。", "打开算法看板 → 展示 M6 → 回到主界面", "最后以 M6 为例，平台把目标函数、决策变量和容量约束放在同一套模型体系中。它最终交付给管理者的，不是一张地图，而是一组可比较、可解释、可执行的末端配送决策。平台形成“需求可预测、设施可规划、人车可协同、风险可仿真、异常可应急”的闭环。", "只展示 M6 一页；结尾回到三个结果：干线 -46%、人工工时 -56.1%、年现金成本 -47.7%。", CYAN)]
story += [box([[P("可信表达提醒", label)], [P("平台展示成本、工时和干线显著改善；碳排放必须区分单件与总量，S2 年运营总碳排高于 S0，不能简单宣称“全面下降”。", small)]], bg=PALE_AMBER, border=colors.HexColor("#E4C98E"), accent=AMBER)]
story += [Spacer(1,7), box([[P("录屏前检查", label)], [P("浏览器全屏 | 点击“录屏模式” | 手机打开本 PDF | 不打开 AI 设置、约束明细、四端协同", small)]], bg=PALE_GREEN, border=colors.HexColor("#A7CBB9"), accent=GREEN)]

doc=BaseDocTemplate(str(OUT), pagesize=(W,H), leftMargin=18, rightMargin=18, topMargin=10, bottomMargin=24,
                    title="平台录屏脚本_手机版_2分55秒", author="京枢智网")
frame=Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="mobile", frames=[frame], onPage=on_page)])
doc.build(story)
print(OUT.resolve())
