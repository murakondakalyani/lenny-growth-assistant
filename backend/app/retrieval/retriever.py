from dataclasses import dataclass
from time import perf_counter

from sqlalchemy import Float, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.chunk import Chunk
from app.models.document import Document
from app.retrieval.embeddings import OllamaEmbeddingProvider


@dataclass
class RetrievedEvidence:
    """
    A single piece of evidence retrieved from the
    Lenny knowledge base.
    """

    chunk_id: str
    document_id: str

    content: str

    title: str
    guest: str | None
    episode: str | None
    source_url: str | None
    heading: str | None

    semantic_score: float
    keyword_score: float
    final_score: float


class HybridRetriever:
    """
    Hybrid retrieval using:

    1. Semantic search with pgvector
    2. Keyword search with PostgreSQL full-text search
    3. Weighted score combination
    4. Episode diversification
    """

    def __init__(self):
        settings = get_settings()

        self.top_k = settings.top_k
        self.rerank_top_k = settings.rerank_top_k

        self.embedding_provider = (
            OllamaEmbeddingProvider()
        )

    async def search(
        self,
        session: AsyncSession,
        query: str,
        top_k: int | None = None,
    ) -> list[RetrievedEvidence]:
        """
        Perform hybrid retrieval.

        Semantic search contributes 70%.
        Keyword search contributes 30%.

        Results are then diversified so that a single
        episode does not dominate the evidence set.
        """

        if not query or not query.strip():
            return []

        limit = top_k or self.rerank_top_k

        started = perf_counter()

        # --------------------------------------------------
        # 1. Generate query embedding
        # --------------------------------------------------

        query_embedding = (
            await self.embedding_provider.embed(query)
        )

        # --------------------------------------------------
        # 2. Semantic retrieval
        # --------------------------------------------------

        semantic_results = (
            await self._semantic_search(
                session=session,
                query_embedding=query_embedding,
                limit=self.top_k,
            )
        )

        # --------------------------------------------------
        # 3. Keyword retrieval
        # --------------------------------------------------

        keyword_results = (
            await self._keyword_search(
                session=session,
                query=query,
                limit=self.top_k,
            )
        )

        # --------------------------------------------------
        # 4. Combine semantic + keyword results
        # --------------------------------------------------

        combined = self._combine_results(
            semantic_results=semantic_results,
            keyword_results=keyword_results,
        )

        # --------------------------------------------------
        # 5. Sort by final hybrid score
        # --------------------------------------------------

        results = sorted(
            combined.values(),
            key=lambda item: item.final_score,
            reverse=True,
        )

        # --------------------------------------------------
        # 6. Diversify across episodes
        # --------------------------------------------------

        diversified = self._diversify_results(
            results,
            limit,
        )

        elapsed_ms = (
            perf_counter() - started
        ) * 1000

        print(
            f"Retrieval "
            f"query='{query}' "
            f"semantic={len(semantic_results)} "
            f"keyword={len(keyword_results)} "
            f"combined={len(results)} "
            f"final={len(diversified)} "
            f"latency_ms={elapsed_ms:.1f}"
        )

        return diversified

    # ======================================================
    # SEMANTIC SEARCH
    # ======================================================

    async def _semantic_search(
        self,
        session: AsyncSession,
        query_embedding: list[float],
        limit: int,
    ):
        """
        Find chunks using pgvector cosine similarity.
        """

        distance = Chunk.embedding.cosine_distance(
            query_embedding
        )

        semantic_score = (
            (1 - distance)
            .cast(Float)
            .label("semantic_score")
        )

        statement = (
            select(
                Chunk,
                Document,
                semantic_score,
            )
            .join(
                Document,
                Chunk.document_id
                == Document.id,
            )
            .where(
                Chunk.embedding.is_not(None)
            )
            .order_by(distance)
            .limit(limit)
        )

        result = await session.execute(
            statement
        )

        return result.all()

    # ======================================================
    # KEYWORD SEARCH
    # ======================================================

    async def _keyword_search(
        self,
        session: AsyncSession,
        query: str,
        limit: int,
    ):
        """
        PostgreSQL full-text keyword search.

        websearch_to_tsquery makes natural-language
        queries such as:

            product market fit

        work naturally.
        """

        ts_query = func.websearch_to_tsquery(
            "english",
            query,
        )

        document_text = func.to_tsvector(
            "english",
            Chunk.content,
        )

        keyword_score = func.ts_rank_cd(
            document_text,
            ts_query,
        ).label("keyword_score")

        statement = (
            select(
                Chunk,
                Document,
                keyword_score,
            )
            .join(
                Document,
                Chunk.document_id
                == Document.id,
            )
            .where(
                document_text.op("@@")(
                    ts_query
                )
            )
            .order_by(
                keyword_score.desc()
            )
            .limit(limit)
        )

        result = await session.execute(
            statement
        )

        return result.all()

    # ======================================================
    # SCORE COMBINATION
    # ======================================================

    def _combine_results(
        self,
        semantic_results,
        keyword_results,
    ) -> dict[str, RetrievedEvidence]:
        """
        Combine semantic and keyword retrieval.

        Final score:

            70% semantic
            30% keyword
        """

        combined: dict[
            str,
            RetrievedEvidence
        ] = {}

        semantic_scores = (
            self._normalize_scores(
                [
                    float(row[2])
                    for row in semantic_results
                ]
            )
        )

        keyword_scores = (
            self._normalize_scores(
                [
                    float(row[2])
                    for row in keyword_results
                ]
            )
        )

        # --------------------------------------------------
        # Add semantic results
        # --------------------------------------------------

        for index, row in enumerate(
            semantic_results
        ):
            chunk, document, _raw_score = row

            semantic_score = (
                semantic_scores[index]
            )

            chunk_id = str(chunk.id)

            combined[chunk_id] = (
                RetrievedEvidence(
                    chunk_id=chunk_id,
                    document_id=str(
                        document.id
                    ),
                    content=chunk.content,
                    title=document.title,
                    guest=document.guest,
                    episode=document.episode,
                    source_url=document.source_url,
                    heading=chunk.heading,
                    semantic_score=semantic_score,
                    keyword_score=0.0,
                    final_score=(
                        0.7
                        * semantic_score
                    ),
                )
            )

        # --------------------------------------------------
        # Add / merge keyword results
        # --------------------------------------------------

        for index, row in enumerate(
            keyword_results
        ):
            chunk, document, _raw_score = row

            keyword_score = (
                keyword_scores[index]
            )

            chunk_id = str(chunk.id)

            if chunk_id in combined:
                evidence = combined[
                    chunk_id
                ]

                evidence.keyword_score = (
                    keyword_score
                )

                evidence.final_score = (
                    0.7
                    * evidence.semantic_score
                    + 0.3
                    * evidence.keyword_score
                )

            else:
                combined[chunk_id] = (
                    RetrievedEvidence(
                        chunk_id=chunk_id,
                        document_id=str(
                            document.id
                        ),
                        content=chunk.content,
                        title=document.title,
                        guest=document.guest,
                        episode=document.episode,
                        source_url=document.source_url,
                        heading=chunk.heading,
                        semantic_score=0.0,
                        keyword_score=keyword_score,
                        final_score=(
                            0.3
                            * keyword_score
                        ),
                    )
                )

        return combined

    # ======================================================
    # RESULT DIVERSIFICATION
    # ======================================================

    @staticmethod
    def _diversify_results(
        results: list[RetrievedEvidence],
        limit: int,
    ) -> list[RetrievedEvidence]:
        """
        Prefer evidence from different episodes.

        This prevents one episode from consuming most
        of the evidence context.

        Example:

            Todd Jackson
            Todd Jackson
            Todd Jackson
            Karri Saarinen
            Rahul Vohra

        becomes more like:

            Todd Jackson
            Karri Saarinen
            Rahul Vohra
            ...
        """

        diversified: list[
            RetrievedEvidence
        ] = []

        seen_episodes: set[str] = set()

        # --------------------------------------------------
        # First pass:
        # one result per episode
        # --------------------------------------------------

        for result in results:

            episode_key = (
                result.episode
                or result.document_id
            )

            if episode_key in seen_episodes:
                continue

            diversified.append(result)

            seen_episodes.add(
                episode_key
            )

            if len(diversified) >= limit:
                break

        # --------------------------------------------------
        # Second pass:
        # fill remaining slots with highest scores
        # --------------------------------------------------

        if len(diversified) < limit:

            selected_ids = {
                result.chunk_id
                for result in diversified
            }

            for result in results:

                if (
                    result.chunk_id
                    in selected_ids
                ):
                    continue

                diversified.append(result)

                if len(diversified) >= limit:
                    break

        return diversified

    # ======================================================
    # SCORE NORMALIZATION
    # ======================================================

    @staticmethod
    def _normalize_scores(
        scores: list[float],
    ) -> list[float]:
        """
        Normalize scores to the range 0..1.
        """

        if not scores:
            return []

        maximum = max(scores)

        if maximum <= 0:
            return [
                0.0
                for _ in scores
            ]

        return [
            score / maximum
            for score in scores
        ]