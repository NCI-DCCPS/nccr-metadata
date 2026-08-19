#!/usr/bin/env python3
"""
NCCR Cohort Discovery & Builder
=================================
A command-line tool that queries the published NCCR metadata to:
1. Discover what filters are available per datasource
2. Show permissible values and their frequencies
3. Build a cohort definition as RDF (Turtle) ready for platform import

Usage:
    python cohort_builder.py discover           # Show all filterable variables
    python cohort_builder.py values Sex         # Show values for a filter
    python cohort_builder.py build              # Interactive cohort builder
    python cohort_builder.py build --output my_cohort.ttl

Requirements:
    pip install rdflib
"""

import argparse
import json
import sys
import uuid
from datetime import datetime
from pathlib import Path

from rdflib import Graph, Namespace, Literal, URIRef, BNode
from rdflib.namespace import RDF, RDFS, XSD, SKOS

# ============================================================
# Namespaces
# ============================================================

NCCR = Namespace("https://nccrdataplatform.ccdi.cancer.gov/vocab#")
NCCR_DS = Namespace("https://nccrdataplatform.ccdi.cancer.gov/datasource/")
NCCR_FLT = Namespace("https://nccrdataplatform.ccdi.cancer.gov/filter/")

# ============================================================
# Data loading
# ============================================================

INSTANCES_URL = "https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_instances.ttl"

# Try local file first, fall back to remote
LOCAL_INSTANCES = Path(__file__).parent.parent / "nccr_instances.ttl"
LOCAL_INSTANCES_ALT = Path(__file__).parent.parent / "output" / "nccr_instances.ttl"


def load_graph() -> Graph:
    """Load the NCCR instances graph."""
    g = Graph()
    if LOCAL_INSTANCES.exists():
        print(f"Loading from local: {LOCAL_INSTANCES.name}")
        g.parse(str(LOCAL_INSTANCES), format="turtle")
    elif LOCAL_INSTANCES_ALT.exists():
        print(f"Loading from local: {LOCAL_INSTANCES_ALT}")
        g.parse(str(LOCAL_INSTANCES_ALT), format="turtle")
    else:
        print(f"Loading from GitHub (this may take a moment)...")
        g.parse(INSTANCES_URL, format="turtle")
    print(f"Loaded {len(g)} triples\n")
    return g


# ============================================================
# Discovery commands
# ============================================================

def cmd_discover(g: Graph, datasource: str | None = None):
    """Show all filterable variables, optionally filtered by datasource."""
    ds_filter = ""
    if datasource:
        ds_filter = f'FILTER(UCASE(?dsId) = "{datasource.upper()}")'

    query = f"""
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?dsLabel ?varLabel ?filterTitle ?filterType WHERE {{
        ?var a nccr:Variable ;
             rdfs:label ?varLabel ;
             nccr:belongsToSource ?ds ;
             nccr:boundToFilter ?filter .
        ?ds rdfs:label ?dsLabel ;
            nccr:sourceId ?dsId .
        ?filter nccr:filterControlTitle ?filterTitle ;
                nccr:filterType ?filterType .
        {ds_filter}
    }}
    ORDER BY ?dsLabel ?filterTitle
    """
    results = list(g.query(query))

    if not results:
        print("No filterable variables found.")
        return

    current_ds = None
    for row in results:
        if str(row.dsLabel) != current_ds:
            current_ds = str(row.dsLabel)
            print(f"\n{'='*60}")
            print(f"  {current_ds}")
            print(f"{'='*60}")
            print(f"  {'Filter':<35} {'Type':<8} Variable")
            print(f"  {'-'*35} {'-'*8} {'-'*30}")
        print(f"  {str(row.filterTitle):<35} {str(row.filterType):<8} {row.varLabel}")


