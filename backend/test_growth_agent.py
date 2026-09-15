import asyncio

from app.agents.growth_agent import GrowthAgent
from app.db.session import AsyncSessionLocal


async def main():

    question = (
        "How should an early-stage startup "
        "find product-market fit?"
    )

    agent = GrowthAgent()

    async with AsyncSessionLocal() as session:

        result = await agent.answer(
            session=session,
            query=question,
        )

    print()
    print("=" * 80)
    print("LENNY GROWTH AGENT TEST")
    print("=" * 80)

    print()
    print("Provider:", result.provider)
    print("Model:", result.model)

    print()
    print("ANSWER")
    print("-" * 80)
    print(result.answer)

    print()
    print("EVIDENCE")
    print("-" * 80)

    for index, evidence in enumerate(
        result.evidence,
        start=1,
    ):
        print(
            f"[{index}] "
            f"{evidence.guest} — "
            f"{evidence.title}"
        )

        print(
            f"Score: "
            f"{evidence.final_score:.3f}"
        )

        print(
            f"URL: "
            f"{evidence.source_url}"
        )

    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())