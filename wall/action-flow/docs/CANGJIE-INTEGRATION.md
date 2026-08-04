# 仓颉插件 · 接线说明（2026-08-05 建立）

> 本文件是「接线说明」，**不复制仓颉的方法**——方法以仓颉仓库为准，它更新 = git pull = 我们自动升级。

## 一、这是什么

仓颉（cangjie-skill）= 把书/长视频/播客蒸馏成 AI 技能的开源方法论（kangarooking/cangjie-skill，AGPL v3）。
我们以**直接引用**方式集成为「技能封装清单」的配套插件：执行封装时按它的 SKILL.md 流程走，不自己维护一份拷贝。

## 二、仓库位置与更新

| 项 | 值 |
|---|---|
| 本地位置 | `wall/action-flow/plugins/cangjie-skill/`（保留 .git，已加入巨作 .gitignore，第三方仓库不进巨作 git） |
| 上游 | `https://github.com/kangarooking/cangjie-skill` |
| 更新方式 | 对话里说「更新仓颉插件」→ `cd wall/action-flow/plugins/cangjie-skill && git pull`（也可网页 /skills 页「更新仓颉」按钮） |
| 更新频率 | 封装前顺手 pull 一次；不设自动定时 |

## 三、执行时怎么用（封装技能）

触发：用户说「开始封装清单第 X 条」（技能封装清单 `skill_candidates.py` 条目）。

1. **读规范**：读 `plugins/cangjie-skill/SKILL.md`（168 行，含执行流程/质量红线/输入输出要求）+ 需要的 `methodology/NN-*.md`
2. **按流程执行**：三重验证 → RIA++ 构造 → 压力测试（诱饵+跨 skill 混淆）→ 交付；质量红线违反则停下报告
3. **裁剪原则**：仓颉是「整书蒸馏多技能」设计；我们封装**单条知识→单个技能**时，跳过整书级产物（BOOK_OVERVIEW / INDEX / DIGEST / GLOSSARY），只取核心：三重验证 → RIA++ 六段 → 压力测试 → 交付
4. **落盘**：`~/.workbuddy/skills/<name>/`（SKILL.md + test-prompts.json）
5. **回写**：`python skill_candidates.py status <key> done`（或 `abandoned "<理由>"`）→ 顺手 `python skill_assets.py add ...` 进技能资产清单（active）

## 四、输出文件速查（仓颉模板）

| 文件 | 作用 | 单条封装要不要 |
|---|---|---|
| `SKILL.md` | 技能本体（六段：R/I/A1/A2/E/B） | ✅ 要 |
| `test-prompts.json` | 触发测试（应调用/诱饵/跨 skill 混淆） | ✅ 要 |
| `BOOK_OVERVIEW.md` / `INDEX.md` / `DIGEST.md` / `GLOSSARY.md` | 整书级产物 | ❌ 单条封装跳过 |

## 五、协议备注（AGPL v3）

- **自用没问题**：AGPL 约束"再分发/提供网络服务"，个人本地使用不触发
- **将来若对外发布工具**：集成仓颉的部分要评估合规（AGPL 传染性），到时再说
- 我们在巨作 .gitignore 忽略了该目录：克隆仓库不等于分发

## 六、故障处理

| 情况 | 处理 |
|---|---|
| git pull 失败（上游改动冲突） | 报告失败原因；必要时 `git stash` 后重试，不动手改仓颉内部文件 |
| 仓颉 SKILL.md 读不懂/执行卡住 | 停在当前步报告，不猜测硬编 |
| 封装中途失败 | 按质量红线回炉；两轮不过 → `skill_candidates.py status <key> abandoned "<理由>"` |
