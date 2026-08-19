---
layout: default
title: Tools
permalink: /tools/
---

# Cohort Discovery & Builder Tool

A command-line tool that queries the published NCCR metadata to explore data sources, discover filterable variables, view value distributions, and build portable cohort definitions.

## Installation

```bash
git clone https://github.com/NCI-DCCPS/nccr-metadata.git
cd nccr-metadata
pip install rdflib
```

## Commands

### Show available datasources

```bash
python tools/cohort_builder.py datasources
```

```
  ID       Name                                          Records     Filters
  -------- --------------------------------------------- ----------- --------
  MCP      Medical Claims Procedure                       62,669,037        0
  MCD      Medical Claims Diagnosis                       54,148,739        0
  PHARM    Pharmacy Claims                                12,611,171        7
  CTC      Consolidated Tumor Case (CTC)                   1,474,368       23
  COG      Children's Oncology Group (COG)                 1,359,308        7
  ...
```

### Discover filterable variables

```bash
python tools/cohort_builder.py discover --source CTC
```

```
  Filter                              Type     Variable
  ----------------------------------- -------- --------------------------
  Sex                                 EQUALS   Sex
  Year of Diagnosis                   EQUALS   Year of Diagnosis
  Min Age (Yrs)                       MIN      Age recode with single ages
  Max Age (Yrs)                       MAX      Age recode with single ages
  ICCC Major (Level 1)                EQUALS   ICCC Major Category
  Race/Ethnicity                      EQUALS   Race and origin recode
  ...
```

### View permissible values with record counts

```bash
python tools/cohort_builder.py values "Race/Ethnicity"
```

```
  Variable: Race and origin recode (NHW, NHB, NHAIAN, NHAPI, Hispanic)
  Source:   Consolidated Tumor Case (CTC)

  Code         Description                                        Records
  ------------ -------------------------------------------------- --------
  1            Non-Hispanic White                                  881,593
  5            Hispanic (All Races)                                312,953
  2            Non-Hispanic Black                                  157,208
  4            Non-Hispanic Asian or Pacific Islander               92,021
  9            Non-Hispanic Unknown Race                            22,974
  3            Non-Hispanic American Indian/Alaska Native            7,619
```

### Top values by frequency (including drug names)

```bash
python tools/cohort_builder.py top "canmedNonProprietaryName" -n 10
```

```
  Variable: canmedNonProprietaryName
  Source:   PHARM (12,611,171 total records)

  #    Value                                                   Records
  ---- ------------------------------------------------------- --------
  1    TAMOXIFEN CITRATE                                        290,923
  2    PREDNISONE                                               145,365
  3    ANASTROZOLE                                              130,623
  4    MERCAPTOPURINE                                            88,902
  5    METHOTREXATE                                              78,912
  ...
```

### Build a cohort definition

```bash
python tools/cohort_builder.py build -o my_cohort.ttl
```

Interactive prompts guide you through:
1. Name your cohort
2. Select datasources (CTC is always included)
3. Add filter criteria (e.g., `Min Age (Yrs) = 7`, `ICCC Major (Level 1) = 01`)

The output is a portable RDF/Turtle file that can be shared with collaborators or imported into the NCCR Data Platform.

### Example: Pediatric Leukemia cohort (ages 7-17)

```bash
python tools/cohort_builder.py build -o pediatric_leukemia.ttl
```

```
  Cohort name: Pediatric Leukemia 7-17
  Select datasources: CTC, COG
  Filter> Min Age (Yrs) = 7
  Filter> Max Age (Yrs) = 17
  Filter> ICCC Major (Level 1) = 01
  Filter> Sex = ALL
  Filter>
  Saved: pediatric_leukemia.ttl
```

## How it works

The tool loads `nccr_instances.ttl` (locally or from GitHub) and uses SPARQL queries to explore the metadata. For high-cardinality fields like drug names, it falls back to fetching the Report JSONs directly from the live NCCR Data Platform.

No authentication or platform account is required — all data queried by this tool is publicly available metadata and aggregate statistics.
