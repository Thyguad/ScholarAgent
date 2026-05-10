from app.models.paper import Paper
from app.tools.arxiv_search import ArxivSearchError, search_arxiv_papers
from app.tools.openalex_search import OpenAlexSearchError, search_openalex_papers


class PaperSearchError(RuntimeError):
    """多源论文搜索整体失败时抛出的项目级异常。"""


def search_papers_across_sources(query: str, max_results: int = 5) -> list[Paper]:
    """多源论文搜索入口。

    当前策略是优先使用 OpenAlex，失败后再用 arXiv 兜底。
    后续 Semantic Scholar API key 通过后，可以在这里加入第二优先级来源。
    """
    errors: list[str] = []

    try:
        papers = search_openalex_papers(query=query, max_results=max_results)
        if papers:
            return papers
    except OpenAlexSearchError as exc:
        errors.append(str(exc))

    try:
        papers = search_arxiv_papers(query=query, max_results=max_results)
        if papers:
            return papers
    except ArxivSearchError as exc:
        errors.append(str(exc))

    if errors:
        raise PaperSearchError("；".join(errors))

    return []
