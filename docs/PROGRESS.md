# ScholarAgent Progress

本文件用于记录 ScholarAgent 的当前进度和下一步接手信息。

如果后续由新的 AI 或开发者接手，请先读：

1. `AGENTS.md`：了解协作方式和代码约束。
2. `docs/PROGRESS.md`：确认当前做到哪一步。
3. `docs/PROJECT_PLAN.md`：了解项目总方案和阶段规划。
4. `docs/DECISIONS.md`：理解关键技术决策的原因。

## 当前快照

- 最后更新：2026-05-12
- 当前分支：`main`
- 当前阶段：阶段 3（简版 Evidence Graph）开发中，核心代码和测试已完成
- 当前状态：已有最小后端入口、研究任务提交接口、统一论文模型、OpenAlex + arXiv 多源论文搜索、Evidence/EvidenceGraph 数据模型、graph_builder 服务、/papers/search 支持可选的证据图谱返回。26 个测试全部通过。
- 项目定位：面向科研新手的科研复现与创新机会评估 Agent
- 详细方案来源：`docs/PROJECT_PLAN.md`

## 已完成

**文档和规划：**
- 阅读并重构了项目 README。
- 明确了 ScholarAgent 的最终定位和核心创新点。
- 确定项目主线为论文、代码、证据图谱、复现评分、验证和创新机会挖掘。
- 新增 `AGENTS.md`，约束 Codex、Claude Code 等 coding agent 的协作方式。
- 新增 `CLAUDE.md`，让 Claude Code 自动继承项目级 agent 约定。
- 新增 `docs/PROJECT_PLAN.md`，沉淀完整项目方案、技术路线、阶段规划和简历表达。
- 新增 `docs/PROGRESS.md`，记录当前阶段和下一步接手信息。
- 新增 `docs/DECISIONS.md`，记录关键决策原因。

**阶段 1（最小 FastAPI 后端）：**
- 创建 `backend/` 最小后端工程。
- 实现 FastAPI 应用入口 `backend/app/main.py`。
- 实现 `/health` 健康检查接口。
- 实现 `POST /research/tasks` 最小研究任务提交接口。
- 使用 Pydantic 定义研究任务请求和响应模型。
- 添加接口测试 `backend/tests/test_main.py`。
- 使用 uv 管理后端 Python 环境。

**阶段 2（论文搜索 MVP）：**
- 生成 `backend/uv.lock`，锁定依赖版本。
- 将 `httpx` 调整为后端运行时依赖。
- 新增 `backend/app/models/paper.py`，定义统一论文结果模型。
- 新增 `backend/app/tools/arxiv_search.py`，封装 arXiv API 请求和 XML 解析逻辑（限流重试、超时、异常处理）。
- 新增 `backend/tests/test_arxiv_search.py`，验证 arXiv XML 转换（6 个测试）。
- 新增 `GET /papers/search`，返回结构化论文列表。
- 新增 `backend/.env.example` 和 `backend/app/core/config.py`，集中管理 API key。
- 新增 `backend/app/tools/openalex_search.py`，封装 OpenAlex `/works` 搜索和倒排索引还原。
- 新增 `backend/app/tools/paper_search.py`，实现”OpenAlex 优先，arXiv 兜底”的多源搜索。
- 新增 OpenAlex 和多源搜索测试（4 个测试）。
- 18 个测试全部通过，真实 OpenAlex API 端到端验证通过。

**阶段 3（简版 Evidence Graph）：**
- 新增 `backend/app/models/evidence_graph.py`，定义 Evidence 和 EvidenceGraph Pydantic 模型。
- 新增 `backend/app/services/__init__.py` 和 `backend/app/services/graph_builder.py`，实现论文到证据节点的转换。
- 修改 `backend/app/main.py`，`/papers/search` 新增 include_graph 参数，可返回 EvidenceGraph。
- 新增 `backend/tests/test_evidence_graph.py`（7 个测试），覆盖溯源、字段覆盖、空列表、ID 稳定性等。
- 新增 API 层测试：验证 include_graph=true 返回完整 EvidenceGraph。
- 26 个测试全部通过。
- 新增 `docs/DECISIONS.md` D011：记录阶段 3 最小 Pydantic 模型决策。

**Git 提交记录（阶段 2）：**
- `ca941c3` feat: add multi-source paper search
- `7077ad5` feat: add backend scaffold and arxiv search

## 当前还没有做
- 没有接入 Semantic Scholar。
- 没有接入 Crossref。
- 没有持久化保存研究任务。
- 没有接入 LLM 做 claim 抽取（阶段 4 目标）。
- 没有实现 EvidenceGraph 的 claim 节点（数据模型已预留）。
- 没有引入 LangGraph、多 Agent、数据库、RAG 或前端。
- 没有 push 到远端（本地领先 origin 2 个 commit）。
- 没有提交阶段 3 代码，等待用户确认。

