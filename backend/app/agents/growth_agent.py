from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.prompts import SYSTEM_PROMPT
from app.providers.factory import get_llm_provider
from app.retrieval.context import format_evidence_context
from app.retrieval.retriever import HybridRetriever, RetrievedEvidence


@dataclass
class AgentResult:
    answer: str
    provider: str
    model: str
    evidence: list[RetrievedEvidence]


class GrowthAgent:
    def __init__(self):
        self.retriever = HybridRetriever()
        self.provider = get_llm_provider()

    async def answer(
        self,
        session: AsyncSession,
        query: str,
        conversation_history=None,
    ) -> AgentResult:

        if not query or not query.strip():
            raise ValueError("Question cannot be empty.")

        # ---------------------------------------------------------
        # 1. Retrieve evidence
        # ---------------------------------------------------------

        evidence = await self.retriever.search(
            session=session,
            query=query.strip(),
            top_k=5,
        )

        evidence_context = format_evidence_context(evidence)

        # ---------------------------------------------------------
        # 2. Build conversation context
        # ---------------------------------------------------------

        history_text = ""

        if conversation_history:
            history_lines = []

            for message in conversation_history[-10:]:
                role = message.get("role", "user")
                content = message.get("content", "")

                if content and content.strip():
                    history_lines.append(
                        f"{role.upper()}: {content.strip()}"
                    )

            if history_lines:
                history_text = (
                    "\n\nCONVERSATION HISTORY:\n"
                    + "\n".join(history_lines)
                )

        # ---------------------------------------------------------
        # 3. Build explicit user prompt
        # ---------------------------------------------------------

        user_prompt = f"""
USER QUESTION:
{query.strip()}

{history_text}

RETRIEVED EVIDENCE:
{evidence_context}

TASK:

Answer the USER QUESTION above.

The question is:
"{query.strip()}"

This is a valid user question. Do NOT ask the user to provide
another question.

Use the retrieved evidence to answer it.

Requirements:
- Answer the question directly.
- Use evidence from the Lenny knowledge base.
- Cite supporting claims as [Source N].
- Never invent sources or citations.
- Never invent quotes.
- If combining multiple sources, explain the synthesis.
- Give practical takeaways where appropriate.
- If evidence is insufficient, explicitly say so.
- Do not discuss the retrieval system.

Finish with:

### Sources

Only include sources that were actually used.
"""

        # ---------------------------------------------------------
        # 4. Generate answer
        # ---------------------------------------------------------

        response = await self.provider.generate(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        return AgentResult(
            answer=response.content,
            provider=response.provider,
            model=response.model,
            evidence=evidence,
        )