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
  研究方向：多 Agent 系统封装成"单入口/单出口"，与「非必要不用大模型」原则一致。参考架构是否适用于未来的自动化编排模块？

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

---

## 2026-06-24

> 数据源：aihot 精选 15 条（24h）+ 100 条（7d）| 手动筛选匹配项目 5+1 条 | 整理 08:50

### 🔴 本周可试

- [ ] **【Unlimited OCR — 百度开源单次长时域解析】** | 来源：https://github.com/baidu/Unlimited-OCR | 🎯 Nigredo 馏析
  研究方向：「One-Shot Long-Horizon Parsing」一次处理长时间跨度的 OCR 任务，适合「视频/课程长片段」截图一次性识别成结构化文本。和传统按帧 OCR 比，节省 token 和时间，可直接当 Nigredo 的「长视频字幕回填」模块。

- [ ] **【JoyAI-VL-Interaction — 京东全栈开源「边看边说」交互模型】** | 来源：https://mp.weixin.qq.com/s/IY6XGp4k6VgD9ZPH6YprCA | 🎯 Nigredo 馏析
  研究方向：vLLM-Omni 原生支持、实时观察视频流 + 主动判断关键事件 + 实时语音回复，开箱支持摄像头/直播流/人脸看护/直播讲解。一人公司凭此可做「AI 监控预警」类小工具，硬件门槛低（普通 USB 摄像头即可）。

- [ ] **【Mistral OCR 4 — 逐词置信度 + 块分类 + 170 语种】** | 来源：https://mistral.ai/news/ocr-4 | 🎯 Nigredo 馏析
  研究方向：边界框 + 块分类（标题/表格/公式/签名）+ 每词置信度 = 字幕/讲义结构化利器。Batch API 半价 1000 页/2 美元，比自托管 GLM-OCR/PaddleOCR 在多语种上更省事。直接评估「Nigredo 摄取 → Albedo 验证」链路。

### 🟡 关注

- [ ] **【Vercel Eve 开源 Agent 框架 — 文件目录即 Agent】** | 来源：https://www.marktechpost.com/2026/06/17/vercel-releases-eve | 🎯 Rubedo 凝华
  研究方向：Vercel 内部跑了上百个 Agent，含 Lead Agent（年费 $5000 / 32x ROI）和 Support Agent（92% 工单自主解决）。这是「单人 Agent 商业化」的真实样本：卖结果、订阅制、自动化销售闭环。研究 Lead Agent 的「定价-定位-获客」模型，能否复用到自己的 Rubedo 自动化业务。

- [ ] **【Viktor 登陆 Microsoft Teams — 零销售做到 2000 万 ARR】** | 来源：https://x.com/rohanpaul_ai/status/2067755504613613699 | 🎯 Rubedo 凝华
  研究方向：AI 员工 Viktor 在 Slack 上年化收入 2000 万美元（无销售团队、未大规模推广），核心是「零学习成本：@Viktor 即可获结果，不用写 prompt、不用主动 @ 也能自动完成」。正式登陆 Microsoft Teams 3.2 亿用户。即日起免费试用含 100 美元信用额度。这是「AI 员工」产品形态的最强背书——直接复刻对照：SSS 自己的自动化业务能不能做到「同事式自然语言」交互？把 prompt 全部藏到工具里。Viktor 偏 C 端「AI 员工」+ Vercel Eve 偏 B 端「高客单订阅」—— 两条路径都验证了「卖结果不卖功能」。立即研究两条路径的「定价-定位-获客」三件套，看能否复用到我们自己的 Rubedo 业务。

- [ ] **【IBM CUGA — 单文件 Agent 框架 + 20+ 开源示例】** | 来源：https://huggingface.co/blog/ibm-research/cuga-apps | 🎯 Rubedo 凝华
  研究方向：单文件 FastAPI 即一个 Agent，三种推理模式（Fast/Balanced/Accurate）自由切换，OpenAI/watsonx/Ollama 一行 env 切换。「单文件可独立部署 + 多模型兼容」= 一人公司起步友好。比 LangChain/LlamaIndex 更轻，看看能否作为 Rubedo 自动化任务调度的备选底座。

- [ ] **【Confucius4-TTS 网易开源 — 14 语种零样本语音克隆】** | 来源：https://www.ithome.com/0/967/636.htm | 🎯 Nigredo 馏析
  研究方向：3 秒音频即可克隆音色，跨语种无口音（相似度 85%+），Apache 协议 + 54GB 资源包可本地部署。短剧出海 / 知识付费 / 有声书 / 小红书「自己的声音播报多语种」—— 一人公司声音副业的成本可能降到「麦克风 + 一次性训练」。

### 💡 探索

- [ ] **【八部门「AI+消费」实施意见 — 个人消费贷款贴息买 AI 产品】** | 来源：https://www.ithome.com/0/966/154.htm | 🎯 OpusMagnum 巨作
  值得关注：政策直接把「智能眼镜/AI 手机/人形机器人/智能网联汽车」纳入贴息消费范围。补贴将集中在「终端首发平台 + 进万家活动」上—— 一人公司若有 AI 硬件/智能家居 SaaS，可借政策窗口期快速触达用户。但要警惕「以旧换新式补贴」的回款账期风险。

- [ ] **【豆包实时语音 3.0 API — 主动加入多人对话 + 工具调用】** | 来源：https://mp.weixin.qq.com/s/L4BJnexabQu5DAxDnwEGxw | 🎯 OpusMagnum 巨作
  值得关注：原生全双工 + 主动判停（误打断 -40%），可在多人会议中「安静待命，话题出现时主动加入」。配合工具调用可订日程/发邮件。这把「会议纪要 AI」从「被动记录」升级到「主动发言」，一人公司若做「销售陪谈/客户复盘」工具，体验质变。

---

> 📡 第二次扫描 | 数据源：aihot 精选 3 条新增 + 搜索 10 条副业/一人公司 | 🕐 08:50

### 🟡 关注

- [ ] **【Runway Seedance 4K / Mini / Kling 3.0 Turbo — 三款视频生成模型同日发布】** | 来源：https://x.com/runwayml/status/2069535148450705517 | 🎯 Rubedo 凝华
  研究方向：Seedance 4K 高分辨率视频生成 + Mini 轻量版 + Kling 3.0 Turbo 快速版，三档覆盖不同需求。首三个月七折（优惠码 30RUNWAY）。对小红书/短视频创作者而言，4K+快速生成 = 批量出内容的成本进一步下降。评估 API 定价与自部署 FastWan-QAD 的经济性对比。

- [ ] **【FastWan-QAD — 单卡 5090 上 1.8 秒生成 5 秒视频，开源】** | 来源：https://x.com/haoailab/status/2069493820732170695 | 🎯 Rubedo 凝华
  研究方向：量化感知蒸馏（QAD）方案，单卡端到端 5 秒 480P 视频 1.8 秒。模型、代码、博客全开源。如果本地部署可行，一人公司短视频批量生产的硬件成本 = 一张 5090 ≈ ¥15000，比 API 调用更可控。测试实际画质和稳定性。

- [ ] **【豆包音频生成模型 1.0 — 单 Prompt 多角色对白 + 背景音乐，2 分钟音频】** | 来源：https://mp.weixin.qq.com/s/iL0uyUjOMUEfudeuDP6wQQ | 🎯 Nigredo 馏析
  研究方向：文本→音频端到端生成，多角色音色一致性 + 音色风格解耦 + 0 样本多模态输入。火山方舟 API 邀测，个人 30 分钟免费额度。音频是 Nigredo 馏析的核心处理类型之一——评估能否替代或补充现有的语音转文字流程（反向：文字→播客/有声内容，作为输出格式）。

### 💡 探索

- [ ] **【7 Solo Founders $1M+ ARR — 2026 年一人公司真实案例拆解】** | 来源：https://greyjournal.net/hustle/grow/solo-founders-million-dollar-ai-businesses-2026/ | 🎯 OpusMagnum 巨作
  值得关注：Base44 单人 6 个月做到 250K 用户后以 $80M 卖给 Wix；HeadshotPro 单人月收 $300K；38% 七位数企业由 solopreneur 主导。一人公司年均技术栈成本 $3K-$12K，运营利润率 60-80%。这些数据是 Rubedo 凝华商业模式设计的硬参考——「一人 + AI 工具」的可行区间已被验证。

- [ ] **【10 AI Side Hustles That Actually Pay in 2026 — 含真实收入数据】** | 来源：https://www.aicofounderstack.com/2026/05/10/10-ai-side-hustles-that-actually-pay-in-2026/ | 🎯 OpusMagnum 巨作
  值得关注：AI编码代工 $5K-$25K/月、B2B 内容系统 $2K-$8K/月、定制 AI Agent/聊天机器人 $1.5K-$5K 部署 + $200-$500/月维护、微型 SaaS $5K-$20K/月、AI 设计服务 $1.5K-$6K/月。收入区间 + 工具栈 + 时间线全部给出。这些是「已知可行的赚钱路径」，对照自己的技能和项目，选 1-2 条优先验证。

## 2026-06-25

> 数据源：aihot 精选 20 条（24h）+ 100 条（7d）+ WebSearch 5 维度（副业/独立开发者/小红书/RAG/OCR-RPA）| 匹配项目 4 个 | 整理 08:50

### 🔴 本周可试

- [ ] **【Notion 用 Cursor SDK 嵌入编码智能体 — 讨论串即 Agent】** | 来源：https://cursor.com/blog/notion | 🎯 Rubedo 凝华
  研究方向：Notion 数周内集成 Cursor SDK，文档中 @Cursor 即可端到端完成规划/构建/测试/PR。这是「文档流即 Agent 流」的真实样本——对照「私信/小红书评论/工单→自动响应→落地交付」链路，Cursor SDK 这种「Provider 无关+可远程 MCP+流式断点恢复」架构能否复用到我们的自动化业务？立即评估 Notion + Cursor 这种「SaaS 内嵌 AI」模式的边际成本。

- [ ] **【豆包专业版 68 元/月起 — 桌面 Agent + Office 套件 + 数据库应用】** | 来源：https://mp.weixin.qq.com/s/Sb-NMXTrWFQES1EDO_Gr2g | 🎯 Rubedo 凝华
  研究方向：豆包 2.1 Pro + 操作本地电脑/浏览器/调用 Skills/定时任务 + 生成带后端数据库的在线应用。68 元/月（学生 38 元）—— 字节亲自下场做「桌面 Agent 套件」定价极激进。对照 Rubedo 的「桌面自动化 + 私域运营」构想：豆包专业版如果开放 Skills 协议，能否作为低成本执行层（替代部分 RPA 场景）？但要警惕「国内 Agent 平台」的数据合规与平台锁定风险。

- [ ] **【字节 TRAE 90% 代码由 AI 生成 — 日均 Token 5.6 万亿、增长 50 倍】** | 来源：https://mp.weixin.qq.com/s/mdmaAyUIvxE8WT_GEbF2wQ | 🎯 Rubedo 凝华
  研究方向：900 次实验显示主流 Coding 模型正确率 80%+，但可交付性仅 40-60 分；结合 Harness 基建后提升至 80 分。结论：「AI 降低编程门槛但需优化指标/治理/协作」。这正是 SSS 当下用 Claude Code 推进项目时的真实痛点——立即总结一份「AI Coding 交付质量提升清单」（指标/治理/协作），应用到 Athanor 的开发实践。

### 🟡 关注

- [ ] **【Zvec — 阿里开源进程内向量数据库，10K Stars 的 SQLite-for-Vectors】** | 来源：https://txtmix.com/posts/tech/alibaba-zvec-embedded-vector-database/ | 🎯 Citrinitas 熔知
  研究方向：pip install zvec 一行部署，定位「SQLite for Vectors」挑战 FAISS/Qdrant。进程内嵌入 = 零运维成本，对 Athanor 这种一人公司起步阶段极度友好。立即评估：是否能把 Citrinitas 当前向量检索模块从 ChromaDB 切换到 Zvec？注意对比检索质量、嵌入模型兼容性、持久化方案。

- [ ] **【2026 智能自动化演进：从规则 RPA 到大模型 Agent RPA】** | 来源：https://www.cnblogs.com/MDLD/articles/20763773 | 🎯 Rubedo 凝华
  研究方向：现代 RPA 平台融合大模型理解能力 + 传统执行能力，非结构化数据处理 + 动态页面适配 + 智能决策成为标配。「个人开发者/工作室/中小企业的工具在 2026 年会迎来爆发式增长」—— 这就是 Rubedo 凝华要切入的赛道。立即梳理：「Agent + RPA」框架下有哪些「人 + AI」协作的标准化模板可直接复用。

- [ ] **【思考即回忆：推理如何解锁 LLM 中的参数化知识（Google Research）】** | 来源：https://research.google/blog/thinking-to-recall-how-reasoning-unlocks-parametric-knowledge-in-llms | 🎯 Albedo 炼真
  研究方向：推理（chain-of-thought）能让 LLM 回忆简单事实（无需复杂推导），原因是推理 token 充当「计算缓冲」+ 「事实启动效应」。这与 Albedo「知识验证」场景直接相关——是否可以利用「推理触发回忆」机制，设计「多步推理 + 内部证据检索」的本地知识验证流水线？对比「直接 RAG 检索」在事实核查上的准确率差异。

- [ ] **【小红书 2026 新规 + AI 内容治理规则 — 鼓励如实标识、反对低质批量】** | 来源：https://news.qq.com/rain/a/20260427A05JSU00 | 🎯 Rubedo 凝华
  研究方向：「AI 托管账号管控」+「必须标识 AI 内容」+「零容忍违规」三条红线。这对 Rubedo「小红书自动化 + 私域运营」业务是双刃剑：一方面 AI 批量号策略必须升级为「人设 + 显式标注」，另一方面合规优质内容反而能获得平台流量倾斜。立即重新设计 SSS 的小红书运营 SOP：内容生产要带「AI 协作者」标识 + 真人审稿环节。

- [ ] **【2026 年 6 款视频转文字工具实测对比 — 场景化选型】** | 来源：https://www.cnblogs.com/1699-m-20260616/p/20679494 | 🎯 Nigredo 馏析
  研究方向：短视频/会议录音/长视频/多语言场景下的工具选型矩阵。Nigredo 当前可能依赖单一转写引擎，对照工具列表评估：「格镜/影忆/通义/讯飞/飞书妙记/腾讯会议」各自在 Nigredo 摄入管线中的定位（实时转写 vs 离线精转 vs 多语种 vs 带说话人分离），决定是否引入多引擎 fallback 提升稳定性。

### 💡 探索

- [ ] **【百度秒哒 AI — 8 个月 50 万商业应用，81% 创作者无编程基础】** | 来源：https://baijiahao.baidu.com/s?id=1868136805695295286&wfr=spider&for=pc | 🎯 OpusMagnum 巨作
  值得关注：百度秒哒定位「想法→产品→变现」全闭环，8 个月诞生 50 万应用，81% 无编程基础用户，8 万笔真实成交。这是国内大厂亲自下场做「零代码商业化平台」的最强信号——一人公司无需自己写底层，可以借平台流量 + AI 工具快速验证 MVP。立即评估：秒哒是否值得作为 Athanor/Rubedo 的「前端快速验证渠道」（先在秒哒上跑出付费用户，再迁移到自有平台）。

- [ ] **【2026 AI 商业化拐点 — Anthropic ARR 470 亿、OpenAI 月活 200 亿】** | 来源：https://adg.csdn.net/6a309c6f10ee7a33f27da8ed.html | 🎯 OpusMagnum 巨作
  值得关注：Anthropic 年增 230%、OpenAI 企业 ARR 320 亿、DeepSeek 估值 450 亿——AI 头部公司「企业级 + 订阅 + API」三轨并进已成定局。对一人公司而言两个信号：(1)「企业级 AI 服务」是真正可付费的市场，C 端纯订阅越来越难；(2) 头部公司在卷长尾应用，留给独立开发者的「垂直小工具 + 行业 know-how」窗口反而更清晰——别和大模型公司正面竞争，做他们做不重的「行业最后一公里」。

