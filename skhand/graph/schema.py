"""Neo4j knowledge graph schema — node and edge type definitions."""

# Node labels
CONCEPT = "Concept"          # Abstract concept (e.g., "purification")
TEXT = "Text"                # Source text reference
SUBSTANCE = "Substance"      # Material substance (e.g., "Rajata Bhasma", "Silver nanoparticles")
PROCESS = "Process"          # A process/technique (e.g., "Marana", "Calcination")
PAPER = "Paper"              # Scientific paper reference

NODE_LABELS = [CONCEPT, TEXT, SUBSTANCE, PROCESS, PAPER]

# Relationship types
EQUIVALENT_TO = "EQUIVALENT_TO"       # Sanskrit concept ↔ modern equivalent
DESCRIBED_IN = "DESCRIBED_IN"         # Concept/substance → text/paper
COMPONENT_OF = "COMPONENT_OF"         # Substance → composite substance
USED_IN = "USED_IN"                   # Substance → process
PRODUCES = "PRODUCES"                 # Process → substance
RELATED_TO = "RELATED_TO"             # General semantic relation

RELATIONSHIP_TYPES = [
    EQUIVALENT_TO, DESCRIBED_IN, COMPONENT_OF,
    USED_IN, PRODUCES, RELATED_TO,
]

# Constraint creation queries
SCHEMA_QUERIES = [
    # Uniqueness constraints
    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{CONCEPT}) REQUIRE n.name IS UNIQUE",
    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{SUBSTANCE}) REQUIRE n.name IS UNIQUE",
    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{PROCESS}) REQUIRE n.name IS UNIQUE",
    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{TEXT}) REQUIRE n.name IS UNIQUE",
    f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{PAPER}) REQUIRE n.name IS UNIQUE",
    # Indexes
    f"CREATE INDEX IF NOT EXISTS FOR (n:{CONCEPT}) ON (n.domain)",
    f"CREATE INDEX IF NOT EXISTS FOR (n:{SUBSTANCE}) ON (n.domain)",
]

# Seed data: known Sanskrit ↔ modern mappings
SEED_MAPPINGS = [
    # (Sanskrit name, Sanskrit label, Modern name, Modern label, relationship properties)
    {
        "sanskrit": {"name": "Rajata Bhasma", "label": SUBSTANCE,
                      "props": {"domain": "ayurveda", "sanskrit": "रजत भस्म",
                                "description": "Calcined silver preparation used in Rasa Shastra"}},
        "modern": {"name": "Silver Nanoparticles", "label": SUBSTANCE,
                   "props": {"domain": "modern", "formula": "Ag NPs",
                             "description": "Nanoscale silver particles with antimicrobial properties"}},
        "rel": EQUIVALENT_TO,
        "rel_props": {"confidence": 0.85, "evidence": "Structural and compositional analysis"},
    },
    {
        "sanskrit": {"name": "Tamra Bhasma", "label": SUBSTANCE,
                      "props": {"domain": "ayurveda", "sanskrit": "ताम्र भस्म",
                                "description": "Calcined copper preparation"}},
        "modern": {"name": "Copper Nanoparticles", "label": SUBSTANCE,
                   "props": {"domain": "modern", "formula": "Cu NPs",
                             "description": "Nanoscale copper particles"}},
        "rel": EQUIVALENT_TO,
        "rel_props": {"confidence": 0.80, "evidence": "XRD and TEM analysis of Tamra Bhasma"},
    },
    {
        "sanskrit": {"name": "Chandrarka Rasa", "label": SUBSTANCE,
                      "props": {"domain": "ayurveda", "sanskrit": "चन्द्रार्क रस",
                                "description": "Cu-Ag bimetallic preparation from Rasaratna Samuccaya"}},
        "modern": {"name": "Cu-Ag Bimetallic Nanoparticles", "label": SUBSTANCE,
                   "props": {"domain": "modern", "formula": "Cu-Ag NPs",
                             "description": "Bimetallic copper-silver nanoparticles with synergistic antimicrobial activity"}},
        "rel": EQUIVALENT_TO,
        "rel_props": {"confidence": 0.75, "evidence": "Compositional similarity, Rasaratna Samuccaya 8.23"},
    },
    {
        "sanskrit": {"name": "Marana", "label": PROCESS,
                      "props": {"domain": "ayurveda", "sanskrit": "मारण",
                                "description": "Incineration/calcination process to convert metals to bhasma"}},
        "modern": {"name": "Calcination", "label": PROCESS,
                   "props": {"domain": "modern",
                             "description": "Thermal treatment to convert substances to oxides/fine particles"}},
        "rel": EQUIVALENT_TO,
        "rel_props": {"confidence": 0.90, "evidence": "Process similarity confirmed by thermal analysis"},
    },
    {
        "sanskrit": {"name": "Shodhana", "label": PROCESS,
                      "props": {"domain": "ayurveda", "sanskrit": "शोधन",
                                "description": "Purification process involving repeated washing/heating with herbal media"}},
        "modern": {"name": "Purification", "label": PROCESS,
                   "props": {"domain": "modern",
                             "description": "Removal of impurities from materials through chemical/physical methods"}},
        "rel": EQUIVALENT_TO,
        "rel_props": {"confidence": 0.85, "evidence": "Functional equivalence in removing toxic impurities"},
    },
    # Component relationships
    {
        "sanskrit": {"name": "Rajata Bhasma", "label": SUBSTANCE, "props": {}},
        "modern": {"name": "Chandrarka Rasa", "label": SUBSTANCE, "props": {}},
        "rel": COMPONENT_OF,
        "rel_props": {"role": "silver component"},
    },
    {
        "sanskrit": {"name": "Tamra Bhasma", "label": SUBSTANCE, "props": {}},
        "modern": {"name": "Chandrarka Rasa", "label": SUBSTANCE, "props": {}},
        "rel": COMPONENT_OF,
        "rel_props": {"role": "copper component"},
    },
]
