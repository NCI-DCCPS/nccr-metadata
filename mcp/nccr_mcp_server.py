#!/usr/bin/env python3
"""
NCCR Metadata MCP Server
========================
Exposes the National Childhood Cancer Registry (NCCR) Data Platform metadata
as Model Context Protocol (MCP) tools, so an AI assistant in any MCP-capable
client (Claude Desktop, Cursor, Windsurf, VS Code, Kiro) can answer grounded
questions about NCCR data — what datasources exist, what variables can be
filtered, what values and frequencies are present, and can build portable
cohort definitions.

All data comes from the PUBLISHED metadata (RDF/Turtle). No authentication and
no patient-level data access are required.

Run:
    python nccr_mcp_server.py

Requirements:
    pip install mcp rdflib
"""

import json
import re
import urllib.request
import uuid
from datetime import datetime
from pathlib import Path

from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, SKOS, XSD

from mcp.server.mcpserver import MCPServer

# ============================================================
# Namespaces
# ============================================================

NCCR = Namespace("https://nccrdataplatform.ccdi.cancer.gov/vocab#")
NCCR_DS = Namespace("https://nccrdataplatform.ccdi.cancer.gov/datasource/")
NCCR_FLT = Namespace("https://nccrdataplatform.ccdi.cancer.gov/filter/")
DATMM = Namespace("http://id.nlm.nih.gov/datmm/")
DCT = Namespace("http://purl.org/dc/terms/")
BF = Namespace("http://id.loc.gov/ontologies/bibframe/")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")

# ============================================================
# Data source locations (local first, then GitHub raw)
# ============================================================

# The metadata is the sibling content of this repo (mcp/ lives inside
# nccr-metadata/). REPO_ROOT therefore points at the repo root where
# nccr_instances.ttl, nccr_vocab.ttl, and datmm/ live — the source of truth.
REPO_ROOT = Path(__file__).parent.parent
RAW_BASE = "https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main"

# Local candidate paths (published repo layout preferred; GitHub raw fallback)
LOCAL_INSTANCES = [
    REPO_ROOT / "nccr_instances.ttl",
]
LOCAL_VOCAB = [
    REPO_ROOT / "nccr_vocab.ttl",
]
LOCAL_DATMM_DIR = [
    REPO_ROOT / "datmm",
]

# Report JSONs (for high-cardinality frequency fallback, e.g., drug names).
# These are NOT stored in the repo; the server fetches them from the live
# platform when a high-cardinality query needs them.
REPORT_SOURCES = {
    "CTC": "ctcReport.json", "ABM": "abmReport.json", "CCDI": "ccdiReport.json",
    "COG": "cogReport.json", "MCD": "mcdReport.json", "MCE": "mceReport.json",
    "MCP": "mcpReport.json", "PHARM": "pharmReport.json", "RO": "roReport.json",
}
REPORT_BASE_URL = "https://nccrdataplatform.ccdi.cancer.gov/data/json/"
LOCAL_REPORT_DIR = [REPO_ROOT / "source-data"]  # optional; usually not present


# ============================================================
# Graph loading (lazy, cached)
# ============================================================

_graph: Graph | None = None


def _first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None


def get_graph() -> Graph:
    """Load and cache the combined NCCR graph (vocab + instances + datmm)."""
    global _graph
    if _graph is not None:
        return _graph

    g = Graph()

    # Instances (required)
    inst = _first_existing(LOCAL_INSTANCES)
    if inst:
        g.parse(str(inst), format="turtle")
    else:
        g.parse(f"{RAW_BASE}/nccr_instances.ttl", format="turtle")

    # Vocab (optional but useful)
    vocab = _first_existing(LOCAL_VOCAB)
    if vocab:
        g.parse(str(vocab), format="turtle")
    else:
        try:
            g.parse(f"{RAW_BASE}/nccr_vocab.ttl", format="turtle")
        except Exception:
            pass

    # DATMM catalog files (optional)
    datmm_dir = _first_existing(LOCAL_DATMM_DIR)
    if datmm_dir:
        for ttl in sorted(datmm_dir.glob("*.ttl")):
            g.parse(str(ttl), format="turtle")
    else:
        for name in ["repository", "agents", "concepts", "ctc", "abm", "ccdi",
                     "cog", "mcd", "mce", "mcp", "pharm", "ro"]:
            try:
                g.parse(f"{RAW_BASE}/datmm/{name}.ttl", format="turtle")
            except Exception:
                pass

    _graph = g
    return g


def slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")


