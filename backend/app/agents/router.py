from app.agents.growth_agent import GrowthAgent


class AgentRouter:
    """
    Routes user requests to the appropriate agent/runtime.

    The first production path is ASK mode using the existing
    Ollama-backed GrowthAgent.

    Claude Agent SDK remains available as an optional cloud
    runtime and can be enabled when Anthropic credits are available.
    """

    def __init__(self):
        self.growth_agent = GrowthAgent()

    async def answer(
        self,
        session,
        query: str,
        conversation_history: list[dict] | None = None,
    ):
        return await self.growth_agent.answer(
            session=session,
            query=query,
            conversation_history=conversation_history,
        )