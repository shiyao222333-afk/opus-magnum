# 项目管理 Workflow v6.0

> CRITICAL: 所有开发对话必须首先读取此文件。回复第一行 MUST 输出 Phase 0 意图分类。

---

## CRITICAL: 绝对规则（不可违反）

1. **CRITICAL: 回复第一行 MUST 输出 Phase 0 意图分类** — 不输出 = 流程违规
2. **CRITICAL: 改前先读** — Read 后再 Edit，NEVER 猜代码
3. **CRITICAL: 同一步骤重试 ≤ 3** — 第 3 次失败 MUST 换方案或停下来询问用户
4. **CRITICAL: 遇阻 NEVER 自行跳过或改方案** — MUST 报告阻塞，等用户选择
5. **CRITICAL: 调试时 MUST 先输出证据链再动手** — 禁止"猜了就改"

---

## Phase 0：意图分类（每条消息必经，不可跳过）

收到每条消息后，MUST 先输出分类判断。

| 用户说的话 | 分类 | 版本 | 走哪条路 |
|-----------|------|------|---------|
| "有 bug / 坏了 / 报错" | 🐛 Bug 修复 | PATCH | 调试模式 或 QuickFix |
| "加个功能 / 优化 / 重构" | ✨ 功能开发 | MINOR | 完整链 |
| "研究一下 / 查一下竞品" | 🔬 调研 | 无 | 到 Phase 1 出报告 |
| "先分析一下 / 看看这个" | 🔍 纯分析 | 无 | 只读代码，不出手 |
| "推荐个 X / 今天天气" | 💬 问答 | 无 | 直接回答 |
| "录入蓝图 / 加入蓝图" | 📋 蓝图录入 | 无 | 蓝图对话模式 |
| "执行 / 确认 / 好了" | ✅ 确认 | 无 | 继续当前 Phase 下一步 |
| AI 分不清 | — | — | 默认归为 🔍 纯分析 → 确认后继续 |

**分类结果 MUST 显式输出**（如 `🐛 Bug 修复 — PATCH — 走调试模式`）。

---

## 三条路径

| 路径 | 触发条件 | 流程 |
|------|---------|------|
| QuickFix | ≤1 文件 ≤5 行 无逻辑变更 | Phase 0 → 直接改 → 验证 → 文档 |
| **调试模式** | 🐛 Bug + 不符合 QuickFix | 读 `DEBUG.md` → 走调试协议 → 修复 → 验证 |
| 完整链 | ✨ 功能 / 🔄 重构 | 读 `EXECUTION.md` → Phase 0.1~5 完整流程 |

---

## Pre-flight（分级加载）

根据任务类型，只读必要的文件：

| 任务类型 | MUST 读 | 按需读 |
|---------|--------|--------|
| 🐛 Bug 修复 | PROJECT_PLAN 顶部当前状态(≤5行) + 今天日志 | `DEBUG.md` |
| ✨ 功能开发 | PROJECT_PLAN 当前状态 + BLUEPRINT 当前重心 | `EXECUTION.md` |
| 🔄 重构 | PROJECT_PLAN 当前状态 + BLUEPRINT | `EXECUTION.md` |
| 🔬 调研 | PROJECT_PLAN 当前状态 | — |
| 💬 问答 | 无 | — |

---

## 文件索引（遇到场景时读对应文件）

| 场景 | 读哪个文件 |
|------|-----------|
| 调试 Bug | `DEBUG.md`（完整调试协议） |
| 执行功能/重构 | `EXECUTION.md`（Phase 2~5 完整规则） |
| 场景 SOP / Gate 格式 / Commit 格式 | `SKILL-CHEATSHEET.md` |
| 审查协议 / 提问规则 / 沟通规则 / Git 规范 / 版本号 | `REFERENCE.md` |
| 流程图 | `FLOWCHART.md`（项目 `workflow/` 目录） |
| 项目蓝图 | `BLUEPRINT.md`（项目 `workflow/` 目录） |

---

## CRITICAL: 执行检查清单（每条消息回复前过一遍）

- [ ] 第一行输出了 Phase 0 意图分类？
- [ ] 走对了路径？（QuickFix / 调试模式 / 完整链）
- [ ] 改代码前先 Read 了目标文件？
- [ ] 调试模式下读了 `DEBUG.md` 并输出证据链？
- [ ] 遇阻时报告了阻塞而不是自行跳过？
- [ ] 没有技术术语（用了生活比喻）？
- [ ] git commit 后自动 push 了？

---

> v6.0 — 文件拆分：主文件 <100 行，调试协议拆入 `DEBUG.md`，执行规则拆入 `EXECUTION.md`，参考内容拆入 `REFERENCE.md`。基于 v5.2。
