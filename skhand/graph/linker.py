"""Map Sanskrit concepts to modern equivalents using Claude + graph."""

from __future__ import annotations

import json

import anthropic

from skhand.config import get_settings
from skhand.graph.builder import create_node, create_relationship
from skhand.graph.schema import CONCEPT, EQUIVALENT_TO, SUBSTANCE
from skhand.utils.display import console


LINKER_PROMPT = """\
You are an expert in both Ayurvedic Rasa Shastra and modern chemistry/nanotechnology.

Given the following Sanskrit/Ayurvedic concept, identify its modern scientific equivalent(s).

Concept: {concept}
Context: {context}

Return a JSON object with:
{{
    "sanskrit_term": "the original term",
    "sanskrit_meaning": "meaning in English",
    "modern_equivalents": [
        {{
            "name": "modern term",
            "domain": "chemistry/biology/pharmacology",
            "confidence": 0.0-1.0,
            "evidence": "brief explanation of why this mapping is valid"
        }}
    ]
}}

Return ONLY valid JSON.
"""


def find_modern_equivalent(concept: str, context: str = "") -> dict | None:
    """Use Claude to find modern equivalents for a Sanskrit concept."""
    settings = get_settings()

    if not settings.anthropic_api_key:
        console.print("[error]API key required for concept linking[/error]")
        return None

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model=settings.claude_fast_model,
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": LINKER_PROMPT.format(concept=concept, context=context),
            }
        ],
    )

    try:
        result = json.loads(response.content[0].text)
        return result
    except json.JSONDecodeError:
        console.print("[warning]Failed to parse linker response[/warning]")
        return None


def link_and_store(concept: str, context: str = ""):
    """Find modern equivalents and store them in the graph."""
    result = find_modern_equivalent(concept, context)
    if not result:
        return

    sanskrit_name = result.get("sanskrit_term", concept)

    # Create Sanskrit node
    create_node(
        CONCEPT,
        sanskrit_name,
        {"domain": "ayurveda", "meaning": result.get("sanskrit_meaning", "")},
    )

    # Create modern equivalents and link
    for equiv in result.get("modern_equivalents", []):
        modern_name = equiv["name"]
        create_node(
            SUBSTANCE if equiv.get("domain") == "chemistry" else CONCEPT,
            modern_name,
            {"domain": "modern"},
        )
        create_relationship(
            CONCEPT, sanskrit_name,
            SUBSTANCE if equiv.get("domain") == "chemistry" else CONCEPT, modern_name,
            EQUIVALENT_TO,
            {"confidence": equiv.get("confidence", 0.5), "evidence": equiv.get("evidence", "")},
        )

    console.print(
        f"[success]Linked '{sanskrit_name}' to "
        f"{len(result.get('modern_equivalents', []))} modern concept(s)[/success]"
    )
