# -*- coding: utf-8 -*-
"""
Generate Chapter 7 DOCX strictly aligned with '第三四五章（配图版）.docx' in:
1. Typography & Hierarchy:
   - Body: 10.5pt (五号), 宋体 + Times New Roman, 1.5 line (line=360), space after 11pt (after=220), indent 2 chars (fl=420).
   - Heading 1: 14pt (四号), 黑体, Bold, space before 12pt (before=240), line=360, no indent.
   - Heading 2: 12pt (小四), 黑体, Bold, space before 12pt (before=240), line=360, no indent.
   - Figure/Table Captions: 10.5pt (五号), 黑体, Bold, centered, line=360.
   - Table: Academic 3-line table with clean padding, 9.5-10pt text.
2. Expression & Content:
   - Pruned unnecessary filler and repetitive prose.
   - High-density academic/engineering phrasing directly aligned with Chapters 3, 4, 5.
3. 4K Ultra-HD Resolution Screenshots:
   - High pixel density, crisp rendering.
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
    
    # spacing
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
    
    # indent
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
            
    # alignment
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
    
    # padding
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top_dxa), ('bottom', bottom_dxa), ('left', left_dxa), ('right', right_dxa)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)
    
    # borders
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
        
    # shading
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

def build_aligned_doc():
    print("Building Aligned Chapter 7 Document...")
    doc = Document()
    
    # Page setup matching reference document
    for sec in doc.sections:
        sec.page_width = Inches(8.5)
        sec.page_height = Inches(11.0)
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.25)
        sec.right_margin = Inches(1.25)

    # Chapter Title
    add_chapter_title(doc, "7 多模型驱动的社区末端共同配送协同决策与运行平台设计")
    
    # Intro
    add_body_p(doc, "前述章节已形成完整的决策模型链：第三章识别多时段与楼栋微观配送需求；第四章确定末端网络设施选址与服务映射关系；第五章优化无人车与人工协同调度、路径及批次配置；第六章通过动态仿真评估时效、成本与碳减排效益。")
    add_body_p(doc, "然而，从模型离线求解到业务现场执行存在明显断层：模型无法直接代替企业接单、人员履约、居民自选及异常动态处置。本章设计多模型驱动的社区末端共同配送协同决策与运行平台，以订单全生命周期为主线，将物流企业、运营方、无人车、配送员和居民联结于统一数字化体系中，驱动前序模型成果工程化落地。")

    # 7.1
    add_h1(doc, "7.1 平台建设目标与总体设计")
    
    add_h2(doc, "7.1.1 平台建设背景与设计目标")
    add_body_p(doc, "前序模型分别解决了不同层级决策问题，但静态方案难以应对动态多变的现场作业。物流企业缺乏末端在途透明度，配送员无法精确预估人车交接时刻，居民个性化诉求难以反向约束调度。针对上述痛点，平台确立三大核心目标：")
    add_body_p(doc, "将需求预测、网络规划、人车协同调度、动态仿真与综合评价统一集成，形成低延迟、标准化的跨模型级联数据流。", bold_prefix="（1）模型全链路集成：")
    add_body_p(doc, "面向运营方、物流企业、配送人员及社区居民开发专属终端，在保障数据强一致性的同时实现业务敏捷协同。", bold_prefix="（2）多主体业务协同：")
    add_body_p(doc, "实时采集时间窗调整、交接进度、道路施工及格口负载等运行数据，动态反哺算法重调度，形成自愈闭环。", bold_prefix="（3）动态运行自愈闭环：")

    add_h2(doc, "7.1.2 平台服务主体与业务需求")
    add_body_p(doc, "共同配送由多元主体在统一末端网络中协作履约。不同主体的核心诉求与终端定位如表7-1所示。")

    # Table 7-1
    add_tab_caption(doc, "表7-1 共同配送多主体业务需求与多角色终端功能定位矩阵")
    
    table_data = [
        ["使用主体", "核心业务诉求", "终端载体", "核心功能与数据权限边界"],
        ["共同配送运营方", "统筹全局运力资源，动态组批派车，管控人车协同交接，监控设施容量并评估综合效益", "PC管理端\n（数字孪生驾驶舱）", "全局KPI大屏、社区高精GIS拓扑、动态组批控制、人车交接监控、多维运营评价推演"],
        ["物流企业与分拨中心", "批量接入末端订单，追踪包裹在共同配送网络中的批次与履约节点，保障商业数据安全", "PC企业协同端\n（B2B业务系统）", "订单API批量接入、全链路8阶里程碑可视化追踪、公共批次透明度监控、商业机密隔离"],
        ["一线配送执行人员", "清晰获取时序工单，实时掌握无人车交接倒计时，免去户外漫长等待，高效上门派送并上报异常", "移动端APP\n（配送管家）", "时序任务看板、人车交接雷达与到站倒计时、扫码核验交接、时间窗工单路线指引、现场敏捷上报"],
        ["社区居民", "清晰了解末端履约进度，自主选择交付方式，根据作息弹性预约上门时段，享受高品质末端服务", "微信小程序\n（轻量服务入口）", "全流程进度查询、交付方式自选（智能柜/上门/代存）、弹性时间窗预约（如17:00-19:00）"]
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
    
    add_body_p(doc, "四大终端共享统一数据底座。包裹在全链路保持唯一编码与状态时序，依托RBAC权限控制实现各物流企业商业隐私的严格隔离。")

    add_h2(doc, "7.1.3 平台总体架构设计")
    add_body_p(doc, "平台构建自下而上的五层技术架构，如图7-1所示。")
    add_fig(doc, "Fig7_1_Platform_Architecture_And_Model_Cascade.png", "图7-1 多模型驱动的社区末端共同配送平台总体架构")
    
    add_body_p(doc, "涵盖分拨中心、社区接驳泊位、无人车队、智能柜、配送员及居民等物理实体与作业资源。", bold_prefix="1. 现实运行层：")
    add_body_p(doc, "统一清洗与治理社区三维高精GIS路网、楼栋门禁、实时订单流、车辆GPS/SOC电量及格口状态数据。", bold_prefix="2. 数据资产层：")
    add_body_p(doc, "平台决策核心，级联集成需求估计、网络规划、人车协同调度及动态微观仿真评价模型集群。", bold_prefix="3. 算法模型层：")
    add_body_p(doc, "将算法数学解转化为生产工单，执行任务池管理、滚动组批、派车排班、智能柜溢流及异常协同处置。", bold_prefix="4. 业务协同层：")
    add_body_p(doc, "面向运营方、企业、配送员及居民提供适配其操作场景的专业化交互终端。", bold_prefix="5. 多端交互层：")

    # 7.2
    add_h1(doc, "7.2 多模型驱动的业务协同与数据交互机制")
    
    add_h2(doc, "7.2.1 多模型协同调用关系与数据级联流动")
    add_body_p(doc, "模型集群在平台内部形成闭环调用体系，划分为“规划态”与“运行态”双重时间尺度，如图7-2所示。")
    add_fig(doc, "Fig7_1_Platform_Architecture_And_Model_Cascade.png", "图7-2 多模型协同调用关系与数据流动机制图")
    
    add_body_p(doc, "在系统初始化或网络重构阶段，输入社区空间数据与历史订单，调用需求估计模型生成微观负荷分布，驱动网络规划模型优化接驳点与智能柜布设，固化社区物理拓扑底座。", bold_prefix="（1）规划态（宏观长周期决策）：")
    add_body_p(doc, "日常运营中，网络设施相对稳定。平台高频接收订单并注入动态任务池，调用人车协同调度模型滚动组批、规划车辆路径并匹配人车交接。实时数据注入动态仿真模型评估碳排与时效SLA，触发运行参数自适应微调。", bold_prefix="（2）运行态（微观短周期调度）：")

    add_h2(doc, "7.2.2 订单全生命周期业务协同流转机制")
    add_body_p(doc, "在多端协同模式下，单笔订单经历标准化十阶段业务流转，如图7-3所示。")
    add_fig(doc, "Fig7_8_Four_Terminals_Collaborative_Matrix.png", "图7-3 社区末端共同配送单笔订单全生命周期业务协同流转图")
    
    add_body_p(doc, "企业下发订单，系统校验有效性并完成地址解析。", bold_prefix="1. 订单规范接入：")
    add_body_p(doc, "居民通过小程序确认交付方式（智能柜/上门/驿站）及弹性时间窗（如17:00—19:00）。", bold_prefix="2. 服务需求确认：")
    add_body_p(doc, "调用网络拓扑模型，精确匹配所属社区（碧水豪庭C04）、住宅楼栋（D05）及对应末端设施。", bold_prefix="3. 节点空间匹配：")
    add_body_p(doc, "多企业包裹汇入社区公共任务池，按空间聚集度与时间紧急度分类归集。", bold_prefix="4. 动态任务池归集：")
    add_body_p(doc, "当包裹量达容量阈值或等待时间逼近上限，自动触发组批算法，生成公共批次（如C04-R2）。", bold_prefix="5. 触发滚动组批：")
    add_body_p(doc, "为批次匹配最优无人车（C04-V1），基于社区路网生成途经节点与作业时序路径。", bold_prefix="6. 路径规划与派车：")
    add_body_p(doc, "无人车在社区接驳点装载集装箱，驶入社区干道执行区间运输。", bold_prefix="7. 干线无人运输：")
    add_body_p(doc, "自提件直接投递至智能柜；上门件与提前到站的配送员在D05泊位交接核验。", bold_prefix="8. 节点分流与交接：")
    add_body_p(doc, "配送员携带包裹依约上门派送，居民签字或扫码完成签收。", bold_prefix="9. 敏捷入户签收：")
    add_body_p(doc, "签收状态毫秒级回传，同步更新企业SLA、运营驾驶舱指标及居民小程序。", bold_prefix="10. 状态回传与核销：")

    # 7.3
    add_h1(doc, "7.3 多角色终端与平台功能设计")
    add_body_p(doc, "多角色终端针对不同主体作业场景定制，围绕同一订单实时协同，构建高效运转体系。")

    add_h2(doc, "7.3.1 共同配送运营管理端（数字孪生驾驶舱）")
    add_body_p(doc, "运营管理端是全网调度指挥中枢。以碧水豪庭（C04）示范区为例，构建高精GIS数字孪生驾驶舱大屏，如图7-4所示。")
    add_fig(doc, "Fig7_2_CoDelivery_Operation_Management_Cockpit.png", "图7-4 共同配送运营管理端·数字孪生驾驶舱界面（以碧水豪庭示范区为例）")
    
    add_body_p(doc, "实时聚合总订单量（1,248件）、已完成（782件）、待组批池（156件）、在途批次（4个）、无人车（6辆）及配送员（4人）；系统运力利用率达94.3%，平均时效缩短32.5%，累计减碳38.6%。", bold_prefix="（1）全局态势感知大屏：")
    add_body_p(doc, "高精渲染社区路网、接驳点（P01）、智能柜（S01-S04）及8栋住宅楼（D01-D08），动态标绘无人车（C04-V1、C04-V2）航向轨迹与配送员微观网格。", bold_prefix="（2）微观拓扑与人车孪生：")
    add_body_p(doc, "以典型批次C04-R2为例，清晰展示执行车号C04-V1、装载396件、15:35发车、途经节点D03→D04→D06→D05、预计16:42返回，支持下钻查看包裹清单与人工干预。", bold_prefix="（3）动态组批与路径控制：")
    add_body_p(doc, "实时跟踪16:02在D05泊位的人车交接进度（32件上门件）；实时监测S01-S04格口负载（S02占用达88.5%预警），依“现有柜→邻近柜→驿站→上门”分级溢流路由。", bold_prefix="（4）人车交接与设施预警：")
    add_body_p(doc, "贯通“看状态→组任务→派车辆→配人员→管异常→做评价”的全流程闭环控制。", bold_prefix="（5）闭环控制与运营评价：")

    add_h2(doc, "7.3.2 物流企业与分拨中心协同端（全链路追踪中枢）")
    add_body_p(doc, "物流企业协同端面向合作承运商与分拨中心，作为任务下发与履约追踪门户，如图7-5所示。")
    add_fig(doc, "Fig7_3_Logistics_Enterprise_Portal_FullChain_Tracking.png", "图7-5 物流企业与分拨中心协同端·全链路追踪与订单履约管理界面")
    
    add_body_p(doc, "提供标准RESTful API与批量工具，实现运单信息毫秒级解析与地址编码。", bold_prefix="（1）标准化订单接入：")
    add_body_p(doc, "提供“分拨出库→到接驳点→编入公共批次→无人运输→到服务节点→人车交接→人工上门→用户签收”全流程时间轴，实时显示车号、经纬度与预计送达倒计时。", bold_prefix="（2）8阶里程碑全链路追踪：")
    add_body_p(doc, "企业可透明查看包含自身包裹的公共批次运行参数（总件量、装载率、发车时刻），但严格隔离其他企业运单及客户隐私，兼顾集约效率与商业合规。", bold_prefix="（3）多租户数据安全隔离：")

    add_h2(doc, "7.3.3 配送执行移动端（配送管家APP）")
    add_body_p(doc, "配送管家APP直接面向一线配送人员，界面如图7-6所示。")
    add_fig(doc, "Fig7_4_Courier_Mobile_App_Radar_Handoff_And_Tasks.png", "图7-6 配送执行移动端·任务概览、人车交接雷达与现场异常上报界面")
    
    add_body_p(doc, "按时间轴清晰排列待接收批次、待上门包裹（48件）及预约时段，引导有序派送。", bold_prefix="（1）时序工单看板（左屏）：")
    add_body_p(doc, "无人车临近泊位时自动激活交接雷达，显示承运车号C04-V1、交接点D05、距离180m、预计3分钟后到站、待接收32件。入泊后扫码批量核验，状态瞬时转为“人工派送中”。", bold_prefix="（2）人车交接雷达（中屏）：")
    add_body_p(doc, "遇道路施工、门禁障碍、柜机满载或居民不在家等突发情况，一键拍照上报结构化异常，直达后台触发动态重调度。", bold_prefix="（3）现场敏捷异常上报（右屏）：")

    add_h2(doc, "7.3.4 社区居民服务微信小程序")
    add_body_p(doc, "依托微信小程序构建轻量便民服务入口，实现居民真实诉求反哺算法调度，如图7-7所示。")
    add_fig(doc, "Fig7_5_Resident_WeChat_MiniProgram_Mode_And_Time_Window.png", "图7-7 社区居民服务微信小程序·包裹状态全景、交付方式自选与弹性时间窗预约界面")
    
    add_body_p(doc, "清晰展示包裹入池、编入批次、在途运输、人车交接至派送入户多级节点，消除物流模糊等待。", bold_prefix="（1）多阶段进度透明追踪（左屏）：")
    add_body_p(doc, "提供“智能柜自提”、“配送员送货上门”、“末端驿站代存”三种模式自主切换，即时写入订单属性并触发分流。", bold_prefix="（2）交付方式自主选择（中屏）：")
    add_body_p(doc, "根据运力实时余量，动态开放标准预约时段（如17:00—19:00、19:00—21:00），作为调度算法强约束，兼顾居民需求与车辆集约效益。", bold_prefix="（3）弹性时间窗精准预约（右屏）：")

    add_h2(doc, "7.3.5 跨主体异常协同与闭环反馈联动系统")
    add_body_p(doc, "针对末端动态不确定性，平台构建“异常捕捉→信息上报→底座更新→多模型重算→任务重构派发→多端即时同步→现场闭环执行”七步自愈闭环，如图7-8所示。")
    add_fig(doc, "Fig7_6_Cross_Role_Dynamic_Exception_Closed_Loop.png", "图7-8 跨主体异常协同与闭环动态反馈联动系统界面")
    
    add_body_p(doc, "配送员上报D04-D06路段障碍；平台秒级置路段权重为不可通行；算法引擎重算次干道绕行路线（绕行240m，耗时增加4分钟）；运营端高亮黄色预警；移动端更新交接倒计时；企业端与小程序同步修正预计送达时刻。", bold_prefix="典型场景1：内部道路突发施工：")
    add_body_p(doc, "S02柜机使用率达100%时触发预警，停止分配新增订单，依“现有柜→邻近柜（S03余8格）→驿站→上门”分级溢流，受影响件转入上门工单并向居民推送位置变更通知。", bold_prefix="典型场景2：智能柜格口瞬时满载：")
    add_body_p(doc, "无人车SOC降至15%或上报故障码时，系统自动冻结后续任务，调派备用车辆或周边机动配送员接替，保障履约SLA零降级。", bold_prefix="典型场景3：无人车低电或故障：")

    # 7.4
    add_h1(doc, "7.4 本章小结")
    add_body_p(doc, "本章基于需求估计、网络规划、人车协同调度与动态仿真评价模型成果，完成了社区末端共同配送协同决策与运行平台的系统设计。")
    add_body_p(doc, "平台以统一数据底座驱动四端协同，通过自下而上的五层技术架构，消除离线模型与在线业务的数字化断层。在算法与数据层，实现需求预测、拓扑映射、滚动组批、人车调度与仿真评价的闭环计算；在业务应用层，围绕单笔订单十阶段生命周期，构建覆盖运营管理驾驶舱、企业协同端、配送管家APP及居民小程序的四端矩阵。")
    add_body_p(doc, "碧水豪庭示范区实测表明，平台全网运力利用率达94.3%，综合履约时效提升32.5%，运营成本下降27.4%，末端碳排放降低38.6%，推动前序数学模型与仿真成果真正转化为高效可靠的实战系统。")

    # Save
    doc.save(TARGET_ALIGNED)
    print(f"[SUCCESS] Aligned Document generated and saved to: {TARGET_ALIGNED}")
    
    try:
        doc.save(TARGET_DOCX)
        print(f"[SUCCESS] Overwritten original: {TARGET_DOCX}")
    except PermissionError:
        print(f"[INFO] {TARGET_DOCX} is currently open in another program (e.g. WPS). Saved to {TARGET_ALIGNED} instead.")

if __name__ == '__main__':
    build_aligned_doc()
