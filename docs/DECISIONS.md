# ScholarAgent Decisions

本文件记录 ScholarAgent 的关键项目决策。

它不替代 `docs/PROJECT_PLAN.md`，只解释重要选择背后的原因，方便后续 AI 或开发者接手时不反复推翻已经讨论过的方向。

## D001：项目定位为科研复现与创新机会评估 Agent

- 状态：已接受
- 日期：2026-05-09

决策：

ScholarAgent 的定位不是普通论文搜索助手，也不是通用深度研究 Agent，而是面向科研新手的科研复现与创新机会评估 Agent。

原因：

- 普通“搜索论文并生成报告”项目差异化不足。
- 科研新手真正困难的不是只找到论文，而是判断论文是否值得复现、代码是否可用、风险在哪里、可以从哪里创新。
- 这个定位更适合在简历和面试中展示 Agent 工程能力、证据验证能力和评估意识。

影响：

- 后续功能要围绕论文、代码、证据、复现评分和创新机会展开。
- 不应把项目做成泛化聊天机器人。

## D002：核心创新是 Evidence Graph，而不是多 Agent 本身

- 状态：已接受
- 日期：2026-05-09

决策：

ScholarAgent 的核心数据结构是 Evidence Graph，用于连接 paper、claim、method、repo、code_file、experiment、evidence 和 opportunity。

原因：

- 多 Agent 本身容易变成概念堆叠。
- Evidence Graph 能让每个结论有来源、有关系、有验证路径。
- 面试时可以清楚表达：项目把科研调研从文本生成问题建模成证据图谱构建和验证问题。

影响：

- 后续报告生成必须尽量依赖 evidence，而不是让模型自由发挥。
- 论文检索、GitHub 调研、复现评分和引用验证都应向 Evidence Graph 写入结构化结果。

## D003：先做确定性工作流，再逐步引入 LangGraph

- 状态：已接受
- 日期：2026-05-09

决策：

前期先用普通 Python 服务和清晰函数完成最小链路，中后期再把 pipeline 工作流化为 LangGraph。

原因：

- 用户是初学者，直接上 LangGraph 会增加理解成本。
- 项目前期更重要的是把数据模型、接口、证据结构和验证方式搭稳。
- 当流程变长、状态变复杂、需要失败重试和 trace 时，再引入 LangGraph 更自然。

影响：

- 阶段 1 到阶段 4 不应急着写复杂图工作流。
- 引入 LangGraph 前，应先有清楚的输入输出模型和最小可运行 pipeline。

## D004：RAG 定位为 Evidence RAG，而不是普通问答 RAG

- 状态：已接受
- 日期：2026-05-09

决策：

ScholarAgent 后续会使用 RAG，但主要用途是为 claim verification、paper-code alignment 和复现风险判断检索证据候选。

原因：

- 普通文档问答 RAG 很常见，项目含金量不够突出。
- Evidence RAG 更贴合本项目“结论必须可验证”的主线。
- RAG 检索结果不直接变成答案，而是交给 Verifier 判断 supported、weakly_supported、unsupported 或 conflict。

影响：

- 前期可以先用关键词和结构化字段检索。
- Qdrant 等向量库后置，不在项目初始化阶段引入。

## D005：多 Agent 用于交叉验证，不用于角色扮演

- 状态：已接受
- 日期：2026-05-09

决策：

多 Agent 的最终用途是让 Paper Evidence Agent、Code Evidence Agent、Reproducibility Auditor、Citation Verifier 和 Writer 分工协作与交叉验证。

原因：

- 简单角色扮演式多 Agent 对工程能力展示有限。
- 独立收集证据、独立审计风险、验证报告 claim 更能体现 Agent 系统设计能力。
- Writer 只能基于已验证 evidence 生成报告，可以降低幻觉。

影响：

- 早期不要为了“看起来多 Agent”而拆很多空角色。
- 每个 Agent 必须有明确输入、结构化输出和验收标准。

## D006：阶段 1 只做最小 FastAPI 后端

- 状态：已接受
- 日期：2026-05-09

决策：

下一步从最小 FastAPI 后端开始，只实现健康检查和最小研究任务接口。

原因：

- 项目需要一个稳定的服务入口，后续论文搜索、任务状态、报告和前端都可以挂在这个入口上。
- FastAPI + Pydantic 适合初学者理解 API、请求响应模型和后端结构。
- 小步可运行比一次性搭完整架构更适合学习。

影响：

- 阶段 1 不安装复杂基础设施。
- 阶段 1 不做论文搜索、不做 LangGraph、不做数据库、不做前端。

## D007：前期用本地 JSON 或内存结构，数据库后置

- 状态：已接受
- 日期：2026-05-09

决策：

前期 Evidence Graph 和任务状态可以用 Pydantic 模型、内存对象或本地 JSON 表示，PostgreSQL 后置。

原因：

- 数据库会增加部署和调试成本。
- 前期重点是理解数据结构和流程，不是优化存储。
- 当任务、证据、trace 和评估数据变多时，再引入数据库更合理。

影响：

- 早期代码要保留清晰的数据边界，方便后续替换存储层。
- 不要在阶段 1 直接引入数据库。

