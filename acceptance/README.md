# 巨作验收 harness（acceptance）

端到端验收的**操作编排**工具。代码归属巨作项目（OpusMagnum）。

> ⚠️ 本 harness **只做操作部分**（拉起服务 / 喂输入 / 读输出 / 清理），**不做审核判定**。
> 审核（这条内容可信吗、优点是什么、能照搬哪几步、来源追到哪）由以后单独的流程负责。
> 流程的权威逐字标准见 `STANDARD_FLOW.md`，本文件与其须保持一致。

---

## 它解决什么

验收一条「B站视频 → 馏析 → 炼真 → 熔知」的链路时，手动操作容易漏步骤、误删中间文件。
本工具把整套操作自动化，并且用「开关式」保护中间文件：

- 拉起炼真 / 熔知时，带**单个**环境变量 **`ACCEPTANCE_KEEP_FILES=1`**
  → 两器同时受控：炼真不把中转①移走、熔知不删中转②，防止误删。
- 平时不带该变量（用 `start_all.bat` 等）→ 原行为恢复。**开关式，不是运行时热切；验收结束 harness 停服即恢复。**

---

## 已注册流程

| 流程名 | 覆盖链路 | 产出 |
|--------|----------|------|
| `bilibili_video` | 馏析 → 炼真 → 熔知（B站视频） | 7 份文件（见下） |

未来新增别的流程：在 `acceptance/flows/` 下新建流程类，用 `@register("名")` 装饰即可，CLI 自动识别。

---

## bilibili_video 流程：7 份文件

严格按用户规定的 6 步：

1. 两监控文件夹改开关式防误删（拉起时带环境变量实现）。
2. 不干涉三器工作，只管输入输出；三器各自 watcher 自动进行。
3. 给 B站网址 → 馏析出**文件1**（中转①）。
4. 同输入提交炼真 **3 次** → 保存 **3 份中转②**（文件2/3/4）。
5. 先从 3 份炼真文件中**随机选 1 份（选一次）**，把**同一份**提交熔知（共 3 次），每次记录 **53 字段结果**后删测试数据 → **3 份字段文件**（文件5/6/7）。
6. 共 **7 份文件**。

产出目录：`acceptance/runs/<时间戳>_<BV>/`

```
01_nigredo_transit1.md          中转①（馏析原始产出）
02_albedo_refined_r1.md         中转②（炼真，同输入第1次）
03_albedo_refined_r2.md         中转②（炼真，同输入第2次）
04_albedo_refined_r3.md         中转②（炼真，同输入第3次）
05_citrinitas_fields_r1.json    熔知 53 字段结果（第1次摄入）
06_citrinitas_fields_r2.json    熔知 53 字段结果（第2次摄入）
07_citrinitas_fields_r3.json    熔知 53 字段结果（第3次摄入）
run_report.md                   人读汇总（含执行日志）
```

> 53 字段结果 = 直接 dump 该文档在 Qdrant 中的**全部顶层 payload 字段真实值**（不手抄清单），
> 由 `citrinitas/scripts/get_fields.py` 导出。

轮询间隔（按用户裁定）：炼真慢 → **5 分钟**探一次；馏析 / 熔知快 → **1 分钟**探一次。

---

## 怎么跑

**前置**（一次性确认）：
- 以**管理员身份**打开终端（与三器一致，因熔知/馏析启动涉及端口清理/提权）。
- 三器依赖已装（各自 `venv`）。`acceptance/core/services.py` 的 `find_python()` 默认用
  `<项目>/venv/Scripts/python.exe`；若你的 venv 路径不同，改这里或用环境变量
  `NIGREDO_ROOT` / `ALBEDO_ROOT` / `CITRINITAS_ROOT` 覆盖项目根。
- 显卡可用（炼真推理需 GPU）。

**运行**：
```bat
cd D:\opus-magnum
python -m acceptance.cli run --flow bilibili_video --url "https://www.bilibili.com/video/BVxxxx"
```

查看已注册流程：
```bat
python -m acceptance.cli list
```

---

## 清理与副作用

- 流程结束会自动清理本次注入的测试文件（`*_acc_r*.md`，在炼真监控夹与熔知收件箱）。
- **原中转①的 `.keep` 安全备份保留**（这就是「防误删」的意义），不会被删。
- 熔知摄入的测试数据在每次记录字段后**立即删除**（`citrinitas/scripts/delete_doc.py`）。

---

## 已知风险（L4 真机验收时留意）

1. **熔知内容去重**：方案1 下，step④ 中转②落暂存、不进收件箱，故 step⑤ 提交同一份 3 次时，每轮记录字段后**立即删除该测试 doc**（清掉 `content_hash`），下一轮同内容可再次摄入，不会因去重卡住。
2. **路径耦合**：中转①必须落在炼真 `WATCH_DIR`（默认 `D:\opus-magnum\front_half\transit\nigredo_out`），依赖馏析 `OUTPUT_DIR` 与之相等。若你改过任一边路径，需同步环境变量或默认值。
3. **耗时**：真实 B站视频需下载 + 炼真 GPU 推理 + 三次摄入，单轮可能数十分钟；超时阈值在 `flows/bilibili_video.py` 顶部可调。
