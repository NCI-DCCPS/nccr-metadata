# Poster: Machine-Readable Metadata and AI-Assisted Discovery for the National Childhood Cancer Registry Data Platform

## Poster Metadata

**Title:** Machine-Readable Metadata and AI-Assisted Discovery for the National Childhood Cancer Registry Data Platform

**Authors:** Radu Robotin, Johanna Goderre Jones, [additional co-authors]

**Affiliation:** Division of Cancer Control and Population Sciences (DCCPS), National Cancer Institute, National Institutes of Health

**Contact:** radu.robotin@nih.gov

---

## Suggested Layout (48" x 36" landscape)

```
┌────────────────────────────────────────────────────────────────────────┐
│                              TITLE BAR                                  │
│  Machine-Readable Metadata and AI-Assisted Discovery for the           │
│  National Childhood Cancer Registry Data Platform                       │
│  Authors • DCCPS/NCI/NIH                              [NCI] [CCDI]     │
├──────────────────┬──────────────────┬──────────────────────────────────┤
│                  │                  │                                    │
│   BACKGROUND     │  APPROACH        │   AI-ASSISTED DISCOVERY            │
│                  │                  │                                    │
│   • Problem      │  • Architecture  │   • LLM + Metadata = Agent        │
│   • NCCR Data    │  • DATMM         │   • Example conversation          │
│   • Gap          │  • NCCR Vocab    │   • How it works diagram          │
│                  │  • Instance Data  │                                    │
│                  │                  │                                    │
├──────────────────┼──────────────────┼──────────────────────────────────┤
│                  │                  │                                    │
│   RESULTS        │  TOOLS           │   IMPACT & FUTURE                  │
│                  │                  │                                    │
│   • 42K triples  │  • Cohort Builder│   • FAIR compliance               │
│   • 9 datasets   │  • CLI demo      │   • NLM Dataset Catalog           │
│   • Frequencies  │  • Export RDF    │   • Curriculum integration         │
│                  │                  │   • QR code to repo                │
│                  │                  │                                    │
└──────────────────┴──────────────────┴──────────────────────────────────┘
```

---

## Section 1: BACKGROUND

### The Problem

Researchers face barriers discovering and understanding what data is available in the NCCR Data Platform before committing to a data access request:

- 9 datasources with 533 variables across cancer registry, claims, pharmacy, and radiation oncology data
- Variable-level metadata is locked in platform-specific JSON files
- No machine-readable, standards-compliant catalog for external discovery
- Students and new researchers lack tools to explore data availability without platform access

### The NCCR Data Platform

- Secure, interactive platform for cohort discovery and data access
- 1,474,368 tumors from 1,359,308 unique patients (ages 0-39)
- Data from 21 states, diagnosis years 1995-2022
- Linked registry, pharmacy claims (12.6M records), medical claims (116M records), COG trials, radiation oncology, census-derived measures
- Controlled access requires IRB approval

### The Gap

How can we make NCCR data **findable** and **understandable** before a researcher even logs in?

---

## Section 2: APPROACH

### Architecture: Three Layers of Linked Metadata

