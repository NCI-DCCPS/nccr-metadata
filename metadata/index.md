---
layout: page
title: Metadata
permalink: /metadata/
---

# NCCR Metadata Files

[Data Sources](data-sources) · [Vocabulary Reference](vocabulary) · [Usage & Examples](usage)

---

This repository publishes the NCCR Data Platform's metadata as linked data (RDF/Turtle), enabling FAIR-compliant discovery and integration.

## DATMM Dataset Catalog

Per NLM requirements, the NCCR Data Platform is described as a **Repository** containing 9 standalone **Dataset** records. Each dataset is a self-contained DATMM record suitable for ingestion into the [NLM Dataset Catalog](https://datasetcatalog.nlm.nih.gov/).

| File | Description |
|------|-------------|
| [`datmm/repository.ttl`]({{ site.baseurl }}/datmm/repository.ttl) | NCCR Data Platform as a DATMM Repository |
| [`datmm/agents.ttl`]({{ site.baseurl }}/datmm/agents.ttl) | Shared agents (NCI, CCDI, SEER, COG, DCCPS) and contributions |
| [`datmm/concepts.ttl`]({{ site.baseurl }}/datmm/concepts.ttl) | Subject concepts with identifiers and scheme membership |
| [`datmm/ctc.ttl`]({{ site.baseurl }}/datmm/ctc.ttl) | Consolidated Tumor Case dataset |
| [`datmm/abm.ttl`]({{ site.baseurl }}/datmm/abm.ttl) | Area-Based Measures dataset |
| [`datmm/ccdi.ttl`]({{ site.baseurl }}/datmm/ccdi.ttl) | CCDI Mappings dataset |
| [`datmm/cog.ttl`]({{ site.baseurl }}/datmm/cog.ttl) | Children's Oncology Group dataset |
| [`datmm/mcd.ttl`]({{ site.baseurl }}/datmm/mcd.ttl) | Medical Claims Diagnosis dataset |
| [`datmm/mce.ttl`]({{ site.baseurl }}/datmm/mce.ttl) | Medical Claims Enrollment dataset |
| [`datmm/mcp.ttl`]({{ site.baseurl }}/datmm/mcp.ttl) | Medical Claims Procedure dataset |
| [`datmm/pharm.ttl`]({{ site.baseurl }}/datmm/pharm.ttl) | Pharmacy Claims dataset |
| [`datmm/ro.ttl`]({{ site.baseurl }}/datmm/ro.ttl) | Radiation Oncology dataset |

## NCCR Vocabulary & Instance Data

| File | Format | Description | Triples |
|------|--------|-------------|---------|
| [`nccr_vocab.ttl`]({{ site.baseurl }}/nccr_vocab.ttl) | OWL / Turtle | Vocabulary — classes and properties for variables, value sets, filters, processing rules, cohort definitions, and display configuration | ~150 |
| [`nccr_instances.ttl`]({{ site.baseurl }}/nccr_instances.ttl) | RDF / Turtle | Instance data — all 533 variables, 3,715 coded values with observed frequencies, 51 cohort filters, and processing rules | 42,067 |

## Architecture

```
datmm/                         ← DATMM catalog layer (NLM Dataset Catalog)
├── repository.ttl                 Repository (NCCR Data Platform)
├── agents.ttl                     Organizations & contributions
├── concepts.ttl                   Subject concepts
├── ctc.ttl                        Consolidated Tumor Case dataset
├── abm.ttl                        Area-Based Measures dataset
├── ccdi.ttl                       CCDI Mappings dataset
├── cog.ttl                        Children's Oncology Group dataset
├── mcd.ttl                        Medical Claims Diagnosis dataset
├── mce.ttl                        Medical Claims Enrollment dataset
├── mcp.ttl                        Medical Claims Procedure dataset
├── pharm.ttl                      Pharmacy Claims dataset
└── ro.ttl                         Radiation Oncology dataset

nccr_vocab.ttl                 ← Schema layer (defines classes & properties)

nccr_instances.ttl             ← Content layer (all variables, values, frequencies)
```

## Three layers of metadata

**Dataset discovery (DATMM)**
: Repository identity, dataset descriptions, contributors, funding, access rights, subject concepts — mapped to the NLM Dataset Catalog

**Scientific metadata (NCCR Vocabulary)**
: Variable definitions, value sets, links to external vocabularies (NAACCR, SEER, ICD-O-3, RxNorm, CanMED, AJCC)

**Platform behavior (NCCR Vocabulary)**
: UI visibility, graph generation, cohort filter bindings, ETL processing rules, observed value frequencies

## Standards used

- [DATMM 6.0.0](http://id.nlm.nih.gov/datmm/) — NLM DATaset Metadata Model
- [SKOS](https://www.w3.org/TR/skos-reference/) — Permissible values as concept schemes
- [Dublin Core Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) — Descriptive properties
- [OWL 2](https://www.w3.org/TR/owl2-overview/) — Vocabulary definition
- [BIBFRAME](http://id.loc.gov/ontologies/bibframe/) — Agent contributions
- [Schema.org](https://schema.org/) — Grants and funding
