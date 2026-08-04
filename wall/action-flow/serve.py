# -*- coding: utf-8 -*-
"""
serve.py — 陈列架（知识→行动回流系统 · 第6类管理台）
职责：把 weekly/ 下最新的周清单 md 渲染成网页，供 Dashy 内嵌展示；
     每条行动项若带 doc_id，渲染「第6类管理栏」：★收藏 / 📅工作流阶段 / 📦归档，
     点击直接写熔知（stats.starred / lifecycle / is_archived），复用 mark_status.py 逻辑。
模板固定只换内容：每次请求自动读最新清单，代码永不改动。

用法：python serve.py [--port 5100]
"""
import argparse
import glob
import html
import json
import os
import re
import sys
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEEKLY_DIR = os.path.join(BASE_DIR, "weekly")

# 复用 mark_status 的 Qdrant 写入/读回/记账本逻辑（同目录，架构边界一致）
sys.path.insert(0, BASE_DIR)
import mark_status as MS  # noqa: E402

# lifecycle 六档中文显示（与熔知 LIFECYCLE_OPTIONS 对齐）
LIFECYCLE_LABELS = {
    "idea": "💡 想法",
    "draft": "📝 草稿",
    "in_progress": "🔧 进行中",
    "review": "🔍 评审",
    "published": "📤 已发布",
    "archived": "🗄️ 已归档",
}
LIFECYCLE_STAGES = list(LIFECYCLE_LABELS.keys())

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>📋 行动清单</title>
<style>
  body {{ font-family: "Microsoft YaHei", sans-serif; background: #17181c; color: #e8e8ec;
         margin: 0; padding: 24px 16px; }}
  .container {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ font-size: 22px; border-bottom: 1px solid #3a3b42; padding-bottom: 10px; }}
  h2 {{ font-size: 17px; margin-top: 28px; color: #ffd866; }}
  h3 {{ font-size: 14px; margin-top: 18px; color: #9cdcfe; }}
  p {{ line-height: 1.7; font-size: 14px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin: 8px 0; line-height: 1.6; font-size: 14px; }}
  blockquote {{ border-left: 3px solid #5a5b63; margin: 8px 0; padding: 4px 12px;
               color: #9a9ba3; background: #1f2025; border-radius: 0 6px 6px 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }}
  th, td {{ border: 1px solid #3a3b42; padding: 8px 10px; text-align: left; }}
  th {{ background: #26272d; }}
  input[type=checkbox] {{ margin-right: 8px; accent-color: #ffd866; }}
  .tag {{ display:inline-block; margin-right:6px; }}
  .hot {{ color: #ff9e3d; font-weight: bold; }}
  li.done {{ color: #6a6b73; text-decoration: line-through; }}
  strong {{ color: #f0f0f4; }}
  hr {{ border: none; border-top: 1px solid #3a3b42; margin: 24px 0; }}
  .meta {{ color: #7a7b83; font-size: 12px; margin-bottom: 16px; }}
  .act {{ margin: 6px 0 2px 0; font-size: 12px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap; }}
  .act button {{ background: #26272d; color: #e8e8ec; border: 1px solid #3a3b42; border-radius: 6px;
                 padding: 3px 10px; cursor: pointer; font-size: 12px; }}
  .act button:hover {{ border-color: #ffd866; color: #ffd866; }}
  .act button.on {{ background: #4a3f1a; border-color: #d4af37; color: #ffd866; }}
  .act select {{ background: #26272d; color: #e8e8ec; border: 1px solid #3a3b42; border-radius: 6px;
                 padding: 3px 6px; font-size: 12px; }}
  .act .st {{ color: #7a7b83; font-size: 11px; }}
  .act .busy {{ opacity: .5; pointer-events: none; }}
  .toast {{ position: fixed; top: 16px; right: 16px; background: #26272d; border: 1px solid #3a3b42;
            color: #ffd866; padding: 8px 14px; border-radius: 8px; font-size: 13px; display: none; z-index: 99; }}
</style>
</head>
<body><div class="container">{content}</div>
<div class="toast" id="toast"></div>
<script>
const LC = {lc_labels};
function toast(msg) {{
  const t = document.getElementById('toast');
  t.textContent = msg; t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 2200);
}}
async function api(path, body) {{
  const r = await fetch(path, {{
    method: 'POST',
    headers: {{ 'Content-Type': 'application/json' }},
    body: JSON.stringify(body),
  }});
  return r.json();
}}
async function refreshAll() {{
  const rows = document.querySelectorAll('[data-did]');
  const ids = [...new Set([...rows].map(r => r.dataset.did))];
  if (!ids.length) return;
  const res = await api('/api/status', {{ doc_ids: ids }});
  if (!res.ok) return;
  const st = res.states || {{}};
  for (const row of rows) {{
    const did = row.dataset.did;
    const s = st[did] || {{}};
    const star = row.querySelector('.act-star');
    const lcSel = row.querySelector('.act-lc');
    const arch = row.querySelector('.act-arch');
    if (star) {{
      star.textContent = s.starred ? '★ 已收藏' : '☆ 收藏';
      star.classList.toggle('on', !!s.starred);
      star.dataset.next = s.starred ? 'unstar' : 'star';
    }}
    if (lcSel) lcSel.value = s.lifecycle || '';
    if (arch) {{
      arch.textContent = s.is_archived ? '↺ 还原' : '📦 归档';
      arch.dataset.next = s.is_archived ? 'unarchive' : 'archive';
    }}
  }}
}}
async function doAction(btn) {{
  const row = btn.closest('[data-did]');
  const did = row.dataset.did;
  const action = btn.dataset.next;
  const value = btn.dataset.value || '';
  btn.classList.add('busy');
  const res = await api('/api/action', {{ doc_id: did, action, value }});
  btn.classList.remove('busy');
  toast(res.ok ? '✅ ' + res.msg : '❌ ' + (res.msg || '操作失败'));
  refreshAll();
}}
document.addEventListener('click', e => {{
  const btn = e.target.closest('.act-star, .act-arch');
  if (btn) doAction(btn);
}});
document.addEventListener('change', e => {{
  const sel = e.target.closest('.act-lc');
  if (!sel) return;
  const row = sel.closest('[data-did]');
  sel.classList.add('busy');
  api('/api/action', {{ doc_id: row.dataset.did, action: 'lifecycle', value: sel.value }}).then(res => {{
    sel.classList.remove('busy');
    toast(res.ok ? '✅ ' + res.msg : '❌ ' + (res.msg || '操作失败'));
    refreshAll();
  }});
}});
refreshAll();
</script>
</body></html>
"""


def render_inline(text):
    """行内格式：粗体 / 行内代码 / 🔥市场验证高亮"""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"🔥市场验证：[^|]+", lambda m: f'<span class="hot">{m.group(0)}</span>', text)
    return text


def action_bar_html(doc_id):
    """第6类管理栏：★收藏 / 📅阶段 / 📦归档（状态由前端 JS 查询填充）"""
    opts = "".join(
        f'<option value="{k}">{v}</option>' for k, v in LIFECYCLE_LABELS.items()
    )
    return (
        f'<div class="act" data-did="{html.escape(doc_id)}">'
        f'<button class="act-star" data-next="star">☆ 收藏</button>'
        f'<select class="act-lc" title="工作流阶段（第6类）">'
        f'<option value="">— 阶段 —</option>{opts}</select>'
        f'<button class="act-arch" data-next="archive">📦 归档</button>'
        f'</div>'
    )


def md_to_html(md_text):
    """极简 markdown → HTML（只支持本模板用到的语法；行动项带 doc_id 时追加第6类管理栏）"""
    lines = md_text.splitlines()
    out = []
    in_table = False
    in_list = False
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()

        # 表格
        if line.strip().startswith("|"):
            if not in_table:
                out.append("<table>")
                in_table = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if all(re.fullmatch(r":?-{2,}:?", c) for c in cells if c):
                i += 1
                continue
            tag = "th" if not in_table or out[-1] == "<table>" else "td"
            out.append("<tr>" + "".join(f"<{tag}>{render_inline(c)}</{tag}>" for c in cells) + "</tr>")
            i += 1
            continue
        elif in_table:
            out.append("</table>")
            in_table = False

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            if in_list:
                out.append("</ul>")
                in_list = False
            lvl = len(m.group(1))
            out.append(f"<h{lvl}>{render_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue

        # 列表项（checkbox，可带 doc_id 管理栏）
        m = re.match(r"^\s*- \[([ xX])\]\s+(.*)", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            checked = m.group(1).lower() == 'x'
            done_cls = ' class="done"' if checked else ''
            content = m.group(2)
            # 提取 doc_id（第6类管理的前提）
            doc_id = None
            dm = re.search(r"\|\s*doc_id[:：]\s*([A-Za-z0-9_-]+)", content)
            if dm:
                doc_id = dm.group(1)
                content = content.replace(dm.group(0), "").rstrip(" |")
            bar = action_bar_html(doc_id) if doc_id else ""
            out.append(
                f'<li{done_cls}><input type="checkbox"{" checked" if checked else ""} disabled> '
                f'{render_inline(content)}{bar}</li>'
            )
            i += 1
            continue

        # 普通列表
        m = re.match(r"^\s*-\s+(.*)", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{render_inline(m.group(1))}</li>")
            i += 1
            continue
        elif in_list:
            out.append("</ul>")
            in_list = False

        # 引用
        m = re.match(r"^>\s?(.*)", line)
        if m:
            out.append(f"<blockquote>{render_inline(m.group(1))}</blockquote>")
            i += 1
            continue

        # 分隔线
        if re.match(r"^---+$", line.strip()):
            out.append("<hr>")
            i += 1
            continue

        # 空行
        if not line.strip():
            i += 1
            continue

        # 普通段落
        out.append(f"<p>{render_inline(line)}</p>")
        i += 1

    if in_list:
        out.append("</ul>")
    if in_table:
        out.append("</table>")
    return "\n".join(out)


def latest_weekly():
    files = sorted(glob.glob(os.path.join(WEEKLY_DIR, "*.md")))
    return files[-1] if files else None


def query_states(doc_ids):
    """批量查第6类状态（starred / lifecycle / is_archived）。Qdrant 单次 scroll + match any。"""
    if not doc_ids:
        return {}
    states = {did: {"starred": False, "lifecycle": "", "is_archived": False} for did in doc_ids}
    try:
        data = MS._http_post(
            f"/collections/{MS.COLLECTION}/points/scroll",
            {
                "filter": {"must": [{"key": "doc_id", "match": {"any": doc_ids}}]},
                "limit": 1000,
                "with_payload": True,
                "with_vector": False,
            },
        )
    except Exception:
        return states
    for p in data.get("result", {}).get("points", []):
        pl = p.get("payload") or {}
        did = pl.get("doc_id")
        if did not in states:
            continue
        st = states[did]
        if pl.get("stats", {}).get("starred"):
            st["starred"] = True
        if pl.get("lifecycle"):
            st["lifecycle"] = pl["lifecycle"]
        if pl.get("is_archived"):
            st["is_archived"] = True
    return states


def apply_action(doc_id, action, value):
    """执行第6类操作，返回 (ok, msg)。复用 mark_status 写入+读回+记账本。"""
    # 1. 查文档
    try:
        points = MS.find_points(doc_id)
    except Exception as e:
        return False, f"Qdrant 连接失败: {e}"
    if not points:
        return False, "未找到该 doc_id（知识库中不存在）"
    point_ids = [p["id"] for p in points]
    title = MS.get_doc_title(points)

    # 2. 写熔知（带读回确认）
    try:
        if action in ("star", "unstar"):
            want = (action == "star")
            msg = MS.write_backend(doc_id, "starred", want, point_ids, points=points)
        elif action == "lifecycle":
            if value not in MS.LIFECYCLE_STAGES and value != "":
                return False, f"无效阶段: {value}"
            msg = MS.write_backend(doc_id, "lifecycle", value, point_ids)
        elif action in ("archive", "unarchive"):
            want = (action == "archive")
            msg = MS.write_backend(doc_id, "archived", want, point_ids)
        else:
            return False, f"无效操作: {action}"
    except Exception as e:
        return False, f"写熔知失败: {e}"

    # 3. 记账本同步（与 CLI 行为一致）
    state = MS.load_state()
    docs = state.setdefault("docs", {})
    entry = docs.setdefault(doc_id, {})
    entry["title"] = entry.get("title") or title
    if action == "unarchive":
        entry.pop("status", None)
        entry["status_at"] = ""
    elif action in ("star", "unstar"):
        entry["starred"] = (action == "star")
    elif action == "lifecycle":
        entry["lifecycle"] = value
    elif action == "archive":
        entry["status"] = "archived"
        entry["status_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    MS.save_state(state)
    MS.append_event(
        f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] serve-action: {doc_id} → {action}"
        + (f" {value}" if value else "")
        + f" ({title[:30]})"
    )
    return True, msg


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path not in ("/", "/index.html"):
            self.send_error(404)
            return
        latest = latest_weekly()
        if not latest:
            body = "<p>暂无行动清单（weekly/ 为空）</p>"
        else:
            with open(latest, encoding="utf-8") as f:
                md_text = f.read()
            body_html = md_to_html(md_text)
            fname = os.path.basename(latest)
            body = f'<p class="meta">📄 {fname} | 自动渲染 · 第6类管理（收藏/阶段/归档）</p>' + body_html
        page = PAGE_TEMPLATE.format(content=body, lc_labels=json.dumps(LIFECYCLE_LABELS, ensure_ascii=False))
        data = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Frame-Options", "ALLOWALL")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        path = self.path.split("?")[0]
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length) if length else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            self._send_json({"ok": False, "msg": "请求体解析失败"}, 400)
            return

        if path == "/api/status":
            ids = [str(d) for d in body.get("doc_ids", [])]
            self._send_json({"ok": True, "states": query_states(ids)})
            return
        if path == "/api/action":
            doc_id = str(body.get("doc_id", ""))
            action = str(body.get("action", ""))
            value = str(body.get("value", ""))
            ok, msg = apply_action(doc_id, action, value)
            self._send_json({"ok": ok, "msg": msg})
            return
        self._send_json({"ok": False, "msg": "未知端点"}, 404)

    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=5100)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"📋 行动清单陈列架: http://localhost:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
