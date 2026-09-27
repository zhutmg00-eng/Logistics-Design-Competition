import os
import shutil
import sys
import docx
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

src_file = r'C:\Users\zhutmg\Desktop\第七章平台(1).docx'
backup_file = r'C:\Users\zhutmg\Desktop\第七章平台(1)_backup_original.docx'

# Step 1: Backup
if not os.path.exists(backup_file):
    shutil.copyfile(src_file, backup_file)
    print(f"[OK] Backed up original file to: {backup_file}")
else:
    print(f"[INFO] Backup already exists at: {backup_file}")

print("Testing docx libraries and helper functions...")
