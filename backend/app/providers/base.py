from dataclasses import dataclass
from typing import Protocol


@dataclass
class LLMResponse:
    content: str
    provider: str
    model: str


class LLMProvider(Protocol):
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> LLMResponse:
        ...