"""Rich terminal formatting for Skhand output."""

from __future__ import annotations

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.theme import Theme

SKHAND_THEME = Theme(
    {
        "sanskrit": "bold gold1",
        "science": "bold dodger_blue1",
        "bridge": "bold green3",
        "title": "bold magenta",
        "meta": "dim",
        "success": "bold green",
        "warning": "bold yellow",
        "error": "bold red",
    }
)

console = Console(theme=SKHAND_THEME)


def print_header():
    """Print the Skhand banner."""
    console.print(
        Panel(
            "[title]स्कन्ध — Skhand v0.1[/title]\n"
            "[meta]Polymath AI Learning Companion[/meta]",
            border_style="magenta",
        )
    )


def print_answer(shastra: str, science: str, setu: str):
    """Print a formatted three-section answer."""
    console.print()
    console.print(
        Panel(
            Markdown(shastra),
            title="[sanskrit]Ancient Knowledge (Shastra / शास्त्र)[/sanskrit]",
            border_style="gold1",
        )
    )
    console.print(
        Panel(
            Markdown(science),
            title="[science]Modern Science[/science]",
            border_style="dodger_blue1",
        )
    )
    console.print(
        Panel(
            Markdown(setu),
            title="[bridge]Bridge (Setu / सेतु)[/bridge]",
            border_style="green3",
        )
    )


def print_status_table(items: list[tuple[str, str, str]]):
    """Print a status table. items: list of (component, status, detail)."""
    table = Table(title="Skhand System Status", border_style="magenta")
    table.add_column("Component", style="title")
    table.add_column("Status")
    table.add_column("Details", style="meta")
    for component, status, detail in items:
        style = "success" if status == "OK" else "error"
        table.add_row(component, f"[{style}]{status}[/{style}]", detail)
    console.print(table)


def print_flashcard(front: str, back: str, card_num: int, total: int):
    """Print a flashcard for review."""
    console.print()
    console.print(
        Panel(
            f"[bold]{front}[/bold]",
            title=f"[title]Card {card_num}/{total}[/title]",
            subtitle="[meta]Press Enter to reveal[/meta]",
            border_style="magenta",
        )
    )


def print_flashcard_answer(back: str):
    """Print the answer side of a flashcard."""
    console.print(
        Panel(
            Markdown(back),
            title="[success]Answer[/success]",
            border_style="green",
        )
    )
