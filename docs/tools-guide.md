# NCCR Metadata Tools — User Guide

This guide explains how to install and use the Python tools included in the `nccr-metadata` repository. Currently the repository includes one tool: the **Cohort Discovery & Builder**.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/NCI-DCCPS/nccr-metadata.git
cd nccr-metadata
```

### 2. Set up Python

You need Python 3.9+ and the `rdflib` package.

**Option A — using uv (recommended):**

```bash
uv venv --python 3.12
source .venv/bin/activate
uv pip install rdflib
```

**Option B — using pip directly:**

```bash
pip install rdflib
```

### 3. Verify it works

```bash
python tools/cohort_builder.py --help
```

You should see the command listing and examples.

---

## Cohort Builder Tool

### Overview

The cohort builder queries NCCR metadata to let you:
- Explore available datasources and their sizes
- Discover which variables can be used as cohort filters
- View permissible values and how many records each value has
- See the most common values for any variable (top N by frequency)
- Build a cohort definition and export it as an RDF/Turtle file

No platform account is needed. The tool works entirely with public metadata.

### How data is loaded

When you run any command, the tool loads the NCCR instances graph (42,000+ RDF triples). It looks for data in this order:

1. `nccr_instances.ttl` in the repository root (fastest — local file)
2. Downloads from GitHub if local file isn't found

The first run may take 5-10 seconds to parse the graph. Subsequent queries against the same session are instant.

---

## Commands Reference

### `datasources` — List available datasources

Shows all 9 NCCR datasources with their record counts and number of filterable variables.

```bash
python tools/cohort_builder.py datasources
```

**Output:**

```
  ID       Name                                          Records     Filters
  -------- --------------------------------------------- ----------- --------
  MCP      Medical Claims Procedure                       62,669,037        0
  MCD      Medical Claims Diagnosis                       54,148,739        0
  PHARM    Pharmacy Claims                                12,611,171        7
  ABM      Area-Based Measures                             1,474,368        0
  CTC      Consolidated Tumor Case (CTC)                   1,474,368       23
  COG      Children's Oncology Group (COG)                 1,359,308        7
  MCE      Medical Claims Enrollment                       1,359,308        0
  CCDI     Childhood Cancer Data Initiative (CCDI)            20,838        2
  RO       Radiation Oncology                                  4,335       11
```

**Notes:**
- "Records" is the total number of records (rows) in that datasource
- "Filters" is how many variables can be used as cohort filter criteria
- Datasources with 0 filters (ABM, MCD, MCE, MCP) can still be included in a cohort but don't have their own filter controls — they're linked to patients via the CTC datasource

---

### `discover` — Show filterable variables

Lists all variables that can be used as filters in the cohort builder.

```bash
# All filterable variables across all datasources
python tools/cohort_builder.py discover

# Only filters for a specific datasource
python tools/cohort_builder.py discover --source CTC
python tools/cohort_builder.py discover --source PHARM
python tools/cohort_builder.py discover -s RO
```

**Output columns:**
- **Filter** — the control title shown in the platform UI
- **Type** — the filter operation: `EQUALS` (select values), `MIN` (minimum), or `MAX` (maximum)
- **Variable** — the underlying data variable being filtered

**Filter types explained:**
- `EQUALS` — select one or more values from a list (e.g., Sex = Male, Female)
- `MIN` — set a minimum threshold (e.g., Min Age = 7)
- `MAX` — set a maximum threshold (e.g., Max Age = 17)

---

### `values` — Show permissible values for a filter

Displays all allowed values for a filter variable, including record counts when available.

```bash
python tools/cohort_builder.py values "Sex"
python tools/cohort_builder.py values "Race/Ethnicity"
python tools/cohort_builder.py values "ICCC Major (Level 1)"
python tools/cohort_builder.py values "Vital Status"
python tools/cohort_builder.py values "CanMED Drug Category"
python tools/cohort_builder.py values "Yost - U.S.-based Socioeconomic Status (SES) Quintile"
```

**Output:**

```
  Variable: Sex
  Source:   Consolidated Tumor Case (CTC)

  Code         Description                                        Records
  ------------ -------------------------------------------------- --------
  2            Female                                              900,104
  1            Male                                                574,264
                                                              ------------
               TOTAL                                            1,474,368
