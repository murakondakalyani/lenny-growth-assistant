import asyncio
import hashlib
import time
from pathlib import Path

from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.chunk import Chunk
from app.models.document import Document
from app.retrieval.chunking import split_into_chunks
from app.retrieval.embeddings import OllamaEmbeddingProvider
from app.retrieval.transcript_parser import parse_transcript


PROJECT_ROOT = Path(__file__).resolve().parents[3]

TRANSCRIPTS_DIR = (
    PROJECT_ROOT
    / "data"
    / "transcripts"
    / "episodes"
)

EMBED_BATCH_SIZE = 32


def content_hash(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def find_transcripts() -> list[Path]:
    return sorted(
        TRANSCRIPTS_DIR.rglob("*.md")
    )


async def document_exists(
    session,
    file_hash: str,
) -> bool:
    result = await session.execute(
        select(Document.id).where(
            Document.content_hash == file_hash
        )
    )

    return result.scalar_one_or_none() is not None


async def ingest_file(
    session,
    embedding_provider,
    path: Path,
):
    parsed = parse_transcript(path)

    if not parsed.content:
        return False, 0

    file_hash = content_hash(parsed.content)

    if await document_exists(session, file_hash):
        return False, 0

    chunks = split_into_chunks(parsed.content)

    if not chunks:
        return False, 0

    document = Document(
        source_type="lenny_transcript",
        title=parsed.title,
        guest=parsed.guest,
        episode=parsed.video_id,
        source_url=parsed.source_url,
        content_hash=file_hash,
    )

    session.add(document)
    await session.flush()

    # Generate embeddings in batches instead of
    # making one HTTP request per chunk.
    for start in range(
        0,
        len(chunks),
        EMBED_BATCH_SIZE,
    ):
        batch = chunks[
            start:start + EMBED_BATCH_SIZE
        ]

        texts = [
            chunk.content
            for chunk in batch
        ]

        embeddings = await embedding_provider.embed_many(
            texts
        )

        for chunk, embedding in zip(
            batch,
            embeddings,
        ):
            session.add(
                Chunk(
                    document_id=document.id,
                    chunk_index=chunk.index,
                    content=chunk.content,
                    embedding=embedding,
                    heading=chunk.heading,
                    source_url=parsed.source_url,
                    guest=parsed.guest,
                    episode=parsed.video_id,
                )
            )

    await session.commit()

    return True, len(chunks)


async def ingest_all():
    files = find_transcripts()

    print("=" * 70)
    print("LENNY KNOWLEDGE BASE INGESTION")
    print("=" * 70)
    print(f"Transcript directory: {TRANSCRIPTS_DIR}")
    print(f"Transcripts found: {len(files)}")
    print(f"Embedding batch size: {EMBED_BATCH_SIZE}")
    print("=" * 70)

    if not files:
        print("No transcript files found.")
        return

    embedding_provider = OllamaEmbeddingProvider()

    ingested = 0
    skipped = 0
    failures = 0
    total_chunks = 0

    started = time.perf_counter()

    for index, path in enumerate(
        files,
        start=1,
    ):
        try:
            async with AsyncSessionLocal() as session:
                was_ingested, chunk_count = (
                    await ingest_file(
                        session,
                        embedding_provider,
                        path,
                    )
                )

            if was_ingested:
                ingested += 1
                total_chunks += chunk_count

                print(
                    f"[{index}/{len(files)}] "
                    f"INGESTED  "
                    f"{path.parent.name}  "
                    f"({chunk_count} chunks)"
                )
            else:
                skipped += 1

                print(
                    f"[{index}/{len(files)}] "
                    f"SKIPPED   "
                    f"{path.parent.name}"
                )

        except Exception as exc:
            failures += 1

            print(
                f"[{index}/{len(files)}] "
                f"FAILED    "
                f"{path.parent.name}: {exc}"
            )

    elapsed = time.perf_counter() - started

    print()
    print("=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)
    print(f"Ingested documents : {ingested}")
    print(f"Skipped documents  : {skipped}")
    print(f"Failed documents   : {failures}")
    print(f"Total chunks       : {total_chunks}")
    print(f"Elapsed time       : {elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(ingest_all())