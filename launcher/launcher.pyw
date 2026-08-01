# -*- coding: utf-8 -*-
"""巨作 Opus Magnum 启动器（系统托盘版）。

双击「启动巨作.bat」即可：托盘出现一个图标，后台服务（馏析/炼真/熔知/凝华）
以无窗口方式启动，由总管自动看护。图标颜色一眼看状态：
  绿 = 全部运行 / 黄 = 部分运行 / 红 = 全部停了 / 灰 = 未启动。
右键菜单可启停、重启单个服务、打开界面、查看日志、退出。
托盘主图标是 2x2 四色方框拼图（每格 = 一个炼金项目，亮=在跑、暗=没跑），
外框颜色表示整体健康度——这就是“带颜色的方框”。
"""

import os
import webbrowser
import threading
import time

from PIL import Image, ImageDraw
import pystray
from pystray import Menu, MenuItem

import services as SVC
from supervisor import Supervisor

SUP = Supervisor()

COLORS = {
    "green": (46, 204, 113, 255),
    "yellow": (241, 196, 15, 255),
    "red": (231, 76, 60, 255),
    "gray": (149, 165, 166, 255),
}


def _bright(col):
    """色块是否偏亮（白/金黄），用于决定描边颜色以保证在托盘上可见。"""
    return col[0] > 180 and col[1] > 180 and col[2] > 180


def make_grid_icon(status_map):
    """主图标：2x2 四色方框拼图，每格 = 一个炼金项目，亮=在跑、暗=没跑；外框表整体健康度。"""
    W = 64
    img = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # 2x2 格子固定顺序：左上=馏析(黑) 右上=炼真(白) 左下=熔知(黄) 右下=凝华(红)
    cells = {
        "nigredo": (4, 4),
        "albedo": (34, 4),
        "citrinitas": (4, 34),
        "rubedo": (34, 34),
    }
    cell = 26
    phase_svcs = {s["key"]: s for s in SVC.SERVICES if s.get("is_phase")}
    running_total = 0
    present_total = 0
    for key, (x, y) in cells.items():
        if key in phase_svcs:
            present_total += 1
            svc = phase_svcs[key]
            on = status_map.get(key, {}).get("running", False)
            if on:
                running_total += 1
            col = svc["color"] if on else (60, 60, 60, 255)
            outline = (110, 110, 110, 230) if _bright(col) else (0, 0, 0, 170)
        else:
            col = (45, 45, 45, 255)        # 该项目未纳入总管：画一个暗灰占位格
            outline = (70, 70, 70, 200)
        d.rectangle([x, y, x + cell, y + cell], fill=col, outline=outline, width=1)
    # 外框颜色 = 整体健康度
    if present_total == 0:
        frame = COLORS["gray"]
    elif running_total == present_total:
        frame = COLORS["green"]
    elif running_total == 0:
        frame = COLORS["red"]
    else:
        frame = COLORS["yellow"]
    d.rectangle([2, 2, W - 3, W - 3], outline=frame, width=3)
    return img


def refresh_icon(icon):
    try:
        icon.icon = make_grid_icon(SUP.status)
        running, total = SUP.overall_state()
        icon.title = f"巨作 Opus Magnum — {running}/{total} 服务运行中"
    except Exception:
        pass


def _act_start_all(icon, item):
    SUP.start_all()


def _act_stop_all(icon, item):
    SUP.stop_all()


def _act_restart(key):
    def _f(icon, item):
        SUP.restart_service(key)
    return _f


def _act_stop(key):
    def _f(icon, item):
        SUP.stop_service(key)
    return _f


def _act_start(key):
    def _f(icon, item):
        SUP.start_service(key)
    return _f


def open_url(url):
    """单独打开某一个服务的网页/界面（只开一个，不一次全开）。"""
    def _f(icon, item):
        webbrowser.open(url)
    return _f


def open_service_log(key):
    """打开某一个服务的独立日志文件（单服务日志，便于排错）。"""
    def _f(icon, item):
        path = SUP.log_path(key)
        target = path if os.path.exists(path) else os.path.join(SVC.LAUNCHER_DIR, "logs")
        try:
            os.startfile(target)
        except Exception:
            pass
    return _f


def open_logs(icon, item):
    os.startfile(os.path.join(SVC.LAUNCHER_DIR, "logs"))


def quit_app(icon, item):
    SUP.stop_all()
    SUP.stop_monitor()
    icon.stop()


def build_menu():
    items = [
        MenuItem("▶ 启动全部", _act_start_all),
        MenuItem("■ 停止全部", _act_stop_all),
        Menu.SEPARATOR,
    ]
    # 每个服务的启停子菜单（启动 / 停止 / 重启）
    for svc in SVC.SERVICES:
        if svc.get("menu_visible") is False:
            continue
        key = svc["key"]
        st = SUP.status.get(key, {})
        dot = "●" if st.get("running") else "○"
        label = f"{dot} {svc['name']}  —  {st.get('detail', '')}"
        sub = Menu(
            MenuItem("启动", _act_start(key)),
            MenuItem("停止", _act_stop(key)),
            MenuItem("重启", _act_restart(key)),
        )
        items.append(MenuItem(label, sub))
    items.append(Menu.SEPARATOR)

    # ③ 单独打开某服务的界面（只开一个，不一次全开）
    #   巨作入口(8501) 现在已是受管服务(见 services.py)，由下面循环自动列出
    open_items = []
    for svc in SVC.SERVICES:
        if svc.get("menu_visible") is False:
            continue
        if svc.get("ui"):
            name = svc["name"].split("（")[0].strip()
            open_items.append(MenuItem(f"{name} ({svc['ui']})", open_url(svc["ui"])))
    items.append(MenuItem("🌐 单独打开界面", Menu(*open_items)))

    # ② 单服务日志（点开直接看某个服务的独立日志文件，便于排错）
    log_items = [
        MenuItem("📂 查看全部日志", open_logs),
    ]
    for svc in SVC.SERVICES:
        if svc.get("menu_visible") is False:
            continue
        key = svc["key"]
        name = svc["name"].split("（")[0].strip()
        log_items.append(MenuItem(f"📄 {name} 日志", open_service_log(key)))
    items.append(MenuItem("📂 单服务日志", Menu(*log_items)))

    items.append(MenuItem("⏏ 退出", quit_app))
    return Menu(*items)


def ticker(icon):
    while True:
        try:
            refresh_icon(icon)
            icon.menu = build_menu()
        except Exception:
            pass
        time.sleep(3)


def main():
    icon = pystray.Icon("opus_magnum", make_grid_icon({}), "巨作 Opus Magnum")
    icon.menu = build_menu()

    # 先同步拉起全部服务，再启动监控线程——
    # 避免监控首轮在 start_all 未完成时把「尚未拉起」误判为「已退出」而双拉服务
    # （缺陷 A 家族：启动竞态 → 双实例 → 角色锁接管 SIGKILL → 内部队列锁孤儿 → 崩溃循环）
    SUP.start_all()
    threading.Thread(target=SUP.run_monitor, daemon=True).start()

    threading.Thread(target=ticker, daemon=True).start()

    icon.run()


if __name__ == "__main__":
    main()
