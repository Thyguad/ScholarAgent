from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query

from app.models.evidence_graph import EvidenceGraph
from app.models.paper import Paper
from app.models.research_task import ResearchTaskCreate, ResearchTaskResponse
from app.services.claim_extractor import ClaimExtractionError, enrich_graph_with_claims
from app.services.graph_builder import build_evidence_graph
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


@app.get("/papers/search")
def search_papers(
    query: str = Query(min_length=2, max_length=200, description="论文搜索关键词。"),
    max_results: int = Query(default=5, ge=1, le=10, description="最多返回论文数量。"),
    include_graph: bool = Query(default=False, description="是否返回证据图谱。"),
    include_claims: bool = Query(default=False, description="是否抽取并返回 claim 节点。"),
) -> list[Paper] | EvidenceGraph:
    """搜索真实论文，可选择附带证据图谱和 LLM 抽取的 claim。

    默认只返回论文列表（向后兼容）。
    传入 include_graph=true 返回包含 evidence_nodes 的 EvidenceGraph。
    传入 include_claims=true 时自动返回 EvidenceGraph，并追加 claim_nodes。
    PaperSearchError 和 ClaimExtractionError 都会转换为 503。
    """
    try:
        papers = search_papers_across_sources(query=query, max_results=max_results)
    except PaperSearchError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # include_claims 或 include_graph 任一为 true 时都返回 EvidenceGraph
    if include_graph or include_claims:
        graph = build_evidence_graph(papers)

        if include_claims:
            try:
                graph = enrich_graph_with_claims(graph)
            except ClaimExtractionError as exc:
                raise HTTPException(status_code=503, detail=str(exc)) from exc

        return graph

    return papers
