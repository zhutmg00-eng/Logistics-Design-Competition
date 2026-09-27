# OpenDesign System Contract: 社区末端共同配送协同平台

> **Reference:** [nexu-io/open-design](https://github.com/nexu-io/open-design)  
> **Modules Applied:** `craft/anti-ai-slop.md`, `craft/typography.md`, `craft/color.md`, `craft/animation-discipline.md`, `craft/accessibility-baseline.md`  
> **Implementation Scope:** `d:/物流设计大赛/chapter7_platform_frontend/`

---

## 1. 核心设计原则 (Core Principles)

本系统严格遵照 OpenDesign 规范构建，全面杜绝 AI 生成界面的模式化瑕疵（AI Slop）：

1. **零元演示控件 (No Meta-Demo Artifacts)**:
   - 彻底移除所有“查看截图”、“Demo”、“原型模式”等非生产性元元素。
   - 所有界面均呈现为真实的 100% 生产环境（Production Grade）调度中枢与多端运行系统（如调度员状态栏、动态时钟、真实生产版本号 `v2.4.0`）。

2. **严控默认靛蓝与渐变 (No Default Tailwind Indigo & Two-Stop Trust Gradients)**:
   - 禁用 `#6366f1`、`#4f46e5`、`#8b5cf6`、`#7c3aed` 等 AI 典型指纹色。
   - 采用专业物流科技深色底座（`#070a12` / `#0f172a` / `#151e30`），主色统一为稳健深邃的工程天蓝（`#0284c7`），辅助色包含顺丰红（`#dc2626`）、运力绿（`#10b981`）、预警橙（`#f59e0b`）。
   - 禁用两点对角紫色到蓝色之“信任渐变”。

3. **矢量单线图标替代 Emoji 与粗糙字符 (Monoline SVG Icons over Emojis & Dingbats)**:
   - 依据 OpenDesign Cardinal Sin #3，严格禁止在标题、按钮、Tab、列表、图例中使用 Emoji（如 📐、🌐、🖥️、📱、💬、🔄、📸）或原始 Unicode 符号（如 `✓`、`✕`、`➜`、`↑`、`↓`、`●`、`▲`）。
   - 全面使用 `1.6–1.8px` 描边、`currentColor` 的单线矢量 SVG 图标（Sleek Monoline SVGs），统一通过 `.od-icon`、`.od-icon-sm`、`.check-icon` 规范控制。

4. **消除圆角卡片粗彩条 (No Left/Top-Border AI Dashboard Stripes)**:
   - 依据 OpenDesign Cardinal Sin #5，圆角卡片禁止附加 `4px/5px` 单边强调色粗边框（如 `.term-box::before`、`tr.selected border-left: 3px solid`）。
   - 卡片采用精致的 1px 细微边界（`rgba(255,255,255,0.08)` 至 `0.14`），状态标识通过内部微章（Pill Badge）或呼吸状态点（`.pulse-dot`）表达。

5. **中文排版底线 (CJK Typography Discipline)**:
   - 中文标题行高严格遵循 OpenDesign CJK 规范：`line-height: 1.35–1.4`，禁止使用西方字体紧凑的 `1.0–1.2` 导致叠字。
   - 正文字体行高为 `1.6–1.7`。中文字符间距保持自然 `0`，禁止对中文标题使用负字偶距（Negative Tracking）。
   - 包含时间、坐标、指标、批次号的所有数值均启用等宽对齐特性（`.tnum` / `font-variant-numeric: tabular-nums`）。

6. **真实领域数据与指标 (Honest Domain Data)**:
   - 数据完全契合第七章学术方案与实际工程场景（如 C04-R2 批次、C04-V1 车型、D01–D08 楼栋节点、S01–S04 柜机、16:02 D05 泊位交接、17:00–19:00 预约窗）。

---

## 2. 语义 Token 规范 (Token Specification)

详见 `tokens.css`。所有前端页面均引入并消费该 Token 表。
全局定义了 Neutrals (70-90%)、Single Intentional Accent (5-10%)、Semantic Tokens (0-5%) 及 Multiplicative 1.25 Typography Scale。
