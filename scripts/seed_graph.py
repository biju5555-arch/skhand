"""Seed the Neo4j knowledge graph with initial data."""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skhand.graph.builder import init_schema, seed_graph
from skhand.utils.display import console, print_header


def main():
    """Initialize schema and seed the graph."""
    print_header()
    console.print("\n[title]Seeding Knowledge Graph[/title]\n")

    try:
        console.print("[meta]Initializing schema...[/meta]")
        init_schema()

        console.print("[meta]Seeding mappings...[/meta]")
        seed_graph()

        console.print("\n[success]Graph seeded successfully![/success]")
        console.print("[meta]Open http://localhost:7474 to explore in Neo4j Browser[/meta]")
    except Exception as e:
        console.print(f"[error]Failed to seed graph: {e}[/error]")
        console.print("[meta]Is Neo4j running? Try: docker-compose up -d[/meta]")
        sys.exit(1)


if __name__ == "__main__":
    main()
