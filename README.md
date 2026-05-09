# ScholarAgent

ScholarAgent 是一个面向研究生的科研调研与项目孵化智能体项目。

本项目的目标不是做一个简单的聊天 Demo，而是逐步搭建一个接近真实工程项目的 AI Agent 系统：用户输入一个研究方向后，系统能够自动完成论文检索、GitHub 项目调研、技术路线分析、实验计划生成、报告撰写和过程追踪，帮助科研新手从一个模糊方向走到一个可执行的项目方案。

这个仓库会以“边学边做”的方式推进。每个阶段都应该有清晰的学习目标、可运行代码和可验证结果，避免一次性堆出一个看不懂的成品。

## 项目目标

ScholarAgent 希望最终支持以下能力：

1. 输入一个研究主题，例如 `LLM Agent for Software Engineering`。
2. 自动检索相关论文，包括 arXiv、Semantic Scholar 等来源。
3. 自动调研相关 GitHub 项目，包括 star、活跃度、技术栈、README、issue 情况等。
4. 对论文和开源项目进行交叉分析，生成技术路线图。
5. 给出适合研究生入门的学习路径、复现计划和可选创新点。
6. 生成带引用来源的 Markdown / PDF 调研报告。
7. 记录 Agent 的执行过程，包括调用了什么工具、得到了什么观察结果、为什么进入下一步。
8. 支持人工审核和修改关键步骤，降低幻觉和错误引用。
9. 最终形成一个可以用于实习展示的完整 AI Agent 工程项目。

## 核心理念

本项目优先追求以下几点：

- 可学习：每一步都要能解释清楚为什么这样设计。
- 可运行：每个阶段都要留下能跑通的小成果。
- 可追踪：Agent 的关键决策、工具调用和中间结果要能被记录。
- 可评估：不能只看生成结果是否“像样”，还要评估引用准确性、检索覆盖率和报告可靠性。
- 可扩展：后续可以加入更多数据源、工具、模型和 Agent 工作流。

## 技术选型

当前计划采用以下技术栈：

| 模块 | 技术 | 作用 |
| --- | --- | --- |
| 后端服务 | FastAPI | 提供 API、任务创建、运行状态查询和前后端通信 |
| Agent 编排 | LangGraph | 管理长流程、多步骤、可恢复的 Agent 工作流 |
| Agent 范式 | ReAct | 在具体节点内部实现“推理 -> 调用工具 -> 观察 -> 继续推理”的循环 |
| 数据模型 | Pydantic | 约束请求、响应和 Agent 结构化输出 |
| 论文检索 | arXiv API、Semantic Scholar API | 获取论文元数据、摘要、引用信息 |
| GitHub 调研 | GitHub REST / GraphQL API、GitHub MCP | 获取仓库信息、README、活跃度和项目指标 |
| 浏览器自动化 | browser-use / Playwright | 处理普通 API 难以覆盖的网页调研任务 |
| 向量检索 | Qdrant | 存储论文、README、网页材料的向量索引 |
| 数据库 | PostgreSQL | 保存项目、任务、论文、仓库、报告和运行记录 |
| 缓存 / 队列 | Redis、Celery 或 RQ | 支持长任务、异步执行和状态缓存 |
| 前端界面 | Next.js、React、TypeScript | 构建研究任务面板、Agent trace、报告编辑和可视化界面 |
| UI 组件 | Tailwind CSS、shadcn/ui、React Flow | 快速搭建现代化界面和工作流图 |
| 评估 | DeepEval、自定义指标 | 评估报告事实性、引用准确性和 Agent 任务完成质量 |
| 部署 | Docker Compose | 本地一键启动后端、前端、数据库和向量库 |

## Agent 设计

项目中会逐步实现多个 Agent 或工作流节点：

| 名称 | 职责 |
| --- | --- |
| Planner Agent | 拆解用户输入的研究主题，生成调研计划 |
| Paper Search Agent | 检索论文、筛选论文、提取论文关键信息 |
| GitHub Research Agent | 检索和分析开源项目，评估项目质量与可复现性 |
| RAG Builder Agent | 将论文、README、网页内容构建为可检索知识库 |
| Critic / Verifier Agent | 检查引用、事实一致性和报告中的潜在幻觉 |
| Report Writer Agent | 生成结构化科研调研报告和项目路线图 |

整体工作流由 LangGraph 管理，单个节点内部可以使用 ReAct 模式完成动态工具调用。

示意流程：

```text
User Topic
  -> Planner Agent
  -> Paper Search Agent
  -> GitHub Research Agent
  -> Synthesis
  -> Critic / Verifier Agent
  -> Report Writer Agent
  -> Final Report
```

## 计划目录结构