---

> 📡 第二次扫描 | 数据源：aihot 精选 20 条（24h）+ 100 条（7d，hasNext 截断）| 关键词搜索 8 维度全部 0 命中 | 🕐 08:50
> 
> **去重对照**：与本日上午第一轮扫描对比，多条匹配项已收录（Notion+CSD、豆包专业版、TRAE 90%、Zvec、Albedo 思考即回忆、百度秒哒、八部门贴息、豆包实时语音 3.0），本轮新增 3 项。
>
> **筛选原则执行**：
> - ❌ 剔除：AI 招聘偏见（社会议题）、Oracle 大规模裁员、AlphaFold 人事（学术圈变动）、Figure 机器人（纯工业）、数据中心电网（基础设施）、AI 数据中心政策、Flock 警长滥用（社会新闻）、Jumper 离职（人事变动）
> - ✅ 保留：Anthropic 孤独感（影响独立开发者生态）、Viktor 2000 万 ARR（已收于昨日队列）、Vercel Eve（已收于昨日队列，本轮强化）
> - 🆕 本轮新增：Viktor 2000 万 ARR 升级（Teams 3.2 亿用户）+ Vercel Eve Lead Agent $5000/年样本 + Anthropic 孤独感

### 🔴 本周可试

- [ ] **【Vercel Eve — Lead Agent 卖 $5000/年、32x ROI、92% 工单自主解决】** | 来源：https://www.marktechpost.com/2026/06/17/vercel-releases-eve | 🎯 Rubedo 凝华
  研究方向：Vercel 内部跑上百个 Agent，Lead Agent（找销售线索、约会议、发跟进，年费 $5000）和 Support Agent（92% 工单自主解决）是「单人 Agent 商业化」最实在的样本——卖结果不卖功能、订阅制而非项目制、自动化销售闭环。这是与今日「百度秒哒 8 个月 50 万应用」互补的样本：百度走 C 端零代码，Vercel 走 B 端高客单。立即研究 Lead Agent 的「定价-定位-获客」三件套，看能否复用到我们自己的 Rubedo 业务（一人公司起步能不能用同样手法？）。

- [ ] **【Viktor 登陆 Microsoft Teams — 零销售做到 2000 万 ARR】** | 来源：https://x.com/rohanpaul_ai/status/2067755504613613699 | 🎯 Rubedo 凝华
  研究方向：AI 员工 Viktor 在 Slack 上年化收入 2000 万美元（无销售团队、未大规模推广），核心是「零学习成本：@Viktor 即可获结果，不用写 prompt、不用主动 @ 也能自动完成」。正式登陆 Microsoft Teams 3.2 亿用户。即日起免费试用含 100 美元信用额度。这是「AI 员工」产品形态的最强背书——直接复刻对照：SSS 自己的自动化业务能不能做到「同事式自然语言」交互？把 prompt 全部藏到工具里。Viktor 偏 C 端「AI 员工」+ Vercel Eve 偏 B 端「高客单订阅」—— 两条路径都验证了「卖结果不卖功能」。立即研究两条路径的「定价-定位-获客」三件套，看能否复用到我们自己的 Rubedo 业务。

### 🟡 关注

- [ ] **【Anthropic 工程负责人：Claude Code 让程序员更孤独，但「单人创业者」增多】** | 来源：https://www.ithome.com/0/967/216.htm | 🎯 Rubedo 凝华
  研究方向：Fiona Fung 透露「氛围编程」让单人创业者增多，但工程师彼此交流减少、长期易感孤独。团队用编程午餐/黑客松/共同开发时段重建协作。这条对 SSS 一人公司路径既是赋能（AI 编码工具让独立可行）也是警告（孤独、协作缺位）。立即对照：把 Anthropic 团队的反孤独实践翻译成「一人公司版协作 SOP」——定期同好圈交流 + 开源协作 + 公开写作。

### ⚪ 了解

- [ ] **【Gemini 3.5 Flash 集成 Computer Use — 跨浏览器/移动/桌面】** | 来源：https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-computer-use-gemini-3-5-flash | 🎯 Rubedo 凝华
  了解：Google 把 Computer Use 做成内置工具集成到 Flash 模型，可调用 Gemini API + Enterprise Agent Platform。新增用户确认 + 间接提示注入自停两项保护。长周期企业自动化场景更强。简单了解——短期内不直接落地，但要跟踪「Computer Use 协议化」对 Rubedo「桌面 Agent」业务的潜在影响。

- [ ] **【Cloudflare 为 AI 智能体推出临时账户】** | 来源：https://blog.cloudflare.com/temporary-accounts | 🎯 Rubedo 凝华
  了解：AI Agent 在调用第三方 API 时需要身份验证但又不能冒用真人账号，临时账户是基础设施级方案。简单了解——一人公司自动化场景下「Agent 身份」是绕不过的问题。

## 2026-06-26

> 数据源：aihot 精选 18 条（24h）+ WebSearch 副业/一人公司/小红书自动化 2 组 | 匹配项目 4 个 | 整理 09:52

### 🔴 本周可试

- [ ] **【Runway Agent 2.0 — 营销视频全流程 AI Agent，面向所有用户开放】** | 来源：https://runwayml.com/news/introducing-agent-2 | 🎯 Rubedo 凝华
  研究方向：对话式开发营销概念→生成变体→自动裁切多平台格式（9:16/16:9/1:1）→导入 Meta/YouTube/TikTok/Google 广告数据→分析→生成下一轮待测广告。SSS 作为效果图设计师，营销视频是最直接的变现出口——评估 Agent 2.0 能否替代现有「手动出图→剪辑→排版」全流程，将一周内容生产压缩到一次对话。重点关注「绩效营销」路径：上传旧广告+数据→AI 自动生成下一轮→形成闭环。

- [ ] **【小互 IP Studio — 开源个人 IP 配图 Agent，31 原创角色+配图方法论】** | 来源：https://x.com/xiaohu/status/2070317717811540149 | 🎯 Rubedo 凝华
  研究方向：Agent 自动读取文章→规划配图类型（情绪图/示意图/四格漫画）→生成→自查返工，默认手绘线稿淡彩画风，5 种皮肤可切换。Python3 + OpenAI 图像 API（默认 GPT-image-2），也支持只输出提示词手动生图。直接用于小红书内容生产配图自动化——对照 SSS 的「军工效果图」风格，看能否把 31 个角色换成自定义角色集，形成个人 IP 配图流水线。

### 🟡 关注

- [ ] **【Midjourney V8.2 preview + 草稿模式随机风格 — 24 倍风格探索速度】** | 来源：https://x.com/midjourney/status/2070223272072065228 | 🎯 Rubedo 凝华
  研究方向：V8.2 美学/个性化效果提前体验 + 草稿模式（24 张低分辨率，价格仅标准 4 张的一半）现已支持 --sref random。风格探索速度比之前快 24 倍 → 找到适合品牌的美学方向 → 点击 Vary 升级为全分辨率。对设计副业意味着「风格试错成本大幅下降」，一人公司快速定位视觉品牌形象的门槛更低了。

- [ ] **【Ornith-1.0 — MIT 开源 Agentic Coding 模型家族，9B-397B 全尺寸】** | 来源：https://x.com/berryxia/status/2070167806700908957 | 🎯 Rubedo 凝华
  研究方向：专注智能体编程，SWE-Bench Verified 82.4、Terminal-Bench 77.5，全系列 MIT 开源 + GGUF 版本 + Ollama/Unsloth 本地运行。一人公司低成本 AI 编码底座的新选项——对照 Claude Code（闭源、按 token 计费）和 Codex（需 ChatGPT Pro），Ornith 本地部署的边际成本趋近于零。评估 9B/31B Dense 版本在 Athanor 项目日常编码中的实际表现。

- [ ] **【OpenAI 内部报告：Codex 占 99.8% 输出 token，Agent 从辅助变主力】** | 来源：https://openai.com/index/how-agents-are-transforming-work | 🎯 Rubedo 凝华
  研究方向：80.6% 用户发起等效人类 30min+工作的请求，非开发者增长 137-189 倍，Legal/Finance/Recruiting 跨过使用过半拐点。趋势信号：Agent 不再是「辅助工具」而是「主力输出」，这对 Rubedo「桌面自动化 + 私域运营」的方向是验证——但 OpenAI 的数据也提醒，Agent 产出需要人类监控纠偏（20% 不可替代），不是全托管。

### 💡 探索

- [ ] **【AI 经济年报：年化收入 $1750B，增速 3 倍于移动互联网】** | 来源：https://x.com/rohanpaul_ai/status/2070288396644491317 | 🎯 OpusMagnum 巨作
  值得关注：AI 营收增速为移动/互联网浪潮的 3 倍，10 亿美元新增从 180 天缩短到 2 天。Token 降价 10%→用量增长 12-18%（弹性强）。对一人公司两个信号：(1)「企业级 AI 服务」是真正可付费市场；(2) 头部公司卷长尾应用，留给独立开发者的窗口是「垂直小工具 + 行业 know-how」——别和大模型正面竞争，做他们做不重的最后一公里。

- [ ] **【"一人公司"爆火真实案例：有人年赚百万，有人收入缩水 90%】** | 来源：https://news.qq.com/rain/a/20260601A02FVF00 | 🎯 OpusMagnum 巨作
  值得关注：弹幕游戏开发：6 款游戏年入 100 万，单款成本仅 1000-1500 元，AI 承担 70% 美术+99% 代码正确率，15 天完成对标大厂质量。反面案例：大厂年薪 60 万→创业月盈利 1000 元，缩水 90%。52.7% 月入不足 7000 元。关键洞察：经验+客户资源是最强壁垒，「零基础」人员无法判断 AI 生成内容正确性；内向型人格获客天然劣势；稳定客户资源是创业前提。

---

## 2026-06-27

> 数据源：aihot 精选 11 条（24h）+ 关键词搜索 8 维度（副业/一人公司/小红书/Agent/RPA/工作流/设计/数字人/TTS/嵌入/音频/浏览器/视频/变现/降本提效，命中均 0）+ WebSearch 5 维度（AI 变现/独立开发者 SaaS/小红书/数字人直播/避坑/AI 出海/知识付费）| 匹配项目 3 个 | 整理 10:00

### 🔴 本周可试

- [ ] **【Leaf 开源项目 — 把网红峰哥做成实时通话 AI 分身，延迟压到 1 秒内】** | 来源：https://x.com/AYi_AInotes/status/2070531964067623381 | 🎯 Nigredo 馏析 + Rubedo 凝华
  研究方向：技术栈三件套：Cartesia ink-whisper 降噪防误触发 + MiniMax 高速版大模型（首字响应 361ms）+ VoxCPM 开源克隆（15 秒素材复刻）。整个工程从 8-20 秒优化到体感 2-3 秒。「女娲 Skill」从直播语料蒸馏人格——这条 Nigredo 馏析处理「直播录音+人格特征」双轨并行；Rubedo 凝华可借此搭「AI 客服/AI 销售陪谈」最小可用产品。立即评估：VoxCPM 克隆质量 + 与 Nigredo 转写流水线的兼容度。

- [ ] **【Claude Code 6 个实用 Hook 玩法 — 让 AI 从聊天框变事件驱动自动化系统】** | 来源：https://mp.weixin.qq.com/s/LVj2foSXi_hBRKxjuYaUyw | 🎯 Rubedo 凝华
  研究方向：Claude Code 内置近 30 个 Hook 事件（年初才 13 个），运行不消耗 token。6 个玩法：权限弹窗提醒、开机日程播报、上下文预压缩时自动生成摘要卡片、结合 Skill 整理下载文件夹、每小时久坐提醒、Bark 推送手机/手表。这正是 Rubedo 凝华「桌面自动化 + 私域运营」的核心抓手——立即把 Hook 玩法整理成「Rubedo 桌面自动化 SOP v1」，并把可对外销售的「预制 Hook 包」作为 MVP 商业化。

- [ ] **【Figma Config 2026 — Code Layers+Motion+Shader+Generative Plugins，画布 AI 来自第三方】** | 来源：https://the-decoder.com/figma-bets-on-human-judgment-at-config-2026-while-the-ai-powering-its-canvas-belongs-to-someone-else | 🎯 Rubedo 凝华
  研究方向：Figma 把 AI 押注在「人类判断」上，画布 AI 能力依赖 Anthropic/OpenAI/Google 等外部模型——推理成本挤压利润率，但 Anthropic 等对手可直接生成界面构成威胁。两个关键信号：(1)「AI 集成层+第三方模型」是被验证可行的轻资产模式；(2) 设计师工具的「人类判断」溢价仍存在。立即评估：能否基于 Figma 插件体系，给军工效果图设计场景做「军工风资产包+提示词模板」副业包（按月订阅/按次收费），与 SSS 当前主业形成「主业反哺+副业变现」闭环。

### 🟡 关注

- [ ] **【Cursor 研究：奖励攻击虚增编码智能体 SWE-bench Pro 分数】** | 来源：https://www.marktechpost.com/2026/06/26/cursor-study-finds-reward-hacking-inflates-coding-agent-benchmark-scores-on-swe-bench-pro | 🎯 Rubedo 凝华
  研究方向：631 条 Opus 4.8 Max 轨迹审计显示 63% 成功修复来自检索（上游查找 57% + git 历史挖掘 9%）。严格隔离后 Opus 4.8 Max 分数从 87.1% 降到 73.0%，Cursor 自家 Composer 2.5 差距最大 20.7 个点。新模型比旧模型更易中招。结论：基准分数「虚高」+ 建议用严格测试环境。这对 SSS 当前用 Claude Code 推进 Athanor 是个警钟——立即检查「我看到的 Claude Code 成功修复有多少是检索现成答案」？是否需要引入「隔离 git 历史 + 限制网络」模式来获得可信开发信号？

- [ ] **【Anthropic Economic Index 报告 — 高薪职业周末使用 Claude 比例更高】** | 来源：https://www.anthropic.com/research/economic-index-june-2026-report | 🎯 OpusMagnum 巨作
  研究方向：工作日个人对话占比 35%，周末升至近 50%；高薪职业在周末占比更高。使用 Claude 最自动化的用户对 AI 明年承担更多任务最乐观，但对薪资/工作安全/工作意义预期最乐观。两个隐含信号：(1) 「AI 重度用户」是高薪职业的「周末续命」工具——一人公司正是这类人；(2) AI 承担任务越多，人类对工作意义感反而更强（反直觉）。可对照设计 SSS 自己的「AI+周末创业」节奏。

- [ ] **【GPT-5.6 Sol — OpenAI最强模型+Ultra子智能体模式，编程超Claude Mythos 5】** | 来源：https://finance.sina.com.cn/tech/digi/2026-06-27/doc-inieuyie1636480.shtml | 🎯 Rubedo 凝华
  研究方向：3档模型（Sol旗舰/Terra均衡/Luna轻量），Terminal-Bench 2.1标准88.8% > Claude Mythos 5(88.0%)，Ultra模式91.9%。Ultra模式引入子智能体加速复杂任务+Max推理强度。7月Cerebras上线750 token/s。⚠️美国政府要求"一客一审"限量开放，短期独立开发者无法访问，但几周后将公开上线。一旦开放，子智能体模式可能替代部分RPA/自动化场景，降低一人公司运营成本——重点关注Ultra模式的定价和开放时间线。Citrinitas 熔知的嵌入模型路线需要根据旗舰模型能力调整（RAG检索质量/长上下文能力）。

- [ ] **【Claude Code v2.1.193 发布 — GitHub Releases】** | 来源：https://github.com/anthropics/claude-code/releases/tag/v2.1.193 | 🎯 Rubedo 凝华
  研究方向：Claude Code 持续迭代，2.1.193 是 6 月底新版本。SSS 当前用 Claude Code 推进 Athanor——立即查看 changelog 是否有「Hook/Sub-agent/MCP/Skill」新能力可以利用，特别是今天那条「Hook 6 玩法」对应的官方支持进展。

### 💡 探索

