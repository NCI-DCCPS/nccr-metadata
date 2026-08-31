#!/usr/bin/env python3
"""
NCCR DATMM — JSON-LD Generator
==============================
Reads the DATMM Turtle files (the source of truth) and produces
JSON-LD for ingestion into the NLM Dataset Catalog.

The output matches the nested structure expected by NLM:
  - One datmm:Dataset node per file acts as the container.
  - datmm:Repository is nested under dct:isPartOf (with its own subjects).
  - bf:Contribution is nested under bf:contribution (agent nested inside).
  - Subject concepts are nested inline under dct:subject.
  - datmm:Documentation (articles) nested under dct:isReferencedBy.
  - No @id fields — the Dataset Catalog mints its own internal URIs.

Turtle remains the source of truth; regenerate this output whenever the
Turtle files change (e.g., an annual data refresh).

Output: datmm-jsonld/  (one file per dataset + a combined file)

Usage:
    python tools/generate_jsonld.py

Requirements:
    pip install rdflib
"""

import json
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

# ============================================================
# Configuration
# ============================================================

REPO_ROOT = Path(__file__).parent.parent
DATMM_DIR = REPO_ROOT / "datmm"
OUTPUT_DIR = REPO_ROOT / "datmm-jsonld"

DATMM = Namespace("http://id.nlm.nih.gov/datmm/")
DCT = Namespace("http://purl.org/dc/terms/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
BF = Namespace("http://id.loc.gov/ontologies/bibframe/")
ADMS = Namespace("http://www.w3.org/ns/adms#")

# JSON-LD @context — matches the structure NLM provided
CONTEXT = {
    "@vocab": "http://schema.org/",
    "datmm": "http://id.nlm.nih.gov/datmm/",
    "schema": "http://schema.org/",
    "dct": "http://purl.org/dc/terms/",
    "foaf": "http://xmlns.com/foaf/0.1/",
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "bf": "http://id.loc.gov/ontologies/bibframe/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "org": "http://www.w3.org/ns/org#",
    "adms": "http://www.w3.org/ns/adms#",
}

DATASET_IDS = [
    "nccr-ctc", "nccr-abm", "nccr-ccdi", "nccr-cog",
    "nccr-mcd", "nccr-mce", "nccr-mcp", "nccr-pharm", "nccr-ro",
]

REPO_URI = DATMM["repository/nccr-data-platform"]


# ============================================================
# Helpers to read single-valued / multi-valued literals
# ============================================================

def _lit(g: Graph, subj, pred):
    """Return the first object as a plain string (or None)."""
    for o in g.objects(subj, pred):
        return str(o)
    return None


def _all(g: Graph, subj, pred):
    """Return all objects as a list of strings."""
    return [str(o) for o in g.objects(subj, pred)]


def concept_node(g: Graph, concept_uri) -> dict:
    """Build a nested skos:Concept object (no @id)."""
    node = {"@type": "skos:Concept"}
    ident = _lit(g, concept_uri, DCT.identifier)
    if ident:
        node["dct:identifier"] = ident
    scheme = _lit(g, concept_uri, SKOS.inScheme)
    if scheme:
        node["skos:inScheme"] = scheme
    label = _lit(g, concept_uri, RDFS.label)
    if label:
        node["rdfs:label"] = label
    source = _lit(g, concept_uri, DCT.source)
    if source:
        node["dct:source"] = source
    return node


def repository_node(g: Graph) -> dict:
    """Build the nested datmm:Repository object."""
    node = {
        "@type": "datmm:Repository",
        "dct:identifier": None,  # NLM assigns a linked-data URI on ingestion
        "dct:title": _lit(g, REPO_URI, DCT.title),
        "foaf:homepage": _lit(g, REPO_URI, FOAF.homepage),
        "dct:alternative": _all(g, REPO_URI, DCT.alternative),
    }
    # Repository-level subjects (shared: Pediatrics + Neoplasms)
    subjects = [concept_node(g, s) for s in g.objects(REPO_URI, DCT.subject)]
    # Order by MeSH id for stable output
    subjects.sort(key=lambda c: c.get("rdfs:label", ""))
    node["dct:subject"] = subjects
    return node


def contribution_nodes(g: Graph, dataset_uri) -> list:
    """Build nested bf:Contribution objects (agent nested inside)."""
    result = []
    for contrib in g.objects(dataset_uri, BF.contribution):
        c = {"@type": "bf:Contribution"}
        roles = _all(g, contrib, BF.role)
        if roles:
            c["bf:role"] = roles
        # Agent
        for agent in g.objects(contrib, BF.agent):
            a = {"@type": "foaf:Agent"}
            aid = _lit(g, agent, DCT.identifier)
            if aid:
                a["dct:identifier"] = aid
            aname = _lit(g, agent, FOAF.name)
            if aname:
                a["foaf:name"] = aname
            c["bf:agent"] = a
        result.append(c)
    return result


def documentation_nodes(g: Graph, dataset_uri) -> list:
    """Build nested datmm:Documentation objects (published articles)."""
    result = []
    for doc in g.objects(dataset_uri, DCT.isReferencedBy):
        d = {"@type": "datmm:Documentation"}
        dtype = _lit(g, doc, DCT.type)
        if dtype:
            d["dct:type"] = dtype
        idents = _all(g, doc, DCT.identifier)
        if idents:
            d["dct:identifier"] = idents
        title = _lit(g, doc, DCT.title)
        if title:
            d["dct:title"] = title
        citation = _lit(g, doc, DCT.bibliographicCitation)
        d["dct:bibliographicCitation"] = citation  # may be None
        hp = _lit(g, doc, FOAF.homepage)
        if hp:
            d["foaf:homepage"] = hp
        result.append(d)
    return result


def dataset_node(g: Graph, dataset_id: str) -> dict:
    """Build the full nested datmm:Dataset object for one dataset."""
    ds = DATMM[f"dataset/{dataset_id}"]

    node = {"@type": "datmm:Dataset"}

    ident = _lit(g, ds, DCT.identifier)
    node["dct:identifier"] = [ident] if ident else []
    node["dct:title"] = _lit(g, ds, DCT.title)
    node["dct:alternative"] = _all(g, ds, DCT.alternative)
    node["foaf:homepage"] = _lit(g, ds, FOAF.homepage)
    node["dct:description"] = _lit(g, ds, DCT.description)
    node["dct:language"] = _lit(g, ds, DCT.language)
    rights = _lit(g, ds, DCT.rights)
    node["dct:rights"] = [rights] if rights else []
    status = _lit(g, ds, ADMS.status)
    if status:
        node["adms:status"] = status

    # Nested repository (under dct:isPartOf)
    node["dct:isPartOf"] = [repository_node(g)]

    # Nested contributions
    node["bf:contribution"] = contribution_nodes(g, ds)

    # Dataset-level subjects (all 3, nested inline)
    subjects = [concept_node(g, s) for s in g.objects(ds, DCT.subject)]
    subjects.sort(key=lambda c: c.get("rdfs:label", ""))
    node["dct:subject"] = subjects

    # Documentation (articles) if any
    docs = documentation_nodes(g, ds)
    if docs:
        node["dct:isReferencedBy"] = docs

    return node


# ============================================================
# Main
# ============================================================

def load_graph() -> Graph:
    g = Graph()
    for ttl in sorted(DATMM_DIR.glob("*.ttl")):
        g.parse(str(ttl), format="turtle")
    return g


def wrap(nodes) -> dict:
    """Wrap one or more dataset nodes in a @context + @graph document."""
    if not isinstance(nodes, list):
        nodes = [nodes]
    return {"@context": CONTEXT, "@graph": nodes}


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    g = load_graph()

    print("NCCR DATMM JSON-LD Generator")
    print("=" * 40)

    all_nodes = []
    for dataset_id in DATASET_IDS:
        node = dataset_node(g, dataset_id)
        all_nodes.append(node)
        doc = wrap(node)
        out_path = OUTPUT_DIR / f"{dataset_id}.jsonld"
        out_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
        n_subj = len(node.get("dct:subject", []))
        has_doc = "yes" if "dct:isReferencedBy" in node else "no"
        print(f"  {dataset_id}.jsonld  (subjects={n_subj}, article={has_doc})")

    # Combined document with all 9 datasets
    combined = wrap(all_nodes)
    combined_path = OUTPUT_DIR / "nccr-datmm.jsonld"
    combined_path.write_text(json.dumps(combined, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Combined: nccr-datmm.jsonld ({len(all_nodes)} datasets)")
    print(f"\nOutput written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
