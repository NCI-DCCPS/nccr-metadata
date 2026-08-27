# Example: Investigating Treatment Patterns for Pediatric CNS Tumors

This walkthrough demonstrates how to use the NCCR metadata to investigate treatment patterns for pediatric central nervous system (CNS) tumors — the second most common childhood cancer group after leukemia.

## Research question

**What treatment modalities (surgery, radiation, chemotherapy) are used for children ages 0-14 diagnosed with CNS tumors, and what detailed radiation therapy and pharmacy data is available to study treatment patterns?**

---

## Step 1: Identify the cancer group

```bash
python tools/cohort_builder.py values "ICCC Major (Level 1)"
```

```
  Code  Description                                                       Records
  ----- ----------------------------------------------------------------- --------
  03    III. CNS and Miscellaneous Intracranial and Intraspinal Neoplasms  164,378
  ...
```

CNS tumors are ICCC Major code **03**, with 164,378 tumor records in NCCR.

---

## Step 2: Explore the subtypes

```bash
python tools/cohort_builder.py values "ICCC (Level 2)"
```

Relevant CNS subtypes:
```
  Code  Description                                                  Records
  ----- ------------------------------------------------------------ --------
  035   IIIe Other specified intracranial and intraspinal neoplasms    82,031
  032   IIIb Astrocytomas                                             40,236
  034   IIId Other gliomas                                            18,737
  033   IIIc Intracranial and intraspinal embryonal tumors              9,298
  031   IIIa Ependymomas and choroid plexus tumor                       8,673
  036   IIIf Unspecified intracranial and intraspinal neoplasms         5,403
```

---

## Step 3: Check what treatment data is available from the registry (CTC)

```bash
python tools/cohort_builder.py values "Chemotherapy"
```

```
  Code  Description       Records
  ----- ----------------- --------
  0     No/Unknown         949,268
  1     Yes                525,100
```

```bash
python tools/cohort_builder.py values "Radiation Therapy"
```

```
  Code  Description                                              Records
  ----- -------------------------------------------------------- --------
  0     None/Unknown                                             948,159
  1     Beam radiation                                           216,727
  3     Radioisotopes (1988+)                                     54,406
  4     Combination of beam with implants or isotopes              8,203
  2     Radioactive implants (includes brachytherapy) (1988+)      4,537
  ...
```

These are summary-level variables from the registry — yes/no for chemo, broad categories for radiation. For treatment pattern research, we need more detail.

---

## Step 4: Explore the Radiation Oncology (RO) datasource

```bash
python tools/cohort_builder.py discover --source RO
```

```
  Filter                              Type     Variable
  ----------------------------------- -------- --------------------------
  Radiation Anatomic Site             EQUALS   Radiation Anatomic Site
  Radiation Therapy Type              EQUALS   Radiation Therapy Type
  Radiation Energy Type               EQUALS   Radiation Energy Type
  Min Dose                            MIN      Radiation Dose Delivered
  Max Dose                            MAX      Radiation Dose Delivered
  Min Fractions                       MIN      Radiation Fractions Delivered
  Max Fractions                       MAX      Radiation Fractions Delivered
  Min Months                          MIN      Months from Index Cancer Dx to Start of Treatment
  Max Months                          MAX      Months from Index Cancer Dx to Start of Treatment
  Min Months                          MIN      Months from Index Cancer Dx to End of Treatment
  Max Months                          MAX      Months from Index Cancer Dx to End of Treatment
```

The RO datasource gives us:
- **Where**: anatomic site of radiation
- **How**: therapy type (proton, photon, etc.) and energy type
- **How much**: total dose and number of fractions
- **When**: months from diagnosis to treatment start and end

```bash
python tools/cohort_builder.py top "radiation_therapy_type"
```

```
  #  Value                              Records
  -- ---------------------------------- --------
  1  3D Conformal Radiation Therapy       1,367
  2  Proton Therapy                       1,232
  3  IMRT                                   824
  4  Stereotactic Radiosurgery              248
  5  Stereotactic Body Radiation Therapy    152
  ...
```

```bash
python tools/cohort_builder.py top "radiation_anatomic_site"
```

```
  #  Value                     Records
  -- ------------------------- --------
  1  Brain                       2,405
  2  Spine                         789
  3  Craniospinal                  543
  ...
```

