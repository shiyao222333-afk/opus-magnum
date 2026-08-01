"""总管（supervisor）：以无窗口方式启动各服务，定时探活，死了就重启。

这层是解决"进程悄悄死掉"的标准做法（和你用的聊天/云盘/杀毒软件一样的套路）：
一个常驻的总管进程拥有所有子进程，把它们的窗口藏起来，每几秒看一眼还活不活，
谁死了立刻重启，并顺手清理过期的单例锁（修掉之前"单例锁只看数字"的隐患）。
"""

import os
import sys
import time
import threading
import subprocess
import logging

from envutil import clean_env
from health import http_get_json, tcp_port_open, pid_alive, read_lock_pid, read_lock_json
import services as SVC

LOG_DIR = os.path.join(SVC.LAUNCHER_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(os.path.join(LOG_DIR, "supervisor.log"), encoding="utf-8")],
)
log = logging.getLogger("supervisor")

# Windows 无窗口标志：子进程不显示黑框控制台
CREATE_NO_WINDOW = 0x08000000
DETACHED_PROCESS = 0x00000008

MONITOR_INTERVAL = 5.0
# 心跳超时阈值（秒）：锁里的 hb 超过此时长未刷新 → 判定进程僵尸（缺陷 A 根因修复）
HB_STALE_SECS = 60


