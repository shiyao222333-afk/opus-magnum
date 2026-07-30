# 端口规划（Port Map）

> 统一固定，避免项目间端口冲突。所有服务均监听 `127.0.0.1`（本机）。

| 服务 | 端口 | 启动方式 | 说明 |
|------|:----:|----------|------|
| Opus Magnum 总指挥部 | 8501 | `D:\opus-magnum\run.bat` | NiceGUI 单页（周看板 / 摄入入口 / 总指挥部） |
| Albedo 炼真 | 无（无头常驻） | `D:\albedo\run.bat` | 监控中转目录轮询，无 Web 端口（`.watcher.pid` 单实例锁） |
| Nigredo 馏析 | 无（无头常驻） | `D:\nigredo\run.bat` | 队列消费器，无 Web 端口（`data/queue_consumer.lock` 单实例锁） |
| Citrinitas 熔知 | 8080 | `D:\citrinitas\run.bat` | NiceGUI 知识库（收件箱 `data/inbox`） |
| Rubedo 凝华 | 8765 | `D:\rubedo\run.bat` | NiceGUI SOP 平台（native=True） |
| Qdrant（熔知向量库） | 6333 | 由 Citrinitas 启动脚本拉起 | 仅本机 |

> 注：原 Streamlit 网页与独立 Supervisor(:8503) 已退役；摄入功能并入巨作「📥 摄入入口」标签页。馏析 / 炼真改为无头常驻，不再占用 8502 / 8501 端口。

## 一键启动前半部分

双击 `D:\opus-magnum\start_all.bat`（或 `front_half\launch.bat`）：
1. 先起 Citrinitas（熔知收件箱开始监听，才能入库）
2. 再起 馏析 / 炼真（无头常驻） + 巨作（:8501）

> 注意：前半部分跑通依赖「熔知收件箱在监听」，所以总启动器强制先起熔知。
