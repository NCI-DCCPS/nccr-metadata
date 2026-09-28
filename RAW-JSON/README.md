# RAW-JSON — Upstream Datasource Metadata (source input)

This folder holds the **raw, unmodified data-dictionary metadata** for the 9 primary
NCCR Data Platform datasources, exactly as produced by the platform's ETL configuration.

These files are the **input** to a DATMM crosswalk — they are *not* NCCR's DATMM
output. They are published here so external partners (e.g., the NLM team) can perform
their own independent crosswalk from the same source, rather than relying on NCCR's
interpretation.

## Contents

One `*_metadata.json` file per datasource:

| File | Datasource |
|------|------------|
| `ctc_metadata.json` | Consolidated Tumor Case (CTC) |
| `abm_metadata.json` | Area-Based Measures (ABM) |
| `ccdi_metadata.json` | CCDI Mappings (CCDI) |
| `cog_metadata.json` | Children's Oncology Group (COG) |
| `mcd_metadata.json` | Medical Claims Diagnosis (MCD) |
| `mce_metadata.json` | Medical Claims Enrollment (MCE) |
| `mcp_metadata.json` | Medical Claims Procedure (MCP) |
| `pharm_metadata.json` | Pharmacy Claims (PHARM) |
| `ro_metadata.json` | Radiation Oncology (RO) |

## File structure

Each file is a JSON object with a single top-level key, `Dictionary_Elements`, whose
value is an array of variable/data-item descriptions. Each element carries fields such as:

- `Column_Name_at_Source`, `Column_DataType_at_Source`
- `Item_Name`, `Item_Number`, `Item_Section`
- `Item_Description`, `Rationale`
- `Internet_Link` (references to external vocabularies: NAACCR, SEER, etc.)
- `Visible_in_UI`, `Visible_in_Quicksight`

Field sets vary slightly by datasource (e.g., only CTC carries `Visible_in_Quicksight`).

## Source & versioning

These files are a **point-in-time snapshot** copied from the NCCR Data Platform's
metadata configuration. They are a source *input*, so they can drift from the platform
as the data dictionaries evolve.

- **Snapshot taken:** 2026-09-04
- **Scope:** the 9 primary datasource `*_metadata.json` files only. Supporting
  configuration files (data-dictionary headers, parameter maps) and reference CSVs
  (primary site, histology preferred terms) are intentionally excluded.
- **Refresh:** re-copy this folder whenever the upstream data dictionaries change
  (e.g., at an annual data refresh) so the snapshot stays current.

> If a partner needs to reconcile a specific version, the maintainers can supply the
> exact upstream revision the snapshot was taken from on request.

## How this differs from NCCR's DATMM

- **`RAW-JSON/` (this folder)** — raw upstream *input*, unmodified source metadata.
- **`datmm/` and `datmm-jsonld/`** — NCCR's *interpretation*: the source metadata
  crosswalked into the DATMM model (Turtle, plus generated JSON-LD).

A partner performing their own crosswalk should start from `RAW-JSON/` and treat the
DATMM files as one possible mapping, not as authoritative source.

## License

Provided under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/), consistent
with the rest of this repository.
