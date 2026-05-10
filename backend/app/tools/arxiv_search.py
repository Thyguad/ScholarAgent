from xml.etree import ElementTree

import httpx

from app.models.paper import Paper


ARXIV_API_URL = "https://export.arxiv.org/api/query"
ATOM_NAMESPACE = {"atom": "http://www.w3.org/2005/Atom"}


def search_arxiv_papers(query: str, max_results: int = 5) -> list[Paper]:
    """搜索 arXiv 论文并返回统一的 Paper 模型。

    这一层只负责调用外部 API 和做数据转换，不直接写 FastAPI 路由。
    这样后续无论是 API、Agent 节点还是测试，都可以复用同一个工具函数。
    """
    safe_max_results = max(1, min(max_results, 10))
    response = httpx.get(
        ARXIV_API_URL,
        params={
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": safe_max_results,
            "sortBy": "relevance",
            "sortOrder": "descending",
        },
        timeout=20,
        headers={"User-Agent": "ScholarAgent/0.1"},
        # 不读取本机代理环境变量，避免开发机上异常代理配置影响 arXiv 请求。
        trust_env=False,
    )
    response.raise_for_status()

    return parse_arxiv_feed(response.text)


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
