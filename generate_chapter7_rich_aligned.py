# -*- coding: utf-8 -*-
"""
Generate Chapter 7 DOCX:
1. Substantive, comprehensive, and academically rigorous text (not overly condensed).
2. Cleaned of redundant filler and colloquialisms while preserving deep explanations for every figure, table, and module.
3. 100% aligned with '第三四五章（配图版）.docx' in:
   - Body: 10.5pt (五号) 宋体 + Times New Roman, line=360 (18pt/1.5x), after=220 (11pt), fl=420 (21pt = 2 chars).
   - Headings: 14pt (四号) Bold 黑体 (H1), 12pt (小四) Bold 黑体 (H2), 15pt Bold 黑体 (Title), line=360, before=240.
   - Captions: 10.5pt Bold 黑体, centered, line=360, after=220.
   - Margins: Top 1", Bottom 1", Left 1.25", Right 1.25".
   - Table: Standard academic 3-line table.
4. 4K Ultra-HD resolution screenshots embedded.
"""
import os
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

SCREENSHOTS_DIR = r'd:\物流设计大赛\chapter7_platform_frontend\screenshots'
TARGET_DOCX = r'C:\Users\zhutmg\Desktop\第七章平台(1).docx'
TARGET_ALIGNED = r'C:\Users\zhutmg\Desktop\第七章平台(1)_对齐排版与4K高清版.docx'

def set_run_font(run, text, font_en='Times New Roman', font_cn='宋体', size_pt=10.5, bold=False, italic=False, color_rgb=None):
    run.text = text
    run.font.name = font_en
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    if color_rgb:
        run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_en}" w:hAnsi="{font_en}" w:eastAsia="{font_cn}" w:cs="{font_en}"/>')
        rPr.append(rFonts)
    else:
        rFonts.set(qn('w:ascii'), font_en)
        rFonts.set(qn('w:hAnsi'), font_en)
        rFonts.set(qn('w:eastAsia'), font_cn)
        rFonts.set(qn('w:cs'), font_en)

def set_p_spacing_and_indent(p, before_dxa=None, after_dxa=220, line_dxa=360, fl_dxa=420, jc=None):
    pPr = p._p.get_or_add_pPr()
    sp = pPr.find(qn('w:spacing'))
    if sp is None:
        sp = OxmlElement('w:spacing')
        pPr.append(sp)
    if before_dxa is not None:
        sp.set(qn('w:before'), str(before_dxa))
    elif qn('w:before') in sp.attrib:
        del sp.attrib[qn('w:before')]
    if after_dxa is not None:
        sp.set(qn('w:after'), str(after_dxa))
    elif qn('w:after') in sp.attrib:
        del sp.attrib[qn('w:after')]
    sp.set(qn('w:line'), str(line_dxa))
    sp.set(qn('w:lineRule'), 'auto')
    
    ind = pPr.find(qn('w:ind'))
    if ind is None:
        ind = OxmlElement('w:ind')
        pPr.append(ind)
    if fl_dxa is not None:
        ind.set(qn('w:firstLine'), str(fl_dxa))
        ind.set(qn('w:firstLineChars'), '0')
    else:
        if qn('w:firstLine') in ind.attrib:
            del ind.attrib[qn('w:firstLine')]
        if qn('w:firstLineChars') in ind.attrib:
            del ind.attrib[qn('w:firstLineChars')]
            
    if jc:
        p.alignment = jc

def set_table_three_lines(table):
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

def set_cell_borders_and_padding(cell, bottom_sz=None, top_sz=None, shading=None, top_dxa=100, bottom_dxa=100, left_dxa=140, right_dxa=140):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top_dxa), ('bottom', bottom_dxa), ('left', left_dxa), ('right', right_dxa)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)
    
    if bottom_sz or top_sz:
        tcBorders = OxmlElement('w:tcBorders')
        if bottom_sz:
            b_node = OxmlElement('w:bottom')
            b_node.set(qn('w:val'), 'single')
            b_node.set(qn('w:sz'), str(bottom_sz))
            b_node.set(qn('w:color'), '000000')
            tcBorders.append(b_node)
        if top_sz:
            t_node = OxmlElement('w:top')
            t_node.set(qn('w:val'), 'single')
            t_node.set(qn('w:sz'), str(top_sz))
            t_node.set(qn('w:color'), '000000')
            tcBorders.append(t_node)
        tcPr.append(tcBorders)
        
    if shading:
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{shading}"/>')
        tcPr.append(shd)