## D008：前端后置，先保证后端链路和证据质量

- 状态：已接受
- 日期：2026-05-09

决策：

前端可视化放在后期，先完成后端链路、证据图谱、复现评分和报告验证。

原因：

- 项目的核心含金量在 Agent 工作流、证据链和评估体系。
- 太早做前端会分散精力。
- 后端数据结构稳定后，前端展示 Evidence Graph、trace 和报告会更自然。

影响：

- 早期不创建前端项目。
- 后期前端重点展示任务、证据图谱、对齐矩阵、复现评分、trace 和报告。

## D009：所有关键结论必须能追溯证据

- 状态：已接受
- 日期：2026-05-09

决策：

ScholarAgent 的报告、评分和创新建议都应尽量绑定 evidence，不输出没有来源的重要结论。

原因：

- 科研调研类 Agent 最大风险是幻觉和错误引用。
- 证据追踪能提升可信度，也方便调试和面试展示。
- 这条原则能统一 Evidence Graph、Evidence RAG、Citation Verification 和 Trace Replay。

影响：

- 生成报告前应优先检查证据是否足够。
- unsupported claim 应被标记、降级或移除。

## D010：项目以边学边做方式推进

- 状态：已接受
- 日期：2026-05-09

决策：

每次开发都采用解释目的、少量实现、运行验证、总结学习点的节奏。

原因：

- 用户是初学者，项目目标是学习和作品建设并重。
- 小步推进能减少理解压力，也更容易保持代码质量。
- 清晰提交历史有利于复盘和简历展示。

影响：

- 每次改代码前先说明改动范围。
- 关键逻辑添加中文注释。
- 验证通过并经用户同意后再提交 git。

## D011：阶段 3 Evidence Graph 先用最小 Pydantic 模型实现

- 状态：已接受
- 日期：2026-05-12

决策：

阶段 3 的 Evidence Graph 使用两个 Pydantic 模型（Evidence + EvidenceGraph），纯内存存储，不引入数据库、NetworkX 或其他图库。

原因：

- 阶段 3 的目标是把论文元数据变成可溯源的证据节点，图谱规模极小（每篇论文 4 条 evidence）。
- Pydantic 列表足够表示当前规模的节点和关系，不需要图的遍历和查询能力。
- 当前阶段不接入 LLM 做 claim 抽取，claim 节点预留到后续阶段。
- 如果过早引入 Neo4j 或 NetworkX，会增加理解成本，违背 D007 "数据库后置"原则。

影响：

- 阶段 3 只生成 paper + evidence 两类节点。
- 每条 evidence 通过 source_paper_id 字段实现溯源。
- claim 节点和 SUPPORTED_BY 关系留到阶段 4（LLM 接入）再实现。
- 后续图谱规模变大时可平滑迁移到 NetworkX 或数据库。

## D012：第一版 claim 抽取只基于 title + summary

- 状态：已接受
- 日期：2026-05-12

决策：

第一版 claim 抽取只使用论文的 title 和 summary（摘要），不解析 PDF 正文，不做 RAG。

原因：

- PDF 正文解析需要引入 PDF 解析工具、切分策略和更大的上下文窗口，这会让阶段 4 的 scope 过大。
- 论文的 title 和 summary 已经包含了论文的核心贡献和结论，足以抽取 1-3 条关键 claim。
- 不做 RAG 是因为当前目标是"从已知论文里抽 claim"，不是"搜索更多证据来验证 claim"。
- evidence_ids 由系统代码绑定（ev_{source_id}_title + ev_{source_id}_summary），不让 LLM 猜内部 ID，降低幻觉风险。
- 第一版只设 1-3 条 claim，避免一次抽取太多不可靠的声明。

影响：

- Claim 的 evidence_ids 固定指向论文 title 和 summary 两条 evidence。
- 后续阶段可以接入 PDF 解析后扩展更多 evidence 来源。
- 后续阶段可以基于 claim 做 supported/unsupported/conflict 验证。

## D013：阶段 4 开发期 Claim 抽取采用 fail-fast 策略

- 状态：已接受
- 日期：2026-05-12

决策：

Claim 抽取过程中任何 LLM 调用失败（API key 未配置、网络错误、非法 JSON 等）都应立即向上抛错，不吞掉异常。

原因：

- include_claims=true 表示用户明确要求 claim，返回空 claim_nodes 容易误导用户以为"没有抽到 claim"。
- 开发期应该尽早暴露 LLM 配置或调用问题。
- 如果某篇论文的 required evidence（title/summary）不存在于图谱中，也不应该继续——claim 必须能追溯真实 evidence。
- 后续产品成熟后可以再引入 partial success + warning 机制。

影响：

- enrich_graph_with_claims 不再捕获 ClaimExtractionError，任何单篇论文失败都会中断整个流程。
- extract_claims_for_paper 在调用 LLM 前先校验 title/summary evidence 是否存在。
- _build_claims 的 evidence_ids 由外部传入（已校验过的），不再内部硬编码。
- API 层将 ClaimExtractionError 转换为 HTTP 503。
