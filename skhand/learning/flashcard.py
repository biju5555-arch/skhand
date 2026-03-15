"""Flashcard generation via Claude."""

from __future__ import annotations

import json

import anthropic

from skhand.config import get_settings
from skhand.learning.store import Flashcard, save_cards
from skhand.prompts.synthesis import FLASHCARD_PROMPT
from skhand.utils.display import console


def generate_flashcards(
    question: str,
    answer: str,
    count: int = 4,
    save: bool = True,
) -> list[Flashcard]:
    """Generate flashcards from a Q&A pair using Claude.

    Args:
        question: The original question
        answer: The synthesized answer (all three sections combined)
        count: Number of flashcards to generate
        save: Whether to persist to SQLite

    Returns:
        List of generated Flashcard objects.
    """
    settings = get_settings()

    if not settings.anthropic_api_key:
        console.print("[error]API key required for flashcard generation[/error]")
        return []

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    prompt = FLASHCARD_PROMPT.format(count=count, question=question, answer=answer)

    response = client.messages.create(
        model=settings.claude_fast_model,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    try:
        cards_data = json.loads(response.content[0].text)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        text = response.content[0].text
        start = text.find("[")
        end = text.rfind("]") + 1
        if start >= 0 and end > start:
            try:
                cards_data = json.loads(text[start:end])
            except json.JSONDecodeError:
                console.print("[warning]Failed to parse flashcard response[/warning]")
                return []
        else:
            console.print("[warning]No JSON array found in response[/warning]")
            return []

    cards = []
    for item in cards_data:
        card = Flashcard(
            front=item.get("front", ""),
            back=item.get("back", ""),
            source_question=question,
        )
        if card.front and card.back:
            cards.append(card)

    if save and cards:
        ids = save_cards(cards, source_question=question)
        for card, card_id in zip(cards, ids):
            card.id = card_id
        console.print(f"[success]Generated and saved {len(cards)} flashcards[/success]")
    elif cards:
        console.print(f"[success]Generated {len(cards)} flashcards[/success]")

    return cards
