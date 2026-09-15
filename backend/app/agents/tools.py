from typing import Any

from claude_agent_sdk import tool

from app.retrieval.retriever import HybridRetriever


@tool(
    "retrieve_knowledge",
    """
    Search Lenny's Podcast knowledge base for evidence relevant to
    the user's question.

    Use this tool whenever the user asks about product management,
    growth, startups, leadership, strategy, or advice that should
    be grounded in Lenny's content.
    """,
    {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The question or topic to search for."
            },
            "top_k": {
                "type": "integer",
                "description": "Maximum number of evidence chunks to return.",
                "default": 5
            }
        },
        "required": ["query"]
    },
)
async def retrieve_knowledge(args: dict[str, Any]) -> dict[str, Any]:
    """
    Claude Agent SDK tool that searches PostgreSQL + pgvector.
    """

    query = str(args.get("query", "")).strip()

    if not query:
        return {
            "success": False,
            "error": "Search query cannot be empty.",
            "results": [],
        }

    top_k = int(args.get("top_k", 5))
    top_k = max(1, min(top_k, 8))

    retriever = HybridRetriever()

    # The SDK tool does not receive our FastAPI DB dependency directly.
    # The retriever creates/uses the configured database session.
    #
    # For the first SDK integration test we use the existing retriever
    # session helper below.
    from app.db.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        evidence = await retriever.search(
            session=session,
            query=query,
            top_k=top_k,
        )

    results = []

    for index, item in enumerate(evidence, start=1):
        results.append(
            {
                "source_number": index,
                "title": item.title,
                "guest": item.guest or "Unknown",
                "episode": item.episode or "Unknown",
                "source_url": item.source_url or "Unavailable",
                "relevance": round(item.final_score, 4),
                "evidence": item.content,
            }
        )

    return {
        "success": True,
        "query": query,
        "result_count": len(results),
        "results": results,
    }