# ============================================================
# MCP server
# ============================================================

mcp = MCPServer("nccr-metadata")


@mcp.tool()
def list_datasources() -> str:
    """List all 9 NCCR datasources with their total record counts and the number
    of filterable variables each has. Use this to get an overview of what data
    the NCCR Data Platform contains."""
    g = get_graph()
    q = """
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?id ?label ?count (COUNT(DISTINCT ?f) as ?filters) WHERE {
        ?ds a nccr:DataSource ;
            nccr:sourceId ?id ;
            rdfs:label ?label .
        OPTIONAL { ?ds nccr:totalRecordCount ?count . }
        OPTIONAL { ?v nccr:belongsToSource ?ds ; nccr:boundToFilter ?f . }
    }
    GROUP BY ?id ?label ?count
    ORDER BY DESC(?count)
    """
    rows = []
    for r in g.query(q):
        rows.append({
            "id": str(r.id),
            "name": str(r.label),
            "records": int(r["count"]) if r["count"] else None,
            "filter_count": int(r.filters) if r.filters else 0,
        })
    return json.dumps({"datasources": rows}, indent=2)


@mcp.tool()
def discover_filters(datasource: str) -> str:
    """List the filterable variables (cohort filters) for a given datasource.
    Each filter has a control title, a filter type (EQUALS, MIN, or MAX), and the
    underlying variable it operates on. Use this to learn how a researcher can
    subset patients in a datasource.

    Args:
        datasource: The datasource ID, e.g. 'CTC', 'PHARM', 'RO', 'COG', 'CCDI'.
    """
    g = get_graph()
    q = f"""
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?varLabel ?title ?type WHERE {{
        ?var a nccr:Variable ;
             rdfs:label ?varLabel ;
             nccr:belongsToSource ?ds ;
             nccr:boundToFilter ?filter .
        ?ds nccr:sourceId ?id .
        ?filter nccr:filterControlTitle ?title ;
                nccr:filterType ?type .
        FILTER(UCASE(?id) = UCASE("{datasource}"))
    }}
    ORDER BY ?title
    """
    rows = [{"filter": str(r.title), "type": str(r.type), "variable": str(r.varLabel)}
            for r in g.query(q)]
    if not rows:
        return json.dumps({
            "datasource": datasource.upper(),
            "filters": [],
            "note": "No filterable variables found. Check the datasource ID with list_datasources."
        }, indent=2)
    return json.dumps({"datasource": datasource.upper(), "filters": rows}, indent=2)


@mcp.tool()
def get_values(variable: str) -> str:
    """Get the permissible values for a variable, with observed record counts
    where available. Matches by the variable's display name or its filter control
    title (e.g. 'Sex', 'Race/Ethnicity', 'ICCC Major (Level 1)', 'Vital Status').
    Counts below 16 are suppressed for privacy.

    Args:
        variable: The variable label or filter control title.
    """
    g = get_graph()
    q = f"""
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?dsLabel ?varLabel ?code ?description ?count WHERE {{
        ?var a nccr:Variable ;
             rdfs:label ?varLabel ;
             nccr:belongsToSource/rdfs:label ?dsLabel ;
             nccr:hasValueSet/nccr:hasCodeValue ?cv .
        ?cv skos:notation ?code .
        OPTIONAL {{ ?cv skos:prefLabel ?description . }}
        OPTIONAL {{ ?cv nccr:recordCount ?count . }}
        OPTIONAL {{ ?var nccr:boundToFilter ?flt . ?flt nccr:filterControlTitle ?ftitle . }}
        FILTER(LCASE(?varLabel) = LCASE("{variable}") || LCASE(COALESCE(?ftitle, "")) = LCASE("{variable}"))
    }}
    ORDER BY DESC(?count)
    """
    rows = list(g.query(q))
    if not rows:
        return json.dumps({
            "variable": variable,
            "values": [],
            "note": "No coded values found. For high-cardinality fields (e.g. drug names), try top_values with the source column name."
        }, indent=2)

    var_label = str(rows[0].varLabel)
    ds_label = str(rows[0].dsLabel)
    values = []
    for r in rows:
        values.append({
            "code": str(r.code),
            "description": str(r.description) if r.description else None,
            "records": int(r["count"]) if r["count"] else None,
        })
    return json.dumps({"variable": var_label, "datasource": ds_label, "values": values}, indent=2)


