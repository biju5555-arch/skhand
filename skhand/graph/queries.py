"""Graph query helpers for Neo4j."""

from __future__ import annotations

from neo4j import GraphDatabase

from skhand.config import get_settings
from skhand.utils.display import console


def _get_driver():
    settings = get_settings()
    return GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
    )


def get_equivalents(concept_name: str) -> list[dict]:
    """Find all modern equivalents of a Sanskrit concept (or vice versa)."""
    driver = _get_driver()
    results = []

    with driver.session() as session:
        # Search both directions
        query = """
        MATCH (a)-[r:EQUIVALENT_TO]-(b)
        WHERE toLower(a.name) CONTAINS toLower($name)
           OR toLower(b.name) CONTAINS toLower($name)
        RETURN a.name AS source, b.name AS target,
               labels(a) AS source_labels, labels(b) AS target_labels,
               r.confidence AS confidence, r.evidence AS evidence
        """
        records = session.run(query, name=concept_name)
        for record in records:
            results.append({
                "source": record["source"],
                "target": record["target"],
                "source_type": record["source_labels"][0] if record["source_labels"] else "",
                "target_type": record["target_labels"][0] if record["target_labels"] else "",
                "confidence": record["confidence"],
                "evidence": record["evidence"],
            })

    driver.close()
    return results


def shortest_path(name1: str, name2: str) -> list[dict] | None:
    """Find shortest path between two concepts."""
    driver = _get_driver()

    with driver.session() as session:
        query = """
        MATCH (a {name: $name1}), (b {name: $name2}),
              path = shortestPath((a)-[*..10]-(b))
        RETURN [n IN nodes(path) | n.name] AS names,
               [r IN relationships(path) | type(r)] AS rels
        """
        result = session.run(query, name1=name1, name2=name2)
        record = result.single()
        if record:
            driver.close()
            return {
                "nodes": record["names"],
                "relationships": record["rels"],
            }

    driver.close()
    return None


def get_concept_context(query: str) -> str:
    """Get formatted graph context for a query to include in synthesis prompts.

    Extracts key terms from the query and looks up their graph connections.
    """
    try:
        driver = _get_driver()
    except Exception:
        return ""

    context_parts = []

    with driver.session() as session:
        # Search for nodes matching words in the query
        result = session.run(
            """
            MATCH (n)
            WHERE ANY(word IN $words WHERE toLower(n.name) CONTAINS toLower(word))
            OPTIONAL MATCH (n)-[r]-(m)
            RETURN n.name AS name, labels(n) AS labels,
                   n.description AS desc, n.domain AS domain,
                   collect(DISTINCT {rel: type(r), target: m.name, conf: r.confidence}) AS connections
            LIMIT 10
            """,
            words=_extract_key_terms(query),
        )

        for record in result:
            name = record["name"]
            domain = record["domain"] or ""
            desc = record["desc"] or ""
            connections = [c for c in record["connections"] if c["target"]]

            entry = f"- {name} ({domain})"
            if desc:
                entry += f": {desc}"

            if connections:
                conn_strs = []
                for c in connections:
                    conf = f" [{c['conf']:.0%}]" if c["conf"] else ""
                    conn_strs.append(f"{c['rel']} -> {c['target']}{conf}")
                entry += "\n  Connections: " + "; ".join(conn_strs)

            context_parts.append(entry)

    driver.close()
    return "\n".join(context_parts) if context_parts else ""


def query_graph(concept_name: str) -> list[dict]:
    """General-purpose concept query for CLI display."""
    driver = _get_driver()
    results = []

    with driver.session() as session:
        query = """
        MATCH (n)
        WHERE toLower(n.name) CONTAINS toLower($name)
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n.name AS name, labels(n) AS labels,
               n.description AS desc, n.domain AS domain,
               n.sanskrit AS sanskrit,
               type(r) AS rel_type, m.name AS connected_to,
               labels(m) AS connected_labels,
               r.confidence AS confidence
        """
        records = session.run(query, name=concept_name)
        for record in records:
            results.append({
                "name": record["name"],
                "type": record["labels"][0] if record["labels"] else "",
                "description": record["desc"] or "",
                "domain": record["domain"] or "",
                "sanskrit": record["sanskrit"] or "",
                "relationship": record["rel_type"] or "",
                "connected_to": record["connected_to"] or "",
                "connected_type": record["connected_labels"][0] if record["connected_labels"] else "",
                "confidence": record["confidence"],
            })

    driver.close()
    return results


def _extract_key_terms(query: str) -> list[str]:
    """Extract key terms from a query for graph lookup."""
    # Simple approach: split on spaces, filter short/common words
    stop_words = {
        "what", "is", "the", "a", "an", "of", "and", "or", "how", "does",
        "do", "to", "in", "for", "with", "this", "that", "are", "was",
        "be", "been", "being", "have", "has", "had", "it", "its",
        "can", "could", "would", "should", "will", "may", "might",
    }
    words = query.replace("?", "").replace(",", "").split()
    return [w for w in words if w.lower() not in stop_words and len(w) > 2]
