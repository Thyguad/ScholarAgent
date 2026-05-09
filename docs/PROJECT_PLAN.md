# ScholarAgent 最终项目方案：科研复现与创新机会评估 Agent

## 一句话定位

ScholarAgent 是一个面向科研新手的科研复现与创新机会评估 Agent。

它帮助用户从一个模糊研究主题出发，构建论文-代码-证据图谱，筛选出值得复现和改进的论文项目，并为每个建议提供论文、代码、实验、证据链和复现风险判断。

更具体地说，ScholarAgent 不只是生成一份“看起来像样”的调研报告，而是把科研调研建模成一个可审计、可评分、可复现的决策支持系统。

它要回答科研新手最关心的几个问题：

1. 这个方向有哪些关键论文？
2. 哪些论文有可用代码？
3. 哪些项目最适合新手复现？
4. 论文中的方法、实验和代码实现是否能对上？
5. 如果要做一个研究生项目，应该从哪里切入？
6. 报告里的关键结论分别来自哪些证据？
7. 系统为什么推荐这个项目，而不是另一个项目？

## 项目边界

ScholarAgent 不是一个通用深度研究 Agent，也不是一个新的 Agent 框架，更不是一个普通 RAG 问答机器人。

本项目的核心边界是：

- 不追求“什么都能研究”，优先聚焦 AI / LLM / Agent / Software Engineering 等计算机科研方向。
- 不追求一次性自动完成完整科研，而是帮助科研新手完成选题、调研、复现判断和初步创新设计。
- 不把“多 Agent”当成卖点，而是把可验证的科研决策链路当成卖点。
- 不把 RAG 做成普通聊天知识库，而是把 RAG 用作证据检索和 claim verification 的基础设施。
- 不让模型自由发挥所有步骤，而是用确定性工具和结构化数据约束关键流程。

项目主线可以概括为：

```text
Research Topic
  -> Paper Search
  -> Paper Understanding
  -> Repository Discovery
  -> Evidence Graph Construction
  -> Paper-Code Alignment
  -> Reproducibility Scoring
  -> Multi-Agent Verification
  -> Evidence-grounded Report
  -> Innovation Opportunity Mining
```

## 差异化判断

当前主流 Agent 项目已经覆盖了很多通用能力：

- GPT Researcher：擅长通用网页调研和带引用报告。
- deep-research 类项目：擅长递归搜索、广度/深度探索和长报告生成。
- SWE-agent：擅长代码仓库任务执行、轨迹记录和可复现实验。
- CrewAI / MetaGPT：擅长多角色协作和流程编排。
- LangGraph / DeerFlow：擅长长流程、状态管理、子 Agent 和可观测执行。

ScholarAgent 的差异化不在于“也能调研”，而在于把科研调研转化为一个可审计、可评分、可复现、可评估的决策支持系统。

核心护城河是：

```text
paper-code-evidence-graph-reproducibility-benchmark
```

也就是把论文、代码、证据图谱、复现可行性和评估集连接起来。

面试中真正有冲击力的表达不是“我做了一个多 Agent 调研助手”，而是：

> 我把科研调研从文本生成问题，建模成了 evidence graph 构建和验证问题。

## 最终核心能力

### 1. Evidence Graph

Evidence Graph 是 ScholarAgent 最终版本的核心数据结构。

系统不只保存论文列表和报告文本，而是把调研过程中的关键对象建成图谱：

| 节点类型 | 示例 |
| --- | --- |
| paper | 一篇论文 |
| claim | 论文或报告中的一个关键结论 |
| method | 一个方法、模型、算法或模块 |
| dataset | 数据集或 benchmark |
| metric | 评价指标 |
| repo | GitHub 仓库 |
| code_file | 代码文件或目录 |
| experiment | 训练、评估、复现实验 |
| evidence | 摘要片段、README 片段、issue、commit、工具观察 |
| opportunity | 可执行创新机会 |

图谱中的关系包括：

