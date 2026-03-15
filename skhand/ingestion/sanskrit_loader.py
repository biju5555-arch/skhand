"""Parse Charaka Samhita JSON and DCS Sanskrit texts."""

from __future__ import annotations

import json
from pathlib import Path

from skhand.config import get_settings
from skhand.ingestion.chunker import Chunk, chunk_sanskrit_verses
from skhand.utils.display import console


def load_charaka_samhita(data_dir: Path | None = None) -> list[Chunk]:
    """Load Charaka Samhita from JSON dataset.

    Expected structure (from gita/Datasets):
    data/sanskrit/charaka-samhita/
      ├── sutrasthana.json
      ├── nidanasthana.json
      └── ...

    Each JSON file contains an array of verse objects with:
    - text (Sanskrit)
    - translation (English)
    - chapter
    - verse_num
    """
    settings = get_settings()
    data_dir = data_dir or settings.sanskrit_data_dir / "charaka-samhita"

    if not data_dir.exists():
        console.print(f"[warning]Data directory not found: {data_dir}[/warning]")
        console.print("[meta]Run: skhand ingest download to fetch datasets[/meta]")
        return []

    all_chunks = []

    for json_file in sorted(data_dir.glob("*.json")):
        sthana = json_file.stem
        console.print(f"[meta]Loading {sthana}...[/meta]")

        with open(json_file, encoding="utf-8") as f:
            data = json.load(f)

        # Handle different JSON structures
        verses = _extract_verses(data, sthana)
        chunks = chunk_sanskrit_verses(verses, source="charaka_samhita")
        all_chunks.extend(chunks)

    console.print(f"[success]Loaded {len(all_chunks)} chunks from Charaka Samhita[/success]")
    return all_chunks


def _extract_verses(data: dict | list, sthana: str) -> list[dict]:
    """Extract verse dicts from various JSON structures."""
    verses = []

    if isinstance(data, list):
        # Flat list of verses
        for item in data:
            verses.append(_normalize_verse(item, sthana))
    elif isinstance(data, dict):
        # Could be nested by chapter
        if "chapters" in data:
            for ch_num, chapter in enumerate(data["chapters"], 1):
                chapter_verses = chapter.get("verses", chapter.get("shlokas", []))
                for v in chapter_verses:
                    v["chapter"] = ch_num
                    verses.append(_normalize_verse(v, sthana))
        elif "verses" in data:
            for v in data["verses"]:
                verses.append(_normalize_verse(v, sthana))
        else:
            # Try treating keys as chapters
            for key, value in data.items():
                if isinstance(value, list):
                    for v in value:
                        if isinstance(v, dict):
                            v.setdefault("chapter", key)
                            verses.append(_normalize_verse(v, sthana))

    return verses


def _normalize_verse(verse: dict, sthana: str) -> dict:
    """Normalize a verse dict to standard format."""
    return {
        "text": verse.get("text", verse.get("sanskrit", verse.get("shloka", ""))),
        "translation": verse.get("translation", verse.get("meaning", verse.get("english", ""))),
        "sthana": sthana,
        "chapter": verse.get("chapter", verse.get("adhyaya", "")),
        "verse_num": verse.get("verse_num", verse.get("number", verse.get("shloka_num", ""))),
    }


def load_dcs_texts(data_dir: Path | None = None) -> list[Chunk]:
    """Load texts from Digital Corpus of Sanskrit (CoNLL-U format).

    DCS files are in CoNLL-U format with morphological analysis.
    We extract the sentence text and metadata.
    """
    settings = get_settings()
    data_dir = data_dir or settings.sanskrit_data_dir / "dcs"

    if not data_dir.exists():
        console.print(f"[warning]DCS directory not found: {data_dir}[/warning]")
        return []

    all_chunks = []

    for conllu_file in sorted(data_dir.glob("**/*.conllu")):
        sentences = _parse_conllu(conllu_file)
        source_name = conllu_file.stem

        # Group sentences into chunks of ~5
        group = []
        for sent in sentences:
            group.append(sent)
            if len(group) >= 5:
                text = "\n".join(group)
                all_chunks.append(
                    Chunk(
                        text=text,
                        metadata={
                            "source": f"dcs_{source_name}",
                            "type": "dcs_text",
                        },
                    )
                )
                group = []

        if group:
            all_chunks.append(
                Chunk(
                    text="\n".join(group),
                    metadata={"source": f"dcs_{source_name}", "type": "dcs_text"},
                )
            )

    console.print(f"[success]Loaded {len(all_chunks)} chunks from DCS[/success]")
    return all_chunks


def _parse_conllu(filepath: Path) -> list[str]:
    """Extract sentence texts from CoNLL-U file."""
    sentences = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("# text = "):
                sentences.append(line[9:])
    return sentences
