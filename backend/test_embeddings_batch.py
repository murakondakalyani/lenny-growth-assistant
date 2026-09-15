import asyncio

from app.retrieval.embeddings import OllamaEmbeddingProvider


async def main():
    provider = OllamaEmbeddingProvider()

    texts = [
        "How do product teams find product-market fit?",
        "What makes a great product manager?",
        "How should startups prioritize growth experiments?",
    ]

    embeddings = await provider.embed_many(texts)

    print("Texts:", len(texts))
    print("Embeddings:", len(embeddings))
    print("Dimensions:", len(embeddings[0]))

    assert len(embeddings) == len(texts)
    assert all(len(vector) == 768 for vector in embeddings)

    print("Batch embedding test OK")


if __name__ == "__main__":
    asyncio.run(main())