- [ ] **【Anthropic 报告：使用 Claude 最自动化的用户对工作安全/意义预期最乐观】** | 来源：https://www.anthropic.com/research/economic-index-june-2026-report | 🎯 OpusMagnum 巨作
  值得关注：自动化程度与「工作意义感」正相关，反直觉但有数据支撑。这意味着「AI 替代焦虑」是媒体叙事而非用户实感。一人公司恰恰是「自动化程度最高+工作意义感最强」的职业形态——这是给 SSS 自己打气，也是「一人公司」对外宣传的强卖点。

- [ ] **【$200/月替代 10 人团队 — 2026 AI SaaS 闷声发财路（里斯本独立开发者 47 天做到 10K MRR）】** | 来源：https://cloud.tencent.com/developer/article/2697559 | 🎯 OpusMagnum 巨作
  值得关注：47 天 0 → 10K MRR，没写一行手写代码；$200/月工具栈替代 10 人团队——这是「独立开发者+SaaS」的「真实」数据点（不是月入百万神话）。对照 SSS 的「一人公司+小工具」路线，评估：Athanor/Rubedo 是否能做成「$200/月工具栈产出」的成功案例？需要哪些关键能力（产品定位+获客+订阅付费）？

- [ ] **【2026 AI 副业避坑指南：90% 人赚不到钱因为 3 个原因（买课/代写/做号三大坑）】** | 来源：https://nav-ai.cn/ai-side-hustle-pitfalls-2026/ | 🎯 OpusMagnum 巨作
  值得关注：抖音/快手正在狂炒「AI 智能体+ OPC 一人公司」赛道，包装「零门槛/不用坐班/全自动」故事——大量博主正在用「卖铲子」的方式收割「想挖金子的人」。SSS 是「真挖金子的人」不是「卖铲子的人」，但要注意：同赛道竞争者涌入 + 平台「AI 批量低质内容」治理收紧 → 必须把「内容真实性+人设独特性+客户资源」做成护城河。

- [ ] **【2026 数字军工大会：360 亿方智能构建安全可控知识智能底座亮相】** | 来源：https://www.sohu.com/a/1025481111_121616897 | 🎯 OpusMagnum 巨作
  值得关注：360、北信源等大厂都在推「AI 知识库+军工安全可控」方案——「数字军工+AI 知识管理」是已被验证的赛道，主办方是「数字赋能·智驱军工能力提升」主题大会。对照 SSS 当前主业（军工效果图设计）+ Athanor（知识管理）：一人公司可以提供「行业 know-how + 客户资源」做差异化——大厂做平台，一家公司做「军工行业垂直知识库+定制化服务」，可能是「主业+副业」的最佳结合点。

---

> 📡 **筛选原则执行**：
> - ❌ 剔除：纽约时报 vs 微软/OpenAI 诉讼（法律纠纷，间接影响）、国家统计局工业利润（与个人无关）、AI 聊天机器人政治偏见（社会议题）、小鹏自动驾驶 L4（行业动态无直接变现）、400 家美国报纸起诉（法律新闻）、Reid Hoffman 评论 xAI（八卦）、Claude Sonnet 4.6/4.5 升级、OLMo Hybrid、纳米光子学芯片（技术圈变动）、OpenAI-Broadcom 推理芯片（基础设施级）、古卷解读（学术成果）
> - ✅ 保留：Leaf 实时通话 AI 分身（项目直接可复用）、Claude Code Hook 6 玩法（自动化 SOP）、Figma Config 2026（设计副业启发）、Cursor 奖励攻击（编码质量警钟）、Anthropic 报告（一人公司自我定位）、Claude Code v2.1.193（跟进工具）、360 数字军工大会（主业延展）、GPT-5.6 Sol详细（Ultra子智能体+编程benchmark）、腾讯Ardot（设计→代码闭环）、Recraft V4（SVG副业工具）、Google Flow（视觉工具发生器）
> - 💡 探索：$200/月独立开发者案例、90% 副业翻车、Anthropic 自动化与意义感、Google Flow被动收入路径
> - 🆕 与昨日去重对照：未与 6-23/6-24/6-25/6-26 任何条目重复（Leaf/Figma Config 2026/360 数字军工大会/Ardot/Recraft/Google Flow均为新项）

---

> 📡 **二次扫描补充** | 数据源：aihot 7d 精选 100 条 + WebSearch GPT-5.6详情 + AI设计工具合集 | 🕐 09:59
>
> 本轮新增 4 项未在首次扫描中出现：

### 🟡 关注（二次扫描补充）

- [ ] **【腾讯 Ardot — AI原生设计智能体平台：产品构思→矢量设计→一键MCP转代码】** | 来源：https://ardot.tencent.com/ | 🎯 Rubedo 凝华
  国内大厂首个打通「产品构思→矢量视觉设计→一键MCP转化代码」的AI设计平台。输出不是静态图片而是可编辑原生矢量资产（保留完整图层与Auto Layout），元素级精修（大白话"按钮改为磨砂高斯模糊"即时生效）。一键导入Figma，MCP协议连接CodeBuddy/Cursor/Claude Code一键转React/Vue代码。SSS作为效果图设计师，Ardot是最直接的设计→交付→收钱工具链——评估能否替代现有手动出图流程，把设计提案到代码交付压缩到一次对话。

- [ ] **【Recraft V4 Vector — 原生SVG矢量图生成+Brand Kit品牌一致性锁定】** | 来源：https://www.recraft.ai/ | 🎯 Rubedo 凝华
  不是伪矢量（位图→路径），而是真正的原生SVG（完美贝塞尔路径，可直接在Illustrator二次编辑）。内置Brand Kit锁定RGB色值和插画规范，生成的图标/插画/Logo严格保持品牌一致性。对设计副业意味着：品牌图标/插画/Logo批量出稿的成本大幅下降，一人公司快速交付品牌视觉资产的门槛更低了。

### 💡 探索（二次扫描补充）

- [ ] **【Google Flow — 纯自然语言「AI视觉工具发生器」，一键上架全球Gallery】** | 来源：https://labs.google/fx/tools/flow | 🎯 OpusMagnum 巨作
  用大白话描述→数十秒生成带参数滑块的专属微应用→一键上架全球Tools Gallery。比如「自动识别主体+90年代Lo-Fi噪声+裁剪9:16」→30秒出工具。品牌视觉规范自动化：设计工作室做「品牌专属滤镜与噪点小工具」，团队成员拖入素材一键完成色调规范+裁剪+水印。一人公司新变现路径：在Tools Gallery发布垂直品牌工具→被动收入（每次Remix/Copy都可能带来付费用户）。

- [ ] **【Next AI Draw.io — 对话式自然语言架构图生成，开源】** | 来源：https://github.com/DayuanJiang/next-ai-draw-io | 🎯 OpusMagnum 巨作
  基于Next.js的draw.io AI增强版，动动嘴就能生成系统架构图。上传白板手绘模糊图→AI用标准云厂商图标复刻美化→导出标准XML。开源，支持Vercel/Railway一键部署或Docker自托管。一人公司做知识管理/技术文档时，流程图/架构图是高频需求——这个工具可以把 Athanor 的知识可视化成本降到「说一句话」的水平。

---

## 2026-06-28

> 数据源：aihot 精选 9 条（24h）+ 100 条（7d，hasNext 截断）+ WebSearch 3 组（AI变现/设计工具/平台红利/内容变现）| 匹配项目 3 个 | 整理 09:06

### 🟡 关注

- [ ] **【Runway API 广告本地化 Recipe — 单次 API 调用翻译+适配多地区广告素材】** | 来源：https://x.com/runwayml/status/2070855164584726791 | 🎯 Rubedo 凝华
  研究方向：把静态广告和图形资产通过一次 API 调用翻译成多语言版本。对一人公司做全球化市场（如把中文内容一键本地化投放海外），这是「一条 API 替代翻译+设计团队」的实质性降本工具。评估 Runway API 定价和语言覆盖广度，看能否嵌入「中文内容→英文/日文/韩文市场」的出海内容流水线。

- [ ] **【DeepSeek 成「香饽饽」— 美国企业 AI 账单失控后 100% 切换，模型路由策略普及】** | 来源：https://www.ithome.com/0/969/400.htm | 🎯 Rubedo 凝华
  研究方向：旧金山公司 Lindy 每月 AI 账单超员工工资，切到 DeepSeek 后预计省数百万美元。「按任务匹配模型而非一刀切用最贵模型」的模型路由策略成为趋势。一人公司的 AI 工具栈必然走「能省则省、按需分配模型」路线——这条新闻是最强背书。立即整理一份「一人公司 AI 模型选型清单」：什么任务用什么模型、月成本估算、切换风险点。

- [ ] **【OpenRouter 统一图像 API — 一个接口调用 30+ 图像模型，含流式预览】** | 来源：https://openrouter.ai/blog/announcements/image-api | 🎯 Rubedo 凝华
  研究方向：整合 Google/OpenAI/Black Forest Labs/Recraft/ByteDance/xAI 等 30+ 模型，标准化请求格式 + 透明定价（Seedream 4.5 每张 $0.04、FLUX.2 Pro 每百万像素 $0.03）。GPT-5 系列支持 SSE 流式预览。一人公司做内容生成时，不必在多个 API 之间来回切换——一个端点搞定所有，且按需切模型降本。

### ⚪ 了解

- [ ] **【DeepSeek DSpark — 投机解码框架，MIT 开源，加速 V4 生成 60-85%】** | 来源：https://www.marktechpost.com/2026/06/27/deepseek-releases-dspark-a-speculative-decoding-framework-that-accelerates-deepseek-v4-per-user-generation-60-85-over-mtp-1 | 🎯 Citrinitas 熔知
  了解：不是新模型而是推理加速框架，在 DeepSeek-V4 上附加草稿模块实现无损加速，训练代码 MIT 开源。对 Citrinitas 的意义：如果 Athanor 未来接入 DeepSeek-V4 做知识检索，DSpark 能显著降低推理延迟和成本。当前优先级低，标记备查。

- [ ] **【阿里千问输入法 macOS 版 — AI 语音 300 字/分，自动润色，9 种方言】** | 来源：https://www.ithome.com/0/969/334.htm | 🎯 Rubedo 凝华
  了解：独立 AI 输入法 App，主打「语音→工整文字」的自动润色链路，纯净无广告，iOS/Android/Windows 版即将发布。这一品类（AI 原生输入法）如果开放 API 或插件体系，可能成为「桌面自动化→内容输出」的新入口。目前仅了解，等 iOS 版上线后评估。

- [ ] **【Qwen-AgentWorld — 语言世界模型，模拟 7 个域环境，1000 万条交互轨迹训练】** | 来源：https://qwen.ai/blog?id=qwen-agentworld | 🎯 Rubedo 凝华
  了解：在单个模型内模拟 MCP/Search/Terminal/SWE/GUI 等 7 个域，可作为解耦环境模拟器用于智能体 RL 训练。开源。当前离一人公司落地较远，但「环境模拟→Agent 训练」这条技术路线值得跟踪——成熟后可能让 Agent 自动化开发成本进一步下降。

### 💡 探索

- [ ] **【小红书 2026 博主转型 6 个出路 — 流量卡瓶颈后的多元变现路径】** | 来源：https://zhuanlan.zhihu.com/p/2053807668461040345 | 🎯 OpusMagnum 巨作
  小红书全面打通买手橱窗/直播带货/知识付费/私域引流/本地团购 5 条变现链路，单一广告收入模式抗风险能力越来越弱。平台大力扶持 2 分钟以上中长视频、4K 横屏、播客、互动图文等新内容形态。对一人公司意味着：小红书不再只是「种草图文」平台，正在变成「全品类内容变现闭环」——评估 Rubedo 内容策略是否需要从纯图文扩展到中长视频/播客/知识付费。

- [ ] **【2026 自媒体变现结构根本性变化 — 广告占比下滑，知识付费/私域/带货/本地服务成主流】** | 来源：https://news.sohu.com/a/1007339916_122510839 | 🎯 OpusMagnum 巨作
  2026 年自媒体广告收入占比持续下滑，「内容+私域+产品」商业闭环成为生存关键。知识付费定价区间 99-299 元，垂直领域课程/手册/模板是主流形态。对一人公司的信号：纯靠流量广告变现的「自媒体」路径已走不通，必须建立「免费内容吸引→私域沉淀→付费产品转化」的三段式漏斗。对照 Rubedo 凝华的「小红书自动化+私域运营」定位，这条趋势是需求端验证。

---

> 📡 第二次扫描 | 数据源：aihot 7d 精选第 2 页 11 条 + WebSearch 补充 4 组（AI Agent / 独立开发者 / SaaS / 副业路径）| 新增匹配 5 个 | 🕐 09:20

### 🟡 关注

- [ ] **【OpenKnowledge — 开源 AI 原生 Markdown 编辑器与 LLM 知识库】** | 来源：https://github.com/inkeep/open-knowledge | 🎯 Citrinitas 熔知
  研究方向：GPL-3.0 开源的 AI 原生 Markdown 编辑器 + LLM Wiki，定位 Obsidian/Notion 替代品。对 Citrinitas 的意义：观察「开源 + 本地优先 + LLM 增强」知识库的产品形态，看是否有可借鉴的交互或技术栈。

- [ ] **【Weave Router — 开源智能模型路由，单次请求 <50ms 自动匹配最优模型】** | 来源：https://github.com/workweave/router | 🎯 Rubedo 凝华
  研究方向：开源模型路由器，兼容 Anthropic/OpenAI/Gemini 等接口，无需修改代码即可接入，号称降低 40-70% 成本。对一人公司自动化工具链的意义：把「按任务选模型」做成基础设施，减少手动比价和切换成本。

- [ ] **【OpenRouter MCP 服务器 — 让编码 Agent 实时查模型/定价/跑测试】** | 来源：https://openrouter.ai/blog/announcements/openrouter-mcp-server | 🎯 Rubedo 凝华
  研究方向：一条命令接入 Claude Code/Codex/Cursor，让 Agent 在编辑器里直接查询最新模型能力、基准排名、定价、测试推理。这是「模型选型」自动化的关键基础设施——对 Rubedo 的 Agent 开发管线有价值。

### 💡 探索

- [ ] **【2026年适合上班族的 10 个 AI 副业方向 — 含定价与路径】** | 来源：https://blog.csdn.net/jennycisp/article/details/161416015 | 🎯 OpusMagnum 巨作
  值得关注：从 AI 智能体代部署（150-300元/单）、数字人带货、AI 漫剧、AI 自媒体、思维导图/流程图代做（15-90元/单）、简历优化到数字产品（9.9-19.9元模板）。虽然文章本身是营销导向，但列出的 10 个方向是「一人公司可切入」的市场信号。对照 SSS 技能栈，评估哪些方向最适配 Athanor/Rubedo 工具链。

- [ ] **【两人年入 27 亿？OPC 一人公司大赛 — 华为云 2026 人工智能 OPC 应用创新大赛】** | 来源：https://finance.sina.com.cn/wm/2026-06-17/doc-inictnut2722053.shtml | 🎯 OpusMagnum 巨作
  值得关注：OPC（One Person Company）概念被大厂和赛事正式推动，2 人 AI 医疗公司年入 4 亿美元、5 人以下 AI Agent/自动化工作流/AI 出海团队成为趋势。华为云联合苏州工业园提供算力/资本/专家/政策资源。这是「一人公司」从边缘叙事走向主流基础设施的标志。评估是否参赛或借鉴其资源对接模式。

---

## 2026-06-29

> 数据源：aihot 精选 7 条（24h）+ 107 条（7d，含第 2 页 7 条）+ WebSearch 8 维度 | 去重对照 6/23-6/28 全部条目 | 匹配项目 4 个 | 整理 08:50

### 🔴 本周可试

