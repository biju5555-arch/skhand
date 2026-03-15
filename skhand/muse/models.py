"""Pydantic request/response schemas for the Muse API."""

from __future__ import annotations

from pydantic import BaseModel, Field


# ─── Request models ──────────────────────────────────────────────────────────

class InspireRequest(BaseModel):
    theme: str = Field(..., min_length=2, max_length=500)
    traditions: list[str] = Field(default_factory=list)
    mood: str = Field(default="epic")
    count: int = Field(default=3, ge=1, le=5)
    quality: str = Field(default="fast")  # "fast" (Haiku) or "deep" (Sonnet)


class CharacterForgeRequest(BaseModel):
    archetype: str = Field(..., min_length=2, max_length=200)
    traditions: list[str] = Field(default_factory=list)
    role: str = Field(default="protagonist")
    era: str = Field(default="mythic")
    traits: list[str] = Field(default_factory=list)
    quality: str = Field(default="fast")


class WorldBuildRequest(BaseModel):
    creation_type: str = Field(default="cosmic_egg")
    pantheon_traditions: list[str] = Field(default_factory=list)
    ethics: str = Field(default="dharma")
    time_system: str = Field(default="cyclical")
    eschatology: str = Field(default="renewal")
    quality: str = Field(default="fast")


class StoryArchitectRequest(BaseModel):
    premise: str = Field(..., min_length=10, max_length=1000)
    structure: str = Field(default="hero_journey")
    hero_type: str = Field(default="reluctant")
    traditions: list[str] = Field(default_factory=list)
    quality: str = Field(default="fast")


class BlendRequest(BaseModel):
    elements: list[dict] = Field(
        ...,
        min_length=2,
        max_length=6,
        description="Each element: {category, id, tradition}",
    )
    goal: str = Field(default="synthesis")
    quality: str = Field(default="fast")


# ─── Response models ─────────────────────────────────────────────────────────

class StorySeed(BaseModel):
    title: str
    premise: str
    traditions_used: list[str]
    key_tension: str
    opening_line: str


class CharacterProfile(BaseModel):
    name: str
    epithet: str
    origin: str
    appearance: str
    personality: str
    weapon_or_tool: str
    companion: str
    inner_conflict: str
    quest: str
    traditions_drawn_from: list[str]


class WorldDescription(BaseModel):
    name: str
    creation_story: str
    cosmology: str
    pantheon_summary: str
    moral_framework: str
    time_and_fate: str
    end_of_world: str
    traditions_drawn_from: list[str]


class StoryOutline(BaseModel):
    title: str
    logline: str
    acts: list[dict]
    mythological_parallels: list[str]
    themes: list[str]


class BlendResult(BaseModel):
    title: str
    synthesis: str
    elements_used: list[str]
    creative_tensions: list[str]
    story_potential: str