def _report_top(field_name: str, limit: int, datasource: str | None):
    """Read top values from Report JSON files (local or live) for high-cardinality fields."""
    local_dir = _first_existing(LOCAL_REPORT_DIR)
    sources = ({datasource.upper(): REPORT_SOURCES[datasource.upper()]}
               if datasource and datasource.upper() in REPORT_SOURCES else REPORT_SOURCES)

    for ds_id, filename in sources.items():
        report = None
        if local_dir and (local_dir / filename).exists():
            try:
                report = json.loads((local_dir / filename).read_text(encoding="utf-8"))
            except Exception:
                report = None
        if report is None:
            try:
                with urllib.request.urlopen(REPORT_BASE_URL + filename, timeout=10) as resp:
                    report = json.load(resp)
            except Exception:
                continue

        for field in report.get("fields", []):
            fn = field.get("fieldName", "")
            if (fn.lower() == field_name.lower()
                    or field_name.lower() in fn.lower()
                    or fn.lower() in field_name.lower()):
                values = field["charts"][0]["values"] if field.get("charts") else []
                out = []
                for v in values[:limit]:
                    if not isinstance(v, list) or len(v) < 3:
                        continue
                    label_info = v[1] if isinstance(v[1], dict) else {}
                    label = str(label_info.get("label", v[0])) if label_info else str(v[0])
                    out.append({"value": label, "records": v[2]})
                return {"variable": fn, "datasource": ds_id,
                        "total_records": report.get("totalCount"), "values": out}
    return None


@mcp.tool()
def top_values(field: str, limit: int = 20, datasource: str = "") -> str:
    """Get the most common values for any variable, ranked by record count. Works
    for high-cardinality fields that get_values can't return, such as drug names
    ('canmedNonProprietaryName'), primary cancer sites ('primarySite'), or
    radiation types ('radiation_therapy_type').

    Args:
        field: The variable label or source column name.
        limit: Max number of values to return (default 20).
        datasource: Optional datasource ID to scope the search (e.g. 'PHARM').
    """
    g = get_graph()
    ds = datasource or None

    # Try the graph first (coded values with counts)
    q = f"""
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?dsLabel ?varLabel ?code ?description ?count WHERE {{
        ?var a nccr:Variable ;
             rdfs:label ?varLabel ;
             nccr:sourceColumn ?col ;
             nccr:belongsToSource ?dsn ;
             nccr:hasValueSet/nccr:hasCodeValue ?cv .
        ?dsn rdfs:label ?dsLabel ; nccr:sourceId ?id .
        ?cv skos:notation ?code ; nccr:recordCount ?count .
        OPTIONAL {{ ?cv skos:prefLabel ?description . }}
        FILTER(LCASE(?varLabel) = LCASE("{field}") || LCASE(?col) = LCASE("{field}")
               || CONTAINS(LCASE(?varLabel), LCASE("{field}")) || CONTAINS(LCASE(?col), LCASE("{field}")))
        {f'FILTER(UCASE(?id) = UCASE("{ds}"))' if ds else ''}
    }}
    ORDER BY DESC(?count)
    LIMIT {limit}
    """
    rows = list(g.query(q))
    if rows:
        return json.dumps({
            "variable": str(rows[0].varLabel),
            "datasource": str(rows[0].dsLabel),
            "values": [{"value": str(r.description or r.code), "records": int(r["count"])}
                       for r in rows],
        }, indent=2)

    # Fallback: Report JSON (high-cardinality fields)
    result = _report_top(field, limit, ds)
    if result:
        return json.dumps(result, indent=2)

    return json.dumps({"field": field, "values": [],
                       "note": "No frequency data found. Try list_datasources or discover_filters first."}, indent=2)


@mcp.tool()
def search_by_subject(mesh_term: str) -> str:
    """Find which NCCR datasets are tagged with a given subject (MeSH term).
    Every dataset carries 'Pediatrics' and 'Neoplasms' plus a dataset-specific
    subject. Useful for topic-based discovery, e.g. 'Radiation Oncology',
    'Drug Prescriptions', 'Socioeconomic Factors', 'Clinical Trials as Topic'.

    Args:
        mesh_term: A subject label to search for (partial match allowed).
    """
    g = get_graph()
    q = f"""
    PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?dsTitle ?subjLabel ?meshId WHERE {{
        ?ds a datmm:Dataset ;
            dct:title ?dsTitle ;
            dct:subject ?concept .
        ?concept rdfs:label ?subjLabel ;
                 dct:identifier ?meshId .
        FILTER(CONTAINS(LCASE(?subjLabel), LCASE("{mesh_term}")))
    }}
    ORDER BY ?dsTitle
    """
    rows = [{"dataset": str(r.dsTitle), "subject": str(r.subjLabel), "mesh": str(r.meshId)}
            for r in g.query(q)]
    return json.dumps({"query": mesh_term, "matches": rows}, indent=2)


