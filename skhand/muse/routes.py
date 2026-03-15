"""Muse routes — page routes + API endpoints for the Writer's Muse."""

import json
import traceback
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from skhand.muse.corpus import (
    get_category,
    get_category_counts,
    get_corpus,
    get_creation_myth,
    get_hero,
    search_corpus,
)
from skhand.muse.models import (
    BlendRequest,
    CharacterForgeRequest,
    InspireRequest,
    StoryArchitectRequest,
    WorldBuildRequest,
)

TEMPLATES_DIR = Path(__file__).parent.parent / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# ─── Page router ─────────────────────────────────────────────────────────────
pages = APIRouter(tags=["muse-pages"])


@pages.get("/muse", response_class=HTMLResponse)
async def muse_dashboard(request: Request):
    counts = get_category_counts()
    return templates.TemplateResponse("muse/dashboard.html", {
        "request": request,
        "counts": counts,
    })


@pages.get("/muse/heroes", response_class=HTMLResponse)
async def muse_heroes_page(request: Request):
    heroes = get_category("heroes")
    return templates.TemplateResponse("muse/heroes.html", {
        "request": request,
        "heroes": heroes,
    })


@pages.get("/muse/heroes/{name}", response_class=HTMLResponse)
async def muse_hero_detail_page(request: Request, name: str):
    hero = get_hero(name)
    if not hero:
        return templates.TemplateResponse("muse/hero_detail.html", {
            "request": request,
            "hero": None,
            "error": f"Hero '{name}' not found",
        })
    return templates.TemplateResponse("muse/hero_detail.html", {
        "request": request,
        "hero": hero,
    })


@pages.get("/muse/creation-myths", response_class=HTMLResponse)
async def muse_creation_myths_page(request: Request):
    myths = get_category("creation_myths")
    taxonomy = get_category("creation_taxonomy")
    return templates.TemplateResponse("muse/creation_myths.html", {
        "request": request,
        "myths": myths,
        "taxonomy": taxonomy,
    })


@pages.get("/muse/pantheon", response_class=HTMLResponse)
async def muse_pantheon_page(request: Request):
    pantheon = get_category("pantheon")
    return templates.TemplateResponse("muse/pantheon.html", {
        "request": request,
        "pantheon": pantheon,
    })


@pages.get("/muse/world-builder", response_class=HTMLResponse)
async def muse_world_builder_page(request: Request):
    return templates.TemplateResponse("muse/world_builder.html", {
        "request": request,
        "creation_types": get_category("creation_taxonomy"),
        "ethics": get_category("ethics"),
        "cosmic_cycles": get_category("cosmic_cycles"),
        "eschatology": get_category("eschatology"),
    })


@pages.get("/muse/character-forge", response_class=HTMLResponse)
async def muse_character_forge_page(request: Request):
    heroes = get_category("heroes")
    archetypes = [h.get("name", "") for h in heroes]
    return templates.TemplateResponse("muse/character_forge.html", {
        "request": request,
        "archetypes": archetypes,
        "heroes": heroes,
    })


@pages.get("/muse/story-seeds", response_class=HTMLResponse)
async def muse_story_seeds_page(request: Request):
    return templates.TemplateResponse("muse/story_seeds.html", {
        "request": request,
    })


@pages.get("/muse/story-architect", response_class=HTMLResponse)
async def muse_story_architect_page(request: Request):
    stages = get_category("hero_journey")
    return templates.TemplateResponse("muse/story_architect.html", {
        "request": request,
        "journey_stages": stages,
    })


# ─── API router ──────────────────────────────────────────────────────────────
api = APIRouter(prefix="/api/muse", tags=["muse-api"])


@api.get("/categories")
async def api_categories():
    """All categories with counts."""
    counts = get_category_counts()
    categories = []
    labels = {
        "heroes": "Epic Heroes",
        "creation_myths": "Creation Myths",
        "pantheon": "Deity Pantheon",
        "cosmic_cycles": "Cosmic Cycles",
        "eschatology": "End of the World",
        "mystical": "Mystical Traditions",
        "ethics": "Moral Frameworks",
        "floods": "Flood Narratives",
        "hero_journey": "Hero's Journey",
        "afterlife": "Afterlife Concepts",
        "axial_age": "Axial Age Thinkers",
        "absolute": "The Absolute",
        "philosophy": "Philosophy Comparisons",
        "neoplatonism": "Neoplatonism & Vedanta",
        "master_index": "Universal Threads",
    }
    for key, count in counts.items():
        if key in labels:
            categories.append({
                "key": key,
                "label": labels[key],
                "count": count,
            })
    return JSONResponse({"categories": categories})


@api.get("/heroes")
async def api_heroes(tradition: Optional[str] = Query(None)):
    """All heroes, optionally filtered by tradition."""
    heroes = get_category("heroes")
    if tradition:
        heroes = [h for h in heroes if tradition.lower() in h.get("tradition", "").lower()]
    return JSONResponse({"heroes": heroes, "count": len(heroes)})