class Supervisor:
    def __init__(self):
        self.procs = {}                       # key -> subprocess.Popen
        self.status = {}                      # key -> {running, detail, since}
        self.desired = {s["key"]: s.get("enabled_by_default", True) for s in SVC.SERVICES}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        # 连续重启退避：同一服务连续不健康达到上限就停手，避免无限拉起弹窗
        self._fail_count = {}
        self._max_restarts = 5
        for s in SVC.SERVICES:
            self.status[s["key"]] = {"running": False, "detail": "未启动", "since": 0.0}

    # ───────────────────────── 启动 / 停止 ─────────────────────────
    def _hidden_popen(self, cmd, cwd, env, log_name="_spawn.log"):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = subprocess.SW_HIDE
        return subprocess.Popen(
            cmd, cwd=cwd, env=env,
            stdout=open(os.path.join(LOG_DIR, log_name), "a", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            creationflags=CREATE_NO_WINDOW | DETACHED_PROCESS,
            startupinfo=si,
        )

    def log_path(self, key):
        """返回某服务的独立日志文件路径（单服务日志，便于排错）。"""
        return os.path.join(LOG_DIR, f"{key}.log")

    def _spawn(self, svc, suppress_browser=False):
        sp = svc["spawn"]
        env = clean_env()
        # 仅「监控自动重启」场景（suppress_browser=True）抑制弹浏览器，避免崩溃重启反复弹窗；
        # 用户主动启动（双击/托盘启动/重启）一律弹浏览器，满足「合并巨作启动」。
        if suppress_browser:
            env["OM_AUTO_OPEN_BROWSER"] = "0"
        cwd = sp.get("cwd")
        if sp["kind"] == "python":
            cmd = [sp["python"]] + list(sp["args"])
        else:  # powershell
            cmd = ["powershell"] + list(sp["args"])
        log.info("启动 %s: %s (cwd=%s)", svc["name"], " ".join(cmd), cwd)
        return self._hidden_popen(cmd, cwd, env, log_name=f"{svc['key']}.log")

    def _run_pre(self, svc):
        pre = svc.get("pre")
        if not pre:
            return
        try:
            self._hidden_popen(list(pre), svc["spawn"].get("cwd"), clean_env())
            log.info("%s 前置命令已执行", svc["key"])
        except Exception as e:
            log.warning("%s 前置命令失败: %s", svc["key"], e)

    def _clear_one_lock(self, lock_path, key):
        """清理/接管一个锁文件（缺陷 A 根因修复版）。

        判定顺序（统一用「角色 role + 心跳 hb」，不再只认裸 PID）：
          1) 锁里 PID == 本总管跟踪的子进程 → 是我们自己刚写的，保留。
          2) 角色 role 匹配本服务（确系本服务的另一实例，如旧 launcher 残留）
             → 接管：活则强杀，然后删锁。
          3) 角色不匹配（外来进程复用 PID 占用了我们的锁文件）
             → 仅删锁，**绝不误杀外来进程**。
          4) PID 已死（孤儿锁）→ 直接删锁，无需杀。
        """
        info = read_lock_json(lock_path)
        if not info:
            return
        pid = info.get("pid")
        if pid is None:
            return
        owned = self.procs.get(key)
        # 1) 本总管刚拉起的子进程 → 保留
        if owned is not None and pid == owned.pid:
            return
        # 2) 角色匹配本服务（旧实例/旧 launcher 残留）→ 接管
        if info.get("role") == key:
            if pid_alive(pid):
                log.warning("%s 锁 PID %s 为同服务旧实例(角色匹配) → 接管并终止", key, pid)
                try:
                    os.kill(pid, 9)
                except Exception as e:
                    log.warning("终止 %s 失败: %s", pid, e)
                time.sleep(1)
            try:
                os.remove(lock_path)
                log.info("已清理过期锁 %s", lock_path)
            except OSError:
                pass
            return
        # 3) 角色不匹配（外来进程复用 PID 占用锁文件）→ 仅删锁，不杀外来进程
        if pid_alive(pid):
            log.warning("%s 锁 PID %s 角色不符(%s)，疑似外来进程复用 PID → 仅删锁不杀",
                        key, pid, info.get("role"))
        try:
            os.remove(lock_path)
            log.info("已清理过期锁 %s", lock_path)
        except OSError:
            pass

    def _clear_stale_lock(self, svc):
        locks = []
        h = svc.get("health", {})
        if h.get("lock"):
            locks.append(h["lock"])
        if svc.get("takeover_lock"):
            locks.append(svc["takeover_lock"])
        for lk in (svc.get("bootstrap_locks") or []):
            locks.append(lk)
        for lk in locks:
            self._clear_one_lock(lk, svc["key"])

    def start_service(self, key, suppress_browser=False):
        svc = self._by_key(key)
        if svc is None:
            return
        if not svc.get("spawn"):   # 非托盘托管（仅网页托管）的服务，托盘不启动
            return
        with self._lock:
            self._clear_stale_lock(svc)
            proc = self.procs.get(key)
            if proc is not None and proc.poll() is None:
                return  # 已在跑
            try:
                self._run_pre(svc)
                time.sleep(1)
                p = self._spawn(svc, suppress_browser=suppress_browser)
                self.procs[key] = p
                self.status[key] = {"running": True, "detail": "运行中", "since": time.time()}
                self.desired[key] = True
                log.info("%s 已启动 pid=%s", svc["name"], p.pid)
            except Exception as e:
                self.status[key] = {"running": False, "detail": f"启动失败: {e}", "since": time.time()}
                log.error("%s 启动失败: %s", svc["name"], e)

    def stop_service(self, key):
        with self._lock:
            proc = self.procs.get(key)
            if proc is not None and proc.poll() is None:
                log.info("停止 %s pid=%s", key, proc.pid)
                try:
                    proc.terminate()
                except Exception:
                    pass
            self.procs.pop(key, None)
            self.status[key] = {"running": False, "detail": "已停止", "since": time.time()}
            self.desired[key] = False

    def restart_service(self, key):
        self.desired[key] = True
        self.stop_service(key)
        time.sleep(1)
        self.start_service(key)

    def start_all(self):
        # 按依赖深度从小到大启动，避免上游还没好下游就报错。
        # 仅启动 enabled_by_default=True 的服务（rubedo 默认关）。
        enabled = [s for s in SVC.SERVICES
                   if s.get("enabled_by_default", True)
                   and s.get("spawn") and s.get("health")]
        for svc in sorted(enabled, key=lambda s: len(s["depends_on"])):
            self.desired[svc["key"]] = True
            self.start_service(svc["key"])
            time.sleep(2)

    def stop_all(self):
        for key in list(self.procs.keys()):
            self.stop_service(key)

    # ───────────────────────── 探活 / 自愈 ─────────────────────────
    def _is_healthy(self, svc, proc):
        # 启动宽限期：宽限期内一律视为健康，不查、不重启。
        # 核心用途：避免慢启动服务（如 NiceGUI 冷启动要 20~30s 才绑端口）被监控线程
        # 误判「端口无响应」而反复杀掉重来，永远起不来（opus 巨作即此情况）。
        since = self.status[svc["key"]].get("since", 0)
        uptime = time.time() - since
        if uptime < svc.get("grace", 0):
            return True, "启动中(宽限期内不查)"
        ephemeral = svc.get("proc_ephemeral", False)
        if not ephemeral:
            if proc is None or proc.poll() is not None:
                return False, "进程已退出"
        h = svc["health"]
        t = h["type"]
        if t == "tcp":
            ok = tcp_port_open(h["host"], h["port"])
            return ok, "端口通" if ok else "端口无响应"
        if t == "lockpid":
            # 健康第一判据：本总管自己拉起并跟踪的子进程是否还活着。
            # 不再用「锁里 PID 是否等于本进程」来判活（那是缺陷 A 的致死根因）。
            # 注意：不用「心跳超时」判僵尸——下载/语音识别单次处理可能远超心跳窗口，
            # 误杀会打断正常处理。心跳只用于「启动接管」与「单例」判定。
            if proc is not None and proc.poll() is None:
                return True, "运行(本进程存活)"
            # 子进程已退出 → 看锁里是否有一个「外部合法实例」可接管
            info = read_lock_json(h["lock"])
            if info and info.get("role") == svc["key"] and pid_alive(info.get("pid")) \
                    and (time.time() - info.get("hb", 0)) < HB_STALE_SECS:
                return True, "运行(外部实例)"
            return False, "进程已退出"
        if t == "citrinitas":
            since = self.status[svc["key"]].get("since", 0)
            uptime = time.time() - since
            # 启动宽限期内：main.py 还在加载，/health 可能暂未就绪 → 一律视为健康，不重启
            # （否则会在预热期反复重启，导致 watcher 永远拿不到 60s 宽限 → 永不稳）
            if uptime < svc.get("grace", 60):
                return True, "启动中(宽限期内不查)"
            data = http_get_json(h["url"])
            if not data or data.get("status") != "ok":
                return False, "health 异常"
            watcher_alive = data.get("watcher", {}).get("alive", True)
            if not watcher_alive:
                return False, "watcher.alive=false(摄入监视器已死)"
            return True, "运行"
        return True, "运行"

    def monitor_once(self):
        for svc in SVC.SERVICES:
            key = svc["key"]
            # 仅「托盘托管」的服务（声明了 spawn + health）才纳入监控自愈；
            # 纯网页托管的服务（如 drop_watcher，只有 web_visible）托盘不碰，
            # 否则缺 spawn/health 字段会 KeyError。这样未来即便有人把它的
            # enabled_by_default 翻成 True，托盘也不会崩。
            if not svc.get("spawn") or not svc.get("health"):
                continue
            if not self.desired.get(key):
                continue
            proc = self.procs.get(key)
            healthy, detail = self._is_healthy(svc, proc)
            if healthy:
                self.status[key] = {
                    "running": True, "detail": detail,
                    "since": self.status[key].get("since", time.time()),
                }
                self._fail_count[key] = 0
            else:
                self._fail_count[key] = self._fail_count.get(key, 0) + 1
                if self._fail_count[key] > self._max_restarts:
                    # 连续崩超上限：停手，避免无限拉起弹窗；等用户介入（或下次启动重置）
                    if self.status[key].get("detail") != f"已停手(连崩{self._max_restarts}次)":
                        log.error(
                            "%s 连续 %d 次重启仍不健康，已停手不再自动重启。"
                            "请检查该服务日志；从托盘「启动」可手动重试。",
                            svc["name"], self._max_restarts,
                        )
                    self.status[key] = {
                        "running": False,
                        "detail": f"已停手(连崩{self._max_restarts}次)",
                        "since": self.status[key].get("since", time.time()),
                    }
                    continue
                log.warning("%s 不健康(%s)，重启中…(连崩 %d/%d)",
                            svc["name"], detail, self._fail_count[key], self._max_restarts)
                self._clear_stale_lock(svc)
                try:
                    if proc is not None:
                        proc.terminate()
                except Exception:
                    pass
                self.procs.pop(key, None)
                time.sleep(1)
                # 监控触发的自动重启：抑制弹浏览器，避免崩溃重启反复弹窗
                self.start_service(key, suppress_browser=True)

    def run_monitor(self):
        log.info("总管监控线程启动")
        while not self._stop.is_set():
            try:
                self.monitor_once()
            except Exception as e:
                log.error("监控异常: %s", e)
            self._stop.wait(MONITOR_INTERVAL)

    def stop_monitor(self):
        self._stop.set()

    def overall_state(self):
        running = sum(1 for s in SVC.SERVICES if self.desired.get(s["key"]) and self.status[s["key"]]["running"])
        total = sum(1 for s in SVC.SERVICES if self.desired.get(s["key"]))
        return running, total

    def _by_key(self, key):
        for s in SVC.SERVICES:
            if s["key"] == key:
                return s
        return None
