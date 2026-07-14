# 三器非监控代码通读 · 启发报告（第二部分）

> 日期：2026-07-15
> 范围：Nigredo / Albedo / Citrinitas 三者**监控文件夹以外的部分**
> 目的：为「一键启动 + 文件夹契约 + 人审闸门 + API 触发 + 鲁棒性 + 审核面板」找可复用代码与设计启发
> 关联：第一部分 `INTEGRATION-CODE-RESEARCH-2026-07-15.md`（已确认炼真无 watch 模块、馏析输出不可配、熔知删除机制）

---

## 一、最关键的 5 个启发（直接改变实施）

### 1. Nigredo 早就有任务队列 → "提交任务"天然是「写队列文件」
- `core/queue.py`：`enqueue(url)` 把地址追加进 `data/queue.json`（去重），`drain_queue()` 取出并清空。
- `run_queue.py` 在 `run.bat` 启动 UI **前** drain 一次。
- **启发**：总管"触发 Nigredo"= 往 `data/queue.json` 追加 URL（文件契约，不 import、不依赖 HTTP）。
- **但**：当前只开机 drain 一次，运行中新塞的 URL 不会被处理。**需补一个常驻 queue worker**（循环 drain），才能被总管实时触发。这是 #24 触发机制的最小改动。

### 2. Albedo 的 UI 早已能解析 Nigredo 输出 → 中转①契约雏形已存在
- `app.py` 有"馏析项目输出"模式 + `_parse_nigredo_json()` / `_best_effort_parse()`，已能消费 Nigredo 的 `text/content/subtitle` + `meta{title,up_name,source_url,video_id}`。
- **但**：Nigredo 当前只落 `data/cache/{bv}.txt`（纯字幕）+ `{bv}.srt`，**没把标题/UP/链接写进文件**。Albedo 的 `meta` 解析形同虚设。
- **启发**：中转①格式应升级为 **`{bv}.md`（YAML frontmatter 带元数据 + 正文=字幕）**，让 Albedo 的 watcher 能零改动复用 `_parse_nigredo_json`。这是顺手补齐的契约，不是新造。

### 3. Citrinitas 收件箱是"纯文本读取" → Albedo 预填的分面元数据（ADR-005）当前被丢弃
- `services/ingest_service.py` 的 `_step_read_content` 只 `open(file).read()` 当文本；`watcher/` 摄入同理。
- Albedo `core/models.py` 的 `IngestionMeta`（content_type/domain_udc/...）已定义、报告里也带，但**走收件箱路径时没人消费**。
- **启发**：Citrinitas 已有 `config/hooks.py` 的**预存储钩子**（`_step_pre_store_hooks` 调用 `get_hooks()`）。写一个新钩子 `albedo_meta_hook`：摄入时找同目录下的 `{name}.meta.json`（Albedo 写报告时顺手写 sidecar），把 `ingestion_meta` 合并进 payload。**这一步才真正兑现 ADR-005**，且不改摄入管线，对熔知零侵入。

### 4. Citrinitas 已有"运行时审查开关"范本 → 我们的人审闸门直接抄模式
- `config/settings.py` 的 `is_force_review_all()`：读 `KB_FORCE_REVIEW_ALL` 环境变量，**即时生效、无需重启**，强制所有摄入进待审核。
- **启发**：Nigredo / Albedo 的 `REQUIRE_HUMAN_REVIEW` 闸门用**完全相同的运行时 env 开关模式**（不重启、不共享配置）。Citrinitas 自身已有审查机制（needs_review + force_review_all），所以我们不在熔知前加闸门（符合用户②"熔知最成熟不动"）。

### 5. Citrinitas 已把状态暴露成信号 → 总管 run_state 不用自己解析日志
- `main.py` 的 `/health` 返回 `watcher.alive` + `watcher.stats`；`data/activity_log.jsonl` 记录 `ingest_success` / `ingest_failed`（含 `doc_id` + `content_hash`）。
- **启发**：总管状态聚合直接轮询 `http://127.0.0.1:8080/health` + 读 `activity_log.jsonl`，比盯着 inbox 删文件靠谱。中转①/②的出现与否用文件夹存在性判断即可。

