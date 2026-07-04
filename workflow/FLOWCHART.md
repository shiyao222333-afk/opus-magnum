# Workflow · 项目管理流程 — 流程框图

> 展示 Phase Pre-flight → Phase 5 全链路数据流。
> 对应 SKILL.md v5.0。

---

## 主干流程图

```mermaid
flowchart TB
    User([用户指令]) --> PreFlight[Pre-flight<br/>分级加载项目上下文]

    PreFlight --> P0{Phase 0<br/>意图分类}
    P0 -->|"💬非编程"| Chat([直接回答])
    P0 -->|"📋蓝图录入"| BlueprintEntry([蓝图对话模式<br/>分析→确认→写入])
    P0 -->|"🛑规划/🔬调研"| P0_1_Plan[Phase 0.1 蓝图对齐<br/>↓<br/>Phase 1 输出方案<br/>🛑暂停等待]
    P0 -->|"🐛Bug ≤1文件 ≤5行"| QuickFix[QuickFix<br/>直接改→验证]
    P0 -->|"🐛Bug 不符合QuickFix"| DebugMode[调试模式<br/>debug_protocol]
    P0 -->|"✨功能/🔄重构"| P0_1[Phase 0.1 蓝图对齐]

    DebugMode --> DP_Think[Thinking Phase<br/>列出2-3个假设]
    DP_Think --> DP_Evidence[证据链<br/>假设→验证→结论]
    DP_Evidence --> DP_Hypo{假设表<br/>第3行?}
    DP_Hypo -->|"是"| DP_Stop[⛔ 停下来<br/>询问用户]
    DP_Hypo -->|"否"| DP_Fix[修复代码]
    DP_Fix --> P3

    QuickFix --> P2_QF[执行+自审]
    P2_QF --> P3

    P0_1 --> BPCheck{BLUEPRINT<br/>存在?}
    BPCheck -->|No| Guide[蓝图引导创建]
    BPCheck -->|Yes| Align{与当前重心<br/>对齐?}
    Guide --> Align_New[蓝图创建后继续]
    Align -->|对齐| P0_5[Phase 0.5 代码探索]
    Align -->|"⚠️偏离"| WarnDiverge[提醒偏离<br/>等待确认]
    WarnDiverge -->|继续| P0_5
    WarnDiverge -->|回主线| User
    Align_New --> P0_5

    P0_5 --> P1[Phase 1 计划拆解<br/>标注MVP+📍节点映射<br/>第三方库API验证]

    P1 --> P1_Decision{需要改代码?}
    P1_Decision -->|No| PausePlanning([输出方案<br/>🛑暂停等待])
    P1_Decision -->|Yes| P1_5[Phase 1.5 方案讨论<br/>MVP审查+节点契约检查]

    P1_5 --> P1_5_Confirm{用户确认?}
    P1_5_Confirm -->|修改| P1
    P1_5_Confirm -->|确认| P2[Phase 2 执行<br/>遇阻升级规则]

    P2 --> P2_Block{遇阻?}
    P2_Block -->|是| BlockReport[⛔ 报告阻塞<br/>等用户选择]
    BlockReport -->|用户选择| P2
    P2_Block -->|否| P2_Continue[继续执行]

    P2_Continue --> P2_5[Phase 2.5 自审<br/>语义/遗漏/调试/安全]

    P2_5 --> P2_5_Pass{自审通过?}
    P2_5_Pass -->|No| P2
    P2_5_Pass -->|Yes| P3[Phase 3 验证<br/>L1→L2→L3→L4]

    P3 --> P3_L4{L4用户验收?}
    P3_L4 -->|"✅通过"| QC[提交前质量检查<br/>全部通过才commit]
    P3_L4 -->|"❌未修好"| P0_5
    P3_L4 -->|"❌新问题"| Revert[回滚 git revert]
    P3_L4 -->|"⚠️需调整"| P2
    Revert --> P0_5

    QC --> QC_Pass{全部通过?}
    QC_Pass -->|No| P2
    QC_Pass -->|Yes| Git[git add -A<br/>git commit<br/>git push]

    Git --> P4[Phase 4 文档更新<br/>CHANGELOG/PROJECT_PLAN/BLUEPRINT<br/>技术债记入PROJECT_PLAN]

    P4 --> P4_BP[蓝图反哺<br/>重心缓解?新认知?新边界?]

    P4_BP --> P4_BP_Update{需更新<br/>蓝图/流程图?}
    P4_BP_Update -->|Yes| UpdateBP[更新 BLUEPRINT.md<br/>和/或 FLOWCHART.md]
    P4_BP_Update -->|No| P5

    UpdateBP --> P5[Phase 5 记忆归档<br/>MEMORY.md + Skill]

    P5 --> Done([✅ 完成])

    PausePlanning -->|用户说开始| P1_5
    DP_Stop -->|用户选择| DebugMode

    %% 样式
    style Chat fill:#e0e0e0,stroke:#999
    style BlueprintEntry fill:#e0e0e0,stroke:#999
    style PausePlanning fill:#fff3cd,stroke:#f0ad4e
    style WarnDiverge fill:#ffeaa7,stroke:#f0ad4e
    style Git fill:#d4edda,stroke:#28a745
    style Done fill:#d4edda,stroke:#28a745
    style QC fill:#cce5ff,stroke:#0275d8
    style DebugMode fill:#fde2e4,stroke:#e63946
    style DP_Stop fill:#fde2e4,stroke:#e63946
    style QuickFix fill:#d4edda,stroke:#28a745
    style BlockReport fill:#fff3cd,stroke:#f0ad4e
```

