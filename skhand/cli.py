"""Skhand CLI — Typer-based command interface."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from skhand.utils.display import console, print_flashcard, print_flashcard_answer, print_header, print_status_table

app = typer.Typer(
    name="skhand",
    help="स्कन्ध — Polymath AI Learning Companion\n\n"
    "Bridge ancient Sanskrit/Ayurvedic knowledge with modern science.",
    no_args_is_help=True,
)
ingest_app = typer.Typer(help="Ingest data into Skhand.")
graph_app = typer.Typer(help="Knowledge graph operations.")
learn_app = typer.Typer(help="Spaced repetition learning.")

app.add_typer(ingest_app, name="ingest")
app.add_typer(graph_app, name="graph")
app.add_typer(learn_app, name="learn")


# ─── Ask ─────────────────────────────────────────────────────────────────────


@app.command()
def ask(
    question: str = typer.Argument(..., help="Your question bridging ancient and modern knowledge"),
    save_cards: bool = typer.Option(False, "--save-cards", "-s", help="Generate and save flashcards from the answer"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show retrieval scores and token usage"),
    n_results: int = typer.Option(5, "--n-results", "-n", help="Number of search results per corpus"),
):
    """Ask a question that bridges Sanskrit/Ayurvedic and modern scientific knowledge."""
    print_header()

    from skhand.query.engine import ask as engine_ask

    result = engine_ask(question=question, n_results=n_results, verbose=verbose)

    if save_cards and result.get("shastra"):
        from skhand.learning.flashcard import generate_flashcards

        full_answer = f"{result['shastra']}\n\n{result['science']}\n\n{result['setu']}"
        generate_flashcards(question=question, answer=full_answer)


# ─── Ingest ──────────────────────────────────────────────────────────────────


@ingest_app.command("sanskrit")
def ingest_sanskrit(
    data_dir: Optional[Path] = typer.Option(None, "--data-dir", "-d", help="Path to Sanskrit data directory"),
):
    """Ingest Sanskrit texts (Charaka Samhita, DCS) into ChromaDB."""
    print_header()
    console.print("\n[title]Ingesting Sanskrit Texts[/title]\n")

    from skhand.ingestion.embedder import SANSKRIT_COLLECTION, embed_chunks
    from skhand.ingestion.sanskrit_loader import load_charaka_samhita, load_dcs_texts

    chunks = load_charaka_samhita(data_dir)
    chunks.extend(load_dcs_texts())

    if not chunks:
        console.print("[warning]No chunks to ingest. Run download_datasets.py first.[/warning]")
        raise typer.Exit(1)

    console.print(f"\n[meta]Embedding {len(chunks)} chunks...[/meta]")
    count = embed_chunks(chunks, SANSKRIT_COLLECTION)
    console.print(f"\n[success]Ingested {count} Sanskrit chunks[/success]")


@ingest_app.command("papers")
def ingest_papers(
    data_dir: Optional[Path] = typer.Option(None, "--data-dir", "-d", help="Path to papers directory"),
):
    """Ingest scientific papers (PDFs) into ChromaDB."""
    print_header()
    console.print("\n[title]Ingesting Scientific Papers[/title]\n")

    from skhand.ingestion.embedder import SCIENCE_COLLECTION, embed_chunks
    from skhand.ingestion.paper_loader import load_papers

    chunks = load_papers(data_dir)

    if not chunks:
        console.print("[warning]No papers to ingest. Add PDFs to data/papers/[/warning]")
        raise typer.Exit(1)

    console.print(f"\n[meta]Embedding {len(chunks)} chunks...[/meta]")
    count = embed_chunks(chunks, SCIENCE_COLLECTION)
    console.print(f"\n[success]Ingested {count} paper chunks[/success]")


@ingest_app.command("world-texts")
def ingest_world_texts(
    data_dir: Optional[Path] = typer.Option(None, "--data-dir", "-d", help="Path to world texts directory"),
):
    """Ingest world texts (cross-cultural corpus) into ChromaDB."""
    print_header()
    console.print("\n[title]Ingesting World Texts — The Story of Humanity[/title]\n")

    from skhand.ingestion.embedder import embed_chunks
    from skhand.ingestion.world_texts_loader import (
        WORLD_TEXTS_COLLECTION,
        load_knowledge_files,
        load_world_texts,
    )

    chunks = load_world_texts(data_dir)
    chunks.extend(load_knowledge_files())

    if not chunks:
        console.print("[warning]No world text chunks to ingest.[/warning]")
        console.print("[meta]Run: python3 acquire_world_texts.py[/meta]")
        raise typer.Exit(1)

    console.print(f"\n[meta]Embedding {len(chunks)} world text chunks...[/meta]")
    count = embed_chunks(chunks, WORLD_TEXTS_COLLECTION)
    console.print(f"\n[success]Ingested {count} world text chunks into '{WORLD_TEXTS_COLLECTION}'[/success]")


@ingest_app.command("download")
def ingest_download():
    """Download Sanskrit datasets from GitHub."""
    print_header()
    console.print("\n[title]Downloading Datasets[/title]\n")

    import subprocess
    import sys

    scripts_dir = Path(__file__).parent.parent / "scripts"
    subprocess.run([sys.executable, str(scripts_dir / "download_datasets.py")], check=True)


# ─── Graph ───────────────────────────────────────────────────────────────────


@graph_app.command("build")
def graph_build():
    """Initialize graph schema and seed with known mappings."""
    print_header()
    console.print("\n[title]Building Knowledge Graph[/title]\n")

    from skhand.graph.builder import init_schema, seed_graph

    init_schema()
    seed_graph()


@graph_app.command("query")
def graph_query_cmd(
    concept: str = typer.Argument(..., help="Concept name to query"),
):
    """Query the knowledge graph for a concept and its connections."""
    print_header()

    from skhand.graph.queries import query_graph

    results = query_graph(concept)

    if not results:
        console.print(f"[warning]No results for '{concept}'[/warning]")
        raise typer.Exit(1)

    # Group by node
    seen_nodes = set()
    table = Table(title=f"Knowledge Graph: {concept}", border_style="magenta")
    table.add_column("Node", style="title")
    table.add_column("Type")
    table.add_column("Domain")
    table.add_column("Relationship", style="bridge")
    table.add_column("Connected To")
    table.add_column("Confidence")

    for r in results:
        node_key = r["name"]
        if node_key not in seen_nodes:
            seen_nodes.add(node_key)
            sanskrit = f" ({r['sanskrit']})" if r.get("sanskrit") else ""
            desc = f"\n{r['description']}" if r.get("description") else ""

        conf = f"{r['confidence']:.0%}" if r.get("confidence") else ""
        table.add_row(
            f"{r['name']}{sanskrit}" if r.get("sanskrit") else r["name"],
            r.get("type", ""),
            r.get("domain", ""),
            r.get("relationship", ""),
            r.get("connected_to", ""),
            conf,
        )

    console.print(table)


@graph_app.command("link")
def graph_link(
    concept: str = typer.Argument(..., help="Sanskrit concept to find modern equivalents for"),
    context: str = typer.Option("", "--context", "-c", help="Additional context"),
):
    """Use Claude to find and store modern equivalents for a Sanskrit concept."""
    print_header()

    from skhand.graph.linker import link_and_store

    link_and_store(concept, context)


# ─── Learn ───────────────────────────────────────────────────────────────────


@learn_app.command("review")
def learn_review(
    limit: int = typer.Option(20, "--limit", "-l", help="Maximum cards to review"),
):
    """Review due flashcards with spaced repetition."""
    print_header()
    console.print("\n[title]Flashcard Review[/title]\n")

    from skhand.learning.scheduler import get_next_review_info, review_card
    from skhand.learning.store import get_due_cards

    cards = get_due_cards(limit=limit)

    if not cards:
        console.print("[success]No cards due for review! Come back later.[/success]")
        return

    console.print(f"[meta]{len(cards)} card(s) due for review[/meta]\n")

    for i, card in enumerate(cards, 1):
        print_flashcard(card.front, card.back, i, len(cards))

        input()  # Wait for Enter
        print_flashcard_answer(card.back)

        # Show next review intervals
        intervals = get_next_review_info(card)
        console.print(
            f"  [meta]1=Again ({intervals[1]}) | 2=Hard ({intervals[2]}) | "
            f"3=Good ({intervals[3]}) | 4=Easy ({intervals[4]})[/meta]"
        )

        while True:
            rating_input = input("  Rating (1-4): ").strip()
            if rating_input in ("1", "2", "3", "4"):
                rating = int(rating_input)
                break
            console.print("[warning]Enter 1-4[/warning]")

        review_card(card, rating)
        console.print(f"[meta]Next review: {card.due_at}[/meta]\n")

    console.print("[success]Review session complete![/success]")


@learn_app.command("stats")
def learn_stats():
    """Show learning statistics."""
    print_header()

    from skhand.learning.store import get_stats

    stats = get_stats()

    table = Table(title="Learning Statistics", border_style="magenta")
    table.add_column("Metric", style="title")
    table.add_column("Value")

    table.add_row("Total Cards", str(stats["total_cards"]))
    table.add_row("Due Now", str(stats["due_now"]))
    table.add_row("Reviews Today", str(stats["reviews_today"]))
    table.add_row("Total Reviews", str(stats["total_reviews"]))

    if stats["rating_distribution"]:
        dist = ", ".join(f"{k}: {v}" for k, v in stats["rating_distribution"].items())
        table.add_row("Rating Distribution", dist)

    console.print(table)


# ─── Status ──────────────────────────────────────────────────────────────────


@app.command()
def status():
    """Show Skhand system status — API, databases, collections."""
    print_header()

    from skhand.config import get_settings

    settings = get_settings()
    items = []

    # API key
    if settings.anthropic_api_key and settings.anthropic_api_key != "your-api-key-here":
        key_preview = settings.anthropic_api_key[:8] + "..."
        items.append(("Anthropic API", "OK", f"Key: {key_preview}"))
    else:
        items.append(("Anthropic API", "NOT SET", "Set ANTHROPIC_API_KEY in .env"))

    # ChromaDB
    from skhand.ingestion.embedder import get_collection_count

    sanskrit_count = get_collection_count("sanskrit_texts")
    science_count = get_collection_count("science_papers")
    world_count = get_collection_count("world_texts")
    items.append(("ChromaDB (Sanskrit)", "OK" if sanskrit_count > 0 else "EMPTY", f"{sanskrit_count} chunks"))
    items.append(("ChromaDB (World Texts)", "OK" if world_count > 0 else "EMPTY", f"{world_count} chunks"))
    items.append(("ChromaDB (Science)", "OK" if science_count > 0 else "EMPTY", f"{science_count} chunks"))

    # Neo4j
    from skhand.graph.builder import get_node_count, get_relationship_count

    node_count = get_node_count()
    rel_count = get_relationship_count()
    if node_count >= 0:
        items.append(("Neo4j", "OK", f"{node_count} nodes, {rel_count} relationships"))
    else:
        items.append(("Neo4j", "OFFLINE", "Run: docker-compose up -d"))

    # Learning
    from skhand.learning.store import get_stats

    stats = get_stats()
    items.append(("Flashcards", "OK", f"{stats['total_cards']} cards, {stats['due_now']} due"))

    # Config
    items.append(("Embedding Model", "OK", settings.embedding_model))
    items.append(("Claude Model", "OK", settings.claude_model))

    print_status_table(items)


@app.command()
def web(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", help="Enable auto-reload for development"),
):
    """Start the Skhand web interface."""
    import uvicorn

    console.print(f"\n[title]Starting Skhand Web UI[/title]")
    console.print(f"[meta]Open http://{host}:{port} in your browser[/meta]\n")
    uvicorn.run("skhand.web.app:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
