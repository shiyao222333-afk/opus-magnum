"""B站视频端到端验收流程（馏析 → 炼真 → 熔知）。

仅负责「操作编排」，不做审核判定。严格按用户规定的 6 步：
  ① 两监控文件夹改开关式防误删（由 harness 拉起时带环境变量实现，验收后不带即恢复）
  ② 不干涉三器工作，只管输入输出；三器各自 watcher 自动进行
  ③ 给 B站网址 → 馏析出文件1（中转①）
  ④ 同输入提交炼真 3 次，保存 3 份中转②
  ⑤ 任选 1 份炼真文件提交熔知 3 次，每次记录 53 字段结果后删测试数据
  ⑥ 共 7 份文件

产出（验收专用目录 acceptance/runs/<stamp>/）：
  01_nigredo_transit1.md          中转①（馏析原始产出）
  02_03_04_albedo_refined_rN.md   3 份中转②（炼真产出，同输入）
  05_06_07_citrinitas_fields_rN.json  3 份熔知 53 字段结果
  run_report.md                   人读汇总

轮询间隔（用户裁定）：炼真 300s / 馏析·熔知 60s。
"""
from __future__ import annotations

import shutil
import subprocess
import time
from pathlib import Path

from ..core.services import (
    WATCH_DIR, INBOX_DIR, INGEST_LOG, CITRINITAS,
    find_python, start_albedo, start_citrinitas, start_nigredo_ui,
    run_nigredo,
)
from ..core.polling import poll_new_file, poll_ingest_log
from ..core.registry import register

# 轮询间隔（用户裁定）
ALBEDO_INTERVAL = 300   # 炼真慢
FAST_INTERVAL = 60      # 馏析 / 熔知快

# 单步超时
NIGREDO_TIMEOUT = 1800
ALBEDO_TIMEOUT = 1800
CITRINITAS_TIMEOUT = 600


