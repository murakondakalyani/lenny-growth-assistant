from app.core.config import get_settings
from app.providers.claude import ClaudeProvider
from app.providers.ollama import OllamaProvider


def get_llm_provider():

    settings = get_settings()

    provider = settings.llm_provider.lower().strip()

    if provider == "ollama":
        return OllamaProvider()

    if provider == "claude":
        return ClaudeProvider()

    raise RuntimeError(
        f"Unsupported LLM provider: {provider}"
    )