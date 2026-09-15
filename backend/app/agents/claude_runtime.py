from dataclasses import dataclass

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    query,
)

from app.agents.prompts import SYSTEM_PROMPT
from app.agents.tools import retrieve_knowledge
from app.core.config import get_settings


@dataclass
class ClaudeAgentResult:
    """
    Normalized result returned by the Claude Agent SDK runtime.
    """

    answer: str
    session_id: str | None
    provider: str
    model: str


def build_agent_options() -> ClaudeAgentOptions:
    """
    Build the Claude Agent SDK configuration.

    The agent receives one custom MCP tool:

        retrieve_knowledge

    This allows Claude to actively retrieve relevant evidence
    from the PostgreSQL + pgvector knowledge base.
    """

    settings = get_settings()

    if not settings.anthropic_api_key:
      raise RuntimeError(
        "ANTHROPIC_API_KEY is not configured. "
        "Add it to your local .env file before using Claude."
      )

    # ---------------------------------------------------------
    # Create the in-process MCP server.
    # ---------------------------------------------------------

    lenny_server = create_sdk_mcp_server(
        name="lenny_knowledge",
        version="1.0.0",
        tools=[
            retrieve_knowledge,
        ],
    )

    # ---------------------------------------------------------
    # Configure Claude Agent SDK.
    # ---------------------------------------------------------

    return ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,

        mcp_servers={
            "lenny": lenny_server,
        },

        # Allow Claude to use our custom retrieval tool.
        allowed_tools=[
            "mcp__lenny__retrieve_knowledge",
        ],

        # This is appropriate for our controlled local
        # development agent where the only allowed tool is
        # our read-only knowledge retrieval tool.
        permission_mode="bypassPermissions",

        # Prevent runaway agent loops.
        max_turns=5,

        # Use the model configured in .env.
        model=settings.anthropic_model,

        # Working directory for the Claude Agent process.
        cwd=".",

        # Explicitly provide the Anthropic API key to the
        # Agent SDK process.
        env={
            "ANTHROPIC_API_KEY": settings.anthropic_api_key,
        },
    )


def build_agent_prompt(
    user_question: str,
    conversation_history: list[dict] | None = None,
) -> str:
    """
    Construct the prompt sent to the Claude Agent.

    Conversation history is supplied by our application database,
    allowing sessions to remain independent and persistent.
    """

    question = user_question.strip()

    if not question:
        raise ValueError("Question cannot be empty.")

    history_text = ""

    if conversation_history:
        history_lines: list[str] = []

        for message in conversation_history[-10:]:
            role = str(message.get("role", "user")).upper()
            content = str(message.get("content", "")).strip()

            if not content:
                continue

            history_lines.append(
                f"{role}: {content}"
            )

        if history_lines:
            history_text = (
                "\n\n"
                "CONVERSATION HISTORY:\n"
                "---------------------\n"
                + "\n".join(history_lines)
            )

    return f"""
USER QUESTION:
{question}

{history_text}

INSTRUCTIONS:

Answer the USER QUESTION above directly.

The text after USER QUESTION is the actual user question.
Do NOT claim that the user has failed to provide a question.

Use the `retrieve_knowledge` tool when information from Lenny's
knowledge base is needed.

When answering questions about Lenny's Podcast, guests, frameworks,
experiences, product strategy, growth, or advice:

1. Retrieve relevant evidence first.
2. Base claims on the retrieved evidence.
3. Cite evidence using [Source N].
4. Only use source numbers returned by the retrieval tool.
5. Never invent citations.
6. Never invent quotes, statistics, guests, episodes, or URLs.
7. If multiple sources support the answer, synthesize them clearly.
8. Clearly distinguish your own synthesis from a guest's claims.
9. If the knowledge base does not contain enough evidence, say so.

Give the user a useful, practical answer.

Do not explain the internal agent process unless the user asks.
""".strip()


async def run_claude_agent(
    user_question: str,
    conversation_history: list[dict] | None = None,
) -> ClaudeAgentResult:
    """
    Run the Claude Agent SDK.

    Claude can call the custom `retrieve_knowledge` MCP tool,
    receive evidence from PostgreSQL/pgvector, and then produce
    a grounded answer.
    """

    settings = get_settings()

    if not settings.anthropic_api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not configured. "
            "Add it to your .env file before using Claude."
        )

    prompt = build_agent_prompt(
        user_question=user_question,
        conversation_history=conversation_history,
    )

    options = build_agent_options()

    answer_parts: list[str] = []
    session_id: str | None = None

    try:
        async for message in query(
            prompt=prompt,
            options=options,
        ):

            # -------------------------------------------------
            # Claude assistant response.
            # -------------------------------------------------

            if isinstance(message, AssistantMessage):

                content = message.content

                if not isinstance(content, list):
                    continue

                for block in content:

                    if isinstance(block, TextBlock):
                        text = block.text.strip()

                        if text:
                            answer_parts.append(text)

            # -------------------------------------------------
            # Final SDK result.
            # -------------------------------------------------

            elif isinstance(message, ResultMessage):

                session_id = getattr(
                    message,
                    "session_id",
                    None,
                )

    except Exception as exc:
        raise RuntimeError(
            f"Claude Agent SDK execution failed: {exc}"
        ) from exc

    # ---------------------------------------------------------
    # Normalize final response.
    # ---------------------------------------------------------

    answer = "\n".join(
        part for part in answer_parts if part.strip()
    ).strip()

    if not answer:
        raise RuntimeError(
            "Claude Agent SDK returned an empty response."
        )

    return ClaudeAgentResult(
        answer=answer,
        session_id=session_id,
        provider="anthropic",
        model=settings.anthropic_model or "default",
    )