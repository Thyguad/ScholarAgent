from app.models.evidence_graph import Claim, Evidence, EvidenceGraph
from app.models.paper import Paper
from app.services.report_builder import build_evidence_report


def _make_paper(source_id: str = "W1") -> Paper:
    return Paper(
        source="openalex",
        source_id=source_id,
        title="A Survey of LLM Agents",
        authors=["Alice Zhang", "Bob Lee"],
        summary="This paper surveys large language model agents.",
        published_at="2024-01-01",
        source_url="https://openalex.org/W1",
        pdf_url=None,
    )


def _make_evidence(paper_id: str = "W1") -> list[Evidence]:
    return [
        Evidence(id=f"ev_{paper_id}_title", source_paper_id=paper_id, field="title", content="A Survey of LLM Agents"),
        Evidence(id=f"ev_{paper_id}_summary", source_paper_id=paper_id, field="summary", content="This paper surveys large language model agents."),
        Evidence(id=f"ev_{paper_id}_authors", source_paper_id=paper_id, field="authors", content="Alice Zhang, Bob Lee"),
    ]


def _make_claim(paper_id: str = "W1", index: int = 1, text: str = "A test claim.", confidence: float = 0.9) -> Claim:
    return Claim(
        id=f"claim_{paper_id}_{index}",
        source_paper_id=paper_id,
        text=text,
        evidence_ids=[f"ev_{paper_id}_title", f"ev_{paper_id}_summary"],
        confidence=confidence,
    )


class TestBuildEvidenceReport:

    def test_empty_graph_returns_minimal_report(self) -> None:
        """空图谱应返回包含提示的基本报告。"""
        graph = EvidenceGraph(papers=[], evidence_nodes=[], claim_nodes=[])
        report = build_evidence_report(graph, query="test query")

        assert "研究报告" in report
        assert "test query" in report
        assert "未搜索到论文" in report

    def test_single_paper_without_claims_includes_basic_info(self) -> None:
        """单篇论文无 claim 时，报告应包含论文基本信息和证据。"""
        paper = _make_paper("W1")
        graph = EvidenceGraph(
            papers=[paper],
            evidence_nodes=_make_evidence("W1"),
            claim_nodes=[],
        )
        report = build_evidence_report(graph, query="test")

        assert paper.title in report
        assert "Alice Zhang" in report
        assert "2024-01-01" in report
        assert "openalex" in report
        assert "ev_W1_title" in report  # 证据节点出现在报告中

    def test_single_paper_with_claims_shows_claim_id(self) -> None:
        """报告必须包含每条 claim 的 claim_id。"""
        paper = _make_paper("W1")
        graph = EvidenceGraph(
            papers=[paper],
            evidence_nodes=_make_evidence("W1"),
            claim_nodes=[_make_claim("W1", 1, "First claim.")],
        )
        report = build_evidence_report(graph, query="test")

        assert "claim_W1_1" in report

    def test_claim_includes_source_paper_id(self) -> None:
        """每条 claim 必须显示其 source_paper_id，方便溯源。"""
        paper = _make_paper("W999")
        graph = EvidenceGraph(
            papers=[paper],
            evidence_nodes=_make_evidence("W999"),
            claim_nodes=[_make_claim("W999", 1, "Traceable claim.")],
        )
        report = build_evidence_report(graph, query="test")

        assert "W999" in report

    def test_claim_includes_evidence_ids(self) -> None:
        """每条 claim 必须显示绑定的 evidence_ids。"""
        paper = _make_paper("W1")
        graph = EvidenceGraph(
            papers=[paper],
            evidence_nodes=_make_evidence("W1"),
            claim_nodes=[_make_claim("W1", 1, "Evidence-linked claim.")],
        )
        report = build_evidence_report(graph, query="test")

        assert "ev_W1_title" in report
        assert "ev_W1_summary" in report

    def test_claim_shows_confidence(self) -> None:
        """report 应显示 claim 的置信度。"""
        paper = _make_paper("W1")
        graph = EvidenceGraph(
            papers=[paper],
            evidence_nodes=_make_evidence("W1"),
            claim_nodes=[_make_claim("W1", 1, "Confident claim.", confidence=0.95)],
        )
        report = build_evidence_report(graph, query="test")

        assert "95%" in report

    def test_multiple_papers_generate_separate_sections(self) -> None:
        """多篇论文应各自独占一节，标题编号递增。"""
        p1 = _make_paper("W1")
        p1.title = "Paper One"
        p2 = _make_paper("W2")
        p2.title = "Paper Two"

        graph = EvidenceGraph(
            papers=[p1, p2],
            evidence_nodes=_make_evidence("W1") + _make_evidence("W2"),
            claim_nodes=[
                _make_claim("W1", 1, "Claim from W1."),
                _make_claim("W2", 1, "Claim from W2."),
            ],
        )
        report = build_evidence_report(graph, query="test")

        assert "## 1. Paper One" in report
        assert "## 2. Paper Two" in report
        assert "Claim from W1" in report
        assert "Claim from W2" in report

    def test_no_claims_section_when_empty(self) -> None:
        """没有 claim 的论文不应出现'关键声明'小节。"""
        paper = _make_paper("W1")
        graph = EvidenceGraph(
            papers=[paper],
            evidence_nodes=_make_evidence("W1"),
            claim_nodes=[],
        )
        report = build_evidence_report(graph, query="test")

        assert "关键声明" not in report

    def test_summary_stats_included(self) -> None:
        """报告头部应显示论文数、证据节点数、claim 数。"""
        graph = EvidenceGraph(
            papers=[_make_paper("W1"), _make_paper("W2")],
            evidence_nodes=_make_evidence("W1") + _make_evidence("W2"),
            claim_nodes=[_make_claim("W1", 1)],
        )
        report = build_evidence_report(graph, query="test")

        assert "论文数：2" in report
        assert "证据节点：6" in report
        assert "Claim：1" in report