def cmd_values(g: Graph, filter_title: str):
    """Show permissible values and frequencies for a filter."""
    # First find the variable linked to this filter
    query = f"""
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?varLabel ?dsLabel ?code ?description ?count WHERE {{
        ?var a nccr:Variable ;
             rdfs:label ?varLabel ;
             nccr:belongsToSource/rdfs:label ?dsLabel ;
             nccr:boundToFilter ?filter ;
             nccr:hasValueSet/nccr:hasCodeValue ?cv .
        ?filter nccr:filterControlTitle ?filterTitle .
        ?cv skos:notation ?code .
        OPTIONAL {{ ?cv skos:prefLabel ?description . }}
        OPTIONAL {{ ?cv nccr:recordCount ?count . }}
        FILTER(LCASE(?filterTitle) = LCASE("{filter_title}"))
    }}
    ORDER BY DESC(?count)
    """
    results = list(g.query(query))

    if not results:
        # Try matching by variable label instead
        query2 = f"""
        PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?varLabel ?dsLabel ?code ?description ?count WHERE {{
            ?var a nccr:Variable ;
                 rdfs:label ?varLabel ;
                 nccr:belongsToSource/rdfs:label ?dsLabel ;
                 nccr:hasValueSet/nccr:hasCodeValue ?cv .
            ?cv skos:notation ?code .
            OPTIONAL {{ ?cv skos:prefLabel ?description . }}
            OPTIONAL {{ ?cv nccr:recordCount ?count . }}
            FILTER(LCASE(?varLabel) = LCASE("{filter_title}"))
        }}
        ORDER BY DESC(?count)
        """
        results = list(g.query(query2))

    if not results:
        print(f"No values found for '{filter_title}'.")
        print("Try: python cohort_builder.py discover")
        return

    var_label = str(results[0].varLabel)
    ds_label = str(results[0].dsLabel)
    print(f"\n  Variable: {var_label}")
    print(f"  Source:   {ds_label}")
    print(f"\n  {'Code':<12} {'Description':<50} {'Records':>12}")
    print(f"  {'-'*12} {'-'*50} {'-'*12}")

    total = 0
    for row in results:
        code = str(row.code)
        desc = str(row.description) if row.description else ""
        count = int(row['count']) if row['count'] else None
        count_str = f"{count:>12,}" if count else "           -"
        if count:
            total += count
        print(f"  {code:<12} {desc:<50} {count_str}")

    if total > 0:
        print(f"  {'':12} {'':50} {'-'*12}")
        print(f"  {'':12} {'TOTAL':<50} {total:>12,}")


def cmd_datasources(g: Graph):
    """Show available datasources and their record counts."""
    query = """
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?id ?label ?count ?filterCount WHERE {
        ?ds a nccr:DataSource ;
            nccr:sourceId ?id ;
            rdfs:label ?label .
        OPTIONAL { ?ds nccr:totalRecordCount ?count . }
        OPTIONAL {
            SELECT ?ds (COUNT(?f) as ?filterCount) WHERE {
                ?var nccr:belongsToSource ?ds ;
                     nccr:boundToFilter ?f .
            } GROUP BY ?ds
        }
    }
    ORDER BY DESC(?count)
    """
    results = list(g.query(query))

    print(f"\n  {'ID':<8} {'Name':<45} {'Records':>12} {'Filters':>8}")
    print(f"  {'-'*8} {'-'*45} {'-'*12} {'-'*8}")
    for row in results:
        count = f"{int(row['count']):>12,}" if row['count'] else "           -"
        filters = str(int(row.filterCount)) if row.filterCount else "0"
        print(f"  {str(row.id):<8} {str(row.label):<45} {count} {filters:>8}")


def cmd_top(g: Graph, field_name: str, limit: int = 50, datasource: str | None = None):
    """Show top values by frequency for any variable (including high-cardinality fields)."""
    ds_filter = ""
    if datasource:
        ds_filter = f'FILTER(UCASE(?dsId) = "{datasource.upper()}")'

    # Try matching by variable label, source column, or filter title
    query = f"""
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?dsLabel ?varLabel ?code ?description ?count WHERE {{
        ?var a nccr:Variable ;
             rdfs:label ?varLabel ;
             nccr:sourceColumn ?col ;
             nccr:belongsToSource ?ds ;
             nccr:hasValueSet/nccr:hasCodeValue ?cv .
        ?ds rdfs:label ?dsLabel ;
            nccr:sourceId ?dsId .
        ?cv skos:notation ?code ;
            nccr:recordCount ?count .
        OPTIONAL {{ ?cv skos:prefLabel ?description . }}
        FILTER(
            LCASE(?varLabel) = LCASE("{field_name}") ||
            LCASE(?col) = LCASE("{field_name}") ||
            CONTAINS(LCASE(?varLabel), LCASE("{field_name}")) ||
            CONTAINS(LCASE(?col), LCASE("{field_name}"))
        )
        {ds_filter}
    }}
    ORDER BY DESC(?count)
    LIMIT {limit}
    """
    results = list(g.query(query))

    if results:
        _display_top_results(results, field_name, limit)
    else:
        # Fallback: try reading directly from Report JSON files
        _top_from_reports(field_name, limit, datasource)