| 关系 | 含义 |
| --- | --- |
| `paper_has_claim` | 论文提出了某个 claim |
| `claim_supported_by` | claim 被某个 evidence 支持 |
| `method_implemented_by` | 方法在某个代码文件中有实现 |
| `experiment_described_by` | 实验由 README、脚本或配置说明 |
| `repo_has_risk` | 仓库存在某类复现风险 |
| `report_claim_verified_by` | 报告结论由某个证据节点验证 |
| `opportunity_derived_from` | 创新机会来自某些 gap 或冲突 |

这会让项目从“生成报告”升级成“构建可验证科研证据图谱”。

### 2. 论文检索与结构化理解

系统根据用户输入的研究主题，检索 arXiv、Semantic Scholar 等来源，返回结构化论文列表。

每篇论文至少应抽取：

- 标题
- 作者
- 年份
- 摘要
- 论文链接
- 关键词
- 研究任务
- 方法概述
- 数据集
- 评价指标
- 可能的代码链接

这一阶段的重点不是生成漂亮总结，而是把论文变成后续模块能使用的结构化数据。

### 3. 论文-代码对齐矩阵

这是 ScholarAgent 的核心创新点之一。

系统需要为论文寻找相关 GitHub 仓库，并判断论文内容和代码实现之间的关系。

对齐矩阵至少包含：

| 维度 | 说明 |
| --- | --- |
| repo 来源 | official / likely official / third-party / not found |
| 方法实现 | 论文中的核心方法是否能在代码中找到对应实现 |
| 数据集支持 | 代码是否提供数据下载、预处理或加载逻辑 |
| 实验脚本 | 是否存在训练、评估、复现实验脚本 |
| 指标支持 | 是否能复现论文中的核心指标 |
| 文档完整度 | README、安装说明、示例是否清晰 |
| 维护活跃度 | star、最近提交、issue、release 等信号 |

输出目标不是“找到一个 repo”，而是回答：

> 这篇论文的代码是否真的支撑它声称的方法和实验？

### 4. 复现可行性评分

这是面向科研新手的关键能力。

系统为每个 paper-repo pair 计算复现可行性评分，帮助用户判断优先复现哪个项目。

建议评分维度：

| 维度 | 含义 |
| --- | --- |
| code_availability | 是否有代码，是否疑似官方 |
| installability | 依赖是否清楚，环境是否容易安装 |
| data_availability | 数据集、模型权重是否可获得 |
| experiment_clarity | 是否有明确训练、评估、复现说明 |
| hardware_cost | 是否需要较高 GPU 成本 |
| maintenance_activity | 仓库是否仍在维护 |
| result_reproducibility_signals | issue、README、文档中是否有复现成功或失败信号 |

评分原则：

- 规则评分为主，LLM 解释为辅。
- 每个分数必须有证据来源。
- 不给没有证据的主观高分。

最终输出应能回答：

> 如果我是科研新手，哪 3 个项目最值得先复现？为什么？

### 5. Evidence RAG

ScholarAgent 需要 RAG，但不是普通“文档聊天式 RAG”。

本项目中的 RAG 定位是 Evidence RAG：

```text
用户或 Verifier 提出一个 claim
  -> 检索最可能支持或反驳它的论文片段、README 片段、代码片段、issue 片段
  -> 返回 evidence candidates
  -> Verifier 判断 supported / weakly_supported / unsupported / conflict
```

Evidence RAG 的使用场景：

- 为报告 claim 找证据。
- 为论文方法找可能对应的代码文件。
- 为复现风险评分找 README、issue 或配置证据。
- 为创新机会挖掘找 limitation、issue 和 benchmark gap。

前期可以先用关键词检索和结构化字段匹配，后期再引入 Qdrant 做向量检索。

### 6. Multi-Agent Verification Workflow

ScholarAgent 最终版应该使用多 Agent，但不是角色扮演式多 Agent。

多 Agent 的价值在于分工收集证据、独立判断、交叉验证。

推荐工作流：

```text
Planner
  -> Paper Evidence Agent
  -> Code Evidence Agent
  -> Reproducibility Auditor
  -> Citation Verifier
  -> Mentor Report Writer
```

各 Agent 的边界：

