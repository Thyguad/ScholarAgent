import time
from xml.etree import ElementTree

import httpx

from app.models.paper import Paper


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}
USER_AGENT = "ScholarAgent/0.1 (https://github.com/Thyguad/ScholarAgent)"


class ArxivSearchError(RuntimeError):
    """arXiv 搜索失败时抛出的项目级异常。"""


def search_arxiv_papers(
    query: str,
    max_results: int = 5,
    *,
    retries: int = 1,
    retry_delay_seconds: float = 3.0,
) -> list[Paper]:
    """搜索 arXiv 论文并返回统一的 Paper 模型。

    这一层只负责调用外部 API 和做数据转换，不直接写 FastAPI 路由。
    这样后续无论是 API、Agent 节点还是测试，都可以复用同一个工具函数。
    """
    search_query = _build_search_query(query)
    safe_max_results = max(1, min(max_results, 10))
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        try:
            response = httpx.get(
                ARXIV_API_URL,
                params={
                    "search_query": search_query,
                    "start": 0,
                    "max_results": safe_max_results,
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                },
                timeout=20,
                headers={"User-Agent": USER_AGENT},
                follow_redirects=True,
                # 不读取本机代理环境变量，避免开发机上异常代理配置影响 arXiv 请求。
                trust_env=False,
            )
            if _should_retry(response.status_code, attempt, retries):
                # arXiv 官方建议连续请求之间保持间隔；遇到限流或临时错误时主动退让。
                time.sleep(_retry_delay(response, retry_delay_seconds, attempt))
                continue

            if response.status_code >= 400:
                raise ArxivSearchError(_status_error_message(response.status_code))

            return parse_arxiv_feed(response.text)
        except ArxivSearchError:
            raise
        except (httpx.HTTPError, ElementTree.ParseError) as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(retry_delay_seconds * (attempt + 1))
                continue
            break

    raise ArxivSearchError(f"arXiv 搜索失败，请稍后重试：{last_error}") from last_error


def parse_arxiv_feed(feed_xml: str) -> list[Paper]:
    """把 arXiv 返回的 Atom XML 转成项目内部使用的论文列表。

    arXiv API 返回的是 XML，不是 JSON。我们先在工具层把外部格式清洗掉，
    后续系统内部就只处理结构稳定的 Pydantic 模型。
    """
    root = ElementTree.fromstring(feed_xml)
    papers: list[Paper] = []

    for entry in root.findall("atom:entry", ATOM_NAMESPACE):
        source_url = _text(entry, "atom:id")
        papers.append(
            Paper(
                source="arxiv",
                source_id=_extract_arxiv_id(source_url),
                title=_normalize_text(_text(entry, "atom:title")),
                authors=_extract_authors(entry),
                summary=_normalize_text(_text(entry, "atom:summary")),
                published_at=_text(entry, "atom:published"),
                source_url=source_url,
                pdf_url=_extract_pdf_url(entry),
            )
        )

    return papers


def _build_search_query(query: str) -> str:
    normalized_query = _normalize_text(query)
    if not normalized_query:
        raise ValueError("query 不能为空")

    return f"all:{normalized_query}"


def _should_retry(status_code: int, attempt: int, retries: int) -> bool:
    return status_code in RETRYABLE_STATUS_CODES and attempt < retries


def _retry_delay(
    response: httpx.Response,
    retry_delay_seconds: float,
    attempt: int,
) -> float:
    retry_after = response.headers.get("Retry-After")
    if retry_after is not None and retry_after.isdigit():
        return float(retry_after)

    return retry_delay_seconds * (attempt + 1)


def _status_error_message(status_code: int) -> str:
    if status_code == 429:
        return "arXiv API 临时限流，请稍后重试。"
    if status_code in {500, 502, 503, 504}:
        return f"arXiv API 暂时不可用，状态码：{status_code}。"
    return f"arXiv API 请求失败，状态码：{status_code}。"


def _text(entry: ElementTree.Element, path: str) -> str:
    element = entry.find(path, ATOM_NAMESPACE)
    if element is None or element.text is None:
        return ""
    return element.text.strip()


def _normalize_text(value: str) -> str:
    # arXiv 的标题和摘要里经常带换行与多余空格，这里统一压成单行文本。
    return " ".join(value.split())


def _extract_authors(entry: ElementTree.Element) -> list[str]:
    authors: list[str] = []
    for author in entry.findall("atom:author", ATOM_NAMESPACE):
        name = _text(author, "atom:name")
        if name:
            authors.append(name)
    return authors


def _extract_pdf_url(entry: ElementTree.Element) -> str | None:
    for link in entry.findall("atom:link", ATOM_NAMESPACE):
        if link.attrib.get("title") == "pdf":
            return link.attrib.get("href")
    return None


def _extract_arxiv_id(source_url: str) -> str:
    if not source_url:
        return ""
    return source_url.rstrip("/").split("/")[-1]
