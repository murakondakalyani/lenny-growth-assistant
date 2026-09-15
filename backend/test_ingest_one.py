import asyncio
from pathlib import Path

from app.db.session import AsyncSessionLocal
from app.retrieval.embeddings import OllamaEmbeddingProvider
from app.retrieval.ingestion import ingest_file


async def main():
    path = Path(
        "data/transcripts/episodes/"
        "ada-chen-rekhi/transcript.md"
    )

    async with AsyncSessionLocal() as session:
        ingested, chunks = await ingest_file(
            session,
            OllamaEmbeddingProvider(),
            path,
        )

    print("Ingested:", ingested)
    print("Chunks:", chunks)


if __name__ == "__main__":
    asyncio.run(main())