def _display_top_results(results, field_name: str, limit: int):
    """Display top results from SPARQL query."""
    var_label = str(results[0].varLabel)
    ds_label = str(results[0].dsLabel)
    print(f"\n  Variable: {var_label}")
    print(f"  Source:   {ds_label}")
    print(f"  Showing top {min(limit, len(results))} values by record count\n")
    print(f"  {'#':<4} {'Value':<55} {'Records':>12}")
    print(f"  {'-'*4} {'-'*55} {'-'*12}")

    total = 0
    for i, row in enumerate(results, 1):
        code = str(row.code)
        desc = str(row.description) if row.description else ""
        count = int(row['count'])
        total += count
        # Show description if available, otherwise code
        display = desc if desc and desc != code else code
        display = display[:55] if len(display) > 55 else display
        print(f"  {i:<4} {display:<55} {count:>12,}")

    print(f"  {'':4} {'':55} {'-'*12}")
    print(f"  {'':4} {'TOTAL (shown)':<55} {total:>12,}")


def _top_from_reports(field_name: str, limit: int, datasource: str | None):
    """Fallback: read frequency data directly from Report JSON files."""
    import urllib.request

    # Try local source-data directory first
    report_dir = Path(__file__).parent.parent / "source-data"
    if not report_dir.exists():
        report_dir = Path("source-data")

    # Report filenames by datasource
    report_sources = {
        "CTC": "ctcReport.json", "ABM": "abmReport.json",
        "CCDI": "ccdiReport.json", "COG": "cogReport.json",
        "MCD": "mcdReport.json", "MCE": "mceReport.json",
        "MCP": "mcpReport.json", "PHARM": "pharmReport.json",
        "RO": "roReport.json",
    }
    REPORT_BASE_URL = "https://nccrdataplatform.ccdi.cancer.gov/data/json/"

    found = False
    sources_to_check = {datasource.upper(): report_sources[datasource.upper()]} if datasource else report_sources

    for ds_id, filename in sources_to_check.items():
        report = None
        local_path = report_dir / filename
        if local_path.exists():
            try:
                with open(local_path, "r", encoding="utf-8") as f:
                    report = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        if report is None:
            # Try fetching from live platform
            try:
                url = REPORT_BASE_URL + filename
                with urllib.request.urlopen(url, timeout=10) as resp:
                    report = json.load(resp)
            except Exception:
                continue

        if report is None:
            continue

        for field in report.get("fields", []):
            fn = field.get("fieldName", "")
            if (fn.lower() == field_name.lower() or
                field_name.lower() in fn.lower() or
                fn.lower() in field_name.lower()):

                found = True
                values = field["charts"][0]["values"] if field.get("charts") else []

                print(f"\n  Variable: {fn}")
                print(f"  Source:   {ds_id} ({report.get('totalCount', 'N/A'):,} total records)")
                print(f"  Showing top {min(limit, len(values))} values by record count\n")
                print(f"  {'#':<4} {'Value':<55} {'Records':>12}")
                print(f"  {'-'*4} {'-'*55} {'-'*12}")

                total = 0
                for i, v in enumerate(values[:limit], 1):
                    code = str(v[0])
                    label_info = v[1] if len(v) > 1 and isinstance(v[1], dict) else {}
                    label = str(label_info.get("label", code)) if label_info else code
                    count = v[2] if len(v) > 2 else 0
                    total += count
                    display = label[:55] if len(label) > 55 else label
                    print(f"  {i:<4} {display:<55} {count:>12,}")

                print(f"  {'':4} {'':55} {'-'*12}")
                print(f"  {'':4} {'TOTAL (shown)':<55} {total:>12,}")
                return

    if not found:
        print(f"No frequency data found for '{field_name}'.")
        print("Try: python cohort_builder.py top --list")


