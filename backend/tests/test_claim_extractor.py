import json

import httpx
import pytest

from app.core.config import Settings
from app.models.evidence_graph import Evidence, EvidenceGraph
from app.models.paper import Paper
from app.services.claim_extractor import (
    ClaimExtractionError,
    enrich_graph_with_claims,
    extract_claims_for_paper,
)
from app.services.graph_builder import build_evidence_graph


def _make_paper(source_id: str = "W123") -> Paper:
    return Paper(
        source="openalex",
        source_id=source_id,
        title="A Survey of LLM Agents",
        authors=["Alice Zhang"],
        summary="This paper surveys large language model agents for software engineering tasks.",
        published_at="2024-01-01",
        source_url="https://openalex.org/W123",
        pdf_url=None,
    )


def _make_evidence_nodes(source_id: str = "W123") -> list[Evidence]:
    """构造包含 title 和 summary 的最小 evidence 列表，供 claim 抽取使用。"""
    return [
        Evidence(
            id=f"ev_{source_id}_title",
            source_paper_id=source_id,
            field="title",
            content="A Survey of LLM Agents",
        ),
        Evidence(
            id=f"ev_{source_id}_summary",
            source_paper_id=source_id,
            field="summary",
            content="This paper surveys large language model agents.",
        ),
    ]


def _fake_llm_response(claims: list[dict]) -> dict:
    """构造符合 OpenAI Chat Completions 格式的假 LLM 返回。"""
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps({"claims": claims})
                }
            }
        ]
    }