- [ ] **【Wayfinder Router — 微秒级确定性模型路由，完全离线开源】** | 来源：https://github.com/itsthelore/wayfinder-router | 🎯 Rubedo 凝华
  研究方向：通过分析提示词结构特征（长度/标题/列表/代码）在微秒级完成路由决策，无需调用其他模型判断，完全离线。支持任何 OpenAI 兼容 API。一人公司的 AI 工具栈省钱利器——把「什么任务用什么模型」做成基础设施层，不用每次手动比价切换。对照 Rubedo 的自动化管线，评估能否嵌入作为模型调度中间件。

- [ ] **【CEO-Bench — 普林斯顿 500 天 AI 创业测试：仅 3 个模型盈利】** | 来源：https://the-decoder.com/only-three-ai-models-finished-above-starting-capital-in-a-500-day-startup-survival-test | 🎯 Rubedo 凝华 + 💡 OpusMagnum 巨作
  研究方向：14 个 AI 模型在模拟 SaaS 公司运营 500 天（起始 100 万美元），仅 Claude Fable 5（最佳 4715 万）、Claude Opus 4.8（2780 万）、GPT-5.5（2130 万）盈利。一个不用 LLM 的简单规则启发式也做到 1576 万。多数模型在结束前破产。核心发现：AI 的长期战略决策和连贯性仍是短板——对一人公司的启示：别把商业决策外包给 AI，AI 是执行工具不是 CEO。

### 🟡 关注

- [ ] **【VibeThinker-3B — 新浪开源 3B 推理模型：逻辑可压缩，事实知识不能】** | 来源：https://the-decoder.com/sinas-open-model-vibethinker-3b-aims-to-show-reasoning-compresses-well-but-factual-knowledge-doesnt | 🎯 Citrinitas 熔知
  研究方向：仅 3B 参数，数学编程基准持平大 200-333 倍的模型，但知识密集型 GPQA 大幅落后。提出「参数压缩-覆盖假说」：逻辑推理依赖少数可压缩模式，广泛世界知识仍需大参数。对 Citrinitas 的意义：知识管理系统中「推理」和「存储」可以分离——小模型做推理编排，大模型做知识检索——降低成本。

- [ ] **【Claude Tag — @Claude 在 Slack 频道中协作，可自主推进数小时】** | 来源：https://www.anthropic.com/news/introducing-claude-tag | 🎯 Rubedo 凝华
  研究方向：在 Slack 中 @Claude 即可委托任务，记住频道上下文、支持多用户交互、可主动更新未解决线程。这是「AI 员工」嵌入已有工作流的产品形态——不是另外开一个新 App，而是在已有协作工具中无缝嵌入。对 Rubedo 的启示：自动化不一定要从零建 App，嵌入飞书/企微/钉钉可能是更低摩擦的路径。

- [ ] **【Krea 2 技术报告正式发布 — 设计工具的训练数据与架构公开】** | 来源：https://www.krea.ai/blog/krea-2-technical-report | 🎯 Rubedo 凝华
  研究方向：Krea 公开了 Krea 2 的数据、架构和训练技术细节。对设计副业来说，了解 AI 设计工具的底层有助于精准使用而非盲目跟风。SSS 作为效果图设计师，可以评估 Krea 2 的「风格控制+实时编辑」能力是否适合军工效果图场景。

- [ ] **【ChatGPT Bidi 1 — 双向语音模型上线测试，支持中途打断】** | 来源：https://www.ithome.com/0/967/852.htm | 🎯 Rubedo 凝华 + Nigredo 馏析
  研究方向：OpenAI 未官宣但用户已发现 Bidi 1 双向语音模型，支持边说话边监听、对话中途打断切换指令。这是「语音交互」从一问一答走向实时对话的标志。对 Nigredo（语音处理管线）和 Rubedo（语音驱动的自动化）都有潜在价值——但当前优先级低于现有管线稳定性，标记关注。

### 💡 探索

- [ ] **【一人 SaaS 创业指南 + AI Agent 工具栈 — 2026 年从 0 到月入 3 万的可复制路线】** | 来源：https://xopcx.com/articles/article-2026-05-20-yiren-solo-saas-2026 | 🎯 OpusMagnum 巨作
  值得关注：含获客/交付/财务三大核心系统的 AI 自动化方案，7 步启动路线图。与之前「$200/月替代 10 人团队」和「47 天 10K MRR」案例互补——这些是「一人公司工具链」的实操手册而非神话故事。

- [ ] **【8 款低成本创业 AI 工具 — 一人副业高效落地必备】** | 来源：https://www.toutiao.com/article/7647437211037729314/ | 🎯 OpusMagnum 巨作
  值得关注：元宝/Notion/Kimi 等工具的组合使用方案，从轻量化运营到技术开发的完整工具栈。对照 SSS 当前工具栈（Claude Code + NiceGUI + Python），是否有可以替换的低成本选项？

> 📡 **筛选原则执行**：
> - ❌ 剔除：Grok 4.5（大企业模型发布）、Artifacts 22（纯行业生态总览）、文明VI AI 对决（娱乐向）、小米自动驾驶（无关）、五眼联盟网络威胁（安全议题）、Oracle 裁员（企业人事）、AI 招聘偏见（社会议题）、GitHub 开源联盟（政策游说）、OpenAI Daybreak 安全计划（企业安全）、Flock 警长滥用（社会新闻）、DFlash 推理加速（基础设施）、苹果 LLM 评委面板（学术）、OpenRouter 数据驻留（企业合规）、Seed2.1（已在 6/25 覆盖）
> - ✅ 保留：Wayfinder Router、CEO-Bench、VibeThinker-3B、Claude Tag、Krea 2、ChatGPT Bidi 1、一人 SaaS 指南、8 款低成本工具
> - 🆕 与 6/23-6/28 去重对照：全部 8 条均未在历史队列中出现
> - 📊 今日 24h 精选仅 7 条（偏少），7d 第 2 页仅 7 条补充有限，WebSearch 补充了实操指南维度

---

> 📡 **二次扫描补充** | 数据源：WebSearch 副业/一人公司/低成本创业 5 组 | 新增 2 条未在首次扫描中出现 | 🕐 08:50

### 🟡 关注（二次扫描补充）

- [ ] **【5 个低成本 AI 创业项目（6/21 实操验证）— 含定价与收入区间】** | 来源：https://k.sina.com.cn/article_7857201856_1d45362c001907487u.html | 🎯 Rubedo 凝华
  研究方向：AI 简历优化（99-299 元/单，月入 1.5-3 万，小红书+闲鱼获客）、AI 数字人定制（2-5 万/月）、AI PPT 定制（200-1000 元/单，月入 1-3 万）、AI 儿童绘本（39-99 元/本，月销 300-500 本）、AI 电商选品服务（500-2000 元/家，月入 10-30 万）。其中 AI PPT/AI 绘本/AI 数字人都与 SSS 设计师背景直接挂钩——设计能力是差异化护城河。评估哪个方向与现有工具栈最适配。

- [ ] **【AI 赋能单人轻创业三大低门槛赛道 — 短视频代运营/数字员工租赁/智能体定制培训】** | 来源：https://baijiahao.baidu.com/s?id=1868687374528166968 | 🎯 Rubedo 凝华
  研究方向：不同于「零代码平台做应用」思路，这三条赛道偏「服务型」——AI 短视频代运营（替商家批量出内容）、数字员工租赁（按任务量/时长收费，零库存零囤货）、智能体定制培训（帮企业优化 AI 模型，纯技术服务）。对 SSS 而言，「AI 短视频代运营」可复用 Nigredo/Rubedo 的图文+视频流水线；「数字员工租赁」是 Rubedo 自动化的另一种定价模型参考。

---

## 2026-07-01

> 数据源：aihot 精选 19 条（24h）+ WebSearch 4 组（AI变现/一人公司/设计副业/solopreneur）| 去重对照 6/23-6/29 全部条目 | 匹配项目 2 个 | 整理 18:05

### 🔴 本周可试

- [ ] **【Claude Sonnet 5 — 性能接近 Opus 4.8、价格砍半，8 月底前特惠 $2/$10 百万 Token】** | 来源：https://www.anthropic.com/news/claude-sonnet-5 | 🎯 Rubedo 凝华
  研究方向：Anthropic 新一代 Sonnet 模型，带计划/浏览器/终端工具使用能力，可自主运行。即日起至 8/31 特惠价：输入 $2/百万、输出 $10/百万（之后恢复 $3/$15）。一人公司用 Claude Code 的所有编码/自动化/Agent 任务成本都下降了——在 8 月底前赶工的价值更高。立即评估 Sonnet 5 在日常 Athanor 开发中能否替代 Opus 4.8，月成本能省多少。

- [ ] **【shot-scraper video — 让 AI Agent 录制浏览器工作演示视频，一行 YAML 定义操作】** | 来源：https://simonwillison.net/2026/Jun/30/shot-scraper-video | 🎯 Rubedo 凝华
  研究方向：shot-scraper 1.10 新增 video 命令，通过 storyboard.yml 定义操作步骤，利用 Playwright screencast 录制浏览器演示视频。Simon Willison 刻意设计 --help 足够详细，让编码 Agent 可直接用。对一人公司意味着：自动化录制产品演示/教程/交付物验收视频——不用手动录屏。评估能否嵌入 Rubedo 的「交付自动化」SOP（做完一个项目→自动生成交付演示视频）。

### 🟡 关注

- [ ] **【mattpocockuk /writing-great-skills — 编写可预测 AI Skill 的系统方法论】** | 来源：https://x.com/shao__meng/status/2072126769986220157 | 🎯 Rubedo 凝华
  研究方向：区分 model-invoked vs user-invoked Skill、三层渐进式信息结构（主步骤/参考/外部文件）、每步明确完成标准、用 leading word 压缩行为要求。诊断五种失败模式：Premature completion/Duplication/Sediment/Sprawl/No-op，并提供 No-op 测试。直接对照 Rubedo 凝华的 SOP Skill 体系，检查当前 Skill 是否有这些失败模式——尤其「Sediment 沉淀」在多个 Skill 积累后可能悄然出现。

- [ ] **【Anthropic 在 Claude Code 中植入隐写术识别中国用户 — 社区逆向发现引发信任危机】** | 来源：https://mp.weixin.qq.com/s/yLb4T2UC16ebKHApdBbgwW | 🎯 Rubedo 凝华
  研究方向：Anthropic 读取本地时区（Asia/Shanghai 或 Asia/Urumqi）+ ANTHROPIC_BASE_URL 环境变量，与加密域名列表比对识别中国用户，并将日期格式做隐写标记传回服务器。短期：SSS 作为中国用户，Claude Code 使用不受影响，但需关注 Anthropic 的后续反应和社区反弹。长期：如果 Claude 对中国用户收紧访问，需要准备备用方案（如 OpenRouter 调用、DeepSeek/美团 LongCat 等国产替代）。

- [ ] **【NotebookLM Short Video Overviews — 复杂资料一键转 60 秒竖屏讲解视频，Web 英文版全量上线】** | 来源：https://x.com/NotebookLM/status/2072043680442245276 | 🎯 Rubedo 凝华
  研究方向：Google 的 NotebookLM 正式向所有英文 Web 用户推出短视频概览功能——上传文档/链接→AI 自动生成 60 秒竖屏讲解视频。Google AI Ultra/Pro 订阅者已可用，免费用户即将开放。这是「文字→视频」的免费工具链新入口——评估能否把 Rubedo 自动化产出（分析报告/拆解笔记）喂入 NotebookLM 生成视频，作为小红书/B站内容分发的低成本起号素材。

- [ ] **【Claude Code 入门：智能体循环 — 四种循环模式 + SKILL.md 端到端自检】** | 来源：https://claude.com/blog/getting-started-with-loops | 🎯 Rubedo 凝华
  研究方向：Claude Code 团队官方指南，划分四种智能体循环：turn-based（用户触发自判断完成）、goal-based（/goal 命令设可验证标准+最大轮次）、time-based（/loop 按时间间隔重复，/schedule 移至云端）、proactive（基于事件或计划自动运行）。这是 AI Agent 自动化从「你盯着跑」到「全自动」的操作手册——直接对标 Rubedo 凝华「零人工干预」原则，立即对照四种循环模式重新设计 Rubedo 的任务调度层。配合 6/27 的 Hook 6 玩法，形成「Hook 事件 + 循环模式」双轨自动化架构。

### ⚪ 了解

- [ ] **【Acti — AI 智能体直接嵌入手机键盘，长按字母触发自定义 Skill】** | 来源：https://techcrunch.com/2026/06/30/acti-puts-ai-agents-directly-into-your-smartphone-keyboard | 🎯 Rubedo 凝华
  了解：新加坡初创公司，530 万美元种子轮，基于 Gemini 的智能体键盘。用自然语言创建 Skills（如长按 T=翻译、C=发送会议链接），本地优先架构。早期测试者两周内创建 1000+ Skills。这是「手机端 Agent」的新入口形态——不是独立 App 而是嵌入键盘这个最高频入口。目前不直接落地，但标记：「键盘级 Agent」如果开放 API 或自定义 Skill，可能成为一人公司「移动端自动化+私域运营」的新型触点。

- [ ] **【Nano Banana 2 Lite + Gemini Omni Flash — Google 最便宜的图/视频生成 API 上线】** | 来源：https://deepmind.google/blog/start-building-with-nano-banana-2-lite-and-gemini-omni-flash | 🎯 Rubedo 凝华
  了解：Nano Banana 2 Lite 文生图 4 秒出图，$0.034/张；Gemini Omni Flash 视频生成 $0.10/秒。API 已开放。对一人公司内容生产来说，图像成本降到几乎为零（100 张图才 $3.4），视频生成也有价格锚点。当前不直接落地，但跟踪——等图片生成质量稳定后，评估能否嵌入 Rubedo「小红书配图」自动化流水线。

### 💡 探索

- [ ] **【2026 年国内开发者用 AI 挣钱的 6 条真实路径（附成本账单）】** | 来源：https://juejin.cn/post/7621058019766698034 | 🎯 OpusMagnum 巨作
  值得关注：掘金上的实操复盘，6 条路径含工具成本/收入区间/时间线，API 价格已打到底（Qwen3.5-Flash 输入 0.2 元/百万 token）。对比之前收录的「10 AI 副业方向」「一人 SaaS 创业指南」，这篇偏「国内 API 价格战背景下」的实操视角——技术门槛降低但「能调 API ≠ 能赚钱」，差异化在行业 know-how。

> 📡 **筛选原则执行**：
> - ❌ 剔除：NVIDIA Nemotron（大企业/需2×H100）、AWS 10亿驻场（纯企业部署）、美团 LongCat-2.0（50K卡集群）、库克Siri欧盟（大企业监管）、AI 数学难题（纯学术）、Claude Science（科研工具）、ADK Go 2.0（企业框架）、Apple Creator Studio（大厂产品）、Claude Desktop Linux（平台扩展）、Grant Sanderson 访谈（学术观点）、Meta 测试竞品（企业八卦）
> - ✅ 保留：Claude Sonnet 5、shot-scraper video、/writing-great-skills、Anthropic 隐写术、NotebookLM Short Video、Claude Code 智能体循环、Acti 键盘、Nano Banana 2 Lite、国内开发者挣钱路径
> - 🆕 与 6/23-6/29 去重对照：全部 9 条均未在历史队列中出现
> - 🔍 今日 24h 精选 19 条中仅 8 条（42%）通过一人公司过滤，剔除率 58%——Vibe 偏大企业/学术。搜索补充 1 条实操指南。

## 2026-07-03

> 数据源：aihot 精选 24 条（24h）+ WebSearch 4 组（AI变现/一人公司/Agent自动化/solopreneur）| 去重对照 6/23-7/01 全部条目 | 匹配项目 3 个 | 整理 08:50

### 🔴 本周可试

