"""In-memory knowledge corpus loader for the Muse inspiration engine."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).parent.parent.parent / "data" / "knowledge"

# Map of corpus keys to (filename, content_key) pairs.
# content_key is the JSON key that holds the primary list/dict of entries.
_SOURCES: dict[str, tuple[str, str | None]] = {
    "heroes": ("hero_epics_global.json", "heroes"),
    "creation_myths": ("creation_myths_universal.json", "myths"),
    "creation_taxonomy": ("creation_myths_universal.json", "taxonomy"),
    "hero_journey": ("hero_journey_parallels.json", "stages"),
    "hero_journey_heroes": ("hero_journey_parallels.json", "hero_mappings"),
    "pantheon": ("indo_european_pantheon.json", "deity_mappings"),
    "cosmic_cycles": ("cosmic_cycles_global.json", "systems"),
    "eschatology": ("ragnarok_pralaya.json", "cycles"),
    "mystical": ("mystical_traditions.json", "traditions"),
    "afterlife": ("egypt_afterlife.json", "entries"),
    "ethics": ("ethics_across_traditions.json", "frameworks"),
    "floods": ("flood_narratives.json", "narratives"),
    "flood_motifs": ("flood_narratives.json", "common_motifs"),
    "mesopotamian": ("mesopotamian_creation.json", "parallels"),
    "axial_age": ("axial_age_parallel.json", "thinkers"),
    "absolute": ("tao_brahman.json", "concepts"),
    "philosophy": ("greek_philosophy_darshana.json", "comparisons"),
    "neoplatonism": ("neoplatonism_vedanta.json", "comparisons"),
    "master_index": ("story_of_humanity.json", "universal_threads"),
    "meta_narratives": ("story_of_humanity.json", "meta_narratives"),
}

# Cache raw file loads to avoid re-reading the same file for multiple keys
_file_cache: dict[str, dict] = {}


def _load_file(filename: str) -> dict:
    """Load and cache a single JSON file."""
    if filename not in _file_cache:
        path = KNOWLEDGE_DIR / filename
        if path.exists():
            _file_cache[filename] = json.loads(path.read_text(encoding="utf-8"))
        else:
            _file_cache[filename] = {}
    return _file_cache[filename]


@lru_cache(maxsize=1)
def get_corpus() -> dict[str, list | dict]:
    """Load all 16 knowledge JSONs into memory. Cached after first call."""
    corpus: dict[str, list | dict] = {}
    for key, (filename, content_key) in _SOURCES.items():
        raw = _load_file(filename)
        if content_key and content_key in raw:
            corpus[key] = raw[content_key]
        else:
            corpus[key] = raw
    return corpus


def get_category(name: str) -> list | dict:
    """Get a single corpus category by key."""
    return get_corpus().get(name, [])


def get_hero(name: str) -> dict | None:
    """Find a hero by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for hero in get_category("heroes"):
        if name_lower in hero.get("name", "").lower():
            return hero
    return None


def get_creation_myth(myth_id: str) -> dict | None:
    """Find a creation myth by its id."""
    for myth in get_category("creation_myths"):
        if myth.get("id") == myth_id:
            return myth
    return None


def search_corpus(query: str, category: str | None = None, tradition: str | None = None) -> list[dict]:
    """Simple text search across the corpus. Returns matching entries with context."""
    query_lower = query.lower()
    results = []
    corpus = get_corpus()

    categories = [category] if category and category in corpus else list(corpus.keys())

    for cat_key in categories:
        data = corpus[cat_key]
        if not isinstance(data, list):
            continue
        for item in data:
            if not isinstance(item, dict):
                continue
            # Filter by tradition if specified
            if tradition:
                item_tradition = item.get("tradition", "")
                if tradition.lower() not in item_tradition.lower():
                    continue
            # Search all string values
            text = json.dumps(item, ensure_ascii=False).lower()
            if query_lower in text:
                results.append({
                    "category": cat_key,
                    "name": item.get("name") or item.get("id") or item.get("concept", ""),
                    "tradition": item.get("tradition", ""),
                    "summary": _extract_summary(item),
                    "item": item,
                })
    return results[:20]


def _extract_summary(item: dict) -> str:
    """Extract a short summary from an item."""
    for key in ("summary", "description", "core_principle", "definition", "quest", "goal_of_practice"):
        val = item.get(key, "")
        if val:
            return val[:300] + ("..." if len(val) > 300 else "")
    return ""


def get_all_traditions() -> list[str]:
    """Collect all unique tradition names across the corpus."""
    traditions = set()
    corpus = get_corpus()
    for data in corpus.values():
        if not isinstance(data, list):
            continue
        for item in data:
            if isinstance(item, dict) and "tradition" in item:
                traditions.add(item["tradition"])
    return sorted(traditions)


def get_category_counts() -> dict[str, int]:
    """Return the count of items per category."""
    counts = {}
    corpus = get_corpus()
    for key, data in corpus.items():
        if isinstance(data, list):
            counts[key] = len(data)
        elif isinstance(data, dict):
            counts[key] = len(data)
    return counts
