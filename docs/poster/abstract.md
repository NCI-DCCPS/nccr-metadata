# Abstract

## Machine-Readable Metadata and AI-Assisted Discovery for the National Childhood Cancer Registry Data Platform

**Authors:** Radu Robotin, Johanna Goderre Jones

**Affiliation:** Division of Cancer Control and Population Sciences, National Cancer Institute, National Institutes of Health

---

### Background

The National Childhood Cancer Registry (NCCR) Data Platform provides researchers with access to linked, de-identified cancer data for children, adolescents, and young adults (ages 0-39) across 9 datasources encompassing tumor registry records (1.4M patients from 21 states, 1995-2022), pharmacy claims (12.6M records), medical claims (116M records), Children's Oncology Group trial enrollment, radiation oncology treatment courses, area-based socioeconomic measures, and cross-study patient linkage via the CCDI Participant Index. However, researchers face barriers discovering what data is available and understanding its scope before investing time in IRB-approved data access requests.

### Methods

We developed and published a machine-readable metadata layer for the NCCR Data Platform using established semantic web standards. The approach consists of three components: (1) dataset-level catalog records conforming to the NLM DATaset Metadata Model (DATMM 6.0.0), describing the platform as a Repository with 9 standalone Dataset entries ready for ingestion into the NLM Dataset Catalog; (2) a lightweight OWL ontology (NCCR Vocabulary) defining classes and properties for variables, value sets, cohort filters, processing rules, and portable cohort definitions; and (3) an instance data layer containing 42,067 RDF triples representing all 533 platform variables, 3,715 coded values with observed frequencies from the current data release, and 51 cohort filter definitions linked to 14 external biomedical vocabularies (NAACCR, SEER, ICD-O-3, RxNorm, CanMED, AJCC, and others). We additionally developed a command-line tool for metadata-driven cohort discovery and a portable RDF-based cohort definition format enabling reproducible and shareable cohort specifications. All artifacts are published as open source on GitHub with automated documentation.

### Results

The published metadata enables data discovery without accessing patient-level information. Researchers can programmatically query which variables exist per datasource, what values are permissible, and how many records each value contains — using standard SPARQL queries or a purpose-built CLI tool. The cohort definition format allows researchers to specify and share patient selection criteria as self-describing RDF files that reference the vocabulary, supporting reproducibility in collaborative research. Critically, the structured metadata also enables AI-assisted discovery: when provided as context to a large language model, the metadata allows the AI to give grounded, factual answers about NCCR data availability — including specific record counts, available filter criteria, and cross-datasource relationships — without hallucination and without access to patient records.

### Conclusions

Publishing NCCR metadata as linked data addresses multiple requirements simultaneously: FAIR data compliance, NLM CADR implementation requirements, researcher education, and a foundation for AI-powered data discovery. The approach is generalizable to other Cancer-Associated Data Repositories (CADRs) sharing similar data distribution models. The combination of structured metadata with AI assistants represents a novel pathway for making complex, multi-source research data platforms discoverable and understandable to a broader research community.

---

**Keywords:** childhood cancer, metadata, linked data, FAIR, DATMM, RDF, ontology, AI-assisted discovery, data platform, cohort definition, NCCR, CCDI

**Repository:** https://github.com/NCI-DCCPS/nccr-metadata

**Documentation:** https://nci-dccps.github.io/nccr-metadata/
