from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query

from app.models.paper import Paper
from app.models.research_task import ResearchTaskCreate, ResearchTaskResponse
from app.tools.paper_search import PaperSearchError, search_papers_across_sources


app = FastAPI(
    title="ScholarAgent API",
    description="面向科研新手的科研复现与创新机会评估 Agent 后端。",
    version="0.1.0",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    """返回服务健康状态，方便我们确认后端是否正常启动。"""
    return {"status": "ok", "service": "scholar-agent-backend"}


@app.post("/research/tasks", response_model=ResearchTaskResponse)
def create_research_task(payload: ResearchTaskCreate) -> ResearchTaskResponse:
    """创建最小研究任务。

    当前阶段还不真正执行论文检索，只先把用户输入的研究主题接住。
    后续阶段会在这里挂接任务队列、论文搜索和 Agent 工作流。
    """
    # 先生成一个临时任务 ID，后续接入数据库后再持久化保存任务状态。
    return ResearchTaskResponse(
        task_id=f"task_{uuid4().hex}",
        topic=payload.topic,
        status="created",
        message="研究任务已创建，后续阶段会接入论文搜索和证据图谱。",
    )


@app.get("/papers/search", response_model=list[Paper])
def search_papers(
    query: str = Query(min_length=2, max_length=200, description="论文搜索关键词。"),
    max_results: int = Query(default=5, ge=1, le=10, description="最多返回论文数量。"),
) -> list[Paper]:
    """搜索真实论文。

    API 层只负责参数校验和错误转换；真正的数据源调用放在工具层。
    当前优先使用 OpenAlex，arXiv 作为备用来源。
    """
    try:
        return search_papers_across_sources(query=query, max_results=max_results)
    except PaperSearchError as exc:
        # 外部 API 失败时返回 503，表示服务暂时不可用，调用方稍后可以重试。
        raise HTTPException(status_code=503, detail=str(exc)) from exc
