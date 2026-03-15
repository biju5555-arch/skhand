"""FSRS spaced repetition scheduler."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fsrs import FSRS, Card, Rating

from skhand.learning.store import Flashcard, record_review, update_card


# Map user rating to FSRS Rating
RATING_MAP = {
    1: Rating.Again,
    2: Rating.Hard,
    3: Rating.Good,
    4: Rating.Easy,
}


def get_scheduler() -> FSRS:
    """Get an FSRS scheduler instance."""
    return FSRS()


def review_card(card: Flashcard, rating: int) -> Flashcard:
    """Process a review and update the card's scheduling state.

    Args:
        card: The flashcard being reviewed
        rating: 1=Again, 2=Hard, 3=Good, 4=Easy

    Returns:
        Updated flashcard with new due date and state.
    """
    scheduler = get_scheduler()
    fsrs_rating = RATING_MAP.get(rating, Rating.Good)

    # Reconstruct FSRS Card from stored state
    fsrs_card = Card()
    if card.fsrs_state:
        # Restore previous state if it exists
        state = card.fsrs_state
        if "stability" in state:
            fsrs_card.stability = state["stability"]
        if "difficulty" in state:
            fsrs_card.difficulty = state["difficulty"]
        if "reps" in state:
            fsrs_card.reps = state["reps"]
        if "lapses" in state:
            fsrs_card.lapses = state["lapses"]

    # Schedule
    now = datetime.now(timezone.utc)
    scheduling_cards = scheduler.repeat(fsrs_card, now)
    updated = scheduling_cards[fsrs_rating]

    new_card = updated.card

    # Store updated state
    card.fsrs_state = {
        "stability": new_card.stability,
        "difficulty": new_card.difficulty,
        "reps": new_card.reps,
        "lapses": new_card.lapses,
        "state": new_card.state.value if hasattr(new_card.state, "value") else int(new_card.state),
    }
    card.due_at = new_card.due.isoformat()
    card.review_count += 1

    # Persist
    update_card(card)
    record_review(card.id, rating)

    return card


def get_next_review_info(card: Flashcard) -> dict:
    """Preview when the card would be due for each rating option."""
    scheduler = get_scheduler()
    fsrs_card = Card()

    if card.fsrs_state:
        state = card.fsrs_state
        if "stability" in state:
            fsrs_card.stability = state["stability"]
        if "difficulty" in state:
            fsrs_card.difficulty = state["difficulty"]
        if "reps" in state:
            fsrs_card.reps = state["reps"]
        if "lapses" in state:
            fsrs_card.lapses = state["lapses"]

    now = datetime.now(timezone.utc)
    scheduling_cards = scheduler.repeat(fsrs_card, now)

    info = {}
    for rating_num, fsrs_rating in RATING_MAP.items():
        updated = scheduling_cards[fsrs_rating]
        due = updated.card.due
        delta = due - now
        info[rating_num] = _format_delta(delta)

    return info


def _format_delta(delta: timedelta) -> str:
    """Format a timedelta as a human-readable string."""
    total_seconds = int(delta.total_seconds())
    if total_seconds < 60:
        return f"{total_seconds}s"
    elif total_seconds < 3600:
        return f"{total_seconds // 60}m"
    elif total_seconds < 86400:
        return f"{total_seconds // 3600}h"
    else:
        return f"{total_seconds // 86400}d"