---

## Step 5: Explore pharmacy claims for CNS tumor drugs

```bash
python tools/cohort_builder.py top "canmedNonProprietaryName" -n 15 --source PHARM
```

Key drugs relevant to CNS tumors from the top list:
```
  #  Value                                  Records
  -- -------------------------------------- --------
  5  TEMOZOLOMIDE  (75 ndc codes)            46,567   ← standard CNS chemo
  3  DEXAMETHASONE  (52 ndc codes)           76,640   ← steroid for brain edema
  4  PREDNISONE  (76 ndc codes)             145,365   ← steroid
  ...
```

The pharmacy data tells us:
- Which drugs are dispensed (by CanMED or RxNorm name)
- When relative to diagnosis (months from dx to dispense)
- Duration and quantity

---

## Step 6: Build the cohort definition

```bash
python tools/cohort_builder.py build -o pediatric_cns_treatment.ttl
```

```
  Cohort name: Pediatric CNS Tumors Treatment Patterns
  Select datasources: CTC, RO, PHARM
  Filter> ICCC Major (Level 1) = 03
  Filter> Min Age (Yrs) = 0
  Filter> Max Age (Yrs) = 14
  Filter>
  Saved: pediatric_cns_treatment.ttl
```

---

## Step 7: Review the exported cohort definition

The generated file captures the complete cohort specification:

```turtle
@prefix nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#> .
@prefix nccr-ds: <https://nccrdataplatform.ccdi.cancer.gov/datasource/> .
@prefix nccr-flt: <https://nccrdataplatform.ccdi.cancer.gov/filter/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<urn:nccr:cohort:...> a nccr:CohortDefinition ;
    nccr:cohortName "Pediatric CNS Tumors Treatment Patterns" ;
    nccr:cohortCreated "2026-08-19T..."^^xsd:dateTime ;
    nccr:includesSource nccr-ds:ctc, nccr-ds:ro, nccr-ds:pharm ;
    nccr:hasFilterCriterion [
        a nccr:FilterCriterion ;
        nccr:appliesFilter nccr-flt:ICCCMajor\(Level1\) ;
        nccr:filterNumericValue 3.0
    ] , [
        a nccr:FilterCriterion ;
        nccr:appliesFilter nccr-flt:MinAge\(Yrs\) ;
        nccr:filterNumericValue 0.0
    ] , [
        a nccr:FilterCriterion ;
        nccr:appliesFilter nccr-flt:MaxAge\(Yrs\) ;
        nccr:filterNumericValue 14.0
    ] .
```

---

## What this cohort would give a researcher

When submitted as a data access request, this cohort would provide:

| Datasource | What you'd receive |
|---|---|
| **CTC** | One record per tumor: demographics, diagnosis date, histology, stage, summary treatment (surgery/chemo/radiation yes-no), vital status, survival months |
| **RO** | One record per radiation treatment course: anatomic site, therapy type, energy type, dose, fractions, start/end timing relative to diagnosis |
| **PHARM** | One record per drug dispensing event: drug name/code, drug class, quantity, duration, timing relative to diagnosis |

This allows analysis of:
- What fraction of pediatric CNS patients receive radiation, chemotherapy, or both?
- What radiation modalities (proton vs photon vs IMRT) are used?
- What is the time from diagnosis to first treatment?
- What supportive care drugs (steroids, antiemetics) are commonly prescribed alongside treatment?
- Are there differences in treatment patterns by histologic subtype (astrocytoma vs embryonal tumor vs ependymoma)?

---

## Limitations to consider

1. **RO data is small** (4,335 records total across all cancer types) — it only covers NCI Cancer Centers and PPCR, not all treatment facilities
2. **Pharmacy claims** don't include hospital-administered IV chemotherapy — only outpatient dispensing
3. **No direct linkage to specific tumor** in pharmacy data — a patient with multiple tumors has all their pharmacy records combined
4. **Not all patients have claims data** — coverage depends on insurer participation
5. **CTC radiation variable** is summary-level (yes/no/type) while RO has detailed treatment data, but for a much smaller subset of patients

---

## Sample generated cohort file

See: [`pediatric_cns_treatment.ttl`](pediatric_cns_treatment.ttl)
