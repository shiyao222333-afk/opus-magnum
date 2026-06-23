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
