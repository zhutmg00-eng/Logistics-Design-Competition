# -*- coding: utf-8 -*-
import os
import re

base_dir = r"d:\物流设计大赛\chapter7_platform_frontend"

files_to_check = [
    "overview_matrix.html",
    "platform_architecture.html",
    "terminal_closed_loop.html",
    "terminal_courier.html",
    "terminal_enterprise.html",
    "terminal_resident.html",
    "index.html"
]

for fname in files_to_check:
    fpath = os.path.join(base_dir, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    orig = content

    # Replace glowing box-shadows: 0 0 Xpx with clean subtle drop shadows or borders
    # e.g. box-shadow: 0 0 16px rgba(...) -> box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35)
    content = re.sub(r"box-shadow:\s*0\s+0\s+(?:10|12|14|16|20)px\s+rgba\([^)]+\);", "box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);", content)
    content = re.sub(r"box-shadow:\s*0\s+0\s+(?:8|10|12)px\s+var\([^)]+\);", "box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);", content)
    content = re.sub(r"box-shadow:\s*0\s+0\s+(?:8|10|12)px\s+currentColor;", "box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);", content)
    content = re.sub(r"box-shadow:\s*0\s+0\s+8px\s+#0284c7;", "box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);", content)

    # In overview_matrix.html, also clean up the title gradient text to solid crisp text
    if fname == "overview_matrix.html":
        content = content.replace(
            "background: linear-gradient(90deg, #ffffff, #bae6fd);\n      -webkit-background-clip: text;\n      -webkit-text-fill-color: transparent;",
            "color: var(--text-main);\n      letter-spacing: -0.01em;"
        )
        content = content.replace(
            "background: linear-gradient(90deg, #ffffff, #bae6fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent;",
            "color: var(--text-main); letter-spacing: -0.01em;"
        )
        # Ensure any stray "碧水豪庭" is completely replaced with "亦城茗苑"
        content = content.replace("碧水豪庭", "亦城茗苑")

    if content != orig:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Refined OpenDesign styles in: {fname}")
    else:
        print(f"No changes needed in: {fname}")

print("All styles refined successfully!")
