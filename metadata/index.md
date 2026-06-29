---
layout: page
title: Metadata
nav_order: 2
---

# NCCR Metadata Files

This repository publishes the NCCR Data Platform's metadata as linked data (RDF/Turtle), enabling FAIR-compliant discovery and integration.

## Files

| File | Format | Purpose | Triples |
|------|--------|---------|---------|
| [`nccr_vocab.ttl`]({{ site.baseurl }}/nccr_vocab.ttl) | OWL / Turtle | **Vocabulary** — classes and properties for variables, value sets, filters, processing rules, and display configuration | ~120 |
| [`nccr_datmm.ttl`]({{ site.baseurl }}/nccr_datmm.ttl) | DATMM / Turtle | **Dataset catalog** — DATMM 6.0.0 metadata describing the platform and all 9 datasources, agents, contributions, and funding | ~180 |
| [`nccr_instances.ttl`]({{ site.baseurl }}/nccr_instances.ttl) | RDF / Turtle | **Instance data** — all 533 variables, 2,303 coded values, 51 cohort filters, and processing rules | 28,620 |

## Architecture

```
nccr_vocab.ttl        ← Schema layer (defines the rules)
       │
nccr_datmm.ttl       ← Catalog layer (who, what, where)
       │
nccr_instances.ttl    ← Content layer (all variables and values)
```

## Three layers of metadata

**Scientific metadata**
: Variable definitions, value sets, links to external vocabularies (NAACCR, SEER, ICD-O-3, RxNorm, CanMED, AJCC)

**Platform behavior**
: UI visibility, Data Browser graph generation, QuickSight dashboard inclusion, cohort filter bindings

**ETL processing**
: Derived columns (month-range, binned), data substitutions, validation patterns, deduplication rules

## Standards used

- [DATMM 6.0.0](http://id.nlm.nih.gov/datmm/) — NLM DATaset Metadata Model
- [SKOS](https://www.w3.org/TR/skos-reference/) — Permissible values as concept schemes
- [Dublin Core Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) — Descriptive properties
- [OWL 2](https://www.w3.org/TR/owl2-overview/) — Vocabulary definition
- [BIBFRAME](http://id.loc.gov/ontologies/bibframe/) — Agent contributions