```

**Tips:**
- Use the exact filter title from `discover` output
- The command also matches by variable label, so both `"Sex"` and `"Vital Status"` work
- If no results, check spelling against the `discover` output

---

### `top` — Show top values by frequency

Shows the most common values for any variable, sorted by record count. Works for high-cardinality fields (like drug names) that aren't available via `values`.

```bash
# Top 50 values (default)
python tools/cohort_builder.py top "canmedNonProprietaryName"

# Limit results
python tools/cohort_builder.py top "canmedNonProprietaryName" -n 10

# Filter by datasource
python tools/cohort_builder.py top "primarySite" --source CTC -n 20

# List all variables that have frequency data
python tools/cohort_builder.py top --list
```

**How it works:**

The `top` command first tries to find frequency data in the RDF graph (for variables that have coded permissible values). If that fails, it falls back to reading the Report JSON files — either locally from `source-data/` or by fetching them from the live NCCR Data Platform website.

**Useful queries:**

```bash
# Most common drugs prescribed
python tools/cohort_builder.py top "canmedNonProprietaryName" -n 20

# Drug classes
python tools/cohort_builder.py top "canmedMajorDrugClass" -n 15

# RxNorm drug names
python tools/cohort_builder.py top "rxnormDisplayName" -n 20

# Primary cancer sites
python tools/cohort_builder.py top "primarySite" -n 20

# Radiation anatomic sites
python tools/cohort_builder.py top "radiation_anatomic_site"

# Radiation therapy types
python tools/cohort_builder.py top "radiation_therapy_type"

# Age distribution
python tools/cohort_builder.py top "ageRecode19Groups"

# Diagnosis codes in medical claims
python tools/cohort_builder.py top "diagnosisCode" --source MCD
```

**Note:** The field name for `top` uses the source column name (camelCase, as stored in the data) rather than the UI display name. Use `top --list` to see all available field names.

---

### `build` — Interactive cohort builder

Guides you through building a cohort definition step by step, then exports it as a Turtle (.ttl) file.

```bash
# Interactive mode
python tools/cohort_builder.py build

# Specify output file
python tools/cohort_builder.py build -o my_cohort.ttl
python tools/cohort_builder.py build --output pediatric_leukemia.ttl
```

**Interactive workflow:**

```
  ============================================================
    NCCR Cohort Builder
  ============================================================

  Cohort name: Pediatric Leukemia Ages 7-17
  
  Available datasources: CTC, ABM, CCDI, COG, MCD, MCE, MCP, PHARM, RO
  (CTC is always included)
  Select datasources (comma-separated): COG, PHARM

  Selected: CTC, COG, PHARM

  Add filter criteria (enter empty line when done):
  Format: FilterTitle = value1, value2, ...
  For ranges: MinAge = 7 or MaxAge = 17

  Filter> Min Age (Yrs) = 7
    Added: Min Age (Yrs) = [7]
  Filter> Max Age (Yrs) = 17
    Added: Max Age (Yrs) = [17]
  Filter> ICCC Major (Level 1) = 01
    Added: ICCC Major (Level 1) = [1]
  Filter> Sex = ALL
    Added: Sex = ['ALL_VALUES']
  Filter>

  Generating cohort definition...

  Saved: Pediatric_Leukemia_Ages_7-17_cohort.ttl
  Datasources: CTC, COG, PHARM
  Criteria: 4

  This file can be imported into the NCCR Data Platform
  or shared with collaborators for reproducible cohort definitions.
```

**Filter syntax:**

| Input | Meaning |
|-------|---------|
| `Sex = 1, 2` | Select codes 1 and 2 |
| `Sex = ALL` | Select all values (no restriction) |
| `Min Age (Yrs) = 7` | Set minimum to 7 |
| `Max Age (Yrs) = 17` | Set maximum to 17 |
| `ICCC Major (Level 1) = 01, 02, 03` | Select multiple codes |
| `Year of Diagnosis = 2015, 2016, 2017` | Select specific years |

**Tips:**
- Use the filter title exactly as shown in `discover` output
- Numeric values are automatically detected
- `ALL` means no restriction on that filter
- Press Enter on an empty line to finish adding criteria

---

### Output format

The `build` command generates an RDF/Turtle file. Here's what a generated cohort looks like:

```turtle
@prefix nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#> .
@prefix nccr-ds: <https://nccrdataplatform.ccdi.cancer.gov/datasource/> .
@prefix nccr-flt: <https://nccrdataplatform.ccdi.cancer.gov/filter/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<urn:nccr:cohort:7dc3b8a2-0a5e-4652-8359-e85aa991c26c> a nccr:CohortDefinition ;
    nccr:cohortCreated "2026-08-19T15:17:58"^^xsd:dateTime ;
    nccr:cohortName "Pediatric Leukemia Ages 7-17" ;
    nccr:includesSource nccr-ds:ctc, nccr-ds:cog, nccr-ds:pharm ;
    nccr:hasFilterCriterion [
        a nccr:FilterCriterion ;
        nccr:appliesFilter nccr-flt:MinAge\(Yrs\) ;
        nccr:filterNumericValue 7.0
    ] , [
        a nccr:FilterCriterion ;
        nccr:appliesFilter nccr-flt:MaxAge\(Yrs\) ;
        nccr:filterNumericValue 17.0
    ] , [
        a nccr:FilterCriterion ;
        nccr:appliesFilter nccr-flt:ICCCMajor\(Level1\) ;
        nccr:filterNumericValue 1.0
    ] , [
        a nccr:FilterCriterion ;
        nccr:allValuesSelected true ;
        nccr:appliesFilter nccr-flt:Sex
    ] .
