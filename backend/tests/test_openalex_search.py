import httpx
import pytest

from app.core.config import Settings
from app.tools import openalex_search
from app.tools.openalex_search import (
    OpenAlexSearchError,
    parse_openalex_works,
    search_openalex_papers,
)


SAMPLE_OPENALEX_RESPONSE = {
    "results": [
        {
            "id": "https://openalex.org/W123",
            "display_name": "A Survey of LLM Agents",
            "authorships": [
                {"author": {"display_name": "Alice Zhang"}},
                {"author": {"display_name": "Bob Lee"}},
            ],
            "abstract_inverted_index": {
                "This": [0],
                "paper": [1],
                "surveys": [2],
                "agents.": [3],
            },
            "publication_date": "2024-01-01",
            "publication_year": 2024,
            "primary_location": {
                "landing_page_url": "https://doi.org/10.1234/example",
                "pdf_url": "https://example.org/paper.pdf",
            },
            "open_access": {"oa_url": "https://example.org/oa.pdf"},
            "doi": "https://doi.org/10.1234/example",
        }
    ]
}


def test_parse_openalex_works_returns_structured_papers() -> None:
    papers = parse_openalex_works(SAMPLE_OPENALEX_RESPONSE)

    assert len(papers) == 1
    paper = papers[0]
    assert paper.source == "openalex"
    assert paper.source_id == "W123"
    assert paper.title == "A Survey of LLM Agents"
    assert paper.authors == ["Alice Zhang", "Bob Lee"]
    assert paper.summary == "This paper surveys agents."
    assert paper.published_at == "2024-01-01"
    assert paper.source_url == "https://doi.org/10.1234/example"
    assert paper.pdf_url == "https://example.org/paper.pdf"


def test_search_openalex_papers_calls_openalex_api(monkeypatch) -> None:
    captured_request: dict[str, object] = {}

    class FakeResponse:
        status_code = 200

        def json(self) -> dict:
            return SAMPLE_OPENALEX_RESPONSE

    def fake_get(
        url: str,
        *,
        params: dict[str, object],
        timeout: int,
        headers: dict[str, str],
        trust_env: bool,
    ) -> FakeResponse:
        captured_request["url"] = url
        captured_request["params"] = params
        captured_request["timeout"] = timeout
        captured_request["headers"] = headers
        captured_request["trust_env"] = trust_env
        return FakeResponse()

    monkeypatch.setattr(
        openalex_search,
        "get_settings",
        lambda: Settings(openalex_api_key="test-key", openalex_mailto="user@example.com"),
    )
    monkeypatch.setattr(httpx, "get", fake_get)

    papers = search_openalex_papers("  LLM   Agent  ", max_results=20)

    assert len(papers) == 1
    assert captured_request["url"] == "https://api.openalex.org/works"
    params = captured_request["params"]
    assert isinstance(params, dict)
    assert params["search"] == "LLM Agent"
    assert params["per-page"] == 10
    assert params["api_key"] == "test-key"
    assert params["mailto"] == "user@example.com"
    assert captured_request["timeout"] == 20
    assert captured_request["headers"] == {
        "User-Agent": "ScholarAgent/0.1 (https://github.com/Thyguad/ScholarAgent)"
    }
    assert captured_request["trust_env"] is False


def test_search_openalex_papers_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr(openalex_search, "get_settings", lambda: Settings())

    with pytest.raises(OpenAlexSearchError):
        search_openalex_papers("LLM Agent")


def test_search_openalex_papers_converts_http_error(monkeypatch) -> None:
    class FakeResponse:
        status_code = 401

        def json(self) -> dict:
            return {}

    monkeypatch.setattr(
        openalex_search,
        "get_settings",
        lambda: Settings(openalex_api_key="bad-key"),
    )
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse())

    with pytest.raises(OpenAlexSearchError):
        search_openalex_papers("LLM Agent")
