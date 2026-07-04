# SKILL 优化计划 — 提示词工程角度

> 创建于：2026-07-04 | 状态：✅ 第一批完成（12/12）| 第二批待执行（2/2）| 第三批待执行（1/1）

---

## 一、问题清单（12 个）

### 用户提出的问题

| # | 问题 | 证据 |
|---|------|------|
| 1 | **点数消耗多** | 每次任务 Pre-flight 要读 SKILL.md(250行) + CHEATSHEET(155行) + BLUEPRINT + PROJECT_PLAN + MEMORY + 日志 ≈ 2000+ 行上下文。任务还没开始，token 已大量消耗 |
| 2 | **对话一长就忘记流程** | Rubedo 调试：前几轮还输出 Phase 0 分类，到第 5 轮后完全跳过流程，直接猜猜猜改代码。SKILL.md 有「中断恢复」段落但只有一句话，实际未生效 |
| 3 | **一个问题打转，切模型才出来** | Rubedo DayPilot：7 轮修复（fix1~fix7），6 个根因层层叠加。SKILL.md 写了「重试 ≤ 3 换方案」，但没有强制触发机制——AI 自己不会数到 3 就停。Citrinitas run.bat 也是 VFY-001~009 连续 9 个 bug |
| 8 | **执行遇阻不解决而是跳过，改方案不经同意** | SKILL.md 写了「遇阻不跳过，创建新任务描述阻塞原因」，但只在全局 MEMORY.md 里，不在 Phase 2 执行纪律里。实际执行时 AI 把「防偏跳过」当默认行为——卡住了就绕，绕了就改方案，改了不告诉你 |
| 9 | **前端代码效果一直不理想** | Rubedo DayPilot 7 轮修复全在前端 JS/CSS。Citrinitas NiceGUI 也反复出 UI bug（VFY-006/007/009）。AI 对前端渲染机制（DOM/CSS/时区/事件循环）的理解系统性弱于后端 Python |

### AI 回顾记录发现的问题

| # | 问题 | 证据 |
|---|------|------|
| 4 | **调试没有「证据链」规则** | Rubedo 调试中，AI 先说 `args.cell.properties.backColor` 不生效（colored=0 证明），后来又说自己「扫描方式错了」其实它生效了，最后发现根因根本不在前端而在后端 Python 的日期比较逻辑。每次都信誓旦旦，每次都错。SKILL.md Phase 0.5 只说「先 Read/Grep 理解」，但没有要求**调试时必须先证明根因再动手修** |
| 5 | **没有「调试假设追踪表」** | Rubedo fix1~fix7，每个 fix 基于不同假设，但 AI 没有记录「试了什么、结果是什么、排除了什么」。导致同样的错误假设可能被重复尝试。Citrinitas run.bat 也是 VFY-003 修了两次才真正解决。MEMORY.md 写了「打地鼠式修复无效时停止做 5 Whys」，但这条经验**只在 memory 里，不在 SKILL.md 流程里** |
| 6 | **第三方库依赖不验证就用** | `dayjs().startOf("isoWeek")` 没加载插件就用了，dayjs 对不认识的单位静默返回当前时刻不报错。AI 假设「dayjs 内置 isoWeek」，没有验证。SKILL.md Phase 1 说「研究执行方式」，但没有一条规则说「用了第三方库的 API → 必须验证该 API 在当前版本/配置下可用」 |
| 7 | **长对话没有「重启检查点」机制** | Rubedo 调试到最后几轮，对话上下文已极长，AI 开始重复之前的错误判断（颜色来源分析来回反复了 3 次）。最终切模型解决了——新模型上下文短，反而更清醒。流程里没有「对话超过 N 轮 → 强制总结进展+假设+已排除项 → 开新对话继续」的机制 |
| 10 | **没有「调试模式」——正常 Phase 链对修 bug 太重** | 修一个 bug 要走 Phase 0→0.1→0.5→1→1.5→2，每步都有 Gate 等确认。QuickFix 只覆盖 ≤1 文件 ≤5 行，真实 bug 几乎不可能符合。结果：要么走完整链太慢太费 token，要么 AI 偷偷跳过流程 |
| 11 | **BLUEPRINT/FLOWCHART 本身过时** | 蓝图「当前重心」还写着 Athanor/Alembic/Crucible 旧名（6/23），FLOWCHART 版本 v1（6/17）。管理流程自己没按自己的流程更新 |
| 12 | **TECH_DEBT.md 从未实际使用** | SKILL 写了「跳过的任务记入 TECH_DEBT.md」，但 4 个项目没有一个有这个文件。防偏机制名存实亡 |