---

## 二、逐项目发现

### Nigredo（馏析）
| 项 | 现状 | 对整合的意义 |
|---|---|---|
| 配置 | `config/__init__.py` 模块常量 + dotenv，**无 OUTPUT 可配**，`CACHE_DIR` 硬编码 | #23 加 `OUTPUT_DIR` / `WATCH` 开关，仿自身风格 |
| 产出 | `DownloadManager.process()` 落 `{bv}.txt`+`{bv}.srt` 到 `CACHE_DIR`；`info.__dict__` 含 title/author/duration/bvid | 中转①应带 frontmatter（标题/UP/链接/BV） |
| 队列 | `data/queue.json` 仅开机 drain 一次 | 补常驻 worker 才能实时触发 |
| 启动 | `run.bat` 有"杀旧进程重启 8502"（行40-42） | #22 改为端口探测复用 |
| 链接 | `detect_platform` 正则含 `b23.tv`/`BV...`；`bilibili.parse_url` 归一化 | #25 短链/?t= 已支持；**合集不支持**（未来 UI 拦截报错） |
| 入口 | `pages/1_📥_视频摄入.py` 调 `dm.process(url)` + 写 `session_state` | 可参考其调用方式 |

### Albedo（炼真）
| 项 | 现状 | 对整合的意义 |
|---|---|---|
| 配置 | **无 config 模块**，`core/llm.py` 内联 `os.environ.get(...)` | #23 建最小 `config.py`（仿 Nigredo 风格，不一刀切引 YAML） |
| 解析 | `_parse_nigredo_json` / `_best_effort_parse` 已支持 Nigredo 输出 | watcher 直接复用，中转①契约早已存在 |
| 输入契约 | `core/models.py:AlbedoInput` 字段 = text/title/up_name/video_id/source_url/signals/text_type | = 中转①文件 frontmatter 字段 |
| 产出 | `report.render_report(out)` → Markdown；`out.to_json()` → 完整对象 | 中转② = `{bv}_refined.md`（人审）+ `{bv}_refined.meta.json`（机读 ingestion_meta） |
| 启动 | `run.bat` 启动 Streamlit 8501，无杀进程逻辑（已天然可复用） | #22 只需加端口探测 |
| 缺失 | 无 watcher（确认） | #23 新建，直接复用熔知 watcher 骨架 + 自身 _parse |

### Citrinitas（熔知）
| 项 | 现状 | 对整合的意义 |
|---|---|---|
| 活跃监控 | `main.py`:`import watcher` + `watcher.start_watcher()`；日志"守望文件夹 v2" | **活跃收件箱 = `data/inbox`**（非 settings 的 `library/inbox`）→ 中转②锁 `data/inbox` |
| 路由模板 | `@app.get("/health")` / `@app.get("/reports/{filename}")` 直接加在 FastAPI `app` | 未来 `/api/ingest` 同样一行，即 API/MCP 模板 |
| 摄入管线 | `ingest_service.ingest`：10 步管线 + **内容哈希去重** + 预存储钩子 + 返回 `doc_id`/`content_hash` | #25 幂等去重已在 sink；返回 doc_id 供 run_state 记录 |
| 审查开关 | `is_force_review_all()` 运行时 env 开关 | #23 闸门模式范本 |
| 状态信号 | `/health` 的 watcher stats + `data/activity_log.jsonl` | #24 run_state 信号源 |
| 钩子点 | `config/hooks.py:get_hooks()` 在入库前介入 | #23 兑现 ADR-005 的 ingestion_meta 消费点 |
| ⚠️ 双 watcher | 仓库同时存在 `watcher/` 包 与根 `watcher_v2.py`；`data/inbox` 与 `library/inbox` 两个收件箱；`.watch*.lock`/`.watch*.migrated` 迁移锁 | **整合前需确认活跃路径，建议统一到 `data/inbox`**（见第四节） |

