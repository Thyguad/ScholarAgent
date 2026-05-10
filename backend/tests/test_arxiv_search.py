import httpx
import pytest

from app.tools import arxiv_search
from app.tools.arxiv_search import (
    ArxivSearchError,
    parse_arxiv_feed,
    search_arxiv_papers,
)


SAMPLE_ARXIV_FEED = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2401.00001v1</id>
    <updated>2024-01-02T00:00:00Z</updated>
    <published>2024-01-01T00:00:00Z</published>
    <title>
      A Survey of LLM Agents
    </title>
    <summary>
      This paper surveys large language model agents.
    </summary>
    <author>
      <name>Alice Zhang</name>
    </author>
    <author>
      <name>Bob Lee</name>
    </author>
    <link href="http://arxiv.org/abs/2401.00001v1" rel="alternate" type="text/html"/>
    <link title="pdf" href="http://arxiv.org/pdf/2401.00001v1" rel="related" type="application/pdf"/>
  </entry>
</feed>
"""


def test_parse_arxiv_feed_returns_structured_papers() -> None:
    papers = parse_arxiv_feed(SAMPLE_ARXIV_FEED)

    assert len(papers) == 1
    paper = papers[0]
    assert paper.source == "arxiv"
    assert paper.source_id == "2401.00001v1"
    assert paper.title == "A Survey of LLM Agents"
    assert paper.authors == ["Alice Zhang", "Bob Lee"]
    assert paper.summary == "This paper surveys large language model agents."
    assert paper.published_at == "2024-01-01T00:00:00Z"
    assert paper.source_url == "http://arxiv.org/abs/2401.00001v1"
    assert paper.pdf_url == "http://arxiv.org/pdf/2401.00001v1"


def test_search_arxiv_papers_calls_arxiv_api(monkeypatch) -> None:
    captured_request: dict[str, object] = {}

    class FakeResponse:
        status_code = 200
        text = SAMPLE_ARXIV_FEED

        def raise_for_status(self) -> None:
            return None

    def fake_get(
        url: str,
        *,
        params: dict[str, object],
        timeout: int,
        headers: dict[str, str],
        follow_redirects: bool,
        trust_env: bool,
    ) -> FakeResponse:
        captured_request["url"] = url
        captured_request["params"] = params
        captured_request["timeout"] = timeout
        captured_request["headers"] = headers
        captured_request["follow_redirects"] = follow_redirects
        captured_request["trust_env"] = trust_env
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)

    papers = search_arxiv_papers("  LLM   Agent  ", max_results=20)

    assert len(papers) == 1
    assert captured_request["url"] == "https://export.arxiv.org/api/query"
    assert captured_request["params"] == {
        "search_query": "all:LLM Agent",
        "start": 0,
        "max_results": 10,
        "sortBy": "relevance",
        "sortOrder": "descending",
    }
    assert captured_request["timeout"] == 20
    assert captured_request["headers"] == {
        "User-Agent": "ScholarAgent/0.1 (https://github.com/Thyguad/ScholarAgent)"
    }
    assert captured_request["follow_redirects"] is True
    assert captured_request["trust_env"] is False


def test_search_arxiv_papers_retries_rate_limited_response(monkeypatch) -> None:
    requests: list[int] = []
    sleeps: list[float] = []

    class FakeResponse:
        def __init__(self, status_code: int) -> None:
            self.status_code = status_code
            self.text = SAMPLE_ARXIV_FEED
            self.headers: dict[str, str] = {}

        def raise_for_status(self) -> None:
            if self.status_code >= 400:
                raise httpx.HTTPStatusError(
                    "request failed",
                    request=httpx.Request("GET", "https://export.arxiv.org/api/query"),
                    response=httpx.Response(self.status_code),
                )

    def fake_get(*args: object, **kwargs: object) -> FakeResponse:
        requests.append(1)
        if len(requests) == 1:
            return FakeResponse(429)
        return FakeResponse(200)

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(arxiv_search.time, "sleep", fake_sleep)

    papers = search_arxiv_papers("LLM Agent", retries=2, retry_delay_seconds=3.0)

    assert len(papers) == 1
    assert len(requests) == 2
    assert sleeps == [3.0]


def test_search_arxiv_papers_respects_retry_after_header(monkeypatch) -> None:
    requests: list[int] = []
    sleeps: list[float] = []

    class FakeResponse:
        def __init__(self, status_code: int, retry_after: str | None = None) -> None:
            self.status_code = status_code
            self.text = SAMPLE_ARXIV_FEED
            self.headers = {}
            if retry_after is not None:
                self.headers["Retry-After"] = retry_after

        def raise_for_status(self) -> None:
            return None

    def fake_get(*args: object, **kwargs: object) -> FakeResponse:
        requests.append(1)
        if len(requests) == 1:
            return FakeResponse(429, retry_after="7")
        return FakeResponse(200)

    monkeypatch.setattr(httpx, "get", fake_get)
    monkeypatch.setattr(arxiv_search.time, "sleep", lambda seconds: sleeps.append(seconds))

    papers = search_arxiv_papers("LLM Agent", retries=2, retry_delay_seconds=3.0)

    assert len(papers) == 1
    assert sleeps == [7.0]


def test_search_arxiv_papers_raises_after_retry_exhaustion(monkeypatch) -> None:
    class FakeResponse:
        status_code = 503
        text = "Service unavailable"
        headers: dict[str, str] = {}

        def raise_for_status(self) -> None:
            raise httpx.HTTPStatusError(
                "request failed",
                request=httpx.Request("GET", "https://export.arxiv.org/api/query"),
                response=httpx.Response(503),
            )

    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: FakeResponse())
    monkeypatch.setattr(arxiv_search.time, "sleep", lambda seconds: None)

    with pytest.raises(ArxivSearchError):
        search_arxiv_papers("LLM Agent", retries=1, retry_delay_seconds=0)


def test_search_arxiv_papers_requires_query() -> None:
    with pytest.raises(ValueError):
        search_arxiv_papers("   ")
