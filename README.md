# 面向超大城市的末端配送协同网络数智化与绿色化决策平台

## 1. 项目简介

本项目面向超大城市末端配送中普遍存在的空间约束严苛、多主体分散配送、末端设施容量失衡以及末端配送成本高企等现实痛点，立足北京经济技术开发区（亦庄高级别自动驾驶示范区）的实证地理底座与运行数据，构建了一套集“多尺度需求预测、混合整数规划选址定容、人机协同双层路径优化、离散事件动态仿真与智能应急调度”于一体的闭环数智化决策支持系统。

系统通过建立“物流分拨中心（HUB）— 社区接驳点 — 智能快件柜/楼栋单元”三级协同网络，实现了干线无人微卡集约巡回、末端无人车精准投柜补货与网格快递员上门履约的深度协同。

---

## 2. 成果展示与系统界面

### 2.1 现状诊断 (As-Is) vs 优化协同方案 (To-Be) 全景对比
系统提供现状纯人工粗放模式与数智化人机协同网络的同屏对比评价，全方位量化干线里程削减、末端工效提升、满柜风险清除与投资回收效益。

![现状诊断与优化方案全景对比看板](docs/images/comparison_telemetry.png)

### 2.2 空间数字孪生底座与运筹求解控制台
系统完整接入亦庄示范区 5 大典型社区（老旧多层、低密别墅、板楼混合、高密高层等）真实 WGS84 边界、336 条内部微循环路网及拓扑节点，并在前端提供严谨的运筹学数学规划公式与求解器收敛过程监控。

![数字孪生底座与运筹算法求解控制台](docs/images/platform_overview.png)

---

## 3. 核心运筹优化模型与数学表达

### 3.1 M1 干线巡回旅行商模型 (Trunk Tour TSP)
为消除现状各企业车辆从枢纽到社区独立点对点往返所造成的严重空驶率，构建以总干线运输里程最小化为目标的 TSP 巡回模型，并引入 MTZ（Miller-Tucker-Zemlin）约束消除子回路：

$$\min Z_1 = \sum_{i \in V} \sum_{j \in V} c_{ij} x_{ij}$$

$$\text{s.t.} \quad \sum_{j \in V, j \ne i} x_{ij} = 1, \quad \forall i \in V$$

$$\sum_{i \in V, i \ne j} x_{ij} = 1, \quad \forall j \in V$$

$$u_i - u_j + |V| x_{ij} \le |V| - 1, \quad \forall i, j \in V \setminus \{\text{HUB}\}, i \ne j$$

$$x_{ij} \in \{0, 1\}, \quad u_i \in \mathbb{R}$$

求解采用 2-Opt 局部搜索启发式算法，干线总里程由现状独立往返 24.84 km 压缩至 13.42 km，里程降幅达 46.0%。

### 3.2 M5 多尺度需求预测与二项 Logit 服务模式选择模型
结合社区宏观户数强度与微观人群属性，基于随机效用最大化（RUM）理论建立离散选择模型，划分送货上门（Doorstep Delivery）与智能柜自提（Locker Self-pickup）需求：

$$V_{\text{door}, i} = \beta_{0, \text{door}} + \beta_{\text{age}} \cdot \text{AgeRatio}_i + \beta_{\text{stair}} \cdot (1 - \text{HighRise}_i)$$

$$V_{\text{locker}, i} = \beta_{0, \text{locker}} - \beta_{\text{walk}} \cdot \frac{D_{\text{walk}, i}}{100} + \beta_{\text{flex}} \cdot \text{YoungRatio}_i$$

$$P(\text{door} \mid i) = \frac{\exp(V_{\text{door}, i})}{\exp(V_{\text{door}, i}) + \exp(V_{\text{locker}, i})}, \quad P(\text{locker} \mid i) = 1 - P(\text{door} \mid i)$$

微观楼栋层快件量按户数与建筑形态权重守恒拆分，并生成 08:00 至 21:00 典型 6 时段分时到件负荷曲线。

### 3.3 M6 容量受限选址定容混合整数规划模型 (Capacitated Facility Location & Sizing MIP)
针对传统单柜配置引发的高峰期严重满柜瓶颈，建立设施激活、副柜扩容与楼栋指派的多目标 MIP 模型：

$$\min Z_6 = \sum_{j \in \mathcal{F}} (f_j y_j + c_s s_j) + \rho \sum_{i \in \mathcal{B}} \sum_{j \in \mathcal{F}} d_{ij} q_i x_{ij}$$

$$\text{s.t.} \quad \sum_{j \in \mathcal{F}} x_{ij} = 1, \quad \forall i \in \mathcal{B}$$

$$d_{ij} x_{ij} \le R_{\max} \; (150\,\text{m}), \quad \forall i \in \mathcal{B}, j \in \mathcal{F}$$

