# -*- coding: utf-8 -*-
"""
Generate complete Chapter 7 docx file with professional typography,
high-resolution screenshots, 3-line academic tables, and refined text content.
"""
import os
import sys
import shutil
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

# Source screenshots directory
SCREENSHOTS_DIR = r'd:\物流设计大赛\chapter7_platform_frontend\screenshots'
TARGET_DOCX = r'C:\Users\zhutmg\Desktop\第七章平台(1).docx'
BACKUP_DOCX = r'C:\Users\zhutmg\Desktop\第七章平台(1)_backup_original.docx'

# Ensure backup exists
if not os.path.exists(BACKUP_DOCX):
    if os.path.exists(TARGET_DOCX):
        shutil.copyfile(TARGET_DOCX, BACKUP_DOCX)
        print(f"[OK] Backed up original to: {BACKUP_DOCX}")

def create_element(name):
    return OxmlElement(name)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    """Set cell background color."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    tcPr.append(shd)

def set_table_three_lines_borders(table):
    """Apply standard academic 3-line table borders (top, bottom, header bottom)."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def set_header_row_bottom_border(row):
    """Apply bottom border to table header row."""
    for cell in row.cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = parse_xml(
            f'<w:tcBorders {nsdecls("w")}>\n'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'</w:tcBorders>'
        )
        tcPr.append(tcBorders)

def add_run(p, text, font_en='Times New Roman', font_cn='宋体', size_pt=12, bold=False, italic=False, color_rgb=(0,0,0)):
    r = p.add_run(text)
    r.font.name = font_en
    r.font.size = Pt(size_pt)
    r.font.bold = bold
    r.font.italic = italic
    if color_rgb:
        r.font.color.rgb = RGBColor(*color_rgb)
    rPr = r._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_en}" w:hAnsi="{font_en}" w:eastAsia="{font_cn}" w:cs="{font_en}"/>')
        rPr.append(rFonts)
    else:
        rFonts.set(qn('w:ascii'), font_en)
        rFonts.set(qn('w:hAnsi'), font_en)
        rFonts.set(qn('w:eastAsia'), font_cn)
        rFonts.set(qn('w:cs'), font_en)
    return r

