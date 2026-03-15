"""SQLite persistence for flashcards and review history."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from skhand.config import get_settings


@dataclass
class Flashcard:
    """A flashcard with FSRS scheduling state."""

    id: int | None = None
    front: str = ""
    back: str = ""
    source_question: str = ""
    created_at: str = ""
    # FSRS state stored as JSON
    fsrs_state: dict = field(default_factory=dict)
    due_at: str = ""
    review_count: int = 0


def get_db(db_path: Path | None = None) -> sqlite3.Connection:
    """Get a SQLite connection, creating tables if needed."""
    settings = get_settings()
    db_path = db_path or settings.db_path
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")

    conn.executescript("""
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            front TEXT NOT NULL,
            back TEXT NOT NULL,
            source_question TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now')),
            fsrs_state TEXT DEFAULT '{}',
            due_at TEXT DEFAULT (datetime('now')),
            review_count INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            reviewed_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (card_id) REFERENCES flashcards(id)
        );
        CREATE INDEX IF NOT EXISTS idx_flashcards_due ON flashcards(due_at);
    """)
    return conn


def save_cards(cards: list[Flashcard], source_question: str = "") -> list[int]:
    """Save flashcards to the database. Returns list of IDs."""
    conn = get_db()
    ids = []

    for card in cards:
        cursor = conn.execute(
            "INSERT INTO flashcards (front, back, source_question, fsrs_state, due_at) "
            "VALUES (?, ?, ?, ?, datetime('now'))",
            (card.front, card.back, source_question, json.dumps(card.fsrs_state)),
        )
        ids.append(cursor.lastrowid)

    conn.commit()
    conn.close()
    return ids


def get_due_cards(limit: int = 20) -> list[Flashcard]:
    """Get cards that are due for review."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM flashcards WHERE due_at <= datetime('now') "
        "ORDER BY due_at ASC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()

    return [_row_to_card(row) for row in rows]


def get_card(card_id: int) -> Flashcard | None:
    """Get a single card by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM flashcards WHERE id = ?", (card_id,)).fetchone()
    conn.close()
    return _row_to_card(row) if row else None


def update_card(card: Flashcard):
    """Update a card's FSRS state and due date."""
    conn = get_db()
    conn.execute(
        "UPDATE flashcards SET fsrs_state = ?, due_at = ?, review_count = ? WHERE id = ?",
        (json.dumps(card.fsrs_state), card.due_at, card.review_count, card.id),
    )
    conn.commit()
    conn.close()


def record_review(card_id: int, rating: int):
    """Record a review event."""
    conn = get_db()
    conn.execute(
        "INSERT INTO reviews (card_id, rating) VALUES (?, ?)",
        (card_id, rating),
    )
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Get learning statistics."""
    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM flashcards").fetchone()[0]
    due = conn.execute(
        "SELECT COUNT(*) FROM flashcards WHERE due_at <= datetime('now')"
    ).fetchone()[0]
    reviews_today = conn.execute(
        "SELECT COUNT(*) FROM reviews WHERE date(reviewed_at) = date('now')"
    ).fetchone()[0]
    total_reviews = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]

    # Rating distribution
    rating_dist = {}
    rows = conn.execute(
        "SELECT rating, COUNT(*) as cnt FROM reviews GROUP BY rating"
    ).fetchall()
    for row in rows:
        rating_names = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}
        rating_dist[rating_names.get(row[0], str(row[0]))] = row[1]

    conn.close()

    return {
        "total_cards": total,
        "due_now": due,
        "reviews_today": reviews_today,
        "total_reviews": total_reviews,
        "rating_distribution": rating_dist,
    }


def _row_to_card(row: sqlite3.Row) -> Flashcard:
    """Convert a database row to a Flashcard."""
    return Flashcard(
        id=row["id"],
        front=row["front"],
        back=row["back"],
        source_question=row["source_question"],
        created_at=row["created_at"],
        fsrs_state=json.loads(row["fsrs_state"]) if row["fsrs_state"] else {},
        due_at=row["due_at"],
        review_count=row["review_count"],
    )
