---
layout: default
title: Data Cut ERD
---

# NCCR Data Cut — Interactive Entity Relationship Diagram

An interactive diagram of the source tables in a full NCCR data cut and how they
link. **Drag tables** to rearrange and **follow the relationship lines** to see
how each source joins to the master tumor table.

- **CTC** is the master (one row per tumor) and holds every patient.
- All sources link on **`dataRequestPatientId`** (patient level).
- **CTC + ABM** also share **`tumorRecordNumber`** (tumor-record level).

<div style="position:relative;width:100%;height:78vh;min-height:560px;border:1px solid rgba(46,196,182,.4);border-radius:14px;overflow:hidden;box-shadow:0 12px 40px rgba(0,0,0,.2);margin:20px 0;background:#0e1f33;">
  <iframe
    src="https://dbdiagram.io/e/6aa1befbf476a8187a5492e7/6aa1bf01f476a8187a54935b"
    title="NCCR Data Cut interactive ERD (dbdiagram.io)"
    style="width:100%;height:100%;border:0;display:block;"
    allowfullscreen>
  </iframe>
</div>

Interactive diagram hosted on
[dbdiagram.io](https://dbdiagram.io/e/6aa1befbf476a8187a5492e7/6aa1bf01f476a8187a54935b).

> **Note:** some columns are summarized for readability (e.g. MCE's ~360 monthly
> enrollment fields and CTC's full 109-column set). The complete field list per
> table is in the data dictionary shipped with each cut.

---

[← Back to home](./)
