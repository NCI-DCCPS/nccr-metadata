#!/usr/bin/env python3
"""Check that the ERD page and DBML list the same data sources as the metadata.

Run from the repo root. Exits non-zero if the ERD assets have drifted from
nccr_instances.ttl, which is how the diagram ended up showing 7 of 9
sources in the first place.
"""
import re
import sys
from rdflib import Graph

V = "https://nccrdataplatform.ccdi.cancer.gov/vocab#"
TTL = "nccr_instances.ttl"
PAGE = "erd.html"
DBML = "erd.dbml"


def metadata_sources():
    g = Graph()
    g.parse(TTL, format="turtle")
    q = f"""
    SELECT ?id ?label ?rec WHERE {{
      ?s a <{V}DataSource> ;
         <{V}sourceId> ?id ;
         <{V}sourceLabel> ?label ;
         <{V}totalRecordCount> ?rec .
    }} ORDER BY DESC(?rec)
    """
    g2 = g.query(q)
    return [(str(r.id), str(r.label), int(r.rec)) for r in g2]


def main():
    sources = metadata_sources()
    page = open(PAGE).read()
    dbml = open(DBML).read()
    dbml_tables = set(re.findall(r"^Table (\w+)", dbml, re.M))

    print(f"Metadata defines {len(sources)} data sources\n")
    print(f"{'ID':7}{'records':>14}  {'page':6} {'dbml':6}  label")
    failures = []

    for sid, label, rec in sources:
        in_page = re.search(rf"<b>{sid}</b>[^<]*{re.escape(format(rec, ','))}", page) is not None
        in_dbml = sid in dbml_tables
        print(
            f"{sid:7}{rec:>14,}  "
            f"{'OK' if in_page else 'MISS':6} {'OK' if in_dbml else 'MISS':6}  {label}"
        )
        if not in_page:
            failures.append(f"{sid} missing (or wrong record count) on {PAGE}")
        if not in_dbml:
            failures.append(f"{sid} missing from {DBML}")

    extra = dbml_tables - {s[0] for s in sources}
    for sid in sorted(extra):
        failures.append(f"{DBML} has table {sid}, which is not a metadata data source")

    print()
    if failures:
        for f in failures:
            print(f"FAIL: {f}")
        return 1
    print(f"PASS: all {len(sources)} sources match the metadata in both the page and the DBML")
    return 0


if __name__ == "__main__":
    sys.exit(main())
