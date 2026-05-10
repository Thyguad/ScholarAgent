from pydantic import BaseModel, Field

from app.models.paper import Paper


class Evidence(BaseModel):
    """证据节点：图谱中最小的可追溯信息单元。

    每条证据都绑定到一篇特定论文，后续任何基于这份图谱生成的
    报告、评分或建议，都可以通过 evidence 追溯到原始来源。
    """

    id: str = Field(description="证据唯一标识，如 ev_W123_title。")
    source_paper_id: str = Field(description="来源论文的 source_id，用于溯源。")
    field: str = Field(description="证据对应的论文字段，如 title / summary / authors / published_at。")
    content: str = Field(description="证据内容，即对应字段的原文片段。")


class EvidenceGraph(BaseModel):
    """简版证据图谱。

    当前阶段只包含论文节点和证据节点，不包含 claim（声明）节点。
    claim 节点预留在后续阶段接入，用于 LLM 抽取论文中的具体结论。
    """

    papers: list[Paper] = Field(description="来自论文搜索的原始论文列表。")
    evidence_nodes: list[Evidence] = Field(description="从论文元数据中提取的证据节点列表。")
