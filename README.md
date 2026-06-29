# NCCR Metadata

RDF vocabulary and DATMM metadata for the [National Childhood Cancer Registry (NCCR) Data Platform](https://nccrdataplatform.ccdi.cancer.gov/home).

## Overview

This repository provides semantic metadata representations for the NCCR Data Platform's datasources and data dictionaries. It enables machine-readable, FAIR-compliant discovery and integration of NCCR data.

## Files

| File | Purpose |
|------|---------|
| `nccr_vocab.ttl` | **Vocabulary** — OWL classes and properties for variables, value sets, filters, processing rules, and display configuration |
| `nccr_datmm.ttl` | **Dataset catalog** — DATMM 6.0.0 metadata describing the platform and its 9 datasources (CTC, ABM, CCDI, COG, MCD, MCE, MCP, PHARM, RO) |
| `nccr_instances.ttl` | **Instance data** — Complete RDF representation of all 533 variables across all 9 NCCR datasources, including value sets, display configs, filters, and processing rules (28,620 triples) |

## Data Sources Described

| ID | Name | Description |
|----|------|-------------|
| CTC | Consolidated Tumor Case | Population-based cancer registry data (SEER), 1995–2022 |
| ABM | Area-Based Measures | Census-derived socioeconomic and geographic context |
| CCDI | CCDI Mappings | Cross-dataset patient matching via the Participant Index |
| COG | Children's Oncology Group | Clinical trial and registry enrollment, 2007–2018 |
| MCD | Medical Claims Diagnosis | ICD-9/ICD-10 diagnosis codes from insurance claims |
| MCE | Medical Claims Enrollment | Patient insurance enrollment status over time |
| MCP | Medical Claims Procedure | ICD/HCPCS/CPT procedure codes from insurance claims |
| PHARM | Pharmacy Claims | Outpatient medication dispensing data |
| RO | Radiation Oncology | Radiation treatment data from cancer centers and PPCR |

## Architecture

```
nccr_vocab.ttl        ← Defines classes & properties (the schema)
       │
nccr_datmm.ttl       ← Dataset-level catalog (who, what, where)
       │
nccr_instances.ttl    ← All variables, value sets, filters, and rules as RDF (the content)
```

The vocabulary supports three layers of metadata:
- **Scientific metadata** — variable definitions, value sets, external vocabulary links (NAACCR, SEER, ICD-O-3, RxNorm, CanMED)
- **Platform behavior** — UI visibility, graph generation, QuickSight inclusion, cohort filter bindings
- **ETL processing** — derived columns, binning rules, data substitutions, validation patterns

## Standards Used

- [DATMM 6.0.0](http://id.nlm.nih.gov/datmm/) — NLM DATaset Metadata Model for dataset discovery
- [SKOS](https://www.w3.org/TR/skos-reference/) — Permissible values as concept schemes
- [Dublin Core Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) — Standard descriptive properties
- [OWL 2](https://www.w3.org/TR/owl2-overview/) — Vocabulary definition
- [BIBFRAME](http://id.loc.gov/ontologies/bibframe/) — Agent contributions

## Usage

Load into any RDF-aware tool:

```python
from rdflib import Graph

g = Graph()
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_vocab.ttl")
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_datmm.ttl")
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_instances.ttl")

# Query: which variables are visible in the Data Browser?
results = g.query("""
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    SELECT ?var ?label WHERE {
        ?var a nccr:Variable ;
             rdfs:label ?label ;
             nccr:hasDisplayConfig/nccr:visibleInUI true .
    } LIMIT 10
""")
for row in results:
    print(row.label)
```

## Citation

> Childhood Cancer Data Initiative (CCDI) National Childhood Cancer Registry (NCCR) Data Platform: An interactive data platform for NCCR cancer statistics [Internet]. National Cancer Institute. doi: [10.71925/byd9-3d93](https://doi.org/10.71925/byd9-3d93).

## License

This metadata is provided under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/).