| Agent | 职责 |
| --- | --- |
| Planner | 将研究主题拆成调研问题、关键词和阶段计划 |
| Paper Evidence Agent | 检索论文、抽取 claim、方法、数据集和指标 |
| Code Evidence Agent | 搜索 GitHub repo，分析 README、文件结构和代码入口 |
| Reproducibility Auditor | 根据证据计算复现可行性评分和风险解释 |
| Citation Verifier | 检查报告 claim 是否有证据支持 |
| Mentor Report Writer | 只基于已验证 evidence 生成面向新手的报告和建议 |

关键约束：

- Writer 不能凭空生成关键结论。
- Verifier 可以驳回 unsupported claim。
- 每个 Agent 输出结构化结果，而不是自由文本。
- 多 Agent 是为了独立证据收集和验证，不是为了看起来复杂。

### 7. Claim-level Citation Verification

ScholarAgent 生成报告后，需要把报告中的关键 claim 拆出来，并绑定证据。

一个 claim 可以来自：

- 论文元数据
- 论文摘要或正文片段
- GitHub README
- GitHub 文件结构
- issue / release / commit 信息
- 工具调用返回的结构化观察

每个 claim 标注支持状态：

| 状态 | 含义 |
| --- | --- |
| supported | 有明确证据支持 |
| weakly_supported | 有相关证据，但不够直接 |
| unsupported | 暂无证据支持 |
| conflict | 不同来源之间存在冲突 |

这一能力的目标是降低 LLM 报告中的幻觉和错误引用。

### 8. Research Trace Replay

ScholarAgent 需要记录 Agent 的关键执行过程，形成可回放 trace。

trace 不记录模型隐藏推理，而是记录可审计的过程摘要：

- 当前阶段
- 输入是什么
- 调用了什么工具
- 工具返回了什么观察
- 产生了什么结构化结果
- 为什么进入下一步
- 哪些结论绑定了哪些证据
- 哪些地方需要人工审核

trace 的价值是：

- 方便调试 Agent。
- 方便用户理解报告从哪里来。
- 方便后续做前端可视化。
- 方便面试时展示工程深度。

### 9. Reproducibility Benchmark

为了证明 ScholarAgent 不是一个“感觉有用”的 Demo，最终需要建立一个小型评估集。

建议维护 20 个左右的经典 paper-repo pair，人工标注：

- 论文标题
- 官方 repo
- 关键代码文件
- 数据集可获得性
- 训练或评估入口
- 复现难度
- 常见复现风险
- 关键 claim 对应证据

用这个评估集衡量：

- repo 匹配是否准确
- evidence 是否命中
- 复现评分是否接近人工判断
- 报告 claim 是否被证据支持

这个模块会显著提升项目含金量，因为它说明项目不仅能生成结果，还能评估自己的结果质量。

### 10. 创新机会挖掘

创新机会不应该由模型凭空生成，而应该来自结构化 gap。

可挖掘的 gap 包括：

- 高引用论文没有可靠代码。
- 多篇论文共享同一个未解决 limitation。
- 某类方法尚未迁移到新的模型、任务或数据集。
- GitHub issue 中反复出现复现困难。
- 论文 claim 和代码实现之间存在不一致。
- benchmark 缺少某类 ablation 或对比实验。

每个创新机会应包含：

- opportunity：机会描述
- evidence：证据来源
- feasibility：可行性
- first_experiment：第一个实验怎么做
- expected_contribution：预期贡献
- risk：主要风险

## Agent 设计原则

本项目不采用“一个大 Agent 拿一堆工具循环到结束”的方式。

采用原则是：

1. 确定性流程优先。
2. 结构化数据优先。
3. Evidence Graph 优先。
4. 小 Agent 优先。
5. 多 Agent 用于交叉验证，不用于堆概念。
6. 关键步骤可验证。
7. 所有重要结论都要有证据。

最终形态可以是多 Agent，但每个 Agent 都要有明确输入、输出和验收标准。

```text
Planner 负责拆问题
Paper Evidence Agent 负责论文证据
Code Evidence Agent 负责代码证据
Reproducibility Auditor 负责复现风险
Citation Verifier 负责证据校验
Mentor Report Writer 负责面向新手表达
```

这种设计的面试价值在于：

