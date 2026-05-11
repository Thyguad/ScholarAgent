from datetime import datetime, timezone

from app.models.evidence_graph import EvidenceGraph


def build_evidence_report(graph: EvidenceGraph, query: str = "") -> str:
    """基于 EvidenceGraph 生成 Markdown 报告。纯规则拼接，不调用 LLM。

    报告中的每个 claim 都附带 claim_id、source_paper_id 和 evidence_ids，
    方便追溯到具体的论文和证据来源。
    """
    lines: list[str] = []

    # --- 报告头部 ---
    topic = query or "未指定主题"
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    paper_count = len(graph.papers)
    evidence_count = len(graph.evidence_nodes)
    claim_count = len(graph.claim_nodes)

    lines.append(f"# 研究报告：{topic}")
    lines.append("")
    lines.append(f"> 搜索关键词：{query or '（未指定）'}")
    lines.append(f"> 生成时间：{now}")
    lines.append(
        f"> 论文数：{paper_count}  |  "
        f"证据节点：{evidence_count}  |  "
        f"Claim：{claim_count}"
    )
    lines.append("")

    if not graph.papers:
        lines.append("_未搜索到论文。_")
        return "\n".join(lines)

    # --- 每篇论文一节 ---
    for index, paper in enumerate(graph.papers, start=1):
        pid = paper.source_id

        # 筛选该论文的 evidence 和 claim
        paper_evidence = [
            ev for ev in graph.evidence_nodes
            if ev.source_paper_id == pid
        ]
        paper_claims = [
            c for c in graph.claim_nodes
            if c.source_paper_id == pid
        ]

        lines.append("---")
        lines.append("")
        lines.append(f"## {index}. {paper.title}")
        lines.append("")

        # 论文基本信息
        authors_text = ", ".join(paper.authors) if paper.authors else "（未知）"
        lines.append(f"- **作者**：{authors_text}")
        lines.append(f"- **发表**：{paper.published_at or '（未知）'}")
        lines.append(f"- **来源**：{paper.source}  |  [查看原文]({paper.source_url})")
        lines.append(f"- **溯源 ID**：`{pid}`")
        lines.append("")

        # 摘要
        if paper.summary:
            lines.append(f"### 摘要")
            lines.append("")
            lines.append(paper.summary)
            lines.append("")

        # 证据节点
        if paper_evidence:
            lines.append("### 证据节点")
            lines.append("")
            lines.append("| 字段 | 内容 | Evidence ID |")
            lines.append("|------|------|-------------|")
            for ev in paper_evidence:
                # 截断过长内容，保持表格可读
                content = ev.content[:150] + "..." if len(ev.content) > 150 else ev.content
                lines.append(f"| {ev.field} | {content} | `{ev.id}` |")
            lines.append("")

        # Claim 节点
        if paper_claims:
            lines.append("### 关键声明")
            lines.append("")
            lines.append("| ID | Claim | 置信度 | 溯源 |")
            lines.append("|----|-------|--------|------|")
            for c in paper_claims:
                confidence_pct = f"{c.confidence:.0%}"
                # 溯源链：claim → source_paper → evidence_ids
                evidence_list = ", ".join(f"`{eid}`" for eid in c.evidence_ids)
                trace = f"→ {evidence_list}"
                lines.append(
                    f"| `{c.id}` | {c.text} | {confidence_pct} | `{pid}` {trace} |"
                )
            lines.append("")

    return "\n".join(lines)
