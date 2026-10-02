#!/usr/bin/env python3
"""Generate the NCCR data-cut ERD assets from the metadata.

Emits two files, both derived from nccr_instances.ttl:

    erd.dbml   paste into dbdiagram.io to update the rendered diagram
    erd.html   the page that embeds the diagram, published to the
                      metadata repo root

Both are generated so the data-source list cannot drift from the registry. The
ERD previously showed 7 of the 9 sources because the diagram was maintained by
hand with no source in the repo, and the page was duplicated in two places.

Usage (from the repo root):
    python tools/generate_erd.py
    python tools/generate_erd.py --all-columns
    python tools/generate_erd.py --max-columns 40

Edit tools/templates/erd.html.template for page changes, never erd.html.
"""
import argparse
import datetime
import re
from rdflib import Graph

TTL = "nccr_instances.ttl"
TEMPLATE = "tools/templates/erd.html.template"
OUT_DBML = "erd.dbml"
OUT_HTML = "erd.html"

V = "https://nccrdataplatform.ccdi.cancer.gov/vocab#"

# The single place the diagram URL is defined. Both the page and the link in it
# read from here, so updating the embed is a one-line change.
EMBED_URL = "https://dbdiagram.io/e/6aa1befbf476a8187a5492e7/6aa1bf01f476a8187a54935b"

# Patient-level join key used in delivered data cuts. It is NOT a variable in
# the registry, so it cannot be read from the metadata; it is declared here so
# the ERD keeps its join semantics. Everything else below is metadata-driven.
PATIENT_KEY = "dataRequestPatientId"

# Tumor-level key, verified present in CTC and ABM in the metadata.
TUMOR_KEY = "tumorRecordNumber"

DBML_TYPES = {
    "lookup_value": "varchar",
    "string": "varchar",
    "numeric": "integer",
    "float": "decimal",
}

TAG_RE = re.compile(r"<[^>]+>")


def clean(text):
    """Flatten an itemDescription into one line of plain text.

    Descriptions in the metadata contain HTML markup and hard line breaks, both
    of which are invalid inside a single-quoted DBML note.
    """
    text = TAG_RE.sub(" ", text)
    text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    text = text.replace("&nbsp;", " ").replace("&quot;", '"')
    return re.sub(r"\s+", " ", text).strip()


def esc_dbml(text):
    """Escape a value for a single-quoted DBML note."""
    return text.replace("\\", "\\\\").replace("'", "\\'")


