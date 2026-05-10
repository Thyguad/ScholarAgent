from fastapi.testclient import TestClient

import app.main as main_module
from app.main import app
from app.models.paper import Paper
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
