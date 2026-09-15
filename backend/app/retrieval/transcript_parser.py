from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class ParsedTranscript:
    guest: str | None
    title: str
    source_url: str | None
    video_id: str | None
    description: str | None
    content: str
    file_path: str


def parse_transcript(path: Path) -> ParsedTranscript:
    """Parse a Lenny's Podcast Markdown transcript."""

    text = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    frontmatter, content = _split_frontmatter(text)
    metadata = _parse_frontmatter(frontmatter)

    title = metadata.get("title") or _extract_title(content)

    body = _extract_transcript_body(content)

    return ParsedTranscript(
        guest=metadata.get("guest"),
        title=title.strip(),
        source_url=metadata.get("youtube_url"),
        video_id=metadata.get("video_id"),
        description=metadata.get("description"),
        content=body.strip(),
        file_path=str(path),
    )


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Split YAML frontmatter from Markdown content."""

    if not text.startswith("---"):
        return "", text

    parts = text.split("---", 2)

    if len(parts) != 3:
        return "", text

    return parts[1].strip(), parts[2].strip()


def _parse_frontmatter(frontmatter: str) -> dict[str, str]:
    """
    Parse the simple YAML frontmatter used by the Lenny transcript repository.

    Supports:
    - quoted scalar values
    - unquoted scalar values
    - multiline values using |
    """

    metadata: dict[str, str] = {}

    lines = frontmatter.splitlines()
    index = 0

    while index < len(lines):
        line = lines[index]

        if not line.strip():
            index += 1
            continue

        match = re.match(
            r"^([A-Za-z0-9_]+):\s*(.*)$",
            line,
        )

        if not match:
            index += 1
            continue

        key = match.group(1)
        value = match.group(2).strip()

        # Multiline YAML value:
        #
        # description: |
        #   line one
        #   line two
        if value == "|":
            multiline: list[str] = []
            index += 1

            while index < len(lines):
                next_line = lines[index]

                if next_line.startswith("  "):
                    multiline.append(next_line.strip())
                    index += 1
                    continue

                if not next_line.strip():
                    multiline.append("")
                    index += 1
                    continue

                break

            metadata[key] = "\n".join(multiline).strip()
            continue

        metadata[key] = _clean_value(value)

        index += 1

    return metadata


def _clean_value(value: str) -> str:
    """Remove surrounding YAML quotes."""

    if len(value) >= 2:
        if value[0] == '"' and value[-1] == '"':
            return value[1:-1]

        if value[0] == "'" and value[-1] == "'":
            return value[1:-1]

    return value


def _extract_title(content: str) -> str:
    """Extract the first Markdown H1 title."""

    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()

    return "Untitled Lenny transcript"


def _extract_transcript_body(content: str) -> str:
    """
    Extract the conversational transcript.

    Removes the Markdown title and '## Transcript' heading,
    while preserving speaker names and timestamps.
    """

    lines = content.splitlines()

    transcript_start: int | None = None

    for index, line in enumerate(lines):
        if line.strip().lower() == "## transcript":
            transcript_start = index + 1
            break

    if transcript_start is not None:
        lines = lines[transcript_start:]
    else:
        lines = [
            line
            for line in lines
            if not line.startswith("# ")
        ]

    return "\n".join(lines).strip()