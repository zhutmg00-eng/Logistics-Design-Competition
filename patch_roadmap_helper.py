from pathlib import Path
p=Path(r"D:\物流设计大赛\generate_technical_roadmap_concise.py")
s=p.read_text(encoding="utf-8")
old='def text(ax, x, y, s, size=10, color="#24465F", weight="normal", ha="left", va="center", z=5):\n    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,\n            ha=ha, va=va, zorder=z)'
new='def text(ax, x, y, s, size=10, color="#24465F", weight="normal", ha="left", va="center", z=5, **kwargs):\n    ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,\n            ha=ha, va=va, zorder=z, **kwargs)'
if old not in s:
    raise SystemExit('target not found')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('patched')