def add_heading_chapter(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.first_line_indent = Pt(0)
    add_run(p, text, font_en='Times New Roman', font_cn='黑体', size_pt=16, bold=True)
    return p

def add_heading_1(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.first_line_indent = Pt(0)
    add_run(p, text, font_en='Times New Roman', font_cn='黑体', size_pt=14, bold=True)
    return p

def add_heading_2(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.first_line_indent = Pt(0)
    add_run(p, text, font_en='Times New Roman', font_cn='黑体', size_pt=12.5, bold=True)
    return p

def add_body_p(doc, text, bold_prefix="", indent=True):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.first_line_indent = Pt(24) if indent else Pt(0)
    if bold_prefix:
        add_run(p, bold_prefix, font_en='Times New Roman', font_cn='宋体', size_pt=12, bold=True)
    add_run(p, text, font_en='Times New Roman', font_cn='宋体', size_pt=12, bold=False)
    return p

def add_bullet_p(doc, prefix, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    p.paragraph_format.line_spacing = 1.25
    p.paragraph_format.first_line_indent = Pt(24)
    add_run(p, prefix, font_en='Times New Roman', font_cn='宋体', size_pt=12, bold=True)
    add_run(p, text, font_en='Times New Roman', font_cn='宋体', size_pt=12, bold=False)
    return p

def add_figure(doc, img_filename, caption_text, width_cm=14.6):
    img_path = os.path.join(SCREENSHOTS_DIR, img_filename)
    if not os.path.exists(img_path):
        print(f"[WARNING] Image not found: {img_path}")
        return None
    
    # Image paragraph
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(8)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.first_line_indent = Pt(0)
    run_img = p_img.add_run()
    run_img.add_picture(img_path, width=Cm(width_cm))
    
    # Caption paragraph
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    p_cap.paragraph_format.first_line_indent = Pt(0)
    add_run(p_cap, caption_text, font_en='Times New Roman', font_cn='黑体', size_pt=10, bold=True, color_rgb=(50,50,50))
    return p_img, p_cap

def add_table_caption(doc, caption_text):
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(8)
    p_cap.paragraph_format.space_after = Pt(4)
    p_cap.paragraph_format.first_line_indent = Pt(0)
    add_run(p_cap, caption_text, font_en='Times New Roman', font_cn='黑体', size_pt=10, bold=True, color_rgb=(50,50,50))
    return p_cap

def build_chapter7():
    print("Building Chapter 7 Document...")
    doc = Document()
    
    # Page setup - Standard A4 with professional margins
    for sec in doc.sections:
        sec.page_width = Cm(21.0)
        sec.page_height = Cm(29.7)
        sec.top_margin = Cm(2.54)
        sec.bottom_margin = Cm(2.54)
        sec.left_margin = Cm(3.17)
        sec.right_margin = Cm(3.17)

    # Chapter Title
    add_heading_chapter(doc, "7 多模型驱动的社区末端共同配送协同决策与运行平台设计")
    
    # Introduction paragraphs
    add_body_p(doc, "前述章节已经围绕社区末端共同配送的核心决策问题构建了系统、完备的数学模型与仿真评价体系：在需求侧，第三章需求估计与情景模拟模型精准刻画了多时段、多情景及楼栋微观层面的动态配送负荷；在网络侧，第四章末端配送网络规划模型科学确立了“社区接驳点—智能快递柜/末端驿站—住宅需求节点”的多级空间拓扑与服务映射关系；在调度侧，第五章无人配送与人工协同调度模型高效求解了人车协同组批、车辆微观路径规划以及高精度交接时间匹配问题；在评价侧，第六章动态仿真与多目标综合评价体系则从履约时效、运营成本、服务可靠性以及全生命周期碳减排等维度对方案成效进行了严谨的量化推演。")
    
    add_body_p(doc, "然而，从数学模型的离线最优求解到现实业务的在线高效运行之间，始终存在着关键的数字化工程断层。模型能够精确解答“需求规模有多少”、“末端设施如何布局”以及“无人车与配送员如何规划路径”，却无法直接替代物流企业的数据对接与订单录入、现场配送员的工单执行与人车交接、社区居民的自主配送方式选择与弹性时间窗预约，亦无法自主处置运行过程中的突发异常与动态扰动。真实的社区末端共同配送是一个涉及多主体交互、多资源协同、多约束耦合且高频动态变化的复杂业务系统，迫切需要一个统一的数字化信息载体与协同决策中枢，将前序模型的数学智慧无缝赋能于现实业务运作。")
    
    add_body_p(doc, "基于此，本项目进一步研发了“多模型驱动的社区末端共同配送协同决策与运行平台”。该平台并非数学模型求解结果的静态展示看板，而是以“订单全生命周期履约”为主线，深度整合多源数据底座与算法模型集群，将共同配送运营方、物流企业与分拨中心、现场配送执行人员以及社区居民四类核心主体深度联结于统一的数字化生态中。平台全面驱动订单智能汇聚、动态滚动组批、无人车自主路径规划、人车精准交接协同、多方式分流交付以及跨主体异常自愈闭环，实现从离线规划向在线实时决策与数字化运营的完整跨越。")

    # Section 7.1
    add_heading_1(doc, "7.1 平台建设目标与总体设计")
    
    add_heading_2(doc, "7.1.1 平台建设背景与设计目标")
    add_body_p(doc, "本项目前述模型分别针对社区末端共同配送体系的不同决策层级进行了深度求解。第三章需求模型输出“社区—情景—楼栋—时段—服务方式”的多维精细化需求矩阵；第四章网络模型输出最优设施选址与微观节点拓扑连接；第五章调度模型输出兼顾运力约束与时间窗的高效人车协同运行计划。这三大模型构成了从“宏观需求识别”到“微观协同运行”的技术链条。然而，若这些技术成果仅停留在离线数据表与静态方案阶段，现实中的各参与主体依然面临信息孤岛与协同壁垒：物流企业难以感知包裹进入社区后的实时承运状态；一线配送员无法精准预判无人车到达交接点的倒计时；社区居民个性化的上门时间与自提诉求难以反向约束调度算法。")
    
    add_body_p(doc, "针对上述痛点，平台确立了“模型全链路集成、多主体深度协同、动态运行自愈闭环”三大建设目标：")
    add_bullet_p(doc, "（1）模型全链路集成（Model Cascade Integration）：", "将需求预测、网络拓扑、人车协同调度、数字孪生仿真及多维综合评价有机融入同一系统底座，构建上下游模型间标准化、低延迟的数据流动与级联触发机制，实现多模型集群的一体化协同计算。")
    add_bullet_p(doc, "（2）多主体业务协同（Multi-Actor Business Orchestration）：", "面向运营方、物流企业、配送人员及社区居民四类主体打造专属交互终端，在保证“一单到底”数据唯一性与状态强一致性的前提下，实现各主体高效履职与跨角色敏捷协同。")
    add_bullet_p(doc, "（3）动态运行自愈闭环（Closed-Loop Adaptive Feedback）：", "平台不仅向下游下发模型生成的调度工单，更实时接收居民端时间窗调整、移动端人车交接状态、高精GIS路网施工障碍及智能柜格口负载等现场数据，动态反哺算法引擎进行滚动重调度，形成“感知—决策—执行—反馈—优化”的完整闭环。")

    add_heading_2(doc, "7.1.2 平台服务主体与业务需求")
    add_body_p(doc, "社区末端共同配送打破了传统单一物流企业“各自为战”的配送边界，由多元主体在统一的末端网络中协作完成履约。不同参与主体的业务诉求、关注视角与交互场景存在显著差异，平台针对各主体的核心需求与痛点进行了系统化矩阵设计，如表7-1所示。")

    # Table 7-1
    add_table_caption(doc, "表7-1 共同配送多主体业务需求与多角色终端功能定位矩阵")
    
    table_data = [
        ["使用主体", "业务核心诉求与痛点", "终端形式与部署载体", "核心功能与数据权限边界"],
        ["共同配送运营方\n（调度与运管中心）", "掌握全局资源动态，组织多企业订单共同组批，协同无人车与配送员作业，监测设施负载并评估碳排效益", "PC管理端\n（数字孪生驾驶舱大屏）", "全局KPI态势感知、社区高精GIS拓扑监控、动态组批与派车控制、人车交接雷达管理、多维运营评价推演"],
        ["物流企业与分拨中心\n（顺丰/京东/三通一达等）", "统一批量接入末端包裹，实时掌握包裹进入共同配送网络后的批次、承运车辆与履约时效，保障数据隐私", "PC企业协同端\n（B2B Web业务系统）", "订单API批量接入、全链路8阶里程碑可视化追踪、公共批次透明度监控、企业履约SLA报表分析（严格隔离他企商业数据）"],
        ["一线配送执行人员\n（现场配送员/安全岗）", "清晰获取当日工单时序，精准预判无人车到站交接倒计时，免去现场漫长等待，高效完成入户交付并上报异常", "移动端APP\n（配送管家 Android/iOS）", "当日任务看板、人车交接高精雷达与倒计时、一键扫码核验交接、预约时间窗上门路线引导、现场施工/门禁敏捷上报"],
        ["社区居民\n（最终服务对象）", "清晰获知包裹末端精准状态，自主选择自提或上门，根据作息弹性预约上门时间窗，享受高品质末端服务", "移动端小程序\n（微信小程序轻量入口）", "末端进度透明查询、交付方式自选（智能柜/上门/驿站）、基于运力余量的弹性时间窗预约（如17:00-19:00）、实时地址微调"]
    ]
    
    t = doc.add_table(rows=len(table_data), cols=4)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_three_lines_borders(t)
    
    col_widths = [Cm(3.0), Cm(4.8), Cm(2.8), Cm(4.2)]
    
    for r_idx, row in enumerate(t.rows):
        # Set header row
        if r_idx == 0:
            set_header_row_bottom_border(row)
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_widths[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_margins(cell, top=120, bottom=120, left=140, right=140)
            if r_idx == 0:
                set_cell_shading(cell, "F1F5F9")
            
            p_c = cell.paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER if (c_idx in [0, 2] or r_idx == 0) else WD_ALIGN_PARAGRAPH.LEFT
            p_c.paragraph_format.first_line_indent = Pt(0)
            p_c.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            p_c.paragraph_format.line_spacing = 1.15
            
            lines = table_data[r_idx][c_idx].split('\n')
            for l_idx, line in enumerate(lines):
                if l_idx > 0:
                    p_c.add_run('\n')
                is_bold = (r_idx == 0) or (l_idx == 0 and c_idx in [0, 2])
                font_size = 10 if r_idx == 0 else 9.5
                add_run(p_c, line, font_en='Times New Roman', font_cn='宋体' if r_idx > 0 else '黑体', size_pt=font_size, bold=is_bold)
    
    # Spacing after table
    p_after_t = doc.add_paragraph()
    p_after_t.paragraph_format.space_before = Pt(4)
    p_after_t.paragraph_format.space_after = Pt(2)
    p_after_t.paragraph_format.first_line_indent = Pt(24)
    add_run(p_after_t, "基于上述差异，平台构建了“统一数据底座驱动、多端角色权限隔离”的协同机制。四大终端并非彼此孤立的烟囱系统，而是共享同一底层数据库与业务中枢。同一包裹在企业端、运营端、配送员端与居民端始终保持唯一订单编号与强一致的时间状态戳，同时基于细粒度 RBAC 权限体系，确保各物流企业商业秘密严格隔离，形成既高度共享又安全受控的协同生态。")

    # Section 7.1.3
    add_heading_2(doc, "7.1.3 平台总体架构设计")
    add_body_p(doc, "为实现物理业务场景、算法模型计算与多端人机交互的无缝融合，平台遵循高内聚、低耦合与微服务架构思想，设计了自下而上的五层总体技术架构，如图7-1所示。")
    
    add_figure(doc, "Fig7_1_Platform_Architecture_And_Model_Cascade.png", "图7-1 多模型驱动的社区末端共同配送平台总体架构")
    
    add_body_p(doc, "平台五层总体架构的具体职能与数据交互逻辑如下：")
    add_bullet_p(doc, "1. 现实运行层（Physical Operations Layer）：", "对应社区共同配送的物理空间实体与作业资源，包括上游分拨中心、社区二级接驳泊位、无人配送车队、智能快递柜/末端服务驿站、一线人工配送员/安全员以及社区终端居民，是平台算法调度与运营管控的最终物理落脚点。")
    add_bullet_p(doc, "2. 数据资产层（Data Asset Layer）：", "构建多源异构数据治理中枢，实现动静态数据的统一接入、清洗与标准化。静态数据涵盖社区三维高精GIS路网、楼栋门禁与拓扑坐标、智能柜格口容量参数等；动态数据涵盖各物流企业实时订单流、车辆GPS轨迹与SOC电量、人员在线工单状态、居民时间窗选择以及道路突发施工等环境感知数据，为上层算法提供高保真数据输入。")
    add_bullet_p(doc, "3. 算法模型层（Algorithm & Model Cascade Layer）：", "平台的“决策大脑”，深度集成前述各章核心模型集群：调用第三章需求估计与情景生成模型进行微观负荷预测；调用第四章网络规划模型解析末端设施选址与节点映射关系；调用第五章无人配送与人车协同调度模型求解动态组批、路径优化与人车交接时序；调用第六章微观动态仿真引擎开展推演评估，输出最优决策向量。")
    add_bullet_p(doc, "4. 业务协同层（Business Orchestration Layer）：", "作为数学算法与业务系统之间的转换枢纽，负责将算法求解的抽象数学解转化为生产级业务工单。核心模块包括：统一订单任务池管理、动态组批与批次生命周期控制、无人车与人工协同调度派单、智能柜格口动态预警与溢流路由、以及跨主体异常自愈协调机制。")
    add_bullet_p(doc, "5. 多端交互层（Multi-Terminal Interaction Layer）：", "面向四类参与主体打造专业化交互界面，包括共同配送运营管理端（数字孪生驾驶舱）、物流企业与分拨中心协同端（全链路追踪中枢）、配送执行移动端（配送管家APP）以及社区居民服务小程序，实现各角色的敏捷交互与数据可视化。")

    # Section 7.2
    add_heading_1(doc, "7.2 多模型驱动的业务协同与数据交互机制")
    
    add_heading_2(doc, "7.2.1 多模型协同调用关系与数据级联流动")
    add_body_p(doc, "平台内部各数学模型之间并非割裂存在，而是形成了自顶向下输入级联、自底向上动态反馈的闭环调用体系，如图7-2所示。")
    
    add_figure(doc, "Fig7_1_Platform_Architecture_And_Model_Cascade.png", "图7-2 多模型协同调用关系与数据流动机制图")
    
    add_body_p(doc, "多模型的级联调用与数据流动机制在实际运营中划分为“离线规划态（Macro Planning）”与“在线运行态（Dynamic Operations）”双重时间尺度：")
    add_bullet_p(doc, "（1）离线规划态（周期性宏观决策）：", "在系统初始化或周期性网络优化阶段，平台输入社区静态空间数据、住户人口画像与历史订单序列，首先调用第三章需求估计模型，生成多时段、多情景下的微观需求分布矩阵；随后调用第四章末端网络规划模型，优化确定社区接驳点位置、智能柜布设点位及住宅节点的覆盖分配关系，固化社区微观拓扑基础设施底座。")
    add_bullet_p(doc, "（2）在线运行态（高频滚动实时决策）：", "进入日常日常运营后，基础设施拓扑保持相对稳定，无需每笔订单重新计算网络布局。平台以第五章人车协同调度模型为核心，实时接收高频新增订单并注入动态任务池，根据装载阈值与最大等待时间触发滚动组批；实时规划无人车路径并匹配人车交接时序。同时，高精运行数据持续注入第六章动态仿真与综合评价模型，实时评估全天碳减排效益、车辆周转率与履约SLA，当出现系统性瓶颈时反向触发参数自适应调优，形成稳定的数据闭环。")

    add_heading_2(doc, "7.2.2 订单全生命周期业务协同流转机制")
    add_body_p(doc, "在多主体共同配送模式下，一件真实包裹从上游分拨中心到达社区居民手中，经历了跨系统、跨主体、跨运力的复杂业务协同。平台围绕单笔订单建立了覆盖十个标准阶段的全生命周期流转机制，如图7-3所示。")
    
    add_figure(doc, "Fig7_8_Four_Terminals_Collaborative_Matrix.png", "图7-3 社区末端共同配送单笔订单全生命周期业务协同流转图")
    
    add_body_p(doc, "单笔订单在四端协同体系中的十阶段标准流转过程如下：")
    add_bullet_p(doc, "阶段1：多源订单规范化接入（Ingestion & Parsing）：", "各物流企业将末端包裹信息通过标准化 API 或批量文件提交至协同平台，系统自动校验订单有效性并进行地址清洗与分词解析。")
    add_bullet_p(doc, "阶段2：居民服务方式与时间窗确认（Preference Confirmation）：", "针对具备自主选择权限的订单，平台通过居民小程序开放交付方式（智能柜自提 / 人工上门 / 驿站代存）及弹性预约时间窗（如 17:00—19:00），居民确认后即时写入订单属性。")
    add_bullet_p(doc, "阶段3：空间网格与拓扑节点映射（Node Matching）：", "平台调用第四章网络拓扑模型，根据订单地址秒级匹配至所属社区（如碧水豪庭 C04）、所属楼栋住宅需求节点（如 D05）及对应末端交付设施。")
    add_bullet_p(doc, "阶段4：汇聚进入动态任务池（Task Pooling）：", "来自顺丰、京东、中通等不同企业的包裹统一沉淀至社区动态公共任务池，按空间聚集度、时间窗紧急度及服务模式进行多维分类聚合。")
    add_bullet_p(doc, "阶段5：智能触发滚动组批（Dynamic Batching）：", "算法引擎实时监测任务池，当包裹总量达到装载容量阈值或最早订单等待时间逼近上限时，自动触发组批算法，生成公共配送批次（如 C04-R2）。")
    add_bullet_p(doc, "阶段6：无人车辆智能分配与路径生成（Route Planning）：", "平台为批次匹配最优可用无人车（如 C04-V1），基于社区路网拓扑计算包含发车时间、服务节点序列、节点装载量及返程时间的精准路径。")
    add_bullet_p(doc, "阶段7：接驳出库与干支协同无人运输（Autonomous Transit）：", "无人配送车在社区接驳点完成自动化/人工集装箱装载，按照规划路径平稳驶入社区干道，执行干支协同区间运输。")
    add_bullet_p(doc, "阶段8：节点多模式分流与人车精准交接（Multi-Modal Delivery & Handoff）：", "无人车到达指定节点后执行分流策略：自提包裹直接投递至智能快递柜（如 S01-S04）；需上门包裹则与提前到达泊位的一线配送员完成现场交接，配送员扫码核验入库。")
    add_bullet_p(doc, "阶段9：一线精细化入户交付与完成签收（Last-100m Delivery & Receipt）：", "配送员携带交接包裹，根据居民预约时间窗顺序上门派送，居民核对无误后签字或扫码确认，完成最后 100 米精准履约。")
    add_bullet_p(doc, "阶段10：多端状态毫秒级同步与全链路回传（Status Synchronization & Analytics）：", "签收状态瞬时回传平台数据底座，同步更新至企业协同端（计费与SLA核销）、运营驾驶舱（绩效与碳排计算）及居民小程序，沉淀全流程运行数据。")

    # Section 7.3
    add_heading_1(doc, "7.3 多角色终端与平台功能设计")
    add_body_p(doc, "多角色终端是本平台由算法模型走向现场实战的核心载体。四大终端针对不同角色的工作场景与权限边界量身定制，围绕同一订单实时交互，共同构建高韧性、高效率的共同配送运营生态。")

    # Section 7.3.1
    add_heading_2(doc, "7.3.1 共同配送运营管理端（数字孪生驾驶舱）")
    add_body_p(doc, "共同配送运营管理端是整个社区末端网络的“运行指挥与决策中枢”。在共同配送模式下，各分散企业的末端资源由运营方进行集约化统筹。运营端深度融合高德 GIS 地图底座与三维数字孪生技术，构建了面向指挥中心的综合驾驶舱大屏，如图7-4所示。")
    
    add_figure(doc, "Fig7_2_CoDelivery_Operation_Management_Cockpit.png", "图7-4 共同配送运营管理端·数字孪生驾驶舱界面（以碧水豪庭示范区为例）")
    
    add_body_p(doc, "如图7-4所示，运营管理端以碧水豪庭（C04）示范区为标杆，深度集成了以下五大核心管控功能：")
    add_bullet_p(doc, "（1）全局核心运营态势感知（Global Operations KPI）：", "大屏顶部与左侧实时聚合关键指标：当前总订单量 1,248 件、已完成 782 件、待组批池 156 件、执行中批次 4 个、在岗无人车 6 辆、一线配送员 4 人；系统整体运力利用率达 94.3%，平均履约时效缩短 32.5%，累计减少碳排放 38.6%，为调度人员提供全方位的宏观运行画像。")
    add_bullet_p(doc, "（2）微观拓扑与人车协同数字孪生（GIS Digital Twin）：", "中心区域高精度渲染碧水豪庭社区高精路网底座、接驳点（P01）、智能柜矩阵（S01-S04）以及 8 栋住宅节点（D01-D08）。动态标绘无人车（C04-V1、C04-V2）实时 GPS 航向、运行速度及行驶轨迹，直观展示一线配送员的微观服务网格与交接雷达，实现社区级“人—车—柜—路”全息孪生感知。")
    add_bullet_p(doc, "（3）智能滚动组批与车辆调度控制（Batch & Dispatch Control）：", "以典型批次 C04-R2 为例，控制面板清晰展示：执行车辆 C04-V1、额定装载 396 件、计划发车时间 15:35、途经节点序列 D03→D04→D06→D05、预计返程时间 16:42。运营人员可随时下钻查看该批次内各物流企业包裹明细及节点卸载清单，并支持一键下发人工干预指令。")
    add_bullet_p(doc, "（4）人车协同交接与设施容量预警（Handoff & Facility Monitoring）：", "系统实时跟踪 16:02 在 D05 接驳泊位的人车交接进度（计划交接 32 件上门件）。右侧设施监控看板动态更新 S01-S04 各智能柜格口实时占用率（如 S02 占用率达 88.5% 触发黄色预警），并严格按照“现有柜→邻近柜→驿站暂存→人工上门”的分级溢流策略自动重构投递任务。")
    add_bullet_p(doc, "（5）全流程“感知-决策-执行-评估”六位一体控制逻辑：", "运营端完整贯通了“看全局状态→组动态任务→派无人车辆→配协同人员→管运行异常→评综合效益”的一体化运营闭环，确立了其作为全平台中枢控制系统的核心地位。")

    # Section 7.3.2
    add_heading_2(doc, "7.3.2 物流企业与分拨中心协同端（全链路追踪中枢）")
    add_body_p(doc, "物流企业协同端面向顺丰、京东、中通、圆通等合作承运商与区域分拨中心。其核心定位是企业向共同配送系统下发包裹任务、并实时跟踪末端履约全过程的数字化门户，界面如图7-5所示。")
    
    add_figure(doc, "Fig7_3_Logistics_Enterprise_Portal_FullChain_Tracking.png", "图7-5 物流企业与分拨中心协同端·全链路追踪与订单履约管理界面")
    
    add_body_p(doc, "企业协同端的核心功能与业务价值体现在以下三方面：")
    add_bullet_p(doc, "（1）统一订单接入与标准化清洗：", "提供标准 RESTful API 与批量导入工具，物流企业可秒级下发运单编号、收件人信息、社区楼栋地址及服务优先级，平台自动完成地址匹配与空间编码。")
    add_bullet_p(doc, "（2）8阶里程碑可视化全链路追踪：", "打破传统末端配送“进入社区即失联”的黑盒状态。企业端为每笔订单提供“分拨中心出库→到达社区接驳点→编入共同批次→无人车在途运输→到达服务节点→人车协同交接→人工上门配送→用户签收完成”的完整时间轴追踪，并实时展示承运车号（C04-V1）、当前经纬度及预计送达倒计时。")
    add_bullet_p(doc, "（3）多租户数据隐私隔离与公共批次透明度保障：", "系统构建了严格的多租户安全隔离体系。物流企业可透明查看包含自身包裹的公共批次宏观运行参数（如该批次总件量、装载率、发车时间），但严格屏蔽批次内其他竞争企业的具体运单号、收件人隐私及商业明细，完美兼顾了共同配送的集约化效率与商业数据合规要求。")

    # Section 7.3.3
    add_heading_2(doc, "7.3.3 配送执行移动端（配送管家APP）")
    add_body_p(doc, "配送执行移动端（“配送管家 APP”）直接面向社区一线配送人员与安全管理员。一线人员无需面对复杂的全局模型与海量图表，其核心诉求是“任务时序清晰、车辆到达精准、扫码交接便捷、异常上报敏捷”。移动端采用专业工程深色卡片布局，界面如图7-6所示。")
    
    add_figure(doc, "Fig7_4_Courier_Mobile_App_Radar_Handoff_And_Tasks.png", "图7-6 配送执行移动端·任务概览、人车交接雷达与现场异常上报界面")
    
    add_body_p(doc, "如图7-6所示，配送管家 APP 构建了三大核心业务视图：")
    add_bullet_p(doc, "（1）当日时序任务与工单全景看板（左屏）：", "按时间轴清晰排列配送员当日任务列表，直观展示待接收批次、待上门包裹数（如 48 件）、特殊服务工单及预约时段分布，引导配送员有条不紊推进现场作业。")
    add_bullet_p(doc, "（2）人车交接高精雷达与动态倒计时（中屏）：", "当无人车驶向交接泊位时，APP 自动激活人车交接雷达界面，明确显示：承运车号 C04-V1、所属批次 C04-R2、交接泊位 D05、剩余距离 180 米、预计 3 分钟后到站、待接收件量 32 件。配送员无需提前在户外漫长等待，车辆入泊后通过 APP 一键扫描车厢条码完成批量核验交接，系统自动将订单状态转为“人工配送中”。")
    add_bullet_p(doc, "（3）现场敏捷异常上报与双向数据互通（右屏）：", "配送员在作业中遇到道路临时施工、单元门禁故障、智能柜满载或居民临时不在家等突发情况时，可通过 APP 拍照并一键提交结构化异常工单。信息毫秒级直达后台算法引擎，触发动态路径重规划与工单重分配，实现一线作业与指挥中枢的双向赋能。")

    # Section 7.3.4
    add_heading_2(doc, "7.3.4 社区居民服务微信小程序")
    add_body_p(doc, "社区居民是共同配送的最终服务对象。针对居民低频、轻量与易用的使用习惯，平台依托微信小程序构建免安装、秒级打开的便民服务入口，实现居民真实需求对后台调度算法的高效反哺，界面如图7-7所示。")
    
    add_figure(doc, "Fig7_5_Resident_WeChat_MiniProgram_Mode_And_Time_Window.png", "图7-7 社区居民服务微信小程序·包裹状态全景、交付方式自选与弹性时间窗预约界面")
    
    add_body_p(doc, "居民服务微信小程序的核心功能包括以下三大模块：")
    add_bullet_p(doc, "（1）末端全透明多阶段进度查询（左屏）：", "居民可清晰查看包裹进入共同配送体系后的多级状态节点（已汇聚入池、已编入无人车批次、无人运输中、已与配送员交接、配送员派送中等），告别传统物流“派送中”的模糊等待。")
    add_bullet_p(doc, "（2）末端交付方式自主个性化选择（中屏）：", "提供“智能快递柜自提”、“配送员送货上门”以及“末端服务驿站暂存”三种交付模式供居民自主切换。居民选择直接写入底层订单属性，实时驱动后台任务分流引擎。")
    add_bullet_p(doc, "（3）基于运力余量的弹性时间窗精准预约（右屏）：", "为避免碎片化时间要求打乱车辆集约化路径，小程序根据算法实时运力富余度，动态开放若干标准预约时间段（如 17:00—19:00、19:00—21:00）。居民确认后，该时间约束自动成为第五章人车协同调度算法的强约束条件，实现居民个性化诉求与系统集约化效益的最佳平衡。")

    # Section 7.3.5
    add_heading_2(doc, "7.3.5 跨主体异常协同与闭环反馈联动系统")
    add_body_p(doc, "真实的社区末端配送环境充满动态不确定性。真正的现代化协同平台必须具备敏捷处置突发扰动的自愈能力。平台构建了跨主体、跨终端的动态异常协同响应机制，界面如图7-8所示。")
    
    add_figure(doc, "Fig7_6_Cross_Role_Dynamic_Exception_Closed_Loop.png", "图7-8 跨主体异常协同与闭环动态反馈联动系统界面")
    
    add_body_p(doc, "当社区发生突发扰动时，平台严格遵循“异常捕捉→信息上报→数字底座更新→多模型重算→任务重构派发→多端即时同步→现场闭环执行”的七步闭环联动体系：")
    add_bullet_p(doc, "典型场景一：社区内部道路突发施工受阻：", "配送员通过移动端上报 D04 至 D06 路段施工障碍；平台 GIS 底座瞬时将该路段权重置为不可通行；算法引擎秒级重算无人车避障绕行路径（由原主干道调整为次干道，里程增加 240 米，耗时增加 4 分钟）；运营驾驶舱高亮显示黄色绕行预警；配送管家 APP 即时更新人车交接倒计时；物流企业端与居民小程序同步修正预计履约时间，确保全链路信息无缝同步。")
    add_bullet_p(doc, "典型场景二：目标智能快递柜格口瞬时满载：", "当 S02 柜机使用率达到 100% 时，系统触发格口容量预警，立即阻断新增订单向该柜分配，并严格依照“现有柜→邻近柜（S03 剩余 8 格）→末端驿站→人工上门”的溢流规则自动拆分任务；受影响订单自动转入配送员上门工单，并在居民端推送取件位置变更通知。")
    add_bullet_p(doc, "典型场景三：无人配送车辆低电量或机械故障：", "当车辆电池 SOC 降至 15% 临界阈值或上报故障代码时，系统自动冻结其后续未执行任务，触发备用无人车前往就近接驳点承接转移包裹，或将紧迫时间窗订单转派至周边机动配送员，保障全网履约 SLA 零降级。")

    # Section 7.4
    add_heading_1(doc, "7.4 本章小结")
    add_body_p(doc, "本章在第三章需求估计与情景模拟、第四章末端配送网络规划、第五章无人配送与人工协同调度模型以及第六章动态仿真与综合评价的基础上，全面完成多模型驱动的社区末端共同配送协同决策与运行平台的系统设计与工程构建。")
    
    add_body_p(doc, "平台以“统一数据底座驱动、多端角色协同联动”为核心架构理念，通过自下而上的五层技术体系，成功打破了离线算法模型与在线实际业务之间的数字化断层。在算法与数据层面，平台实现了需求预测、拓扑映射、滚动组批、人车调度与仿真评价的全链路级联计算与双向反馈；在业务与应用层面，围绕单笔订单十阶段全生命周期，构建了涵盖共同配送运营管理端（数字孪生驾驶舱）、物流企业协同端（全链路追踪中枢）、配送执行移动端（配送管家 APP）以及社区居民服务小程序的四端协同矩阵体系。")
    
    add_body_p(doc, "经碧水豪庭等示范区的实景数据验证，本平台展现出优异的系统鲁棒性与协同调度性能，实现了全网运力利用率达 94.3%、综合履约时效提升 32.5%、运营总成本下降 27.4% 以及末端碳排放降低 38.6% 的显著成效。本平台的成功构建，使整篇竞赛论文的前序数学规划与仿真推演成果真正落地为一套“看得见、调得动、管得住、评得准”的现代化智慧物流实战系统，为我国智慧城市社区末端物流的集约化、绿色化与数字化转型提供了极具推广价值的整体解决方案。")

    # Save output docx
    doc.save(TARGET_DOCX)
    print(f"[SUCCESS] Document generated and saved to: {TARGET_DOCX}")

if __name__ == '__main__':
    build_chapter7()
