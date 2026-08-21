# NCCR Data Discovery — Curriculum Use Cases

Exercises for students learning to explore and use NCCR Data Platform metadata. All exercises use the publicly available metadata and the [cohort builder tool](../tools/) — no platform account or data access required.

## Prerequisites

```bash
git clone https://github.com/NCI-DCCPS/nccr-metadata.git
cd nccr-metadata
pip install rdflib
```

---

## Beginner: Exploring What Data Exists

### Exercise 1: What cancer data is available for children under 5?

**Learning objectives:** Discover datasources, understand age filters, interpret record counts.

**Steps:**

```bash
# See all available datasources and their sizes
python tools/cohort_builder.py datasources

# What cancer types are represented?
python tools/cohort_builder.py values "ICCC Major (Level 1)"

# What does the age distribution look like?
python tools/cohort_builder.py top "ageRecode19Groups"
```

**Questions to answer:**
1. How many total tumor records exist in CTC?
2. What are the top 3 cancer types by record count?
3. How many records fall in the 00 years and 01-04 years age groups combined?
4. What percentage of all records are for children under 5?

---

### Exercise 2: What drugs are most commonly dispensed to childhood cancer patients?

**Learning objectives:** Explore pharmacy claims, understand drug classification hierarchies.

**Steps:**

```bash
# What drug categories exist?
python tools/cohort_builder.py values "CanMED Drug Category"

# What are the top 20 individual drugs?
python tools/cohort_builder.py top "canmedNonProprietaryName" -n 20

# What major drug classes are represented?
python tools/cohort_builder.py top "canmedMajorDrugClass" -n 15
```

**Questions to answer:**
1. What percentage of pharmacy records are classified as "CHEMOTHERAPY" vs "HORMONAL THERAPY"?
2. What is the most common individual drug? Is it a cancer treatment?
3. Why do so many records say "Not found in CanMED; see RxNorm fields"? What does this tell us about the data?
4. Name three drugs from the top 20 that you would consider cancer-specific vs general supportive care.

---

### Exercise 3: What is the race/ethnicity breakdown in NCCR?

**Learning objectives:** Understand demographic variables, think about representativeness and coding.

**Steps:**

```bash
python tools/cohort_builder.py values "Race/Ethnicity"
```

**Questions to answer:**
1. What are the five race/ethnicity categories used?
2. What percentage of records are "Non-Hispanic Unknown Race"? What might cause this?
3. NCCR covers 21 states representing 52.7% of U.S. children/AYA. How might this geographic selection affect the race/ethnicity distribution compared to the full U.S. population?
4. Why is "Hispanic" listed as a separate category that includes all races?

---

### Exercise 4: What socioeconomic context is available?

**Learning objectives:** Understand area-based measures, census linkage, and contextual variables.

**Steps:**

```bash
python tools/cohort_builder.py discover --source ABM
python tools/cohort_builder.py values "Yost - U.S.-based Socioeconomic Status (SES) Quintile"
```

**Questions to answer:**
1. How many variables does the ABM datasource have? What do they measure?
2. What does "No Data Available for Variable for Year of Diagnosis" mean in the SES quintile values? How many records have this value?
3. The SES quintiles are based on 2010 Census boundaries. What limitation does this create for cases diagnosed in 2020?
4. Why might a researcher want to combine SES data with tumor data?

---

## Intermediate: Designing a Research Cohort

### Exercise 5: Design a cohort for studying AYA leukemia survival

**Learning objectives:** Combine multiple filters, think about inclusion/exclusion criteria, consider which datasources add value.

**Steps:**

```bash
# What filters are available in CTC?
python tools/cohort_builder.py discover --source CTC

# Find the leukemia code
python tools/cohort_builder.py values "ICCC Major (Level 1)"

# What vital status options exist?
python tools/cohort_builder.py values "Vital Status"

# What does the COG datasource add?
python tools/cohort_builder.py discover --source COG

# Build the cohort
python tools/cohort_builder.py build -o aya_leukemia_survival.ttl
```

**Cohort criteria:**
- Datasources: CTC, COG
- Age: 15-39 (AYA definition)
- Cancer type: ICCC Major = 01 (Leukemias)
- All other filters: ALL

**Questions to answer:**
1. Why include COG alongside CTC? What research question does COG enrollment data help answer?
2. What years of diagnosis are covered? Does the COG coverage (2007-2018) limit your cohort differently than CTC (1995-2022)?
3. Open the generated `.ttl` file. What information does it capture? Could another researcher reproduce your cohort from this file alone?
4. What additional variables might you want to request in the actual data download that aren't reflected in the cohort filters?

---

### Exercise 6: Investigate treatment patterns for a specific cancer

**Learning objectives:** Use multiple datasources together, understand claims vs registry data.

**Steps:**

```bash
# What surgery options are recorded?
python tools/cohort_builder.py values "Surgery of Primary Site"

# What chemotherapy information is available?
python tools/cohort_builder.py values "Chemotherapy"

# What about pharmacy-level detail?
python tools/cohort_builder.py discover --source PHARM
python tools/cohort_builder.py top "canmedNonProprietaryName" -n 30

# What does claims procedure data show?
python tools/cohort_builder.py datasources
# Note MCP has 62M records — what does this mean?
```

**Questions to answer:**
1. CTC has a "Chemotherapy" variable with yes/no/unknown. PHARM has individual drug names. When would you use each?
2. MCP (Medical Claims Procedure) has 62M records for 1.4M patients. What does this ratio tell you about the granularity of claims data?
3. If you wanted to study "time from diagnosis to first chemotherapy drug," which datasources would you need? What variables from each?
4. What limitations exist in pharmacy claims data? (Hint: the Data Browser page mentions hospital-based chemotherapy.)

