from pathlib import Path
p=Path(r"D:\物流设计大赛\generate_technical_roadmap_concise.py")
s=p.read_text(encoding='utf-8')
old='text(ax, bx + bw / 2, by + bh * 0.85, module_title, 10.3, accent, "bold", "center", z=5)'
new='text(ax, bx + bw / 2, by + bh * 0.85, module_title, 10.3, "#FFFFFF", "bold", "center", z=5)'
if old not in s:
    raise SystemExit('module title target not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('module titles fixed')