```
┌─────────────────────────────────────────┐
│  DATMM 6.0.0 (Dataset Discovery)       │  ← NLM Dataset Catalog
│  • Repository: NCCR Data Platform       │
│  • 9 standalone Dataset records         │
│  • Contributor, MeSH subjects           │
├─────────────────────────────────────────┤
│  NCCR Vocabulary (Variable Schema)      │  ← OWL ontology
│  • DataSource, Variable, ValueSet       │
│  • CohortFilter, CohortDefinition      │
│  • DisplayConfig, ProcessingRule        │
├─────────────────────────────────────────┤
│  Instance Data (Content)                │  ← 42,067 RDF triples
│  • 533 variables with descriptions      │
│  • 3,715 coded values                   │
│  • Observed frequencies from live data  │
│  • 51 cohort filter definitions         │
└─────────────────────────────────────────┘
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| Platform = DATMM Repository | Users can search NLM catalog by repository |
| Each datasource = standalone Dataset | Individually discoverable and citable |
| Permissible values as SKOS concepts | Machine-queryable, FAIR-compliant |
| Observed frequencies included | Data discovery without accessing patient data |
| Cohort definitions as RDF | Portable, reproducible, shareable |
| Published on GitHub with Jekyll docs | Open, versioned, no infrastructure cost |

---

## Section 3: AI-ASSISTED DISCOVERY

### The Vision: LLM + Structured Metadata = Intelligent Data Discovery

An AI assistant (powered by an LLM) can read the published NCCR metadata and help researchers:

1. **Understand** what data is available without reading documentation
2. **Explore** variables, value sets, and distributions through natural language
3. **Build** cohort definitions by describing their research question
4. **Learn** about the platform's capabilities as part of a training curriculum

### How It Works

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│                  │     │                  │     │                  │
│  Researcher      │────▶│  LLM Agent       │────▶│  NCCR Metadata   │
│  (natural lang)  │     │  (reasoning)     │     │  (RDF/SPARQL)    │
│                  │◀────│                  │◀────│                  │
│  "What drugs     │     │  Translates to   │     │  42K triples     │
│   treat AYA      │     │  SPARQL, runs    │     │  533 variables   │
│   leukemia?"     │     │  query, explains │     │  3,715 values    │
│                  │     │  results         │     │  frequencies     │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

### Example Conversation

> **Student:** "I want to study treatment patterns for brain tumors in children under 15. What data does NCCR have?"
>
> **AI:** Based on the NCCR metadata, here's what's available:
>
> **Registry data (CTC):** 164,378 CNS tumor records. Includes diagnosis histology, summary treatment (surgery yes/no, chemo yes/no, radiation type), vital status, and survival.
>
> **Radiation Oncology (RO):** Detailed treatment courses with anatomic site, therapy type (proton therapy: 1,232 records; 3D conformal: 1,367), dose, fractions, and timing relative to diagnosis.
>
> **Pharmacy Claims (PHARM):** 12.6M dispensing records. Temozolomide (46,567 records) is the most common CNS chemotherapy. Dexamethasone (76,640) for brain edema management.
>
> Would you like me to build a cohort definition for CTC + RO + PHARM, ages 0-14, ICCC code 03?

### What Makes This Possible

The metadata is:
- **Structured** — RDF triples queryable via SPARQL
- **Self-describing** — every variable has descriptions, permissible values, and counts
- **Complete** — covers all 9 datasources and their relationships
- **Public** — no authentication needed to explore metadata
- **Versioned** — tied to specific data releases for reproducibility

Without structured metadata, an LLM would need to hallucinate or guess. With it, the LLM can provide **grounded, factual answers** backed by real data.

---

## Section 4: RESULTS

### Published Metadata

| Metric | Value |
|--------|-------|
| Total RDF triples | 42,067 |
| Variables described | 533 |
| Coded values (with frequencies) | 3,715 |
| Cohort filters defined | 51 |
| Derived variables (ETL-computed) | 18 |
| External vocabularies linked | 14 (NAACCR, SEER, ICD-O-3, RxNorm, CanMED, etc.) |
| DATMM Dataset records | 9 (standalone, catalog-ready) |

### Standards Compliance

- **DATMM 6.0.0** — NLM DATaset Metadata Model (ready for Dataset Catalog ingestion)
- **OWL 2** — Formal ontology for variable-level schema
- **SKOS** — Permissible values as concept schemes
- **Dublin Core** — Standard descriptive properties
- **BIBFRAME** — Agent contributions

### Frequency Data Examples

| Variable | Top Value | Count |
|----------|-----------|-------|
| Sex (CTC) | Female | 900,104 |
| ICCC Major | Epithelial neoplasms & melanomas | 655,380 |
| Drug (PHARM) | Tamoxifen Citrate | 290,923 |
| Radiation Type (RO) | 3D Conformal | 1,367 |
| SES Quintile (ABM) | Fifth (highest) | 247,325 |

---

## Section 5: TOOLS

### Cohort Discovery CLI

```bash
# Explore datasources
$ python cohort_builder.py datasources
  CTC   1,474,368 records   23 filters
  PHARM 12,611,171 records   7 filters
  RO        4,335 records  11 filters

