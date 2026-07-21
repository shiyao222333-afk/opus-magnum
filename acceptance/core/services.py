"""验收 harness 服务编排：拉起 / 探活 / 停止三器，以及喂入馏析。

原则（用户裁定）：
  - harness 只负责启动服务 + 喂输入 + 读输出 + 清理，不干涉三器内部逻辑。
  - 验收开关统一为单个环境变量 ACCEPTANCE_KEEP_FILES=1：拉起炼真 / 熔知时带上，
    两器同时受控（炼真保留中转①、熔知保留收件箱原文件），防止中间文件误删；
    验收结束 harness 停掉这两个服务即恢复常态（默认不带该变量 → 正常删除）。「开关式」，不是运行时热切。
  - 方案1（用户裁定）：验收期把炼真 OUTPUT_DIR 重定向到暂存目录（STAGING_DIR，非熔知收件箱），
    使 step④ 的三份中转②绝不被熔知自动摄入；step⑤ 再把选中的那份复制进收件箱触发摄入。
    这样既保留「三器自动」、又不撞熔知内容去重。
  - 轮询间隔按用户裁定：炼真慢 → 5min；馏析 / 熔知快 → 1min。
"""
from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

# ── 三器项目根（可用环境变量覆盖，便于不同机器）──
NIGREDO = Path(os.getenv("NIGREDO_ROOT", r"D:\nigredo"))
ALBEDO = Path(os.getenv("ALBEDO_ROOT", r"D:\albedo"))
CITRINITAS = Path(os.getenv("CITRINITAS_ROOT", r"D:\citrinitas"))

# 端口（探活用）
PORTS = {"nigredo": 8502, "albedo": 8501, "citrinitas": 8080}

# 两个监控文件夹（用户定义的「两个监控文件夹」）
WATCH_DIR = Path(os.getenv("ALBEDO_WATCH_DIR", r"D:\opus-magnum\front_half\transit\nigredo_out"))
INBOX_DIR = Path(os.getenv("KB_INBOX_DIR", r"D:\citrinitas\library\inbox"))
INGEST_LOG = CITRINITAS / "local_data" / "ingest_log.jsonl"

# 炼真输出暂存目录（方案1：验收期重定向炼真 OUTPUT_DIR 到此，避免 step④ 中转②被熔知自动摄入）
STAGING_DIR = Path(os.getenv("ACCEPTANCE_STAGING_DIR", r"D:\opus-magnum\acceptance\_staging\albedo_out"))


def find_python(project: Path) -> str:
    """解析运行某项目的 Python 解释器。

    优先级：
      1. 环境变量 <NAME>_PYTHON（NIGREDO_PYTHON / ALBEDO_PYTHON / CITRINITAS_PYTHON）
         —— 由调用方按本机实际可用解释器传入，解决「项目 venv 为空壳/缺失」的情况。
      2. 项目自带 venv/Scripts/python.exe
      3. 受管 venv
      4. PATH 中的 python
    """
    env_key = {
        NIGREDO: "NIGREDO_PYTHON",
        ALBEDO: "ALBEDO_PYTHON",
        CITRINITAS: "CITRINITAS_PYTHON",
    }.get(project)
    if env_key and os.environ.get(env_key):
        return os.environ[env_key]
    cand = project / "venv" / "Scripts" / "python.exe"
    if cand.exists():
        return str(cand)
    managed = Path(r"C:\Users\Lenovo\.workbuddy\binaries\python\envs\default\Scripts\python.exe")
    if managed.exists():
        return str(managed)
    return "python"


class Service:
    """后台子进程句柄。"""

    def __init__(self, name: str, proc: subprocess.Popen):
        self.name = name
        self.proc = proc

    @property
    def alive(self) -> bool:
        return self.proc.poll() is None

    def stop(self, timeout: int = 10) -> None:
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=timeout)
            except Exception:
                self.proc.kill()


def wait_port(port: int, timeout: int = 120, interval: float = 1.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=2):
                return True
        except OSError:
            time.sleep(interval)
    return False


def ensure_qdrant(timeout: int = 60) -> bool:
    """确保 Qdrant 在 6333 就绪；不在则尝试用 citrinitas 的 helper 启动。"""
    if wait_port(6333, timeout=5):
        return True
    helper = CITRINITAS / "scripts" / "qdrant_helper.ps1"
    if helper.exists():
        try:
            subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(helper)],
                cwd=str(CITRINITAS), timeout=timeout, check=False,
            )
        except Exception as e:  # pragma: no cover
            print(f"[warn] 启动 Qdrant 失败: {e}", file=sys.stderr)
    return wait_port(6333, timeout=timeout)


