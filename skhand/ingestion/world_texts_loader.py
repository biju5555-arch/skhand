"""Load and chunk world texts from the cross-cultural corpus.

Reads JSONL files produced by acquire_world_texts.py and converts them
into Chunk objects for embedding into ChromaDB.
"""

from __future__ import annotations

import json
from pathlib import Path

from skhand.ingestion.chunker import Chunk
from skhand.utils.display import console

# Default location for processed world texts
DEFAULT_WORLD_TEXTS_DIR = Path(__file__).parent.parent.parent / "data" / "world_texts" / "processed"

# Collection name for world texts
WORLD_TEXTS_COLLECTION = "world_texts"

# Civilization display names
CIVILIZATION_NAMES = {
    "mesopotamia": "Mesopotamia",
    "egypt": "Ancient Egypt",
    "greece": "Ancient Greece",
    "norse": "Norse/Scandinavian",
    "china": "China",
    "india": "India",
    "rome": "Rome",
    "mesoamerica": "Mesoamerica",
    "japan": "Japan",
    "west_africa": "West Africa",
    "finland": "Finland",
    "israel": "Israel",
    "arabia": "Arabia",
    "persia": "Persia",
    "egypt_hellenistic": "Hellenistic Egypt",
    "spain_jewish": "Jewish Spain",
}

# Universal story thread tags based on content keywords
THREAD_KEYWORDS = {
    "creation": [
        "creation", "beginning", "cosmos", "heaven and earth", "first man",
        "chaos", "void", "primordial", "in the beginning", "cosmogony",
        "tiamat", "marduk", "genesis", "atum", "brahma",
    ],
    "flood": [
        "flood", "deluge", "waters", "ark", "utnapishtim", "noah",
        "deucalion", "manu", "inundation", "great water",
    ],
    "hero_journey": [
        "hero", "quest", "journey", "adventure", "trial", "ordeal",
        "odyssey", "gilgamesh", "arjuna", "odysseus", "sigurd", "sundiata",
    ],
    "cosmic_cycles": [
        "cycle", "age", "yuga", "kalpa", "aeon", "ragnarok", "pralaya",
        "golden age", "iron age", "five suns", "world age",
    ],
    "immortality": [
        "immortal", "eternal life", "elixir", "ambrosia", "amrita",
        "philosopher's stone", "fountain of youth", "herb of life",
    ],
    "knowledge_theft": [
        "fire", "prometheus", "knowledge", "forbidden", "tree of knowledge",
        "rune", "odin", "secret", "stolen", "gift of",
    ],
    "underworld": [
        "underworld", "death", "afterlife", "hades", "sheol", "netherworld",
        "descend", "inanna", "orpheus", "izanagi", "judgment", "osiris",
    ],
}


def detect_threads(text: str) -> list[str]:
    """Detect which universal story threads a chunk relates to."""
    text_lower = text.lower()
    threads = []
    for thread, keywords in THREAD_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                threads.append(thread)
                break
    return threads


