"""Claude API synthesis — the intelligence layer."""

from __future__ import annotations

import anthropic

from skhand.config import get_settings
from skhand.prompts.synthesis import SYSTEM_PROMPT, build_synthesis_prompt
from skhand.query.sanskrit_search import SearchResult
from skhand.utils.display import console


def format_search_results(results: list[SearchResult]) -> str:
    """Format search results as context for Claude."""
    if not results:
        return "(No relevant sources found)"

    parts = []
    for i, r in enumerate(results, 1):
        citation = r.citation
        parts.append(f"[{i}] {citation} (relevance: {1 - r.score:.2f})")
        parts.append(r.text)
        parts.append("")
    return "\n".join(parts)


def synthesize(
    question: str,
    sanskrit_results: list[SearchResult],
    science_results: list[SearchResult],
    graph_context: str = "",
    verbose: bool = False,
) -> dict:
    """Call Claude to synthesize a three-section answer.

    Returns dict with keys: shastra, science, setu, usage.
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        console.print("[error]ANTHROPIC_API_KEY not set in .env[/error]")
        return {
            "shastra": "API key not configured.",
            "science": "",
            "setu": "",
            "usage": None,
        }

    sanskrit_context = format_search_results(sanskrit_results)
    science_context = format_search_results(science_results)

    user_prompt = build_synthesis_prompt(
        question=question,
        sanskrit_context=sanskrit_context,
        science_context=science_context,
        graph_context=graph_context,
    )

    if verbose:
        console.print(f"[meta]Sanskrit sources: {len(sanskrit_results)}[/meta]")
        console.print(f"[meta]Science sources: {len(science_results)}[/meta]")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    response = client.messages.create(
        model=settings.claude_model,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    answer_text = response.content[0].text
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "model": settings.claude_model,
    }

    if verbose:
        console.print(
            f"[meta]Tokens: {usage['input_tokens']} in / "
            f"{usage['output_tokens']} out ({usage['model']})[/meta]"
        )

    return {**_parse_sections(answer_text), "usage": usage}


def _parse_sections(text: str) -> dict:
    """Parse the three-section answer from Claude's response."""
    sections = {"shastra": "", "science": "", "setu": ""}

    current_section = None
    current_lines: list[str] = []

    for line in text.split("\n"):
        stripped = line.strip().lower()
        is_header = stripped.startswith("#")

        if is_header and "shastra" in stripped:
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = "shastra"
            current_lines = []
        elif is_header and "modern science" in stripped:
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = "science"
            current_lines = []
        elif is_header and ("setu" in stripped or "bridge" in stripped):
            if current_section:
                sections[current_section] = "\n".join(current_lines)
            current_section = "setu"
            current_lines = []
        else:
            current_lines.append(line)

    # Assign last section
    if current_section:
        sections[current_section] = "\n".join(current_lines)

    # Fallback: if parsing failed, put everything in shastra
    if not any(sections.values()):
        sections["shastra"] = text

    return {k: v.strip() for k, v in sections.items()}
