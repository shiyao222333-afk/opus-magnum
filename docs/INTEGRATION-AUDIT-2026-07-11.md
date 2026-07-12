# 整合后 4 项目完整审核报告（2026-07-11）

> 范围：前半部分整合的 4 个项目 —— Opus Magnum（巨作总管）、Nigredo（馏析）、Albedo（炼真）、Citrinitas（熔知）。
> 凝华（Rubedo）本期未整合，仅顺带记录其端口不一致问题。
> 审核维度：目录联接 / 集成骨架 / 端口 / 依赖合规 / 配置正确性 / 健康检查 / git 卫生。

---

## 一句话结论

**集成骨架方向正确、可用**，但存在 **3 个真 bug（P0）会让"总指挥部"显示错、连不上**，外加若干文档/卫生问题。建议优先修 P0-1、P0-3（各一行、零风险），P0-2 避免状态误报也建议做。

> ✅ **状态更新（2026-07-11）**：P0-1 / P0-2 / P0-3 已全部修复（详见 `CHANGELOG.md` 的 `Fixed — 2026-07-11`）。剩余为文档/卫生问题（见下方 P2）与未纳入本次范围的 rubedo 端口错配（8504→实际 8081）。

---

## ✅ 好的方面（先安心）

| 项 | 结论 |
|----|------|
| 三个目录联接（junction） | ✅ 正确指向 `D:\nigredo` / `D:\albedo` / `D:\citrinitas`，且已被 `.gitignore` 正确忽略（不会误进 git） |
| 熔知收件箱 `D:\citrinitas\data\inbox` | ✅ 存在（含 `.gitkeep`），总管投递有真实落点 |
| `github_client.py` 重写（requests 版） | ✅ 类/方法签名与 `dashboard.py` 调用完全对得上，`GitHubClient` / `list_issues` / `list_all_issues` / `get_repo_summary` 均保留，无 token 时优雅降级 |
| 端口实际占用 | ✅ 除下方 P0-1 的配置错配外，各服务监听端口无真实冲突 |
| 熔知健康检查 | ✅ `main.py:107 @app.get("/health")` 存在，能被总指挥部正确识别 |
| 炼真 app 完整性 | ✅ `app.py` + `flows/refine.py` + `core/*` 是真正能跑的完整程序；依赖（streamlit+requests+python-dotenv）自洽够用 |
| LICENSE | ✅ 4 个项目均已有 MIT LICENSE |
| 依赖合规 | ✅ 已清零 AGPL/LGPL（ebooklib→自写 epub_reader；pygithub→requests；chardet→charset_normalizer） |

---

## 🔴 P0 — 真 bug（影响日常使用，建议优先修）

### P0-1：总指挥部里"炼真 Albedo"永远显示离线 / "项目连接器"连不上它

- **现象**：打开 Opus 总指挥部（`http://127.0.0.1:8500`）的「服务状态速览」，炼真亮红灯；「项目连接器」测试炼真 → 失败。
- **根因**：`config/settings.py` 把 Albedo 的地址写成 `8503`（`CRUCIBLE_PORT` 默认值），但 **8503 其实是"前半部分总管 Supervisor"的端口**；炼真自己实际跑在 **8501**（`D:\albedo\run.bat` → `--server.port 8501`）。等于总指挥部去 8503 找炼真，找到的却是总管界面。
- **连带**：`health_check` 探测 `http://localhost:8503/health` → 总管（NiceGUI）没有 `/health` 路由 → 返回非 200 → 判离线。
- **影响**：炼真状态误报 + 连接器失效。
- **修复**：改 `config/settings.py` 第 56-57 行 `CRUCIBLE_PORT`/`CRUCIBLE_URL` 默认值为 `8501`；同步改 `.env.example` 的 `CRUCIBLE_PORT=8503` → `8501`、`CRUCIBLE_URL=http://localhost:8503` → `8501`。（各 1 行，零风险）

### P0-2：总指挥部里"馏析 Nigredo"和"炼真 Albedo"状态灯永远红（哪怕真在跑）

- **现象**：Nigredo / Albedo 明明开着，总指挥部却显示离线。
- **根因**：总指挥部靠问每个项目「你还活着吗」（`GET /health` 接口）来判断。熔知（NiceGUI）手动加了该接口，会回答；但 **Nigredo、Albedo 用的 Streamlit 框架没有这个接口**，不回答 → 被判离线。
- **影响**：统一状态面板对 2/3 子项目失效，误以为没启动。
- **修复（二选一，中等工作量）**：
  1. 改 `core/health_check.py`：先试 `/health`，失败再回退探首页 `/`（Streamlit 运行时首页返回 200）；或
  2. 给 Nigredo / Albedo 各加一个轻量 `/health` 响应（Streamlit 需借助 `st.runtime` 或外部探测，较麻烦，方案 1 更省事）。