def load_world_texts(data_dir: Path | None = None) -> list[Chunk]:
    """Load all processed world texts from JSONL files.

    Each JSONL file contains pre-chunked text with metadata from
    acquire_world_texts.py.
    """
    data_dir = data_dir or DEFAULT_WORLD_TEXTS_DIR

    if not data_dir.exists():
        console.print(f"[warning]World texts directory not found: {data_dir}[/warning]")
        console.print("[meta]Run: python3 acquire_world_texts.py[/meta]")
        return []

    all_chunks = []
    jsonl_files = sorted(data_dir.glob("**/*.jsonl"))

    if not jsonl_files:
        console.print(f"[warning]No JSONL files found in {data_dir}[/warning]")
        return []

    console.print(f"[meta]Found {len(jsonl_files)} world text files[/meta]")

    civilizations_seen = set()
    traditions_seen = set()

    for jsonl_file in jsonl_files:
        file_chunks = 0
        source_name = jsonl_file.stem

        with open(jsonl_file, encoding="utf-8") as f:
            for line_num, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                text = entry.get("text", "")
                if not text or len(text) < 50:
                    continue

                meta = entry.get("metadata", entry)

                # Build rich metadata for the chunk
                civilization = meta.get("civilization", "unknown")
                tradition = meta.get("tradition", "unknown")
                civilizations_seen.add(civilization)
                traditions_seen.add(tradition)

                # Detect universal story threads
                threads = detect_threads(text)

                chunk_meta = {
                    "source": meta.get("source", source_name),
                    "name": meta.get("name", source_name),
                    "tradition": tradition,
                    "civilization": civilization,
                    "civilization_display": CIVILIZATION_NAMES.get(civilization, civilization),
                    "era": meta.get("era", ""),
                    "language_original": meta.get("language_original", ""),
                    "type": "world_text",
                    "chunk_index": meta.get("chunk_index", line_num),
                    "universal_threads": ",".join(threads) if threads else "",
                }

                # Add optional fields
                if meta.get("book"):
                    chunk_meta["book"] = meta["book"]

                chunk = Chunk(text=text, metadata=chunk_meta)
                all_chunks.append(chunk)
                file_chunks += 1

        if file_chunks > 0:
            console.print(f"[meta]  {source_name}: {file_chunks} chunks[/meta]")

    console.print(
        f"[success]Loaded {len(all_chunks)} world text chunks "
        f"from {len(civilizations_seen)} civilizations, "
        f"{len(traditions_seen)} traditions[/success]"
    )

    return all_chunks


def load_knowledge_files(data_dir: Path | None = None) -> list[Chunk]:
    """Load structured knowledge JSON files as chunks for embedding.

    Knowledge files contain cross-cultural comparisons, timelines,
    and thematic analyses that should also be searchable.
    """
    knowledge_dir = data_dir or (Path(__file__).parent.parent.parent / "data" / "knowledge")

    if not knowledge_dir.exists():
        return []

    all_chunks = []

    for json_file in sorted(knowledge_dir.glob("*.json")):
        try:
            with open(json_file, encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue

        source_name = json_file.stem

        # Handle different knowledge file structures
        entries = []
        if isinstance(data, dict):
            if "entries" in data:
                entries = data["entries"]
            elif "threads" in data:
                entries = data["threads"]
            elif "comparisons" in data:
                entries = data["comparisons"]
            elif "narratives" in data:
                entries = data["narratives"]
            else:
                # Treat top-level keys as entries
                for key, value in data.items():
                    if isinstance(value, dict):
                        value["_key"] = key
                        entries.append(value)
                    elif isinstance(value, str) and len(value) > 50:
                        entries.append({"_key": key, "text": value})
        elif isinstance(data, list):
            entries = data

        for i, entry in enumerate(entries):
            if isinstance(entry, str):
                text = entry
            elif isinstance(entry, dict):
                # Build text from entry fields
                parts = []
                for field in ["title", "name", "_key"]:
                    if entry.get(field):
                        parts.append(entry[field])
                        break
                for field in ["description", "text", "summary", "analysis",
                              "comparison", "narrative", "content"]:
                    if entry.get(field):
                        parts.append(str(entry[field]))
                # Include tradition-specific details
                for field in ["traditions", "parallels", "sources"]:
                    if entry.get(field):
                        if isinstance(entry[field], list):
                            parts.append(", ".join(str(x) for x in entry[field]))
                        elif isinstance(entry[field], dict):
                            for k, v in entry[field].items():
                                parts.append(f"{k}: {v}")
                text = "\n".join(parts)
            else:
                continue

            if len(text) < 50:
                continue

            chunk_meta = {
                "source": f"knowledge_{source_name}",
                "name": entry.get("title", entry.get("name", source_name)) if isinstance(entry, dict) else source_name,
                "type": "knowledge_file",
                "tradition": "cross_cultural",
                "civilization": "comparative",
            }

            all_chunks.append(Chunk(text=text, metadata=chunk_meta))

    if all_chunks:
        console.print(f"[success]Loaded {len(all_chunks)} knowledge chunks[/success]")

    return all_chunks