$$\sum_{i \in \mathcal{B}} q_i x_{ij} \le (C_{\text{main}} y_j + C_{\text{slave}} s_j) \cdot \theta_{\text{turnover}}, \quad \forall j \in \mathcal{F}$$

$$x_{ij} \le y_j, \quad s_j \le S_{\max} y_j, \quad \forall i, j$$

$$y_j \in \{0, 1\}, \quad s_j \in \mathbb{Z}_{\ge 0}, \quad x_{ij} \in \{0, 1\}$$

模型自适应配置 56 格口候选扩容副柜，确保自提快件高峰期柜体饱和度稳定在 60% 至 70% 的健康区间，彻底清除爆柜滞留隐患。

### 3.4 M2 社区双层人机协同车辆路径模型 (Two-Echelon Collaborative CVRP)
界定无人配送车（X3 标称载重 200kg/容积 450L，等效运力 400 件）与人工快递员的分工界面：
- 无人车：承担出入口接驳点至各激活设施点、非上门楼栋入口的巡航投柜；
- 快递员：专注于老龄人群及特定大件楼栋的最后 100 米精准上门服务；
- 约束条件：包含单车次容量约束（400 件/次）与单网格快递员单日工时红线约束（480 分钟）。

### 3.5 M8 离散事件动态仿真系统 (Discrete Event Simulation DES)
构建 08:00 至 21:00 动态推进的离散事件状态转移模型：

$$O_j(t + \Delta t) = \max\Big(0, \; \min\big(C_j^{\text{eff}}, \; O_j(t) + \Delta A_j(t) - \Delta D_j(t)\big)\Big)$$

其中包裹到达增量遵循非齐次泊松过程 $\Delta A_j(t) \sim \text{Poisson}(\lambda_j(t)\Delta t)$，居民取件释放遵循二项分布 $\Delta D_j(t) \sim \text{Binomial}(O_j(t), P_{\text{pickup}}(t))$。

---

## 4. 现状基准 (As-Is) 与 优化协同 (To-Be) 综合对比

| 评价维度 | 现状纯人工基准 (As-Is) | 优化协同方案 (To-Be) | 改善幅度与量化效益 |
| :--- | :--- | :--- | :--- |
| 干线运输总里程 | 24.84 km（5点独立往返） | 13.42 km（M1闭环巡回） | 降低 46.0%（节约 11.42 km） |
| 社区内人工步巡里程 | 13.78 km（全楼栋覆盖） | 9.07 km（仅上门子集） | 降低 34.2%（节约 4.71 km） |
| 全网人工总投入工时 | 151.2 小时/日（负荷过载） | 60.8 小时/日（集约高效） | 降低 59.8%（释放 90.4 工时/日） |
| 智能柜满柜风险社区数 | 3 个社区严重超载（峰值 152%） | 0 个社区（负荷稳定在 60-70%） | 彻底消除 100% 满柜风险 |
| 年运营总成本 (OPEX) | 283.4 万元/年 | 131.4 万元/年 | 年均净节约 152.0 万元 (降低 53.6%) |
| 年干线运输碳排放量 | 1,459.2 kg CO2（燃油微卡） | 187.3 kg CO2（纯电无人车） | 降低 87.2%（年减排 1,271.9 kg） |
| 静态投资回收期 | - | 0.39 年（约 4.7 个月） | 设备初期改造成本极速收回 |

---

## 5. 系统架构与技术栈

系统采用高性能前后端分离与轻量化微服务架构：

```
+-----------------------------------------------------------------------------------+
|                  前端展现层: WebGIS 数字孪生与运筹算法控制台                       |
|  - Vue 3 核心状态机 + Tailwind CSS 响应式科技主题                                 |
|  - Leaflet 1.9.4 + 高德暗黑矢量底图 (国内无障碍加载)                              |
|  - ECharts 5 专业图表库 (满柜时序对抗图、五维效益雷达图、成本减碳对比柱状图)       |
|  - KaTeX 出版级数学公式实时渲染引擎                                               |
+-----------------------------------------------------------------------------------+
                                         │  ▲  HTTP RESTful API (JSON)
                                         ▼  │
+-----------------------------------------------------------------------------------+
|                  服务接口层: FastAPI 异步服务与网关中间件 (server.py)             |
|  - /api/overview: 全网拓扑、M1干线规划与全景对比核心指标矩阵                      |
|  - /api/calculate: 动态需求预测、MIP定容选址、M2人车协同路径多阶段连续求解        |
|  - /api/simulation: 08:00-21:00 离散事件动态仿真状态机                           |
|  - /api/solver/models: 五大核心规划模型 LaTeX 规范表达字典                        |
|  - /api/amap/*: 高德开放平台 Web 服务接入与北京全域小区实时搜索规划               |
+-----------------------------------------------------------------------------------+
                                         │  ▲  内存数据流
                                         ▼  │
+-----------------------------------------------------------------------------------+
|                  算法核心层: 运筹优化与智能调度引擎 (demo/core/)                  |
|  - data_manager.py: 空间数据、路网边表与设施拓扑解析器                            |
|  - forecast_model.py: 多尺度需求分解与二项 Logit 离散选择模型                     |
|  - layout_optimizer.py: 容量受限选址定容混合整数规划 (MIP)                        |
|  - routing_engine.py: TSP 干线巡回与多主体协同 CVRP 引擎                          |
|  - simulation_engine.py: 离散事件动态仿真内核 (DES)                               |
|  - ai_copilot.py: 极端场景（大促暴单/极寒暴雪/车辆故障）自适应应急重排中枢        |
|  - amap_client.py: 高德开放平台地理编码、逆地理编码、周边搜与气象实况网关         |
+-----------------------------------------------------------------------------------+
```

