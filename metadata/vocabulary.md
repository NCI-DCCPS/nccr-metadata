---
layout: page
title: Vocabulary
permalink: /metadata/vocabulary/
nav_exclude: true
---

# NCCR Vocabulary Reference

**Namespace:** `https://nccrdataplatform.ccdi.cancer.gov/vocab#`  
**Prefix:** `nccr:`  
**File:** [`nccr_vocab.ttl`]({{ site.baseurl }}/nccr_vocab.ttl)

---

## Classes

### Core domain

| Class | Description |
|-------|-------------|
| `nccr:DataSource` | A named collection of variables (e.g., CTC, PHARM, COG) |
| `nccr:DataSourceGroup` | A logical grouping of related data sources (e.g., Medical Claims) |
| `nccr:Variable` | A data element described in a metadata dictionary |
| `nccr:DerivedVariable` | A variable computed during ETL (binned columns, month ranges) |
| `nccr:ValueSet` | A controlled set of permissible values (extends `skos:ConceptScheme`) |
| `nccr:CodeValue` | A single allowed code (extends `skos:Concept`) |
| `nccr:Section` | A logical grouping of variables (e.g., Demographic, Treatment) |

### Processing & ETL

| Class | Description |
|-------|-------------|
| `nccr:ProcessingRule` | A transformation or deduplication rule applied during ETL |
| `nccr:DataSubstitution` | A value replacement applied during processing |
| `nccr:BinDefinition` | A numeric interval for binning a continuous variable |
| `nccr:ValidationRule` | A regex or pattern constraint for field validation |

### Platform behavior

| Class | Description |
|-------|-------------|
| `nccr:CohortFilter` | A filter control used in the Cohort Discovery page |
| `nccr:DisplayConfig` | UI and dashboard display settings for a variable |
| `nccr:SourceVocabulary` | An external coding system (NAACCR, SEER, ICD-O-3, etc.) |

### Cohort definitions

| Class | Description |
|-------|-------------|
| `nccr:CohortDefinition` | A saved set of filter criteria defining a patient cohort — portable, reproducible, citable |
| `nccr:FilterCriterion` | A single filter selection within a cohort definition |

---

## Key properties

### Variable identity

| Property | Domain | Description |
|----------|--------|-------------|
| `nccr:sourceColumn` | Variable | Column name in source data |
| `nccr:itemName` | Variable | Human-readable display name |
| `nccr:itemNumber` | Variable | NAACCR/registry item number |
| `nccr:itemDescription` | Variable | Detailed description |
| `nccr:semanticType` | Variable | One of: string, numeric, float, boolean, lookup_value, numeric_relation |
| `nccr:fieldLength` | Variable | Maximum field length |
| `nccr:externalLink` | Variable | URL to external documentation |

### Relationships

| Property | Domain → Range | Description |
|----------|----------------|-------------|
| `nccr:belongsToSource` | Variable → DataSource | Links variable to its parent source |
| `nccr:hasVariable` | DataSource → Variable | Links source to its variables |
| `nccr:hasValueSet` | Variable → ValueSet | Links variable to permissible values |
| `nccr:inSection` | Variable → Section | Groups variable in a section |
| `nccr:sourceVocabulary` | Variable → SourceVocabulary | Links to external standard |
| `nccr:boundToFilter` | Variable → CohortFilter | Links to cohort builder filter |
| `nccr:derivedFrom` | DerivedVariable → Variable | Source of a derived column |

### Display & platform

| Property | Domain | Description |
|----------|--------|-------------|
| `nccr:visibleInUI` | DisplayConfig | Show in Data Browser |
| `nccr:visibleInQuicksight` | DisplayConfig | Include in analytics dashboards |
| `nccr:generateGraph` | DisplayConfig | Generate distribution graph |
| `nccr:graphLimit` | DisplayConfig | Max values in graph |
| `nccr:filterType` | CohortFilter | EQUALS, MIN, or MAX |
| `nccr:filterControlTitle` | CohortFilter | UI label for the filter |

### Cohort definition

| Property | Domain | Description |
|----------|--------|-------------|
| `nccr:cohortName` | CohortDefinition | User-assigned name |
| `nccr:cohortCreator` | CohortDefinition | Who created it |
| `nccr:cohortCreated` | CohortDefinition | When it was created (xsd:dateTime) |
| `nccr:dataVersion` | CohortDefinition | NCCR data version for reproducibility |
| `nccr:patientCount` | CohortDefinition | Matching patients at save time |
| `nccr:tumorCount` | CohortDefinition | Matching tumors at save time |
| `nccr:includesSource` | CohortDefinition → DataSource | Which datasources are selected |
| `nccr:hasFilterCriterion` | CohortDefinition → FilterCriterion | Links to filter selections |
| `nccr:appliesFilter` | FilterCriterion → CohortFilter | Which filter is being used |
| `nccr:filterNumericValue` | FilterCriterion | Numeric value for MIN/MAX filters |
| `nccr:filterStringValue` | FilterCriterion | String value for EQUALS filters |
| `nccr:selectsValue` | FilterCriterion → CodeValue | Reference to a coded value |
| `nccr:allValuesSelected` | FilterCriterion | True if no restriction (ALL_VALUES) |

---

## Source vocabularies (named individuals)

| URI | Label |
|-----|-------|
| `nccr:vocab-NAACCR` | North American Association of Central Cancer Registries |
| `nccr:vocab-SEER` | Surveillance, Epidemiology, and End Results |
| `nccr:vocab-ICD-O-3` | International Classification of Diseases for Oncology, 3rd ed. |
| `nccr:vocab-ICD-9` | ICD-9 |
| `nccr:vocab-ICD-10` | ICD-10 |
| `nccr:vocab-AJCC` | American Joint Committee on Cancer |
| `nccr:vocab-RxNorm` | NLM normalized clinical drug names |
| `nccr:vocab-CanMED` | NCI Cancer Medications Enquiry Database |
| `nccr:vocab-HCPCS` | Healthcare Common Procedure Coding System |
| `nccr:vocab-CPT` | Current Procedural Terminology |
| `nccr:vocab-CoC` | Commission on Cancer |
| `nccr:vocab-NPCR` | National Program of Cancer Registries |
| `nccr:vocab-ATC` | Anatomical Therapeutic Chemical Classification |
