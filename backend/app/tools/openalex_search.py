import httpx

from app.core.config import get_settings
from app.models.paper import Paper


OPENALEX_WORKS_URL = "https://api.openalex.org/works"
USER_AGENT = "ScholarAgent/0.1 (https://github.com/Thyguad/ScholarAgent)"


class OpenAlexSearchError(RuntimeError):
    """OpenAlex 搜索失败时抛出的项目级异常。"""


def search_openalex_papers(query: str, max_results: int = 5) -> list[Paper]:
    """使用 OpenAlex 搜索论文并转换为统一 Paper 模型。"""
    normalized_query = _normalize_text(query)
    if not normalized_query:
        raise ValueError("query 不能为空")

    settings = get_settings()
    if not settings.openalex_api_key:
        raise OpenAlexSearchError("OPENALEX_API_KEY 未配置，请在 backend/.env 中填写。")

    response = httpx.get(
        OPENALEX_WORKS_URL,
        params=_build_openalex_params(
            query=normalized_query,
            max_results=max_results,
            api_key=settings.openalex_api_key,
            mailto=settings.openalex_mailto,
        ),
        timeout=20,
        headers={"User-Agent": USER_AGENT},
        trust_env=False,
    )

    if response.status_code >= 400:
        raise OpenAlexSearchError(f"OpenAlex 请求失败，状态码：{response.status_code}。")

    try:
        payload = response.json()
    except ValueError as exc:
        raise OpenAlexSearchError("OpenAlex 返回内容不是合法 JSON。") from exc

    return parse_openalex_works(payload)


def parse_openalex_works(payload: dict) -> list[Paper]:
    """把 OpenAlex works JSON 转成项目内部统一的 Paper 列表。"""
    papers: list[Paper] = []

    for work in payload.get("results", []):
        source_url = _source_url(work)
        papers.append(
            Paper(
                source="openalex",
                source_id=_extract_openalex_id(str(work.get("id", ""))),
                title=_normalize_text(str(work.get("display_name") or "")),
                authors=_extract_authors(work),
                summary=_reconstruct_abstract(work.get("abstract_inverted_index")),
                published_at=str(work.get("publication_date") or work.get("publication_year") or ""),
                source_url=source_url,
                pdf_url=_pdf_url(work),
            )
        )

    return papers


def _build_openalex_params(
    *,
    query: str,
    max_results: int,
    api_key: str,
    mailto: str | None,
) -> dict[str, str | int]:
    safe_max_results = max(1, min(max_results, 10))
    params: dict[str, str | int] = {
        "search": query,
        "per-page": safe_max_results,
        "sort": "relevance_score:desc",
        "select": ",".join(
            [
                "id",
                "display_name",
                "authorships",
                "abstract_inverted_index",
                "publication_date",
                "publication_year",
                "primary_location",
                "open_access",
                "doi",
            ]
        ),
    }

    params["api_key"] = api_key

    if mailto:
        params["mailto"] = mailto

    return params


def _extract_openalex_id(openalex_url: str) -> str:
    if not openalex_url:
        return ""
    return openalex_url.rstrip("/").split("/")[-1]


def _extract_authors(work: dict) -> list[str]:
    authors: list[str] = []
    for authorship in work.get("authorships", []):
        author = authorship.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(str(name))
    return authors


def _reconstruct_abstract(inverted_index: object) -> str:
    """把 OpenAlex 的 abstract_inverted_index 还原成普通摘要文本。

    OpenAlex 为了节省空间，把摘要存成 `{单词: [位置...]}` 的倒排索引。
    我们在工具层还原它，后续 Agent 就不用理解 OpenAlex 的特殊格式。
    """
    if not isinstance(inverted_index, dict):
        return ""

    positions: dict[int, str] = {}
    for word, indexes in inverted_index.items():
        if not isinstance(indexes, list):
            continue
        for index in indexes:
            if isinstance(index, int):
                positions[index] = str(word)

    return " ".join(positions[index] for index in sorted(positions))


def _source_url(work: dict) -> str:
    primary_location = work.get("primary_location") or {}
    landing_page_url = primary_location.get("landing_page_url")
    if landing_page_url:
        return str(landing_page_url)

    doi = work.get("doi")
    if doi:
        return str(doi)

    return str(work.get("id") or "")


def _pdf_url(work: dict) -> str | None:
    primary_location = work.get("primary_location") or {}
    pdf_url = primary_location.get("pdf_url")
    if pdf_url:
        return str(pdf_url)

    open_access = work.get("open_access") or {}
    oa_url = open_access.get("oa_url")
    if oa_url:
        return str(oa_url)

    return None


def _normalize_text(value: str) -> str:
    return " ".join(value.split())
