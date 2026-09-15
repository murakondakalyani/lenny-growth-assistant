import asyncio

from app.db.session import AsyncSessionLocal
from app.skills.ship30 import Ship30Skill


async def main():
    topic = (
        "How should an early-stage startup find product-market fit?"
    )

    print("=" * 80)
    print("SHIP 30 SKILL TEST")
    print("=" * 80)

    print()
    print(f"Topic: {topic}")
    print()

    async with AsyncSessionLocal() as session:
        skill = Ship30Skill()

        result = await skill.generate(
            session=session,
            topic=topic,
        )

    print("=" * 80)
    print("RESULT")
    print("=" * 80)

    print()
    print(f"Provider: {result.provider}")
    print(f"Model: {result.model}")
    print(f"Word count: {result.word_count}")

    print()
    print("-" * 80)
    print(result.content)
    print("-" * 80)

    print()
    print("Sources retrieved:")

    for index, item in enumerate(result.evidence, start=1):
        print(
            f"[Source {index}] "
            f"{item.guest or 'Unknown'} — "
            f"{item.title}"
        )

    print()
    print("=" * 80)
    print("SHIP 30 TEST PASSED")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())