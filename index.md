---
layout: default
title: Home
---

# NCCR Data Platform — Metadata & Documentation

The [National Childhood Cancer Registry (NCCR) Data Platform](https://nccrdataplatform.ccdi.cancer.gov/home) is a secure, interactive system for exploring, discovering, and requesting de-identified cancer data for children, adolescents, and young adults (ages 0–39).

This site provides **machine-readable metadata** for the platform's datasources and data dictionaries, published as linked data using standard semantic web vocabularies.

---

## What's here

| Section | Description |
|---------|-------------|
| [Metadata](metadata/) | DATMM catalog records, RDF vocabulary, and instance data |
| [Data Sources](metadata/data-sources) | Descriptions of the 9 NCCR datasources |
| [Vocabulary](metadata/vocabulary) | Classes and properties defined in the NCCR vocabulary |
| [Usage & Examples](metadata/usage) | Code snippets for Python, R, and SPARQL |
| [Cohort Builder Tool](tools/) | CLI tool for discovering variables, exploring value frequencies, and building cohort definitions |
| [Data Cut ERD](erd.html) | Interactive entity-relationship diagram of a full data cut (full-screen) |
| [Metadata Graph](graph.html) | Interactive graph of the ontology and example data, parsed live from the Turtle |
| [MCP Server](https://github.com/NCI-DCCPS/nccr-metadata/blob/main/mcp/README.md) | Query NCCR metadata from any AI assistant (Claude, Cursor, VS Code, Kiro) |
| [Data Request Skill](https://github.com/NCI-DCCPS/nccr-metadata/blob/main/skills/nccr-data-request/README.md) | Helps a researcher draft and validate an NCCR data request |

---

## AI-assisted discovery and data requests

Two pieces work together so you can explore NCCR and prepare a data request
conversationally:

**1. The MCP server** — register it once in your AI editor, then ask questions in
plain language. It answers from the published metadata, with real record counts and
no access to patient data.
[Setup instructions →](https://github.com/NCI-DCCPS/nccr-metadata/blob/main/mcp/README.md)

**2. The data request skill** — drop it into your assistant's skills folder
(`~/.kiro/skills/`, `~/.claude/skills/`, or your framework's equivalent) and it guides
you through the NCCR Data Request form: drafting the narrative sections within the
1500-character limits, choosing Research Areas, the SEER Research Plus collaborator
rules, and selecting data elements.
[Install instructions →](https://github.com/NCI-DCCPS/nccr-metadata/blob/main/skills/nccr-data-request/README.md)

The server supplies the facts; the skill supplies the judgment. The assistant drafts
and validates — you review, attach your IRB and approval documents, submit, and sign.

---

## Download files

| File | Description |
|------|-------------|
| [nccr_vocab.ttl](nccr_vocab.ttl) | Vocabulary — OWL ontology (schema) |
| [nccr_instances.ttl](nccr_instances.ttl) | Instance data — 42,067 triples with value frequencies |
| [datmm/](datmm/) | DATMM catalog — 9 standalone dataset records + repository |

- [GitHub repository](https://github.com/NCI-DCCPS/nccr-metadata)

---

## Citation

> Childhood Cancer Data Initiative (CCDI) National Childhood Cancer Registry (NCCR) Data Platform: An interactive data platform for NCCR cancer statistics [Internet]. National Cancer Institute. DOI: [10.71925/byd9-3d93](https://doi.org/10.71925/byd9-3d93).
