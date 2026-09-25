---
name: nccr-data-request
description: >
  Helps a researcher write an NCCR Data Request. Use when someone is preparing,
  drafting, reviewing, or asking for help with an NCCR data request, data submission
  form, SEER Research Plus request, or the narrative sections (Research Aims,
  Research Relevance, Scientific Approach / Analytic Plan), Research Areas selection,
  collaborator listing, or data element selection.
---

# Writing an NCCR Data Request

Guide the researcher through the NCCR Data Request form. Your job is to draft,
tighten, and validate — **not** to submit. The researcher supplies institutional
documents, reviews everything, submits, and signs.

## Before anything else: four fields are published

**Project Name, Scientific Research Aims, Research Relevance, and Scientific
Approach & Analytic Plan are all PUBLICLY DISPLAYED.**

Say this out loud early. Then actively watch for content the researcher may not want
public:
- unpublished hypotheses or a competitive edge they'd rather not telegraph
- preliminary or unvalidated findings
- collaborator or funding details not yet announced
- anything identifying about patients (never appropriate anywhere)

Write these four fields as if a peer, a journalist, and a competitor will all read
them. That's usually achievable without weakening the request.

## The character limit is tighter than it looks

The three narrative fields are **1500 characters max**, which is roughly
**200–250 words**. That is one solid paragraph, not a page.

Practical approach: draft freely first, then compress. Cut background before cutting
specifics — reviewers already know the field. Count characters, not words, and report
the count when you hand back a draft.

---

## Field-by-field guidance

### 1. Project Name
Unique, descriptive, and easy to identify later. Public.

- Should convey population + topic at a glance.
- Avoid internal codenames, grant numbers, and acronyms only your lab uses.
- Useful test: *"If I saw this in a list of 200 requests in two years, would I know
  which study it was?"*

Weak: `AYA Study 2` · `Robotin R01 Aim 2`
Better: `Late Effects of Radiation in AYA CNS Tumor Survivors, 2005–2020`

### 2. Scientific Research Aims (1500 ch, public)
*"Briefly describe your proposed research, its aims, and its value to science or
public health."*

Structure that works:
1. One or two sentences of gap/context. **Short.**
2. The aim(s), stated specifically — numbered if more than one.
3. Why it matters for science or public health.

**Most common failure: too much background, not enough aim.** If more than a third of
the text is context, rebalance. Aims should be concrete enough that someone could
tell whether you achieved them.

### 3. Research Relevance (1500 ch, public)
*"Briefly describe how your research will advance a particular scientific field of
inquiry."*

**This is NOT a restatement of the Aims — people conflate them constantly.**
- Aims = what *you* will do.
- Relevance = what the *field* gains, and which field specifically.

Name the field. Name the specific gap or limitation in current knowledge. Say what
becomes possible or better once this work exists. If a sentence would fit equally
well in the Aims box, it probably belongs there instead.

### 4. Scientific Approach and Analytic Plan (1500 ch, public)
*"Briefly summarize your analytic plan, including key outcomes of interest."*

