"""Search the world texts ChromaDB collection for cross-cultural queries."""

from __future__ import annotations

from skhand.ingestion.embedder import get_chroma_client, get_embedding_function
from skhand.ingestion.world_texts_loader import WORLD_TEXTS_COLLECTION
from skhand.query.sanskrit_search import SearchResult


def search_world_texts(query: str, n_results: int = 5) -> list[SearchResult]:
    """Search world texts collection for cross-cultural matches."""
    client = get_chroma_client()
    embed_fn = get_embedding_function()

    try:
        collection = client.get_collection(
            name=WORLD_TEXTS_COLLECTION,
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


def search_by_thread(thread_id: str, n_results: int = 10) -> list[SearchResult]:
    """Search world texts filtered by a universal story thread.

    thread_id: one of 'creation', 'flood', 'hero_journey', 'cosmic_cycles',
               'immortality_quest', 'knowledge_theft', 'underworld_descent'
    """
    client = get_chroma_client()
    embed_fn = get_embedding_function()

    try:
        collection = client.get_collection(
            name=WORLD_TEXTS_COLLECTION,
            embedding_function=embed_fn,
        )
    except Exception:
        return []

    if collection.count() == 0:
        return []

    # Use metadata filter for thread
    results = collection.query(
        query_texts=[thread_id.replace("_", " ")],
        n_results=min(n_results, collection.count()),
        where={"universal_threads": {"$contains": thread_id}},
        include=["documents", "metadatas", "distances"],
    )

    search_results = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            search_results.append(SearchResult(text=doc, metadata=meta, score=dist))

    return search_results


def search_by_civilization(
    query: str, civilization: str, n_results: int = 5
) -> list[SearchResult]:
    """Search world texts filtered by civilization."""
    client = get_chroma_client()
    embed_fn = get_embedding_function()

    try:
        collection = client.get_collection(
            name=WORLD_TEXTS_COLLECTION,
            embedding_function=embed_fn,
        )
    except Exception:
        return []

    if collection.count() == 0:
        return []

    results = collection.query(
        query_texts=[query],
        n_results=min(n_results, collection.count()),
        where={"civilization": civilization},
        include=["documents", "metadatas", "distances"],
    )

    search_results = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            search_results.append(SearchResult(text=doc, metadata=meta, score=dist))

    return search_results
