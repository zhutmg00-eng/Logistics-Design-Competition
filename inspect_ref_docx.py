import zipfile
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

ref_path = r'C:\Users\zhutmg\Desktop\第三四五章（配图版）.docx'
with zipfile.ZipFile(ref_path, 'r') as zf:
    styles_xml = zf.read('word/styles.xml')
    doc_xml = zf.read('word/document.xml')

root_s = ET.fromstring(styles_xml)
W_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

print("=== 1. Styles in 第三四五章（配图版）.docx ===")
for style in root_s.findall(f'{W_NS}style'):
    s_id = style.get(f'{W_NS}styleId')
    s_type = style.get(f'{W_NS}type')
    name_el = style.find(f'{W_NS}name')
    name = name_el.get(f'{W_NS}val') if name_el is not None else s_id
    
    rPr = style.find(f'{W_NS}rPr')
    fonts_str = ''
    sz_str = ''
    bold_str = ''
    if rPr is not None:
        rFonts = rPr.find(f'{W_NS}rFonts')
        if rFonts is not None:
            a = rFonts.get(f'{W_NS}ascii')
            ea = rFonts.get(f'{W_NS}eastAsia')
            fonts_str = f"ascii={a}, eastAsia={ea}"
        sz = rPr.find(f'{W_NS}sz')
        if sz is not None:
            sz_str = f"{int(sz.get(f'{W_NS}val'))/2}pt"
        if rPr.find(f'{W_NS}b') is not None:
            bold_str = "BOLD"
            
    pPr = style.find(f'{W_NS}pPr')
    spacing_str = ''
    ind_str = ''
    if pPr is not None:
        sp = pPr.find(f'{W_NS}spacing')
        if sp is not None:
            before = sp.get(f'{W_NS}before')
            after = sp.get(f'{W_NS}after')
            line = sp.get(f'{W_NS}line')
            lineRule = sp.get(f'{W_NS}lineRule')
            spacing_str = f"before={before}, after={after}, line={line}, lineRule={lineRule}"
        ind = pPr.find(f'{W_NS}ind')
        if ind is not None:
            fl = ind.get(f'{W_NS}firstLine')
            flc = ind.get(f'{W_NS}firstLineChars')
            ind_str = f"firstLine={fl}, firstLineChars={flc}"

    print(f"[{s_id}] {name} ({s_type}): font=[{fonts_str}], size={sz_str}, {bold_str} | spacing=[{spacing_str}], ind=[{ind_str}]")

print("\n=== 2. Inspecting Sample Paragraphs in document.xml ===")
root_d = ET.fromstring(doc_xml)
body = root_d.find(f'{W_NS}body')

p_count = 0
for child in body:
    if child.tag == f'{W_NS}p':
        p_count += 1
        pPr = child.find(f'{W_NS}pPr')
        pStyle = 'None'
        if pPr is not None:
            pStyle_el = pPr.find(f'{W_NS}pStyle')
            if pStyle_el is not None:
                pStyle = pStyle_el.get(f'{W_NS}val')
        
        # text
        texts = []
        for t in child.iter(f'{W_NS}t'):
            if t.text:
                texts.append(t.text)
        full_text = "".join(texts).strip()
        
        # check runs for direct fonts/sizes
        run_fonts = []
        for r in child.findall(f'{W_NS}r'):
            rPr = r.find(f'{W_NS}rPr')
            if rPr is not None:
                rf = rPr.find(f'{W_NS}rFonts')
                sz = rPr.find(f'{W_NS}sz')
                b = rPr.find(f'{W_NS}b')
                f_desc = []
                if rf is not None:
                    f_desc.append(f"ea={rf.get(f'{W_NS}eastAsia')}, a={rf.get(f'{W_NS}ascii')}")
                if sz is not None:
                    f_desc.append(f"{int(sz.get(f'{W_NS}val'))/2}pt")
                if b is not None:
                    f_desc.append("B")
                if f_desc:
                    run_fonts.append(":".join(f_desc))
        
        if full_text and (p_count <= 40 or any(kw in full_text for kw in ['3.', '4.', '5.', '图3-', '图4-', '图5-', '表3-', '表4-'])):
            rf_str = f" | Runs: {set(run_fonts)}" if run_fonts else ""
            print(f"P{p_count:03d} (Style={pStyle}){rf_str}: {full_text[:80]}")

sectPr = body.find(f'{W_NS}sectPr')
if sectPr is not None:
    pgSz = sectPr.find(f'{W_NS}pgSz')
    pgMar = sectPr.find(f'{W_NS}pgMar')
    print("\n=== 3. Section Properties ===")
    if pgSz is not None:
        print(f"Page Size: w={pgSz.get(f'{W_NS}w')}, h={pgSz.get(f'{W_NS}h')}")
    if pgMar is not None:
        print(f"Page Margins: top={pgMar.get(f'{W_NS}top')}, bottom={pgMar.get(f'{W_NS}bottom')}, left={pgMar.get(f'{W_NS}left')}, right={pgMar.get(f'{W_NS}right')}")