@api.get("/heroes/{name}")
async def api_hero(name: str):
    """Single hero by name."""
    hero = get_hero(name)
    if not hero:
        return JSONResponse({"error": f"Hero '{name}' not found"}, status_code=404)
    return JSONResponse({"hero": hero})


@api.get("/creation-myths")
async def api_creation_myths(type: Optional[str] = Query(None)):
    """All creation myths, optionally filtered by type."""
    myths = get_category("creation_myths")
    if type:
        myths = [m for m in myths if m.get("type") == type]
    return JSONResponse({"myths": myths, "count": len(myths)})


@api.get("/creation-myths/types")
async def api_creation_myth_types():
    """The 6-type taxonomy of creation myths."""
    taxonomy = get_category("creation_taxonomy")
    return JSONResponse({"types": taxonomy})


@api.get("/pantheon")
async def api_pantheon():
    """Deity cognate mappings."""
    pantheon = get_category("pantheon")
    return JSONResponse({"deities": pantheon, "count": len(pantheon)})


@api.get("/cosmic-cycles")
async def api_cosmic_cycles():
    """7 time systems."""
    cycles = get_category("cosmic_cycles")
    return JSONResponse({"systems": cycles, "count": len(cycles)})


@api.get("/ethics")
async def api_ethics():
    """8 moral frameworks."""
    ethics = get_category("ethics")
    return JSONResponse({"frameworks": ethics, "count": len(ethics)})


@api.get("/mystical")
async def api_mystical():
    """7 esoteric paths."""
    mystical = get_category("mystical")
    return JSONResponse({"traditions": mystical, "count": len(mystical)})


@api.get("/eschatology")
async def api_eschatology():
    """5 end-of-world traditions."""
    eschatology = get_category("eschatology")
    return JSONResponse({"cycles": eschatology, "count": len(eschatology)})


@api.get("/floods")
async def api_floods():
    """Flood narratives + motifs."""
    narratives = get_category("floods")
    motifs = get_category("flood_motifs")
    return JSONResponse({
        "narratives": narratives,
        "motifs": motifs,
        "count": len(narratives) if isinstance(narratives, list) else 0,
    })


@api.get("/hero-journey")
async def api_hero_journey():
    """Hero's journey stages."""
    stages = get_category("hero_journey")
    heroes = get_category("hero_journey_heroes")
    return JSONResponse({
        "stages": stages,
        "hero_mappings": heroes,
        "stage_count": len(stages) if isinstance(stages, list) else 0,
    })


@api.get("/threads")
async def api_threads():
    """Universal story threads from master index."""
    threads = get_category("master_index")
    return JSONResponse({"threads": threads, "count": len(threads) if isinstance(threads, list) else 0})


@api.get("/search")
async def api_search(
    q: str = Query(..., min_length=2),
    category: Optional[str] = Query(None),
    tradition: Optional[str] = Query(None),
):
    """Search corpus + optionally ChromaDB."""
    # Corpus search
    corpus_results = search_corpus(q, category=category, tradition=tradition)

    # Try ChromaDB search
    chromadb_results = []
    try:
        from skhand.query.world_search import search_world_texts
        raw = search_world_texts(q, n_results=5)
        for r in raw:
            chromadb_results.append({
                "text": r.text[:300],
                "metadata": r.metadata,
                "score": round(r.score, 4),
                "source": "chromadb",
            })
    except Exception:
        pass

    return JSONResponse({
        "query": q,
        "corpus_results": corpus_results,
        "chromadb_results": chromadb_results,
        "total": len(corpus_results) + len(chromadb_results),
    })


# ─── Generation endpoints (Claude) ──────────────────────────────────────────

@api.post("/inspire")
async def api_inspire(req: InspireRequest):
    """Generate story seeds from theme + traditions."""
    try:
        from skhand.muse.prompts import generate_inspiration
        result = await generate_inspiration(req)
        return JSONResponse(result)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@api.post("/character/forge")
async def api_character_forge(req: CharacterForgeRequest):
    """Generate a character profile."""
    try:
        from skhand.muse.prompts import generate_character
        result = await generate_character(req)
        return JSONResponse(result)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@api.post("/world/build")
async def api_world_build(req: WorldBuildRequest):
    """Generate a world description."""
    try:
        from skhand.muse.prompts import generate_world
        result = await generate_world(req)
        return JSONResponse(result)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@api.post("/story/architect")
async def api_story_architect(req: StoryArchitectRequest):
    """Generate a story outline on mythological patterns."""
    try:
        from skhand.muse.prompts import generate_story_outline
        result = await generate_story_outline(req)
        return JSONResponse(result)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)


@api.post("/blend")
async def api_blend(req: BlendRequest):
    """Blend elements across traditions into a creative synthesis."""
    try:
        from skhand.muse.blender import blend_elements
        result = await blend_elements(req)
        return JSONResponse(result)
    except Exception as e:
        traceback.print_exc()
        return JSONResponse({"error": str(e)}, status_code=500)