当前仓库仍处于初始化阶段，后续计划演进为：

```text
ScholarAgent/
  backend/
    app/
      api/
      core/
      agents/
      tools/
      models/
      services/
      storage/
      main.py
    tests/
    pyproject.toml
  frontend/
    app/
    components/
    lib/
    package.json
  docs/
    architecture.md
    learning-notes.md
  docker-compose.yml
  README.md
```

说明：

- `backend/app/agents/`：放 LangGraph 工作流和具体 Agent 逻辑。
- `backend/app/tools/`：放论文搜索、GitHub 搜索、网页浏览、PDF 解析等工具。
- `backend/app/models/`：放 Pydantic 模型和数据库模型。
- `backend/app/services/`：放业务服务，例如任务管理、报告生成、评估服务。
- `frontend/`：放 Next.js / React 前端。
- `docs/`：记录架构设计、学习笔记、阶段总结，方便后续交接。

## 阶段路线

### 阶段 0：项目准备

目标：

- 初始化仓库。
- 明确项目方向、技术栈和 README。
- 准备 GitHub 远程仓库和 MCP 配置。

当前状态：

- 本地仓库已初始化。
- GitHub 仓库已创建。
- README 正在完善。

### 阶段 1：最小 FastAPI 后端

目标：

- 创建 `backend/`。
- 配置 Python 项目。
- 实现 `/health` 接口。
- 实现一个接收研究主题的接口，例如 `POST /research/topics`。

学习重点：

- Python 项目结构。
- FastAPI 基础。
- Pydantic 请求和响应模型。
- 本地运行与接口测试。

### 阶段 2：第一个论文搜索工具

目标：

- 接入 arXiv API 或 Semantic Scholar API。
- 输入关键词，返回结构化论文列表。
- 将搜索工具封装成 Agent 可调用的 tool。

学习重点：

- API 调用。
- 工具封装。
- 结构化数据建模。

### 阶段 3：第一个 ReAct Agent

目标：

- 构建一个能调用论文搜索工具的最小 ReAct Agent。
- 让 Agent 根据用户主题搜索论文并生成简短总结。

学习重点：

- ReAct 的 Thought / Action / Observation 模式。
- Tool calling。
- 如何限制 Agent 输出格式。

### 阶段 4：LangGraph 工作流

目标：

- 使用 LangGraph 串联 Planner、Paper Search 和 Report Writer。
- 保存每一步的状态。
- 为后续 human-in-the-loop 和断点恢复打基础。

学习重点：

- 状态图。
- 节点。
- 边。
- checkpoint。
- 可观测的 Agent 执行流程。

### 阶段 5：数据存储和任务系统

目标：

- 引入数据库保存研究主题、任务运行、论文和报告。
- 支持查询历史任务和运行状态。

学习重点：

- 数据库建模。
- 异步任务。
- 后端服务分层。

### 阶段 6：前端可视化

目标：

- 使用 Next.js / React 构建基础界面。
- 展示研究任务、论文列表、GitHub 项目列表和 Agent 执行时间线。

学习重点：

- 前后端通信。
- Agent trace 可视化。
- React Flow 工作流图。

### 阶段 7：RAG 和知识库

目标：

- 支持上传或抓取论文 PDF。
- 对论文、README 和网页材料切分、向量化、入库。
- 支持基于证据的问答和报告生成。

学习重点：

- Embedding。
- 向量数据库。
- RAG。
- 引用溯源。

### 阶段 8：成熟化和作品包装

目标：

- 加入评估模块。
- 加入 Docker Compose。
- 完善 README、架构图和演示视频。
- 准备简历项目描述和面试讲解材料。

学习重点：

- LLM 应用评估。
- 工程化部署。
- 项目展示和技术表达。

## 当前交接状态

截至目前：

- 项目目录：`/Users/xuhaoquan/project/ScholarAgent`
- GitHub 仓库：`https://github.com/Thyguad/ScholarAgent`
- 当前分支：`main`
- 最近提交：请使用 `git log --oneline -1` 查看
- 项目还没有开始写业务代码。
- 下一步建议从“阶段 1：最小 FastAPI 后端”开始。

## 协作约定

这个项目的主要学习方式是：先理解，再实现，再验证。

每次新增功能时，应尽量遵循以下流程：

1. 先说明这一小步要解决什么问题。
2. 再说明需要新增或修改哪些文件。
3. 编写尽量少但工程风格正确的代码。
4. 运行测试或本地服务验证结果。
5. 总结这一阶段学到了什么。
6. 提交到 git，保持仓库历史清晰。

如果后续由另一个 AI 或开发者接手，请优先阅读本 README，并从“当前交接状态”和“阶段路线”继续推进，不要直接跳到复杂功能。