---

## 三、对实施任务（#22–#28）的修正 / 细化

- **#22 一键启动**：Citrinitas `run.bat` 自带 Qdrant 启停 + 管理员提权 + 配置/模型检测；start_all 直接调它即可，复用探测 8080。`start_all.bat` 顺序：先 Citrinitas（它拉起 Qdrant 依赖）→ Nigredo（8502）→ Albedo（8501）→ Supervisor（8503）。每个先探测端口，监听则跳过。
- **#23 文件夹契约**：
  - 中转① = `{bv}.md`：`--- YAML frontmatter(title/up_name/video_id/source_url/platform) ---` + 正文=字幕。
  - 中转② = `{bv}_refined.md`（鉴定报告，人审用）+ `{bv}_refined.meta.json`（ingestion_meta sidecar，供熔知钩子消费）。
  - 人审闸门 = `review_pending/` 与 `approved/` 两目录：产出方写 `review_pending/`；`REQUIRE_HUMAN_REVIEW=false` 时 worker 自动晋级；`true` 时等 `approved/`（总管或人在项目 UI 点通过→移动文件）。
- **#24 编排**：触发=写 Nigredo `data/queue.json`（文件契约，非 import）；状态=轮询 Citrinitas `/health` + `activity_log.jsonl` + 中转①②文件出现。
- **#25 鲁棒**：Citrinitas 已有内容哈希去重；BV 命名 + 链接归一化 Nigredo 已有；同地址两遍 → 中转文件覆盖 + 熔知去重 → 录入一致。
- **#26 审核面板**：审批=**移动文件** `review_pending/→approved/`（纯文件契约，无需给 Nigredo/Albedo 加 HTTP）；未来 API 用 Citrinitas `/health` 同款 `@app.post` 模板。
- **#28 独立性**：三器配置风格各异（Nigredo 模块 / Albedo 内联 / Citrinitas YAML）→ 各自加**自己风格**的开关（OUTPUT_DIR/REQUIRE_HUMAN_REVIEW），**绝不共享配置**（落实用户 G 修正）。

---

## 四、待你确认的小尾巴

1. **活跃收件箱**：我判断是 `data/inbox`（依据：run.bat 文案"Drop files into data\inbox\" + `main.py` import `watcher` + `watcher/processor.py` 用 `INBOX_DIR`）。`library/inbox`（`WATCH_V2_INBOX_DIR` 默认）疑似遗留/次要。→ 确认后中转②锁定 `data/inbox`，并建议清理双 watcher 歧义。
2. **Nigredo 常驻 queue worker**：建议新增独立 `queue_worker.py`（循环 drain `data/queue.json`，处理失败写 `data/queue_errors.jsonl`），由 `run.bat` 在 UI 之外另起一个后台进程。是否同意？

---

## 五、复用清单（直接抄，不重造）

| 目标 | 直接复用 | 来源 |
|---|---|---|
| Albedo watcher 骨架 | watchdog + 队列 + 超时 + 状态机 + 故障分类 | Citrinitas `watcher/` |
| 人审闸门开关模式 | `is_force_review_all()` 的运行时 env 读取 | Citrinitas `config/settings.py` |
| 中转①解析 | `_parse_nigredo_json` / `_best_effort_parse` | Albedo `app.py` |
| 中转①输入契约 | `AlbedoInput` 字段 | Albedo `core/models.py` |
| 中转②格式 | `render_report` + `to_json` | Albedo `core/report.py` |
| 未来摄入 API | `@app.get("/health")` 路由模板 | Citrinitas `main.py` |
| 入库去重 | 内容哈希去重步骤 | Citrinitas `ingest_service._step_dedup` |
| ADR-005 兑现 | `config/hooks.py` 预存储钩子 | Citrinitas `ingest_service._step_pre_store_hooks` |
