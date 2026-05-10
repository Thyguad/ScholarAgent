from pydantic import BaseModel, Field


class Paper(BaseModel):
    """论文搜索结果的统一结构。

    后续不管论文来自 arXiv、Semantic Scholar 还是其他来源，都尽量转换成这个模型，
    这样上层 Agent 不需要关心底层 API 的原始返回格式。
    """

    source: str = Field(description="论文来源，例如 arxiv。")
    source_id: str = Field(description="来源系统里的论文 ID，例如 arXiv ID。")
    title: str = Field(description="论文标题。")
    authors: list[str] = Field(description="作者列表。")
    summary: str = Field(description="论文摘要。")
    published_at: str = Field(description="论文发布时间，先保留来源返回的字符串。")
    source_url: str = Field(description="论文详情页 URL。")
    pdf_url: str | None = Field(default=None, description="论文 PDF URL。")
