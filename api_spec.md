# Inter-Project API Specification
# OpusMagnum 项目间通信规范

> **本文档定义四人公司各项目之间如何互相调用。**
> 所有项目均实现本文定义的 REST 端点，OpusMagnum 作为总指挥部通过本文定义的客户端调用各项目。

---

## 认证方式

所有接口使用 **API Key 认证**（最简单方案）：

```
Headers:
  X-Api-Key: opus-magnum-local
```

API Key 各项目统一从环境变量 `OPUS_API_KEY` 读取，默认值：`opus-magnum-local`

---

## 端口分配

| 项目 | 端口 | 说明 |
|------|------|------|
| OpusMagnum | `8500` | 总指挥部 |
| Athanor | `8080` | 知识库引擎 (NiceGUI) |
| Alembic | `8502` | 视频→知识提炼 |
| Crucible | `8503` | 矛盾检测 |
| Elixir（远期）| `8504` | 内容发布 |

---

## 公共端点（每个项目都要实现）

### `GET /health`

**用途**：OpusMagnum 检测各项目是否在线

**响应示例**：
```json
{
  "status": "ok",
  "project": "athanor",
  "version": "0.1.0",
  "uptime_seconds": 3600
}
```

---

## Athanor 暴露的端点（供其他项目调用）

### `POST /api/documents/ingest`

**用途**：Alembic 处理完视频后，将文档推入 Athanor 知识库

**请求体**：符合 `document.schema.json`

**响应示例**：
```json
{
  "success": true,
  "doc_id": "a1b2c3d4-...",
  "message": "Document ingested successfully"
}
```

### `GET /api/documents/search`

**用途**：OpusMagnum 快捷搜索知识库

**查询参数**：`?q=关键词&kb_name=default&limit=5`

**响应示例**：
```json
{
  "results": [
    {
      "doc_id": "a1b2c3d4-...",
      "title": "钣金工艺基础",
      "snippet": "折弯半径是...",
      "score": 0.92
    }
  ]
}
```

### `POST /api/contradictions/mark`

**用途**：Crucible 检测完成后，将矛盾标记写入对应文档

**请求体**：符合 `contradiction_report.schema.json`（简化版）

---

## Alembic 暴露的端点

### `POST /api/videos/submit`

**用途**：OpusMagnum 或用户提交视频处理任务

**请求体**：
```json
{
  "url": "https://www.bilibili.com/video/BV1xx411c7mD",
  "priority": "normal"
}
```

**响应示例**：
```json
{
  "task_id": "task_001",
  "status": "pending",
  "message": "Task submitted"
}
```

### `GET /api/videos/{video_id}/status`

**用途**：OpusMagnum 查询处理进度

**响应**：符合 `video_meta.schema.json`

### `GET /api/videos/{video_id}/result`

**用途**：获取处理后的文档（符合 `document.schema.json`）

---

## Crucible 暴露的端点

### `POST /api/scan`

**用途**：OpusMagnum 触发矛盾检测

**请求体**：
```json
{
  "kb_name": "mechanical-design",
  "mode": "full"
}
```

### `GET /api/reports/{report_id}`

**用途**：获取矛盾报告（符合 `contradiction_report.schema.json`）

### `GET /api/reports/latest`

**用途**：获取最新报告摘要

---

## OpusMagnum 暴露的端点（供其他项目回调）

### `POST /api/callbacks/task-update`

**用途**：Alembic 处理进度更新时，主动通知 OpusMagnum

**请求体**：
```json
{
  "task_id": "task_001",
  "status": "completed",
  "output_doc_id": "a1b2c3d4-..."
}
```

### `POST /api/callbacks/contradiction-ready`

**用途**：Crucible 检测完成时，通知 OpusMagnum

---

## 错误处理规范

所有接口统一错误格式：

```json
{
  "error": true,
  "code": "DOC_NOT_FOUND",
  "message": "Document a1b2c3d4 not found in knowledge base",
  "details": { "kb_name": "default" }
}
```

**常用错误码**：

| 错误码 | HTTP 状态码 | 含义 |
|---------|-------------|------|
| `UNAUTHORIZED` | 401 | API Key 错误 |
| `NOT_FOUND` | 404 | 资源不存在 |
| `VALIDATION_ERROR` | 400 | 请求体不符合 Schema |
| `INTERNAL_ERROR` | 500 | 项目内部错误 |
| `PROJECT_OFFLINE` | 503 | 项目未启动 |

---

## 实施路线图

| 阶段 | 内容 | 负责项目 |
|------|------|----------|
| **Phase 1** | Athanor 实现 `/health` + `/api/documents/ingest` | Athanor |
| **Phase 2** | Alembic 实现 `/health` + `/api/videos/submit` + 回调 OpusMagnum | Alembic |
| **Phase 3** | Crucible 实现 `/health` + `/api/scan` | Crucible |
| **Phase 4** | OpusMagnum 实现所有客户端，打通联动 | OpusMagnum |

---

*本文档随项目实施持续更新。各项目实现接口后，在对应行打 ✅。*
