import json
import re

import httpx

from app.core.config import get_settings
from app.models.evidence_graph import Claim, Evidence, EvidenceGraph
from app.models.paper import Paper


class ClaimExtractionError(RuntimeError):
    """Claim 抽取失败时抛出的项目级异常。"""


def _required_evidence_ids(source_paper_id: str) -> list[str]:
    """返回 claim 抽取所依赖的 evidence ID 列表。

    当前阶段 claim 基于论文的 title 和 summary 抽取，
    所以要求图谱中必须存在这两条 evidence。
    """
    return [
        f"ev_{source_paper_id}_title",
        f"ev_{source_paper_id}_summary",
    ]


def _ensure_required_evidence_exists(
    source_paper_id: str,
    evidence_nodes: list[Evidence],
) -> list[str]:
    """确认 claim 绑定的 evidence 真实存在。

    ScholarAgent 的核心原则是每条 claim 都必须能追溯到 evidence。
    如果 evidence_graph 缺少 title 或 summary evidence，就不要继续抽取 claim，
    否则会生成指向不存在 evidence 的 claim。
    """
    existing_ids = {ev.id for ev in evidence_nodes}
    required_ids = _required_evidence_ids(source_paper_id)
    missing_ids = [eid for eid in required_ids if eid not in existing_ids]

    if missing_ids:
        raise ClaimExtractionError(
            f"缺少 claim 抽取所需 evidence：{', '.join(missing_ids)}"
        )

    return required_ids


def enrich_graph_with_claims(graph: EvidenceGraph) -> EvidenceGraph:
    """在已有 EvidenceGraph 上补充 claim_nodes。

    为每篇论文调用 LLM 抽取 claim，然后把 claim 绑定到对应
    title/summary evidence 上。

    开发阶段选择 fail-fast：只要 LLM 抽取失败，就让错误向上抛出，
    由 API 层转换成 503，避免用户误以为只是没有 claim。
    """
    all_claims: list[Claim] = []

    for paper in graph.papers:
        # 筛选出属于这篇论文的 evidence 节点
        paper_evidence = [
            ev for ev in graph.evidence_nodes
            if ev.source_paper_id == paper.source_id
        ]

        claims = extract_claims_for_paper(paper, paper_evidence)
        all_claims.extend(claims)

    graph.claim_nodes = all_claims
    return graph


def extract_claims_for_paper(
    paper: Paper,
    evidence_nodes: list[Evidence],
) -> list[Claim]:
    """从单篇论文的 title + summary 中抽取 claim。

    使用 LLM（OpenAI-compatible API）抽取 1-3 条关键科研声明，
    然后用代码绑定 evidence_ids，不让 LLM 猜系统内部 ID。

    在调用 LLM 前先校验 required evidence 是否真实存在于图谱中，
    确保生成的 claim 不会指向不存在的 evidence。
    """
    settings = get_settings()

    if not settings.llm_api_key:
        raise ClaimExtractionError("LLM_API_KEY 未配置，请在 backend/.env 中填写。")

    # 校验 required evidence 是否真实存在，校验通过后拿到 evidence_ids
    evidence_ids = _ensure_required_evidence_exists(
        paper.source_id,
        evidence_nodes,
    )

    llm_response = _call_llm(
        paper=paper,
        settings=settings,
    )

    raw_claims = _parse_llm_response(llm_response)
    claims = _build_claims(paper.source_id, raw_claims, evidence_ids)

    return claims


def _call_llm(*, paper: Paper, settings) -> dict:
    """调用 OpenAI-compatible Chat Completions API。

    第一版直接使用 httpx，不引入 OpenAI SDK，减少依赖。
    """
    url = f"{settings.llm_base_url.rstrip('/')}/chat/completions"

    try:
        response = httpx.post(
            url,
            json={
                "model": settings.llm_model,
                "temperature": 0,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a careful research claim extraction assistant. "
                            "Extract only claims that are directly supported by the "
                            "provided paper title and abstract. Do not use external "
                            "knowledge. Return strict JSON."
                        ),
                    },
                    {
                        "role": "user",
                        "content": _build_user_prompt(paper, settings.llm_max_claims_per_paper),
                    },
                ],
            },
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            timeout=settings.llm_timeout_seconds,
            trust_env=False,
        )
    except httpx.HTTPError as exc:
        raise ClaimExtractionError(f"LLM 请求失败：{exc}") from exc

    if response.status_code >= 400:
        raise ClaimExtractionError(
            f"LLM API 返回错误，状态码：{response.status_code}，"
            f"详情：{response.text[:300]}"
        )

    try:
        return response.json()
    except ValueError as exc:
        raise ClaimExtractionError("LLM 返回内容不是合法 JSON。") from exc


def _build_user_prompt(paper: Paper, max_claims: int) -> str:
    return (
        f"论文标题：\n{paper.title}\n\n"
        f"论文摘要：\n{paper.summary}\n\n"
        f"请抽取 1-{max_claims} 条关键科研 claim。\n"
        "要求：\n"
        "1. claim 必须来自标题或摘要。\n"
        "2. claim 应该是具体、可验证的陈述。\n"
        "3. 不要加入外部知识。\n"
        "4. 只返回 JSON，格式为：\n"
        '{"claims":[{"text":"...","confidence":0.9}]}'
    )


def _parse_llm_response(payload: dict) -> list[dict]:
    """从 LLM 返回的 Chat Completions JSON 中提取 claims 列表。

    LLM 的 JSON 可能包在 Markdown 代码块里（```json ... ```），
    需要先清洗再解析。
    """
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ClaimExtractionError(
            f"LLM 返回结构异常，缺少 choices[0].message.content：{exc}"
        ) from exc

    # 清洗可能的 Markdown 代码块包裹
    json_text = _strip_markdown_code_block(content)

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ClaimExtractionError(
            f"LLM 返回不是合法 JSON：{content[:300]}"
        ) from exc

    if not isinstance(data, dict) or "claims" not in data:
        raise ClaimExtractionError(
            f"LLM 返回 JSON 缺少 claims 字段：{content[:300]}"
        )

    if not isinstance(data["claims"], list):
        raise ClaimExtractionError(
            f"LLM 返回的 claims 不是数组：{content[:300]}"
        )

    return data["claims"]


def _strip_markdown_code_block(text: str) -> str:
    """去掉 LLM 返回里可能包裹的 ```json ... ```。"""
    # 匹配 ```json ... ``` 或 ``` ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def _build_claims(
    source_paper_id: str,
    raw_claims: list[dict],
    evidence_ids: list[str],
) -> list[Claim]:
    """把 LLM 返回的原始 claim dict 转成 Claim 模型。

    evidence_ids 由外部传入（已经过 _ensure_required_evidence_exists 校验），
    确保每条 claim 绑定的 evidence 都真实存在于图谱中。
    LLM 不应该猜系统内部 ID。
    """
    claims: list[Claim] = []

    for index, raw in enumerate(raw_claims, start=1):
        text = (raw.get("text") or "").strip()
        # 过滤空 claim 文本
        if not text:
            continue

        confidence = _clamp_confidence(raw.get("confidence"))

        claims.append(Claim(
            id=f"claim_{source_paper_id}_{index}",
            source_paper_id=source_paper_id,
            text=text,
            evidence_ids=evidence_ids,
            confidence=confidence,
        ))

    return claims


def _clamp_confidence(value: object) -> float:
    """安全处理 confidence 值：缺失默认 0.5，超出 0-1 范围则裁剪。"""
    if not isinstance(value, (int, float)):
        return 0.5
    return max(0.0, min(1.0, float(value)))