每个编程任务经历这个闭环，保证可追溯、可回溯。
**纯规划、闲聊、蓝图录入则分流到短路径，不走完整体流程。**

---

## 节点定义

### 意图分类与路径选择（Phase 0）

| 节点 | 名称 | 输入 | 输出 | 逻辑 |
|:--:|------|------|------|------|
| P0 | 意图分类 | 用户指令 | 路由到合适分支 | 语义分析：含"修/bug/fix"→🐛，含"新/添加/add"→✨，含"重构/改架构"→🔄，含"录入蓝图"→📋，含"研究/调研"→🔬，纯问题→💬 |
| QuickFix | 快速修复 | ≤1文件≤5行无逻辑变更的 bug | 代码改动 | Phase 0 → 直接改 → 自审 → 验证 |
| DebugMode | 调试模式 | 不符合 QuickFix 的 bug | 代码改动 | Thinking Phase → 证据链 → 假设追踪表 → 修复 |
| DP_Think | 调试思考 | 用户报告的症状 | 2-3个假设 | 行动前思考，列出可能根因 |
| DP_Evidence | 证据链 | 假设 | 根因确认/排除 | 假设→验证方法→验证结果→结论 |
| DP_Hypo | 假设检查 | 假设追踪表行数 | 继续/停下 | 第3行→MUST停下询问用户 |

### 蓝图对齐（Phase 0.1）

| 节点 | 名称 | 输入 | 输出 | 逻辑 |
|:--:|------|------|------|------|
| P0_1 | 蓝图对齐 | BLUEPRINT.md + FLOWCHART.md | 对齐判断 | 读蓝图→判断任务与当前重心关系→输出对齐/偏离/不存在 |
| Guide | 蓝图引导创建 | 空 | BLUEPRINT.md + FLOWCHART.md | 逐节引导用户填写愿景/原则/重心/边界/验收 |
| P0_5 | 代码探索 | 项目目录 | 代码理解 | 搜索/阅读现有代码，理解架构 |

### 计划与讨论（Phase 1 → 1.5）

| 节点 | 名称 | 输入 | 输出 | 逻辑 |
|:--:|------|------|------|------|
| P1 | 计划拆解 | 用户需求 + 代码理解 | 任务清单 + 流程映射 | 拆 SMART 任务→标注 MVP必须/锦上添花→第三方库API验证→每个任务 📍映射到 FLOWCHART 节点 |
| P1_5 | 方案讨论 | 任务清单 | 用户确认的方案 | 逐任务讨论怎么实现→MVP 审查→节点契约检查→用户确认 |
| PausePlanning | 暂停等待 | — | — | 纯规划/调研到此暂停，等用户说"开始" |

### 执行与验证（Phase 2 → 3）

| 节点 | 名称 | 输入 | 输出 | 逻辑 |
|:--:|------|------|------|------|
| P2 | 执行 | 确认的方案 | 代码改动 | 按 Task ID 顺序执行，改前先读，重试≤3 |
| P2_Block | 遇阻检查 | 任务状态 | 继续/报告 | 遇阻→MUST报告阻塞，NEVER自行跳过或改方案 |
| BlockReport | 阻塞报告 | 阻塞描述 | 用户选择 | ①继续 ②跳过(需同意) ③换方案(需同意) |
| P2_5 | 自审 | 代码改动 | 自审通过/不通过 | 语义正确性/遗漏路径/调试残留/安全问题 |
| P3 | 验证 | 代码改动 | 验证通过/不通过 | L1语法→L2单元+回归→L3服务→L4用户验收 |
| QC | 质量检查 | 验证通过的代码 | commit/rework | L1+L4+自审+无调试残留+文档已更新 → 全部通过才 commit |

