# 端口规划（Port Map）

> 统一固定，避免项目间端口冲突。所有服务均监听 `127.0.0.1`（本机）。

| 服务 | 端口 | 启动方式 | 说明 |
|------|:----:|----------|------|
| Opus Magnum 总指挥部 | 8500 | `D:\opus-magnum\run.bat` | Streamlit 总仪表盘 |
| Albedo 炼真 | 8501 | `D:\albedo\run.bat` | Streamlit 精炼界面 |
| Nigredo 馏析 | 8502 | `D:\nigredo\run.bat` | Streamlit 采集界面 |
| **前半部分总管 Supervisor** | **8503** | `D:\opus-magnum\front_half\launch.bat` | NiceGUI 流水线入口（新增） |
| Citrinitas 熔知 | 8080 | `D:\citrinitas\run.bat` | NiceGUI 知识库（收件箱 `data/inbox`） |
| Rubedo 凝华 | 8765 | `D:\rubedo\run.bat` | NiceGUI SOP 平台（native=True） |
| Qdrant（熔知向量库） | 6333 | 由 Citrinitas 启动脚本拉起 | 仅本机 |

## 一键启动前半部分

双击 `D:\opus-magnum\front_half\launch.bat`：
1. 先起 Citrinitas（熔知收件箱开始监听，才能入库）
2. 再起 Supervisor（总管界面，贴 B站 链接一键跑流水线）

> 注意：前半部分跑通依赖「熔知收件箱在监听」，所以总启动器强制先起熔知。
