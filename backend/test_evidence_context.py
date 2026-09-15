import asyncio

from app.db.session import AsyncSessionLocal
from app.retrieval.context import format_evidence_context
from app.retrieval.retriever import HybridRetriever


async def main():
    query = "How should a startup find product market fit?"

    retriever = HybridRetriever()

    async with AsyncSessionLocal() as session:
        results = await retriever.search(
            session,
            query,
            top_k=5,
        )

    context = format_evidence_context(results)

    print("=" * 80)
    print("GROUNDED EVIDENCE CONTEXT")
    print("=" * 80)
    print(context)
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())