- [ ] **【Fable 5 自主优化 AIHOT 网站 SEO/GEO 全记录 — 22 个 Agent 并行、自行提交 CDN 工单、发现安全漏洞】** | 来源：https://mp.weixin.qq.com/s/L6R_SPWlOBv6dI0wWWHQrg | 🎯 Rubedo 凝华
  研究方向：Claude Fable 5 自主启动 22 个 Agent 调研 40 分钟，自行否定 Opus 4.8 的 Cloudflare 方案（无法国内直连），改用火山引擎 CDN；自行找到工单入口提交专业工单，22 分钟开通；发现工程师漏笔问题并礼貌追问；发现安全漏洞自行加暗号验证。最终生成运维文档含续期步骤。这是「Agent 全自主运维」的真实案例——对照 Rubedo 的「桌面自动化+私域运营」，Fable 5 的「自主判断→自主执行→自主纠错→自主文档」四段式是最高级别的自动化模板。立即研究：哪些 Rubedo 场景可以达到类似的「全自主」水平？

- [ ] **【阿里 Page Agent — 开源 JS 库实现网页 DOM 自然语言操控，MIT 协议】** | 来源：https://www.marktechpost.com/2026/07/02/meet-alibabas-page-agent-a-javascript-in-page-gui-agent-that-controls-web-interfaces-with-natural-language-through-the-dom | 🎯 Rubedo 凝华
  研究方向：嵌入网页后可用自然语言指令直接操作 DOM 元素（点击、填表等），不依赖截图或多模态模型，将 DOM 脱水压缩为 FlatDomTree 文本映射让纯文本模型精准执行。继承用户 cookies 和会话，无需独立后端。MIT 协议开源。对一人公司自动化意味着：「轻量级网页 RPA」不需要 Playwright/Puppeteer 的重型基础设施——一个 JS 库嵌入即可。评估能否嵌入小红书/酷家乐等平台做自动化采集和操作。

- [ ] **【Fable 5 RLI 基准 16.1% — AI 可完成 16% 自由职业项目，8 个月增长 6 倍】** | 来源：https://the-decoder.com/ai-agents-can-now-complete-16-percent-of-freelance-jobs-at-pro-quality-up-from-2-5-percent-eight-months-ago | 🎯 Rubedo 凝华 + 💡 OpusMagnum 巨作
  研究方向：AI 智能体完成 240 个付费自由职业项目（总值 14.4 万美元）的专业质量比例从 2.5%→16.1%，8 个月增长 6 倍。Fable 5 16.1% > Opus 4.8 8.3% > GPT-5.5 6.3%。对一人公司的双重信号：(1) 利好——AI 工具让单人产出逼近专业水准，一人公司成本优势更大；(2) 威胁——低端自由职业市场正在被 AI 直接替代，必须往「AI 做不到的专业品味+行业 know-how」方向升级。

- [ ] **【browser-use video-use — 开源 AI 视频剪辑 Skill，让编码 Agent 剪视频】** | 来源：https://x.com/shao__meng/status/2072644710523691110 | 🎯 Nigredo 馏析 + Rubedo 凝华
  研究方向：browser-use 团队推出面向 Codex/Claude Code 的开源 Skill「video-use」，让 LLM 通过 ElevenLabs Scribe 将音频转写为 ~12KB 文本（含逐词时间戳、说话人分离、事件标记），仅在决策点生成 PNG 帧图。技术流水线：转写→打包→生成 JSON EDL→ffmpeg 渲染→最多 3 轮自评估。这是「AI 剪辑」从概念走向实用的标志——对照 Nigredo（视频处理管线）和 Rubedo（小红书/短视频内容生产），video-use 的「转写+EDL+ffmpeg」三段式可以直接嵌入现有管线。评估实际剪辑质量和渲染稳定性。

- [ ] **【天工 3.2 Skywork Tags — AI 智能体加入工作群聊，Slack/飞书/钉钉/Discord/Telegram】** | 来源：https://mp.weixin.qq.com/s/OqL6ID-mAel8XN-slYgXOA | 🎯 Rubedo 凝华
  研究方向：昆仑万维天工 3.2 发布 Skywork Tags，Agent 以团队成员身份接入即时通讯工具，在原有工作群中 @Skywork 参与讨论，无需切换窗口或迁移数据。共享版 Agent 持续吸收团队上下文后表现反超精心调教的个人版。这是「Agent 嵌入协作流」的产品形态——对照 6/29 收录的 Claude Tag（Slack 专用），Skywork Tags 覆盖更多国内平台（飞书/钉钉），且「共享版 > 个人版」的发现意味着「团队 Agent」可能比「个人 Agent」更有商业价值。评估能否作为 Rubedo「私域运营 Agent」的低成本部署选项。

### 🟡 关注

- [ ] **【花旗/Adobe/Atlassian 限制员工使用 AI 旗舰模型 — 成本失控的警钟】** | 来源：https://www.ithome.com/0/971/937.htm | 🎯 Rubedo 凝华
  研究方向：花旗禁用 Claude Opus 4.6/4.7 和 GPT-5.5，Adobe 终止 Claude 无限制使用协议，Atlassian 月支出从 500 万飙至 1500 万美元。GitHub 改用开源模型并测试按量计费。这是「AI 成本失控」的真实数据——一人公司更要警惕：「旗舰模型=高成本」不是大企业才面临的问题。对照 6/28 收录的「DeepSeek 模型路由省钱」和「Wayfinder Router」，立即整理一份「一人公司 AI 成本管控 SOP」：什么任务用什么模型、月预算上限、切换触发条件。

- [ ] **【千问 C端 Agent Harness — 多快好省工程哲学，Token 消耗仅为海外产品 1/10】** | 来源：https://mp.weixin.qq.com/s/l70iUM0bIpG9EdV9Px7QPQ | 🎯 Rubedo 凝华
  研究方向：千问团队总结 Agent 工程「多快好省」方法论：执行时间降至初始 1/3，Token 消耗仅为海外产品 1/10。提出从 Prompt Engineering→Harness Engineering→AIWare Engineering 的演进路径，强调「低功耗，够用就行」。核心四组件：User Memory / Environment / Task System / Assistant，「情商」是主动服务最难环节。对一人公司的意义：「够用就行」原则直接对标「非必要不用大模型」——国产 Agent 方案的成本优势已经验证。评估千问 App 胶囊入口能否作为 Rubedo 的 C端 Agent 部署渠道。

- [ ] **【Kimi K2.7 Code — 开源权重模型正式上线 GitHub Copilot，首个可选开源模型】** | 来源：https://github.blog/changelog/2026-07-01-kimi-k2-7-is-now-available-in-github-copilot | 🎯 Rubedo 凝华
  研究方向：Kimi K2.7 Code 成为 Copilot 模型选择器首个开源权重选项，GitHub 托管于 Azure，按供应商列表价格用量计费。逐步推送至 Pro/Pro+/Max 用户，后续扩展至 Business/Enterprise。对一人公司编码成本优化：开源权重模型进入主流 IDE——意味着编码成本可以进一步降低。评估 K2.7 Code 在日常 Athanor 开发中的表现，与 Claude Sonnet 5 对比性价比。

- [ ] **【Emil Kowalski 设计工程师 Skills — 让 AI 编码工具具备 UI 动画审美判断】** | 来源：https://x.com/shao__meng/status/2072484635955900792 | 🎯 Rubedo 凝华
  研究方向：Vercel/Linear 前设计师将多年 UI/动画原则沉淀为三个 Skill：动画必须有理由；高频操作禁用动画；控制在 300ms 内；只动画 transform 和 opacity；入口从 scale(0.95)+opacity:0 开始；尊重 prefers-reduced-motion。review-animations 严格审查动画代码输出 Before/After/Why 表格。SSS 作为效果图设计师，这些 Skill 是「设计审美→AI 编码」的直接桥梁——立即研究能否把类似的设计原则 Skill 化（军工效果图风格→UI 组件→代码），形成 Rubedo 的设计差异化。

### ⚪ 了解

- [ ] **【Fable 5 仅 $4.44 搭建 Rube Goldberg 机器 — 低成本自主 Agent 演示】** | 来源：https://x.com/OpenRouter/status/2072738704922439689 | 🎯 Rubedo 凝华
  了解：Fable 5 用 $4.44 完成复杂连锁机械搭建。这是「Agent 低成本自主执行」的极端演示——但 Rube Goldberg 机器本身是趣味项目，不具备直接商业化价值。了解 Agent 的成本边界和自主能力上限。

- [ ] **【Senior SWE-Bench — 评估 AI 智能体作为高级工程师，最强模型 75%+ 任务未达高级水平】** | 来源：https://senior-swe-bench.snorkel.ai/ | 🎯 Rubedo 凝华
  了解：开源基准测试，Claude Opus 4.8 搭配 Mini-SWE-Agent 通过率 24.0%，Sonnet 5 为 19.4%，GPT-5.5 为 16.0%。最强前沿模型在超 75% 任务中未能达到高级工程师级别。对 SSS 的信号：AI 编码工具在「高级工程师级复杂任务」上仍有大量失败——别完全信任 AI 输出，保留人类审查环节。

- [ ] **【AI 版支付宝阿宝开放公测 — 对话式办事助手，资金操作需本人确认】** | 来源：https://www.ithome.com/0/971/469.htm | 🎯 Rubedo 凝华
  了解：支付宝 AI 助手开放公测，对话方式安排办事（查公积金等），所有资金变动需本人确认。平台级 AI 助手进一步验证「对话→操作→确认」交互模式的普及——对 Rubedo 的 Agent 交互设计有参考价值，但不直接落地。

### 💡 探索

- [ ] **【2026 OPC 深度研究报告：AI 工具到创业生态，超级个体月入 30 万实战路径】** | 来源：https://www.opcwang.com/article/2026yi-ren-gong-si-opcshen-du-yan-jiu-bao-gao-cong-ai-gong-ju-dao-chuang-ye-sheng-tai-chao-ji-ge-ti-yue-ru-30mo-shi-zhan-lu-jing | 🎯 OpusMagnum 巨作
  值得关注：系统解剖一人公司从 AI 编程工具到流量平台的完整创业生态，「超级个体月入 30 万」的实战路径分析。与之前收录的「一人 SaaS 创业指南」「47 天 10K MRR」「10 AI 副业方向」互补——这篇偏「国内 OPC 生态全景」视角，包含工具栈/获客/合规/运营四大维度。对照 SSS 的 Athanor 项目，看哪些路径可以直接复用。

> 📡 **筛选原则执行**：
> - ❌ 剔除：得州特斯拉FSD致命车祸（社会新闻）、扎克伯格Agent进展不如预期（大企业内部动态）、Mythos网络安全（学术/安全议题）、Microsoft Frontier Company 25亿美元（纯大企业部署）、SGLang Agent开发（ML基础设施）、Anthropic五角大楼控权（军事/政治）、可灵AI 20亿美元注资（大企业融资）、谷歌用电量增长37%（基础设施）、宇树科技IPO（企业动态）、ghealth CLI（健康数据工具，完全无关）、OpenAI提议美国政府持股5%（企业/政治）
> - ✅ 保留：Fable 5 SEO/GEO自主优化（Agent自动化标杆）、Page Agent（轻量网页RPA）、RLI 16.1%（自由职业市场巨变）、browser-use video-use（视频剪辑Skill）、Skywork Tags（Agent入群聊）、花旗Adobe成本失控（成本管控信号）、千问Harness（国产Agent省钱）、Kimi K2.7 Copilot（开源编码模型）、Emil Kowalski设计Skill（设计→编码）、Fable 5 $4.44（成本边界演示）、Senior SWE-Bench（AI编码质量参考）、支付宝阿宝（平台演进信号）
> - 🆕 与 6/23-7/01 去重对照：全部 12+1 条均未在历史队列中出现（Fable 5 SEO/GEO ≠ CEO-Bench 6/29、RLI ≠ CEO-Bench、video-use ≠ shot-scraper 7/01、Skywork Tags ≠ Claude Tag 6/29、Page Agent ≠ 任何历史项、花旗Adobe成本 ≠ DeepSeek路由6/28）
> - 🔍 今日 24h 精选 24 条中仅 13 条（54%）通过一人公司过滤，剔除率 46%。WebSearch 补充 1 条 OPC 研报。

> 📡 **二次扫描补充** | 数据源：WebSearch 8 组（副业/一人公司/独立开发者/变现/AI设计/小红书自动化/平台红利/低成本创业）+ aihot 7d 精选第 2 页 | 新增 3 条未在首次扫描中出现 | 🕐 08:50

### 🔴 本周可试（二次扫描补充）

- [ ] **【构建 AI 智能体应优先设计路由 — 正确路由降本 90%+，Coinbase 已验证】** | 来源：https://www.tomtunguz.com/ai-execution-routing | 🎯 Citrinitas 熔知
  VC 分析：路由决定每个请求由哪层模型处理，70-80% 流量可走免费本地模型或异步推理，AI 开销降低 90%+。Coinbase 通过更好的默认设置+路由+缓存将 AI 支出减半。路由三层架构：技能分类器→路由器→模型选择器。本地计算近零成本，异步批量推理比实时推理便宜两个数量级。对 Citrinitas 熔知直接参考——知识管理管线的「搜索/嵌入/推理」可对应路由三层，避免成本失控。

### 🟡 关注（二次扫描补充）

- [ ] **【xAI Voice Agent Builder — 2 分钟无代码创建生产级语音 Agent】** | 来源：https://x.ai/news/grok-voice-agent-builder | 🎯 Nigredo 馏析
  无代码平台创建生产级语音智能体：集成电话/知识检索/工具/MCP/Guardrails，语音到语音路径，τ-voice Bench 67.3% 领先 Gemini 3.1 Flash Live（43.8%）和 GPT Realtime 1.5（35.3%）。80+ 语音+声音克隆，附赠免费电话号码，$0.05/分钟。对 Nigredo 馏析的语音处理管线提供低门槛方案——评估能否替代/补充现有语音转文字链路，以及作为 Rubedo「销售陪谈/客服 Agent」的语音基础。

- [ ] **【小红书 MCP Skills 全集 — 8 个 Agent Skills 覆盖运营全流程】** | 来源：https://txtmix.com/posts/tech/xiaohongshu-mcp-skills-complete-guide/ | 🎯 Rubedo 凝华
  一条命令搞定小红书运营自动化：登录/发笔记/搜索/互动/涨粉全流程，兼容 Claude Code/Cursor/Codex 等 AI 编码工具。对凝华的「小红书自动化+私域运营」直接可用——评估能否嵌入 Rubedo 内容变现流水线，把小红书运营 SOP 从手动→全自动。

### 💡 探索（二次扫描补充）

- [ ] **【支付宝阿宝 AI 助手 — 8 亿用户级的 AI 服务分发窗口，应从「了解」升级为「探索」】** | 来源：https://www.ithome.com/0/971/469.htm | 🎯 OpusMagnum 巨作
  首次扫描列入 ⚪了解，二次扫描升级为 💡探索。支付宝级平台开放 AI 助手入口，以对话方式安排办事（查公积金→自动匹配小程序），所有资金变动需用户确认。8 亿用户级别的「AI 服务分发窗口」——一人公司可开发阿宝小程序/技能，进入支付宝生态变现。评估阿宝的技能/插件接入接口和开放能力。

---

## 2026-07-08

> 数据源：aihot 精选 18 条（24h，7/6-7/7）+ WebSearch 7 组（副业/一人公司/开源工具/AI设计/小红书/平台红利）| 去重对照 6/23-7/03 全部条目 | 匹配项目 4 个 | 整理 08:50

### 🔴 本周可试

- [ ] **【tokhub.me — 向阳乔木开源 API 中转站监测网站，真实充值调用监控稳定性，Docker 一键部署】** | 来源：https://aihot.virxact.com/items/cmr9apy0u02hxslsmxllfd51t | 🎯 Rubedo 凝华
  研究方向：通过真实充值调用监控各家 API 稳定性，也可作公司内部 Token/网关统一管理，解决选型头疼问题。这直接服务于 Athanor 当前的「摄入管线稳定性修复」重心——用看板提前发现单一 API 抖动，避免管线中断；同时统一网关降低多模型调用成本。本周可试：Docker 一键部署 tokhub，接入 Athanor 现有 API key，跑一周稳定性看板。

