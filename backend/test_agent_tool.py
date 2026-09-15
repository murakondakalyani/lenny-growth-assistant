import asyncio

from app.agents.tools import retrieve_knowledge


async def main():
    print("=" * 80)
    print("CLAUDE AGENT RETRIEVAL TOOL TEST")
    print("=" * 80)

    print(f"Tool name: {retrieve_knowledge.name}")
    print(f"Tool description: {retrieve_knowledge.description}")

    # The @tool decorator produces an SdkMcpTool.
    # The underlying Python handler is stored in `handler`.
    handler = retrieve_knowledge.handler

    result = await handler(
        {
            "query": "How should an early-stage startup find product-market fit?",
            "top_k": 5,
        }
    )

    print()
    print(f"Success: {result['success']}")
    print(f"Query: {result['query']}")
    print(f"Results: {result['result_count']}")
    print()

    for item in result["results"]:
        print(
            f"[Source {item['source_number']}] "
            f"{item['guest']} — {item['title']}"
        )

        print(f"Score: {item['relevance']}")
        print(f"URL: {item['source_url']}")

        evidence = item["evidence"].replace("\n", " ")

        print(
            f"Evidence: {evidence[:300]}..."
        )

        print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main())