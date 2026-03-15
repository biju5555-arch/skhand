"""Search the Sanskrit texts ChromaDB collection."""

from __future__ import annotations

from dataclasses import dataclass

from skhand.ingestion.embedder import (
    SANSKRIT_COLLECTION,
    get_chroma_client,
    get_embedding_function,
)


@dataclass
class SearchResult:
    """A single search result with text, metadata, and score."""

    text: str
    metadata: dict
    score: float  # Distance (lower = more similar for cosine)

    @property
    def citation(self) -> str:
        """Format as a citation string."""
        # Handle world text metadata
        name = self.metadata.get("name", "")
        civilization = self.metadata.get("civilization_display", self.metadata.get("civilization", ""))

        if name and civilization:
            parts = [name]
            if civilization:
                parts.append(f"[{civilization}]")
            era = self.metadata.get("era", "")
            if era:
                parts.append(era)
            return " — ".join(parts)

        # Fallback: Sanskrit/Indic citation format
        source = self.metadata.get("source", "unknown")
        sthana = self.metadata.get("sthana", "")
        chapter = self.metadata.get("chapter", "")
        verse = self.metadata.get("verse", "")

        parts = [source.replace("_", " ").title()]
        if sthana:
            parts.append(sthana.replace("_", " ").title())
        if chapter:
            parts.append(f"Ch. {chapter}")
        if verse:
            parts.append(f"v. {verse}")
        return ", ".join(parts)


def search_sanskrit(query: str, n_results: int = 5) -> list[SearchResult]:
    """Search Sanskrit text collection."""
    client = get_chroma_client()
    embed_fn = get_embedding_function()

    try:
        collection = client.get_collection(
            name=SANSKRIT_COLLECTION,
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