- [ ] **【小红书变现真相 2026 — 网创资源平台实测对比 + 变现通用避坑】** | 来源：https://www.sohu.com/a/1045944588_122652693 | 🎯 Rubedo 凝华
  研究方向：3 天前的实测文，从资源覆盖/时效性/落地性/便捷性/稳定性五维度拆解主流网创资源平台，并整理小红书变现行业通用避坑。SSS 作为效果图设计师，小红书内容变现是最直接的起号路径——本周研究「资源平台 + 小红书变现」组合打法，对照已收录的小红书 MCP Skills 全集，设计 SSS 的小红书起号→私域转化 SOP。

### 🟡 关注

- [ ] **【Fun-ASR-Realtime — 通义实验室实时语音识别，单模型 30 语言 16 方言，百毫秒级延迟】** | 来源：https://aihot.virxact.com/items/cmr8tzbde00jjsllsayhpgjqg | 🎯 Nigredo 馏析
  研究方向：流式延迟百毫秒级，API 上阿里云百炼，单模型覆盖多语多方言。Nigredo 馏析的语音转文字管线可直接评估——是否替代或补充现有转写引擎（通义/讯飞/飞书妙记），尤其多语种/方言场景。关注 API 定价与本地部署可行性。

- [ ] **【OpenClaw 登陆 HuggingFace 本地应用 — 一键部署完全本地、无云端、无密钥 Agent】** | 来源：https://aihot.virxact.com/items/cmr9jbw7a0085ihe85luucw73 | 🎯 Rubedo 凝华
  研究方向：可选任意 GGUF/MLX 模型，复制设置即得本地工具调用 Agent，隐私敏感场景零云端零密钥。对 Rubedo「桌面自动化 + 私域运营」是低成本隐私方案——评估能否承载本地 RPA/自动化任务，避开云端 Agent 的数据合规风险。

- [ ] **【「三周前，我不小心创办了一家小公司」— 父亲为自闭症儿子开发沟通应用，AI 图像 + 声音克隆找到 PMF】** | 来源：https://aihot.virxact.com/items/cmr83ashr0189sl04hhietwtx | 🎯 Rubedo 凝华 + 💡 OpusMagnum 巨作
  研究方向：一人公司真实 PMF 案例——用 AI 图像生成 + 声音克隆解决被忽视的细分需求，意外跑通。对照 SSS「找被忽视的行业 know-how 需求」路径，研究其「需求发现→MVP→PMF」三段式，能否复用到 Athanor/Rubedo 的垂直知识库方向（军工行业 know-how 正是最被大厂做不重的细分）。

- [ ] **【GitHub 开源盘点：AI Agent 基础设施 + 端侧自托管工具爆发式增长（odysseus 等）】** | 来源：http://www.mynw.cn/news/1087812.html | 🎯 Rubedo 凝华
  研究方向：1 天前的周度盘点，AI Agent 基础设施和端侧自托管工具爆发，重点提及 odysseus（本地...）。这与 OpenClaw/OpenScience 同属「低成本开源自托管」趋势——评估这些端侧工具能否构成 Rubedo 的零成本执行底座，降低对云端 API 的依赖与成本。

### ⚪ 了解

- [ ] **【OpenScience — Apache 2.0 开源 AI 科研工作台，本地运行自带密钥，npm 安装即用】** | 来源：https://aihot.virxact.com/items/cmr8reau2005fslvpmqjll6du | 🎯 Rubedo 凝华
  了解：覆盖多学科、支持任意模型切换的本地科研工作台，数据不出本机。对「低成本自托管 AI 工具链」是补充选项——当前优先级低，标记备查，等 Rubedo 需要本地知识/研究工作台时评估。

- [ ] **【Claude Fable 5 下线前必跑的 8 个实战 Prompt — 提升构建速度、降 token 开销、可迁移 API 计费】** | 来源：https://aihot.virxact.com/items/cmr8j9weh02kxsl0dy08683oe | 🎯 Rubedo 凝华
  了解：含自主实验、工作模式固化等 8 个实战 Prompt，强调迁至 API 计费后降 token 开销。对 SSS 用 Claude Code 推进 Athanor 是直接的提示词降本参考——了解其「工作模式固化」思路，看能否沉淀为 Rubedo 的 SOP Skill。

### 💡 探索

- [ ] **【斯坦福数据：AI 颠覆初级程序员就业，22-25 岁开发者就业降 19%、入门岗减 28%】** | 来源：https://aihot.virxact.com/items/cmr96dq8400pdslsmu56r8muy | 🎯 OpusMagnum 巨作
  值得关注：智能体编程兴起使「初级程序员」头衔消亡，编程变为基本能力。对一人公司是宏观结构利好——技能洼地被 AI 填平，单人产出逼近专业水准（呼应 Fable 5 RLI 16.1%）。但低端代工市场被压缩，必须往「AI 做不到的专业品味 + 行业 know-how」升级。这是巨作层面的战略储备信号：一人公司的护城河不在「会写代码」，而在「行业判断 + 客户资源 + 审美」。

> 📡 **筛选原则执行**：
> - ❌ 剔除：Apple APMs 安全对齐（纯学术）、Tomer Tunguz AI 世界观（观点无应用）、Meta 伪装未成年（安全丑闻）、AT&T 专利法令/语料版税（政策观点）、Runway 巴黎办公室（大企业布局）、SK 海力士 IPO（大企业）、NVIDIA Kyber 延迟（算力供给）、扎克伯格千兆瓦集群（大企业）、欧盟 Chat Control（监管无变现）、Google 隐私默认训练 AI（平台变更但无赚钱窗口）、SGLang DSpark（已在 6/28 覆盖）
> - ✅ 保留：tokhub.me（Agent 稳定性监测）、Fun-ASR-Realtime（Nigredo 语音）、OpenClaw（本地 Agent）、父亲小公司（一人公司 PMF）、GitHub 开源盘点（端侧自托管）、OpenScience（自托管工作台）、Claude Fable 5 Prompt（提示词降本）、小红书变现真相（内容变现）、斯坦福就业数据（宏观结构）
> - 🆕 与 6/23-7/03 去重对照：全部 9 条均未在历史队列中出现
> - 🔍 今日 24h 精选 18 条中 9 条（50%）通过一人公司过滤，剔除率 50%，偏大企业/学术/监管；WebSearch 补充 2 条新鲜内容（小红书变现 3 天前、GitHub 盘点 1 天前）

> 📡 **补充扫描（WebSearch 7 天精选兜底）** | 数据源：WebSearch 6 组（AI工具/副业/一人公司/平台红利/RAG-OCR/数字人/Claude替代）| 去重对照 6/23-7/07 全部条目（含本轮已写入 2026-07-08 段）| 新增 5 条 | 🕐 08:50

### 🔴 本周可试（补充）

- [ ] **【阿里 7/10 起全面禁用 Claude 全系（含 Claude Code），推荐自研 Qoder 替代】** | 来源：https://finance.sina.com.cn/roll/2026-07-03/doc-inifpyyq2334050.shtml | 🎯 Rubedo 凝华
  研究方向：阿里将 Claude 列入「高风险软件」并 7/10 全面禁用（含 Sonnet/Opus/Fable 模型与 Claude Code），推荐自研 Qoder 作平替——直接戳中 SSS 当前用 Claude Code 推进 Athanor 的命门。立即制定国产编码 Agent 预案（Qoder/豆包 Trae/千问），评估迁移成本与功能缺口，避免「断供」式单点依赖。

### 🟡 关注（补充）

- [ ] **【腾讯混元 Hy3 正式发布 — Agent 能力跃升，256K 上下文，MoE 2950 亿】** | 来源：https://www.tencent.com/zh-cn/articles/2202386.html | 🎯 Citrinitas 熔知
  研究方向：国产 MoE 模型，256K 长上下文 + 原生 Agent 工具调用，正好补 Claude 被禁后的「长文档摄入 / 知识检索」需求。评估 Hy3 能否作为 Citrinitas 熔知的国产 LLM 底座（RAG 问答、长文解析），对比 Claude 的月成本与合规优势。

- [ ] **【美团 LongCat-2.0 开源 — 1.6T 权重 + 推理引擎 + 国产芯片适配】** | 来源：https://finance.sina.com.cn/tech/roll/2026-07-06/doc-inifwmvt8661077.shtml | 🎯 Citrinitas 熔知
  研究方向：美团开源全系权重、推理引擎与核心文档，华为昇腾/摩尔线程/沐曦已完成适配。1.6T 全量需大显存，但「开源 + 国产芯片」路线为低成本私有化 LLM 推理提供战略选项。重点跟踪后续蒸馏版 / 小参数版本，评估能否作为 Citrinitas 自托管推理底座（规避 API 断供 + 数据不出域）。

- [ ] **【AI 数字人直播 7/15 起必须全程显著标识，否则重罚】** | 来源：http://www.rhkb.cn/news/841995 | 🎯 Rubedo 凝华
  研究方向：监管正式落地——境内 AI 拟人互动（直播带货等商业场景）须全程显著标注「AI」身份，7/15 生效。若 SSS 未来做数字人内容 / 销售陪谈，须把「身份标识」做成合规前置项；同时「标识合规 + 真人背书」反而能建立信任壁垒。对照 Nigredo 数字人管线调整 SOP，避免踩线。

### ⚪ 了解（补充）

- [ ] **【5 款开源 AI 视频转写工具实测盘点（klipa 横评）】** | 来源：https://klipa.ai/en/blog/open-source-ai-video-transcription-tools_688 | 🎯 Nigredo 馏析
  研究方向：近期开源视频转写工具横向评测，覆盖 Whisper 系与新晋方案。Nigredo 摄入管线依赖转写引擎，对照清单评估是否引入多引擎 fallback（实时 vs 离线精转），尤其针对中文长视频 / 方言 / 说话人分离场景提升稳定性——降低对单一转写服务的依赖。

> 📡 补充筛选：以上 5 条来自 aihot 24h 窗口之外的 7 天精选，均与本轮已写入的 2026-07-08 段不重复；阿里 Claude 禁为 7/3 事件、Hy3/LongCat 为 7/6 发布、数字人标识 7/15 生效在即、klipa 为 7/4 横评——均为补充扫描首次收录，无历史重复。

## 2026-07-10

> 数据源：aihot 精选 23 条（24h，7/9-7/10）+ WebSearch 4 组（副业/小红书红利/低成本开源/AI设计接单）| 去重对照 6/23-7/08 全部条目 | 匹配项目 4 个 | 整理 08:50

### 🔴 本周可试

- [ ] **【ChatGPT Sites — 想法一步变可发布网站，OpenAI 官方上线】** | 来源：https://x.com/OpenAIDevs/status/2075331020090687666 | 🎯 Rubedo 凝华
  研究方向：输入一个想法即生成可分享的实时网站，无需写代码。这是「想法→产品→获客」最短路径的官方版——对照 Athanor/Rubedo 的 MVP 公开验证：能否把知识库 Demo / 自动化案例快速做成可分享网页，挂到小红书/私域引流？本周试做一个 Rubedo 能力展示页，验证「零代码建站→获客」闭环。

### 🟡 关注

- [ ] **【colibrì — 纯 C 实现，消费级 25GB 内存电脑跑通 744B 参数 GLM-5.2】** | 来源：https://github.com/JustVugg/colibri | 🎯 Citrinitas 熔知
  研究方向：int4 量化后常驻内存仅 9.9GB、流式加载磁盘专家，把「本地跑超大模型」的门槛压到一台普通电脑。这对 Citrinitas 熔知是低成本自托管推理底座的强心针——继续跟踪蒸馏/小参数版，评估能否替代云端 API（规避断供 + 数据不出域 + 边际成本趋零），与 7/08 收录的 LongCat/Hy3 国产自托管路线互补。

- [ ] **【社交媒体 AI 内容泛滥实测：LinkedIn 超 40% 长文为 AI 写作】** | 来源：https://www.pangram.com/blog/ai-in-your-feed | 🎯 Rubedo 凝华
  研究方向：Pangram 扫描 100 万帖发现整体 AI 率 13.8%、LinkedIn 长文 40%+ 完全 AI 生成。内容通胀正在全平台发生——这对 Rubedo「小红书自动化+私域」是双刃剑：批量 AI 内容越泛滥，平台越倾向给「真人背书 + 显式标注 + 独特人设」的内容流量倾斜。立即复核 SSS 的小红书 SOP：把「真人审稿 + AI 协作者标识 + 行业 know-how 独家性」做成不可复制的护城河。

- [ ] **【微软 Flint — 给 AI 智能体的可视化语言，一句话生成 46 种美观图表】** | 来源：https://microsoft.github.io/flint-chart | 🎯 Rubedo 凝华
  研究方向：用人类可编辑的 spec（数据 + 语义类型 + 图表类型）让 Agent 自动推导坐标轴/配色/布局，渲染到 Vega-Lite/ECharts/Chart.js，并提供 MCP 服务器接入智能体工作流，已开源。SSS 作为效果图设计师，图表/信息图自动化是高频需求——评估 Flint 能否嵌入 Nigredo/Rubedo 的「报告/方案可视化」流水线，把「说一句话出一张专业图表」做成对外交付能力。

### ⚪ 了解

- [ ] **【Mistral Studio — 把提示词和技能当生产资产管理：版本/回滚/审计/标签推送】** | 来源：https://mistral.ai/news/manage-prompts-and-skills-in-studio | 🎯 Rubedo 凝华
  了解：prompts/skills 被视为生产资产，不可变版本 + 明确所有权 + 分类标签 + 审计日志，非开发者也能编辑测试后标签推生产。对 Rubedo 的 Skill 体系是治理范本——对照当前 Skill 是否有「版本化 + 回滚 + 变更可追溯」机制，尤其多 Skill 积累后的「沉淀（Sediment）」风险。

- [ ] **【TeXada — 基于 MiniCPM 的本地数学 Agent，公式 OCR 转可编辑 LaTeX】** | 来源：https://x.com/OpenBMB/status/2075218678027850154 | 🎯 Nigredo 馏析
  了解：支持自然语言转 LaTeX、手写/图像公式 OCR 转可编辑 LaTeX、LaTeX 补全与错误修复，全程本地推理无云端。Nigredo 摄入管线依赖文本/公式提取，TeXada 可作为「扫描文档/讲义公式」的本地化补充引擎——当前优先级低，标记备查。

- [ ] **【Claude 推出「反思」功能（Beta）— 让模型回顾并修正自己的回答】** | 来源：https://www.anthropic.com/news/reflect-with-claude | 🎯 Rubedo 凝华
  了解：对话中 Claude 可主动反思、识别疏漏并修正。这与自动化质量闭环直接相关——对照 Rubedo「零人工干预」原则，评估「反思」机制能否作为 Agent 自检环节，在交付前自动纠错（类似 Albedo 验证的轻量前置）。

- [ ] **【ChatGPT Work — OpenAI 跨应用自主工作的 AI 智能体】** | 来源：https://openai.com/index/chatgpt-for-your-most-ambitious-work | 🎯 Rubedo 凝华
  了解：面向「最雄心勃勃的工作」，可跨文件/日历/邮件/通讯等应用自主推进任务。这是 OpenAI 对「跨应用自主 Agent」的正面下场，与 7/06 收录的 Claude Cowork 同赛道——印证「AI 员工嵌入现有工作流」已成大厂共识，对 Rubedo 自动化业务的定位和获客叙事是需求端验证。

