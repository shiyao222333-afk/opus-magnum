# 🔬 待研究项队列

> 来源：AI 每日新闻自动化 | 自动追加，手动勾选
> 
> 用法：研究完一条就勾掉 `[x]`。积压太多时优先清 🔴。

---

## 2026-06-23

> 数据源：aihot 精选 16 条 | 匹配项目 2 个 | 整理 10:19

### 🔴 本周可试

- [ ] **【PP-OCRv6 — 50 语言 OCR，最小 1.5M 参数】** | 来源：https://huggingface.co/blog/PaddlePaddle/pp-ocrv6 | 🎯 Nigredo 馏析
  研究方向：这个轻量 OCR 能否嵌入 Nigredo 管道，处理无字幕视频的截图/PPT 文字提取？tiny 版只有 1.5M 参数，可直接在 Hugging Face 用，是否需要额外训练或微调？

- [ ] **【微信 Agent「小微」灰度内测 — 主入口发消息/红包，子入口可读聊天记录】** | 来源：https://mp.weixin.qq.com/s/qVdfx01e9C9r5mGi0jh2BA | 🎯 Rubedo 凝华
  研究方向：微信是转化闭环的最后一公里。小微开放后，私信自动化的平台风险与机会并存。研究小微的能力边界（能否接收消息/触发自动化？API 是否开放？），判断对小红书→微信导流链路的影响。

### 🟡 关注

- [ ] **【Sakana Fugu — 多 Agent 编排封装成单 API】** | 来源：https://x.com/berryxia/status/2069090959938466298 | 🎯 Rubedo 凝华
  研究方向：多 Agent 系统封装成"单入口/单出口"，与「非必要不用大模型」原则一致。参考架构是否适用于未来的 Homunculus 自动化模块？

- [ ] **【Oak — 专为 AI Agent 设计的 Git 替代品】** | 来源：Show HN | 🎯 Rubedo 凝华
  研究方向：BLAKE3 内容哈希 + 内容定义分块，专为 Claude Code/Cursor 等 AI 编码工具设计。对用 AI 辅助开发的项目管理是否有价值？

---

> 📡 第二次扫描 | 数据源：同批 16 条 | 按机会雷达规则过滤 | 🕐 10:35

### 🟡 关注

- [ ] **【Aleph 2.0 — Runway 旗舰视频编辑模型，集成 Figma Weave】** | 来源：https://runwayml.com/news/aleph-2-in-figma-weave | 🎯 Rubedo 凝华
  研究方向：AI视频编辑实现"改一帧→传播全片段"，1080p/30s。如果自部署或API开放，能否降低B站/小红书视频制作成本？独立创作者的AI剪辑方案进展到什么程度？

- [ ] **【Claude Code 让「单人创业者」增多 — Anthropic 工程负责人谈 AI 编程对独立开发者的影响】** | 来源：https://www.ithome.com/0/967/216.htm | 🎯 Rubedo 凝华
  研究方向：AI编程工具正在降低创业门槛，"氛围编程"让更多单人创业者出现。这对一人公司的竞争格局意味着什么？哪些副业方向因为AI编程变得更可行？

- [ ] **【Google ADK + A2A 协议 — 跨语言多智能体系统搭建】** | 来源：https://developers.googleblog.com/build-cross-language-multi-agent-team-with-google-agent-development-kit-and-a2a | 🎯 Rubedo 凝华
  研究方向：将单体提示词分解为专业化微智能体（降低爆炸半径、可单独测试）。是否适用于未来 Rubedo 的自动化任务调度？A2A 协议能否连接 Python/NiceGUI 与外部服务？

### 💡 探索

- [ ] **【Google DeepMind 7500万美元投资 A24，进军 AI 电影制作】** | 来源：https://techcrunch.com/2026/06/22/google-deepmind-bets-75m-on-ais-future-in-hollywood-with-a24-deal | 🎯 OpusMagnum 巨作
  值得关注：Netflix、亚马逊、DeepMind 都在涌向 AI 影视。AI视频生成从"玩具"到"电影级"的跨越正在发生。一人公司是否能靠 AI 视频工具（如 Runway/Sora）接商业视频单？这是个值得关注的新变现方向。