> 系统不是让一个大模型直接写报告，而是先收集 paper evidence 和 code evidence，再通过 verifier 限制最终结论。

LLM 适合做：

- 查询改写
- 摘要压缩
- 结构化抽取
- 证据解释
- 报告组织
- gap 分析
- claim 拆解
- evidence relevance 判断

确定性代码适合做：

- API 调用
- 数据清洗
- 字段校验
- 评分规则
- URL 去重
- trace 记录
- 状态流转
- 缓存和持久化
- evidence graph 写入
- 评估指标计算

## 推荐技术路线

### 后端

- FastAPI：提供 API 服务。
- Pydantic：定义请求、响应、论文、仓库、证据、trace 等结构。
- pytest：验证工具函数和接口。
- Ruff：格式化和静态检查。

### Agent 工作流

- LangGraph：在中后期管理长流程、状态、人工审核和断点恢复。
- ReAct：只用于具体节点内部，不作为整个系统的主结构。
- 多 Agent：用于论文证据、代码证据、复现审计和 citation verification 的独立分工。

### Evidence Graph

- 前期：用 Pydantic 模型和本地 JSON 表示节点与边。
- 中期：用 PostgreSQL 存储 paper、repo、claim、evidence、score、trace。
- 后期：增加图查询视图，支持查看 claim 到 evidence 的完整路径。

### Evidence RAG

- 前期：使用关键词检索、字段匹配和简单 chunk。
- 中期：使用 Qdrant 存论文摘要、PDF 片段、README、issue 和代码片段。
- 后期：将 RAG 检索结果交给 Verifier 判断支持关系，而不是直接生成回答。

### 数据源

- arXiv API：第一阶段论文检索。
- Semantic Scholar API：第二阶段补充引用、venue、作者等信息。
- GitHub REST API：第一阶段 GitHub 仓库调研。
- GitHub GraphQL API：后续需要一次性组合多个字段时使用。

### 存储

- 前期：内存对象或本地 JSON，方便学习和调试。
- 中期：PostgreSQL 存任务、论文、仓库、claim、evidence、报告和 trace。
- 后期：Qdrant 存论文、README、issue、网页和代码片段的向量索引。

### 评估

- 前期：用人工样例检查 paper search、repo match 和报告引用。
- 中期：建立 20 个 paper-repo pair 的 Reproducibility Benchmark。
- 后期：评估 repo_match_accuracy、evidence_hit_rate、citation_precision 和 reproducibility_score_quality。

### 前端

- Next.js + React + TypeScript。
- Tailwind CSS + shadcn/ui。
- React Flow 展示 Agent trace 和工作流图。

前端后置，先保证后端链路和证据质量。

## 阶段规划

### 阶段 1：最小 FastAPI 后端

目标：

- 创建 `backend/`。
- 实现 `/health`。
- 实现最小研究任务接口。

学习重点：

- Python 项目结构。
- FastAPI 基础。
- Pydantic 请求和响应模型。

验收标准：

- 本地服务能启动。
- `/health` 返回正常状态。
- 能提交一个研究主题。

### 阶段 2：论文搜索 MVP

目标：

- 接入 arXiv。
- 输入研究主题，返回结构化论文列表。
- 为每篇论文保留来源 URL。

验收标准：

- 输入一个主题，返回 5 到 10 篇论文。
- 每篇论文有标题、摘要、链接和基础元数据。

### 阶段 3：简版 Evidence Graph

目标：

- 定义 paper、claim、evidence、trace 的基础数据结构。
- 将论文搜索结果写入简版证据图谱。
- 为每个论文摘要和元数据保留 evidence 节点。

验收标准：

- 每篇论文都能对应到 evidence 节点。
- 能从一个 claim 找到它的来源论文或摘要证据。

### 阶段 4：基础 Evidence Report

目标：

- 基于论文列表和 evidence graph 生成结构化 Markdown 报告。
- 报告中的每个小结都带来源。

验收标准：

- 不是自由发挥式报告。
- 每个关键段落能追溯到 evidence graph 中的来源。

### 阶段 5：GitHub 仓库发现

目标：

- 根据论文标题、作者、链接或关键词寻找 GitHub repo。
- 标注 repo 来源置信度。