### 文档与归档（Phase 4 → 5）

| 节点 | 名称 | 输入 | 输出 | 逻辑 |
|:--:|------|------|------|------|
| P4 | 文档更新 | commit 后的变更 | 更新的文档 | 更新 CHANGELOG/PROJECT_PLAN/BLUEPRINT；技术债记入 PROJECT_PLAN 已知问题段落 |
| P4_BP | 蓝图反哺 | 当前实现 | 蓝图更新建议 | 检查：重心缓解了？新认知？新边界？需更新蓝图/流程图？ |
| P5 | 记忆归档 | 会话全量变更 | MEMORY.md + Skill | 重要变更→MEMORY，可复用流程→Skill |

---

## 连线表

| 起 → 止 | 触发条件 | 说明 |
|---------|---------|------|
| P0 → Chat | 意图=💬非编程 | 直接回答，不创建任务 |
| P0 → BlueprintEntry | 意图=📋蓝图录入 | 蓝图对话模式 |
| P0 → P0_1_Plan | 意图=🛑规划/🔬调研 | 输出方案后暂停 |
| P0 → QuickFix | 🐛Bug ≤1文件≤5行 | 快速通道 |
| P0 → DebugMode | 🐛Bug 不符合QuickFix | 调试模式 |
| P0 → P0_1 | 意图=✨/🔄 | 完整链 |
| DP_Think → DP_Evidence | 假设列出 | 进入证据链 |
| DP_Evidence → DP_Hypo | 证据链完成 | 检查假设表行数 |
| DP_Hypo → DP_Stop | 第3行 | MUST停下询问用户 |
| DP_Hypo → DP_Fix | 未到第3行 | 修复代码 |
| DP_Fix → P3 | 修复完成 | 进入验证 |
| Align → P0_5 | 对齐 | 继续推进 |
| Align → WarnDiverge | 偏离 | 提醒用户，等待确认 |
| P1_Decision → PausePlanning | 纯规划 | 暂停等待 |
| P1_Decision → P1_5 | 需改代码 | 进入方案讨论 |
| P1_5_Confirm → P1 | 用户要求修改 | 回到拆解 |
| P1_5_Confirm → P2 | 用户确认 | 开始执行 |
| P2_Block → BlockReport | 遇阻 | 报告阻塞等用户选择 |
| P2_Block → P2_Continue | 无阻塞 | 继续执行 |
| P2_5_Pass → P2 | 自审不通过 | 回到修复 |
| P2_5_Pass → P3 | 自审通过 | 进入验证 |
| P3_L4 → QC | 用户验收通过 | 质量检查 |
| P3_L4 → P0_5 | 用户说"还是坏的" | 重新探索 |
| P3_L4 → Revert | 用户说"出现新问题" | git revert 回滚 |
| P3_L4 → P2 | 用户说"需要调整" | 回到执行 |
| QC_Pass → P2 | 检查不通过 | 回到修复 |
| QC_Pass → Git | 全部通过 | git commit + push |
| P4_BP_Update → UpdateBP | 需要更新 | 更新蓝图/流程图 |
| P4_BP_Update → P5 | 不需要 | 直接归档 |
| PausePlanning → P1_5 | 用户说"开始" | 进入方案讨论 |
| DP_Stop → DebugMode | 用户选择后 | 重新进入调试 |

---

## 反馈回路（5 类）

| 回路 | 触发条件 | 路径 | 用途 |
|------|---------|------|------|
| 🔁 修复回路 | P2_5 自审未通过 | P2_5 → P2 | 内部修正 |
| 🔁 验证回路 | P3 L4 用户验收失败 | P3 → P0_5 / Revert / P2 | 用户驱动修正 |
| 🔁 阻塞回路 | P2 遇阻 | P2 → BlockReport → P2 | 阻塞升级 |
| 🔁 调试刹车回路 | 假设表第3行 | DP_Hypo → DP_Stop → DebugMode | 防止无限猜 |
| 🔁 蓝图回路 | P4 蓝图反哺发现变化 | P4 → UpdateBP | 长期演化 |

---

> **版本**: v2 | **对应 SKILL.md**: v5.0 | **更新日期**: 2026-07-04
