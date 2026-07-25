# B站视频端到端验收报告

- 输入网址: https://www.bilibili.com/video/BV1DEKJ6WETH
- 生成时间: 2026-07-25 09:02:53
- 中转①(馏析): 01_nigredo_transit1.md

## 产出文件（共 7 份）
1. `01_nigredo_transit1.md` — 馏析原始产出
2. `02_albedo_refined_r1.md` — 炼真中转②（同输入第1次）
3. `03_albedo_refined_r2.md` — 炼真中转②（同输入第2次）
4. `04_albedo_refined_r3.md` — 炼真中转②（同输入第3次）
5. `05_citrinitas_fields_r1.json` — 熔知 53 字段结果（第1次）
6. `06_citrinitas_fields_r2.json` — 熔知 53 字段结果（第2次）
7. `07_citrinitas_fields_r3.json` — 熔知 53 字段结果（第3次）

## 下一步
本流程仅完成「操作编排」。审核判定（可信度/优点/可照搬步骤/溯源）由以后单独流程负责。

## 执行日志
- === B站视频验收流程启动: https://www.bilibili.com/video/BV1DEKJ6WETH ===
- [2/5] 馏析下载（先于拉起炼真，捕获中转①）…
-   中转①: D:\opus-magnum\front_half\transit\nigredo_out\BV1DEKJ6WETH.md
- [1/5] 拉起炼真 / 熔知（带验收开关 ACCEPTANCE_KEEP_FILES；炼真输出重定向暂存）…
-   [清理] 已清 6 个残留验收注入文件
- [3/5] 炼真 ×3（同输入）…
-   第1次：已注入 01_nigredo_transit1_acc_r1.md，等待炼真产出（≤1800s，每300s探）…
-   第1次：中转② -> 01_nigredo_transit1_acc_r1_refined.md
-   第2次：已注入 01_nigredo_transit1_acc_r2.md，等待炼真产出（≤1800s，每300s探）…
-   第2次：中转② -> 01_nigredo_transit1_acc_r2_refined.md
-   第3次：已注入 01_nigredo_transit1_acc_r3.md，等待炼真产出（≤1800s，每300s探）…
-   第3次：中转② -> 01_nigredo_transit1_acc_r3_refined.md
- [4/5] 熔知 ×3（先随机选 1 份，同一份提交 3 次，记录 53 字段后删除）…
-   选中炼真文件: 01_nigredo_transit1_acc_r3_refined.md（同一份提交 3 次）
-   第1次：已注入 01_nigredo_transit1_acc_r3_refined_acc_r1_20260725-084407.md，等待熔知摄入（≤900s，每60s探）…
-   第1次：doc_id=doc_b7964cb0e939f5c2 已记录字段 -> 05_citrinitas_fields_r1.json
-   第1次：已删除测试数据 doc_id=doc_b7964cb0e939f5c2
-   第2次：已注入 01_nigredo_transit1_acc_r3_refined_acc_r2_20260725-084407.md，等待熔知摄入（≤900s，每60s探）…
-   第2次：doc_id=doc_c7107f0330f4bb28 已记录字段 -> 06_citrinitas_fields_r2.json
-   第2次：已删除测试数据 doc_id=doc_c7107f0330f4bb28
-   第3次：已注入 01_nigredo_transit1_acc_r3_refined_acc_r3_20260725-084407.md，等待熔知摄入（≤900s，每60s探）…
-   第3次：doc_id=doc_fd59dc2ba12622d6 已记录字段 -> 07_citrinitas_fields_r3.json
-   第3次：已删除测试数据 doc_id=doc_fd59dc2ba12622d6
- [5/5] 生成报告 + 清理监控夹残留测试文件…