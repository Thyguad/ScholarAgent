from uuid import uuid4

from fastapi import FastAPI

from app.models.research_task import ResearchTaskCreate, ResearchTaskResponse


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
