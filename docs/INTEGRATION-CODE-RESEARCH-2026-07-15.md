# 三器代码调研报告（INTEGRATION-CODE-RESEARCH-2026-07-15）

> 目的：为「一键启动 + 三器中转文件夹 + B站全流程默认检查」任务（#22–#26）做只读代码调研，
> 确认现状、找出可复用代码、设计人审闸门。本报告**不修改任何项目代码**。

## 1. 调研范围与方法
- 通读 Nigredo / Albedo / Citrinitas 三者源码（配置、下载器、精炼入口、watcher、API 层）。
- 仅只读分析，未改动任何文件。
- 关键文件：`nigredo/config/__init__.py`、`nigredo/core/downloader.py`、`nigredo/platforms/bilibili.py`；
  `albedo/app.py`、`albedo/flows/refine.py`、`albedo/core/report.py`；
  `citrinitas/main.py`、`citrinitas/watcher/listener.py`、`citrinitas/watcher/processor.py`。

## 2. 各器现状速览

### Nigredo（馏析 · Streamlit · :8502）
- 配置：`config/__init__.py` 用 python-dotenv，路径写死 `DATA_DIR/data`、`CACHE_DIR=data/cache`、`REPORTS_DIR=data/reports`。**无独立可配置「输出目录」变量**。
- 产出：`DownloadManager._save_subtitle_files` 把字幕存到 `cache_dir/{bv_id}.txt` + `.srt`（**硬编码到 data/cache**）。
- 链接解析：`bilibili.parse_url` 支持 BV 直链 + `b23.tv` 短链（跟随 302）。带 `?t=` 参数 OK（正则用 search）。**合集/番剧链接不支持**（非单个 BV，会失败）。
- API：**无 HTTP API**，纯 Streamlit UI。
- 去重：`VideoCache` 按 BV 号去重（`cache.is_processed`）。

### Albedo（炼真 · Streamlit · :8501）
- **无 watch/monitor 模块**（确认：用户记忆模糊，确实没建过）。
- **无 config 模块**：目录只有 `core/ flows/ data/ docs/ app.py`，输出落到 `data/out`（硬编码）。
- 精炼入口：`flows/refine.py` 的 `refine_text(...)` 返回含 `.report` 的精炼对象（鉴定报告）。
- 入库就绪报告格式：见 `docs/ADR-005-INGESTION-READY-REPORT.md`（YAML frontmatter + 正文）。
- API：**无 HTTP API**，纯 Streamlit UI。

### Citrinitas（熔知 · NiceGUI/FastAPI · :8080）
- watcher 完整：`watcher/{listener,processor,state,failures,utils,migration}.py`。
- 机制：watchdog `Observer` 监听 `INBOX_DIR`（= `D:\citrinitas\data\inbox`）→ `on_created` 入队 → `_processing_loop` 取文件 → `_process_file_with_timeout`（超时保护）→ 重试重入队 → 摄入 → **处理后 `os.remove` 删原文件**（书类归档 `library/books/` 永久保留）。
- 状态：`state.py` 的 `_append_state` / `_watch_stats`，落 `file_state.jsonl`；有 `needs_review`、`failed`、`done` 状态。
- 幂等：`_do_ingest` 检测 "duplicate"/"重复" → 标 `done` + 删文件（doc_id 基于 file_path 确定性）。
- 重试/DLQ：`_handle_failure` + 超时重入队 + `WATCH_V2_DLQ_TTL_DAYS` 过期清理 + 启动 `_recover_retry_files`。
- API：底层是 FastAPI（NiceGUI），已有 `@app.get("/health")` 和 `@app.get("/reports/{filename}")`。**无「提交任务」API**。

## 3. 五个待查点结论（来自用户提问）
1. **炼真有无 watch 模块** → **无**。需新建（可复用熔知 watcher 模式）。
2. **馏析输出目录可配** → **不可配**，硬编码 `data/cache`。需加 `OUTPUT_DIR` 可配置项，默认指向炼真监控目录。
3. **三器可复用代码** → 见第 5 节。
4. **熔知删除机制** → 处理后 `os.remove`（非书类），书类永久保留。**人审闸门要加在「处理前」分支**（见第 6 节）。
5. **三器 API** → Nigredo/Albedo 无 API（Streamlit）；Citrinitas 有 FastAPI 底层但仅 `/health`。→ **需补「提交任务」API**（至少 Nigredo，Albedo/Citrinitas 同理可加）。

