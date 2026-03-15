"""Search the scientific papers ChromaDB collection."""

from __future__ import annotations

from skhand.ingestion.embedder import (
    SCIENCE_COLLECTION,
    get_chroma_client,
    get_embedding_function,
)
from skhand.query.sanskrit_search import SearchResult


def search_papers(query: str, n_results: int = 5) -> list[SearchResult]:
    """Search scientific papers collection."""
    client = get_chroma_client()
    embed_fn = get_embedding_function()

    try:
        collection = client.get_collection(
            name=SCIENCE_COLLECTION,
            embedding_function=embed_fn,
        )
    except Exception:
        return []

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    search_results = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        search_results.append(SearchResult(text=doc, metadata=meta, score=dist))

    return search_results