### P0-3：`.env.example` 里的 GitHub 仓库名是旧名字（athanor/alembic/crucible），这些仓库根本不存在

- **现象**：照模板新建 `.env` 的人，GitHub 同步（「开发进度」页）全部 404 失败。
- **根因**：模板没跟着改名更新。`settings.py` 的**默认值**已经是正确仓库名（`shiyao222333-afk/citrinitas` 等），但模板写的是已废弃的旧名。
- **影响**：新环境 / 别人拉下来跑不通 GitHub 同步。
- **修复**：改 `.env.example`：
  ```
  ATHANOR_REPO=shiyao222333-afk/citrinitas
  ALEMBIC_REPO=shiyao222333-afk/nigredo
  CRUCIBLE_REPO=shiyao222333-afk/albedo
  OPUSMAGNUM_REPO=shiyao222333-afk/opus-magnum
  ```
  （注意：`github_client.list_all_issues` 内部字典键仍用旧代号 athanor/alembic/crucible，但映射到正确的 `settings.*_repo`，功能不受影响，仅命名气味，低优先级。）

---

## 🟡 P1 — 体验 / 一致性（建议修，不阻塞）

### P1-1：Opus 有两个"启动入口"，都不明显是"整合后的主入口"
- `run.bat`（根目录）→ 开的是**老的总指挥部**（8500，战略雷达/仪表盘）。
- 真正的前半部分总管（8503，贴 B站 链接跑流水线）要用 `front_half\launch.bat`。
- 蓝图/路线图里叫"总管界面"的是 8503，但**主启动器不开它** → 用户双击主启动器得不到整合体验。
- 建议：在 `run.bat` 文案或 README 明确区分两者；或在根目录加一个指向 `front_half\launch.bat` 的入口。

### P1-2：总管界面目前是"空壳"
- `supervisor/orchestrator.py` 三段全是 `TODO(M2)` 占位：贴 B站 链接只打印假进度，不真下载字幕 / 不真精炼 / 不真投递。
- 属预期（M1–M4 还没写），但需向用户明确：现在双击总管界面**不能用真实功能**，只是骨架。

### P1-3：`FLOWCHART.md` 还是旧的
- 仍写 `PyGithub`（已换成 requests）、端口错（Crucible→8503 实为总管；Albedo 写成 8503 而非 8501）。
- 文档与现状不符，易误导。建议随 P0 修复一并更新。

### P1-4：炼真 `run.bat` 依赖检查偏弱
- 只检查 `import streamlit`；若 `requests` / `python-dotenv` 缺失不会触发自动安装（首次能装全，后续若环境缺包会崩）。边缘情况，低优先。

---

## ⚪ P2 — 卫生 / 未提交（建议清理，不影响功能）

| 编号 | 问题 | 处理建议 |
|------|------|----------|
| P2-1 | Nigredo 根目录有个叫 **`nul`** 的垃圾文件（Windows 保留设备名，126 字节，未被 git 跟踪） | 直接删除（`nul` 是 DOS 保留名，任何程序无法正常读写它，几乎肯定是误重定向产生的脏文件） |
| P2-2 | Opus 根目录有 **`D:opus-magnum.workbuddytmp`** 临时目录（未被跟踪） | 清理（WorkBuddy 临时产物） |
| P2-3 | **Citrinitas 有 26+ 文件改了没提交**（含 `config/settings.py`、`doc_manager.py`、`ingest_pipeline.py`、`pages/*`、`search_engine/*`、`services/*` 等）——这是你之前自己的开发，不是本次 M0-5 改的 | 建议先 `git commit` / 备份，避免丢失或与其他改动混淆 |
| P2-4 | 4 个项目均有未提交改动 + 新增 LICENSE，均未推到 GitHub | 建议做一次统一提交 + 推送 |
| P2-5 | 凝华（Rubedo）端口三处不一致：`settings.py` 写 8504 / `PORTS.md` 写 8081 / 记忆写 8765 | 本期未整合，仅记录；待阶段 2 接入时统一 |

---

## 建议下一步（待你确认）

1. **修 P0-1 + P0-3**（各 1 行配置，零风险）→ 立刻消除状态误报与连接器失效。
2. **修 P0-2**（改 `health_check` 回退探首页）→ 让状态面板对 3 个子项目都准。
3. **清理 P2-1 / P2-2** 垃圾文件；**P2-3 / P2-4** 做一次提交。
4. **更新 P1-3 `FLOWCHART.md`** 随 P0 一并改。
5. 总管界面真实功能（M1–M4）另行开工。

> 问：要我现在动手修 P0-1 / P0-3（最安全的两处）吗？还是连 P0-2 一起做？
