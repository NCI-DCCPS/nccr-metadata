---
layout: page
title: Usage & Examples
permalink: /metadata/usage/
nav_exclude: true
---

# Usage & Code Examples

## Loading the ontology

### Python (rdflib)

```python
from rdflib import Graph, Namespace

NCCR = Namespace("https://nccrdataplatform.ccdi.cancer.gov/vocab#")

g = Graph()
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_vocab.ttl")
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_instances.ttl")

# Load DATMM catalog records
for f in ["repository", "agents", "concepts", "ctc", "abm", "ccdi", "cog", "mcd", "mce", "mcp", "pharm", "ro"]:
    g.parse(f"https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/datmm/{f}.ttl")

print(f"Loaded {len(g)} triples")
```

### R (rdflib / redland)

```r
library(rdflib)

rdf <- rdf()
rdf_parse(rdf, "https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_instances.ttl",
          format = "turtle")
```

---

## Example SPARQL queries

### List all visible CTC variables

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX nccr-ds: <https://nccrdataplatform.ccdi.cancer.gov/datasource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?variable ?label ?section WHERE {
    ?variable a nccr:Variable ;
              rdfs:label ?label ;
              nccr:belongsToSource nccr-ds:ctc ;
              nccr:hasDisplayConfig/nccr:visibleInUI true .
    OPTIONAL { ?variable nccr:inSection/rdfs:label ?section . }
}
ORDER BY ?section ?label
```

### Find all cohort filters for a datasource

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX nccr-ds: <https://nccrdataplatform.ccdi.cancer.gov/datasource/>

SELECT ?filter ?title ?type ?field WHERE {
    ?filter a nccr:CohortFilter ;
            nccr:filterControlTitle ?title ;
            nccr:filterType ?type ;
            nccr:filterFieldName ?field ;
            nccr:filterDataSource nccr-ds:ctc .
}
ORDER BY ?title
```

### Get permissible values for a variable

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?code ?description WHERE {
    ?var nccr:sourceColumn "sex" ;
         nccr:hasValueSet ?vs .
    ?vs nccr:hasCodeValue ?cv .
    ?cv skos:notation ?code ;
        skos:prefLabel ?description .
}
ORDER BY ?code
```

### Find variables linked to a specific standard

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?variable ?label ?source WHERE {
    ?variable a nccr:Variable ;
              rdfs:label ?label ;
              nccr:sourceVocabulary ?vocab .
    ?vocab rdfs:label ?source .
    FILTER(?source = "NAACCR"@en)
}
LIMIT 20
```

### List all derived (binned) variables

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?derived ?label ?sourceVar ?binLabel ?min ?max WHERE {
    ?derived a nccr:DerivedVariable ;
             rdfs:label ?label ;
             nccr:derivedFrom ?sourceVar ;
             nccr:hasBinDefinition ?bin .
    ?bin nccr:binLabel ?binLabel ;
         nccr:binMin ?min ;
         nccr:binMax ?max .
}
ORDER BY ?derived ?min
```

### Query value distributions (frequencies)

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?label ?count WHERE {
    ?var nccr:sourceColumn "sex" ;
         nccr:belongsToSource <https://nccrdataplatform.ccdi.cancer.gov/datasource/ctc> ;
         nccr:hasValueSet ?vs .
    ?vs nccr:hasCodeValue ?cv .
    ?cv skos:prefLabel ?label ;
        nccr:recordCount ?count .
}
ORDER BY DESC(?count)
```

Example result:
```
Female: 900,104
Male:   574,264
```

### Find rare values (low frequency)

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?varLabel ?code ?description ?count WHERE {
    ?var a nccr:Variable ;
         rdfs:label ?varLabel ;
         nccr:hasValueSet/nccr:hasCodeValue ?cv .
    ?cv skos:notation ?code ;
        skos:prefLabel ?description ;
        nccr:recordCount ?count .
    FILTER(?count < 100)
}
ORDER BY ?count
LIMIT 20
```

### Get total record counts per datasource

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?source ?label ?count WHERE {
    ?source a nccr:DataSource ;
            rdfs:label ?label ;
            nccr:totalRecordCount ?count .
}
ORDER BY DESC(?count)
```

---

## Building a cohort: discovering filterable variables

The NCCR Data Platform allows researchers to build patient cohorts by selecting datasources and applying filters. The metadata captures which variables are filterable and what values are available.

