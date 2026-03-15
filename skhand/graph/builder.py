"""Build the Neo4j knowledge graph from ingested data."""

from __future__ import annotations

from neo4j import GraphDatabase

from skhand.config import get_settings
from skhand.graph.schema import SCHEMA_QUERIES, SEED_MAPPINGS
from skhand.utils.display import console


def get_driver():
    """Get a Neo4j driver instance."""
    settings = get_settings()
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )


def init_schema():
    """Create constraints and indexes in Neo4j."""
    driver = get_driver()
    with driver.session() as session:
        for query in SCHEMA_QUERIES:
            try:
                session.run(query)
            except Exception as e:
                console.print(f"[warning]Schema query skipped: {e}[/warning]")
    driver.close()
    console.print("[success]Graph schema initialized[/success]")


def seed_graph():
    """Seed the knowledge graph with known Sanskrit ↔ modern mappings."""
    driver = get_driver()

    with driver.session() as session:
        for mapping in SEED_MAPPINGS:
            s = mapping["sanskrit"]
            m = mapping["modern"]
            rel = mapping["rel"]
            rel_props = mapping.get("rel_props", {})

            # Merge Sanskrit node
            s_props = {**s.get("props", {}), "name": s["name"]}
            _merge_node(session, s["label"], s_props)

            # Merge Modern node
            m_props = {**m.get("props", {}), "name": m["name"]}
            _merge_node(session, m["label"], m_props)

            # Create relationship
            _merge_relationship(session, s["label"], s["name"], m["label"], m["name"], rel, rel_props)

    driver.close()
    console.print("[success]Seeded graph with known mappings[/success]")


def _merge_node(session, label: str, props: dict):
    """Merge a node into the graph."""
    name = props["name"]
    extra_props = {k: v for k, v in props.items() if k != "name"}

    set_clause = ""
    if extra_props:
        set_parts = [f"n.{k} = ${k}" for k in extra_props]
        set_clause = "SET " + ", ".join(set_parts)

    query = f"MERGE (n:{label} {{name: $name}}) {set_clause}"
    session.run(query, name=name, **extra_props)


def _merge_relationship(session, label1, name1, label2, name2, rel_type, props):
    """Merge a relationship between two nodes."""
    set_clause = ""
    if props:
        set_parts = [f"r.{k} = ${k}" for k in props]
        set_clause = "SET " + ", ".join(set_parts)

    query = (
        f"MATCH (a:{label1} {{name: $name1}}) "
        f"MATCH (b:{label2} {{name: $name2}}) "
        f"MERGE (a)-[r:{rel_type}]->(b) {set_clause}"
    )
    session.run(query, name1=name1, name2=name2, **props)


def create_node(label: str, name: str, properties: dict | None = None):
    """Create or update a single node."""
    props = {"name": name, **(properties or {})}
    driver = get_driver()
    with driver.session() as session:
        _merge_node(session, label, props)
    driver.close()


def create_relationship(
    label1: str, name1: str,
    label2: str, name2: str,
    rel_type: str, properties: dict | None = None,
):
    """Create or update a relationship."""
    driver = get_driver()
    with driver.session() as session:
        _merge_relationship(session, label1, name1, label2, name2, rel_type, properties or {})
    driver.close()


def get_node_count() -> int:
    """Get total number of nodes in the graph."""
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) AS count")
            count = result.single()["count"]
        driver.close()
        return count
    except Exception:
        return -1


def get_relationship_count() -> int:
    """Get total number of relationships in the graph."""
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) AS count")
            count = result.single()["count"]
        driver.close()
        return count
    except Exception:
        return -1
