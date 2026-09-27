"""Generate the detailed defense recording script PDF (phone portrait)."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Frame, KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle

OUT = Path("output/pdf/平台录屏脚本_答辩详细版_3分钟.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)
pdfmetrics.registerFont(TTFont("CN", "C:/Windows/Fonts/msyh.ttc", subfontIndex=0))
pdfmetrics.registerFont(TTFont("CNB", "C:/Windows/Fonts/msyhbd.ttc", subfontIndex=0))

W,H=360,640
INK=colors.HexColor("#172A35"); MUTED=colors.HexColor("#526A76")
CYAN=colors.HexColor("#087F9C"); DARK=colors.HexColor("#07536A"); BLUE=colors.HexColor("#1E6FA5")
GREEN=colors.HexColor("#16805D"); AMBER=colors.HexColor("#A96612"); RED=colors.HexColor("#B42318")
LINE=colors.HexColor("#C9D7DE"); SOFT=colors.HexColor("#F2F7F9")
PALE_CYAN=colors.HexColor("#E7F5F8"); PALE_GREEN=colors.HexColor("#ECF8F2"); PALE_AMBER=colors.HexColor("#FFF7E7")
title=ParagraphStyle("title",fontName="CNB",fontSize=20,leading=25,textColor=INK,spaceAfter=3)
subtitle=ParagraphStyle("subtitle",fontName="CN",fontSize=8.6,leading=12.4,textColor=MUTED,spaceAfter=8)
section=ParagraphStyle("section",fontName="CNB",fontSize=12.4,leading=16,textColor=DARK,spaceBefore=3,spaceAfter=5)
step_title=ParagraphStyle("step_title",fontName="CNB",fontSize=10.8,leading=14,textColor=INK)
timer=ParagraphStyle("timer",fontName="CNB",fontSize=7.8,leading=10,textColor=colors.white,alignment=1)
label=ParagraphStyle("label",fontName="CNB",fontSize=7.4,leading=9.5,textColor=DARK)
body=ParagraphStyle("body",fontName="CN",fontSize=8.0,leading=11.55,textColor=INK)
small=ParagraphStyle("small",fontName="CN",fontSize=7.35,leading=10.6,textColor=MUTED)
bullet=ParagraphStyle("bullet",parent=body,leftIndent=9,firstLineIndent=-7,spaceAfter=2)
quote=ParagraphStyle("quote",fontName="CN",fontSize=8.05,leading=11.8,textColor=DARK)

def P(t,st=body): return Paragraph(t,st)
def card(rows,bg=colors.white,border=LINE,accent=CYAN):
    return Table(rows,colWidths=[324],style=TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),bg),("BOX",(0,0),(-1,-1),0.8,border),("LINEBEFORE",(0,0),(0,-1),3.2,accent),
        ("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))

def step(no,dur,name,purpose,action,narration,takeaway,accent=CYAN):
    badge=Table([[P(no,timer),P(dur,timer)]],colWidths=[26,72],rowHeights=[17],style=TableStyle([
        ("BACKGROUND",(0,0),(0,0),accent),("BACKGROUND",(1,0),(1,0),DARK),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),2),("RIGHTPADDING",(0,0),(-1,-1),2)]))
    head=Table([[badge,P(name,step_title)]],colWidths=[98,214],rowHeights=[24],style=TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),2)]))
    rows=[[head],[P("本段目的",label)],[P(purpose,small)],[P("操作",label)],[P(action,body)],[P("详细口播",label)],[P(narration,body)],[P("评委应听懂",label)],[P(takeaway,small)]]
    return KeepTogether([card(rows),Spacer(1,6)])

def on_page(c,doc):
    c.saveState(); c.setFillColor(colors.HexColor("#E8F4F7")); c.rect(0,H-9,W,9,fill=1,stroke=0)
    c.setFillColor(CYAN); c.rect(0,H-9,W,9,fill=1,stroke=0)
    c.setFont("CN",6.6); c.setFillColor(MUTED); c.drawString(18,14,"京枢智网 | 答辩录屏详细脚本")
    c.drawRightString(W-18,14,f"{doc.page} / 9"); c.restoreState()

story=[]
# Cover / presenter briefing
story += [Spacer(1,13),P("平台录屏脚本",title),P("答辩详细版 | 建议 2 分 55 秒 - 3 分钟 | 手机竖屏",subtitle)]
story += [P("这项系统是什么",section)]
story += [P("它面向超大城市社区末端共同配送的组织者和运营管理者，把 HUB、社区接驳点、智能柜、无人车、快递员和需求数据放进同一套决策链，帮助管理者从“凭经验安排”转向“可预测、可比较、可执行”的决策。",quote)]
story += [Spacer(1,7),P("核心用户",section)]
story += [P("物流平台/共同配送运营方：统一组织车辆、设施和人员。",bullet)]
story += [P("社区设施运营方：判断柜体够不够、建在哪里、是否扩容。",bullet)]
story += [P("街道或园区管理者：评估成本、效率、服务覆盖和风险。",bullet)]
story += [Spacer(1,7),P("评委会关心的三个问题",section)]
story += [P("1. 需求从哪来：用概率预测和分位数覆盖常态、大促和波动情景。",bullet)]
story += [P("2. 方案怎么形成：用设施定容和人车协同模型生成可执行方案。",bullet)]
story += [P("3. 结果怎么证明：用仿真验证峰值压力，并用 KPI 对比和算法看板闭环。",bullet)]
story += [Spacer(1,7),P("开场总述口播",section)]
story += [P("“这是一个面向超大城市末端共同配送的决策支持平台，而不是单纯的数据大屏。它服务的对象是需要同时管理需求、设施、无人车和快递员的运营管理者。平台围绕需求预测、选址定容、人车协同、运行仿真和应急调度形成完整闭环，重点回答三个问题：社区需要多少末端运力，设施和人车应该怎么配置，出现高负荷或突发事件时如何快速重排。”",quote)]
story += [PageBreak()]

# Step 1
story += [Spacer(1,12),P("先讲业务背景：平台解决什么问题",section)]
story += [step("01","00:00-00:18","项目定位与服务对象","先交代平台属于谁、服务谁、替代了什么决策过程，让评委建立业务语境。","保持主界面，指向平台名称、模块导航和顶部关键指标；不要急着切换页面。","这项平台面向超大城市社区末端共同配送。传统模式下，各企业各自派车、各自进社区，驿站、智能柜和快递员之间缺少统一调度，容易出现车辆重复进区、柜体高峰爆满、人工超时和异常响应慢。平台服务的核心用户，就是需要统筹这些资源的配送运营方和社区末端设施管理者。","评委应听懂：平台是“运营管理决策系统”，不是简单展示数据。",BLUE)]
story += [PageBreak()]

# Step 2
story += [Spacer(1,12),P("再讲现状与优化：为什么要做对比",section)]
story += [step("02","00:18-00:42","S0、S1、S2 方案对比","展示平台能把现状问题和优化措施转成可量化、可比较的方案，而不是只给一个结论。","全域(5社区) -> 方案模式选择叠图对比 -> 情景 N 普通日 -> 保持左右分屏。","这里用同一套需求数据对比三个方案。S0 是现状：各社区独立往返，主要由人工完成。S1 解决设施问题：采用巡回干线并扩容智能柜。S2 再加入人车协同：无人车负责投柜和补货，快递员专注上门服务。平台显示干线里程从 24.84 公里降到 13.42 公里，人工工时从 123.5 小时降到 54.2 小时，年现金成本从 245.6 万元降到 128.6 万元。这些指标说明优化不是单点改善，而是运输、设施和作业方式的联动优化。","评委应听懂：S0 是问题基线，S1 是设施优化，S2 是设施加人车协同的完整推荐方案。",RED)]
story += [PageBreak()]

# Step 3
story += [Spacer(1,12),P("讲清数据与需求：平台为什么会得出这些结果",section)]
story += [step("03","00:42-01:05","真实 GIS 底座与概率需求预测","说明平台的可信数据从哪里来，以及需求预测如何成为选址和路径规划的统一输入。","点击 C04 亦城茗苑 -> 数字孪生 -> 点击聚焦 -> 切换需求预测 -> 选择 P20 大促峰值。","平台首先把业务落在真实空间上。系统接入 5 个社区的 WGS84 边界、楼栋、设施和内部路网，在高德底图上显示时自动校正坐标系，保证社区边界、HUB、接驳点和楼栋位置能够对应。需求预测则不是只给一个平均值，而是输出 P50、P80、P90 不同风险分位数，并区分智能柜自提和上门配送。这样后续设施容量和路径班次就能同时考虑普通日与大促峰值。","评委应听懂：这套平台有统一的数据底座，预测结果会直接驱动后续优化，不是各模块各算各的。",CYAN)]
story += [PageBreak()]

# Step 4
story += [Spacer(1,12),P("讲设施决策：从需求到选址定容",section)]
story += [step("04","01:05-01:28","MIP 选址定容与扩容","说明平台如何回答“建在哪里、建多大、覆盖谁”，以及如何避免只扩容不解决覆盖问题。","保持 C04 和 P20 -> 进入选址定容 -> 查看有效容量、服务半径和楼栋分配。","选址定容模块使用混合整数规划模型，把主柜、副柜和楼栋分配作为决策变量，同时考虑容量、覆盖距离和新增投资。对于高峰风险大的社区，平台优先利用存量设施，再决定新增多少副柜；对于服务距离超标的楼栋，则重新分配或增加服务点。它要避免两个常见错误：一是只看总容量，导致部分楼栋仍然太远；二是盲目扩容，造成设备和运营成本浪费。","评委应听懂：设施方案是带硬约束的优化结果，不是按户数简单平均配置。",GREEN)]
story += [PageBreak()]

# Step 5
story += [Spacer(1,12),P("讲执行方案：人车如何协同",section)]
story += [step("05","01:28-01:52","两级人车协同路径与班次","说明无人车与快递员如何分工，为什么这种协同能同时提升效率和服务质量。","进入人车协同 -> 保持 S2 -> 查看无人车巡航和上门服务路径。","S2 采用两级协同网络。第一级由无人车承担 HUB 到社区接驳点、再到智能柜的微循环投柜和补货，减少快递员重复搬运；第二级由快递员专注老年住户、大件和需要上门的楼栋。路径模型同时考虑车辆容量、服务时间窗、快递员工时和电池安全余量。这样做的价值不是用无人车完全替代人，而是让无人设备承担标准化、重复性运输，让人力集中在更有温度的近端服务上。","评委应听懂：这是“人机分工”，不是“机器替代人”；地图上的蓝线和橙色虚线分别代表两类任务。",CYAN)]
story += [PageBreak()]

# Step 6
story += [Spacer(1,12),P("讲验证：方案在高峰和扰动下是否可靠",section)]
story += [step("06","01:52-02:16","动态占用仿真与情景压力测试","说明优化方案不是静态最优，而是在普通日、大促和扰动场景下都能验证。","仿真对抗 -> 选择大促峰值或取件后扰动 -> 查看柜体占用曲线、21:00 未完成件量和班次甘特图。","仿真模块按 08:00 到 21:00 的时序推演包裹到达、柜体占用、投柜和上门履约。它重点回答三件事：高峰时柜体是否会溢出，21:00 前是否能完成配送，无人车和快递员班次是否超出工时。这样，选址和路径方案不仅停留在数学模型里，还能接受动态运行压力测试，帮助管理者提前发现薄弱环节。","评委应听懂：平台把“方案能做”进一步验证到“高峰时能不能稳定执行”。",AMBER)]
story += [PageBreak()]

# Step 7
story += [Spacer(1,12),P("讲 AI：从聊天到可下发决策",section)]
story += [step("07","02:16-02:40","AI 应急调度与自适应重排","说明 AI 不是独立聊天窗口，而是读取运筹平台上下文、生成可执行处置建议的决策入口。","进入 AI 应急调度 -> 打开 AI 调度中枢 -> 点击暴雪极端调度重排 -> 等待正式报告完成。","当出现暴雪、爆柜或突发扰动时，平台会把当前社区、需求、设施、路径和约束状态传给 AI 中枢。AI 结合 M1 到 M8 运筹模型，输出风险判断、扩容动作、分流方案和调度工单。它适合处理规则之外但业务上又必须快速响应的异常场景，例如道路受阻、柜体临满或上门需求突然增加。系统只展示正式建议，不展示内部思考过程。","评委应听懂：AI 的价值在于连接运筹模型和现场执行，把异常转化为可实施动作。",RED)]
story += [PageBreak()]

# Step 8
story += [Spacer(1,12),P("最后收束：平台价值和可信结论",section)]
story += [step("08","02:40-03:00","算法看板与总结","用模型体系和量化结果收束，同时说明评价边界，体现方案的可信度。","打开算法看板 -> 展示 M6 -> 返回主界面 -> 保持 2 秒后停止录制。","整个平台把需求预测、设施定容、人车协同、动态仿真和应急调度放进同一套模型体系中，最终交付给管理者的不是一张地图，而是一组可比较、可解释、可执行的末端配送决策。核心结论是：干线里程下降 46%，人工工时下降 56.1%，年现金成本下降 47.7%。同时平台不会把结果简单包装成“所有指标全面下降”，碳排放会区分单件和总量呈现，体现评价的可信度。","评委应听懂：这是一套从预测、规划、执行到应急的完整决策闭环，核心价值是降本、提效和提升韧性。",CYAN)]
story += [Spacer(1,6),card([[P("答辩收尾总口播",label)],[P("“我们希望解决的不是某一个配送节点的问题，而是超大城市社区末端共同配送的系统性协同问题。平台让需求、设施、无人车、快递员和应急决策进入同一个可计算、可验证的闭环，为运营管理者提供可落地的决策依据。”",quote)]],bg=PALE_GREEN,border=colors.HexColor("#A7CBB9"),accent=GREEN)]
story += [Spacer(1,6),card([[P("录屏前检查",label)],[P("浏览器全屏 | 打开“录屏模式” | 手机打开本 PDF | 不打开 AI 设置、约束明细、四端协同",small)]],bg=PALE_AMBER,border=colors.HexColor("#E4C98E"),accent=AMBER)]

doc=BaseDocTemplate(str(OUT),pagesize=(W,H),leftMargin=18,rightMargin=18,topMargin=10,bottomMargin=24,title="平台录屏脚本_答辩详细版_3分钟",author="京枢智网")
frame=Frame(doc.leftMargin,doc.bottomMargin,doc.width,doc.height,id="main",leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)
doc.addPageTemplates([PageTemplate(id="mobile",frames=[frame],onPage=on_page)])
doc.build(story)
print(OUT.resolve())
