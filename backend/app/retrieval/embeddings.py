from typing import Sequence

import httpx

from app.core.config import get_settings


class OllamaEmbeddingError(RuntimeError):
    """Raised when Ollama embedding generation fails."""


class OllamaEmbeddingProvider:
    def __init__(self):
        settings = get_settings()

        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_embedding_model or "nomic-embed-text"

    async def embed(self, text: str) -> list[float]:
        """Embed a single piece of text."""
        results = await self.embed_many([text])
        return results[0]

    async def embed_many(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in one Ollama request."""
        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise OllamaEmbeddingError(
                "Cannot embed empty text."
            )

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/embed",
                    json={
                        "model": self.model,
                        "input": texts,
                    },
                )

                response.raise_for_status()

        except httpx.HTTPError as exc:
            raise OllamaEmbeddingError(
                f"Ollama embedding request failed: {exc}"
            ) from exc

        data = response.json()

        embeddings: Sequence[Sequence[float]] = data.get(
            "embeddings",
            [],
        )

        if len(embeddings) != len(texts):
            raise OllamaEmbeddingError(
                f"Expected {len(texts)} embeddings, "
                f"got {len(embeddings)}."
            )

        vectors = [list(vector) for vector in embeddings]

        for vector in vectors:
            if len(vector) != 768:
                raise OllamaEmbeddingError(
                    f"Expected 768 dimensions, "
                    f"got {len(vector)}."
                )

        return vectors