---

## 二、改进计划（4 个改进包）

### 改进包 A：调试协议（问题 3/4/5/8/10）— 第一批紧急

#### A1. 新增「调试模式」— 解决问题 10

当前 QuickFix 门槛太高（≤1 文件 ≤5 行），真实 bug 走不进去。新增第三条路径：

| 路径 | 触发条件 | 流程 |
|------|---------|------|
| QuickFix | ≤1 文件 ≤5 行 无逻辑变更 | Phase 0 → 直接改 → 验证 |
| **调试模式（新增）** | 🐛 Bug + 用户说"修"/"坏了" | Phase 0 → 证据链 → 定位 → 修复 → 验证 |
| 完整链 | ✨ 功能 / 🔄 重构 | Phase 0 → 0.1 → 0.5 → 1 → 1.5 → 2 → ... |

调试模式跳过蓝图对齐和任务拆解（bug 不需要对齐蓝图），但**强制走证据链**。

#### A2. 证据链规则 — 解决问题 4

调试模式下，改代码前必须输出：

```
## 证据链
现象：[用户报告的症状]
假设：[我认为根因是 X]
验证方法：[我怎么证明假设对不对]
验证结果：[证据支持/推翻了假设]
结论：[根因确认 = X / 假设排除，换下一个]
```

没有证据链就动手 → 流程违规。

#### A3. 假设追踪表 + 强制刹车 — 解决问题 3/5

同一 bug 修复第 2 次尝试时，必须输出假设表：

```
## 假设追踪
| # | 假设 | 验证结果 | 状态 |
|---|------|---------|------|
| 1 | dp.visibleStart() 返回旧周 | 改了没效果 | ❌ 排除 |
| 2 | toDate() 时区跨天 | 改了部分好 | ⚠️ 部分正确 |
| 3 | ... | ... | ... |
```

**强制刹车**：同一 bug 假设表填到第 3 行还没解决 → **必须停下来**，向用户报告：「已尝试 3 个假设均未解决，建议：① 切换模型 ② 重新从头研究 ③ 换技术方案。你选哪个？」

#### A4. 阻塞升级规则 — 解决问题 8

Phase 2 执行中遇到任何阻塞，禁止自行跳过或改方案。必须：

```
## ⛔ 遇到阻塞
阻塞点：[具体描述]
影响：[对当前任务的影响]
选项：① 继续尝试 ② 跳过（需你同意）③ 换方案（需你同意）
```

用户不选 → AI 不能自作主张。

---

### 改进包 B：瘦身+激活（问题 1/6/11/12）— 第一批紧急

#### B1. Pre-flight 分级加载 — 解决问题 1

当前每次都全读（SKILL 250行 + CHEATSHEET 155行 + BLUEPRINT + PROJECT_PLAN + MEMORY）。改为：

| 任务类型 | 必读 | 按需读 |
|---------|------|--------|
| 🐛 Bug 修复 | PROJECT_PLAN 当前状态(5行) + 今天日志 | BLUEPRINT 仅在偏离时读 |
| ✨ 功能开发 | PROJECT_PLAN 当前状态 + BLUEPRINT 当前重心 | CHEATSHEET 仅在不确定时 grep |
| 🔬 调研 | PROJECT_PLAN 当前状态 | — |
| 💬 问答 | 无 | — |

SKILL.md 本身不每次全读——改为 AI 内化后按场景 grep CHEATSHEET。

#### B2. 第三方库 API 验证规则 — 解决问题 6