---

## 6. 项目目录结构规范

```
.
├── .gitignore                      # Git 过滤规范（过滤私密文档与凭证）
├── README.md                       # 系统正式说明文档
├── requirements.txt                # Python 依赖清单
├── run_server.py                   # 根目录快速启动入口脚本
├── data/                           # 基础数据底座
│   ├── 五社区无人配送模型数据汇总.xlsx # 5社区WGS84边界、楼栋、设施与拓扑路网
│   ├── 01_社区空间数据包.xlsx       # 北京市社区单元与老旧小区分类数据
│   ├── 02_无人配送车与智能柜参数包.xlsx # 无人车技术参数、智能柜造价与电价碳排因子
│   └── 03_道路通行与政策规则包.xlsx # 北京市无人配送车道路测试与准入规则
├── docs/                           # 文档与图像资源
│   └── images/
│       ├── comparison_telemetry.png# 现状与优化全景对比看板截图
│       └── platform_overview.png   # 平台数字孪生与算法控制台截图
└── demo/                           # 系统源码与资产
    ├── server.py                   # FastAPI 后端服务主程序
    ├── core/                       # 核心算法引擎包
    │   ├── __init__.py
    │   ├── data_manager.py         # 数据管理器
    │   ├── forecast_model.py       # 需求预测模型 (M5)
    │   ├── layout_optimizer.py     # 选址定容优化器 (M6)
    │   ├── routing_engine.py       # 协同路径规划引擎 (M1, M2)
    │   ├── simulation_engine.py    # 离散事件仿真引擎 (M8)
    │   ├── ai_copilot.py           # 智能调度与应急决策中枢
    │   └── amap_client.py          # 高德 Web 服务与 MCP 客户端
    └── static/                     # 前端单页应用
        ├── index.html              # 数字孪生大屏前端页面
        ├── app.js                  # Vue 3 核心状态与图表交互脚本
        ├── style.css               # 自定义科技主题与地图容器样式
        └── libs/                   # 本地化第三方前端核心库 (Leaflet, Vue, ECharts)
```

---

## 7. 环境准备与启动指南

### 7.1 环境依赖
- 推荐操作系统：Windows 10 / 11, Linux, macOS
- Python 版本：Python 3.10 及以上版本

### 7.2 安装步骤
克隆本仓库到本地环境：

```bash
git clone https://github.com/zhutmg00-eng/Logistics-Design-Competition.git
cd Logistics-Design-Competition
```

安装 Python 运行依赖：

```bash
pip install -r requirements.txt
```

### 7.3 启动系统
在项目根目录下执行启动脚本：

```bash
python run_server.py
```

终端将输出服务就绪提示：

```text
============================================================
超大城市末端配送协同网络数智化与绿色化决策平台
第九届北京市大学生物流设计大赛 · 主题二 原型系统
服务地址: http://127.0.0.1:8000
============================================================
```

在本地浏览器中访问 `http://127.0.0.1:8000` 即可使用系统全套功能。

---

## 8. 高德开放平台 Web 服务 Key 配置说明

系统默认基于亦庄示范区 5 大标杆社区的预置高精实证数据集运行。若需启用全北京任意真实小区的在线地理编码与实时拓扑扫描功能，可通过如下方式配置高德开放平台 Web 服务 Key：

1. 登录高德开放平台（lbs.amap.com），申请应用并获取 **Web 服务** 类型 API Key；
2. 在浏览器中打开系统，点击顶栏右上角 **“高德Key: 未绑定”** 按钮；
3. 在弹出的配置窗口中填入 Key 并点击 **“测试并保存生效”**，系统将自动发起连通性核验并持久化配置；
4. 进入 **“自定义推演”** 模块，输入北京任意小区名称（如“海淀远大园”、“望京新城”），系统将秒级调用高德接口完成空间要素提取与方案规划。
