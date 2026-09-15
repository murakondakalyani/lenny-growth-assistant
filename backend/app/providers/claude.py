from anthropic import AsyncAnthropic

from app.core.config import get_settings
from app.providers.base import LLMResponse


class ClaudeProvider:
    def __init__(self):
        settings = get_settings()

        if not settings.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not configured."
            )

        if not settings.anthropic_model:
            raise RuntimeError(
                "ANTHROPIC_MODEL is not configured."
            )

        self.client = AsyncAnthropic(
            api_key=settings.anthropic_api_key
        )

        self.model = settings.anthropic_model

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    }
                ],
            )

        except Exception as exc:
            raise RuntimeError(
                f"Claude generation failed: {exc}"
            ) from exc

        content_parts = []

        for block in response.content:

            if getattr(
                block,
                "type",
                None,
            ) == "text":

                content_parts.append(
                    block.text
                )

        content = "\n".join(
            content_parts
        ).strip()

        if not content:
            raise RuntimeError(
                "Claude returned an empty response."
            )

        return LLMResponse(
            content=content,
            provider="claude",
            model=self.model,
        )