用了第三方库的 API（非 Python 标准库）→ 必须先验证：
- 该 API 在当前版本存在
- 该 API 的参数/返回值符合预期
- 该 API 不依赖额外插件/配置

验证方式：查官方文档 或 写一行测试代码跑。

#### B3. 蓝图自更新 — 解决问题 11

SKILL.md 加一条：每次改 SKILL.md 时，同步检查 BLUEPRINT.md 和 FLOWCHART.md 是否过时。

#### B4. 技术债激活 — 解决问题 12

把 TECH_DEBT.md 改为更轻量的机制：直接在 PROJECT_PLAN.md 的「已知问题」段落里记录，不再要求独立文件。每次 Phase 4 文档更新时检查是否有技术债需要记录。

---

### 改进包 C：防遗忘（问题 2/7）— 第二批重要

#### C1. 调试注入器 — 解决问题 2

调试模式下，每隔 5 轮对话自动注入一条提醒：「⚠️ 检查：当前是否在按流程走？证据链是否更新？假设表是否填了？」

#### C2. 长对话检查点 — 解决问题 7

对话超过 15 轮时，输出进度摘要：
```
## 📋 长对话检查点（第 N 轮）
当前任务：[一句话]
已完成：[列表]
当前假设：[最新假设]
已排除：[列表]
下一步：[一句话]
```

如果上下文已混乱 → 建议：「对话较长，建议开新对话，以上摘要作为起点。」

---

### 改进包 D：前端保障（问题 9）— 第三批长期

#### D1. 前端任务加验证规则

前端改动（JS/CSS/HTML）额外要求：
- 改完必须说明预期效果 vs 实际效果
- 涉及第三方 UI 库 → 必须查文档确认 API（比后端更严格）
- 涉及时区/日期 → 必须写测试验证

#### D2. 前端能力补强（长期）

根因是 AI 对前端渲染机制理解弱。长期方案：
- 积累前端踩坑记录到 MEMORY.md（DayPilot UTC 陷阱等）
- 前端任务优先用"最小改动"原则——不重构，只改必要的那几行
- 复杂前端任务考虑拆分：AI 写逻辑 + 人工调样式

---

## 三、提示词工程研究 — SKILL.md 优化方向

### 研究来源

