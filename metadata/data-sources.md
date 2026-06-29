---
layout: page
title: Data Sources
nav_order: 3
---

# NCCR Data Sources

The NCCR Data Platform integrates 9 data sources, linked through persistent patient identifiers. The Consolidated Tumor Case (CTC) dataset serves as the central linkage hub.

---

## Consolidated Tumor Case (CTC)

| Property | Value |
|----------|-------|
| **ID** | `CTC` |
| **Full name** | Consolidated Tumor Case |
| **Coverage** | 1995–2022 |
| **Population** | 52.7% of U.S. children/AYA ages 0-39 (2020 populations) |
| **Source** | SEER and other population-based cancer registries |

Final adjudicated data from 19 population-based cancer registries including California, Colorado, Connecticut, Georgia, Hawai'i, Idaho, Illinois, Iowa, Kentucky, Louisiana, New Jersey, New Mexico, New York, Seattle-Puget Sound, Tennessee, Texas, Utah, and Wisconsin.

Also includes NAACCR Virtual Pooled Registry linkage for identifying prior and subsequent malignant neoplasms.

---

## Area-Based Measures (ABM)

| Property | Value |
|----------|-------|
| **ID** | `ABM` |
| **Full name** | Area-Based Measures |
| **Coverage** | Patients with SEER diagnosis year 2006–2022 |
| **Source** | U.S. Census, American Community Survey |

Non-clinical variables derived from the US Census providing broader context of health-related factors. Variables use 2010 Census attributes and geographic boundaries. Includes Yost socioeconomic quintiles, Rural-Urban Commuting Area codes, and persistent poverty indicators.

---

## Childhood Cancer Data Initiative Mappings (CCDI)

| Property | Value |
|----------|-------|
| **ID** | `CCDI` |
| **Full name** | Childhood Cancer Data Initiative Mappings |
| **Source** | CCDI Participant Index (CPI) |

Leverages the CPI to match individuals across organizations, datasets, and studies. Maps publicly available participant identifiers to NCCR identifiers, enabling dataset merging across public health surveillance, research studies, and real-world healthcare resources.

Three types of external resources: datasets (e.g., genomic data), organizations (e.g., AACR Project GENIE), and studies (e.g., St. Jude).

---

## Children's Oncology Group (COG)

| Property | Value |
|----------|-------|
| **ID** | `COG` |
| **Full name** | Children's Oncology Group |
| **Coverage** | Diagnosis year 2007–2018 |
| **Source** | COG clinical trials and registry protocols |

Data for patients enrolled in COG studies including clinical trials and registry protocols such as Childhood Cancer Research Network and Project:EveryChild. Enables researchers to understand differences between trial participants and non-participants.

---

## Medical Claims — Diagnosis (MCD)

| Property | Value |
|----------|-------|
| **ID** | `MCD` |
| **Group** | Medical Claims |
| **Source** | Insurance claims (various insurers) |

ICD-9 or ICD-10 diagnosis codes associated with each claim, sequence numbers for diagnoses occurring on multiple claims within the same month, and months elapsed between index cancer diagnosis and claim service date.

---

## Medical Claims — Enrollment (MCE)

| Property | Value |
|----------|-------|
| **ID** | `MCE` |
| **Group** | Medical Claims |
| **Coverage** | Enrollment status for years 2000–2023; SEER diagnosis year 2000–2021 |
| **Source** | Insurance claims (various insurers) |

Patient insurance enrollment status at various points in time before and after their index cancer diagnosis.

---

## Medical Claims — Procedure (MCP)

| Property | Value |
|----------|-------|
| **ID** | `MCP` |
| **Group** | Medical Claims |
| **Source** | Insurance claims (various insurers) |

ICD-9, ICD-10, HCPCS, or CPT procedure codes, applicable modifiers, sequence numbers for procedures on multiple claims within the same month, and months from index cancer diagnosis to service date.

---

## Pharmacy Claims (PHARM)

| Property | Value |
|----------|-------|
| **ID** | `PHARM` |
| **Full name** | Pharmacy Claims |
| **Coverage** | Claims since 2000 |
| **Source** | Commercial plans, Medicaid, commercial pharmacies |

Outpatient pharmacy dispensing records including 9- and 11-digit NDC codes, CanMED/RxNorm drug classification, dispense quantity and duration, and months from diagnosis to dispense. Primarily oral antineoplastics and infusion-based chemotherapies. Hospital-based chemotherapy not currently included.

---

## Radiation Oncology (RO)

| Property | Value |
|----------|-------|
| **ID** | `RO` |
| **Full name** | Radiation Oncology |
| **Source** | NCI-supported Cancer Centers, Pediatric Proton/Photon Consortium Registry (PPCR) |

Expanded radiation treatment data including anatomic site, therapy type, energy type, total and prescribed doses and fractions, months from index diagnosis to start and end of treatment, and other clinical record elements.
