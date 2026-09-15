from app.retrieval.retriever import RetrievedEvidence


def format_evidence_context(
    evidence: list[RetrievedEvidence],
) -> str:

    if not evidence:
        return (
            "No relevant evidence was found in the Lenny knowledge base."
        )

    sections = []

    for index, item in enumerate(evidence, start=1):

        sections.append(
            f"""
SOURCE {index}

TITLE:
{item.title}

GUEST:
{item.guest or "Unknown"}

EPISODE ID:
{item.episode or "Unknown"}

SOURCE URL:
{item.source_url or "Unavailable"}

RELEVANCE SCORE:
{item.final_score:.3f}

EVIDENCE:
{item.content}
""".strip()
        )

    return "\n\n".join(sections)