1. [Agentic Prompt Engineering: LLM Roles Guide](https://digitalthoughtdisruption.com/2025/08/12/agentic-prompt-engineering-llm-roles-guide/)
2. [awesome-ai-system-prompts](https://github.com/dontriskit/awesome-ai-system-prompts) — 分析了 v0、ChatGPT、Cline、same.new、Manus、Bolt.new 等真实系统提示词
3. [Lost in the Middle: 注意力衰减及缓解策略](https://qubittool.com/zh/blog/long-context-lost-in-the-middle)

### 核心发现

#### 发现 1：「迷失在中间」— 关键指令位置决定遵循率

LLM 对长文本的注意力呈 **U 型曲线**：开头和结尾的指令遵循率极高（95%+），中间部分断崖式下跌（< 50%）。

**对 SKILL.md 的诊断**：
- Pre-flight 在开头（✅ 好）
- Phase 2 执行纪律（最常被遗忘的）在文档**正中间**（❌ 最差位置）
- QuickFix 短路径在结尾附近（✅ 尚可）
- 没有在结尾重申关键规则

**优化方向**：
- 在 SKILL.md **开头**放「绝对规则」摘要（3-5 条 CRITICAL 规则）
- 在 SKILL.md **结尾**放「执行检查清单」（每条消息回复前必须过一遍）
- Phase 2 执行纪律从中间移到开头摘要里

#### 发现 2：强制性语言分级 — ALWAYS/NEVER/CRITICAL

真实系统提示词大量使用大写强调词标识规则刚性等级：
- `ALWAYS` / `NEVER` → 绝对规则
- `MUST` / `MUST NOT` → 强制性要求
- `STRICTLY FORBIDDEN` → 零容忍禁止
- `CRITICAL` / `IMPORTANT` → 高优先级提醒

**对 SKILL.md 的诊断**：
- 当前用「必须」「不可跳过」——力度不够，且不统一
- 没有 CRITICAL / MUST / NEVER 等通用强调词
- 所有规则看起来同等重要，AI 不知道哪些是绝对不可违反的

**优化方向**：
- 关键规则用 `CRITICAL:` / `MUST:` / `NEVER:` 前缀
- 非关键规则不加前缀
- 形成视觉层次：AI 一眼看出哪些是红线

#### 发现 3：XML 标签封装规则集 — 语义隔离

same.new、Manus、Bolt.new 用自定义 XML 标签将规则集封装成独立模块：
```
<tool_calling>
  1. ALWAYS follow the tool call schema exactly...
  3. NEVER refer to tool names when speaking to the USER...
</tool_calling>
```

**对 SKILL.md 的诊断**：
- 当前用 Markdown 标题（`##`）分节——有帮助但不够强
- 调试规则散落在 Phase 0.5 / Phase 2 / QuickFix 多个段落，没有集中封装
- AI 需要跨段落拼凑完整规则

**优化方向**：
- 用 `<debug_protocol>...</debug_protocol>` 封装调试协议
- 用 `<execution_rules>...</execution_rules>` 封装执行纪律
- 用 `<pre_flight>...</pre_flight>` 封装启动检查
- 每个标签内是自包含的完整规则集，不需要跨段落引用

#### 发现 4：Agent Loop — 每步重新评估

Manus 的显式代理循环：
```
<agent_loop>
1. Analyze Events → 2. Select Tools → 3. Wait for Execution
→ 4. Iterate (每次只选择一个工具调用) → 5. Submit Results
→ 6. Enter Standby
</agent_loop>
```

每次迭代只调用一个工具，强制在每步后重新评估状态。

**对 SKILL.md 的诊断**：
- 当前 Phase 2 执行是线性的（改→自查→下一步），没有"重新评估"环节
- 调试时 AI 改了一处就冲向验证，不会停下来想"这个改动是否改变了我的假设"

**优化方向**：
- 调试模式引入 mini-loop：假设 → 验证 → 重新评估 → 下一步
- 每步改完后必须回答："这个结果是否改变了我的根因假设？"

#### 发现 5：Thinking Phase — 行动前重新加载上下文

v0 和 Bolt.new 都有强制思考阶段：
```
BEFORE creating a Code Project, v0 uses <Thinking> tags to
think through the project structure...
```
```
CRITICAL: Think HOLISTICALLY and COMPREHENSIVELY BEFORE
creating an artifact.
```

**对 SKILL.md 的诊断**：
- 当前没有"行动前思考"机制
- Phase 0 分类后直接冲向 Phase 0.5 代码探索，没有停下来想"我应该用什么策略"

**优化方向**：
- 调试模式下，第一次 Read 代码前必须输出 `<thinking>` 块：从症状倒推可能根因，列出 2-3 个假设
- 长对话检查点时也用 `<thinking>` 重新加载上下文

#### 发现 6：错误修复上限 — same.new 的"最多 3 次"

same.new 明确规定了修复运行时错误的上限（最多 3 次尝试），防止无限修复循环。

**对 SKILL.md 的诊断**：
- 当前写了「重试 ≤ 3」，但没有强制触发机制
- AI 自己不会数到 3 就停——需要外部计数器或显式假设表

**优化方向**：
- 假设追踪表本身就是计数器——第 3 行自动触发刹车
- 用 `CRITICAL:` 标识："假设表填到第 3 行 → MUST 停下来询问用户"

#### 发现 7：模块化文件拆分 — SOUL/AGENTS/IDENTITY 模式

Clawdbot 的三文件架构：
- `SOUL.md` → 个性/语气
- `AGENTS.md` → 操作规则与审批层级
- `IDENTITY.md` → 隐私边界与上下文感知的披露规则

**对 SKILL.md 的诊断**：
- 当前 SKILL.md + CHEATSHEET 两文件——功能上对应 AGENTS.md
- 缺少 SOUL.md（AI 沟通风格规则散落在各处）
- 缺少 IDENTITY.md（项目身份/边界规则在 BLUEPRINT.md 里但混杂了其他内容）

**优化方向**（长期）：
- 保持当前两文件结构（对一人公司够用）
- 但在 SKILL.md 内部用标签实现"逻辑模块化"

### SKILL.md 优化总结 — 7 条具体建议

| # | 优化点 | 提示词工程依据 | 优先级 |
|---|--------|-------------|--------|
| S1 | **开头加「绝对规则」摘要**（3-5 条 CRITICAL，含 Phase 2 执行纪律核心） | U 型曲线：开头注意力最高 | 🔴 紧急 |
| S2 | **结尾加「执行检查清单」**（每条消息回复前过一遍） | U 型曲线：结尾注意力最高 | 🔴 紧急 |
| S3 | **用 CRITICAL/MUST/NEVER 前缀分级规则** | 强制性语言分级 | 🟡 重要 |
| S4 | **用 XML 标签封装调试协议**（`<debug_protocol>`） | 语义隔离 | 🟡 重要 |
| S5 | **调试模式引入 Thinking Phase**（行动前输出假设） | 行动前重新加载上下文 | 🟡 重要 |
| S6 | **假设追踪表作为强制计数器**（第 3 行触发刹车） | 错误修复上限 | 🔴 紧急 |
| S7 | **长对话检查点重申关键规则** | 上下文衰减对抗 | 🟢 长期 |

---

## 四、执行计划

| # | 任务 | 改哪个文件 | 批次 | 对应优化 |
|---|------|----------|------|---------|
| 1 | ✅ SKILL.md 新增「调试模式」段落（A1） | SKILL.md | 第一批 | S4 |
| 2 | ✅ SKILL.md 新增「证据链」规则（A2） | SKILL.md | 第一批 | S4, S5 |
| 3 | ✅ SKILL.md 新增「假设追踪表+强制刹车」（A3） | SKILL.md | 第一批 | S6 |
| 4 | ✅ SKILL.md Phase 2 新增「阻塞升级」规则（A4） | SKILL.md | 第一批 | — |
| 5 | ✅ SKILL.md Pre-flight 改为分级加载（B1） | SKILL.md | 第一批 | — |
| 6 | ✅ SKILL.md Phase 1 新增「第三方库验证」（B2） | SKILL.md | 第一批 | — |
| 7 | ✅ BLUEPRINT.md 更新旧名+当前重心（B3） | BLUEPRINT.md | 第一批 | — |
| 8 | ✅ SKILL.md 技术债改为 PROJECT_PLAN 内联（B4） | SKILL.md | 第一批 | — |
| 9 | ✅ SKILL.md 开头加「绝对规则」摘要（S1） | SKILL.md | 第一批 | S1 |
| 10 | ✅ SKILL.md 结尾加「执行检查清单」（S2） | SKILL.md | 第一批 | S2 |
| 11 | ✅ SKILL.md 用 CRITICAL/MUST/NEVER 分级（S3） | SKILL.md | 第一批 | S3 |
| 12 | ✅ FLOWCHART.md 同步更新流程图 | FLOWCHART.md | 第一批 | — |
| 13 | ✅ SKILL.md 新增「调试注入器」（C1） | SKILL.md | 第二批 | S7 |
| 14 | ✅ SKILL.md 新增「长对话检查点」（C2） | SKILL.md | 第二批 | S7 |
| 15 | ✅ SKILL.md 新增「前端任务验证规则」（D1） | SKILL.md | 第三批 | — |

---

## 五、一句话总结

12 个问题，10 个能改 SKILL 解决，2 个是 AI 能力天花板（靠规则缓解）。
提示词工程的核心发现：**指令位置 > 指令内容**——把关键规则放在 SKILL.md 首尾，用 CRITICAL/MUST/NEVER 分级，用 XML 标签封装调试协议，用假设追踪表做强制计数器。
分三批：第一批止血+降本（12 个任务），第二批防退化（2 个），第三批补前端短板（1 个）。
