"""Claude prompts for creative generation in the Writer's Muse."""

from __future__ import annotations

import json
from typing import Any

import anthropic

from skhand.config import get_settings
from skhand.muse.corpus import get_category, search_corpus

SYSTEM_PROMPT = """You are the Writer's Muse — a creative collaborator who draws on the deep well of world mythology, comparative religion, and cross-cultural philosophy to inspire fiction writers, game designers, and storytellers.

Your style:
- Specific and sensory, never encyclopedic or academic
- Bold in blending traditions — find unexpected resonances between cultures
- Give everything a name — places, artifacts, titles, epithets
- Include tensions and contradictions — the best stories live in paradox
- Write narrative-ready prose that a writer can directly use or riff on
- Always output valid JSON matching the requested schema

You have deep knowledge of: Vedic/Hindu mythology, Greek mythology, Norse mythology, Egyptian mythology, Mesopotamian mythology, Chinese mythology, Japanese mythology, Celtic mythology, West African oral traditions, Mesoamerican mythology, Buddhist cosmology, Sufi mysticism, Kabbalah, Neoplatonism, and comparative philosophy."""


def _get_client_and_model(quality: str = "fast") -> tuple[anthropic.Anthropic, str]:
    """Get Claude client and appropriate model based on quality setting."""
    settings = get_settings()
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    model = settings.claude_fast_model if quality == "fast" else settings.claude_model
    return client, model


def _build_context(categories: list[str], query: str = "") -> str:
    """Build context from corpus entries and optionally ChromaDB."""
    parts = []
    for cat in categories:
        data = get_category(cat)
        if isinstance(data, list) and data:
            parts.append(f"## {cat.replace('_', ' ').title()}")
            for item in data[:5]:
                if isinstance(item, dict):
                    name = item.get("name") or item.get("id") or item.get("concept", "")
                    tradition = item.get("tradition", "")
                    summary = ""
                    for k in ("summary", "description", "core_principle", "definition", "quest"):
                        if item.get(k):
                            summary = item[k][:200]
                            break
                    parts.append(f"- **{name}** ({tradition}): {summary}")

    # Add ChromaDB results if query provided
    if query:
        try:
            from skhand.query.world_search import search_world_texts
            results = search_world_texts(query, n_results=3)
            if results:
                parts.append("\n## Semantic Search Results")
                for r in results:
                    parts.append(f"- {r.text[:200]} [Source: {r.metadata.get('name', 'unknown')}]")
        except Exception:
            pass

    # Add graph context if available
    if query:
        try:
            from skhand.graph.queries import get_concept_context
            graph_ctx = get_concept_context(query)
            if graph_ctx:
                parts.append(f"\n## Knowledge Graph\n{graph_ctx}")
        except Exception:
            pass

    return "\n".join(parts)


def _call_claude(system: str, user_prompt: str, quality: str = "fast", max_tokens: int = 2048) -> dict:
    """Call Claude and parse JSON response."""
    client, model = _get_client_and_model(quality)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user_prompt}],
    )
    text = response.content[0].text

    # Extract JSON from response (handle markdown code blocks)
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    result = json.loads(text.strip())
    result["_usage"] = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": model,
    }
    return result


async def generate_inspiration(req) -> dict:
    """Generate story seeds from theme + traditions."""
    context = _build_context(
        ["heroes", "creation_myths", "master_index", "mystical"],
        query=req.theme,
    )

    tradition_filter = ""
    if req.traditions:
        tradition_filter = f"\nFocus on these traditions: {', '.join(req.traditions)}"

    user_prompt = f"""Generate {req.count} story seeds inspired by the theme: "{req.theme}"
Mood: {req.mood}{tradition_filter}

Use this mythological context for inspiration:
{context}

Return a JSON object:
{{
  "seeds": [
    {{
      "title": "evocative title",
      "premise": "2-3 sentence premise with specific details, names, places",
      "traditions_used": ["tradition1", "tradition2"],
      "key_tension": "the central dramatic conflict",
      "opening_line": "a compelling first line for the story"
    }}
  ]
}}"""

    return _call_claude(SYSTEM_PROMPT, user_prompt, quality=req.quality)


