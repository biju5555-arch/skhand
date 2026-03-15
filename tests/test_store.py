"""Tests for the flashcard store."""

import tempfile
from pathlib import Path

from skhand.learning.store import Flashcard, get_db, get_due_cards, get_stats, save_cards


def test_save_and_retrieve_cards(tmp_path):
    db_path = tmp_path / "test.db"
    conn = get_db(db_path)
    conn.close()

    cards = [
        Flashcard(front="What is Shodhana?", back="Purification process in Ayurveda"),
        Flashcard(front="Formula for Tamra Bhasma?", back="Calcined copper oxide (CuO)"),
    ]

    # Override settings path for test
    import skhand.learning.store as store_mod
    original = store_mod.get_settings

    _db_path = db_path  # capture for closure

    class FakeSettings:
        db_path = _db_path

    store_mod.get_settings = lambda: FakeSettings()

    try:
        ids = save_cards(cards, source_question="test")
        assert len(ids) == 2

        stats = get_stats()
        assert stats["total_cards"] == 2
        assert stats["due_now"] == 2
    finally:
        store_mod.get_settings = original
