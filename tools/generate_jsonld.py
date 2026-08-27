#!/usr/bin/env python3
"""
NCCR DATMM — JSON-LD Generator
==============================
Reads the DATMM Turtle files and produces JSON-LD output for ingestion
into the NLM Dataset Catalog. Generates:

  1. One combined file (nccr-datmm.jsonld) with all records in a flat @graph
  2. One JSON-LD file per dataset (nccr-<id>.jsonld) — each a self-contained
     record including its dataset, documentation, referenced concepts, and
     the shared repository + SEER contribution.

Output goes to the datmm-jsonld/ folder.

Usage:
    python tools/generate_jsonld.py

Requirements:
    pip install rdflib
"""

import json
from pathlib import Path

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

# ============================================================
# Configuration
# ============================================================

REPO_ROOT = Path(__file__).parent.parent
DATMM_DIR = REPO_ROOT / "datmm"
OUTPUT_DIR = REPO_ROOT / "datmm-jsonld"

DATMM = Namespace("http://id.nlm.nih.gov/datmm/")
DCT = Namespace("http://purl.org/dc/terms/")
BF = Namespace("http://id.loc.gov/ontologies/bibframe/")

# JSON-LD @context shared by all output files
CONTEXT = {
    "datmm": "http://id.nlm.nih.gov/datmm/",
    "dct": "http://purl.org/dc/terms/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "bf": "http://id.loc.gov/ontologies/bibframe/",
    "adms": "http://www.w3.org/ns/adms#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
}

# Dataset id -> source TTL filename
DATASET_FILES = {
    "nccr-ctc": "ctc.ttl",
    "nccr-abm": "abm.ttl",
    "nccr-ccdi": "ccdi.ttl",
    "nccr-cog": "cog.ttl",
    "nccr-mcd": "mcd.ttl",
    "nccr-mce": "mce.ttl",
    "nccr-mcp": "mcp.ttl",
    "nccr-pharm": "pharm.ttl",
    "nccr-ro": "ro.ttl",
}

SHARED_FILES = ["repository.ttl", "agents.ttl", "concepts.ttl"]


# ============================================================
# Helpers
# ============================================================

def load_full_graph() -> Graph:
    """Load all DATMM Turtle files into a single graph."""
    g = Graph()
    for ttl in sorted(DATMM_DIR.glob("*.ttl")):
        g.parse(str(ttl), format="turtle")
    return g


def graph_to_jsonld(g: Graph) -> dict:
    """Serialize a graph to a JSON-LD dict with our shared @context."""
    # rdflib produces an expanded @graph; we re-wrap with our compact context
    raw = g.serialize(format="json-ld", context=CONTEXT, auto_compact=True)
    return json.loads(raw)


def build_combined() -> dict:
    """Build the combined JSON-LD document (all records)."""
    g = load_full_graph()
    doc = graph_to_jsonld(g)
    return doc


def build_per_dataset(dataset_id: str, dataset_file: str) -> dict:
    """Build a self-contained JSON-LD document for one dataset.

    Includes: the dataset + its documentation, the shared repository,
    the SEER agent + contribution, and only the concepts this dataset
    references via dct:subject.
    """
    g = Graph()
    # Load the dataset file (contains dataset + its documentation)
    g.parse(str(DATMM_DIR / dataset_file), format="turtle")
    # Load shared repository + agents (contribution)
    g.parse(str(DATMM_DIR / "repository.ttl"), format="turtle")
    g.parse(str(DATMM_DIR / "agents.ttl"), format="turtle")

    # Load the full concepts graph, then copy over only referenced concepts
    concepts_g = Graph()
    concepts_g.parse(str(DATMM_DIR / "concepts.ttl"), format="turtle")

    dataset_uri = DATMM[f"dataset/{dataset_id}"]
    referenced = list(g.objects(dataset_uri, DCT.subject))
    for concept in referenced:
        for p, o in concepts_g.predicate_objects(concept):
            g.add((concept, p, o))

    return graph_to_jsonld(g)


# ============================================================
# Main
# ============================================================

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("NCCR DATMM JSON-LD Generator")
    print("=" * 40)

    # 1. Combined document
    combined = build_combined()
    combined_path = OUTPUT_DIR / "nccr-datmm.jsonld"
    combined_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    node_count = len(combined.get("@graph", [])) if "@graph" in combined else 1
    print(f"  Combined: {combined_path.name} ({node_count} nodes)")

    # 2. Per-dataset documents
    for dataset_id, dataset_file in DATASET_FILES.items():
        doc = build_per_dataset(dataset_id, dataset_file)
        out_path = OUTPUT_DIR / f"{dataset_id}.jsonld"
        out_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        nodes = len(doc.get("@graph", [])) if "@graph" in doc else 1
        print(f"  Dataset:  {out_path.name} ({nodes} nodes)")

    print(f"\nOutput written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