## 下一步建议

阶段 3 核心代码已完成。当前版本的 EvidenceGraph 包含 paper + evidence 两类节点，每条 evidence 可通过 source_paper_id 追溯原始论文。

建议确认后提交 git，然后进入阶段 4：基础 Evidence Report——基于 EvidenceGraph 生成首个带来源的 Markdown 报告，每个小结都绑定 evidence 节点。

## 最近验证记录

阶段 1 到阶段 2 已通过以下验证：

```bash
cd backend
uv run pytest
```

结果：18 个测试全部通过。

```bash
cd backend
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

结果：本地服务能启动。

```bash
curl -i http://127.0.0.1:8000/health
```

结果：返回 `{"status":"ok","service":"scholar-agent-backend"}`。

```bash
curl -i -X POST http://127.0.0.1:8000/research/tasks \
  -H 'Content-Type: application/json' \
  -d '{"topic":"LLM Agent for Software Engineering"}'
```

结果：返回 `status=created` 和 `task_` 开头的任务 ID。

```bash
curl -i 'http://127.0.0.1:8000/papers/search?query=electron&max_results=1'
```

结果：接口能调用论文搜索链路。当前策略是 OpenAlex 优先，OpenAlex 失败时尝试 arXiv 兜底。

真实 OpenAlex 端到端验证：

```bash
curl -sS -i 'http://127.0.0.1:8000/papers/search?query=LLM%20Agent%20for%20Software%20Engineering&max_results=3'
```

结果：返回 `HTTP/1.1 200 OK`，并返回 3 篇 `source="openalex"` 的真实论文：

- `LLM-Based Multi-Agent Systems for Software Engineering: Literature Review, Vision, and the Road Ahead`
- `Demystifying LLM-Based Software Engineering Agents`
- `From LLMs to LLM-based Agents for Software Engineering: A Survey of Current, Challenges and Future`

阶段 2.1 额外验证：

- arXiv XML 样例可以解析为 `Paper` 模型。
- arXiv 搜索工具会生成正确的请求参数。
- `max_results` 会被限制在 1 到 10 之间。
- arXiv 请求已设置 `User-Agent`，并禁用读取本机代理环境变量，避免异常代理配置影响请求。
- 真实 arXiv 请求曾返回 `429` 限流，因此当前真实网络验证不作为本地测试的唯一依据。
- 阶段 2.2 额外验证：`GET /papers/search` 接口已接入 arXiv 工具，并能把工具层错误转换成 503。
- 阶段 2.3 额外验证：OpenAlex JSON 样例可以解析为 `Paper` 模型，多源搜索会优先使用 OpenAlex，并在 OpenAlex 失败时回退到 arXiv。
- 阶段 2 真实验证：OpenAlex API key 已生效，论文搜索 API 可以返回真实论文 JSON。

当前后端环境管理方式：

```bash
cd backend
uv sync --extra dev
uv run pytest
uv run uvicorn app.main:app --host 127.0.0.1 --port 8000
```

后续新增依赖时：

```bash
cd backend
uv add package_name
uv add --optional dev dev_package_name
uv sync --extra dev
```

OpenAlex API key 配置：

```bash
cd backend
cp .env.example .env
```

然后编辑 `backend/.env`：

```bash
OPENALEX_API_KEY=你的 OpenAlex API key
OPENALEX_MAILTO=你的邮箱
```

## 当前风险和提醒

- 项目目标较大，后续必须坚持小步推进，避免一次性引入太多技术。
- 阶段 3 只做数据模型和内存图谱，不要引入数据库或持久化。
- 多 Agent、Evidence RAG、LangGraph、Qdrant、PostgreSQL 都还不是当前阶段的内容。
- 当前研究任务只返回临时任务 ID，还没有持久化任务状态。
- `backend/.env` 用于保存本地 API key，不提交 Git。
- `backend/.venv/` 是 uv 创建的本地虚拟环境，不提交 Git。
- `backend/uv.lock` 需要提交 Git，用于保证其他机器能复现相同依赖版本。
- 新增依赖优先用 `uv add`，不要手动 `pip install`。
- 每次完成一小步后，都应该更新本文件，记录当前阶段、已完成内容、验证方式和下一步。

## 接手检查清单

新的 AI 或开发者接手时，请先确认：

- 当前 git 状态是否干净。
- `AGENTS.md` 中的协作约定是否已阅读。
- `docs/PROJECT_PLAN.md` 中的阶段规划是否已阅读。
- 本文件中的当前阶段是否和代码状态一致。
- 本次准备做的任务是否只属于当前阶段。

## 更新规则

每完成一个小阶段，请更新：

- `当前快照`
- `已完成`
- `当前还没有做`
- `下一步建议`
- 必要时补充 `当前风险和提醒`

如果做出新的关键技术决策，请同步更新 `docs/DECISIONS.md`。
