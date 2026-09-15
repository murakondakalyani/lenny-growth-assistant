import httpx

from app.core.config import get_settings
from app.providers.base import LLMResponse


class OllamaProvider:

    def __init__(self):
        settings = get_settings()

        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_model

        if not self.model:
            raise RuntimeError(
                "OLLAMA_MODEL is not configured."
            )

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:

        payload = {
            "model": self.model,
            "system": system_prompt,
            "prompt": user_prompt,
            "stream": False,
            "options": {
                "temperature": 0.4,
            },
        }

        # Long-form Ship 30 generation can take several minutes
        # on a local 4B model.
        timeout = httpx.Timeout(
            connect=10.0,
            read=600.0,
            write=30.0,
            pool=30.0,
        )

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:

                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )

                response.raise_for_status()

                data = response.json()

                content = data.get("response", "").strip()

                if not content:
                    raise RuntimeError(
                        "Ollama returned an empty response."
                    )

                return LLMResponse(
                    content=content,
                    provider="ollama",
                    model=self.model,
                )

        except httpx.TimeoutException as exc:
            raise RuntimeError(
                "Ollama generation timed out after 600 seconds. "
                "The local model may be too slow for this request."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"Ollama returned HTTP {exc.response.status_code}: "
                f"{exc.response.text[:500]}"
            ) from exc

        except httpx.RequestError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.base_url}: {exc}"
            ) from exc

        except Exception as exc:
            raise RuntimeError(
                f"Ollama generation failed: {exc}"
            ) from exc