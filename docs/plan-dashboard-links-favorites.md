# 巨作周看板 · 文章超链接预览 + 收藏持久化 — 实现方案（存档）

> 状态：**实现中**（2026-08-01 下午决策修订：走法改 A、本期直接实现）。
> 决策记录（2026-08-01）：初版——超链接走法选 **B（巨作自建预览页）**，本期**先存档方案、暂不实现**。
> **决策修订（2026-08-01 下午）**：超链接走法改为 **A（外链熔知 8080 /doc/{doc_id} + 本地弹窗兜底）**；本期**直接实现**。
> 团队：software-opus-board（主理人齐活林 / 架构师高见远）。架构师方案已基于实地读码 + Qdrant 临时集合实测，非纸面推演。

---

## 0. 已查证事实（方案地基）

- **看板**：`app.py` 的 `page_dashboard()`（路由 `/`）调 `core/qdrant_bridge.fetch_week_docs()` 拉本周文档，按 `source_project` 分组列出 title（纯文本，无链接无收藏）。
- **数据结构**：巨作直读共享 Qdrant 集合 `athanor_v1`（env `QDRANT_URL` 默认 `http://127.0.0.1:6333`）。每条文档按 `doc_id` 切多 chunk。`payload` 含 `doc_id/title/source/source_project/timeline.ingested/text/auto_summary/subject/keywords/domain/content_type/stats{access_count, starred}`。
- **收藏字段现成**：熔知 `ingest_pipeline.py:342` 写入 `"stats":{"access_count":0,"starred":False}`；`schema.md:185` 定义 `starred|boolean|是否收藏`。即"熔知53字段里对应的位置" = **`stats.starred`**。
- **熔知详情页**：`D:\citrinitas\pages\hub\detail.py:14` 有 `@ui.page("/doc/{doc_id}")`，但本方案选 B 走法，**不依赖它**。
- **只读桥**：`qdrant_bridge.py` 头注释声明"只读"。本需求必然打破"只读"，但**不打破五器独立**（写入仍走 Qdrant REST，不 import 熔知代码）。

### 实测关键结论（推翻最初假设）
架构师在 Qdrant 临时集合 `_arch_probe_tmp`（测完 DELETE，生产集合全程只读）实测：
- Qdrant 1.18.2 的 `set_payload` 支持 `key:"stats"` + `filter:{doc_id}` 单次 HTTP 写完 `stats.starred`，**自动保留 `access_count`**、覆盖该 doc 全部 chunk。
- 无需"先 scroll 读 access_count → 合并 → 写回"三步走；也无需先 scroll 出 chunk id 列表。
- 命令行可复现：
  ```bash
  curl -X POST "http://127.0.0.1:6333/collections/{C}/points/payload?wait=true" \
    -H "Content-Type: application/json" \
    -d '{"payload":{"starred":true},"key":"stats",
         "filter":{"must":[{"key":"doc_id","match":{"value":"D2"}}]}}'
  ```

---

## 1. 决策记录

| # | 决策点 | 结论 | 说明 |
|---|---|---|---|
| 1 | 超链接走法 | **A：外链熔知 8080 `/doc/{doc_id}` + 本地弹窗兜底**（2026-08-01 下午修订拍板；原 B 作废） | 零新增页面；熔知离线时本地弹窗兜底；代价 = 依赖熔知 8080 在线 |
| 2 | 打破"只读桥" | **获准（隐含于用户需求"保存到熔知53字段"）** | 加三重围栏 + 文件头诚实标注"AI 设计决策，非用户指令，待确认" |
| 3 | 收藏字段 | **`stats.starred`，不新增字段** | 不引入 `starred_at`（会污染熔知 schema，须熔知侧拍板） |
| 4 | 本周区 vs 收藏区 | 默认**双显**（本周区内已收藏条带 ★ 高亮） | 一行 filter 可改互斥，随时可调整 |
| 5 | 收藏区上限 | 前 20 + "共 N 篇"计数 | 防收藏累积撑爆看板 |
| 6 | payload index | 暂不建（190 点全扫描毫秒级） | 点数破万再议 |
| 7 | 全量 scroll 缓存 | 暂不加，保持真值来源单一 | 刷新体感慢（>1s）再加 60s TTL |