### List all filterable variables by datasource

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?datasource ?variable ?filterTitle ?filterType WHERE {
    ?var a nccr:Variable ;
         rdfs:label ?variable ;
         nccr:belongsToSource/rdfs:label ?datasource ;
         nccr:boundToFilter ?filter .
    ?filter nccr:filterControlTitle ?filterTitle ;
            nccr:filterType ?filterType .
}
ORDER BY ?datasource ?filterTitle
```

Example results:
```
Consolidated Tumor Case (CTC)    Sex                      Sex              EQUALS
Consolidated Tumor Case (CTC)    Year of Diagnosis        Year of Diagnosis  EQUALS
Consolidated Tumor Case (CTC)    Age recode...            Min Age (Yrs)    MIN
Consolidated Tumor Case (CTC)    Age recode...            Max Age (Yrs)    MAX
Pharmacy Claims                  CanMED Drug Category     CanMED Drug Category  EQUALS
Radiation Oncology               Radiation Anatomic Site  Radiation Anatomic Site  EQUALS
```

### What values can I filter on for a specific variable?

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?value ?description ?count WHERE {
    ?var a nccr:Variable ;
         rdfs:label "ICD-O-3 Behavior Code" ;
         nccr:boundToFilter ?filter ;
         nccr:hasValueSet/nccr:hasCodeValue ?cv .
    ?cv skos:notation ?value ;
        skos:prefLabel ?description .
    OPTIONAL { ?cv nccr:recordCount ?count . }
}
ORDER BY ?value
```

### Which datasources have filterable variables?

```sparql
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?datasource (COUNT(?filter) as ?filterCount) WHERE {
    ?var nccr:belongsToSource ?ds ;
         nccr:boundToFilter ?filter .
    ?ds rdfs:label ?datasource .
}
GROUP BY ?datasource
ORDER BY DESC(?filterCount)
```

### Full Python example: explore CTC filters before building a cohort

```python
"""Discover what filters are available for CTC and their possible values."""
from rdflib import Graph, Namespace

g = Graph()
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_instances.ttl")

# Step 1: What can I filter on in CTC?
filters_query = """
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX nccr-ds: <https://nccrdataplatform.ccdi.cancer.gov/datasource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?varLabel ?filterTitle ?filterType WHERE {
    ?var a nccr:Variable ;
         rdfs:label ?varLabel ;
         nccr:belongsToSource nccr-ds:ctc ;
         nccr:boundToFilter ?filter .
    ?filter nccr:filterControlTitle ?filterTitle ;
            nccr:filterType ?filterType .
}
ORDER BY ?filterTitle
"""
print("=== Available CTC Filters ===")
for row in g.query(filters_query):
    print(f"  {row.filterTitle} ({row.filterType}) — variable: {row.varLabel}")

# Step 2: What are the possible values for Sex?
values_query = """
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?code ?label ?count WHERE {
    ?var nccr:sourceColumn "sex" ;
         nccr:belongsToSource <https://nccrdataplatform.ccdi.cancer.gov/datasource/ctc> ;
         nccr:hasValueSet/nccr:hasCodeValue ?cv .
    ?cv skos:notation ?code ;
        skos:prefLabel ?label .
    OPTIONAL { ?cv nccr:recordCount ?count . }
}
ORDER BY ?code
"""
print("\n=== Sex values ===")
for row in g.query(values_query):
    count_str = f" ({int(row['count']):,} records)" if row['count'] else ""
    print(f"  Code {row.code}: {row.label}{count_str}")
```

---

## Python: full example

```python
"""Query NCCR metadata to find all filterable pharmacy variables."""
from rdflib import Graph, Namespace

NCCR = Namespace("https://nccrdataplatform.ccdi.cancer.gov/vocab#")
NCCR_DS = Namespace("https://nccrdataplatform.ccdi.cancer.gov/datasource/")

g = Graph()
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_instances.ttl")

query = """
PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
PREFIX nccr-ds: <https://nccrdataplatform.ccdi.cancer.gov/datasource/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?varLabel ?filterTitle ?filterType WHERE {
    ?var a nccr:Variable ;
         rdfs:label ?varLabel ;
         nccr:belongsToSource nccr-ds:pharm ;
         nccr:boundToFilter ?filter .
    ?filter nccr:filterControlTitle ?filterTitle ;
            nccr:filterType ?filterType .
}
"""

results = g.query(query)
for row in results:
    print(f"{row.varLabel:40s} → {row.filterTitle} ({row.filterType})")
```

---

## Loading into Protégé

1. Open Protégé
2. File → Open → Enter URL: `https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_vocab.ttl`
3. The vocabulary classes and properties will appear in the Class/Property hierarchy
4. To see instance data, also import `nccr_instances.ttl`