def esc_html(text):
    """Escape a value for HTML text content."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("'", "&rsquo;")
    )


def fetch_sources(g):
    """Return the data sources with their authoritative labels and counts."""
    q = f"""
    SELECT ?id ?label ?rec ?pat ?basis WHERE {{
      ?s a <{V}DataSource> ;
         <{V}sourceId> ?id ;
         <{V}sourceLabel> ?label ;
         <{V}totalRecordCount> ?rec ;
         <{V}sourcePatientCount> ?pat ;
         <{V}patientCountBasis> ?basis .
    }} ORDER BY DESC(?rec)
    """
    return [
        {
            "id": str(r.id),
            "label": str(r.label),
            "records": int(r.rec),
            "patients": int(r.pat),
            "basis": str(r.basis),
        }
        for r in g.query(q)
    ]


def fetch_columns(g, source_id):
    """Return (column, dbml_type, description) for one source, metadata order."""
    q = f"""
    SELECT ?col ?stype ?desc WHERE {{
      ?s a <{V}DataSource> ; <{V}sourceId> "{source_id}" ; <{V}hasVariable> ?v .
      ?v <{V}sourceColumn> ?col .
      OPTIONAL {{ ?v <{V}semanticType> ?stype }}
      OPTIONAL {{ ?v <{V}itemDescription> ?desc }}
    }} ORDER BY ?col
    """
    out = []
    for r in g.query(q):
        stype = str(r.stype) if r.stype else "string"
        desc = clean(str(r.desc)) if r.desc else ""
        out.append((str(r.col), DBML_TYPES.get(stype, "varchar"), desc))
    return out


def render_dbml(sources, columns_by_source, max_columns):
    lines = [
        "// NCCR Data Cut ERD",
        "// GENERATED FILE - DO NOT EDIT.",
        "// Produced by tools/generate_erd.py from nccr_instances.ttl.",
        "// Table names, labels and counts come from the metadata. Regenerate",
        "// instead of hand-editing, so the diagram cannot drift from the registry.",
        "",
    ]

    for src in sources:
        sid = src["id"]
        cols = columns_by_source[sid]
        total = len(cols)

        # Join keys must survive truncation or the Ref lines below dangle.
        keys = [c for c in cols if c[0] in (PATIENT_KEY, TUMOR_KEY)]
        rest = [c for c in cols if c[0] not in (PATIENT_KEY, TUMOR_KEY)]

        if max_columns is None or total <= max_columns:
            shown = keys + rest
        else:
            shown = keys + rest[: max(0, max_columns - len(keys))]
        truncated = total - len(shown)

        note = (
            f"{src['label']}\n"
            f"{src['records']:,} records | {src['patients']:,} patients "
            f"({src['basis']})\n"
            f"{total} variables in the registry"
        )
        if truncated:
            note += f", {len(shown)} shown here"

        lines.append(f"Table {sid} {{")
        lines.append(f"  {PATIENT_KEY} varchar [note: 'Patient-level join key (delivered cut)']")

        for col, dtype, desc in shown:
            if col == PATIENT_KEY:
                continue
            attrs = []
            if col == TUMOR_KEY:
                attrs.append("note: 'Tumor-level join key'")
            elif desc:
                short = desc if len(desc) <= 90 else desc[:87].rstrip() + "..."
                attrs.append(f"note: '{esc_dbml(short)}'")
            suffix = f" [{', '.join(attrs)}]" if attrs else ""
            lines.append(f"  {col} {dtype}{suffix}")

        if truncated:
            lines.append(f"  // + {truncated} more columns, see the data dictionary")

        lines.append(f"  Note: '''{note}'''")
        lines.append("}")
        lines.append("")

    lines.append("// Relationships")
    lines.append(f"// CTC is the master table. Every source joins to it on {PATIENT_KEY};")
    lines.append(f"// ABM additionally shares {TUMOR_KEY} with CTC.")
    for src in sources:
        if src["id"] == "CTC":
            continue
        lines.append(f"Ref: {src['id']}.{PATIENT_KEY} > CTC.{PATIENT_KEY}")
    lines.append(f"Ref: ABM.{TUMOR_KEY} - CTC.{TUMOR_KEY}")
    lines.append("")

    return "\n".join(lines)


def render_html(sources, columns_by_source, template):
    """Fill the page template from the metadata."""
    strip = []
    for i, src in enumerate(sources):
        sep = "" if i == len(sources) - 1 else " &middot;"
        # Drop the redundant parenthetical acronym; the ID is already shown.
        label = re.sub(rf"\s*\({src['id']}\)", "", src["label"])
        strip.append(
            f"    <b>{src['id']}</b> {esc_html(label)} {src['records']:,}{sep}"
        )

    # Name the two widest tables from the metadata rather than hardcoding them.
    widest = sorted(
        sources, key=lambda s: len(columns_by_source[s["id"]]), reverse=True
    )[:2]

    values = {
        "GENERATED": datetime.date.today().isoformat(),
        "EMBED_URL": EMBED_URL,
        "PATIENT_KEY": PATIENT_KEY,
        "TUMOR_KEY": TUMOR_KEY,
        "SOURCE_COUNT": str(len(sources)),
        "SOURCE_STRIP": "\n".join(strip),
        "WIDEST_SOURCE": widest[0]["id"],
        "WIDEST_COLS": str(len(columns_by_source[widest[0]["id"]])),
        "SECOND_SOURCE": widest[1]["id"],
        "SECOND_COLS": str(len(columns_by_source[widest[1]["id"]])),
    }

    page = template
    for key, val in values.items():
        page = page.replace("{{" + key + "}}", val)

    leftover = re.findall(r"\{\{(\w+)\}\}", page)
    if leftover:
        raise SystemExit(f"Template placeholder(s) not filled: {sorted(set(leftover))}")

    return page


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ttl", default=TTL)
    ap.add_argument("--template", default=TEMPLATE)
    ap.add_argument("--dbml", default=OUT_DBML)
    ap.add_argument("--html", default=OUT_HTML)
    ap.add_argument(
        "--max-columns",
        type=int,
        default=25,
        help="cap columns per table for readability (default: 25)",
    )
    ap.add_argument(
        "--all-columns",
        action="store_true",
        help="emit every column, including MCE's monthly enrollment fields",
    )
    args = ap.parse_args()

    g = Graph()
    g.parse(args.ttl, format="turtle")

    sources = fetch_sources(g)
    columns_by_source = {s["id"]: fetch_columns(g, s["id"]) for s in sources}

    cap = None if args.all_columns else args.max_columns

    with open(args.dbml, "w") as fh:
        fh.write(render_dbml(sources, columns_by_source, cap))

    with open(args.template) as fh:
        template = fh.read()
    with open(args.html, "w") as fh:
        fh.write(render_html(sources, columns_by_source, template))

    total_vars = sum(len(c) for c in columns_by_source.values())
    print(f"Wrote {args.dbml} and {args.html}")
    print(f"  {len(sources)} data sources, {total_vars} variables")
    for s in sources:
        n = len(columns_by_source[s["id"]])
        print(f"  {s['id']:6} {s['label'][:46]:46} {n:4} vars  {s['records']:>12,} records")


if __name__ == "__main__":
    main()
