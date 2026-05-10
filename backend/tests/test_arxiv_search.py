import httpx

from app.tools.arxiv_search import parse_arxiv_feed, search_arxiv_papers


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
        text = SAMPLE_ARXIV_FEED

        def raise_for_status(self) -> None:
            return None

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

    monkeypatch.setattr(httpx, "get", fake_get)

    papers = search_arxiv_papers("LLM Agent", max_results=20)

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
    assert captured_request["headers"] == {"User-Agent": "ScholarAgent/0.1"}
    assert captured_request["trust_env"] is False
