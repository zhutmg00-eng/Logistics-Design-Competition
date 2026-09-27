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

print("=== Detailed Paragraph Formatting in 第三四五章（配图版）.docx ===")
count = 0
for child in body.findall(f'{W_NS}p'):
    texts = [t.text for t in child.iter(f'{W_NS}t') if t.text]
    full_text = "".join(texts).strip()
    if not full_text:
        continue
    
    pPr = child.find(f'{W_NS}pPr')
    sp_info = "None"
    ind_info = "None"
    jc_info = "None"
    if pPr is not None:
        sp = pPr.find(f'{W_NS}spacing')
        if sp is not None:
            sp_info = f"before={sp.get(f'{W_NS}before')}, after={sp.get(f'{W_NS}after')}, line={sp.get(f'{W_NS}line')}, lineRule={sp.get(f'{W_NS}lineRule')}"
        ind = pPr.find(f'{W_NS}ind')
        if ind is not None:
            ind_info = f"fl={ind.get(f'{W_NS}firstLine')}, flc={ind.get(f'{W_NS}firstLineChars')}, left={ind.get(f'{W_NS}left')}"
        jc = pPr.find(f'{W_NS}jc')
        if jc is not None:
            jc_info = jc.get(f'{W_NS}val')
            
    # Sample a few body paragraphs and headings
    if any(h in full_text[:10] for h in ['4.3', '4.3.1', '图4-', '表4-']) or (count < 15 and len(full_text) > 40):
        print(f"Text: {full_text[:40]}...")
        print(f"  jc={jc_info}, spacing=[{sp_info}], ind=[{ind_info}]")
        count += 1
        if count >= 12:
            break
