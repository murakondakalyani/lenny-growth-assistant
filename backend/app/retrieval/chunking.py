from dataclasses import dataclass


@dataclass
class TextChunk:
    index: int
    content: str
    heading: str | None = None


def split_into_chunks(
    text: str,
    max_words: int = 800,
    overlap_words: int = 120,
) -> list[TextChunk]:

    if not text.strip():
        return []

    # Only real Markdown headings are treated as sections.
    # Speaker lines such as "Guest (00:12:34):" are NOT headings.
    sections = []
    current_heading = None
    current_lines = []

    for line in text.splitlines():
        stripped = line.strip()

        if not stripped:
            continue

        if stripped.startswith("#"):
            if current_lines:
                sections.append((current_heading, current_lines))
                current_lines = []

            current_heading = stripped.lstrip("#").strip()
        else:
            current_lines.append(stripped)

    if current_lines:
        sections.append((current_heading, current_lines))

    chunks = []

    for heading, section_lines in sections:
        words = " ".join(section_lines).split()

        if not words:
            continue

        start = 0

        while start < len(words):
            end = min(start + max_words, len(words))

            chunk_words = words[start:end]

            content = " ".join(chunk_words)

            if heading:
                content = f"Section: {heading}\n\n{content}"

            chunks.append(
                TextChunk(
                    index=len(chunks),
                    content=content,
                    heading=heading,
                )
            )

            if end >= len(words):
                break

            next_start = end - overlap_words

            if next_start <= start:
                next_start = end

            start = next_start

    return chunks