---
layout: page
title: Usage & Examples
nav_order: 5
---

# Usage & Code Examples

## Loading the ontology

### Python (rdflib)

```python
from rdflib import Graph, Namespace

NCCR = Namespace("https://nccrdataplatform.ccdi.cancer.gov/vocab#")

g = Graph()
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_vocab.ttl")
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_datmm.ttl")
g.parse("https://raw.githubusercontent.com/NCI-DCCPS/nccr-metadata/main/nccr_instances.ttl")

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
