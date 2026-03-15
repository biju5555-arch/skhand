"""Blend elements across traditions into creative synthesis."""

from __future__ import annotations

import json

from skhand.muse.corpus import get_category, get_corpus
from skhand.muse.prompts import SYSTEM_PROMPT, _build_context, _call_claude


def _resolve_element(element: dict) -> dict | None:
    """Resolve an element reference to its actual data."""
    category = element.get("category", "")
    elem_id = element.get("id", "")
    tradition = element.get("tradition", "")

    data = get_category(category)
    if not isinstance(data, list):
        return {"category": category, "id": elem_id, "tradition": tradition, "data": str(data)[:200]}

    for item in data:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("id") or item.get("concept", "")
        if elem_id.lower() in name.lower():
            return {
                "category": category,
                "name": name,
                "tradition": item.get("tradition", tradition),
                "summary": _extract_item_summary(item),
                "raw": item,
            }

    # Fallback: return the reference itself
    return {"category": category, "id": elem_id, "tradition": tradition}


def _extract_item_summary(item: dict) -> str:
    """Get a useful summary from an item."""
    for key in ("summary", "description", "quest", "core_principle", "definition", "goal_of_practice"):
        val = item.get(key, "")
        if val:
            return val[:400]
    return json.dumps(item, ensure_ascii=False)[:400]


async def blend_elements(req) -> dict:
    """Blend multiple mythological elements into a creative synthesis."""
    # Resolve all elements
    resolved = []
    for elem in req.elements:
        result = _resolve_element(elem)
        if result:
            resolved.append(result)

    # Build context from resolved elements
    context_parts = ["## Elements to Blend"]
    for r in resolved:
        name = r.get("name") or r.get("id", "unknown")
        tradition = r.get("tradition", "")
        summary = r.get("summary", "")
        context_parts.append(f"\n### {name} ({tradition}, category: {r.get('category', '')})")
        if summary:
            context_parts.append(summary)

    # Add broader context
    categories = list({r.get("category", "") for r in resolved if r.get("category")})
    if categories:
        context_parts.append("\n" + _build_context(categories[:3]))

    context = "\n".join(context_parts)

    user_prompt = f"""Blend these mythological elements into an original creative synthesis:

{context}

Goal: {req.goal}

Find the unexpected connections, resonances, and creative tensions between these elements.
Create something that feels inevitable in retrospect but surprising in the moment.

Return a JSON object:
{{
  "blend": {{
    "title": "evocative title for this synthesis",
    "synthesis": "3-5 paragraphs of narrative-ready prose that weaves these elements together — specific, sensory, named. This should read like the opening of a myth or the pitch for an epic.",
    "elements_used": ["element1 — how it was transformed", "element2 — what role it plays"],
    "creative_tensions": ["tension between element X and element Y that creates dramatic potential"],
    "story_potential": "2-3 sentences on where this synthesis could go as a full narrative"
  }}
}}"""

    return _call_claude(SYSTEM_PROMPT, user_prompt, quality=req.quality, max_tokens=3000)