---

## 2. 超链接预览（2026-08-01 修订：A 走法）

> ⚠️ 本节原设计为 B 走法（巨作自建预览页），**已被用户修订为 A 走法**：看板标题直接外链熔知 8080 `/doc/{doc_id}`（URL 一律经 `settings.citrinitas.endpoint`），熔知不可达时本地弹窗（标题/auto_summary/subject/keywords/text 预览）兜底。数据层（§3）与 ★ 收藏交互（§4）不受影响。原 B 走法设计保留备查：

**（B 走法 · 已作废，备查）** 新增巨作预览页 `@ui.page("/doc/{doc_id}")` in `app.py`：
- 调用 `core.qdrant_bridge` 的取数函数，按 `doc_id` 从 `scroll_payloads()` 结果中定位该文档首个 chunk（payload 已含全部展示字段）。
- 渲染：标题、`auto_summary`、`subject`、`keywords`（标签）、`source`/`source_project`、`timeline`、`text[:N]`（正文摘要，或按需完整）。
- 纯读，不依赖熔知进程。
- 看板条目 `_doc_row()` 中「👁 预览」链接指向 `/doc/{doc_id}`（巨作内跳转，NiceGUI 同站）。

> 走法 A（现采纳）：外链熔知 8080 `/doc/{doc_id}` + 本地弹窗兜底。2026-08-01 下午修订拍板，取代原 B。

---

## 3. 收藏写入（核心接口）

### `set_starred` —— 唯一写入口
```python
def set_starred(doc_id: str, value: bool, *, timeout: int = 8) -> dict:
    """把某文档所有 chunk 的 stats.starred 置为 value。全模块唯一写入口。"""
```
**返回契约（永不抛异常）**：`{ok:bool, doc_id:str, starred:bool, updated:int, error:str|None}`。
**关键点**：
1. `?wait=true` 必须带（否则异步落盘，刷新可能读旧值，表现"点了没反应"）。
2. `key:"stats"` 走嵌套合并（漏了会整体替换 stats、丢 access_count，不可逆）。
3. `filter:{doc_id}` 覆盖全部 chunk（用 filter 而非 point id 列表，免前置 scroll）。
4. 先 `POST points/count` 数 chunk 数：Qdrant 对"匹配 0 点"的 set_payload 也返回 completed，必须 count 才能区分"写成功"与"doc 不存在"。

### 围栏（三件套）
```python
WRITABLE_PAYLOAD_KEYS = frozenset({"stats.starred"})  # 白名单，新增写字段必先改此行
# 全模块只允许 set_starred 一个函数发写请求
# 文件头追加变更声明块（诚实标注 AI 设计决策，非用户指令）
```

### 其余新增函数（`core/qdrant_bridge.py`）
| 函数 | 签名 | 契约 |
|---|---|---|
| `is_starred` | `(d:dict)->bool` | 三层容错（stats 缺失/非 dict/starred 缺失 → False），绝不抛 |
| `count_doc_points` | `(doc_id,*,timeout=8)->int` | `POST points/count` exact:true；异常返 0 |
| `fetch_dashboard_docs` | `()->dict` | 见下 |
| `fetch_starred_docs` | `()->list` | 薄封装 = `fetch_dashboard_docs()["starred"]` |
| `fetch_week_docs` | *保持不变* | 向后兼容 |

`fetch_dashboard_docs()` 单次 scroll 产出两组，给每个 doc 打瞬态标记（下划线前缀，**严禁回写 Qdrant**）：
- `_starred: bool` = `is_starred(d)`
- `_this_week: bool` = `_doc_timestamp(d) >= monday`
- 返回 `{week:[...], starred:[...], monday, now}`；并集 = `_starred or _this_week`。

---

## 4. UI 层（app.py）