@register("bilibili_video")
class BilibiliVideoFlow:
    name = "bilibili_video"

    def __init__(self, out_dir):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log: list[str] = []

    def _say(self, msg: str) -> None:
        print(msg)
        self.log.append(msg)

    # ───────────────────────── 主流程 ─────────────────────────
    def run(self, url: str) -> dict:
        self._say(f"=== B站视频验收流程启动: {url} ===")

        # 【步骤③】先馏析，趁炼真未启动立即捕获中转①（避免被炼真改名 .keep）
        self._say("[2/5] 馏析下载（先于拉起炼真，捕获中转①）…")
        nigredo_ui = start_nigredo_ui()  # 可选：UI 探活，失败不阻断
        transit1 = run_nigredo(url, timeout=NIGREDO_TIMEOUT)
        self._say(f"  中转①: {transit1}")
        local_transit = self.out_dir / "01_nigredo_transit1.md"
        shutil.copy(transit1, local_transit)

        # 【步骤①】拉起炼真 / 熔知（带验收开关；此步后才开始自动处理）
        self._say("[1/5] 拉起炼真 / 熔知（带验收开关 ALBEDO_KEEP_INPUT / KB_KEEP_INBOX）…")
        albedo_svc = start_albedo()
        citrinitas_svc = start_citrinitas()

        try:
            # 【步骤④】炼真 ×3（同输入）
            self._say("[3/5] 炼真 ×3（同输入）…")
            refined_paths: list[Path] = []
            seen_inbox = {p.name for p in INBOX_DIR.glob("*_refined.md")}
            bv = local_transit.stem
            for r in range(1, 4):
                inj = WATCH_DIR / f"{bv}_acc_r{r}.md"
                shutil.copy(local_transit, inj)
                self._say(f"  第{r}次：已注入 {inj.name}，等待炼真产出（≤{ALBEDO_TIMEOUT}s，每{ALBEDO_INTERVAL}s探）…")
                out = poll_new_file(
                    INBOX_DIR, seen_inbox, timeout=ALBEDO_TIMEOUT,
                    interval=ALBEDO_INTERVAL, pattern="*_refined.md",
                )
                if out is None:
                    raise TimeoutError(f"炼真第{r}次超时未产出中转②")
                shutil.copy(out, self.out_dir / f"0{r + 1}_albedo_refined_r{r}.md")
                refined_paths.append(out)
                self._say(f"  第{r}次：中转② -> {out.name}")

            # 【步骤⑤】熔知 ×3（同一炼真文件，每次记录 53 字段后删测试数据）
            self._say("[4/5] 熔知 ×3（同一炼真文件，记录 53 字段后删除）…")
            chosen = self.out_dir / "02_albedo_refined_r1.md"  # 任选第 1 份
            if not chosen.exists():
                chosen = refined_paths[0]
            field_files: list[Path] = []
            pos_holder = [INGEST_LOG.stat().st_size if INGEST_LOG.exists() else 0]
            py = find_python(CITRINITAS)
            for r in range(1, 4):
                inj = INBOX_DIR / f"{chosen.stem}_acc_r{r}.md"
                shutil.copy(chosen, inj)
                self._say(f"  第{r}次：已注入 {inj.name}，等待熔知摄入（≤{CITRINITAS_TIMEOUT}s，每{FAST_INTERVAL}s探）…")
                doc_id = poll_ingest_log(
                    INGEST_LOG, pos_holder, timeout=CITRINITAS_TIMEOUT,
                    interval=FAST_INTERVAL, match_source=inj.name,
                )
                if doc_id is None:
                    raise TimeoutError(f"熔知第{r}次超时未摄入（doc_id 未出现）")
                # 记录 53 字段
                out_json = self.out_dir / f"0{r + 4}_citrinitas_fields_r{r}.json"
                subprocess.run(
                    [py, "scripts/get_fields.py", doc_id, "--out", str(out_json)],
                    cwd=str(CITRINITAS), check=True,
                )
                field_files.append(out_json)
                self._say(f"  第{r}次：doc_id={doc_id} 已记录字段 -> {out_json.name}")
                # 删测试数据
                subprocess.run([py, "scripts/delete_doc.py", doc_id], cwd=str(CITRINITAS), check=True)
                self._say(f"  第{r}次：已删除测试数据 doc_id={doc_id}")

            # 【步骤⑥】报告 + 清理
            self._say("[5/5] 生成报告 + 清理监控夹残留测试文件…")
            self._write_report(url, local_transit, refined_paths, field_files)
            self._cleanup_watch(bv, chosen.stem)
            if nigredo_ui is not None:
                nigredo_ui.stop()
            return {"ok": True, "out_dir": str(self.out_dir),
                    "files": [str(p) for p in [local_transit, *refined_paths, *field_files]]}
        finally:
            albedo_svc.stop()
            citrinitas_svc.stop()

    # ───────────────────────── 辅助 ─────────────────────────
    def _write_report(self, url, transit1, refined_paths, field_files) -> None:
        lines = [
            "# B站视频端到端验收报告",
            "",
            f"- 输入网址: {url}",
            f"- 生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"- 中转①(馏析): {transit1.name}",
            "",
            "## 产出文件（共 7 份）",
            "1. `01_nigredo_transit1.md` — 馏析原始产出",
        ]
        for i, p in enumerate(refined_paths, 1):
            lines.append(f"{i + 1}. `0{i + 1}_albedo_refined_r{i}.md` — 炼真中转②（同输入第{i}次）")
        for i, p in enumerate(field_files, 1):
            lines.append(f"{i + 4}. `0{i + 4}_citrinitas_fields_r{i}.json` — 熔知 53 字段结果（第{i}次）")
        lines += [
            "",
            "## 下一步",
            "本流程仅完成「操作编排」。审核判定（可信度/优点/可照搬步骤/溯源）由以后单独流程负责。",
            "",
            "## 执行日志",
        ]
        lines += [f"- {m}" for m in self.log]
        (self.out_dir / "run_report.md").write_text("\n".join(lines), encoding="utf-8")

    def _cleanup_watch(self, bv: str, chosen_stem: str) -> None:
        """清理本次注入的测试文件（保留原中转①的 .keep 安全备份，绝不删原始数据）。

        删除模式仅限本次注入的 `*_acc_r*.md`（在 WATCH_DIR 与 INBOX_DIR）。
        """
        removed = []
        for d in (WATCH_DIR, INBOX_DIR):
            for pat in (f"{bv}_acc_r*.md", f"{chosen_stem}_acc_r*.md"):
                for p in d.glob(pat):
                    try:
                        p.unlink()
                        removed.append(str(p))
                    except Exception as e:
                        self._say(f"  [清理跳过] {p.name}: {e}")
        if removed:
            self._say(f"  已清理 {len(removed)} 个测试注入文件（原中转① .keep 保留）")
