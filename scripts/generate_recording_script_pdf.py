"""Generate the standalone, phone-friendly recording script PDF."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

OUT = Path("output/pdf/录屏演示脚本_手机版.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Windows CJK fonts; the font files are present in this environment.
pdfmetrics.registerFont(TTFont("CN", "C:/Windows/Fonts/msyh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("CNB", "C:/Windows/Fonts/msyhbd.ttc", subfontIndex=0))

PAGE_W, PAGE_H = 360, 640
INK = colors.HexColor("#172A35")
MUTED = colors.HexColor("#526A76")
CYAN = colors.HexColor("#087F9C")
CYAN_DARK = colors.HexColor("#07536A")
GREEN = colors.HexColor("#16805D")
AMBER = colors.HexColor("#A96612")
RED = colors.HexColor("#B42318")
LINE = colors.HexColor("#C9D7DE")
SOFT = colors.HexColor("#F2F7F9")
PALE_CYAN = colors.HexColor("#E7F5F8")
PALE_GREEN = colors.HexColor("#ECF8F2")
PALE_AMBER = colors.HexColor("#FFF7E7")

styles = getSampleStyleSheet()
title = ParagraphStyle("title", fontName="CNB", fontSize=21, leading=27, textColor=INK, spaceAfter=3)
subtitle = ParagraphStyle("subtitle", fontName="CN", fontSize=9.2, leading=13, textColor=MUTED, spaceAfter=8)
section = ParagraphStyle("section", fontName="CNB", fontSize=13, leading=17, textColor=CYAN_DARK, spaceBefore=3, spaceAfter=5)
step_title = ParagraphStyle("step_title", fontName="CNB", fontSize=11.5, leading=15, textColor=INK)
time_style = ParagraphStyle("time", fontName="CNB", fontSize=8.2, leading=10, textColor=colors.white, alignment=1)
label = ParagraphStyle("label", fontName="CNB", fontSize=7.8, leading=10, textColor=CYAN_DARK)
body = ParagraphStyle("body", fontName="CN", fontSize=8.4, leading=12.1, textColor=INK)
body_small = ParagraphStyle("body_small", fontName="CN", fontSize=7.7, leading=11.1, textColor=MUTED)
bullet = ParagraphStyle("bullet", parent=body, leftIndent=9, firstLineIndent=-7, spaceAfter=2)
note = ParagraphStyle("note", parent=body_small, textColor=CYAN_DARK)

def P(text, style=body):
    return Paragraph(text, style)

def rule(color=LINE, width=1):
    return Table([[""]], colWidths=[324], rowHeights=[0.7], style=TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), color),
        ("BOX", (0,0), (-1,-1), 0, color),
    ]))

def step_card(number, duration, title_text, action, narration, focus, accent=CYAN):
    badge = Table([[P(f"{number}", time_style), P(duration, time_style)]], colWidths=[28, 60], rowHeights=[17], style=TableStyle([
        ("BACKGROUND", (0,0), (0,0), accent),
        ("BACKGROUND", (1,0), (1,0), CYAN_DARK),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 2), ("RIGHTPADDING", (0,0), (-1,-1), 2),
    ]))
    head = Table([[badge, P(title_text, step_title)]], colWidths=[91, 221], rowHeights=[25], style=TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 0), ("RIGHTPADDING", (0,0), (-1,-1), 2),
    ]))
    content = [
        head,
        P("操作", label),
        P(action, body),
        Spacer(1, 3),
        P("口播", label),
        P(narration, body),
        Spacer(1, 3),
        P("画面重点", label),
        P(focus, body_small),
    ]
    box = Table([[""], [content]], colWidths=[324], style=TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.white),
        ("BOX", (0,0), (-1,-1), 0.8, LINE),
        ("LINEBEFORE", (0,0), (0,-1), 3.2, accent),
        ("LEFTPADDING", (0,0), (-1,-1), 7),
        ("RIGHTPADDING", (0,0), (-1,-1), 7),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return KeepTogether([box, Spacer(1, 7)])

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(colors.HexColor("#E8F4F7"))
    canvas.rect(0, PAGE_H-9, PAGE_W, 9, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.rect(0, PAGE_H-9, PAGE_W * min(doc.page, 4) / 4, 9, fill=1, stroke=0)
    canvas.setFont("CN", 6.8)
    canvas.setFillColor(MUTED)
    canvas.drawString(18, 15, "京枢智网 · 录屏演示脚本")
    canvas.drawRightString(PAGE_W-18, 15, f"{doc.page} / 4")
    canvas.restoreState()

story = []
# Page 1: preparation and timeline
story += [
    Spacer(1, 13),
    P("录屏演示脚本", title),
    P("手机竖屏版 · 建议总时长 2 分 45 秒", subtitle),
    P("录屏前准备", section),
    P("1. 电脑打开网页并点击右上角“录屏模式”。", bullet),
    P("2. 浏览器全屏，手机打开本 PDF，按页往下看。", bullet),
    P("3. 确认 AI 调度中枢显示“云端大模型在线”；若未配置，仍可使用离线推演。", bullet),
    P("4. 全程不要打开：AI 设置、约束明细、四端协同。", bullet),
    Spacer(1, 6),
    P("时间轴", section),
]
timeline = [
    ["01", "00:00-00:20", "全域态势与方案反差"],
    ["02", "00:20-00:45", "真实 GIS 定位与数字孪生"],
    ["03", "00:45-01:05", "需求预测与 P20 峰值情景"],
    ["04", "01:05-01:25", "MIP 选址定容与扩容"],
    ["05", "01:25-01:50", "人机协同路径"],
    ["06", "01:50-02:20", "AI 应急调度与流式推演"],
    ["07", "02:20-02:45", "算法看板与总结"],
]
timeline_table = Table([[P(a, label), P(b, body), P(c, body)] for a,b,c in timeline], colWidths=[24, 75, 225], rowHeights=[24]*7)
timeline_table.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), SOFT),
    ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.white, SOFT]),
    ("BOX", (0,0), (-1,-1), 0.7, LINE),
    ("INNERGRID", (0,0), (-1,-1), 0.35, LINE),
    ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5),
]))
story += [timeline_table, Spacer(1, 8)]
story += [Table([[P("节奏提醒", label)], [P("每一步先停 1 秒再操作；口播按本页文字读，不必额外补充模型名称。", body)]], colWidths=[324], style=TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), PALE_AMBER),
    ("BOX", (0,0), (-1,-1), 0.8, colors.HexColor("#E4C98E")),
    ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))]
story += [PageBreak()]

# Page 2: steps 1 and 2
story += [Spacer(1, 12), P("前半段：建立问题与空间底座", section)]
story += [step_card("01", "00:00-00:20", "全域态势与方案反差",
    "全域(5社区) → 方案模式“叠图对比” → 情景“N 普通日” → 保持左右分屏",
    "先看现状与推荐方案的差异。S0 使用独立往返干线和纯人工作业，存在高工时与爆柜风险；S2 通过巡回干线、设施扩容和人车协同，把干线里程降低 46%，人工工时降低 56.1%，预计年节约约 117 万元。",
    "红虚线表示现状往返，青实线表示 M1 巡回；右侧重点停在干线、工时和年节约三项指标。", RED)]
story += [step_card("02", "00:20-00:45", "真实 GIS 定位与数字孪生",
    "点击 C04 亦城茗苑 → 进入“数字孪生” → 点击地图“聚焦”",
    "这里展示亦城茗苑的真实空间底座，包括 HUB、社区接驳点、楼栋和内部路网。地图数据来自 WGS84，在高德底图上显示前会自动校正到 GCJ-02，因此社区边界和设施位置能够与真实地点对应。",
    "让 C04 社区边界和内部路网占满地图；指出三级网络和 M1 巡回干线 13.42 公里。", CYAN)]
story += [PageBreak()]

# Page 3: steps 3-5
story += [Spacer(1, 12), P("中段：需求、设施与协同运行", section)]
story += [step_card("03", "00:45-01:05", "需求预测与 P20 峰值情景",
    "保持 C04 → 进入“需求预测” → 情景切换到“P20 大促峰值”",
    "系统先估计社区需求分布，再拆分智能柜自提和送货上门需求。P50、P80、P90 分位用于覆盖不同风险情景，右侧时段曲线展示 08:00 到 21:00 的到达波峰。",
    "重点看概率分位、自提/上门比例，以及峰值时段曲线。", AMBER)]
story += [step_card("04", "01:05-01:25", "MIP 选址定容与扩容",
    "进入“选址定容” → 保持 C04 和 P20 情景",
    "在峰值需求下，系统通过混合整数规划决定主柜、副柜和楼栋分配。方案同时满足容量约束与 150 米便民服务半径，避免只扩容不解决覆盖问题。",
    "停在有效容量、峰值饱和度和投资回收三项关键结果。", GREEN)]
story += [step_card("05", "01:25-01:50", "人机协同路径与班次衔接",
    "进入“人车协同” → 保持 S2 人机协同 → 查看地图路径",
    "无人车承担社区微循环和驿站到柜机的接驳，快递员只处理需要上门的楼栋。这样既减少重复搬运，也能保留对老年住户和重件用户的上门服务。",
    "蓝色路线讲无人车巡航，橙色虚线讲适老上门步巡；不必逐条展开所有表格。", CYAN)]
story += [PageBreak()]

# Page 4: steps 6-7 and closing checklist
story += [Spacer(1, 12), P("后段：AI 决策与学术闭环", section)]
story += [step_card("06", "01:50-02:20", "AI 应急调度与流式推演",
    "进入“AI 应急调度” → 打开 AI 调度中枢 → 点击“暴雪极端调度重排”",
    "AI 中枢读取当前社区遥测数据，联合 M1 到 M8 运筹模型生成应急重排建议。正式回答会给出风险判断、调度动作和可下发工单，内部思考过程不会展示。",
    "等待“推理中”结束并出现正式报告后再继续；不要打开 AI 设置或 API Key。", RED)]
story += [step_card("07", "02:20-02:45", "算法看板与总结",
    "打开“算法看板” → 选择 M6 → 停留 3 秒后回到主界面",
    "最后以 M6 为例说明目标函数、决策变量和容量约束。整套平台从需求预测、设施定容，到人车协同和应急重排，形成了可计算、可对比、可执行的决策闭环。",
    "只展示 M6 一页；结尾回到三个结果：干线 -46%、人工工时 -56.1%、年节约约 117 万元。", CYAN)]
story += [Spacer(1, 4), Table([[P("结束检查", label)], [P("已回到主界面  |  已说出三个核心结果  |  停止录制", body)]], colWidths=[324], style=TableStyle([
    ("BACKGROUND", (0,0), (-1,-1), PALE_GREEN),
    ("BOX", (0,0), (-1,-1), 0.8, colors.HexColor("#A7CBB9")),
    ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
    ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
]))]

doc = BaseDocTemplate(str(OUT), pagesize=(PAGE_W, PAGE_H), leftMargin=18, rightMargin=18, topMargin=10, bottomMargin=25,
                      title="录屏演示脚本_手机版", author="京枢智网")
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="mobile", frames=[frame], onPage=header_footer)])
doc.build(story)
print(OUT.resolve())