def start_albedo() -> Service:
    """拉起炼真监控（带验收开关 ACCEPTANCE_KEEP_FILES=1 + 输出重定向到暂存）。

    方案1：把 ALBEDO_OUTPUT_DIR 指向 STAGING_DIR（非熔知收件箱），使 step④ 产出的三份中转②
    绝不会被熔知自动摄入；step⑤ 再把选中的那份复制进收件箱触发摄入，避免内容去重撞车。
    强制 ALBEDO_REQUIRE_HUMAN_REVIEW=false：中转②直接落进 OUTPUT_DIR 根目录。
    ACCEPTANCE_KEEP_FILES=1：保留中转①（改名 .keep），防误删；验收结束停服即恢复。
    """
    py = find_python(ALBEDO)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ,
               ACCEPTANCE_KEEP_FILES="1",
               ALBEDO_OUTPUT_DIR=str(STAGING_DIR),
               ALBEDO_REQUIRE_HUMAN_REVIEW="false")
    proc = subprocess.Popen(
        [py, "-m", "watcher.run"], cwd=str(ALBEDO), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    return Service("albedo", proc)


def start_citrinitas() -> Service:
    """确保 Qdrant 就绪并拉起熔知（带验收开关 ACCEPTANCE_KEEP_FILES=1），探活 8080。

    ACCEPTANCE_KEEP_FILES=1：摄入后保留收件箱原文件，供验收流程读取/复制；验收结束停服即恢复。
    """
    ensure_qdrant()
    py = find_python(CITRINITAS)
    # 验收期放宽守望文件夹单文件处理超时：默认 30s 会掐断 classify(LLM)+embed 步骤，
    # 导致同一份文件被反复超时重入队、第 3 次提交卡死（熔知第3次超时未摄入）。
    # 改为 600s，足够单次摄入完成。仅经环境变量覆盖，不改 citrinitas 源码。
    env = dict(os.environ, ACCEPTANCE_KEEP_FILES="1", KB_WATCH_V2_PROCESS_TIMEOUT="600")
    proc = subprocess.Popen(
        [py, "main.py"], cwd=str(CITRINITAS), env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
    )
    if not wait_port(PORTS["citrinitas"], timeout=120):
        proc.terminate()
        raise RuntimeError("熔知启动超时（端口 8080 未就绪）")
    return Service("citrinitas", proc)


def start_nigredo_ui() -> Service | None:
    """可选：拉起馏析 Streamlit UI（端口 8502）作探活；失败不阻断（处理走 run_queue.py）。"""
    run_bat = NIGREDO / "run.bat"
    if not run_bat.exists():
        return None
    try:
        proc = subprocess.Popen(
            ["cmd", "/c", str(run_bat)], cwd=str(NIGREDO),
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return Service("nigredo", proc)
    except Exception as e:  # pragma: no cover
        print(f"[warn] 馏析 UI 启动失败（不影响处理）: {e}", file=sys.stderr)
        return None


def purge_acceptance_docs(substr: str = "_acc_r") -> int:
    """清理历次验收残留的 Qdrant 测试点。

    验收注入文件命名含 '_acc_r'（如 {bv}_acc_r1.md / {bv}_acc_r1_refined.md）。
    按 payload（序列化为 JSON）含该子串滚动全量点、收集 point id 批量删除，
    避免上一轮 step④ 自动摄入的内容残留导致本轮 step⑤ 撞内容去重。仅删测试数据，不动真实文档。
    返回删除的点数（Qdrant 未就绪时返回 0）。
    """
    # 用标准库 urllib 直连 Qdrant REST，避免依赖未安装的 requests 包。
    import json as _json
    import urllib.error as _uerr
    import urllib.request as _ureq
    qdrant_url = "http://localhost:6333"
    collection = "athanor_v1"
    try:
        if not wait_port(6333, timeout=5):
            return 0

        def _post(path: str, body: dict) -> dict:
            data = _json.dumps(body).encode("utf-8")
            req = _ureq.Request(
                f"{qdrant_url}{path}",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with _ureq.urlopen(req, timeout=30) as resp:
                return _json.loads(resp.read().decode("utf-8"))

        # 滚动全量点（按 next_page_offset 翻页，避免整数 offset 误用）
        point_ids: list = []
        next_offset = None
        while True:
            body = {"limit": 1000, "with_payload": True, "with_vector": False}
            if next_offset is not None:
                body["offset"] = next_offset
            try:
                data = _post(f"/collections/{collection}/points/scroll", body)
            except _uerr.URLError:
                break
            result = data.get("result", {})
            pts = result.get("points", [])
            if not pts:
                break
            for p in pts:
                payload = p.get("payload") or {}
                if substr in _json.dumps(payload, ensure_ascii=False):
                    pid = p.get("id")
                    if pid is not None:
                        point_ids.append(pid)
            next_offset = result.get("next_page_offset")
            if next_offset is None:
                break

        # 批量删除命中的点（每批最多 1000）
        deleted = 0
        for i in range(0, len(point_ids), 1000):
            batch = point_ids[i:i + 1000]
            try:
                _post(f"/collections/{collection}/points/delete", {"points": batch})
                deleted += len(batch)
            except _uerr.URLError:
                pass
        return deleted
    except Exception:
        return 0


def enqueue_nigredo(url: str) -> None:
    """把 URL 写入馏析队列 data/queue.json（去重）。"""
    queue = NIGREDO / "data" / "queue.json"
    items: list = []
    if queue.exists():
        try:
            data = json.loads(queue.read_text(encoding="utf-8"))
            if isinstance(data, list):
                items = data
        except Exception:
            items = []
    if url not in items:
        items.append(url)
    queue.parent.mkdir(parents=True, exist_ok=True)
    queue.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _resolve_short_url(short_url: str) -> str | None:
    """解析 b23.tv / bilibili.tv 短链，跟随重定向返回最终真实 URL。

    优先 HEAD（最轻量），被拒则回退 GET（只读响应头、不下载正文）。
    仅用于从短链拿到含 BV 号的完整地址，不改变任何文件或数据。
    """
    import urllib.error as _uerr
    import urllib.request as _ureq
    if not short_url.startswith(("http://", "https://")):
        short_url = "https://" + short_url
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    for method in ("HEAD", "GET"):
        try:
            req = _ureq.Request(short_url, method=method, headers=headers)
            with _ureq.urlopen(req, timeout=15) as resp:
                return resp.geturl()
        except _uerr.HTTPError as e:
            loc = e.headers.get("Location")
            if loc:
                return loc if loc.startswith(("http://", "https://")) else ("https://bilibili.com" + loc)
            if method == "GET":
                return None
        except Exception:
            if method == "GET":
                return None
    return None


def _extract_bvid(url: str) -> str | None:
    """从 B站 URL 提取 BV 号（如 BV1AbPrzJEba）。

    支持完整 BV 网址（https://www.bilibili.com/video/BVxxx）与
    b23.tv / bilibili.tv 短链（自动解析重定向后再提取）。
    """
    import re
    if "b23.tv" in url or "bilibili.tv" in url:
        resolved = _resolve_short_url(url)
        if resolved:
            url = resolved
    m = re.search(r"(BV[0-9A-Za-z]+)", url)
    return m.group(1) if m else None


def _clear_nigredo_cache_gate(bv_id: str) -> None:
    """清理该视频在馏析缓存里的「非音频残留」与索引条目（兼容 L3 目录拆分前后）。

    L3 前：缓存全在 data/cache/ 根（{bv}.wav/.srt/.txt）。
    L3 后：音频在 data/cache/audio/、字幕在 data/cache/outputs/。
    两种布局都清，保证 download_audio 取到 .wav，且 index.json 不短路。
    仅动缓存生成物（非源码），守铁律。
    """
    cache = NIGREDO / "data" / "cache"
    candidates = []
    if cache.exists():
        candidates += list(cache.glob(f"{bv_id}.*"))          # 旧布局（根）
    audio_dir = cache / "audio"
    out_dir = cache / "outputs"
    if audio_dir.exists():
        candidates += list(audio_dir.glob(f"{bv_id}.*"))
    if out_dir.exists():
        candidates += list(out_dir.glob(f"{bv_id}.*"))
    for f in candidates:
        if f.suffix.lower() != ".wav":
            try:
                f.unlink()
            except OSError:
                pass
    idx = cache / "index.json"
    if idx.exists():
        try:
            data = json.loads(idx.read_text(encoding="utf-8"))
            if bv_id in data:
                data.pop(bv_id, None)
                idx.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass


def run_nigredo(url: str, timeout: int = 1800) -> Path:
    """喂入 URL 并运行 run_queue.py 处理，返回新产出的中转①路径（在 WATCH_DIR）。

    加固（解决 L4 验收实测的两个坑，均不改兄弟项目源码）：
      1. 每次跑前清掉该视频的缓存「非音频残留」+ 索引条目 → 保证 download_audio 取到
         .wav（否则会误取上一次生成的 .srt 字幕当音频，导致 Whisper 解码崩溃）。
      2. 对 Windows 原生段错误 0xC0000005（GPU 加载模型时偶发坏态、需 TDR 驱动复位）
         最多重试 8 次，冷却采用几何退避 12→30→60→120s（总上限约 10 分钟）等 GPU 真正
         复位，而非固定 12s（固定 12s 远短于 TDR 复位，会把偶发坏态放大成必崩）。
      3. 不强制 CUDA_MODULE_LOADING：实测 EAGER 救不活已坏态 GPU、健康 GPU 下 LAZY 同等
         稳定，故保持纯 LAZY（CUDA 默认）。恢复韧性由第 2 点的退避冷却承担。
      4. 失败时把 run_queue.py 内部输出透出，便于排查（之前被 PIPE 吞掉）。
    """
    bv_id = _extract_bvid(url)
    before = {p.name for p in WATCH_DIR.glob("*.md")}
    py = find_python(NIGREDO)
    last_rc = None
    proc = None
    # GPU 稳定性：本机 CUDA 13.2 + WDDM 下，ctranslate2 创建 CUDA context 加载 Whisper
    # 模型时偶发原生段错误(0xC0000005)，GPU 随即进入需 TDR 驱动复位的「坏态」。
    # 实测：EAGER 并不能救活已坏态 GPU（仅降概率），健康 GPU 下 LAZY 与 EAGER 同等稳定；
    # 真正能扛住的是「崩后等待驱动完成 TDR 复位再重试」→ 故采用几何退避冷却，保持纯 LAZY。
    # 0xC0000005 = 3221225477：仅对此错误重试；其它错误直接放弃，避免掩盖真实 bug。
    BACKOFF = [12, 30, 60, 120, 120, 120, 120]   # 各次失败后的冷却秒数；总上限约 10 分钟
    MAX_ATTEMPTS = len(BACKOFF) + 1              # 8 次（含首跑）
    for attempt in range(1, MAX_ATTEMPTS + 1):
        # run_queue.py 是「读取即清空队列」：失败后重试必须重新喂入 URL，否则
        # 重试时队列已空 → 直接「无待处理任务」退出 → 重试失效。故每次尝试前重写队列。
        enqueue_nigredo(url)
        if bv_id:
            _clear_nigredo_cache_gate(bv_id)   # 每次尝试前清残留+索引，保证取到 .wav 并重跑
        proc = subprocess.run(
            [py, "run_queue.py"], cwd=str(NIGREDO), timeout=timeout,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            env=dict(os.environ),
        )
        last_rc = proc.returncode
        if proc.returncode == 0:
            break
        if proc.returncode == 3221225477:
            print(f"[warn] 馏析 run_queue.py 第{attempt}次 GPU 段错误(0xC0000005)，"
                  f"坏态 GPU 需等 TDR 驱动复位", file=sys.stderr)
            if proc.stdout:
                print(proc.stdout, file=sys.stderr)
            if attempt < MAX_ATTEMPTS:
                cooldown = BACKOFF[min(attempt - 1, len(BACKOFF) - 1)]
                print(f"        冷却 {cooldown}s 后重试（几何退避，总上限约 10 分钟）",
                      file=sys.stderr)
                time.sleep(cooldown)
            continue
        break  # 其它错误不重试
    if last_rc != 0:
        if proc and proc.stdout:
            print(proc.stdout, file=sys.stderr)
        raise RuntimeError(f"馏析 run_queue.py 失败 (rc={last_rc})")
    after = [p for p in WATCH_DIR.glob("*.md") if p.name not in before]
    if not after:
        if proc and proc.stdout:
            print(proc.stdout, file=sys.stderr)
        raise RuntimeError("馏析未产出中转①（WATCH_DIR 无新 .md）")
    after.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return after[0]
