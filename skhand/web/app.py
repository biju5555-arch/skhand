"""Skhand Web UI — FastAPI application with all routes."""

from __future__ import annotations

import traceback
from pathlib import Path

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

app = FastAPI(title="Skhand", description="Polymath AI Learning Companion")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:19006",
        "https://skanda.fly.dev",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Mount Writer's Muse routers
from skhand.muse.routes import api as muse_api, pages as muse_pages  # noqa: E402

app.include_router(muse_pages)
app.include_router(muse_api)


# ─── Page routes ────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/graph", response_class=HTMLResponse)
async def graph_page(request: Request):
    return templates.TemplateResponse("graph.html", {"request": request})


@app.get("/learn", response_class=HTMLResponse)
async def learn_page(request: Request):
    return templates.TemplateResponse("learn.html", {"request": request})


@app.get("/status", response_class=HTMLResponse)
async def status_page(request: Request):
    return templates.TemplateResponse("status.html", {"request": request})


# ─── API routes ─────────────────────────────────────────────────────────────


@app.get("/api/ping")
async def api_ping():
    """Lightweight connectivity check for mobile app."""
    return JSONResponse({"status": "ok"})


@app.post("/api/ask")
async def api_ask(request: Request):
    """Submit a question and get a three-section answer."""
    body = await request.json()
    question = body.get("question", "").strip()
    save_cards = body.get("save_cards", False)

    if not question:
        return JSONResponse({"error": "Question is required"}, status_code=400)

    try:
        from skhand.query.engine import ask as engine_ask

        result = engine_ask(question=question, n_results=5, verbose=False)

        response = {
            "shastra": result.get("shastra", ""),
            "science": result.get("science", ""),
            "setu": result.get("setu", ""),
            "usage": result.get("usage"),
        }

        if save_cards and result.get("shastra"):
            from skhand.learning.flashcard import generate_flashcards

            full_answer = (
                f"{result['shastra']}\n\n{result['science']}\n\n{result['setu']}"
            )
            cards = generate_flashcards(question=question, answer=full_answer)
            response["cards_generated"] = len(cards)

        return JSONResponse(response)

    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/graph/query")
async def api_graph_query(concept: str = Query(..., description="Concept name to search")):
    """Query the knowledge graph for a concept."""
    try:
        from skhand.graph.queries import query_graph

        results = query_graph(concept)
        return JSONResponse({"results": results, "concept": concept})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/graph/equivalents")
async def api_graph_equivalents(concept: str = Query(..., description="Concept name")):
    """Get modern equivalents for a concept."""
    try:
        from skhand.graph.queries import get_equivalents

        results = get_equivalents(concept)
        return JSONResponse({"results": results, "concept": concept})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/learn/due")
async def api_learn_due(limit: int = Query(20, ge=1, le=100)):
    """Get flashcards due for review."""
    try:
        from skhand.learning.store import get_due_cards

        cards = get_due_cards(limit=limit)
        return JSONResponse({
            "cards": [
                {
                    "id": c.id,
                    "front": c.front,
                    "back": c.back,
                    "source_question": c.source_question,
                    "due_at": c.due_at,
                    "review_count": c.review_count,
                }
                for c in cards
            ],
            "count": len(cards),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/learn/review")
async def api_learn_review(request: Request):
    """Submit a review rating for a flashcard."""
    body = await request.json()
    card_id = body.get("card_id")
    rating = body.get("rating")

    if not card_id or rating not in (1, 2, 3, 4):
        return JSONResponse(
            {"error": "card_id and rating (1-4) required"}, status_code=400
        )

    try:
        from skhand.learning.scheduler import review_card
        from skhand.learning.store import get_card

        card = get_card(card_id)
        if not card:
            return JSONResponse({"error": "Card not found"}, status_code=404)

        updated = review_card(card, rating)
        return JSONResponse({
            "card_id": updated.id,
            "due_at": updated.due_at,
            "review_count": updated.review_count,
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/learn/stats")
async def api_learn_stats():
    """Get learning statistics."""
    try:
        from skhand.learning.store import get_stats

        return JSONResponse(get_stats())
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/api/flashcards/generate")
async def api_flashcards_generate(request: Request):
    """Generate flashcards from a question and answer."""
    body = await request.json()
    question = body.get("question", "")
    answer = body.get("answer", "")
    count = body.get("count", 4)

    if not question or not answer:
        return JSONResponse(
            {"error": "question and answer required"}, status_code=400
        )

    try:
        from skhand.learning.flashcard import generate_flashcards

        cards = generate_flashcards(question=question, answer=answer, count=count)
        return JSONResponse({
            "cards": [
                {"id": c.id, "front": c.front, "back": c.back} for c in cards
            ],
            "count": len(cards),
        })
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/status")
async def api_status():
    """Get system status (mirrors CLI status command)."""
    from skhand.config import get_settings

    settings = get_settings()
    items = []

    # API key
    if settings.anthropic_api_key and settings.anthropic_api_key != "your-api-key-here":
        key_preview = settings.anthropic_api_key[:8] + "..."
        items.append({"component": "Anthropic API", "status": "OK", "detail": f"Key: {key_preview}"})
    else:
        items.append({"component": "Anthropic API", "status": "NOT SET", "detail": "Set ANTHROPIC_API_KEY in .env"})

    # ChromaDB
    try:
        from skhand.ingestion.embedder import get_collection_count

        sanskrit_count = get_collection_count("sanskrit_texts")
        science_count = get_collection_count("science_papers")
        world_count = get_collection_count("world_texts")
        items.append({"component": "ChromaDB (Sanskrit)", "status": "OK" if sanskrit_count > 0 else "EMPTY", "detail": f"{sanskrit_count} chunks"})
        items.append({"component": "ChromaDB (World Texts)", "status": "OK" if world_count > 0 else "EMPTY", "detail": f"{world_count} chunks"})
        items.append({"component": "ChromaDB (Science)", "status": "OK" if science_count > 0 else "EMPTY", "detail": f"{science_count} chunks"})
    except Exception as e:
        items.append({"component": "ChromaDB", "status": "ERROR", "detail": str(e)})

    # Neo4j
    try:
        from skhand.graph.builder import get_node_count, get_relationship_count

        node_count = get_node_count()
        rel_count = get_relationship_count()
        if node_count >= 0:
            items.append({"component": "Neo4j", "status": "OK", "detail": f"{node_count} nodes, {rel_count} relationships"})
        else:
            items.append({"component": "Neo4j", "status": "OFFLINE", "detail": "Run: docker-compose up -d"})
    except Exception as e:
        items.append({"component": "Neo4j", "status": "ERROR", "detail": str(e)})

    # Learning
    try:
        from skhand.learning.store import get_stats

        stats = get_stats()
        items.append({"component": "Flashcards", "status": "OK", "detail": f"{stats['total_cards']} cards, {stats['due_now']} due"})
    except Exception as e:
        items.append({"component": "Flashcards", "status": "ERROR", "detail": str(e)})

    items.append({"component": "Embedding Model", "status": "OK", "detail": settings.embedding_model})
    items.append({"component": "Claude Model", "status": "OK", "detail": settings.claude_model})

    return JSONResponse({"items": items})
