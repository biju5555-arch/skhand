"""Text chunking for Sanskrit and scientific texts."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A chunk of text with metadata."""

    text: str
    metadata: dict = field(default_factory=dict)
    chunk_id: str = ""

    def __post_init__(self):
        if not self.chunk_id:
            # Generate from metadata
            parts = [
                self.metadata.get("source", "unknown"),
                self.metadata.get("sthana", ""),
                self.metadata.get("chapter", ""),
                self.metadata.get("verse", ""),
            ]
            self.chunk_id = "-".join(str(p) for p in parts if p)


def chunk_sanskrit_verses(
    verses: list[dict],
    source: str = "charaka_samhita",
    group_size: int = 3,
) -> list[Chunk]:
    """Chunk Sanskrit verses, grouping nearby shlokas for context.

    Each verse dict should have: text, translation (optional), sthana, chapter, verse_num.
    Groups `group_size` consecutive verses for better semantic context.
    """
    chunks = []

    for i in range(0, len(verses), group_size):
        group = verses[i : i + group_size]
        combined_text = []
        verse_range = []

        for v in group:
            sanskrit = v.get("text", "")
            translation = v.get("translation", "")
            verse_num = v.get("verse_num", "")
            verse_range.append(str(verse_num))

            if sanskrit:
                combined_text.append(f"Sanskrit: {sanskrit}")
            if translation:
                combined_text.append(f"Translation: {translation}")
            combined_text.append("")

        first = group[0]
        metadata = {
            "source": source,
            "sthana": first.get("sthana", ""),
            "chapter": first.get("chapter", ""),
            "verse": f"{verse_range[0]}-{verse_range[-1]}" if len(verse_range) > 1 else verse_range[0],
            "type": "sanskrit_verse",
        }

        chunks.append(Chunk(text="\n".join(combined_text).strip(), metadata=metadata))

    return chunks


def chunk_text_by_size(
    text: str,
    chunk_size: int = 1000,
    overlap: int = 200,
    metadata: dict | None = None,
) -> list[Chunk]:
    """Chunk plain text by character count with overlap.

    Used for scientific papers and prose sections.
    """
    if metadata is None:
        metadata = {}

    chunks = []
    start = 0
    chunk_num = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            last_period = text.rfind(".", start, end)
            last_newline = text.rfind("\n", start, end)
            break_at = max(last_period, last_newline)
            if break_at > start + chunk_size // 2:
                end = break_at + 1

        chunk_text = text[start:end].strip()
        if chunk_text:
            chunk_meta = {**metadata, "chunk_num": chunk_num}
            chunks.append(Chunk(text=chunk_text, metadata=chunk_meta))
            chunk_num += 1

        start = end - overlap

    return chunks
