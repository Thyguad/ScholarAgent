from app.models.evidence_graph import Evidence, EvidenceGraph
from app.models.paper import Paper


def build_evidence_graph(papers: list[Paper]) -> EvidenceGraph:
    """把论文列表转换为简版证据图谱。

    当前阶段不抽取论文正文中的 claim（声明），只把每篇论文的基本元数据
    拆成可追溯的 evidence 节点。

    每条 evidence 都能通过 source_paper_id 追溯到原论文，
    后续阶段生成报告或评分时，就可以绑定具体证据作为来源。
    """
    evidence_nodes: list[Evidence] = []

    for paper in papers:
        # 论文的唯一溯源标识，后续不管 evidence 流转到哪里，
        # 都能通过这个字段找到原始论文。
        pid = paper.source_id

        # 为论文的关键字段各生成一条 evidence 节点
        evidence_nodes.extend([
            Evidence(
                id=f"ev_{pid}_title",
                source_paper_id=pid,
                field="title",
                content=paper.title,
            ),
            Evidence(
                id=f"ev_{pid}_summary",
                source_paper_id=pid,
                field="summary",
                content=paper.summary,
            ),
            Evidence(
                id=f"ev_{pid}_authors",
                source_paper_id=pid,
                field="authors",
                content=", ".join(paper.authors),
            ),
            Evidence(
                id=f"ev_{pid}_published_at",
                source_paper_id=pid,
                field="published_at",
                content=paper.published_at,
            ),
        ])

    return EvidenceGraph(papers=papers, evidence_nodes=evidence_nodes)