async def generate_character(req) -> dict:
    """Generate a character profile from archetype + traditions."""
    context = _build_context(
        ["heroes", "pantheon", "mystical", "ethics"],
        query=req.archetype,
    )

    traits_str = f"\nDesired traits: {', '.join(req.traits)}" if req.traits else ""
    traditions_str = f"\nDraw from: {', '.join(req.traditions)}" if req.traditions else ""

    user_prompt = f"""Create a vivid, original character inspired by the archetype: "{req.archetype}"
Role: {req.role}
Era: {req.era}{traits_str}{traditions_str}

Use this mythological context:
{context}

Return a JSON object:
{{
  "character": {{
    "name": "a culturally resonant name with meaning",
    "epithet": "a title or byname (e.g., 'the Twice-Burned', 'Keeper of the Broken Seal')",
    "origin": "2-3 sentences about their birth/origin with specific mythological echoes",
    "appearance": "vivid physical description with symbolic details",
    "personality": "inner life, contradictions, what they love and fear",
    "weapon_or_tool": "their signature item with history and meaning",
    "companion": "ally, familiar, or bound spirit with their own personality",
    "inner_conflict": "the war within them — what they want vs what they need",
    "quest": "what drives them forward, the thing they must do or die trying",
    "traditions_drawn_from": ["tradition1", "tradition2"]
  }}
}}"""

    return _call_claude(SYSTEM_PROMPT, user_prompt, quality=req.quality)


async def generate_world(req) -> dict:
    """Generate a world description from multiple mythological parameters."""
    context_parts = []
    if req.creation_type:
        context_parts.append(_build_context(["creation_myths", "creation_taxonomy"]))
    if req.pantheon_traditions:
        context_parts.append(_build_context(["pantheon"]))
    if req.ethics:
        context_parts.append(_build_context(["ethics"]))
    if req.time_system:
        context_parts.append(_build_context(["cosmic_cycles"]))
    if req.eschatology:
        context_parts.append(_build_context(["eschatology"]))

    context = "\n".join(context_parts)
    traditions_str = ", ".join(req.pantheon_traditions) if req.pantheon_traditions else "multiple traditions"

    user_prompt = f"""Build an original fictional world with these mythological foundations:
- Creation type: {req.creation_type}
- Pantheon traditions to draw from: {traditions_str}
- Ethical framework: {req.ethics}
- Time system: {req.time_system}
- Eschatology/end-times: {req.eschatology}

Mythological context:
{context}

Return a JSON object:
{{
  "world": {{
    "name": "evocative world name with meaning",
    "creation_story": "3-4 sentences — how this world began, with specific imagery",
    "cosmology": "how the world is structured — realms, planes, connections",
    "pantheon_summary": "the gods/powers of this world — names, domains, relationships, conflicts",
    "moral_framework": "how right and wrong work here — what is the cosmic law?",
    "time_and_fate": "how time works, whether fate is fixed or mutable, calendar/ages",
    "end_of_world": "how this world ends — or doesn't — and what comes after",
    "traditions_drawn_from": ["tradition1", "tradition2"]
  }}
}}"""

    return _call_claude(SYSTEM_PROMPT, user_prompt, quality=req.quality, max_tokens=3000)


async def generate_story_outline(req) -> dict:
    """Generate a story outline mapped to mythological patterns."""
    context = _build_context(
        ["hero_journey", "heroes", "master_index"],
        query=req.premise,
    )

    traditions_str = f"\nDraw patterns from: {', '.join(req.traditions)}" if req.traditions else ""

    user_prompt = f"""Create a story outline based on this premise: "{req.premise}"
Structure: {req.structure} (hero's journey, three-act, five-act, or mythic cycle)
Hero type: {req.hero_type}{traditions_str}

Mythological context:
{context}

Return a JSON object:
{{
  "outline": {{
    "title": "story title",
    "logline": "one-sentence pitch",
    "acts": [
      {{
        "name": "act name",
        "mythological_parallel": "which myth pattern this maps to",
        "beats": ["beat 1 — specific scene/moment", "beat 2", "beat 3"],
        "emotional_arc": "how the reader/audience should feel"
      }}
    ],
    "mythological_parallels": ["specific myth or pattern this echoes"],
    "themes": ["theme1", "theme2"],
    "key_symbols": ["symbol with meaning"]
  }}
}}"""

    return _call_claude(SYSTEM_PROMPT, user_prompt, quality=req.quality, max_tokens=3000)
