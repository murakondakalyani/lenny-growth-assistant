from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.artifacts.sanitizer import sanitize_html
from app.providers.factory import get_llm_provider
from app.retrieval.context import format_evidence_context
from app.retrieval.retriever import HybridRetriever, RetrievedEvidence


@dataclass
class ArtifactResult:
    title: str
    artifact_type: str
    content_format: str
    content: str
    sanitized_content: str
    provider: str
    model: str
    evidence: list[RetrievedEvidence]


ARTIFACT_SYSTEM_PROMPT = """
You are the Artifact Studio skill inside The Lenny Growth Assistant.

Your job is to transform grounded Lenny knowledge into a useful
visual artifact.

The artifact must be complete HTML.

==================================================
SECURITY
==================================================

The HTML is untrusted generated content.

NEVER include:

- JavaScript
- <script>
- <iframe>
- <object>
- <embed>
- inline event handlers such as onclick or onload
- javascript: URLs
- external executable resources

Use HTML and CSS only.

==================================================
DESIGN
==================================================

Create a polished, professional artifact.

Use:

- semantic HTML
- clear hierarchy
- cards
- headings
- tables when useful
- concise sections
- whitespace
- readable typography
- responsive layout

The artifact should look like a real product document,
not raw generated HTML.

==================================================
GROUNDING
==================================================

Use only the supplied Lenny evidence.

Never invent:

- quotes
- statistics
- guests
- episode names
- URLs
- facts

Cite evidence as:

[Source 1]
[Source 2]

The source number must correspond exactly to the supplied evidence.

==================================================
OUTPUT
==================================================

Return ONLY complete HTML.

Do not use Markdown fences.

Do not explain the HTML.

Do not include JavaScript.
"""


class ArtifactGenerator:

    def __init__(self):
        self.retriever = HybridRetriever()
        self.provider = get_llm_provider()

    async def generate(
        self,
        session: AsyncSession,
        prompt: str,
        artifact_type: str = "decision_canvas",
    ) -> ArtifactResult:

        prompt = prompt.strip()

        if not prompt:
            raise ValueError(
                "Artifact prompt cannot be empty."
            )

        evidence = await self.retriever.search(
            session=session,
            query=prompt,
            top_k=5,
        )

        evidence_context = format_evidence_context(evidence)

        user_prompt = f"""
ARTIFACT TYPE:

{artifact_type}

USER REQUEST:

{prompt}

==================================================
RETRIEVED LENNY EVIDENCE
==================================================

{evidence_context}

==================================================
TASK
==================================================

Create a complete HTML artifact responding to the user's request.

The artifact should be useful without requiring additional explanation.

If the artifact is a decision canvas, include:

- Problem
- Evidence
- Options
- Trade-offs
- Recommendation
- Next Experiment

If another artifact type is requested, adapt the structure appropriately.

Requirements:

1. Use only the supplied evidence for Lenny-specific claims.
2. Cite claims with [Source N].
3. Never invent sources.
4. Never include JavaScript.
5. Never include iframes.
6. Never include event handlers.
7. Never include javascript: URLs.
8. Return complete HTML.
9. Include useful CSS.
10. Make the artifact visually polished.
"""

        response = await self.provider.generate(
            system_prompt=ARTIFACT_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        raw_content = response.content.strip()

        if not raw_content:
            raise RuntimeError(
                "Artifact generator returned empty content."
            )

        # Remove accidental Markdown fences if the model adds them.
        if raw_content.startswith("```html"):
            raw_content = raw_content[7:]

        if raw_content.startswith("```"):
            raw_content = raw_content[3:]

        if raw_content.endswith("```"):
            raw_content = raw_content[:-3]

        raw_content = raw_content.strip()

        sanitized = sanitize_html(raw_content)

        if not sanitized:
            raise RuntimeError(
                "Artifact sanitization produced empty content."
            )

        return ArtifactResult(
            title=self._make_title(prompt),
            artifact_type=artifact_type,
            content_format="html",
            content=raw_content,
            sanitized_content=sanitized,
            provider=response.provider,
            model=response.model,
            evidence=evidence,
        )

    @staticmethod
    def _make_title(prompt: str) -> str:
        words = prompt.split()

        if not words:
            return "Lenny Artifact"

        title = " ".join(words[:10])

        if len(words) > 10:
            title += "..."

        return title