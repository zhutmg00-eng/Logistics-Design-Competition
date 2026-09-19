# 项目远程协同开发与 Agent 规范指南 (Team Collaboration Guide)

> 本指南专为本项目（超大城市末端配送协同网络数智化与绿色化决策平台）团队成员及成员使用的 AI Agent（如 Antigravity, Cursor, Claude Code, GitHub Copilot 等）设计。
> 
> **核心目标**：实现零学习成本的 AI 辅助协同开发、确保每位队员的 GitHub 贡献者头像正确显示（便于简历背书）、统一代码与提交规范、彻底杜绝隐私与竞赛材料泄露。

---

## 快速导航

- [一、 队员 30 秒极简上手指引（人类阅读）](#一-队员-30-秒极简上手指引人类阅读)
- [二、 专属 AI Agent 系统提示词（直接复制给 Agent 读）](#二-专属-ai-agent-系统提示词直接复制给-agent-读)
- [三、 贡献者头像与 GitHub 身份绑定指南](#三-贡献者头像与-github-身份绑定指南)
- [四、 提交规范与变更说明模板 (Commit Message)](#四-提交规范与变更说明模板-commit-message)
- [五、 安全红线：提交前隐私与文件核验清单](#五-安全红线提交前隐私与文件核验清单)

---

## 一、 队员 30 秒极简上手指引（人类阅读）

如果你不想花费大量时间学习复杂的 Git 命令，请按以下 3 步操作即可：

### 第 1 步：克隆仓库到本地
在终端中执行：
```bash
git clone https://github.com/zhutmg00-eng/Logistics-Design-Competition.git
cd Logistics-Design-Competition
```

### 第 2 步：绑定你自己的 GitHub 身份（关键：简历背书）
为了让 GitHub 的 **Contributors 贡献者列表** 显示你自己的 GitHub 头像与主页链接，必须将本地 Git 邮箱设置为你的 **GitHub 注册邮箱**：
```bash
# 替换为你的 GitHub 用户名和你的 GitHub 注册邮箱
git config user.name "你的GitHub用户名"
git config user.email "你的GitHub绑定邮箱@example.com"
```
*(注：如果不想公开真实邮箱，可在 GitHub 设置 -> Emails 中查看并使用形如 `ID+username@users.noreply.github.com` 的隐私邮箱)*

### 第 3 步：把本指南第二部分的【Agent 提示词】直接喂给你的 AI
在你的 AI 编程助手（Antigravity / Cursor / Copilot 等）开启对话时，**直接复制本指南第二部分的提示词发给它**。后续的所有拉取、建分支、写代码、排查隐私、提交与推送，均由 Agent 全自动规范执行！

---

## 二、 专属 AI Agent 系统提示词（直接复制给 Agent 读）

> **给队员的使用方法**：复制下方代码块内的全部文本，作为你的 AI Agent 的 **System Prompt / 初始指令** 发送给它。

```markdown
你现在是本项目（Logistics-Design-Competition）的专职研发协作 Agent。在本项目中进行任何开发、代码修改或 Git 提交操作时，你必须严格遵守以下协作协议：

1. 【身份确认红线】：
   - 在执行任何 git commit 之前，必须先运行 `git config user.name` 和 `git config user.email`；
   - 确认当前配置的是使用者的个人 GitHub 身份，严禁使用默认/匿名身份提交，以确保贡献者头像在 GitHub 正常展示。

2. 【隐私与安全红线（最高优先级）】：
   - 在执行 `git add` 之前，必须先运行 `git status` 严格审查待提交文件；
   - 严禁提交任何 `.docx`, `~$*.docx`, `.zip`, `parsed_*.txt` 文件（这是私密竞赛材料与分工记录）；
   - 严禁提交包含个人高德 Key / 密钥的 `config.json` 或 `.env` 文件；
   - 严禁提交开发过程中的临时截图（`demo/*.png`），截图需规范存放于 `docs/images/`；
   - 发现上述文件时，立即将其加入 `.gitignore` 或执行清理，严禁推送到远程仓库。

3. 【分支与协作开发流程】：
   - 任何新功能或算法修改，必须先拉取最新主干：`git checkout main && git pull origin main`；
   - 创建独立的特性分支进行开发：`git checkout -b feat/your-feature-name` 或 `fix/your-fix-name`；
   - 修改完成后，必须在本地运行语法检查（如 `python -m py_compile <file>` 或 `node -c <file>`），确保 0 报错。

4. 【提交信息规范（Conventional Commits）】：
   - 严禁使用 "update", "fix bug", "test" 等不明所以的单行提交；
   - 每次 commit 必须包含类型前缀、简明标题以及详细的修改原因与影响范围；
   - 提交格式示例：
     ```
     feat(layout): 引入基于拉格朗日松弛的副柜定容算法
     
     - 优化 layout_optimizer.py 中的副柜决策逻辑，增加峰值负荷松弛度
     - 修复高密社区大促场景下边缘楼栋指派超时的异常
     - 前端布局模块同步增加有效容量利用率展示
     ```

5. 【推送与合并】：
   - 推送分支至远程仓库：`git push -u origin 分支名`；
   - 推送后向使用者汇报清晰的 Pull Request 创建指引及本次代码变动的总结。
```

---

## 三、 贡献者头像与 GitHub 身份绑定指南

为了确保每位队员在项目的 GitHub 首页以及个人个人主页的 Contribution Graph（绿墙）中留下记录，GitHub 的判定机制为：
> **Git Commit 中的作者邮箱 == GitHub 账号绑定的 Verified 邮箱**

### 3.1 验证本地配置是否生效
在本地项目根目录下运行：
```bash
git config user.name
git config user.email
```
* 如果输出的正是你登录 GitHub 的邮箱，则配置成功；
* 如果邮箱错误，可使用以下命令更正：
  ```bash
  git config user.email "正确的GitHub邮箱"
  git config user.name "你的GitHub用户名"
  ```

### 3.2 不想暴露私人邮箱的解决方案
1. 打开 GitHub 网站，进入 **Settings** -> **Emails**；
2. 勾选 **Keep my email addresses private**；
3. 复制页面中显示的专属邮箱（例如：`12345678+username@users.noreply.github.com`）；
4. 在本地终端中设置该邮箱即可：
   ```bash
   git config user.email "12345678+username@users.noreply.github.com"
   ```
   使用该邮箱提交，GitHub 依然能准确识别你的头像和账号，同时完全隐藏真实邮箱。

---

## 四、 提交规范与变更说明模板 (Commit Message)

本项目采用业内通用的 **Conventional Commits** 规范。严禁产生模糊不清的提交。

### 4.1 提交类型 (Type)
- `feat`: 新增功能/新算法模块（如新增需求预测算法、新界面卡片）
- `fix`: 修复缺陷（如修复地图加载失败、修复距离计算除以零异常）
- `docs`: 仅文档变动（如更新 README、增加技术方案说明）
- `style`: 代码格式调整（不影响逻辑的空格、分号、格式化等）
- `refactor`: 代码重构（既不新增功能也不修复 bug 的代码重整）
- `perf`: 性能优化（提升算法求解速度、减少页面首屏渲染时间）
- `test`: 增加或修改测试用例

### 4.2 标准提交模板
```text
<type>(<scope>): <简明扼要的一句话总结（50字以内）>

<详细修改说明（空一行后填写）：>
- 为什么进行此次修改（背景或解决的问题）
- 修改了哪些核心文件或算法逻辑
- 对其他模块是否产生破坏性变动或依赖调整
```

#### 正面范例：
```text
feat(routing): 改进M2社区内CVRP启发式算法并增加动态装载校验

- 重构 routing_engine.py 中的 solve_community_m2 方法，引入最近插入法替代简单贪心
- 增加了每车次 400 件体积与重量双重容量约束的硬性校验
- 优化后社区内无人车巡航里程平均缩短 8.2%
```

#### 反面范例（严禁出现）：
- `git commit -m "update"`（未说明修改内容）
- `git commit -m "改了几个bug"`（无法追溯具体改动点）
- `git commit -m "temp"`（零参考价值）

---

## 五、 安全红线：提交前隐私与文件核验清单

在任何提交推送前，**无论是人工操作还是 Agent 操作，都必须核对以下清单**：

| 检查项 | 核验动作 | 违规后果 |
| :--- | :--- | :--- |
| **高德/第三方 API 密钥** | 确保没有任何私人 Key 硬编码在 `amap_client.py` 或任何前端 JS 代码中。Key 应仅保存在本地未提交的 `config.json` 或环境变量中。 | 导致个人配额被刷爆、违反接口安全条例 |
| **竞赛项目书与内部文件** | 检查 `git status`，确保不含 `*.docx`、`分工*.txt`、`全网数据搜集*` 目录。 | 泄露团队原创材料与选题思路 |
| **临时大文件与调试截屏** | 确保未将本地调试时产生的无规则临时图片提交进代码库。正规演示图应压缩后命名存放在 `docs/images/`。 | 导致仓库体积膨胀至数十兆甚至数百兆 |
| **本地运行验证** | 提交前在本地运行 `python run_server.py`，确认至少能在本地 `8000` 端口成功启动无崩溃。 | 破坏主干分支，导致其他协作者拉取后无法运行 |

---

## 六、 常用协同场景处理速查

### 6.1 拉取最新代码与合并
在开始一天的工作前，先同步远程更新：
```bash
git checkout main
git pull origin main
```

### 6.2 遇到代码冲突 (Merge Conflict)
如果与队友修改了同一行代码导致冲突：
1. 打开提示冲突的文件，搜索 `<<<<<<< HEAD`；
2. 结合队友的代码保留正确的部分，删除冲突标记符号；
3. 运行本地语法检测确认无误后执行：
   ```bash
   git add <解决冲突的文件>
   git commit -m "merge: resolve conflicts with main"
   git push origin <你的分支>
   ```

---

> 本文档由项目组统一制定并持续维护。如有规则疑问或流程建议，请联系项目负责人协商更新。
