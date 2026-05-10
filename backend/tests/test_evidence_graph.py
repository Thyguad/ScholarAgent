from app.models.evidence_graph import EvidenceGraph
from app.models.paper import Paper
from app.services.graph_builder import build_evidence_graph


def _make_paper(source_id: str = "W123") -> Paper:
    return Paper(
        source="openalex",
        source_id=source_id,
        title="A Survey of LLM Agents",
        authors=["Alice Zhang", "Bob Lee"],
        summary="This paper surveys large language model agents.",
        published_at="2024-01-01",
        source_url="https://openalex.org/W123",
        pdf_url=None,
    )


class TestBuildEvidenceGraph:
    """验证 graph_builder 能把论文列表正确转换为证据图谱。"""

    def test_each_paper_generates_four_evidence_nodes(self) -> None:
        """每篇论文应生成 title、summary、authors、published_at 4 条 evidence。"""
        papers = [_make_paper("W1"), _make_paper("W2")]
        graph = build_evidence_graph(papers)

        assert len(graph.evidence_nodes) == 8  # 2 篇论文 × 4 条

    def test_every_evidence_is_traceable_to_its_source_paper(self) -> None:
        """每条 evidence 的 source_paper_id 必须能追溯到原论文。
        这是证据图谱的核心保证——后续任何结论都能找到出处。
        """
        papers = [_make_paper("W123"), _make_paper("W456")]
        graph = build_evidence_graph(papers)

        paper_ids = {p.source_id for p in papers}
        for ev in graph.evidence_nodes:
            assert ev.source_paper_id in paper_ids, (
                f"证据 {ev.id} 绑定的论文 {ev.source_paper_id} 不在论文列表中"
            )

    def test_evidence_content_matches_source_paper(self) -> None:
        """证据内容必须和原论文对应字段一致。"""
        paper = _make_paper("W123")
        graph = build_evidence_graph([paper])

        title_ev = next(ev for ev in graph.evidence_nodes if ev.field == "title")
        assert title_ev.content == paper.title

        authors_ev = next(ev for ev in graph.evidence_nodes if ev.field == "authors")
        assert "Alice Zhang" in authors_ev.content
        assert "Bob Lee" in authors_ev.content

    def test_evidence_nodes_cover_all_fields(self) -> None:
        """确保证据节点覆盖了预期的 4 个字段。"""
        graph = build_evidence_graph([_make_paper("W123")])

        fields = {ev.field for ev in graph.evidence_nodes}
        assert fields == {"title", "summary", "authors", "published_at"}

    def test_empty_paper_list_returns_empty_evidence(self) -> None:
        """没有论文时，证据列表也应该为空。"""
        graph = build_evidence_graph([])

        assert graph.papers == []
        assert graph.evidence_nodes == []

    def test_graph_preserves_original_papers(self) -> None:
        """图谱中的 papers 字段应和输入的论文列表一致。"""
        papers = [_make_paper("W1"), _make_paper("W2")]
        graph = build_evidence_graph(papers)

        assert graph.papers == papers

    def test_evidence_id_is_stable_and_predictable(self) -> None:
        """证据 ID 格式为 ev_{source_id}_{field}，可预测且不会重复。"""
        graph = build_evidence_graph([_make_paper("W123")])

        ids = {ev.id for ev in graph.evidence_nodes}
        expected = {
            "ev_W123_title",
            "ev_W123_summary",
            "ev_W123_authors",
            "ev_W123_published_at",
        }
        assert ids == expected
