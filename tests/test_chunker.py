"""Tests for the chunker module."""

from skhand.ingestion.chunker import Chunk, chunk_sanskrit_verses, chunk_text_by_size


def test_chunk_text_by_size_basic():
    text = "Hello world. " * 100
    chunks = chunk_text_by_size(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(isinstance(c, Chunk) for c in chunks)


def test_chunk_text_preserves_metadata():
    text = "Some text here. More text follows."
    meta = {"source": "test", "type": "unit_test"}
    chunks = chunk_text_by_size(text, chunk_size=5000, metadata=meta)
    assert len(chunks) == 1
    assert chunks[0].metadata["source"] == "test"


def test_chunk_sanskrit_verses():
    verses = [
        {"text": "verse1", "translation": "trans1", "sthana": "sutra", "chapter": 1, "verse_num": 1},
        {"text": "verse2", "translation": "trans2", "sthana": "sutra", "chapter": 1, "verse_num": 2},
        {"text": "verse3", "translation": "trans3", "sthana": "sutra", "chapter": 1, "verse_num": 3},
        {"text": "verse4", "translation": "trans4", "sthana": "sutra", "chapter": 1, "verse_num": 4},
    ]
    chunks = chunk_sanskrit_verses(verses, group_size=3)
    assert len(chunks) == 2  # 3 + 1
    assert "verse1" in chunks[0].text
    assert chunks[0].metadata["sthana"] == "sutra"


def test_chunk_empty_input():
    chunks = chunk_text_by_size("", chunk_size=100)
    assert len(chunks) == 0

    chunks = chunk_sanskrit_verses([])
    assert len(chunks) == 0
