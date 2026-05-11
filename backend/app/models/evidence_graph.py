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


class Claim(BaseModel):
    """论文中的关键声明。

    Claim 不是模型自由发挥的总结，而是从论文标题和摘要中抽取出的
    可验证结论。每条 claim 都必须绑定 evidence_ids，方便后续追溯来源。
    """

    id: str = Field(description="Claim 唯一标识，如 claim_W123_1。")
    source_paper_id: str = Field(description="来源论文的 source_id。")
    text: str = Field(description="Claim 文本。")
    evidence_ids: list[str] = Field(description="支持该 claim 的 evidence id 列表。")
    confidence: float = Field(ge=0, le=1, description="LLM 对该 claim 抽取结果的置信度。")


class EvidenceGraph(BaseModel):
    """简版证据图谱。

    包含论文节点、证据节点和从论文中抽取的 claim 节点。
    claim_nodes 在 LLM 接入前为空列表，不影响旧逻辑。
    """

    papers: list[Paper] = Field(description="来自论文搜索的原始论文列表。")
    evidence_nodes: list[Evidence] = Field(description="从论文元数据中提取的证据节点列表。")
    claim_nodes: list[Claim] = Field(
        default_factory=list,
        description="从论文标题和摘要中抽取的 claim 节点列表。",
    )