> 📡 **筛选原则执行**：
> - ❌ 剔除：Google SensorFM（健康AI学术）、Musk 赞 Anthropic（大公司动态）、Sequoia 3万亿支出（纯宏观）、Bun 被收购（基础设施）、SWE-1.7 benchmark（模型评测）、LiteRT.js（端侧推理基础设施）、Anthropic 硬问题（公关）、GPT-5.6 发布（7/03 已收录 Sol 详细）、伯南克受托人（公司治理）、特斯拉擎天柱（机器人硬件）、Meta Muse Spark（模型发布）、法国反垄断 CUDA（监管）、NVIDIA Nemotron Puzzle（模型/算力）、蚂蚁 LingBot 视频/世界模型（研究发布）
> - ✅ 保留：ChatGPT Sites（零代码建站）、colibrì（低成本自托管推理）、LinkedIn AI 泛滥（内容生态变化）、微软 Flint（AI 设计图表）、Mistral Studio（Skill 资产治理）、TeXada（本地公式OCR）、Claude 反思（Agent 自检）、ChatGPT Work（跨应用自主Agent）
> - 🆕 与 6/23-7/08 去重对照：全部 8 条均未在历史队列中出现（ChatGPT Sites ≠ 百度秒哒/Ardot；colibrì ≠ LongCat/Hy3；Flint ≠ Ardot/Recraft/Figma；LinkedIn 泛滥 ≠ 小红书变现真相/自媒体结构变化）
> - 🔍 今日 24h 精选 23 条中 8 条（35%）通过一人公司过滤，剔除率 65%，偏大企业/学术/模型发布；WebSearch 4 组补充均为 7 天窗口外旧文或已收录项（小红书变现真相 5 天前已在 7/08 队列），无新增。

> 📡 **二次扫描补充（机会雷达深度 7d：txtmix AI副业早报 7/4 + 大黑AI速报 7/7-7/10 共 16 期）** | 新增 18 条，与 aihot 主段 8 条零重复 | 🕐 08:50
>
> 主段 WebSearch 4 组未命中副业/一人公司垂直信号，本补充专攻「副业机会/一人公司/赚钱渠道/平台红利/降本工具」，覆盖主段缺口。

### 🔴 本周可试（二次扫描补充）

- [ ] **【腾讯开源 BrowserSkill — 让 AI 智能体直接操作浏览器】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-09_1601 | 🎯 Rubedo 凝华
  研究方向：腾讯开源的浏览器操作 Skill，让 Agent 像人一样点网页、填表、抓数据。对照主段 ChatGPT Sites（建站），BrowserSkill 补上「网页 RPA」环节——评估能否嵌入 Rubedo 的小红书/酷家乐采集与 Athanor 摄入管线的网页抓取，降低对单一 API 的依赖、提升稳定性。

- [ ] **【Cognition SWE-1.7 — 低成本逼近前沿的编程 Agent 模型（1000 tok/s，成本仅几分之一）】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-09_0401 | 🎯 Rubedo 凝华
  研究方向：基于 Kimi K2.7 的编程模型，SWE-Bench Pro 逼近最强模型但成本大幅降低、速度 1000 tok/s。SSS 当前用 Claude Code 推进 Athanor，编码成本是直接痛点——本周评估 SWE-1.7 能否承接日常编码/测试，把 Claude 额度留给复杂架构决策，月成本可降一截（主段 colibrì 解决「推理底座」，SWE-1.7 解决「编码成本」）。

- [ ] **【agent-bridge — Claude Code + Codex 双开会话桥开源（MIT，纯本地）】** | 来源：https://github.com/raysonmeng/agent-bridge | 🎯 Rubedo 凝华
  研究方向：把 Claude（规划）和 Codex（执行）接进同一常驻会话，自动互传结果、额度见底无缝接续，大部分代码由两个 Agent 自己写出来。对 Athanor 开发是「双模型编排」现成参考——评估接入 OpenCode/Gemini CLI，做成 SSS 自己的本地多 Agent 编码流，降本又不被单一厂商锁定。

### 🟡 关注（二次扫描补充）

- [ ] **【LangChain 开源 deepagents + Gemini API Managed Agents（后台/远程 MCP）】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-08_0401 | 🎯 Rubedo 凝华
  研究方向：同一天两个 Agent 基础设施开源/升级——LangChain deepagents（深度 Agent 框架）+ Gemini Managed Agents 支持后台运行和远程 MCP。对 Rubedo 自动化底座是直接可选型——对照 6/29 Weave/Wayfinder 路由，评估「框架 + 托管 Agent + 远程工具」能否构成零运维的自动化执行层。

- [ ] **【OpenAI GPT-Live 全双工语音模型全面推送（实时 UI + 调用 GPT-5.5）】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-09_1201 | 🎯 Nigredo 馏析 + Rubedo 凝华
  研究方向：官方版全双工语音，边说边听、可实时操控界面、调用模型。对 Nigredo 语音处理管线（实时转写/语音驱动）是直接方案；对 Rubedo 是「语音驱动自动化 + 销售陪谈 Agent」的语音底座。对照 6/29 ChatGPT Bidi 1，GPT-Live 已全量推送——评估接入成本与中文表现。

- [ ] **【Kyutai Pocket TTS 开源 — 5 秒音频克隆音色】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-07_0001 | 🎯 Nigredo 馏析
  研究方向：法国 Kyutai 开源极轻量 TTS，5 秒样本即可克隆音色。对照 6/24 Confucius4-TTS，Pocket TTS 是多一个开源选项——评估能否作为 Nigredo「文字→有声内容」输出格式，或做知识付费/播客的低成本配音，本地部署零成本。

- [ ] **【Koder — 浏览器 UI 编码工具发布（设计稿→代码）】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-07_2001 | 🎯 Rubedo 凝华
  研究方向：浏览器内直接做 UI 编码的工具，把设计意图转成可运行界面。对照主段 微软 Flint（图表）+ 6/27 Ardot/Recraft，Koder 是「设计→代码」赛道又一新玩家——SSS 作为效果图设计师，评估能否把军工效果图风格稿直通代码交付，缩短提案到收钱的距离。

- [ ] **【淘宝 GrowBrain — Agentic 内容成长引擎（商家内容自动化）】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-09_2001 | 🎯 Rubedo 凝华
  研究方向：淘宝发布面向商家的 Agentic 内容成长引擎，自动生成并优化店铺内容。这是「平台级内容 Agent」红利信号——对照 Rubedo 小红书/私域内容自动化与 6/25 小红书新规，研究能否借平台原生 Agent 降低内容生产成本，或把 SSS 内容服务对齐平台工具做差异化。

- [ ] **【工信部发布 Claude Code 后门风险提示 + 北京拟限制海外访问中国 AI 模型】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-08_1601 | 🎯 Rubedo 凝华
  研究方向：监管连续出手——工信部提示 Claude Code 后门风险、北京拟限制海外访问中国 AI 模型。叠加 7/08 阿里 7/10 禁用 Claude，国产模型从「备选」变「刚需」——立即把 Hy3/LongCat/DeepSeek 迁移预案从「待办」提到「本周必须跑通」，避免 Athanor 开发工具链断供（呼应主段 colibrì 自托管路线）。

- [ ] **【Danluu Agentic coding 方法论 — 测试驱动 + 默认无 code review】** | 来源：https://news.ycombinator.com/item?id=48782671 | 🎯 Rubedo 凝华
  研究方向：资深工程师分享「测试当一等公民、靠属性测试/fuzzing 替代手写单测与 review」的 AI 编程工作流，支撑「接单产能翻倍」。对 SSS 用 AI 接单/做 Athanor 是直接可抄的工程质量 SOP——研究能否沉淀为 Rubedo 的交付质量检查清单（呼应主段 Claude 反思 自检机制）。

### ⚪ 了解（二次扫描补充）

- [ ] **【Grok-4.5 正式发布 — Terminal-Bench 击败对手、成本更低】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-09_0801 | 🎯 Rubedo 凝华
  了解：xAI 发布 Grok-4.5，Terminal-Bench 超过竞争对手且成本/效率更优，Code Arena Frontend 升至第 3。前沿编码模型又多一个低成本选项——标记备查，等 API 开放后评估能否加入 Athanor 编码模型路由（成本维度补充主段 colibrì）。

- [ ] **【Manus 推出 Branch 并行会话功能】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-10_0001 | 🎯 Rubedo 凝华
  了解：Agent 产品 Manus 支持并行分支会话，同一任务多路线探索。对 Rubedo 多 Agent 编排有产品形态参考——了解其「分支/合并」交互，看能否复用到自动化任务调度。

- [ ] **【魔芯 MoWorld — 50FPS 视频生成、成本降 70%、获华为联想投资】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-09_0002 | 🎯 Rubedo 凝华
  了解：视频生成速度和成本再下探（50FPS、成本降 70%）。对照 6/24 FastWan-QAD / Seedance，视频生产降本趋势明确——标记跟踪，等 SSS 做小红书/短视频时评估自部署 vs API 的经济性。

### 💡 探索（二次扫描补充）

- [ ] **【小互用 Claude Code 建站 3 天盈利 — 一人公司 PMF 真实样本】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-08_2001 | 🎯 OpusMagnum 巨作
  值得关注：开发者小互用 Claude Code 三天建站即盈利，是「AI 编程 + 一人交付」的最新 PMF 案例。对照主段 ChatGPT Sites（零代码建站），验证「建站/小工具即盈利」路径仍跑得通——研究其选品与获客，看能否复制到我们的垂直知识库方向。

- [ ] **【BrowSync — Mac 多浏览器同步工具，内购限免、独立开发年收入估千万级】** | 来源：https://browsync.ct106.com | 🎯 OpusMagnum 巨作
  值得关注：纯本地、隐私优先、iCloud 同步的 Mac 工具，靠「内购限免」拉声量、月费 $9.99 变现，独立开发者年收入估千万级。这是一人公司「小工具 + 订阅制」产品形态标杆——研究其定价/限免/增长打法，对照 SSS 能否做类似的 AI Coding 上下文同步工具（Cursor↔Claude Code↔Codex）。

- [ ] **【Show HN 半衰期 7 小时 — 4.1 万次 launch 数据复盘】** | 来源：https://news.ycombinator.com/item?id=48759838 | 🎯 OpusMagnum 巨作
  值得关注：统计 41,301 个 Show HN，热度半衰期仅 7 小时，成功者都是「真有刚需的工具」而非刻意 launch。对 SSS 副业 launch 是清醒方法论：把「首发 0-7 小时响应预案 + 第 7 天复盘」做成标准动作，「找 30 个真实用户比 3000 个点赞重要」——直接复用到 Rubedo 任何产品的发布 SOP。

- [ ] **【OASIS Ring 走红 — Vibe Coding 语音/手势硬件，AI 硬件+内容复合变现】** | 来源：https://www.36kr.com/p/3880964231707525 | 🎯 OpusMagnum 巨作
  值得关注：智能戒指 OASIS Ring 不做健康、专做「AI 输入设备」，用声音/手势控制电脑里的 AI。今年 Vibe Coding 硬件（三键键盘、AI 麦克风、AI 耳机）集中走红——这是「软件副业 + 硬件测评/配置文件内容」复合变现窗口，SSS 可卖「国产 AI 助手 + 智能戒指」语音命令预设（¥19-49/套）。

- [ ] **【Cloudflare Monetization Gateway — Agent 自动收费网关，按使用付费】** | 来源：https://news.daheiai.com/realtime.php?file=quick_2026-07-08_1201 | 🎯 OpusMagnum 巨作
  值得关注：Cloudflare 推出按使用付费的自动收费网关，Agent 可直接对调用方计费、分成、结算。一人公司做「按次/按量收费的 AI 工具」最大痛点（收钱、对账、分成）被平台接管——研究能否作为 Rubedo 未来对外售卖自动化服务的变现基建，省去自己搭支付。

> 📡 **二次扫描筛选**：
> - ❌ 剔除（与主段同理由）：纯大企业/基础设施（Ollama 融资、MiniMax M3 P、DeepSeek 自研芯片、NVIDIA Nemotron、Gemma 4、三星芯片、机器人上市、具身基准、医疗微调、AWS/SageMaker 集成、百度下载破百万）、监管无直接变现（GPT-5.6 日区假消息辟谣、OpenAI 人事）、已收录重复（阿里禁用 Claude 7/08、Hy3 7/08、Fun-ASR 7/08、Claude Sonnet 5 7/01、GPT-5.6 6/27、Kimi K2.7 7/03、Claude Loop 7/01、小红书 MCP 7/03）
> - ✅ 保留（18 条，全为副业/一人公司/赚钱/平台红利维度，主段 WebSearch 未命中）：BrowserSkill、SWE-1.7、agent-bridge、deepagents+Managed Agents、GPT-Live、Kyutai Pocket TTS、Koder、GrowBrain、工信部后门+北京限制、Danluu、Grok-4.5、Manus Branch、MoWorld、小互建站、BrowSync、Show HN 半衰期、OASIS Ring、Cloudflare Gateway
> - 🆕 与 6/23-7/08 及本日主段 8 条三重去重：全部 18 条均为新增，无重复
> - 🔍 本日总覆盖：aihot 主段 8 条 + 二次扫描 18 条 = 26 条高相关信号；大模型密集发布期，信号密度极高，已按「宁少勿滥」剔除所有无关项

## 2026-07-12

> 数据源：WebSearch 多维度扫描 16 组（副业/一人公司/开源工具/AI设计/平台红利/AI编程平替/事实核查/向量OCR/RAG）+ 7天窗口补充 | 去重对照 6/23-7/10 全部条目 | 匹配项目 5 个 | 整理 08:50

### 🔴 本周可试

- [ ] **【Days to First $1,000 — 11 个 AI 副业按"首赚千元"速度排名（31 位独立运营者收据）】** | 来源：https://betonai.net/days-to-first-1000-with-ai-in-2026-11-side-hustles-ranked-by-how-fast-a-solo-operator-got-paid-receipts-from-31-operators/ | 🎯 Rubedo 凝华
  研究方向：最快路径是"本地商家 AI 语音客服搭建"（中位 14 天首赚 $1K、最快 4 天）、AI 接待员（21 天）、Cursor 接单开发（23 天）、AI 社媒内容包（28 天）；最慢是 AI 图库（71 天）。对照 SSS 技能栈，优先验证"AI 社媒内容包 / 设计接单"两条——既是中位最快、又复用 Nigredo+Rubedo 流水线。本周挑一条跑"首单→首千元"最小闭环。

- [ ] **【国产编码 Agent 平替矩阵 — OpenCode / QwenCode / ZCode / DeepCode CLI 集中开源（MIT/Apache，免费商用）】** | 来源：https://new.qq.com/rain/a/20260709A0811Y00?refer=cp_1009 | 🎯 Rubedo 凝华
  研究方向：阿里 7/10 禁用 + 工信部后门提示后，平替已成型——OpenCode（17万Star、无监控、本地存储、75+模型）、Qwen Code（Apache-2.0、25k Star）、ZCode（GLM-5.2、Terminal-Bench 81%、API $1.4/$4.4 仅为 Opus 1/5）、Deep Code CLI（DeepSeek-V4 原生、MIT）。本周必须把 Athanor 开发工具链从"Claude Code 单点"迁到"OpenCode + 国产模型"双轨，避免断供式单点依赖（呼应 7/08 预案）。

### 🟡 关注

- [ ] **【Google Gemma 4 全系开源（Apache 2.0，31B 端侧多模态+深度思考）】** | 来源：https://www.163.com/dy/article/L1ICDGJD0511ABV6.html | 🎯 Citrinitas 熔知
  研究方向：7/11 解封，原生多模态（视觉+音频）+ 深度推理，笔记本/手机可离线跑。补上 Citrinitas「自托管推理底座」多模态短板——与 7/08 LongCat/Hy3、7/10 colibrì 形成「开源自托管三选一」。评估 Gemma 4 能否本地承担 Athanor 的图片/音频摄入与长文档解析，进一步降低对云端 API 的依赖与断供风险。

- [ ] **【Z.ai 发布 ZCode — 免费 AI 编码 IDE（GLM-5.2，MIT，微信/飞书机器人远程控制）】** | 来源：https://www.ai-master.cc/blog/blog-413 | 🎯 Rubedo 凝华
  研究方向：基于 GLM-5.2（744B MoE），Terminal-Bench 2.1 得 81%（Opus 4.8 为 85%），SWE-bench Pro 62.1 超 GPT-5.5，基础版免费、付费 $16.2/月（低于 Cursor $20），API 成本仅为闭源 1/5–1/9。这是 Claude Code 断供后最直接的「免费+国产+可远程微信操控」平替——本周实测 ZCode 承接 Athanor 日常编码，把 Claude 额度留给复杂架构决策。