class TestExtractClaimsForPaper:
    """验证从单篇论文抽取 claim 的核心逻辑。"""

    def test_generates_claims_with_stable_ids(self, monkeypatch) -> None:
        """LLM 正常返回时，claim 的 id 格式应为 claim_{source_id}_{index}。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        def fake_post(url, *, json=None, headers=None, timeout=None, trust_env=None):
            assert json["temperature"] == 0
            return _FakeResponse(200, _fake_llm_response([
                {"text": "This paper surveys LLM-based agents.", "confidence": 0.95},
            ]))

        monkeypatch.setattr(httpx, "post", fake_post)

        paper = _make_paper("W123")
        claims = extract_claims_for_paper(paper, _make_evidence_nodes("W123"))

        assert len(claims) == 1
        c = claims[0]
        assert c.id == "claim_W123_1"
        assert c.source_paper_id == "W123"
        assert c.text == "This paper surveys LLM-based agents."

    def test_claim_evidence_ids_bound_by_code(self, monkeypatch) -> None:
        """evidence_ids 由代码绑定（title + summary），不让 LLM 猜。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        monkeypatch.setattr(
            httpx, "post",
            lambda *a, **kw: _FakeResponse(200, _fake_llm_response([
                {"text": "A survey.", "confidence": 0.9},
            ])),
        )

        paper = _make_paper("W456")
        claims = extract_claims_for_paper(paper, _make_evidence_nodes(paper.source_id))

        assert claims[0].evidence_ids == ["ev_W456_title", "ev_W456_summary"]

    def test_multiple_claims_per_paper(self, monkeypatch) -> None:
        """LLM 返回多条 claim 时，每条应有独立的 index。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        monkeypatch.setattr(
            httpx, "post",
            lambda *a, **kw: _FakeResponse(200, _fake_llm_response([
                {"text": "Claim 1.", "confidence": 0.9},
                {"text": "Claim 2.", "confidence": 0.8},
                {"text": "Claim 3.", "confidence": 0.7},
            ])),
        )

        claims = extract_claims_for_paper(_make_paper("W123"), _make_evidence_nodes("W123"))
        assert len(claims) == 3
        assert [c.id for c in claims] == [
            "claim_W123_1", "claim_W123_2", "claim_W123_3"
        ]

    def test_filters_empty_claim_text(self, monkeypatch) -> None:
        """LLM 返回空 text 的 claim 应被过滤掉。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        monkeypatch.setattr(
            httpx, "post",
            lambda *a, **kw: _FakeResponse(200, _fake_llm_response([
                {"text": "", "confidence": 0.9},   # 空文本——过滤掉
                {"text": "Valid claim.", "confidence": 0.8},
            ])),
        )

        claims = extract_claims_for_paper(_make_paper("W123"), _make_evidence_nodes("W123"))
        assert len(claims) == 1
        assert claims[0].text == "Valid claim."

    def test_missing_confidence_defaults_to_half(self, monkeypatch) -> None:
        """confidence 缺失时使用默认值 0.5。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        monkeypatch.setattr(
            httpx, "post",
            lambda *a, **kw: _FakeResponse(200, _fake_llm_response([
                {"text": "A claim without confidence."},
            ])),
        )

        claims = extract_claims_for_paper(_make_paper("W123"), _make_evidence_nodes("W123"))
        assert claims[0].confidence == 0.5

    def test_clamps_confidence_out_of_range(self, monkeypatch) -> None:
        """confidence 超出 0-1 时应被裁剪到合法范围。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        monkeypatch.setattr(
            httpx, "post",
            lambda *a, **kw: _FakeResponse(200, _fake_llm_response([
                {"text": "Overconfident.", "confidence": 1.5},
                {"text": "Negative confidence.", "confidence": -0.3},
            ])),
        )

        claims = extract_claims_for_paper(_make_paper("W123"), _make_evidence_nodes("W123"))
        assert claims[0].confidence == 1.0   # 1.5 裁剪到 1.0
        assert claims[1].confidence == 0.0   # -0.3 裁剪到 0.0

    def test_requires_api_key(self, monkeypatch) -> None:
        """没有 LLM_API_KEY 时应抛 ClaimExtractionError。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key=None),
        )

        with pytest.raises(ClaimExtractionError, match="LLM_API_KEY"):
            extract_claims_for_paper(_make_paper(), _make_evidence_nodes("W123"))

    def test_invalid_json_raises_error(self, monkeypatch) -> None:
        """LLM 返回的不是合法 JSON 时抛 ClaimExtractionError。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        class BadJsonResponse:
            status_code = 200
            def json(self):
                return {"choices": [{"message": {"content": "not json at all!!!"}}]}

        monkeypatch.setattr(httpx, "post", lambda *a, **kw: BadJsonResponse())

        with pytest.raises(ClaimExtractionError):
            extract_claims_for_paper(_make_paper(), _make_evidence_nodes("W123"))

    def test_missing_claims_field_raises_error(self, monkeypatch) -> None:
        """LLM 返回的 JSON 没有 claims 字段时抛 ClaimExtractionError。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        class BadStructureResponse:
            status_code = 200
            def json(self):
                return {"choices": [{"message": {"content": '{"other": 1}'}}]}

        monkeypatch.setattr(httpx, "post", lambda *a, **kw: BadStructureResponse())

        with pytest.raises(ClaimExtractionError):
            extract_claims_for_paper(_make_paper(), _make_evidence_nodes("W123"))

    def test_llm_http_error_raises(self, monkeypatch) -> None:
        """LLM API 返回非 2xx 状态码时抛 ClaimExtractionError。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        monkeypatch.setattr(
            httpx, "post",
            lambda *a, **kw: _FakeResponse(401, {"error": "Unauthorized"}),
        )

        with pytest.raises(ClaimExtractionError):
            extract_claims_for_paper(_make_paper(), _make_evidence_nodes("W123"))

    def test_missing_title_evidence_raises_error(self) -> None:
        """缺少 title evidence 时应在调 LLM 之前就抛错，不需要 monkeypatch LLM。"""
        paper = _make_paper("W123")
        evidence_nodes = [
            Evidence(
                id="ev_W123_summary",
                source_paper_id="W123",
                field="summary",
                content="summary",
            )
        ]

        with pytest.raises(ClaimExtractionError, match="ev_W123_title"):
            extract_claims_for_paper(paper, evidence_nodes)

    def test_strips_markdown_code_block_from_llm_response(self, monkeypatch) -> None:
        """LLM 返回包在 ```json ... ``` 里时，应正确剥离并解析。"""
        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        content = '```json\n{"claims":[{"text":"A claim.","confidence":0.9}]}\n```'
        class MarkdownResponse:
            status_code = 200
            def json(self):
                return {"choices": [{"message": {"content": content}}]}

        monkeypatch.setattr(httpx, "post", lambda *a, **kw: MarkdownResponse())

        claims = extract_claims_for_paper(_make_paper("W123"), _make_evidence_nodes("W123"))
        assert len(claims) == 1
        assert claims[0].text == "A claim."


