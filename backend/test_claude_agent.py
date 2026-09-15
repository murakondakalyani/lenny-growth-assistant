import asyncio

from app.agents.claude_runtime import run_claude_agent


async def main():
    question = (
        "How should an early-stage startup find product-market fit?"
    )

    print("=" * 80)
    print("CLAUDE AGENT SDK TEST")
    print("=" * 80)

    print()
    print(f"Question: {question}")
    print()

    try:
        result = await run_claude_agent(
            user_question=question,
            conversation_history=[],
        )

        print("=" * 80)
        print("AGENT RESULT")
        print("=" * 80)

        print()
        print(f"Provider: {result.provider}")
        print(f"Model: {result.model}")
        print(f"Session ID: {result.session_id}")

        print()
        print("ANSWER")
        print("-" * 80)
        print(result.answer)

        print()
        print("=" * 80)
        print("CLAUDE AGENT TEST PASSED")
        print("=" * 80)

    except Exception as exc:
        print()
        print("=" * 80)
        print("CLAUDE AGENT TEST FAILED")
        print("=" * 80)
        print()
        print(type(exc).__name__)
        print(str(exc))
        print()

        raise


if __name__ == "__main__":
    asyncio.run(main())