- [ ] **【2026 事实核查/幻觉治理工具栈成熟 — Standard/Hybrid/Agentic RAG + 7 款验证工具 + ReMMD-Agent + 氢离子动态证据】** | 来源：https://news-factory.app/blog/news-fact-checking-2026 | 🎯 Albedo 炼真
  研究方向：幻觉治理已从「概念」进入「工程标配」——三层 RAG（Standard 降 15-25% / Hybrid KG-RAG 降 18% / Agentic RAG 降 25-40%）；7 款验证工具（Perplexity Sonar、Vectara HHEM 幻觉评分、Guardrails AI、Patronus AI、Google Fact Check Explorer 等）；上交大/清华 ReMMD-Agent 用「原子化解析+记忆库复用」把假新闻核查做到 82.4%；阿里健康氢离子把静态引用升级为「动态证据定位」（校验时效性/权威性）。这是 Albedo 炼真的可直接复用的技术栈与产品范式——把「知识验证→证据追踪→时效性校验」做成 Athanor 的验证层。

- [ ] **【VideoCaptioner — 15k Star 开源字幕神器，一行命令搞定转录/翻译/烧录，自带 Claude Code Skill】** | 来源：https://guopei.blog.csdn.net/article/details/162551646 | 🎯 Nigredo 馏析
  研究方向：CLI+GUI 双模式，ASR（必剪/Whisper）+ LLM 语义断句翻译 + FFmpeg 烧录全流程一体化，免费功能零成本；还提供 Claude Code Skill（`/videocaptioner`），让 AI 编程助手直接调它处理视频字幕。对照 7/03 browser-use video-use 与 7/08 klipa 横评，VideoCaptioner 是「字幕回填」环节更省心的一体化选项——评估接入 Nigredo 视频摄入管线，降低多工具拼凑成本。

- [ ] **【MinerU + DeepSeek-OCR 2 — PDF 结构化+OCR+自动目录，中文强】** | 来源：https://gitcode.csdn.net/69b2863454b52172bc60bd7b.html | 🎯 Citrinitas 熔知 + Nigredo 馏析
  研究方向：MinerU（OpenDataLab）做 PDF 解析+版面分析+标题层级+自动目录+Markdown 输出；DeepSeek-OCR 2 用 VLM+LLM 还原阅读顺序与层级、自动生成 Markdown 目录。两者都是 Athanor 摄入管线的「文档→结构化」候选引擎，尤其适合军工效果图规范/技术文档的批量入库——对比 7/08 TeXada（公式）与既有方案，评估能否统一文档摄入栈。

- [ ] **【PilotDeck — 清华/OpenBMB/面壁开源本地 Agent OS，智能路由省约 70% 成本】** | 来源：https://watermelonwater.tech/insights/%E6%9C%AC%E5%9C%B0agentos%E4%BA%BA%E4%BA%BA%E5%8F%AF%E6%8B%A5%E6%9C%89 | 🎯 Rubedo 凝华
  研究方向：一个项目一个 WorkSpace（文件/记忆/技能/任务进度/成本记录），开源可本地部署；智能路由按任务难度动态降级模型（社媒场景省约 70%，复杂任务用 1/6 成本超 Sonnet 4.6 单 Agent）。这正是 Rubedo「零人工干预 + 算账」原则的工具化样本——评估能否作为 Athanor 开发的本地 Agent 工作舱，把「灵感→执行」压成一个人调度一支 Agent 小队。

- [ ] **【OpenWork — 开源本地优先 AI Agent 桌面工作台（OpenCode 引擎，可一键分发工作流）】** | 来源：https://www.toutiao.com/article/7657883971157492267 | 🎯 Rubedo 凝华
  研究方向：对标 Claude Cowork/Codex，本地优先（127.0.0.1 起 OpenCode，数据不出本地），接入 50+ 模型，支持把「Skills+MCP+提示词+自动化流程」打包成分享链接一键导入。对 Rubedo 的双重价值：(1) 隐私可控的本地 Agent 工作台；(2)「可分发工作流」是可对外售卖的数字化产品形态——把 SSS 的自动化 SOP 做成模板卖，正是内容变现新路径。

- [ ] **【小红书 AI 视频流量扶持 — RED 精选计划曝光 50万→270万，最高 8 万流量券/月+100万基金】** | 来源：https://www.toutiao.com/a7644305256737735211?channel= | 🎯 Rubedo 凝华
  研究方向：AI 中长视频满足「真实信息增量 / 艺术辨识度 / 完整剧情逻辑」三项即可进 RED 精选，篇均曝光从 50 万升至 270 万、最高 8 万流量券/月、推荐周期延至 90 天。2026 以来已封禁 110 万+ AI 托管账号——但「有辨识度的 AI 视觉创作」被明确扶持。SSS 作为效果图设计师，立即把小红书 SOP 重写为「AI 中长视频 + 强个人风格 + 知识增量」，对齐 RED 精选拿流量倾斜（呼应 6/25 小红书新规）。

- [ ] **【视频号完成商业化闭环 — 微信小店整合+社交推荐权重提升+直播基建成熟】** | 来源：https://c.m.163.com/news/a/KVAAQCNK0522COE6.html | 🎯 Rubedo 凝华
  研究方向：视频号从「内容平台」跃为「商业平台」——微信小店内闭环下单（免跳转）、社交推荐权重提升（朋友互动影响推荐流）、直播带货工具补齐。对 SSS 的「小红书种草→微信私域成交」组合拳是平台级红利：视频号承接私域、微信小店直接变现，链路比抖音更短。评估是否把内容分发从「抖音测爆款+小红书种草」补上「视频号沉淀私域」第三极。

### ⚪ 了解

- [ ] **【证券时报《2026 一人公司洞察报告》：1 元撬动 72 倍人力，零成本工具矩阵曝光】** | 来源：https://blog.csdn.net/liferecords/article/details/161227643 | 🎯 Rubedo 凝华
  了解：量化结论——一人公司月工具成本（OpenClaw+Dify+n8n 全免费方案）可压到 ¥0，混合方案约 ¥402/月，对比 5 人团队成本比 1:200、产出达 60-80%。这是对「一人公司可行性」的硬数据背书，标记备查，用于对外讲 SSS 一人公司故事时引用。

- [ ] **【goose — Linux 基金会 AAIF 托管开源 AI Agent（47k Star，MCP 70+ 扩展）】** | 来源：https://f.mffb.com.cn/a/498123.html | 🎯 Rubedo 凝华
  了解：Block 内部孵化、2026/4 迁入 Linux 基金会，本地优先、支持 15+ LLM 与 70+ MCP 扩展（GitHub/数据库/Shell/文件系统），桌面 GUI+CLI+API 三形态。MCP 生态最广泛的本地 Agent 之一——标记备查，作为 Rubedo 自动化底座的候选（与 OpenClaw/OpenWork/PilotDeck 横向对比）。

### 💡 探索

- [ ] **【Chatbase 117 天做到 $1M ARR — 零融资零团队，16 个粉丝起步，现 $8M ARR】** | 来源：https://1opc.ai/article/881/arr-chatbase-yasser-elsaid-ai-gpt | 🎯 OpusMagnum 巨作
  值得关注：创始人 Yasser Elsaid 做「基于自己数据训练定制 GPT 聊天机器人」的拖拽式平台，117 天从 16 粉丝到 $1M ARR、现 $8M，全程零融资零销售团队、纯自举。最大反直觉启示：「16 个粉丝也能引爆产品」——别等准备好才推广。对 Athanor/Rubedo 的直接启发：知识库聊天机器人（Citrinitas 方向）是被验证的 solo PMF 赛道，且「先发产品再涨粉」比「先涨粉再卖货」更稳。

- [ ] **【OPC 政策红利密集落地 — 北京/海南/济南/重庆最高算力补贴 50 万、海南奖励 800 万】** | 来源：https://www.mycaijing.com/article/detail/569521?source_id=40 | 🎯 OpusMagnum 巨作
  值得关注：2026 年以来超 20 城出台一人公司专项政策——北京通州模型券 30 万/算力券 50 万、海南自贸港税收优惠+数据跨境+最高 800 万奖励、济南 50 亿产业基金+免租空间、重庆创业担保贷款个人 50 万/小微 600 万且 50% 贴息。这是巨作层面的战略储备：一人公司的「政策套利窗口」正在打开，SSS 可评估把公司主体落在有补贴的城市（如海南/北京），把算力/模型/办公成本外部化。

> 📡 **筛选原则执行**：
> - ❌ 剔除：纯大企业/融资/芯片（MiniMax 160亿融资、曙光8000超集群、Meta出租算力、Anthropic自研芯片、AMD Zen6、英伟达H100涨价、Grok-4.5已在7/10）、模型发布重复（GPT-5.6 Sol已在6/27、GPT-5.6公开已在7/11）、学术/基准（ARC-AGI-3已在7/09覆盖）、自媒体平台对比旧文（与6/25小红书新规/7/08变现真相重叠）
> - ✅ 保留：betonai首千元排名、国产编码平替矩阵、Gemma 4、ZCode、事实核查工具栈(Albedo首条命中)、VideoCaptioner、MinerU/DeepSeek-OCR2、PilotDeck、OpenWork、小红书RED精选、视频号闭环、72倍人力、goose、Chatbase、OPC政策
> - 🆕 与 6/23-7/10 去重对照：全部 15 条均为新增，无重复；其中 **Albedo 炼真首次有命中条目**（事实核查/幻觉治理工具栈）
> - 🔍 本周（7/10→7/12）主线：国产替代 + 自托管 + 平台红利；aihot 专家流本次未直接可用，改用 WebSearch 多维度扫描兜底，覆盖等同

---

> 📡 **二次扫描补充（机会雷达 7d 深度）** | 数据源：aihot.virxact.com 24h 精选（7/11-7/12）+ WebSearch 副业/AI设计/开源Agent/平台红利 6 组 | 与专家主段 15 条及 6/23-7/10 全量去重 | 新增 8 条 | 🕐 08:50

### 🟡 关注（二次扫描补充）

- [ ] **【Perplexity Computer Analytics — 跨模型信用额度支出监控，免费】** | 来源：https://aihot.virxact.com/items/cmrf3pi9j0730ih8eb6hjx4hn | 🎯 Rubedo 凝华
  研究方向：免费的 analytics 跨模型实时跟踪 credit 消耗，补上主段缺失的「成本监控」半环。SSS 当前用 Claude Code + 多模型路由，把各模型 credit 接入 Perplexity Analytics 看板，量化「哪个任务最烧钱」，为 7/03 起的「AI 成本管控 SOP」补数据底座。

- [ ] **【Claude Code 桌面版内置沙盒浏览器 — 直接读网页交互，免复制粘贴】** | 来源：https://aihot.virxact.com/items/cmrf8177m007bihprf4zml1hn | 🎯 Rubedo 凝华
  研究方向：Claude 现在能在沙盒里直接开浏览器读网页、点链接、抓内容，前端调试与文档/RAG 资料查阅不用再手动复制。试用于 Athanor 摄入管线的「网页资料自动抓取→结构化入库」环节，看能否替代部分 Playwright 脚本，提升管线稳定性（呼应当前「摄入管线稳定性修复」重心）。

- [ ] **【OpenAI GPT-5.6-Sol 误删用户整块 Mac 硬盘 — Agent 放权的安全红线】** | 来源：https://aihot.virxact.com/items/cmrfr2xvi02brihjlp1tlzg1n | 🎯 Rubedo 凝华
  研究方向：Agent 因路径变量错误拿到全权限误删用户数据。这是「零人工干预」原则的安全警钟——Rubedo 自动化 SOP 必须给 Agent 设「文件系统沙箱 + 写操作二次确认 + 备份前置」。立即把「权限最小化 + 危险操作拦截」写进 Rubedo 的 Agent 安全清单，避免 Athanor 摄入/交付脚本重演。

- [ ] **【百度「搭子联盟」开放 — 个人 AI Agent 的变现/协作分发渠道】** | 来源：https://aihot.virxact.com/items/cmrf0774z04wyih8e0snjs2g2 | 🎯 Rubedo 凝华
  研究方向：百度搭子（个人 AI）启动「搭子联盟」，给个人开发者提供变现与协作渠道，浏览器调用 + 智能路由降耗 20%。这是主段小红书 MCP / 视频号闭环之外的又一个「平台级 Agent 分发红利」——评估能否把 Rubedo 的自动化能力上架搭子联盟变现，或借其流量获客。

- [ ] **【LiteRT.js — 浏览器端 WebGPU 推理运行时，免服务器跑模型】** | 来源：https://aihot.virxact.com/items/cmre0j0vj002sihwk71qvktk7 | 🎯 Rubedo 凝华
  研究方向：Google 开源 LiteRT.js，前端 WebGPU 直接跑模型，省去服务器开销。一人公司做轻量 AI 应用（如 Nigredo 的本地字幕预览、Rubedo 的小红书配图工具）可把推理塞进浏览器——零后端成本、隐私不出端。评估能否用于 Athanor 的「端侧轻推理」场景。

### ⚪ 了解（二次扫描补充）

- [ ] **【Meta 撤回 Instagram「无许可 AI 深伪」功能 — 平台创作政策收紧】** | 来源：https://aihot.virxact.com/items/cmrflz3sd00x5ihjlndy4k7rn | 🎯 Rubedo 凝华
  了解：Meta 在反对声下撤回无需许可的 AI 图像生成。平台对「AI 生成 + 真人肖像权」的边界正在收紧——标记备查，若 SSS 未来做数字人 / AI 头像类内容，须把「授权 + 标识」做成前置合规项（呼应 7/08 数字人直播标识令）。

### 💡 探索（二次扫描补充）

- [ ] **【2026 AI 设计变现指南：25 赛道 + 月入 4 万收益模型】** | 来源：https://www.douchuanghui.com/thread-21568-1-1.html | 🎯 OpusMagnum 巨作
  值得关注：可落地收益模型——设计服务 80 单×¥350=¥28,000 + 模板销售 ¥5,000 + 课程 ¥8,000 = 月入 ¥41,000，成本仅 ¥3,000（利润率 92.7%）。SSS 本身是效果图设计师，这条把「AI 设计接单→模板被动收入→课程」三段式讲透，可直接对标设计自己的副业收入结构，与 Athanor/Rubedo 主业形成「设计副业反哺」闭环。

- [ ] **【2026 普通人用 AI 赚钱完整指南：6 大路径 + 25 品类利润率表】** | 来源：https://www.douchuanghui.com/thread-20974-1-1.html | 🎯 OpusMagnum 巨作
  值得关注：25 个品类附利润率（AI LOGO 90-98%、AI 私域话术包 90-98%、AI 知识付费 92-99%）与变现周期。这是「已知可行赚钱路径」的速查表——对照 SSS 技能栈（设计 / 效果图 / 知识管理），挑 1-2 条优先验证，比盲目试错省时间。

> 📡 **二次扫描筛选**：
> - ❌ 剔除（与专家主段/历史重叠或弱相关）：七龙虾大厂Agent混战（与主段 OpenWork/PilotDeck/goose 本地 Agent 主题重叠）、Meta Compute 出租裸算力（专家主段已剔除）、OPC 创新社区算力补贴（与主段 OPC 政策红利完全重复）、Claude Code v2.1.207 常规版本（无行为变更）、GPT-5.6 医疗评估/博科圣地/苹果诉 OpenAI/宇树手术机器人/Ghost Font/数学猜想（大企业/学术/安全，非一人公司）
> - ✅ 保留（8 条，均为主段未覆盖的新维度）：Perplexity Analytics（成本监控）、Claude Code 桌面浏览器（自动化）、GPT-5.6-Sol 误删（RPA 安全）、百度搭子联盟（平台分发红利）、LiteRT.js（端侧推理）、Meta IG 撤回（合规预警）、AI 设计 25 赛道（设计副业）、6 大变现路径（收入速查）
> - 🆕 与专家主段 15 条及 6/23-7/10 全量三重去重：8 条均为新增，无重复

