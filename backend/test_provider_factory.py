from app.providers.factory import get_llm_provider


provider = get_llm_provider()

print(
    "Provider class:",
    provider.__class__.__name__,
)

print("Provider factory OK")