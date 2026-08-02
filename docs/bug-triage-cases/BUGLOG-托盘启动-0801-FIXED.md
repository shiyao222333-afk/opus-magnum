# BUGLOG · 双击启动巨作无托盘 — 已修复（2026-08-01）

> 症状：双击「启动巨作」快捷方式 → 黑框一闪而过 → 托盘图标不出现、巨作不启动、supervisor.log 无任何记录。
> 用户从 7/31 起多次反馈，同一症状 ≥3 轮未过 → bug-triage 流程收敛。

## 根因（最终确认）

**`launcher/启动巨作.bat` 含 UTF-8 编码的中文注释，而 Windows cmd 按系统默认代码页（GBK/936）解析 .bat 文件 → 中文乱码破坏 if 括号块/命令流 → `start` 行从未执行 → 托盘程序从未被启动。**

关键证据链：
1. AI 直接跑 `venv pythonw launcher.pyw` **三次全部成功**（21:46/21:53/22:19）——但全部**绕过了 .bat**，导致长期误判"托盘程序没问题"。
2. 用户双击/快捷方式/PowerShell 执行 .bat → 探针（.bat 首行写日志）**始终 0 字节** → 命令流在探针行前就断了。
3. 重写 .bat 为**纯 ASCII（零中文）**后：探针立即有记录、pythonw 进程出现、supervisor.log 22:41:59 正常启动巨作、8501 端口起来 → 根因实锤。
4. 原版 .bat（git HEAD）同样含中文 REM 注释 → **用户从 7/31 起就从未成功过**（非本次改动引入）。

## 修复方案

`启动巨作.bat` 重写为全 ASCII：
- 删除所有中文注释 / chcp 65001（全 ASCII 不需要）
- if 块改为 goto 简化结构（避免括号块解析风险）
- 探针行前置：`echo [%date% %time%] double-click >> "%~dp0_doubleclick.log"`（诊断后保留无害，可删）
- 启动命令不变：`start "" "%PYW%" "%SCRIPT%"`（PYW=venv pythonw，SCRIPT=launcher.pyw）

## 教训（沉淀）

1. **Windows .bat 文件必须避免中文**（尤其 UTF-8 无 BOM + 系统 GBK 代码页）：中文注释会被 cmd 静默解析成乱码，可能破坏命令结构且**无任何报错**。写 .bat 一律 ASCII/英文。
2. **验证启动链路必须走完整 .bat**：直接跑 pythonw/launcher.pyw 会绕过 .bat 自身的问题，造成"程序没问题"的假象。
3. **"双击无反应"类 bug 用探针日志一锤定音**：在 .bat 首行写日志文件，双击后看日志有无记录即可区分"入口没触发" vs "脚本中途断"。
4. 诊断工具（探针/psutil/GBK 解码检查）输出均可一键复制纯文本，符合 bug-triage 要求。