def cmd_top_list(g: Graph):
    """List all variables that have frequency data available."""
    query = """
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?dsLabel ?varLabel ?sourceCol (COUNT(?cv) as ?valueCount) WHERE {
        ?var a nccr:Variable ;
             rdfs:label ?varLabel ;
             nccr:sourceColumn ?sourceCol ;
             nccr:belongsToSource/rdfs:label ?dsLabel ;
             nccr:hasValueSet/nccr:hasCodeValue ?cv .
        ?cv nccr:recordCount ?count .
    }
    GROUP BY ?dsLabel ?varLabel ?sourceCol
    ORDER BY ?dsLabel ?varLabel
    """
    results = list(g.query(query))

    if not results:
        print("No variables with frequency data found.")
        return

    current_ds = None
    print(f"\n  Variables with frequency data (use with 'top' command):\n")
    for row in results:
        if str(row.dsLabel) != current_ds:
            current_ds = str(row.dsLabel)
            print(f"\n  {current_ds}")
            print(f"  {'-'*60}")
        print(f"    {str(row.varLabel):<45} ({int(row.valueCount)} values)")


# ============================================================
# Cohort builder
# ============================================================

def cmd_build(g: Graph, output: str | None = None):
    """Interactive cohort builder."""
    print("=" * 60)
    print("  NCCR Cohort Builder")
    print("=" * 60)
    print()

    # Step 1: Name
    name = input("  Cohort name: ").strip()
    if not name:
        name = f"cohort-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Step 2: Datasources
    print("\n  Available datasources: CTC, ABM, CCDI, COG, MCD, MCE, MCP, PHARM, RO")
    print("  (CTC is always included)")
    ds_input = input("  Select datasources (comma-separated): ").strip().upper()
    datasources = ["CTC"]
    if ds_input:
        for ds in ds_input.split(","):
            ds = ds.strip()
            if ds and ds != "CTC":
                datasources.append(ds)

    print(f"\n  Selected: {', '.join(datasources)}")

    # Step 3: Filters
    print("\n  Add filter criteria (enter empty line when done):")
    print("  Format: FilterTitle = value1, value2, ...")
    print("  For ranges: MinAge = 7 or MaxAge = 17")
    print()

    criteria = []
    while True:
        line = input("  Filter> ").strip()
        if not line:
            break
        if "=" not in line:
            print("    (use format: FilterTitle = value1, value2)")
            continue
        parts = line.split("=", 1)
        filter_title = parts[0].strip()
        values_str = parts[1].strip()

        # Parse values
        if values_str.upper() == "ALL":
            values = ["ALL_VALUES"]
        else:
            values = [v.strip() for v in values_str.split(",")]
            # Try to convert numeric values
            parsed = []
            for v in values:
                try:
                    parsed.append(int(v))
                except ValueError:
                    try:
                        parsed.append(float(v))
                    except ValueError:
                        parsed.append(v)
            values = parsed

        criteria.append({"title": filter_title, "values": values})
        print(f"    Added: {filter_title} = {values}")

    # Step 4: Generate RDF
    print(f"\n  Generating cohort definition...")
    turtle = build_cohort_turtle(name, datasources, criteria)

    # Step 5: Output
    if output:
        out_path = Path(output)
    else:
        out_path = Path(f"{name.replace(' ', '_')}_cohort.ttl")

    out_path.write_text(turtle, encoding="utf-8")
    print(f"\n  Saved: {out_path}")
    print(f"  Datasources: {', '.join(datasources)}")
    print(f"  Criteria: {len(criteria)}")
    print(f"\n  This file can be imported into the NCCR Data Platform")
    print(f"  or shared with collaborators for reproducible cohort definitions.")


