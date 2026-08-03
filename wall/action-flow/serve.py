# -*- coding: utf-8 -*-
"""
serve.py — 陈列架（知识→行动回流系统）
职责：把 weekly/ 下最新的周清单 md 渲染成网页，供 Dashy 内嵌展示。
模板固定只换内容：每次请求自动读最新清单，代码永不改动。

用法：python serve.py [--port 5100]
"""
import argparse
import glob
import html
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEEKLY_DIR = os.path.join(BASE_DIR, "weekly")

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>📋 行动清单</title>
<style>
  body {{ font-family: "Microsoft YaHei", sans-serif; background: #17181c; color: #e8e8ec;
         margin: 0; padding: 24px 16px; }}
  .container {{ max-width: 860px; margin: 0 auto; }}
  h1 {{ font-size: 22px; border-bottom: 1px solid #3a3b42; padding-bottom: 10px; }}
  h2 {{ font-size: 17px; margin-top: 28px; color: #ffd866; }}
  h3 {{ font-size: 14px; margin-top: 18px; color: #9cdcfe; }}
  p {{ line-height: 1.7; font-size: 14px; }}
  ul {{ padding-left: 20px; }}
  li {{ margin: 6px 0; line-height: 1.6; font-size: 14px; }}
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
</style>
</head>
<body><div class="container">{content}</div></body>
</html>
"""


def render_inline(text):
    """行内格式：粗体 / 行内代码 / 🔥市场验证高亮"""
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"🔥市场验证：[^|]+", lambda m: f'<span class="hot">{m.group(0)}</span>', text)
    return text


def md_to_html(md_text):
    """极简 markdown → HTML（只支持本模板用到的语法）"""
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
            # 简单判断表头：上一行是 <table> 且未写过 <tr> 表头
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

        # 列表项（checkbox）
        m = re.match(r"^\s*- \[([ xX])\]\s+(.*)", line)
        if m:
            if not in_list:
                out.append("<ul>")
                in_list = True
            checked = m.group(1).lower() == 'x'
            done_cls = ' class="done"' if checked else ''
            out.append(
                f'<li{done_cls}><input type="checkbox"{" checked" if checked else ""} disabled> '
                f'{render_inline(m.group(2))}</li>'
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


class Handler(BaseHTTPRequestHandler):
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
            body = f'<p class="meta">📄 {fname} | 自动渲染 · 代码固定只换内容</p>' + body_html
        page = PAGE_TEMPLATE.format(content=body)
        data = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("X-Frame-Options", "ALLOWALL")
        self.end_headers()
        self.wfile.write(data)

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
