from pydantic import BaseModel, Field


class ResearchTaskCreate(BaseModel):
    """创建研究任务时，前端或用户需要提交的数据。"""

    topic: str = Field(
        min_length=2,
        max_length=200,
        description="用户想调研的科研主题，例如 LLM Agent for Software Engineering。",
    )


class ResearchTaskResponse(BaseModel):
    """创建研究任务后，后端返回给调用方的结构化结果。"""

    task_id: str = Field(description="任务 ID，后续会用于查询任务状态。")
    topic: str = Field(description="用户提交的研究主题。")
    status: str = Field(description="任务当前状态。")
    message: str = Field(description="给用户看的简短说明。")
