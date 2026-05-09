# ScholarAgent

ScholarAgent 是一个面向科研新手的科研复现与创新机会评估 Agent 项目。

本项目的目标不是做一个简单的聊天 Demo，也不是再造一个通用深度研究工具，而是逐步搭建一个接近真实工程项目的 AI Agent 系统：用户输入一个研究方向后，系统能够检索论文、调研 GitHub 项目、构建论文-代码-证据图谱、评估复现可行性、验证报告结论并挖掘可执行创新机会，帮助科研新手从模糊方向走到可复现、可改进、可展示的项目方案。

这个仓库会以“边学边做”的方式推进。每个阶段都应该有清晰的学习目标、可运行代码和可验证结果，避免一次性堆出一个看不懂的成品。

完整项目方案见：[docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)。
当前接手进度见：[docs/PROGRESS.md](docs/PROGRESS.md)。
关键决策记录见：[docs/DECISIONS.md](docs/DECISIONS.md)。

## 项目定位

ScholarAgent 的最终定位是：

> 面向科研新手的科研复现与创新机会评估 Agent。

它重点回答以下问题：

1. 一个研究方向有哪些关键论文？
2. 哪些论文有可用代码？
3. 论文中的方法、实验和代码实现是否能对上？
4. 哪些项目最适合科研新手复现？
5. 报告中的关键结论分别来自哪些证据？
6. 如果要做一个研究生项目，应该从哪里切入？
7. 系统为什么推荐这个项目，而不是另一个项目？

## 核心创新点

ScholarAgent 的核心不是“多 Agent”本身，而是一条可信的科研决策链路：

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

项目最终希望形成以下能力：

- Evidence Graph：把 paper、claim、method、repo、code_file、experiment、evidence 建模成可查询证据图谱。
- Paper-Code Alignment：判断论文方法、数据集、实验指标和 GitHub 代码实现是否能对齐。
- Reproducibility Scoring：基于代码完整度、依赖复杂度、数据可获得性、硬件成本和维护活跃度评估复现风险。
- Evidence RAG：不是做普通问答 RAG，而是为 claim verification 和 paper-code alignment 检索证据候选。
- Multi-Agent Verification：用不同 Agent 分别收集论文证据、代码证据、复现风险和引用验证结果。
- Reproducibility Benchmark：用人工标注的 paper-repo pair 评估系统质量。

## 核心理念

本项目优先追求以下几点：

- 可学习：每一步都要能解释清楚为什么这样设计。
- 可运行：每个阶段都要留下能跑通的小成果。
- 可追踪：Agent 的关键工具调用、观察结果和中间产物要能被记录。
- 可验证：重要结论要能追溯到论文、代码、README、issue 或工具观察证据。
- 可评估：不能只看生成结果是否“像样”，还要评估引用准确性、repo 匹配准确性和复现评分质量。
- 可扩展：后续可以加入更多数据源、Evidence RAG、多 Agent 验证和前端可视化。

## 技术路线摘要

详细技术路线和阶段规划以 [docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) 为准。

当前方向大致包括：

| 模块 | 作用 |
| --- | --- |
| FastAPI 后端 | 提供任务创建、状态查询和接口服务 |
| Pydantic 数据模型 | 约束论文、仓库、claim、evidence、trace 等结构化数据 |
| 论文检索工具 | 获取 arXiv、Semantic Scholar 等论文信息 |
| GitHub 调研工具 | 获取 repo、README、文件结构、issue 和活跃度信号 |
| Evidence Graph | 保存论文、代码、证据、claim 和复现评分之间的关系 |
| LangGraph 工作流 | 管理长流程、状态、节点输出、人工审核和可恢复执行 |
| Evidence RAG | 为 claim verification 和 paper-code alignment 检索证据 |
| 前端可视化 | 展示任务、证据图谱、对齐矩阵、复现评分、trace 和报告 |
| 评估模块 | 评估 repo 匹配、证据命中、引用准确性和复现评分质量 |

## Agent 设计原则

ScholarAgent 不采用“一个大 Agent 拿一堆工具循环到结束”的方式。

本项目更强调：

1. 确定性流程优先。
2. 结构化数据优先。
3. Evidence Graph 优先。
4. 小 Agent 优先。
5. 多 Agent 用于交叉验证，不用于堆概念。
6. 关键步骤可验证。
7. 所有重要结论都要有证据。

最终多 Agent 形态包括：

```text
Planner
  -> Paper Evidence Agent
  -> Code Evidence Agent
  -> Reproducibility Auditor
  -> Citation Verifier
  -> Mentor Report Writer
```

其中 Writer 只能基于已验证 evidence 生成报告，Verifier 可以标记或驳回 unsupported claim。

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
    PROJECT_PLAN.md
    PROGRESS.md
    DECISIONS.md
    architecture.md
    learning-notes.md
  docker-compose.yml
  AGENTS.md
  CLAUDE.md
  README.md
```

说明：

- `backend/app/agents/`：放 LangGraph 工作流和具体 Agent 节点逻辑。
- `backend/app/tools/`：放论文搜索、GitHub 搜索、网页浏览、PDF 解析等工具。
- `backend/app/models/`：放 Pydantic 模型和后续数据库模型。
- `backend/app/services/`：放任务管理、报告生成、评分和验证服务。
- `backend/app/storage/`：放 Evidence Graph、缓存和持久化相关逻辑。
- `frontend/`：放 Next.js / React 前端。
- `docs/`：记录最终方案、当前进度、关键决策、架构设计、学习笔记和阶段总结。

## 当前交接状态

截至目前：

- 项目目录：`/Users/xuhaoquan/project/ScholarAgent`
- GitHub 仓库：`https://github.com/Thyguad/ScholarAgent`
- 当前分支：`main`
- 项目还没有开始写业务代码。
- 已确定最终项目方案：[docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md)
- 当前进度记录：[docs/PROGRESS.md](docs/PROGRESS.md)
- 关键决策记录：[docs/DECISIONS.md](docs/DECISIONS.md)
- 下一步建议从“阶段 1：最小 FastAPI 后端”开始。

## 协作约定

这个项目的主要学习方式是：先理解，再实现，再验证。

用户是初学者，每次新增功能时，应尽量遵循以下流程：

1. 先说明这一小步要解决什么问题。
2. 再说明需要新增或修改哪些文件。
3. 编写尽量少但工程风格正确的代码。
4. 写代码时为关键逻辑添加中文注释，方便初学者理解。
5. 运行测试、本地服务或命令验证结果。
6. 总结这一阶段学到了什么。
7. 在用户同意后再提交 git，保持仓库历史清晰。

如果后续由另一个 AI 或开发者接手，请优先阅读 `AGENTS.md`、[docs/PROJECT_PLAN.md](docs/PROJECT_PLAN.md) 和 [docs/PROGRESS.md](docs/PROGRESS.md)，不要直接跳到复杂功能。