def add_chapter_title(doc, text):
    p = doc.add_paragraph()
    set_p_spacing_and_indent(p, before_dxa=240, after_dxa=240, line_dxa=360, fl_dxa=None, jc=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p.add_run(), text, font_en='Times New Roman', font_cn='黑体', size_pt=15, bold=True)
    return p

def add_h1(doc, text):
    p = doc.add_paragraph()
    set_p_spacing_and_indent(p, before_dxa=240, after_dxa=None, line_dxa=360, fl_dxa=None, jc=WD_ALIGN_PARAGRAPH.LEFT)
    set_run_font(p.add_run(), text, font_en='Times New Roman', font_cn='黑体', size_pt=14, bold=True)
    return p

def add_h2(doc, text):
    p = doc.add_paragraph()
    set_p_spacing_and_indent(p, before_dxa=240, after_dxa=None, line_dxa=360, fl_dxa=None, jc=WD_ALIGN_PARAGRAPH.LEFT)
    set_run_font(p.add_run(), text, font_en='Times New Roman', font_cn='黑体', size_pt=12, bold=True)
    return p

def add_body_p(doc, text, bold_prefix="", indent=True):
    p = doc.add_paragraph()
    set_p_spacing_and_indent(p, before_dxa=None, after_dxa=220, line_dxa=360, fl_dxa=420 if indent else None, jc=WD_ALIGN_PARAGRAPH.JUSTIFY)
    if bold_prefix:
        set_run_font(p.add_run(), bold_prefix, font_en='Times New Roman', font_cn='宋体', size_pt=10.5, bold=True)
    set_run_font(p.add_run(), text, font_en='Times New Roman', font_cn='宋体', size_pt=10.5, bold=False)
    return p

def add_fig(doc, img_filename, caption_text, width_cm=14.6):
    img_path = os.path.join(SCREENSHOTS_DIR, img_filename)
    if not os.path.exists(img_path):
        print(f"[WARNING] Image not found: {img_path}")
        return None
    
    p_img = doc.add_paragraph()
    set_p_spacing_and_indent(p_img, before_dxa=160, after_dxa=60, line_dxa=360, fl_dxa=None, jc=WD_ALIGN_PARAGRAPH.CENTER)
    r_img = p_img.add_run()
    r_img.add_picture(img_path, width=Cm(width_cm))
    
    p_cap = doc.add_paragraph()
    set_p_spacing_and_indent(p_cap, before_dxa=None, after_dxa=220, line_dxa=360, fl_dxa=None, jc=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p_cap.add_run(), caption_text, font_en='Times New Roman', font_cn='黑体', size_pt=10.5, bold=True)
    return p_img, p_cap

def add_tab_caption(doc, caption_text):
    p_cap = doc.add_paragraph()
    set_p_spacing_and_indent(p_cap, before_dxa=240, after_dxa=120, line_dxa=360, fl_dxa=None, jc=WD_ALIGN_PARAGRAPH.CENTER)
    set_run_font(p_cap.add_run(), caption_text, font_en='Times New Roman', font_cn='黑体', size_pt=10.5, bold=True)
    return p_cap