## 4. 遗漏视角 A–H 结论
| 视角 | 现状 | 结论 |
|---|---|---|
| **A 触发机制** | 三器无「提交任务」API | **必须新建**：Nigredo 暴露 `POST /api/process{url}`；总管经 API 触发，不 import 三器，保独立性，契合未来 API/MCP |
| **B 并发/队列** | 熔知 watcher 已有 Queue+超时+重入队 | 炼真新建 watcher 复用同模式即可；多链接不冲突 |
| **C 失败/重试** | 熔知已有超时重入队+DLQ+retry恢复 | 炼真复用；中转①→中转② 失败标 `error/` 可重入 |
| **D 幂等去重** | 熔知 doc_id 去重 + Nigredo BV 去重 | 基本具备；中转文件用 BV 命名即确定性，同地址两遍熔知自动跳过 |
| **E 人审 UI 入口** | 熔知有 `needs_review`+审核页；炼真侧无 | 中转①（炼真侧）人审 UI 需新建，或总管统一「待审面板」聚合中转①② |
| **F 链接形态** | BV✅ b23.tv✅ 带参✅ 合集❌ | 合集/番剧暂不支持，需在 orchestrator/UI 明确限制或报错 |
| **G 中转路径一致性** | 见用户修正：各器独立配置，默认值对齐同一物理路径 | 不引入共享配置，保独立性 |
| **H 统一日志** | 熔知 `local_data/logs/`；Nigredo 控制台；Albedo 未知 | 非阻塞，可后续 `start_all.bat` 聚合或各器日志归一 |

## 5. 可复用代码清单（代码互鉴，用户③要求）
- **watcher 模式**（熔知 `watcher/*`）：watchdog 监听 + Queue + 超时保护 `_process_file_with_timeout` + 重试重入队 + `state.py` 状态机 + `failures.py` 故障分类。**炼真 watch 模块直接复用此套**（copy 或抽共享库）。
- **配置加载**：Nigredo `config/__init__.py`（dotenv）+ Citrinitas `config/settings.py`。Albedo 需补同类 config 模块（加 `OUTPUT_DIR`/`WATCH_DIR`/`REQUIRE_HUMAN_REVIEW`）。
- **文件契约（frontmatter）**：Albedo `ADR-005` 的入库就绪报告格式（YAML frontmatter + 正文）应作为中转②文件标准；中转①（馏析→炼真）也用同类 frontmatter（text/title/up_name/source_url/video_id/signals）。
- **去重**：Nigredo `VideoCache`（BV）→ 中转①文件名用 BV；Citrinitas doc_id（file_path）→ 中转②确定性。
- **URL 解析**：Nigredo `bilibili.parse_url`（BV+b23.tv+带参）可直接复用于 orchestrator 的链接规范化。

## 6. 人审闸门设计方案（草案，用户①④）
**需求**：监控文件夹文件在「被解析前」需人工审核通过，不自动删除；闸门可开关（调试开、稳定关）。

**熔知侧（中转②）**：在 `watcher/processor._process_file` 开头加分支——
```
if REQUIRE_HUMAN_REVIEW and not file_approved(filepath):
    move to inbox/_pending_review/   # 不处理、不删除
    state = "pending_review"
    return
# 否则正常处理（稳定期 REQUIRE_HUMAN_REVIEW=False 时全自动，退回原 needs_review）
```
审核通过后（UI 点「通过」）将文件移回 `inbox/` 触发处理，或调用内部 `approve(filepath)`。

**炼真侧（中转①）**：新建 watch 模块同理——文件落入监控目录后，若闸门开则移到 `watch_in/_pending_review/`，人审通过后精炼并写中转②。

**配置项**：各器 `config` 加 `REQUIRE_HUMAN_REVIEW: bool = True`（默认开，调试期）；稳定后设 `False`。

**统一审核 UI（用户 E）**：总管 Supervisor(8503) 加「待审面板」，聚合中转①`_pending_review/` 与中转②`_pending_review/`，一处点通过。

## 7. 对任务规划的影响与确认
- #23 炼真 watch 模块：**确认需新建**，复用熔知 watcher 模式；加人审闸门 + 状态机（in/approved/processing/done/error）。
- #22 启动脚本：Nigredo 需先支持「已在跑则复用」（去掉 run.bat 杀旧进程），否则违背「瞬间打开」。
- #24 编排：确认经 **Nigredo API** 触发（非 import）；监控中转①②进度；状态聚合。
- #25 鲁棒：文件用 BV 命名（已具备）；合集链接需在 UI 限制（F 视角）。
- #26 UI：贴链接跑全程 + 待审面板（人审闸门为开时）。
- #28 独立性：四器各自 config 独立，默认值对齐物理路径（G 已修正）。

---
*本报告为规划调研，供实施阶段（#22–#26）参考。所有结论基于 2026-07-15 代码快照。*
