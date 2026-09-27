import zipfile
import sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding='utf-8')

ref_path = r'C:\Users\zhutmg\Desktop\第三四五章（配图版）.docx'
with zipfile.ZipFile(ref_path, 'r') as zf:
    doc_xml = zf.read('word/document.xml')

root_d = ET.fromstring(doc_xml)
W_NS = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
body = root_d.find(f'{W_NS}body')

print("=== Headings and Figures in 第三四五章（配图版）.docx ===")
for child in body.findall(f'{W_NS}p'):
    texts = [t.text for t in child.iter(f'{W_NS}t') if t.text]
    full_text = "".join(texts).strip()
    if not full_text:
        continue
    
    if any(full_text.startswith(kw) for kw in ['3.', '4.', '5.', '图3-', '图4-', '图5-', '表3-', '表4-', '表5-']):
        pPr = child.find(f'{W_NS}pPr')
        sp_info = "None"
        ind_info = "None"
        jc_info = "None"
        if pPr is not None:
            sp = pPr.find(f'{W_NS}spacing')
            if sp is not None:
                sp_info = f"before={sp.get(f'{W_NS}before')}, after={sp.get(f'{W_NS}after')}, line={sp.get(f'{W_NS}line')}"
            ind = pPr.find(f'{W_NS}ind')
            if ind is not None:
                ind_info = f"fl={ind.get(f'{W_NS}firstLine')}, flc={ind.get(f'{W_NS}firstLineChars')}"
            jc = pPr.find(f'{W_NS}jc')
            if jc is not None:
                jc_info = jc.get(f'{W_NS}val')
        
        # runs
        run_fonts = []
        for r in child.findall(f'{W_NS}r'):
            rPr = r.find(f'{W_NS}rPr')
            if rPr is not None:
                rf = rPr.find(f'{W_NS}rFonts')
                sz = rPr.find(f'{W_NS}sz')
                b = rPr.find(f'{W_NS}b')
                f_desc = []
                if rf is not None:
                    f_desc.append(f"ea={rf.get(f'{W_NS}eastAsia')}")
                if sz is not None:
                    f_desc.append(f"{int(sz.get(f'{W_NS}val'))/2}pt")
                if b is not None:
                    f_desc.append("B")
                run_fonts.append(":".join(f_desc))
        
        print(f"[{full_text[:35]}] jc={jc_info}, sp=[{sp_info}], ind=[{ind_info}], runs={run_fonts[:2]}")
