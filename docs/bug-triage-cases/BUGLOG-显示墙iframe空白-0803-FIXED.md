# BUGLOG-显示墙iframe空白-0803-FIXED

> 元数据：项目=opus-magnum ｜ 跨度=2026-08-03 20:58~21:40 ｜ 总轮数=2 ｜ 触发方式=用户报"显示墙空白" ｜ 流程依据=bug-triage skill
> 一句话背景：巨作 /wall 页面用 `ui.html` 注入 `<iframe>` 内嵌 Dashy，iframe 被 NiceGUI 3.14 的 DOMPurify 消毒直接删除，从未渲染。

## 1. 现象
- 技术表现：巨作 /wall 页面（显示墙）iframe 区域空白（黑框），Dashy 独立访问（localhost:4000）完美渲染
- 用户原话：「显示墙空白，什么都没有」「还是没有」（Ctrl+Shift+R 强制刷新后仍空白）

## 2. 调试历程（证据链）
### 阶段一：Dashy 侧排查（第 0 轮）
- 假设：Dashy 服务/构建/响应头/缓存问题
- 验证方法：curl /healthz、/conf.yml、js-yaml 解析、dist 完整性、Chrome headless 渲染、重启进程
- 诊断证据：/healthz 200；/conf.yml 200（3 分区完整）；js-yaml 解析成功；dist 266 资源全在；Dashy 独立截图完美渲染；重启后配置校验通过；用户强刷仍空白
- 结论：❌ 排除 — Dashy 侧 100% 正常

### 阶段二：iframe 场景模拟（第 1 轮）
- 假设：Dashy 在 iframe 内渲染失败（JS/路由/Cookie 等）
- 验证方法：CDP 脚本模拟 iframe 嵌入（file:// 页面 iframe→Dashy），attach iframe target 检查
- 诊断证据：Dashy V4.5.5 启动日志、bodyPreview 完整 3 分区、hasSections=true、title=显示墙 — **iframe 场景 Dashy 完美渲染**
- 结论：❌ 排除 — Dashy 在 iframe 内正常

### 阶段三：巨作 /wall 主体 DOM 检查（第 2 轮）✅
- 假设：巨作 /wall 页面的 iframe 元素根本没注入
- 验证方法：真实 Chrome GUI + CDP 输出主体 HTML（diag_iframe4/5）
- 诊断证据：
  - iframeCount=0（真实 Chrome 下 iframe 元素不存在，Targets 无 Dashy）
  - 主体 HTML：`<div id="c26">Dashy 聚合入口…</div><div id="c27"></div>` — **ui.html 渲染成空 div**
  - 页面尾部脚本：`Element.prototype.setHTML = html => { this.innerHTML = DOMPurify.sanitize(html) }` — NiceGUI 3.14 DOMPurify 消毒
  - NiceGUI 3.14 `ui.html` 签名：`(content, *, sanitize=True, tag='div')` — sanitize 默认 True；`ui.frame` 组件已不存在
- 结论：✅ 确认 — **ui.html 的 iframe 被 DOMPurify 消毒删除**（iframe 防 XSS 默认移除），iframe 元素从未存在，Dashy 从未加载。显示墙批次（8-03 15:20）只验证端口 200 未验证 iframe 渲染，验收遗漏。

## 3. 最终方案
- 关键改动：`app.py` page_wall — `ui.html('<iframe ...>')` → `ui.element("iframe").props('src="http://localhost:4000"').classes(...).style(...)`
  - 为什么有效：ui.element 直接创建原生 HTML 元素（不走 HTML 字符串注入），完全绕开 DOMPurify 消毒；属性用 props 设置，无 XSS 风险
  - 备选（未用）：ui.html(sanitize=False) 也可，但注入字符串方案不如 ui.element 干净
- 验证：真实 Chrome GUI 截图 — 修复前空白 48,869B → 修复后 142,630B（iframe 内 Dashy 完整渲染，对比 Dashy 独立 45,856B）；iframe 元素 src/尺寸正常

## 4. 已排除方向（含证伪证据）
| # | 方向 | 轮次 | 诊断证伪证据 | 根因 |
|---|------|------|------------|------|
| 1 | Dashy 服务端异常 | 0 | /healthz 200、/conf.yml 200、js-yaml 成功 | 无 |
| 2 | Dashy 构建产物不完整 | 0 | dist 266 资源全在、546KB 主 JS | 无 |
| 3 | 响应头拦截 iframe | 0 | 无 X-Frame-Options/CSP | 无 |
| 4 | 浏览器缓存 | 0 | 用户强刷仍空白 | 无 |
| 5 | Dashy iframe 渲染失败 | 1 | file:// 模拟 iframe 内 Dashy 完美渲染 | 无 |
| 6 | 巨作进程旧代码 | 1 | 16308 启动 15:33 > app.py 修改 15:26 | 无 |
| 7 | SERVICES 字符串元素 | 1 | 两个 SERVICES 全是 dict（日志 AttributeError 是历史） | 无 |
| 8 | CSP/响应头限制 | 2 | 8501 响应头无 CSP/X-Frame-Options | 无 |

## 5. 教训（每条绑定具体证据）
1. **NiceGUI 3.14 的 ui.html 有 DOMPurify 消毒，iframe 标签默认被删**（阶段三：c27 空 div）— 内嵌 iframe 必须用 `ui.element("iframe")` 原生方式；写 ui.html 前先查 sanitize 行为
2. **"端口 200" ≠ "功能正常"**（阶段三：Dashy/Dashy iframe 都 200 但巨作 iframe 从未渲染）— UI 类功能必须做真实浏览器渲染验证（截图/PDF/控制台），不能只 curl 端口
3. **headless 截图不渲染 iframe、headless WebSocket 可能连不上、headless PDF 与真实渲染有差异**（阶段一/二）— 前端渲染问题必须用真实 Chrome GUI + CDP 验证
4. **headless Chrome 首次启动显示 chrome://intro 引导页**（阶段三）— 加 `--no-first-run --no-default-browser-check`
5. **诊断工具价值**：CDP + `Target.setAutoAttach`/`Target.attachToTarget` 能读 iframe 内部状态与 console，是前端疑难 bug 的核心诊断手段
