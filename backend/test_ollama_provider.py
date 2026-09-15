import asyncio

from app.providers.ollama import OllamaProvider


async def main():

    provider = OllamaProvider()

    response = await provider.generate(
        system_prompt=(
            "You are a concise assistant. "
            "Answer in one sentence."
        ),
        user_prompt=(
            "What is product-market fit?"
        ),
    )

    print("=" * 60)
    print("OLLAMA PROVIDER TEST")
    print("=" * 60)
    print("Provider:", response.provider)
    print("Model:", response.model)
    print("Response:")
    print(response.content)
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())