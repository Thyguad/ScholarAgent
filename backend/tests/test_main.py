from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app
from app.models.evidence_graph import EvidenceGraph
from app.models.paper import Paper
from app.services.graph_builder import build_evidence_graph
from app.tools.paper_search import PaperSearchError


client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "scholar-agent-backend",
    }


def test_create_research_task() -> None:
    response = client.post(
        "/research/tasks",
        json={"topic": "LLM Agent for Software Engineering"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"].startswith("task_")
    assert data["topic"] == "LLM Agent for Software Engineering"
    assert data["status"] == "created"


def test_create_research_task_requires_valid_topic() -> None:
    # Pydantic 会在进入业务逻辑前校验输入，避免空主题进入后续 Agent 流程。
    response = client.post("/research/tasks", json={"topic": ""})

    assert response.status_code == 422


def test_search_papers_returns_paper_results(monkeypatch) -> None:
    def fake_search_papers_across_sources(query: str, max_results: int) -> list[Paper]:
        assert query == "LLM Agent"
        assert max_results == 2
        return [
            Paper(
                source="openalex",
                source_id="W123",
                title="A Survey of LLM Agents",
                authors=["Alice Zhang"],
                summary="This paper surveys large language model agents.",
                published_at="2024-01-01T00:00:00Z",
                source_url="https://openalex.org/W123",
                pdf_url=None,
            )
        ]

    monkeypatch.setattr(
        main_module,
        "search_papers_across_sources",
        fake_search_papers_across_sources,
    )

    response = client.get("/papers/search", params={"query": "LLM Agent", "max_results": 2})

    assert response.status_code == 200
    data = response.json()
    assert data[0]["source"] == "openalex"
    assert data[0]["title"] == "A Survey of LLM Agents"


def test_search_papers_with_include_graph_returns_evidence_graph(monkeypatch) -> None:
    """传入 include_graph=true 时应返回 EvidenceGraph 结构，而非纯论文列表。"""

    def fake_search_papers_across_sources(query: str, max_results: int) -> list[Paper]:
        return [
            Paper(
                source="openalex",
                source_id="W123",
                title="Test Paper",
                authors=["Alice"],
                summary="A summary.",
                published_at="2024-01-01",
                source_url="https://example.org/W123",
                pdf_url=None,
            )
        ]

    monkeypatch.setattr(
        main_module,
        "search_papers_across_sources",
        fake_search_papers_across_sources,
    )

    response = client.get(
        "/papers/search",
        params={"query": "test", "max_results": 1, "include_graph": True},
    )

    assert response.status_code == 200
    data = response.json()
    # EvidenceGraph 应有 papers 和 evidence_nodes 两个字段
    assert "papers" in data
    assert "evidence_nodes" in data
    assert len(data["papers"]) == 1
    # 每篇论文 4 条 evidence
    assert len(data["evidence_nodes"]) == 4
    # 每条 evidence 应该有 id 和 source_paper_id
    for ev in data["evidence_nodes"]:
        assert ev["source_paper_id"] == "W123"


def test_search_papers_converts_search_error_to_503(monkeypatch) -> None:
    def fake_search_papers_across_sources(query: str, max_results: int) -> list[Paper]:
        raise PaperSearchError("论文搜索暂时不可用")

    monkeypatch.setattr(
        main_module,
        "search_papers_across_sources",
        fake_search_papers_across_sources,
    )

    response = client.get("/papers/search", params={"query": "LLM Agent"})

    assert response.status_code == 503
    assert "论文搜索暂时不可用" in response.json()["detail"]