def build_cohort_turtle(name: str, datasources: list, criteria: list) -> str:
    """Generate a cohort definition as Turtle."""
    g = Graph()
    g.bind("nccr", NCCR)
    g.bind("nccr-ds", NCCR_DS)
    g.bind("nccr-flt", NCCR_FLT)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)

    cohort_id = str(uuid.uuid4())
    cohort_uri = URIRef(f"urn:nccr:cohort:{cohort_id}")

    # Metadata
    g.add((cohort_uri, RDF.type, NCCR.CohortDefinition))
    g.add((cohort_uri, NCCR.cohortName, Literal(name)))
    g.add((cohort_uri, NCCR.cohortCreated,
           Literal(datetime.now().isoformat(), datatype=XSD.dateTime)))

    # Datasources
    for ds in datasources:
        g.add((cohort_uri, NCCR.includesSource, NCCR_DS[ds.lower()]))

    # Filter criteria
    for criterion in criteria:
        bnode = BNode()
        g.add((cohort_uri, NCCR.hasFilterCriterion, bnode))
        g.add((bnode, RDF.type, NCCR.FilterCriterion))

        # Try to match the filter title to a known filter URI
        filter_uri = NCCR_FLT[criterion["title"].replace(" ", "")]
        g.add((bnode, NCCR.appliesFilter, filter_uri))

        values = criterion["values"]
        if values == ["ALL_VALUES"]:
            g.add((bnode, NCCR.allValuesSelected, Literal(True, datatype=XSD.boolean)))
        else:
            for v in values:
                if isinstance(v, (int, float)):
                    g.add((bnode, NCCR.filterNumericValue, Literal(v, datatype=XSD.decimal)))
                else:
                    g.add((bnode, NCCR.filterStringValue, Literal(str(v))))

    return g.serialize(format="turtle")


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="NCCR Cohort Discovery & Builder",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cohort_builder.py datasources             Show available datasources
  python cohort_builder.py discover                Show all filterable variables
  python cohort_builder.py discover --source CTC   Show only CTC filters
  python cohort_builder.py values Sex              Show values for Sex filter
  python cohort_builder.py values "ICCC Major (Level 1)"  Show ICCC classifications
  python cohort_builder.py top --list              List variables with frequency data
  python cohort_builder.py top "CanMED Non-proprietary Name"  Top drugs by count
  python cohort_builder.py top "CanMED Major Drug Class"      Top drug classes
  python cohort_builder.py top Sex                            Value frequencies for Sex
  python cohort_builder.py top "Primary Site" -n 20           Top 20 primary sites
  python cohort_builder.py build                   Interactive cohort builder
  python cohort_builder.py build -o my_cohort.ttl  Save to specific file
        """
    )
    subparsers = parser.add_subparsers(dest="command")

    # datasources
    subparsers.add_parser("datasources", help="Show available datasources and record counts")

    # discover
    discover_parser = subparsers.add_parser("discover", help="Show filterable variables")
    discover_parser.add_argument("--source", "-s", help="Filter by datasource ID (e.g., CTC, PHARM)")

    # values
    values_parser = subparsers.add_parser("values", help="Show permissible values for a filter")
    values_parser.add_argument("filter", help="Filter title or variable name")

    # top
    top_parser = subparsers.add_parser("top", help="Show top values by frequency for any variable")
    top_parser.add_argument("field", nargs="?", help="Variable name, source column, or filter title")
    top_parser.add_argument("--source", "-s", help="Filter by datasource ID")
    top_parser.add_argument("--limit", "-n", type=int, default=50, help="Number of results (default: 50)")
    top_parser.add_argument("--list", action="store_true", help="List all variables with frequency data")

    # build
    build_parser = subparsers.add_parser("build", help="Interactive cohort builder")
    build_parser.add_argument("--output", "-o", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    g = load_graph()

    if args.command == "datasources":
        cmd_datasources(g)
    elif args.command == "discover":
        cmd_discover(g, args.source)
    elif args.command == "values":
        cmd_values(g, args.filter)
    elif args.command == "top":
        if args.list or not args.field:
            cmd_top_list(g)
        else:
            cmd_top(g, args.field, args.limit, args.source)
    elif args.command == "build":
        cmd_build(g, args.output)


if __name__ == "__main__":
    main()