def build_rich_aligned_doc():
    print("Building Rich & Aligned Chapter 7 Document...")
    doc = Document()
    
    # Page setup strictly matching reference document
    for sec in doc.sections:
        sec.page_width = Inches(8.5)
        sec.page_height = Inches(11.0)
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.25)
        sec.right_margin = Inches(1.25)

    # Chapter Title
    add_chapter_title(doc, "7 多模型驱动的社区末端共同配送协同决策与运行平台设计")
    
    # Section Intro - 3 substantive paragraphs
    add_body_p(doc, "前述章节围绕社区末端共同配送的核心决策问题建立了较为完备的模型体系：第三章需求估计与情景模拟模型识别了不同社区、楼栋和时段下的配送负荷及服务方式分布；第四章末端网络规划模型确立了住宅需求节点与末端设施之间的服务映射关系与空间连接拓扑；第五章无人配送与人工协同模型求解了车辆微观路径、配送批次划分与人员协作时序；第六章动态仿真与评价模型则进一步通过微观推演，量化评估了方案在时效、成本与碳排放等维度的综合成效。")
    
    add_body_p(doc, "然而，从数学模型的离线求解到现实场景的实际运行之间仍存在关键断层。模型能够计算出“最优需求量”、“最优设施选址”以及“最优行驶路线”，却不能直接代替物流企业接入实际订单、一线配送员执行作业、社区居民自主选择服务方式以及运营人员动态处理突发异常。真实的共同配送过程涉及订单流、运力流、人车协同与设施负载的持续变化，是一个多主体高频交互的动态复杂系统，亟需一个统一的数字化载体将模型算法与实际业务紧密连接。")
    
    add_body_p(doc, "为此，本章进一步设计多模型驱动的社区末端共同配送协同决策与运行平台。平台以单笔订单的全生命周期为主线，将物流企业、运营方、无人配送车、人工配送员和社区居民有机联结在同一业务体系中，使前述各章模型真正转化为订单智能组织、车辆自主调度、人车精准交接、居民个性化服务以及突发扰动自愈的工程化运行能力。")

    # 7.1
    add_h1(doc, "7.1 平台建设目标与总体设计")
    
    add_h2(doc, "7.1.1 平台建设背景与设计目标")
    add_body_p(doc, "本项目前述模型分别针对共同配送体系的不同决策层级进行了求解，各模型之间已具备清晰的技术逻辑链条：需求估计模型提供多维负荷矩阵输入；网络规划模型确定设施选址与住宅覆盖拓扑；调度模型将规划结果转化为具体批次与运行路线。然而，若这些成果仅停留在静态方案和离线数据表中，实际运营中的各参与主体依然难以高效协作：物流企业无法获知自身订单进入社区后的承运车辆与实时节点；配送员难以及时掌握无人车到达交接点的精确时间；居民个性化的时间窗诉求亦无法有效反哺调度算法。")
    
    add_body_p(doc, "针对上述现实痛点，平台确立了三个维度的核心建设目标：")
    add_body_p(doc, "将需求估计、网络规划、人车协同调度、动态仿真以及综合评价模型纳入同一系统底座，构建标准化、低延迟的数据传递与级联触发机制，使各模型能够协同计算而非孤立运算。", bold_prefix="（1）实现模型全链路集成：")
    add_body_p(doc, "针对运营方、物流企业、一线配送员和社区居民构建差异化的专属交互入口，在保证全网核心状态强一致性的前提下，满足各主体完成自身作业所需的信息交互与操作需求。", bold_prefix="（2）实现多主体业务协同：")
    add_body_p(doc, "平台不仅向下游业务输出算法调度方案，更持续采集居民时间窗预约、人员实际交接、道路突发施工、车辆故障及柜机格口负载等运行数据，动态反哺算法进行重调度，实现运营方案的自适应调整。", bold_prefix="（3）实现动态运行自愈闭环：")

    add_h2(doc, "7.1.2 平台服务主体与业务需求")
    add_body_p(doc, "共同配送打破了传统单一物流企业封闭运作的边界，由多元主体依托统一末端网络共同完成履约。不同参与主体的业务诉求、关注视角与交互场景存在显著差异，平台针对各主体的核心需求与痛点进行了系统化设计，如表7-1所示。")

    # Table 7-1
    add_tab_caption(doc, "表7-1 共同配送多主体业务需求与多角色终端功能定位矩阵")
    
    table_data = [
        ["使用主体", "业务核心诉求与痛点", "终端形式与载体", "核心功能与数据权限边界"],
        ["共同配送运营方", "掌握全域运行状态，统筹多企业订单共同组批，协同无人车与配送员作业，监测设施负载并评估运营效益", "PC管理端\n（数字孪生驾驶舱）", "全局KPI大屏、社区高精GIS拓扑感知、动态组批控制、人车交接监控、多维运营评价推演"],
        ["物流企业与分拨中心", "批量接入末端包裹任务，实时掌握订单进入共同配送网络后的批次、承运车辆与履约时效，保障商业隐私", "PC企业协同端\n（B2B业务系统）", "订单API批量接入、全链路8阶里程碑可视化追踪、公共批次透明度监控、企业数据安全隔离"],
        ["一线配送执行人员", "清晰获取时序工单，实时获取无人车到站交接倒计时，免去现场漫长等待，高效入户派送并敏捷上报异常", "移动端APP\n（配送管家）", "时序任务看板、人车交接雷达与到站倒计时、一键扫码核验、时间窗工单指引、现场敏捷异常上报"],
        ["社区居民", "清晰了解末端履约进度，自主选择交付方式，根据作息弹性预约上门时段，享受高品质末端配送服务", "微信小程序\n（轻量服务入口）", "末端进度透明查询、交付方式自选（智能柜/上门/代存）、弹性时间窗预约（如17:00-19:00）"]
    ]
    
    t = doc.add_table(rows=len(table_data), cols=4)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_three_lines(t)
    col_widths = [Cm(2.8), Cm(4.6), Cm(2.8), Cm(4.4)]
    
    for r_idx, row in enumerate(t.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.width = col_widths[c_idx]
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            set_cell_borders_and_padding(cell, bottom_sz=6 if r_idx == 0 else None, shading="F1F5F9" if r_idx == 0 else None,
                                        top_dxa=100, bottom_dxa=100, left_dxa=120, right_dxa=120)
            p_c = cell.paragraphs[0]
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER if (c_idx in [0, 2] or r_idx == 0) else WD_ALIGN_PARAGRAPH.LEFT
            set_p_spacing_and_indent(p_c, before_dxa=None, after_dxa=60, line_dxa=260, fl_dxa=None)
            
            lines = table_data[r_idx][c_idx].split('\n')
            for l_idx, line in enumerate(lines):
                if l_idx > 0:
                    p_c.add_run('\n')
                is_bold = (r_idx == 0) or (l_idx == 0 and c_idx in [0, 2])
                set_run_font(p_c.add_run(), line, font_en='Times New Roman', font_cn='黑体' if is_bold else '宋体', size_pt=9.5, bold=is_bold)
    
    add_body_p(doc, "基于上述差异，平台构建了“统一数据底座驱动、多端角色权限隔离”的协同机制。四大终端并非彼此独立的系统，而是依托统一后台数据库与业务中枢运行。同一包裹在企业端、运营端、配送员端和居民端始终保持唯一的订单编号与时间状态戳。同时，系统通过细粒度 RBAC 权限控制，确保物流企业仅能查看自身订单与公共批次的宏观状态，严格隔离不同企业间的客户信息与商业机密。")

    add_h2(doc, "7.1.3 平台总体架构设计")
    add_body_p(doc, "为实现现实业务、模型计算与多端交互的有机融合，平台遵循高内聚、低耦合与微服务架构思想，设计了自下而上的五层技术架构，如图7-1所示。")
    add_fig(doc, "Fig7_1_Platform_Architecture_And_Model_Cascade.png", "图7-1 多模型驱动的社区末端共同配送平台总体架构")
    
    add_body_p(doc, "对应社区共同配送的物理基础设施与作业主体，包括分拨中心、社区二级接驳泊位、无人配送车队、智能快递柜/末端驿站、一线配送员及社区居民，是平台算法调度与运营管控的最终物理落脚点。", bold_prefix="1. 现实运行层：")
    add_body_p(doc, "构建多源异构数据治理底座，统一接入与清洗动静态数据。静态数据涵盖社区三维高精GIS路网、楼栋门禁拓扑、设施容量参数；动态数据涵盖实时订单流、车辆GPS轨迹与SOC电量、人员在线工单状态及柜机格口实时负载，为上层算法提供数据支撑。", bold_prefix="2. 数据资产层：")
    add_body_p(doc, "平台的决策核心，集成前述各章核心模型集群：调用第三章需求估计模型进行微观负荷预测；调用第四章网络规划模型解析设施选址与服务映射；调用第五章人车协同调度模型求解组批、路径与交接时序；调用第六章微观动态仿真模型开展推演与多维评价。", bold_prefix="3. 算法模型层：")
    add_body_p(doc, "作为算法模型与业务系统之间的转换枢纽，负责将算法求解的抽象数学解转化为生产级业务工单。核心模块包括统一任务池管理、动态组批与批次生命周期控制、无人车与人工协同派单、智能柜格口动态预警与溢流路由，以及跨主体异常协调机制。", bold_prefix="4. 业务协同层：")
    add_body_p(doc, "面向四类参与主体打造专业化交互界面，包括运营管理端数字孪生驾驶舱、物流企业协同端全链路追踪系统、配送执行移动端APP以及居民服务微信小程序，实现各角色的敏捷交互与数据可视化呈现。", bold_prefix="5. 多端交互层：")

    # 7.2
    add_h1(doc, "7.2 多模型驱动的业务协同与数据交互机制")
    
    add_h2(doc, "7.2.1 多模型协同调用关系与数据级联流动")
    add_body_p(doc, "平台内部各数学模型之间并非独立存在，而是构成了自顶向下输入级联、自底向上动态反馈的闭环调用体系，如图7-2所示。")
    add_fig(doc, "Fig7_1_Platform_Architecture_And_Model_Cascade.png", "图7-2 多模型协同调用关系与数据流动机制图")
    
    add_body_p(doc, "多模型的级联调用与数据流动机制在实际运营中划分为“离线规划态”与“在线运行态”双重时间尺度：")
    add_body_p(doc, "在系统初始化或网络优化阶段，平台输入社区静态空间数据、住户画像与历史订单序列，调用第三章需求估计模型生成多时段微观需求矩阵，进而驱动第四章网络规划模型优化确定接驳点位置、智能柜布设点位及住宅节点的覆盖分配关系，固化社区物理拓扑底座。", bold_prefix="（1）离线规划态（宏观长周期决策）：")
    add_body_p(doc, "日常运营中，基础设施拓扑保持相对稳定，无需每笔订单重新求解网络布局。平台以第五章人车协同调度模型为核心，实时接收新增订单并注入动态任务池，根据装载阈值与最大等待时间触发滚动组批，实时生成车辆路径并匹配人车交接。高精运行数据持续注入第六章动态仿真与综合评价模型，在线评估碳减排、车辆周转率与履约SLA，当出现系统性瓶颈时反向触发参数调优，形成稳定的数据闭环。", bold_prefix="（2）在线运行态（微观短周期调度）：")

    add_h2(doc, "7.2.2 订单全生命周期业务协同流转机制")
    add_body_p(doc, "在多主体共同配送模式下，一件真实包裹从分拨中心进入社区直至送达居民手中，经历了跨系统、跨主体、跨运力的协同履约过程。平台围绕单笔订单建立了覆盖十个关键阶段的全生命周期流转机制，如图7-3所示。")
    add_fig(doc, "Fig7_8_Four_Terminals_Collaborative_Matrix.png", "图7-3 社区末端共同配送单笔订单全生命周期业务协同流转图")
    
    add_body_p(doc, "单笔订单在四端协同体系中的十阶段标准流转过程如下：")
    add_body_p(doc, "各物流企业将末端包裹信息通过标准化API或批量文件提交至平台，系统自动校验订单有效性并进行地址清洗与分词解析。", bold_prefix="阶段1（多源订单规范接入）：")
    add_body_p(doc, "针对具备自主选择权限的订单，平台通过小程序向居民开放交付方式自选（智能柜/上门/代存）及弹性预约时间窗（如17:00—19:00），居民确认后即时写入订单属性。", bold_prefix="阶段2（服务需求动态确认）：")
    add_body_p(doc, "调用第四章网络拓扑模型，根据订单地址秒级匹配所属社区（如碧水豪庭C04）、住宅楼栋需求节点（如D05）及对应末端交付设施。", bold_prefix="阶段3（空间网格节点映射）：")
    add_body_p(doc, "来自不同企业的包裹统一沉淀至社区动态公共任务池，系统按空间聚集度、时间窗紧急度及服务模式进行多维分类聚合。", bold_prefix="阶段4（动态公共任务池归集）：")
    add_body_p(doc, "算法引擎实时监测任务池，当包裹总量达到装载容量阈值或最早订单等待时间逼近上限时，自动触发组批算法生成公共配送批次（如C04-R2）。", bold_prefix="阶段5（触发智能滚动组批）：")
    add_body_p(doc, "平台为批次匹配最优可用无人车（如C04-V1），基于社区路网拓扑计算包含发车时间、服务节点序列、节点装载量及返程时间的精准时空路径。", bold_prefix="阶段6（无人车辆匹配与路径生成）：")
    add_body_p(doc, "无人配送车在社区接驳点完成集装箱装载，按照规划路径平稳驶入社区干道，执行干支协同区间运输。", bold_prefix="阶段7（干线出库与无人运输）：")
    add_body_p(doc, "无人车到达指定节点后执行分流策略：自提件直接投递至智能柜（如S01-S04）；需上门件则在D05泊位与提前到站的配送员完成现场交接，配送员扫码核验入库。", bold_prefix="阶段8（节点分流与人车交接）：")
    add_body_p(doc, "配送员携带交接包裹，根据居民预约时间窗顺序上门派送，居民核对无误后扫码或签字确认，完成最后100米精准交付。", bold_prefix="阶段9（一线入户派送与签收）：")
    add_body_p(doc, "签收状态瞬时回传平台数据底座，同步更新至企业端（时效与SLA核销）、运营端（绩效与碳排统计）及居民小程序，沉淀全流程运行数据。", bold_prefix="阶段10（多端状态同步与数据沉淀）：")

    # 7.3
    add_h1(doc, "7.3 多角色终端与平台功能设计")
    add_body_p(doc, "多角色终端是本平台由算法模型走向实际应用的核心载体。四大终端针对不同角色的工作场景量身定制，围绕同一订单实时交互，共同构建高韧性、高效率的共同配送运营生态。")

    # 7.3.1
    add_h2(doc, "7.3.1 共同配送运营管理端（数字孪生驾驶舱）")
    add_body_p(doc, "运营管理端是整个社区末端网络的运行指挥与决策中枢。在共同配送模式下，分散企业的末端资源由运营方统筹组织。运营端深度融合高德 GIS 底座与数字孪生技术，构建了面向指挥大屏的综合管控驾驶舱，如图7-4所示。")
    add_fig(doc, "Fig7_2_CoDelivery_Operation_Management_Cockpit.png", "图7-4 共同配送运营管理端·数字孪生驾驶舱界面（以碧水豪庭示范区为例）")
    
    add_body_p(doc, "运营管理端以碧水豪庭（C04）示范区为标杆，深度集成了五大核心管控功能：")
    add_body_p(doc, "大屏顶部与侧边栏实时聚合关键运营指标：当前总订单量 1,248 件、已完成 782 件、待组批池 156 件、执行中批次 4 个、在岗无人车 6 辆、一线配送员 4 人；系统整体运力利用率达 94.3%，平均履约时效缩短 32.5%，累计减少碳排放 38.6%，为调度人员提供全方位的宏观运行画像。", bold_prefix="（1）全局核心运营态势感知：")
    add_body_p(doc, "中心区域高精度渲染碧水豪庭社区高精路网底座、接驳点（P01）、智能柜矩阵（S01-S04）以及 8 栋住宅节点（D01-D08）。动态标绘无人车（C04-V1、C04-V2）实时 GPS 航向、运行速度及行驶轨迹，直观展示一线配送员的微观服务网格与交接雷达，实现社区级“人—车—柜—路”全息孪生感知。", bold_prefix="（2）微观拓扑与人车数字孪生：")
    add_body_p(doc, "以典型批次 C04-R2 为例，控制面板清晰展示：执行车辆 C04-V1、装载 396 件、计划发车时间 15:35、途经节点序列 D03→D04→D06→D05、预计返程时间 16:42。运营人员可下钻查看该批次内各物流企业包裹明细及节点卸载清单，并支持一键下发人工干预指令。", bold_prefix="（3）动态组批与车辆调度控制：")
    add_body_p(doc, "系统实时跟踪 16:02 在 D05 接驳泊位的人车交接进度（计划交接 32 件上门件）。右侧设施监控看板动态更新 S01-S04 各智能柜格口实时占用率（如 S02 占用率达 88.5% 触发黄色预警），并严格按照“现有柜→邻近柜→驿站暂存→人工上门”的分级溢流策略自动重构投递任务。", bold_prefix="（4）人车交接协同与设施预警：")
    add_body_p(doc, "运营端完整贯通了“看全局状态→组动态任务→派无人车辆→配协同人员→管运行异常→评综合效益”的一体化运营闭环，确立了其作为全平台中枢控制系统的核心地位。", bold_prefix="（5）全流程闭环控制与运营评价：")

    # 7.3.2
    add_h2(doc, "7.3.2 物流企业与分拨中心协同端（全链路追踪中枢）")
    add_body_p(doc, "物流企业协同端面向顺丰、京东、三通一达等合作承运商与区域分拨中心。其核心定位是企业向共同配送系统下发包裹任务、并实时跟踪末端履约全过程的数字化门户，界面如图7-5所示。")
    add_fig(doc, "Fig7_3_Logistics_Enterprise_Portal_FullChain_Tracking.png", "图7-5 物流企业与分拨中心协同端·全链路追踪与订单履约管理界面")
    
    add_body_p(doc, "企业协同端的核心功能与业务价值体现在以下三个方面：")
    add_body_p(doc, "提供标准 RESTful API 与批量导入工具，物流企业可秒级下发运单编号、收件人信息、社区楼栋地址及服务优先级，平台自动完成地址清洗、空间匹配与网格编码。", bold_prefix="（1）统一订单接入与标准化清洗：")
    add_body_p(doc, "打破传统末端配送“进入社区即失联”的黑盒状态。企业端为每笔订单提供“分拨中心出库→到达社区接驳点→编入共同批次→无人车在途运输→到达服务节点→人车协同交接→人工上门配送→用户签收完成”的完整时间轴追踪，并实时展示承运车号（C04-V1）、当前经纬度及预计送达倒计时。", bold_prefix="（2）8阶里程碑可视化全链路追踪：")
    add_body_p(doc, "系统构建了严格的多租户安全隔离体系。物流企业可透明查看包含自身包裹的公共批次宏观运行参数（如该批次总件量、装载率、发车时间），但严格屏蔽批次内其他竞争企业的具体运单号、收件人隐私及商业明细，完美兼顾了共同配送的集约化效率与商业数据合规要求。", bold_prefix="（3）多租户数据隔离与批次透明度：")

    # 7.3.3
    add_h2(doc, "7.3.3 配送执行移动端（配送管家APP）")
    add_body_p(doc, "配送执行移动端（“配送管家 APP”）直接面向社区一线配送人员与安全管理员。一线人员无需面对全局复杂模型，其核心诉求是“任务时序清晰、车辆到达精准、扫码交接便捷、异常上报敏捷”。移动端界面如图7-6所示。")
    add_fig(doc, "Fig7_4_Courier_Mobile_App_Radar_Handoff_And_Tasks.png", "图7-6 配送执行移动端·任务概览、人车交接雷达与现场异常上报界面")
    
    add_body_p(doc, "配送管家 APP 构建了三大核心业务视图：")
    add_body_p(doc, "按时间轴清晰排列配送员当日任务列表，直观展示待接收批次、待上门包裹数（如 48 件）、特殊服务工单及预约时段分布，引导配送员有序推进现场派送。", bold_prefix="（1）当日时序任务与工单看板（左屏）：")
    add_body_p(doc, "当无人车驶向交接泊位时，APP 自动激活人车交接雷达界面，明确显示：承运车号 C04-V1、所属批次 C04-R2、交接泊位 D05、剩余距离 180 米、预计 3 分钟后到站、待接收件量 32 件。配送员无需提前在户外漫长等待，车辆入泊后通过 APP 一键扫描车厢条码完成批量核验交接，系统自动将订单状态更新为“人工配送中”。", bold_prefix="（2）人车交接雷达与动态倒计时（中屏）：")
    add_body_p(doc, "配送员在作业中遇到道路临时施工、单元门禁故障、智能柜满载或居民临时不在家等突发情况时，可通过 APP 拍照并一键提交结构化异常工单。信息毫秒级直达后台算法引擎，触发动态路径重规划与工单重分配，实现一线作业与指挥中枢的双向互通。", bold_prefix="（3）现场敏捷异常上报与数据互通（右屏）：")

    # 7.3.4
    add_h2(doc, "7.3.4 社区居民服务微信小程序")
    add_body_p(doc, "社区居民是共同配送的最终服务对象。针对居民低频、轻量与易用的使用习惯，平台依托微信小程序构建便民服务入口，实现居民真实需求对后台调度算法的高效反哺，界面如图7-7所示。")
    add_fig(doc, "Fig7_5_Resident_WeChat_MiniProgram_Mode_And_Time_Window.png", "图7-7 社区居民服务微信小程序·包裹状态全景、交付方式自选与弹性时间窗预约界面")
    
    add_body_p(doc, "居民服务微信小程序的核心功能包括以下三大模块：")
    add_body_p(doc, "居民可清晰查看包裹进入共同配送体系后的多级状态节点（已汇聚入池、已编入无人车批次、无人运输中、已与配送员交接、配送员派送中等），彻底消除传统物流“派送中”的模糊等待感。", bold_prefix="（1）末端全透明多阶段进度查询（左屏）：")
    add_body_p(doc, "提供“智能快递柜自提”、“配送员送货上门”以及“末端服务驿站暂存”三种交付模式供居民自主切换。居民选择直接写入底层订单属性，实时驱动后台任务分流引擎。", bold_prefix="（2）末端交付方式自主个性化选择（中屏）：")
    add_body_p(doc, "为避免碎片化时间要求打乱车辆集约化路径，小程序根据算法实时运力富余度，动态开放若干标准预约时间段（如 17:00—19:00、19:00—21:00）。居民确认后，该时间约束自动成为第五章人车协同调度算法的强约束条件，实现居民个性化诉求与系统集约化效益的最佳平衡。", bold_prefix="（3）基于运力余量的弹性时间窗预约（右屏）：")

    # 7.3.5
    add_h2(doc, "7.3.5 跨主体异常协同与闭环反馈联动系统")
    add_body_p(doc, "真实的社区末端配送环境充满动态不确定性。真正的现代化协同平台必须具备敏捷处置突发扰动的自愈能力。平台构建了跨主体、跨终端的动态异常协同响应机制，界面如图7-8所示。")
    add_fig(doc, "Fig7_6_Cross_Role_Dynamic_Exception_Closed_Loop.png", "图7-8 跨主体异常协同与闭环动态反馈联动系统界面")
    
    add_body_p(doc, "当社区发生突发扰动时，平台严格遵循“异常捕捉→信息上报→数字底座更新→多模型重算→任务重构派发→多端即时同步→现场闭环执行”的七步闭环联动体系：")
    add_body_p(doc, "配送员通过移动端上报 D04 至 D06 路段施工障碍；平台 GIS 底座瞬时将该路段权重置为不可通行；算法引擎秒级重算无人车避障绕行路径（由原主干道调整为次干道，里程增加 240 米，耗时增加 4 分钟）；运营驾驶舱高亮显示黄色绕行预警；配送管家 APP 即时更新人车交接倒计时；物流企业端与居民小程序同步修正预计履约时间，确保全链路信息无缝同步。", bold_prefix="典型场景一（社区内部道路突发施工）：")
    add_body_p(doc, "当 S02 柜机使用率达到 100% 时，系统触发格口容量预警，立即阻断新增订单向该柜分配，并严格依照“现有柜→邻近柜（S03 剩余 8 格）→末端驿站→人工上门”的溢流规则自动拆分任务；受影响订单自动转入配送员上门工单，并在居民端推送取件位置变更通知。", bold_prefix="典型场景二（目标智能快递柜格口满载）：")
    add_body_p(doc, "当车辆电池 SOC 降至 15% 临界阈值或上报故障代码时，系统自动冻结其后续未执行任务，触发备用无人车前往就近接驳点承接转移包裹，或将紧迫时间窗订单转派至周边机动配送员，保障全网履约 SLA 零降级。", bold_prefix="典型场景三（无人车低电量或机械故障）：")

    # 7.4
    add_h1(doc, "7.4 本章小结")
    add_body_p(doc, "本章在第三章需求估计与情景模拟、第四章末端配送网络规划、第五章无人配送与人工协同调度模型以及第六章动态仿真与综合评价的基础上，全面完成多模型驱动的社区末端共同配送协同决策与运行平台的系统设计与工程构建。")
    
    add_body_p(doc, "平台以“统一数据底座驱动、多端角色协同联动”为核心架构理念，通过自下而上的五层技术体系，成功打破了离线算法模型与在线实际业务之间的数字化断层。在算法与数据层面，平台实现了需求预测、拓扑映射、滚动组批、人车调度与仿真评价的全链路级联计算与双向反馈；在业务与应用层面，围绕单笔订单十阶段全生命周期，构建了涵盖共同配送运营管理端、物流企业协同端、配送执行移动端以及社区居民服务小程序的四端协同矩阵体系。")
    
    add_body_p(doc, "经碧水豪庭等示范区的实景数据验证，本平台展现出优异的系统鲁棒性与协同调度性能，实现了全网运力利用率达 94.3%、综合履约时效提升 32.5%、运营总成本下降 27.4% 以及末端碳排放降低 38.6% 的显著成效。本平台的成功构建，使整篇竞赛论文的前序数学规划与仿真推演成果真正落地为一套“看得见、调得动、管得住、评得准”的现代化智慧物流实战系统，为我国智慧城市社区末端物流的集约化、绿色化与数字化转型提供了极具推广价值的整体解决方案。")

    # Save
    doc.save(TARGET_ALIGNED)
    print(f"[SUCCESS] Rich & Aligned Document saved to: {TARGET_ALIGNED}")
    
    try:
        doc.save(TARGET_DOCX)
        print(f"[SUCCESS] Also updated: {TARGET_DOCX}")
    except PermissionError:
        print(f"[INFO] {TARGET_DOCX} is currently locked by editor. Saved to {TARGET_ALIGNED} instead.")

if __name__ == '__main__':
    build_rich_aligned_doc()
