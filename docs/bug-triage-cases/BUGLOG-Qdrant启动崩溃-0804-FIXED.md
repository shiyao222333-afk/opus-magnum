# BUGLOG-Qdrant启动崩溃-0804-FIXED

> 元数据：项目=opus-magnum ｜ 跨度=2026-08-03 22:51 ~ 08-04 10:20 ｜ 流程依据=bug-triage skill
> 一句话背景：前端重构后重启服务时 Qdrant/熔知 无法启动——**不是重构代码问题，是两个"启动方式"坑**：Qdrant 被我测试时的自定义存储环境变量触发假崩溃；熔知被 WorkBuddy 的 os.remove 钩子递归爆栈。

## 1. 现象
- Qdrant（6333）启动即 panic：`aws_lc_0_39_1_jent_entropy_switch_notime_impl`（AWS-LC 熵初始化崩溃），10+ 次重试全崩、重启电脑仍崩
- 熔知（8080）启动退出：`RecursionError: maximum recursion depth exceeded`（main.py `_enforce_single_instance` 的 `os.remove` 被 WorkBuddy `sitecustomize.py` 的 `_safe_remove` 钩子包装后递归 991+ 次）
- 用户原话：「网页重构前从来没有出现过这个问题」「在这个会话环境已经持续用了一个多月了，从来没有出现过」

## 2. 调试历程（证据链）
### 阶段一：怀疑重构代码（第 1 轮）❌
- 假设：前端重构（app.py 顶部条）导致 Qdrant 崩溃
- 验证：grep 代码证据——app.py 与 Qdrant 仅 4 处读/探测（qdrant_reachable/set_starred/fetch_dashboard_docs），**无任何 subprocess/kill 逻辑**；重构 commit 6f41ff5 未碰任何 Qdrant 相关文件
- 结论：❌ 排除 — 重构代码与 Qdrant 无因果（时序关联=我重启巨作撞多实例托盘 bug（已修）杀了 Qdrant）

### 阶段二：怀疑会话环境（第 1~2 轮）❌
- 假设：WorkBuddy 会话 CPU 熵受限（沙箱），用户桌面正常
- 验证：沙箱豁免仍 panic；用户澄清「这个环境用一个多月了从没这问题」
- 结论：❌ 排除 — 不是环境本身，是**启动参数差异**

### 阶段三：启动参数差异（第 2 轮）✅
- 假设：我之前测试都用**自定义 env**（`QDRANT__STORAGE__STORAGE_PATH=D:\citrinitas\library\qdrant_db` + `QDRANT__SERVICE__HTTP_PORT=6333`）启动 Qdrant → 触发 AWS-LC 熵 panic；**正确方式=默认配置**（cwd=exe 目录、无自定义 storage env，与 qdrant_helper.ps1 一致）
- 验证：`Popen([D:\qdrant\qdrant.exe], cwd=D:\qdrant)`（无自定义 env）→ **启动成功，athanor_v1 完整（926 点）**
- 结论：✅ 确认 — Qdrant 假崩溃根因=自定义存储 env；数据一直在 D:\qdrant\storage（默认），从未损坏
- 熔知根因（同一轮）：WorkBuddy shim（PYTHONPATH 注入 sitecustomize）包装 os.remove → 熔知单例锁删除递归爆栈；**正确方式=clean_env()（剥 PYTHONPATH）启动** → 熔知成功（8080，926 点）

## 3. 最终方案（启动方式修正，无需改业务代码）
| 服务 | 正确启动方式 | 错误方式（踩坑） |
|---|---|---|
| Qdrant | `Popen(qdrant.exe, cwd=exe目录)` 默认配置 | 自定义 `QDRANT__STORAGE__STORAGE_PATH` env → AWS-LC 熵假崩溃 |
| 熔知（及一切五器 python 服务） | `env=clean_env()`（剥 PYTHONPATH） | 继承 WorkBuddy PYTHONPATH（shim sitecustomize）→ os.remove 钩子递归爆栈 |

## 4. 已排除方向
| # | 方向 | 证伪证据 |
|---|------|---------|
| 1 | 重构代码导致 | app.py 无启停 Qdrant 逻辑、diff 未碰 Qdrant 链路 |
| 2 | Qdrant exe 损坏 | 两个版本 exe 都"崩"，但默认配置启动成功=exe 正常 |
| 3 | 会话环境熵受限 | 用户澄清同环境稳定一月；默认配置同环境启动成功 |
| 4 | 重启电脑可恢复 | 重启后仍崩（因为启动参数没变） |

## 5. 教训（绑定证据）
1. **自定义 env 可能触发假崩溃**（阶段三：QDRANT__STORAGE__STORAGE_PATH → AWS-LC panic）——排查启动失败先试"默认配置零 env"，别一上来加自定义参数
2. **WorkBuddy shim 钩子（sitecustomize.py 包装 os.remove 等）会干扰子进程**（阶段三：熔知单例锁删除递归爆栈）——**WorkBuddy 会话启动任何 python 服务一律用 `clean_env()`（launcher/envutil.py）剥 PYTHONPATH**
3. **"同一个环境之前能用"≠"现在启动方式对"**（阶段三：之前托盘/qdrant_helper 用默认方式一直正常；我排查时改用自定义参数反而触发崩溃）——用户坚持"之前稳定"是排查的宝贵线索，别过早归因环境