@mcp.tool()
def get_dataset_info(dataset_id: str) -> str:
    """Get the DATMM catalog description of a dataset: title, description, access
    rights, homepage, contributor, and subjects. Use this for a full profile of
    one datasource.

    Args:
        dataset_id: Short ID such as 'ctc', 'abm', 'pharm', 'ro', 'cog', 'ccdi',
                    'mcd', 'mce', 'mcp' (with or without the 'nccr-' prefix).
    """
    g = get_graph()
    did = dataset_id if dataset_id.startswith("nccr-") else f"nccr-{dataset_id.lower()}"
    ds = DATMM[f"dataset/{did}"]

    title = next(g.objects(ds, DCT.title), None)
    if title is None:
        return json.dumps({"dataset_id": dataset_id, "error": "Not found. Use a valid ID like 'ctc' or 'pharm'."}, indent=2)

    subjects = []
    for c in g.objects(ds, DCT.subject):
        lbl = next(g.objects(c, RDFS.label), None)
        mid = next(g.objects(c, DCT.identifier), None)
        subjects.append({"label": str(lbl) if lbl else None, "mesh": str(mid) if mid else None})

    contributor = None
    for contrib in g.objects(ds, BF.contribution):
        for agent in g.objects(contrib, BF.agent):
            nm = next(g.objects(agent, FOAF.name), None)
            contributor = str(nm) if nm else None

    info = {
        "id": did,
        "title": str(title),
        "alternative": [str(a) for a in g.objects(ds, DCT.alternative)],
        "description": str(next(g.objects(ds, DCT.description), "")),
        "rights": str(next(g.objects(ds, DCT.rights), "")),
        "homepage": str(next(g.objects(ds, FOAF.homepage), "")),
        "contributor": contributor,
        "subjects": subjects,
    }
    return json.dumps(info, indent=2)


@mcp.tool()
def build_cohort(name: str, datasources: list[str], filters: list[dict]) -> str:
    """Build a portable cohort definition as RDF/Turtle. The result is a
    self-describing file a researcher can save, share, or attach to a publication.

    Args:
        name: A name for the cohort, e.g. 'Pediatric CNS Tumors 0-14'.
        datasources: Datasource IDs to include, e.g. ['CTC', 'RO', 'PHARM'].
                     CTC is always included automatically.
        filters: A list of filter criteria. Each item is a dict like:
                 {"filter": "Min Age (Yrs)", "values": [7]} or
                 {"filter": "Sex", "values": ["ALL"]} or
                 {"filter": "ICCC Major (Level 1)", "values": ["01","02"]}.
    """
    g = Graph()
    g.bind("nccr", NCCR)
    g.bind("nccr-ds", NCCR_DS)
    g.bind("nccr-flt", NCCR_FLT)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)

    cohort_uri = URIRef(f"urn:nccr:cohort:{uuid.uuid4()}")
    g.add((cohort_uri, RDF.type, NCCR.CohortDefinition))
    g.add((cohort_uri, NCCR.cohortName, Literal(name)))
    g.add((cohort_uri, NCCR.cohortCreated, Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

    ds_ids = list(dict.fromkeys(["CTC"] + [d.upper() for d in datasources]))
    for d in ds_ids:
        g.add((cohort_uri, NCCR.includesSource, NCCR_DS[d.lower()]))

    for crit in filters:
        title = crit.get("filter", "")
        values = crit.get("values", [])
        bnode = BNode()
        g.add((cohort_uri, NCCR.hasFilterCriterion, bnode))
        g.add((bnode, RDF.type, NCCR.FilterCriterion))
        g.add((bnode, NCCR.appliesFilter, NCCR_FLT[title.replace(" ", "")]))
        if any(str(v).upper() in ("ALL", "ALL_VALUES") for v in values):
            g.add((bnode, NCCR.allValuesSelected, Literal(True, datatype=XSD.boolean)))
        else:
            for v in values:
                if isinstance(v, (int, float)):
                    g.add((bnode, NCCR.filterNumericValue, Literal(v, datatype=XSD.decimal)))
                else:
                    g.add((bnode, NCCR.filterStringValue, Literal(str(v))))

    turtle = g.serialize(format="turtle")
    return turtle


if __name__ == "__main__":
    mcp.run()