Should name, concretely:
- **Study design** (retrospective cohort, cross-sectional, case-control…)
- **Cohort definition** — population, age range, diagnosis, years
- **Key variables** — exposures and covariates
- **Key outcomes of interest** (explicitly requested by the form — don't omit)
- **Statistical approach** (models, stratification, handling of missingness,
  competing risks)

**Most common failure: vagueness.** "We will analyze the data to examine outcomes"
tells a reviewer nothing. Name the model and the outcome.

**Consistency check:** the cohort described here must match the Data Elements you
request and any attached cohort definition. Mismatches are a frequent source of
back-and-forth.

### 5. Research Areas (public)
Select from this controlled list — multiple may apply:

- Health disparities
- Methods development
- Research focused on particular cancer diagnosis
- Social/Behavioral
- Population health
- Late-effects of cancer
- Health services
- Treatment patterns
- Epidemiology

Select what genuinely applies. Over-selecting reads as unfocused; under-selecting can
misroute the request. Offer suggestions based on their Aims text, but let them decide.

### 6. Specify Collaborators
Anyone on the team who needs access to the requested dataset. **The rules differ by
institution and are easy to get wrong:**

- **Every collaborator needs their own SEER Research Plus account.**
- **Internal** (same institution, approved SEER Research Plus users) may access the
  downloaded data directly under this request.
- **External** (different institution) must each:
  1. have a SEER Research Plus account, **and**
  2. **submit their own data request referencing this request's ID**, citing the
     **exact project title, cohorts, and project details**.
- Controlled-access data may only go to individuals and organizations meeting the
  security requirements in **NIH Guide Notice NOT-OD-25-083**.

Flag the external-collaborator mechanics early. It surprises people and it adds
calendar time, because each external person runs a parallel request.

### 7. Data Elements Requested
Select the specific fields to include, per data source. Recommended fields are
selected by default and are required; other defaulted fields may be adjusted.

For CTC, the baseline defaults are Tumor Record Number, Sequence Number--Central, and
the four Virtual Pooled Registry fields: Index Cancer, Total number of primary tumors,
Chronological order for this tumor, and Number of Months from Index Cancer to Tumor.
Together these identify the tumor record and place it in the patient's sequence of
primaries. They come with every CTC request regardless of the science, so don't spend
justification on them.

Guidance:
- Request what you need **and can justify from the Analytic Plan.** Over-requesting
  invites scrutiny; under-requesting means an amendment later.
- Every element should map to something in the analytic plan — an exposure, outcome,
  covariate, or stratifier.
- If NCCR metadata tools are available (MCP server or the cohort builder CLI), use
  them to look up what variables exist per source, their permissible values, and how
  often each value actually occurs. Feasibility before commitment.

#### Do the reviewer's coverage check before they do
NCCR staff review submitted requests and flag variables the researcher did **not**
select but that the stated research aims imply they need. Under-requesting is the
failure mode this catches, and it costs the researcher an amendment cycle. Run the
same check yourself while the draft is still editable.

Work backwards from the Analytic Plan, not forwards from the element list:
1. Pull out every named exposure, outcome, covariate, stratifier, and time variable
   from the aims and analytic plan.
2. For each one, find the variable that carries it. Use `list_data_elements` per
   source, or the metadata site.
3. Then ask what the stated design *requires* but the aims never mention. Survival
   analysis needs follow-up time and vital status. Stratified estimates need the
   stratifying variable itself. Adjusted models need each stated covariate. Trend or
   latency claims need the relevant timing variable.
4. Name the gaps to the researcher and let them decide: "your plan says you'll adjust
   for stage, but stage isn't in your selection."

Say what you searched and what you couldn't find. If a variable the plan depends on
doesn't exist in any source, that's a finding worth raising early, because it may
change the analytic plan rather than the element list.

### 8. CCDI Mappings Approval Documentation
Upload a PDF of your approval from other resources to link data (for example, a dbGaP
profile approval).

This is a **prerequisite, not a formality** — if the researcher intends to link to
another resource, they need that approval in hand before submitting. Ask about it
early rather than at the end.

---

## How to run the session

1. **Ask what they're studying**, in their own words. Don't start with the form.
2. **Flag prerequisites immediately**: IRB status, SEER Research Plus accounts for
   everyone on the team, and any CCDI mappings approval PDF. These have lead times.
3. **Draft the narrative fields** from their description. Draft all four together —
   they need to be consistent with each other.
4. **Report character counts** for each of the three 1500-char fields.
5. **Suggest Research Areas** based on the Aims; let them confirm.
6. **Walk the collaborator rules**, distinguishing internal from external.
7. **Help with Data Elements** using the metadata tools if available, checking each
   element against the analytic plan, then running the coverage check in the other
   direction to catch variables the plan needs but the selection omits.
8. **Validate before handing off**: all required fields present, limits respected,
   cohort described consistently, approval documents ready, and no unexplained gap
   between the analytic plan and the selected elements.
9. **Hand off explicitly.** State what they must do: review, attach IRB and approval
   documents, submit, and sign/acknowledge.

## Boundaries — never do these
- **Never submit** the request or claim to have submitted it.
- **Never** draft or supply IRB approval, institutional attestations, or signatures.
- **Never** invent data availability, record counts, or variable names. Look them up
  in the NCCR metadata, or say you don't know.
- **Never** put patient-identifying content anywhere in the request.
- Don't assert that a field is a form default beyond what the metadata marks.
  `list_data_elements` flags the baseline defaults; treat anything unmarked as the
  researcher's choice.
- When you flag a variable the aims imply, present it as a gap for the researcher to
  judge, not as a platform requirement. You are anticipating reviewer feedback, not
  speaking for the reviewers.

## Useful reference points
- **NCCR metadata** (variables, permissible values, real frequencies):
  https://nci-dccps.github.io/nccr-metadata/
- **Repo** (vocabulary, instance data, cohort tooling, MCP server):
  https://github.com/NCI-DCCPS/nccr-metadata
- **NCCR Data Platform**: https://nccrdataplatform.ccdi.cancer.gov
- **NOT-OD-25-083** — controlled-access data security requirements.

> Form fields and limits are captured in `request-form.ttl` in this repository.
> If the live form changes, update both that file and this skill.