---

### Exercise 7: What radiation therapy data is available for pediatric brain tumors?

**Learning objectives:** Work with the Radiation Oncology datasource, understand treatment detail beyond registry data.

**Steps:**

```bash
# What RO filters are available?
python tools/cohort_builder.py discover --source RO

# What anatomic sites are treated?
python tools/cohort_builder.py top "radiation_anatomic_site"

# What therapy types exist?
python tools/cohort_builder.py top "radiation_therapy_type"

# What energy types?
python tools/cohort_builder.py top "radiation_energy_type"

# Build a brain tumor + radiation cohort
python tools/cohort_builder.py build -o brain_radiation.ttl
# → Datasources: CTC, RO
# → ICCC Major (Level 1) = 03 (CNS tumors)
# → Min Age = 0, Max Age = 14
```

**Questions to answer:**
1. How many total records does the RO datasource have? Why is it much smaller than CTC?
2. The RO data comes from "NCI-supported Cancer Centers and PPCR." What selection bias does this introduce compared to population-based registry data?
3. What radiation treatment details are available in RO that are NOT available in CTC's "Radiation Therapy" variable?
4. Design a study question that requires both CTC and RO data together.

---

## Advanced: Cross-Datasource Research Design

### Exercise 8: Socioeconomic disparities in treatment access

**Learning objectives:** Integrate multiple datasources, think about confounders, design a multi-faceted research question.

**Steps:**

```bash
# SES measures
python tools/cohort_builder.py values "Yost - U.S.-based Socioeconomic Status (SES) Quintile"

# Treatment timing
python tools/cohort_builder.py discover --source CTC
# Note: "Min Months" and "Max Months" filters for time-to-treatment

# Pharmacy timing
python tools/cohort_builder.py top "monthsFromIndexDxtoDispense" --source PHARM

# Claims enrollment (insurance coverage)
python tools/cohort_builder.py discover --source MCE
```

**Design a study:**

Write a 1-paragraph research aim that uses NCCR data to investigate whether socioeconomic status is associated with time to treatment initiation in pediatric cancer patients.

**Questions to answer:**
1. Which datasources do you need? (at minimum: CTC + ABM + PHARM or CTC + ABM)
2. What is your exposure variable? What is your outcome variable?
3. What confounders would you control for? Which ones are available in the metadata?
4. The SES data uses 2010 Census boundaries but patients were diagnosed 1995-2022. How does this affect your study design?
5. Insurance enrollment data (MCE) is available for years 2000-2023. How might you use this to strengthen your study?

---

### Exercise 9: CCDI data linkage — connecting research studies to registry data

**Learning objectives:** Understand the CCDI Participant Index, cross-study matching, and how linked data enables novel research.

**Steps:**

```bash
# What does CCDI offer?
python tools/cohort_builder.py discover --source CCDI
python tools/cohort_builder.py datasources
# Note: CCDI has 20,838 records

# What external resources are mapped?
python tools/cohort_builder.py values "Resources"
```

**Questions to answer:**
1. What is the CCDI Participant Index (CPI)? How does it differ from the CTC registry data?
2. The CCDI datasource has far fewer records than CTC (20K vs 1.4M). Why? What subset of patients does it represent?
3. If a researcher has genomic data from dbGaP study phs002790, how would CCDI mappings help them?
4. Why would a researcher want to combine registry data (CTC) with molecular characterization data (via CCDI)?

---

## Discussion Exercises (No Coding Required)

### Exercise 10: Data privacy and small cell suppression

The NCCR metadata shows aggregate counts but suppresses values with fewer than 16 records.

**Discussion:**
1. Why is the threshold 16 (rather than 5 or 10)?
2. Give an example of how showing exact small counts could identify a patient. (Hint: rare cancer + rare demographic + specific state.)
3. The platform requires IRB approval for individual-level data. What additional protections exist beyond suppression?
4. How does de-identification affect the types of research questions you can ask?

---

### Exercise 11: Representativeness and generalizability

**Discussion:**
1. CTC covers 21 states representing 52.7% of U.S. children/AYA ages 0-39. List three states you think are likely included and three that might be missing. What populations are underrepresented?
2. Pharmacy claims include "commercial plans, Medicaid, and commercial pharmacies." Who is missing from this data? (Hint: uninsured, VA, IHS.)
3. COG data covers diagnosis years 2007-2018. CTC covers 1995-2022. If you're studying trends over time, how does this mismatch affect your analysis?
4. A study finding from NCCR data says "30% of pediatric leukemia patients received Drug X within 6 months of diagnosis." Can you generalize this to all U.S. children with leukemia? Why or why not?

---

### Exercise 12: Comparing NCCR to other cancer data resources

**Discussion:**
1. How does NCCR differ from SEER*Stat in terms of what data is available and how you access it?
2. What does NCCR offer that a single-institution dataset does not?
3. What does a single-institution dataset offer that NCCR does not?
4. When would you use NCCR vs. the Childhood Cancer Survivor Study (CCSS) for long-term outcomes research?

---

## Capstone: Write a Data Request Justification

Using what you've learned, write a 1-page justification for a data access request to the NCCR Data Platform. Include:

1. **Research question** (1-2 sentences)
2. **Datasources needed** and why each is required
3. **Cohort definition** (which filters, what values)
4. **Variables of interest** beyond the filters (reference the data dictionary)
5. **Limitations** you anticipate based on the metadata (coverage, representativeness, suppression)
6. **Generated cohort file** (attach the .ttl file from the cohort builder)

Example topics:
- Racial disparities in time-to-treatment for AYA lymphoma
- COG trial participation rates by socioeconomic status
- Radiation dose patterns for pediatric CNS tumors
- Pharmacy utilization patterns in the first year post-diagnosis
