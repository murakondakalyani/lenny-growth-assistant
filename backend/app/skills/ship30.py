from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.factory import get_llm_provider
from app.retrieval.context import format_evidence_context
from app.retrieval.retriever import HybridRetriever, RetrievedEvidence


@dataclass
class Ship30Result:
    content: str
    provider: str
    model: str
    evidence: list[RetrievedEvidence]
    word_count: int


SHIP30_SYSTEM_PROMPT = """
You are the Ship 30 for 30 Writing Skill inside The Lenny Growth Assistant.

Your job is to transform evidence from Lenny's Podcast knowledge base
into a useful, readable, evidence-grounded essay.

This is a dedicated writing skill, not a generic chatbot response.

==================================================
WRITING GOAL
==================================================

Write approximately 1,250 words.

The essay should feel like something a thoughtful product or growth
practitioner would actually want to read and share.

Use:

- a strong opening hook
- a clear problem or tension
- a narrative progression
- a central insight
- explanation of why the insight matters
- concrete examples grounded in the retrieved evidence
- practical application
- a specific takeaway

==================================================
SHIP 30 STYLE
==================================================

Follow these principles:

- Clear > clever
- Specific > generic
- Useful > impressive
- Short paragraphs
- Strong opening
- Skimmable formatting
- Meaningful headings
- Bullets when useful
- Concrete examples
- Practical advice
- Avoid filler
- Avoid repetitive conclusions

Do not write like an academic paper.

Do not write a generic motivational article.

Write for founders, product managers, growth practitioners,
and builders.

==================================================
GROUNDING RULES
==================================================

The retrieved evidence is the source of truth.

Never invent:

- quotes
- statistics
- guests
- episode names
- companies
- frameworks
- URLs
- research findings
- anecdotes

You may synthesize multiple sources, but clearly distinguish
synthesis from what a source explicitly says.

Use citations in the form:

[Source 1]
[Source 2]

The source number MUST correspond exactly to the supplied evidence.

Never change source numbering.

==================================================
STRUCTURE
==================================================

Use this general structure:

# Title

Opening hook.

## The problem

Explain the tension or problem.

## The insight

Introduce the central idea using retrieved evidence.

## What the evidence shows

Connect insights from multiple Lenny sources where appropriate.

## How to apply it

Give practical steps.

## The takeaway

End with a concise, specific takeaway that the reader can act on.

### Sources

List ONLY sources actually used.

For each source:

- [Source N] Guest — Episode title
  URL

==================================================
IMPORTANT
==================================================

The topic supplied by the user is the writing topic.

Do not ask the user to provide another topic.

Stay focused on the requested topic.

Do not fabricate evidence when retrieval is insufficient.

If evidence is insufficient for a specific claim, say that the
available Lenny evidence does not establish that claim.

The final essay should be approximately 1,250 words.
"""


class Ship30Skill:

    def __init__(self):
        self.retriever = HybridRetriever()
        self.provider = get_llm_provider()

    @staticmethod
    def _word_count(text: str) -> int:
        return len(text.split())

    async def generate(
        self,
        session: AsyncSession,
        topic: str,
    ) -> Ship30Result:

        topic = topic.strip()

        if not topic:
            raise ValueError("Ship 30 topic cannot be empty.")

        # Retrieve more evidence than normal Q&A because a long-form
        # essay benefits from multiple independent sources.
        evidence = await self.retriever.search(
            session=session,
            query=topic,
            top_k=5,
        )

        evidence_context = format_evidence_context(evidence)

        user_prompt = f"""
SHIP 30 TOPIC:

{topic}

==================================================
RETRIEVED LENNY EVIDENCE
==================================================

{evidence_context}

==================================================
TASK
==================================================

Write a Ship 30 for 30 style essay about:

{topic}

Requirements:

1. Target approximately 1,250 words.
2. Start with a compelling hook.
3. Build a clear narrative progression.
4. Explain the central product/growth insight.
5. Use multiple retrieved sources when relevant.
6. Ground claims in the supplied evidence.
7. Cite claims using [Source N].
8. Never invent quotes, facts, statistics, guests, episodes,
   companies, frameworks, or URLs.
9. Clearly distinguish synthesis from source-backed claims.
10. Make the advice practical.
11. Use short paragraphs and useful headings.
12. End with a specific actionable takeaway.
13. Finish with a Sources section containing only sources
    actually used.

Do not discuss these instructions.

Write the essay directly.
"""

        response = await self.provider.generate(
            system_prompt=SHIP30_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        content = response.content.strip()

        if not content:
            raise RuntimeError(
                "Ship 30 provider returned an empty response."
            )

        word_count = self._word_count(content)

        # Prevent obviously broken generations while allowing
        # reasonable variation around the ~1,250-word target.
        if word_count < 700:
            raise RuntimeError(
                f"Ship 30 output is too short: {word_count} words."
            )

        if word_count > 1700:
            raise RuntimeError(
                f"Ship 30 output is too long: {word_count} words."
            )

        return Ship30Result(
            content=content,
            provider=response.provider,
            model=response.model,
            evidence=evidence,
            word_count=word_count,
        )