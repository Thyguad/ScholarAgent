from app.models.paper import Paper
from app.tools import paper_search
from app.tools.arxiv_search import ArxivSearchError
from app.tools.openalex_search import OpenAlexSearchError
from app.tools.paper_search import PaperSearchError, search_papers_across_sources


def _paper(source: str) -> Paper:
    return Paper(
        source=source,
        source_id="paper-1",
        title="A Survey of LLM Agents",
        authors=["Alice Zhang"],
        summary="summary",
        published_at="2024-01-01",
        source_url="https://example.org/paper",
        pdf_url=None,
    )


def test_search_papers_across_sources_prefers_openalex(monkeypatch) -> None:
    def fake_openalex(query: str, max_results: int) -> list[Paper]:
        return [_paper("openalex")]

    def fake_arxiv(query: str, max_results: int) -> list[Paper]:
        raise AssertionError("OpenAlex 有结果时不应该调用 arXiv")

    monkeypatch.setattr(paper_search, "search_openalex_papers", fake_openalex)
    monkeypatch.setattr(paper_search, "search_arxiv_papers", fake_arxiv)

    papers = search_papers_across_sources("LLM Agent")

    assert papers[0].source == "openalex"


def test_search_papers_across_sources_falls_back_to_arxiv(monkeypatch) -> None:
    def fake_openalex(query: str, max_results: int) -> list[Paper]:
        raise OpenAlexSearchError("OpenAlex failed")

    def fake_arxiv(query: str, max_results: int) -> list[Paper]:
        return [_paper("arxiv")]

    monkeypatch.setattr(paper_search, "search_openalex_papers", fake_openalex)
    monkeypatch.setattr(paper_search, "search_arxiv_papers", fake_arxiv)

    papers = search_papers_across_sources("LLM Agent")

    assert papers[0].source == "arxiv"


def test_search_papers_across_sources_raises_when_all_sources_fail(monkeypatch) -> None:
    monkeypatch.setattr(
        paper_search,
        "search_openalex_papers",
        lambda query, max_results: (_ for _ in ()).throw(OpenAlexSearchError("OpenAlex failed")),
    )
    monkeypatch.setattr(
        paper_search,
        "search_arxiv_papers",
        lambda query, max_results: (_ for _ in ()).throw(ArxivSearchError("arXiv failed")),
    )

    try:
        search_papers_across_sources("LLM Agent")
    except PaperSearchError as exc:
        assert "OpenAlex failed" in str(exc)
        assert "arXiv failed" in str(exc)
    else:
        raise AssertionError("Expected PaperSearchError")
