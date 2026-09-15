import asyncio

from app.db.session import AsyncSessionLocal
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

    print()
    print("=" * 80)
    print("RETRIEVAL TEST")
    print("=" * 80)
    print("Query:", query)
    print("Results:", len(results))
    print()

    for index, result in enumerate(
        results,
        start=1,
    ):
        print(f"[{index}] {result.title}")
        print(f"Guest: {result.guest}")
        print(f"Episode: {result.episode}")
        print(f"Semantic: {result.semantic_score:.3f}")
        print(f"Keyword: {result.keyword_score:.3f}")
        print(f"Final: {result.final_score:.3f}")
        print(f"Source: {result.source_url}")
        print(
            "Evidence:",
            result.content[:500].replace("\n", " "),
        )
        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())