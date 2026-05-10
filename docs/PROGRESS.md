# ScholarAgent Progress

本文件用于记录 ScholarAgent 的当前进度和下一步接手信息。

如果后续由新的 AI 或开发者接手，请先读：

1. `AGENTS.md`：了解协作方式和代码约束。
2. `docs/PROGRESS.md`：确认当前做到哪一步。
3. `docs/PROJECT_PLAN.md`：了解项目总方案和阶段规划。
4. `docs/DECISIONS.md`：理解关键技术决策的原因。

## 当前快照

- 最后更新：2026-05-10
- 当前分支：`main`
- 当前阶段：阶段 2.1，arXiv 搜索工具已完成
- 当前状态：已有最小后端入口、研究任务提交接口、arXiv 论文模型和 arXiv 搜索工具，并已切换为 uv 管理后端 Python 环境
- 项目定位：面向科研新手的科研复现与创新机会评估 Agent
- 详细方案来源：`docs/PROJECT_PLAN.md`

## 已完成

- 阅读并重构了项目 README。
- 明确了 ScholarAgent 的最终定位和核心创新点。
- 确定项目主线为论文、代码、证据图谱、复现评分、验证和创新机会挖掘。
- 新增 `AGENTS.md`，约束 Codex、Claude Code 等 coding agent 的协作方式。
- 新增 `CLAUDE.md`，让 Claude Code 自动继承项目级 agent 约定。
- 新增 `docs/PROJECT_PLAN.md`，沉淀完整项目方案、技术路线、阶段规划和简历表达。
- 新增 `docs/PROGRESS.md`，记录当前阶段和下一步接手信息。
- 新增 `docs/DECISIONS.md`，记录关键决策原因。
- 创建 `backend/` 最小后端工程。
- 实现 FastAPI 应用入口 `backend/app/main.py`。
- 实现 `/health` 健康检查接口。
- 实现 `POST /research/tasks` 最小研究任务提交接口。
- 使用 Pydantic 定义研究任务请求和响应模型。
- 添加接口测试 `backend/tests/test_main.py`。
- 使用 uv 管理后端 Python 环境。
- 生成 `backend/uv.lock`，用于锁定依赖版本。
- 后端依赖以 `backend/pyproject.toml` 为准，日常使用 `uv sync --extra dev` 同步环境。
- 将 `httpx` 调整为后端运行时依赖，用于调用 arXiv API。
- 新增 `backend/app/models/paper.py`，定义统一论文结果模型。
- 新增 `backend/app/tools/arxiv_search.py`，封装 arXiv API 请求和 XML 解析逻辑。
- 新增 `backend/tests/test_arxiv_search.py`，验证 arXiv XML 能转换为结构化论文模型。

## 当前还没有做

- 没有把 arXiv 搜索工具挂到 FastAPI 接口。
- 没有接入 Semantic Scholar。
- 没有持久化保存研究任务。
- 没有接入 Evidence Graph。
- 没有引入 LangGraph、多 Agent、数据库、RAG 或前端。
- 没有提交本轮阶段 1 和阶段 2.1 代码，等待用户确认。

## 下一步建议

下一步建议继续 `docs/PROJECT_PLAN.md` 中的阶段 2：论文搜索 MVP。

下一小步建议做阶段 2.2：把 arXiv 搜索工具挂到 FastAPI 接口。

1. 向用户解释 API 路由如何复用工具函数。
2. 新增一个论文搜索接口，例如 `GET /papers/search?query=...`。
3. 在接口层限制 `max_results`，默认返回 5 篇，最多返回 10 篇。
4. 将 `search_arxiv_papers` 的结果作为结构化 JSON 返回。
5. 为关键逻辑添加中文注释。
6. 用测试验证接口能返回论文列表。
7. 总结本阶段学到的工具层和 API 层分工。
8. 用户同意后再提交 git。

## 最近验证记录

阶段 1 和阶段 2.1 已通过以下验证：

```bash
cd backend
uv run pytest
```

结果：5 个测试全部通过。

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

阶段 2.1 额外验证：

- arXiv XML 样例可以解析为 `Paper` 模型。
- arXiv 搜索工具会生成正确的请求参数。
- `max_results` 会被限制在 1 到 10 之间。
- arXiv 请求已设置 `User-Agent`，并禁用读取本机代理环境变量，避免异常代理配置影响请求。
- 真实 arXiv 请求曾返回 `429` 限流，因此当前真实网络验证不作为本地测试的唯一依据。

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

## 当前风险和提醒

- 项目目标较大，后续必须坚持小步推进，避免一次性引入太多技术。
- 多 Agent、Evidence RAG、LangGraph、Qdrant、PostgreSQL 都还不是阶段 2 的内容。
- 阶段 2 的目标不是生成完整调研报告，而是先把论文搜索结果变成结构化数据。
- 当前研究任务只返回临时任务 ID，还没有持久化任务状态。
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
