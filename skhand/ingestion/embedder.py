"""Embed text chunks into ChromaDB collections."""

from __future__ import annotations

from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from skhand.config import get_settings
from skhand.ingestion.chunker import Chunk
from skhand.utils.display import console

# Collection names
SANSKRIT_COLLECTION = "sanskrit_texts"
SCIENCE_COLLECTION = "science_papers"
WORLD_TEXTS_COLLECTION = "world_texts"


def get_chroma_client() -> chromadb.ClientAPI:
    """Get a persistent ChromaDB client."""
    settings = get_settings()
    persist_dir = Path(settings.chroma_persist_dir)
    persist_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(persist_dir))


def get_embedding_function() -> SentenceTransformerEmbeddingFunction:
    """Get the sentence transformer embedding function."""
    settings = get_settings()
    return SentenceTransformerEmbeddingFunction(model_name=settings.embedding_model)


def embed_chunks(chunks: list[Chunk], collection_name: str) -> int:
    """Embed chunks into a ChromaDB collection.

    Returns the number of chunks added.
    """
    if not chunks:
        console.print("[warning]No chunks to embed[/warning]")
        return 0

    client = get_chroma_client()
    embed_fn = get_embedding_function()

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embed_fn,
        metadata={"hnsw:space": "cosine"},
    )

    # Batch insert (ChromaDB has a limit of ~5000 per batch)
    batch_size = 500
    total_added = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]

        ids = []
        documents = []
        metadatas = []

        for j, chunk in enumerate(batch):
            chunk_id = chunk.chunk_id or f"{collection_name}_{i + j}"
            ids.append(chunk_id)
            documents.append(chunk.text)
            # ChromaDB metadata values must be str, int, float, or bool
            clean_meta = {
                k: str(v) if not isinstance(v, (int, float, bool)) else v
                for k, v in chunk.metadata.items()
            }
            metadatas.append(clean_meta)

        collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        total_added += len(batch)
        console.print(f"[meta]  Embedded {total_added}/{len(chunks)} chunks[/meta]")

    console.print(
        f"[success]Collection '{collection_name}' now has "
        f"{collection.count()} total chunks[/success]"
    )
    return total_added


def get_collection_count(collection_name: str) -> int:
    """Get the number of items in a collection."""
    try:
        client = get_chroma_client()
        collection = client.get_collection(name=collection_name)
        return collection.count()
    except Exception:
        return 0