```

**What's captured:**
- Unique cohort ID
- Creation timestamp
- Cohort name
- Which datasources are included
- Each filter criterion with its selected values

**What you can do with it:**
- Share with collaborators who can rebuild the same cohort
- Attach to a publication as a reproducible cohort specification
- Import into the NCCR Data Platform (future feature)
- Version control your cohort definitions alongside analysis code

---

## Common Workflows

### Workflow 1: "I want to study X — what data exists?"

```bash
# 1. Check what datasources are relevant
python tools/cohort_builder.py datasources

# 2. Explore filters for the primary datasource
python tools/cohort_builder.py discover --source CTC

# 3. Check specific variable values
python tools/cohort_builder.py values "ICCC Major (Level 1)"

# 4. Look at distributions for detailed variables
python tools/cohort_builder.py top "primarySite" -n 30
```

### Workflow 2: "How common is [condition/drug/treatment]?"

```bash
# Drugs
python tools/cohort_builder.py top "canmedNonProprietaryName" -n 30

# Cancer sites
python tools/cohort_builder.py top "primarySite" -n 30

# Radiation treatments
python tools/cohort_builder.py top "radiation_therapy_type"

# Drug categories
python tools/cohort_builder.py values "CanMED Drug Category"
```

### Workflow 3: "Build and export a cohort definition"

```bash
# 1. Explore what's available
python tools/cohort_builder.py discover --source CTC
python tools/cohort_builder.py values "ICCC Major (Level 1)"

# 2. Build the cohort
python tools/cohort_builder.py build -o my_study_cohort.ttl

# 3. Share the .ttl file with your team or include in your DAR
```

---

## Troubleshooting

### "No values found for X"

The `values` command works with filter titles as shown in `discover` output. Try:
- Check exact spelling: `python tools/cohort_builder.py discover --source CTC`
- Use the `top` command instead for non-filterable variables: `python tools/cohort_builder.py top "fieldName"`
- Use `top --list` to see all variables with frequency data

### "Loading from GitHub (this may take a moment)..."

The tool is downloading the instances file remotely. This only happens if `nccr_instances.ttl` isn't in your local clone. To speed things up:

```bash
# Make sure you pulled the latest
git pull
```

### "No frequency data found"

Some variables are high-cardinality (thousands of values) and require the Report JSON fallback. The tool will try to fetch from the live platform. If your network blocks this:

```bash
# Download reports manually
curl -o source-data/pharmReport.json https://nccrdataplatform.ccdi.cancer.gov/data/json/pharmReport.json
curl -o source-data/ctcReport.json https://nccrdataplatform.ccdi.cancer.gov/data/json/ctcReport.json
```

### Field names for `top` vs display names for `values`

- `values` uses the **UI display name** (e.g., "CanMED Drug Category", "Race/Ethnicity")
- `top` uses the **source column name** for high-cardinality fields (e.g., "canmedNonProprietaryName", "primarySite")

Use `discover` to see UI names, `top --list` to see source column names.

---

## Data Freshness

The metadata reflects the most recent NCCR data release. Key facts about the current data:

- **CTC**: 1,474,368 tumors from 1,359,308 patients (diagnosis years 1995-2022)
- **PHARM**: 12,611,171 dispensing records
- **MCP**: 62,669,037 procedure records
- **MCD**: 54,148,739 diagnosis records
- **COG**: 1,359,308 records (diagnosis years 2007-2018)
- **RO**: 4,335 radiation treatment records

Record counts below 16 are suppressed for patient privacy.
