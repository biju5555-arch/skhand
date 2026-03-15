"""Multi-corpus query engine — the orchestrator."""

from __future__ import annotations

from skhand.graph.queries import get_concept_context
from skhand.query.paper_search import search_papers
from skhand.query.sanskrit_search import search_sanskrit
from skhand.query.synthesizer import synthesize
from skhand.query.world_search import search_world_texts
from skhand.utils.display import console, print_answer


def ask(
    question: str,
    n_results: int = 5,
    verbose: bool = False,
    use_graph: bool = True,
) -> dict:
    """Full pipeline: search all corpora, get graph context, synthesize via Claude.

    Searches Sanskrit texts, world texts, and science papers, then synthesizes
    a cross-cultural answer via Claude.

    Returns the synthesis result dict with keys: shastra, science, setu, usage.
    """
    console.print(f"[meta]Searching corpora for: {question}[/meta]")

    # Search all collections
    sanskrit_results = search_sanskrit(question, n_results=n_results)
    world_results = search_world_texts(question, n_results=n_results)
    science_results = search_papers(question, n_results=n_results)

    if verbose:
        console.print(f"[meta]Sanskrit hits: {len(sanskrit_results)}[/meta]")
        for r in sanskrit_results:
            console.print(f"[meta]  {r.citation} (score: {r.score:.3f})[/meta]")
        console.print(f"[meta]World text hits: {len(world_results)}[/meta]")
        for r in world_results:
            console.print(f"[meta]  {r.citation} (score: {r.score:.3f})[/meta]")
        console.print(f"[meta]Science hits: {len(science_results)}[/meta]")
        for r in science_results:
            console.print(f"[meta]  {r.citation} (score: {r.score:.3f})[/meta]")

    # Merge world text results with sanskrit results for synthesis
    # (world texts provide cross-cultural context alongside Indic sources)
    combined_traditional = sanskrit_results + world_results

    # Get knowledge graph context
    graph_context = ""
    if use_graph:
        try:
            graph_context = get_concept_context(question)
        except Exception:
            if verbose:
                console.print("[meta]Graph context unavailable[/meta]")

    # Synthesize via Claude
    result = synthesize(
        question=question,
        sanskrit_results=combined_traditional,
        science_results=science_results,
        graph_context=graph_context,
        verbose=verbose,
    )

    # Display
    print_answer(
        shastra=result["shastra"],
        science=result["science"],
        setu=result["setu"],
    )

    return result