class TestEnrichGraphWithClaims:
    """验证 enrich_graph_with_claims 在 EvidenceGraph 上批量补充 claim。"""

    def test_adds_claims_to_graph(self, monkeypatch) -> None:
        """单篇论文的 graph 应被填充对应的 claim_nodes。"""
        paper = _make_paper("W1")
        graph = build_evidence_graph([paper])

        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )
        monkeypatch.setattr(
            httpx, "post",
            lambda *a, **kw: _FakeResponse(200, _fake_llm_response([
                {"text": "Claim about survey.", "confidence": 0.9},
            ])),
        )

        enriched = enrich_graph_with_claims(graph)
        assert len(enriched.claim_nodes) == 1
        assert enriched.claim_nodes[0].source_paper_id == "W1"

    def test_empty_graph_returns_empty_claims(self) -> None:
        """空图谱没有论文，claim_nodes 也应为空。"""
        graph = EvidenceGraph(papers=[], evidence_nodes=[])
        enriched = enrich_graph_with_claims(graph)
        assert enriched.claim_nodes == []

    def test_multiple_papers_each_get_own_claims(self, monkeypatch) -> None:
        """多篇论文时，每篇都有自己的 claim，source_paper_id 不混淆。"""
        papers = [_make_paper("W1"), _make_paper("W2")]
        graph = build_evidence_graph(papers)

        monkeypatch.setattr(
            "app.services.claim_extractor.get_settings",
            lambda: Settings(llm_api_key="test-key"),
        )

        # 两篇论文分别返回不同的 claim
        call_count = [0]
        def fake_post(*a, **kw):
            call_count[0] += 1
            if call_count[0] == 1:
                return _FakeResponse(200, _fake_llm_response([
                    {"text": "Claim from W1.", "confidence": 0.9},
                ]))
            return _FakeResponse(200, _fake_llm_response([
                {"text": "Claim from W2.", "confidence": 0.8},
            ]))

        monkeypatch.setattr(httpx, "post", fake_post)

        enriched = enrich_graph_with_claims(graph)
        assert len(enriched.claim_nodes) == 2
        source_ids = {c.source_paper_id for c in enriched.claim_nodes}
        assert source_ids == {"W1", "W2"}

    def test_enrich_graph_raises_when_one_paper_fails(self, monkeypatch) -> None:
        """开发阶段 fail-fast：任何一篇论文的 LLM 抽取失败都应向上抛错。"""
        papers = [_make_paper("W1"), _make_paper("W2")]
        graph = build_evidence_graph(papers)

        import app.services.claim_extractor as claim_extractor_mod

        def fake_extract(paper: Paper, evidence_nodes: list) -> list:
            raise ClaimExtractionError("LLM failed")

        monkeypatch.setattr(
            claim_extractor_mod,
            "extract_claims_for_paper",
            fake_extract,
        )

        with pytest.raises(ClaimExtractionError, match="LLM failed"):
            enrich_graph_with_claims(graph)


class FakeResponse:
    """模拟 httpx.Response 的最小对象。"""
    status_code: int
    _json: dict

    def __init__(self, status_code: int, json_data: dict) -> None:
        self.status_code = status_code
        self._json = json_data

    def json(self) -> dict:
        return self._json


class _FakeResponse:
    """httpx post 返回的假对象。"""
    def __init__(self, status_code: int, json_data: dict, text: str = "") -> None:
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def json(self) -> dict:
        return self._json