验收标准：

- 每篇论文输出 repo 候选。
- 标注 official / likely official / third-party / not found。

### 阶段 6：论文-代码对齐矩阵

目标：

- 分析 README、文件结构、requirements、examples、scripts。
- 输出 paper-code alignment matrix，并将 repo、code_file、experiment 写入 evidence graph。

验收标准：

- 能说明论文方法和代码实现是否存在对应关系。
- 能说明实验和数据是否有复现入口。

### 阶段 7：复现可行性评分

目标：

- 实现规则评分。
- 为每个评分输出证据和解释。

验收标准：

- 能排序出最适合新手复现的项目。
- 分数不是纯 LLM 主观判断。

### 阶段 8：LangGraph 工作流化

目标：

- 将 pipeline 改造成 LangGraph 状态机。
- 加入 typed state、节点级 trace 和失败重试。

验收标准：

- 每个节点输入输出清晰。
- 中间状态可查看。
- 部分节点失败时可定位原因。

### 阶段 9：Multi-Agent Verification Workflow

目标：

- 将论文证据、代码证据、复现审计和 citation verification 拆成独立 Agent 节点。
- 使用 Verifier 检查 Writer 的关键结论。

验收标准：

- 每个 Agent 都有结构化输出。
- Writer 只能使用已验证 evidence。
- unsupported claim 会被标记或移除。

### 阶段 10：Evidence RAG

目标：

- 将论文摘要、PDF 片段、README、issue 和代码片段切分入库。
- 为 claim verification 和 paper-code alignment 提供 evidence candidates。

验收标准：

- 输入一个 claim，能检索出可能支持或反驳它的证据片段。
- RAG 结果不直接生成结论，而是交给 Verifier 判断。

### 阶段 11：Claim-level Citation Verification

目标：

- 抽取报告中的关键 claim。
- 为 claim 绑定 evidence。
- 标注 supported / weakly_supported / unsupported / conflict。

验收标准：

- 报告后附 verification appendix。
- 用户能看到哪些结论证据强，哪些需要谨慎。

### 阶段 12：Reproducibility Benchmark

目标：

- 建立 20 个左右的人工标注 paper-repo pair。
- 用于评估 repo 匹配、证据命中和复现评分质量。

验收标准：

- 有固定 benchmark 数据。
- 能输出 repo_match_accuracy、citation_precision、evidence_hit_rate 等指标。

### 阶段 13：创新机会挖掘

目标：

- 基于论文、代码、复现评分和 issue 信号生成可执行创新点。

验收标准：

- 每个创新点都有证据、首个实验和风险说明。
- 不输出空泛建议。

### 阶段 14：前端可视化和作品包装

目标：

- 展示任务列表、论文列表、evidence graph、对齐矩阵、复现评分、trace 和报告。
- 准备简历描述、架构图和演示材料。

验收标准：

- 可以完整演示一次从主题到项目建议的流程。
- 面试时能讲清楚架构、取舍和评估方法。

## MVP 收敛版本

为了避免项目过大，第一版可交付 MVP 应控制在以下范围：

```text
输入研究主题
  -> arXiv 搜索论文
  -> 结构化论文列表
  -> 简版 Evidence Graph
  -> GitHub repo 候选发现
  -> 简版复现可行性评分
  -> 带来源的 Markdown 报告
```

第一版暂不做：

- PDF 全文解析
- Qdrant 向量库
- 复杂多 Agent 角色系统
- 自动跑代码实验
- 完整前端大屏
- 大规模评估体系

第一版要保留的“高级项目基因”是：

- 所有关键结论都能落到 evidence 节点。
- 复现评分必须有规则和证据。
- 报告不是自由写作，而是基于 evidence graph 生成。
- 后续能自然扩展到多 Agent、RAG 和 benchmark。

## 评估指标

后期可以建立固定测试集，例如 5 到 10 个研究主题：

- LLM Agent for Software Engineering
- Retrieval-Augmented Generation Evaluation
- Code Agent Benchmark
- Multi-Agent Collaboration for Research
- LLM-based Program Repair

最终建议建立 Reproducibility Benchmark，包含 20 个左右的人工标注 paper-repo pair。