# Top drugs by frequency  
$ python cohort_builder.py top "canmedNonProprietaryName" -n 5
  1  TAMOXIFEN CITRATE     290,923
  2  PREDNISONE            145,365
  3  ANASTROZOLE           130,623
  4  MERCAPTOPURINE         88,902
  5  METHOTREXATE           78,912

# Build exportable cohort definition
$ python cohort_builder.py build -o my_cohort.ttl
```

### Portable Cohort Definitions (RDF)

```turtle
<urn:nccr:cohort:abc123> a nccr:CohortDefinition ;
    nccr:cohortName "AYA Leukemia 15-39" ;
    nccr:includesSource nccr-ds:ctc, nccr-ds:pharm ;
    nccr:hasFilterCriterion [
        nccr:appliesFilter nccr-flt:MinAge ;
        nccr:filterNumericValue 15 ] .
```

- Shareable between researchers
- Attachable to publications
- Importable to the platform (planned)

---

## Section 6: IMPACT & FUTURE DIRECTIONS

### Current Impact

- **FAIR compliance** — NCCR metadata meets Findable, Accessible, Interoperable, Reusable criteria
- **NLM Dataset Catalog** — 9 datasets ready for ingestion (Nov 2026 CADR deadline)
- **Education** — Curriculum materials with 12 exercises for training researchers
- **Reproducibility** — Cohort definitions as portable, versioned artifacts

### Future Directions

1. **AI-powered discovery agent** — Deploy LLM with NCCR metadata as a RAG knowledge base for natural-language data exploration
2. **Platform integration** — Import/export cohort definitions as RDF directly from the Data Browser
3. **Automated metadata publishing** — CI/CD pipeline regenerates RDF after each ETL data release
4. **Cross-CADR interoperability** — Shared vocabulary enables queries across NCI data resources
5. **SPARQL endpoint** — Public query service for programmatic metadata access

### Try It Yourself

**Repository:** https://github.com/NCI-DCCPS/nccr-metadata

**Documentation:** https://nci-dccps.github.io/nccr-metadata/

**[QR CODE HERE]**

---

## Section 7: ACKNOWLEDGMENTS

This work is supported by the Childhood Cancer Data Initiative (CCDI) at the National Cancer Institute. The NCCR Data Platform is a collaboration between NCI's Division of Cancer Control and Population Sciences (DCCPS), the SEER Program, Children's Oncology Group, and participating state cancer registries.

---

## Supplementary: Poster Design Notes

### Visual elements to include

1. **Architecture diagram** — the three-layer stack (DATMM → Vocabulary → Instances)
2. **AI conversation mockup** — screenshot-style box showing the student/AI dialog
3. **CLI output screenshot** — terminal showing the cohort builder in action
4. **Data flow diagram** — JSON metadata → RDF converter → published GitHub → LLM agent → researcher
5. **QR code** — linking to https://nci-dccps.github.io/nccr-metadata/
6. **NCCR/NCI/CCDI logos**

### Color palette suggestion

- Primary: NCI blue (#1b3a5c)
- Accent: CCDI green (#2e7d32)
- Background: Light gray (#f8f9fa)
- Code blocks: Dark (#1a1a2e) with syntax highlighting

### Key talking points for the session

1. "The metadata itself is the discovery tool — no patient data needed"
2. "An AI can answer questions about NCCR because the metadata is structured, not because it has access to patient records"
3. "Researchers can explore what's available before investing time in an IRB application"
4. "The cohort definition format enables reproducible research — attach it to your paper"
5. "This approach scales to other CADRs — the vocabulary is reusable"
