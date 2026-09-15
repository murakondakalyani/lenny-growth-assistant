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
into a high-quality digital essay.

This is a dedicated writing skill. Do not answer like a normal chatbot.

WRITING OBJECTIVE

Create a useful, specific, memorable essay based on the user's topic
and the retrieved Lenny evidence.

Write for product managers, founders, growth practitioners, and startup
operators.

Prioritize:

- specificity over generic advice
- clarity over cleverness
- practical insight over abstract theory
- concrete examples over vague statements
- a strong point of view supported by evidence
- useful takeaways

STRUCTURE

Target approximately 1,250 words.

Use this progression:

1. HOOK
   Start with a strong, specific hook.

2. PROBLEM
   Establish the problem, tension, misconception, or surprising
   observation.

3. INSIGHT
   Introduce the key idea from the retrieved evidence.

4. EXPLANATION
   Explain the idea clearly.

5. EXAMPLES
   Use concrete examples from the retrieved evidence.

6. APPLICATION
   Explain what the reader should actually do.

7. TAKEAWAY
   End with a specific action the reader can apply.

Use headings and bullets when useful.

Keep paragraphs short and skimmable.

GROUNDING

Retrieved evidence is authoritative for claims about Lenny's Podcast,
guests, frameworks, experiences, companies, metrics, and advice.

Never invent:

- quotes
- statistics
- guests
- episodes
- companies
- URLs
- frameworks
- claims attributed to guests

If you use a claim from the evidence, cite it as:

[Source 1]

The source number must correspond exactly to the retrieved evidence.

Do not invent or change source numbers.

QUOTES

Prefer paraphrasing.

Only use a direct quote when the exact wording exists in the evidence.

Never fabricate a quote.

SYNTHESIS

You may combine ideas from multiple sources.

Clearly distinguish synthesis from what a specific guest said.

For example:

"Taken together, these ideas suggest..."

STYLE

Write like a thoughtful product/growth practitioner.

Avoid:

- generic motivational language
- corporate filler
- "in today's fast-paced world"
- excessive jargon
- repetitive conclusions
- empty statements

Prefer:

- short sentences
- concrete language
- useful frameworks
- specific actions
- memorable observations
- strong transitions

FINAL SECTION

End with:

## The takeaway

Then provide a specific practical takeaway.

After that include:

### Sources

List only sources actually used.

Format:

- [Source N] Guest — Episode title
  URL

QUALITY CHECK

Before finalizing, verify:

1. Is there a strong hook?
2. Does the essay have narrative progression?
3. Is it approximately 1,250 words?
4. Is it skimmable?
5. Is the takeaway specific?
6. Are Lenny-related claims grounded?
7. Are citations correct?
8. Did I invent anything?
9. Is this a useful essay rather than a generic chatbot answer?

If evidence is insufficient, say so instead of inventing support.
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

        if not topic or not topic.strip():
            raise ValueError(
                "A topic is required to create a Ship 30 essay."
            )

        topic = topic.strip()

        # ---------------------------------------------------------
        # Retrieve Lenny evidence
        # ---------------------------------------------------------

        evidence = await self.retriever.search(
            session=session,
            query=topic,
            top_k=8,
        )

        evidence_context = format_evidence_context(evidence)

        # ---------------------------------------------------------
        # Build writing prompt
        # ---------------------------------------------------------

        user_prompt = f"""
SHIP 30 TOPIC:

{topic}

RETRIEVED LENNY EVIDENCE:

{evidence_context}

TASK:

Write a Ship 30 for 30 style essay about:

"{topic}"

Target approximately 1,250 words.

The essay must:

- start with a compelling hook
- establish a clear problem or tension
- develop one central idea
- use relevant evidence from Lenny's content
- include concrete examples
- provide practical application
- remain skimmable
- end with a specific takeaway
- cite evidence using [Source N]
- include a ### Sources section

Do not fabricate facts or citations.

Do not write a generic product-management article.

Make the essay useful enough that a product manager or founder
could take action after reading it.
""".strip()

        # ---------------------------------------------------------
        # Generate essay
        # ---------------------------------------------------------

        response = await self.provider.generate(
            system_prompt=SHIP30_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        content = response.content.strip()

        if not content:
            raise RuntimeError(
                "Ship 30 skill returned an empty essay."
            )

        word_count = self._word_count(content)

        # ---------------------------------------------------------
        # Quality guard
        # ---------------------------------------------------------

        if word_count < 700:
            raise RuntimeError(
                f"Ship 30 essay is too short: {word_count} words. "
                "Expected approximately 1,250 words."
            )

        if word_count > 1700:
            raise RuntimeError(
                f"Ship 30 essay is too long: {word_count} words. "
                "Expected approximately 1,250 words."
            )

        return Ship30Result(
            content=content,
            provider=response.provider,
            model=response.model,
            evidence=evidence,
            word_count=word_count,
        )