每条样本至少标注：

- official repo
- repo confidence
- 关键代码文件
- 数据集可获得性
- 实验入口
- 复现难度
- 关键 claim 的支持证据

建议评估指标：

| 指标 | 含义 |
| --- | --- |
| paper_recall | 是否找到主题下关键论文 |
| repo_match_accuracy | 论文和 repo 匹配是否正确 |
| evidence_hit_rate | 是否能检索到支持 claim 的证据 |
| citation_precision | 报告引用是否真的支持 claim |
| reproducibility_score_quality | 复现评分是否符合人工判断 |
| unsupported_claim_rate | 报告中无证据 claim 的比例 |
| trace_completeness | 关键步骤是否有 trace |
| report_usefulness | 报告是否能帮助用户决定下一步 |

## 简历表述

不建议写：

> 基于 LangGraph 和多 Agent 实现科研调研助手，自动搜索论文并生成报告。

建议写：

> 设计并实现面向科研新手的科研复现与创新机会评估 Agent，构建论文-代码-证据图谱，将论文检索、GitHub 代码分析、论文-代码对齐、复现风险评分与 citation verification 整合为可追踪的 LangGraph 工作流。

更工程化的版本：

> 构建基于 LangGraph 的可审计科研调研工作流，使用 typed state、Evidence Graph、Evidence RAG、节点级缓存、失败重试和 provenance tracking，将每个研究结论绑定到论文、GitHub 文件或工具观察证据，降低 LLM 生成报告中的不可验证 claim。

可以拆成技术亮点：

- Agent Workflow Engineering：将长程科研调研拆解为可恢复状态机，避免单轮 LLM 调用不可控。
- Evidence Graph：将 paper、claim、method、repo、code_file、experiment 和 evidence 建模为可查询证据图谱。
- Evidence RAG：不是做普通知识库问答，而是为 claim verification 和 paper-code alignment 检索证据候选。
- Multi-Agent Verification：用 Paper Evidence Agent、Code Evidence Agent、Reproducibility Auditor 和 Citation Verifier 交叉验证报告结论。
- Evidence Grounding：实现 claim-level evidence linking，提升科研报告可信度。
- Paper-Code Alignment：从论文方法、实验设置、数据集、指标和 GitHub 文件结构中抽取信号，判断代码是否支撑论文 claim。
- Reproducibility Scoring：综合代码完整度、依赖复杂度、数据可获得性、硬件成本和维护活跃度，为科研新手推荐低风险复现项目。
- Benchmark Evaluation：建立人工标注 paper-repo pair，用 repo_match_accuracy、evidence_hit_rate 和 citation_precision 评估系统质量。

## 面试时重点讲什么

面试中不要只讲“用了哪些框架”，而要讲工程取舍：

1. 为什么不用一个大 Agent，而用可控 workflow？
2. 哪些步骤用规则，哪些步骤用 LLM？
3. 如何避免报告幻觉？
4. 如何定义和计算复现可行性？
5. 如何让每个结论可追踪？
6. 如果论文和代码不一致，系统如何处理？
7. 如何评估报告是否真的有用？
8. 为什么这里的 RAG 是 Evidence RAG，而不是普通问答 RAG？
9. 多 Agent 如何服务于验证，而不是简单角色扮演？

## 当前结论

ScholarAgent 的最终方向确定为：

> 面向科研新手的科研复现与创新机会评估 Agent。

项目最重要的不是“多 Agent”本身，而是构建一条可信的科研决策链路：

```text
论文是否重要
  -> 代码是否存在
  -> 证据图谱是否完整
  -> 实验是否能复现
  -> 结论是否有证据
  -> 系统评估是否可靠
  -> 新手是否值得做
  -> 可以从哪个创新点切入
```

最终让项目“眼前一亮”的不是用了多少框架，而是这三个结果：

1. 能构建论文-代码-证据图谱。
2. 能用多 Agent 和 Evidence RAG 验证报告 claim。
3. 能用 Reproducibility Benchmark 评估系统质量。

只要守住这条主线，ScholarAgent 就能从普通调研助手变成一个有简历含金量的 AI Agent 工程项目。