- `page_dashboard()` 拆为外壳（标题/日期/Qdrant 探测）+ `@ui.refreshable def dashboard_body()`。
- `_doc_row(d, online)`：★按钮 + 标题(链接预览页) + 👁预览链接。
- `_on_toggle_star(d)`：**async** + `await run.io_bound(set_starred, ...)` + `btn.disable()` 防连点 + `ui.notify` + `dashboard_body.refresh()`。
- ⭐收藏区（前 20 + 计数）置于 📥本周区之上；本周区按 `source_project` 分组逻辑维持原样。
- 熔知 URL 一律走 `settings.citrinitas.endpoint(path)`，禁止硬编码 8080。
- 同步 urllib 调用阻塞事件循环 → 回调必须 async + `await run.io_bound(...)`。

---

## 5. 任务分解

| 任务 | 文件 | 依赖 | 优先级 |
|---|---|---|---|
| T01 数据层 | `core/qdrant_bridge.py` | 无 | P0 |
| T02 UI层（外链熔知 + 本地兜底弹窗；★ 收藏交互；无自建预览页） | `app.py` | T01 | P0 |
| T03 验收脚本 | `acceptance/test_starred_flow.py` | T01（可与 T02 并行）| P1 |
| T04 文档同步 | `CHANGELOG.md` / `BLUEPRINT.md` | T01,T02 | P1 |

### T01 自验（命令行）
```python
from core.qdrant_bridge import *
d = fetch_dashboard_docs()["week"][0]; did = d["doc_id"]
before = [p for p in scroll_payloads() if p["doc_id"]==did]
print(set_starred(did, True))      # ok=True, updated=chunk数
after  = [p for p in scroll_payloads() if p["doc_id"]==did]
assert all(p["stats"]["starred"] for p in after)
assert [p["stats"].get("access_count") for p in before] == [p["stats"].get("access_count") for p in after]
print(set_starred(did, False))     # 还原
print(set_starred("不存在的id", True))  # ok=False, updated=0
```

### T03 验收脚本断言（5 项）
全 chunk 一致 / `access_count` 未丢 / 幂等重复写 / 不存在 doc_id 返 `ok=False` / 跨周收藏能被 `fetch_dashboard_docs()["starred"]` 捞到。脚本必须自我还原（跑完把 starred 改回原值）。

---

## 6. 踩坑清单（工程师必读）
1. set_payload 三要素缺一不可：`?wait=true` + `key:"stats"` + `filter:{doc_id}`。
2. `key:"stats"` 漏写 → stats 整体替换、access_count 永久丢失（不可逆）。
3. Qdrant 对"匹配 0 点"的 set_payload 也返 completed → 必须先 count 区分。
4. payload 按 doc_id 多 chunk → 任何遍历必须 doc_id 去重。
5. `stats` 三层容错，统一走 `is_starred()`，业务代码不要手写 `d["stats"]["starred"]`。
6. `_starred`/`_this_week` 瞬态标记严禁回写 Qdrant。
7. for 循环内绑按钮必须 `lambda d=d:` 默认参数绑定（闭包变量捕获坑）。
8. 局部刷新用 `@ui.refreshable` + `.refresh()`，不用 `ui.update()` 或整页跳转。
9. 写 Qdrant 同步阻塞 → 回调 async + `await run.io_bound(...)`。
10. 点击后先 `btn.disable()` 防连点；失败 `enable()` 且不 refresh。
11. 熔知地址走 `settings.citrinitas.endpoint(path)`，禁硬编码 8080。
12. 依赖零新增：Web 用 nicegui 3.14.0（已装），HTTP 用标准库 urllib（复用 `_post()`），**不要引入 requests/qdrant_client**。

---

## 7. 待确认 / 已知假设
- 超链接走法：**A（外链熔知 8080 + 本地兜底；2026-08-01 下午修订拍板）**。
- 打破只读桥：已作为 AI 设计决策标注，用户需求隐含授权；若用户改主意，回滚方式 = 删 `set_starred` + 收藏按钮改为跳熔知 8080 操作。
- 是否记录"收藏时间"：本期不加（`starred_at` 会污染熔知 schema，须熔知侧拍板）；代价 = 收藏区只能按录入时间排序。
- 本周区是否排除已收藏：默认双显，一行 filter 可改。
