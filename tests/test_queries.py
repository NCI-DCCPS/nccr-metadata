#!/usr/bin/env python3
"""
Tests for NCCR Metadata SPARQL Queries
=======================================
Validates that every query documented in metadata/usage.md returns
correct results against the published TTL files. Run with:

    python tests/test_queries.py

Or with pytest:

    pytest tests/test_queries.py -v

These tests ensure that changes to the ontology or instance data
don't break the documented usage examples.
"""

import sys
from pathlib import Path

import pytest
from rdflib import Graph

# ============================================================
# Fixtures — load the graph once for all tests
# ============================================================

REPO_ROOT = Path(__file__).parent.parent

@pytest.fixture(scope="module")
def graph():
    """Load all TTL files into a single graph."""
    g = Graph()
    # Vocabulary
    g.parse(REPO_ROOT / "nccr_vocab.ttl", format="turtle")
    # Instances
    g.parse(REPO_ROOT / "nccr_instances.ttl", format="turtle")
    # DATMM files
    datmm_dir = REPO_ROOT / "datmm"
    for ttl_file in datmm_dir.glob("*.ttl"):
        g.parse(ttl_file, format="turtle")
    print(f"\nLoaded {len(g)} triples from all TTL files")
    return g


# ============================================================
# Test: Basic graph integrity
# ============================================================

class TestGraphIntegrity:
    """Verify the graph loads and has expected minimum content."""

    def test_triple_count_minimum(self, graph):
        """Graph should have at least 40K triples."""
        assert len(graph) > 40000, f"Expected >40000 triples, got {len(graph)}"

    def test_datasources_exist(self, graph):
        """All 9 datasources should exist."""
        results = graph.query("""
            PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
            SELECT (COUNT(?ds) as ?n) WHERE { ?ds a nccr:DataSource . }
        """)
        count = int(list(results)[0][0])
        assert count == 9, f"Expected 9 DataSources, got {count}"

    def test_variables_exist(self, graph):
        """Should have 533 variables."""
        results = graph.query("""
            PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
            SELECT (COUNT(?v) as ?n) WHERE { ?v a nccr:Variable . }
        """)
        count = int(list(results)[0][0])
        assert count == 533, f"Expected 533 Variables, got {count}"

    def test_cohort_filters_exist(self, graph):
        """Should have 51 cohort filters."""
        results = graph.query("""
            PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
            SELECT (COUNT(?f) as ?n) WHERE { ?f a nccr:CohortFilter . }
        """)
        count = int(list(results)[0][0])
        assert count == 51, f"Expected 51 CohortFilters, got {count}"

    def test_code_values_have_frequencies(self, graph):
        """At least 2000 CodeValues should have recordCount."""
        results = graph.query("""
            PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
            SELECT (COUNT(?cv) as ?n) WHERE { ?cv nccr:recordCount ?c . }
        """)
        count = int(list(results)[0][0])
        assert count >= 2000, f"Expected >=2000 CodeValues with counts, got {count}"


# ============================================================
# Test: Documented query — List all visible CTC variables
# ============================================================

class TestVisibleCTCVariables:
    """From usage.md: 'List all visible CTC variables'"""

    QUERY = """
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
    """

    def test_returns_results(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) > 50, f"Expected >50 visible CTC variables, got {len(results)}"

    def test_sex_is_visible(self, graph):
        results = list(graph.query(self.QUERY))
        labels = [str(row.label) for row in results]
        assert "Sex" in labels, "Sex should be a visible CTC variable"

    def test_nccrid_is_not_visible(self, graph):
        """nccrId has Visible_in_UI=false, should not appear."""
        results = list(graph.query(self.QUERY))
        labels = [str(row.label) for row in results]
        assert "NCCR Persistent Identifier" not in labels


# ============================================================
# Test: Documented query — Find all cohort filters for CTC
# ============================================================

class TestCohortFiltersCTC:
    """From usage.md: 'Find all cohort filters for a datasource'"""

    QUERY = """
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
    """

    def test_returns_results(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) > 10, f"Expected >10 CTC filters, got {len(results)}"

    def test_sex_filter_exists(self, graph):
        results = list(graph.query(self.QUERY))
        titles = [str(row.title) for row in results]
        assert "Sex" in titles

    def test_year_of_diagnosis_filter(self, graph):
        results = list(graph.query(self.QUERY))
        titles = [str(row.title) for row in results]
        assert "Year of Diagnosis" in titles

    def test_filter_has_correct_type(self, graph):
        results = list(graph.query(self.QUERY))
        sex_rows = [row for row in results if str(row.title) == "Sex"]
        assert len(sex_rows) == 1
        assert str(sex_rows[0].type) == "EQUALS"


# ============================================================
# Test: Documented query — Get permissible values for sex
# ============================================================

class TestPermissibleValuesSex:
    """From usage.md: 'Get permissible values for a variable'"""

    QUERY = """
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
    """

    def test_returns_male_and_female(self, graph):
        results = list(graph.query(self.QUERY))
        descriptions = [str(row.description) for row in results]
        assert "Male" in descriptions
        assert "Female" in descriptions

    def test_correct_codes(self, graph):
        results = list(graph.query(self.QUERY))
        code_map = {str(row.code): str(row.description) for row in results}
        assert code_map.get("1") == "Male"
        assert code_map.get("2") == "Female"


# ============================================================
# Test: Documented query — Variables linked to NAACCR
# ============================================================

class TestVariablesLinkedToNAACCR:
    """From usage.md: 'Find variables linked to a specific standard'"""

    QUERY = """
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
    """

    def test_returns_results(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) > 0, "Should find variables linked to NAACCR"

    def test_naaccr_record_version_found(self, graph):
        results = list(graph.query(self.QUERY))
        labels = [str(row.label) for row in results]
        assert "NAACCR Record Version" in labels


# ============================================================
# Test: Documented query — Derived (binned) variables
# ============================================================

class TestDerivedBinnedVariables:
    """From usage.md: 'List all derived (binned) variables'"""

    QUERY = """
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
    """

    def test_returns_results(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) > 0, "Should find derived binned variables"

    def test_bins_have_valid_ranges(self, graph):
        results = list(graph.query(self.QUERY))
        for row in results:
            assert float(row.min) <= float(row.max), (
                f"Bin {row.binLabel} has min > max"
            )


# ============================================================
# Test: Documented query — Value distributions (frequencies)
# ============================================================

class TestValueDistributions:
    """From usage.md: 'Query value distributions (frequencies)'"""

    QUERY = """
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
    """

    def test_returns_male_and_female_counts(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) == 2, f"Expected 2 sex values with counts, got {len(results)}"

    def test_female_count(self, graph):
        results = list(graph.query(self.QUERY))
        counts = {str(row.label): int(row['count']) for row in results}
        assert counts["Female"] == 900104, f"Expected Female=900104, got {counts.get('Female')}"

    def test_male_count(self, graph):
        results = list(graph.query(self.QUERY))
        counts = {str(row.label): int(row['count']) for row in results}
        assert counts["Male"] == 574264, f"Expected Male=574264, got {counts.get('Male')}"


# ============================================================
# Test: Documented query — Total record counts per datasource
# ============================================================

class TestTotalRecordCounts:
    """From usage.md: 'Get total record counts per datasource'"""

    QUERY = """
    PREFIX nccr: <https://nccrdataplatform.ccdi.cancer.gov/vocab#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?source ?label ?count WHERE {
        ?source a nccr:DataSource ;
                rdfs:label ?label ;
                nccr:totalRecordCount ?count .
    }
    ORDER BY DESC(?count)
    """

    EXPECTED_COUNTS = {
        "Medical Claims Procedure": 62669037,
        "Medical Claims Diagnosis": 54148739,
        "Pharmacy Claims": 12611171,
        "Consolidated Tumor Case (CTC)": 1474368,
        "Area-Based Measures": 1474368,
        "Children's Oncology Group (COG)": 1359308,
        "Medical Claims Enrollment": 1359308,
        "Childhood Cancer Data Initiative (CCDI) Mappings": 20838,
        "Radiation Oncology": 4335,
    }

    def test_all_datasources_have_counts(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) == 9, f"Expected 9 datasources with counts, got {len(results)}"

    def test_ctc_count(self, graph):
        results = list(graph.query(self.QUERY))
        counts = {str(row.label): int(row['count']) for row in results}
        assert counts.get("Consolidated Tumor Case (CTC)") == 1474368

    def test_mcp_count(self, graph):
        results = list(graph.query(self.QUERY))
        counts = {str(row.label): int(row['count']) for row in results}
        assert counts.get("Medical Claims Procedure") == 62669037

    def test_all_counts_match(self, graph):
        results = list(graph.query(self.QUERY))
        counts = {str(row.label): int(row['count']) for row in results}
        for label, expected in self.EXPECTED_COUNTS.items():
            assert counts.get(label) == expected, (
                f"{label}: expected {expected}, got {counts.get(label)}"
            )


# ============================================================
# Test: Documented query — Find rare values
# ============================================================

class TestRareValues:
    """From usage.md: 'Find rare values (low frequency)'"""

    QUERY = """
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
    """

    def test_returns_results(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) > 0, "Should find rare values"

    def test_all_counts_below_threshold(self, graph):
        results = list(graph.query(self.QUERY))
        for row in results:
            assert int(row['count']) < 100

    def test_no_suppressed_values(self, graph):
        """Counts should be >= 16 (small cell suppression threshold)."""
        results = list(graph.query(self.QUERY))
        for row in results:
            assert int(row['count']) >= 16, (
                f"Found count {row['count']} for {row.code} — should be suppressed"
            )


# ============================================================
# Test: Documented full example — Filterable pharmacy variables
# ============================================================

class TestFilterablePharmVariables:
    """From usage.md: full Python example."""

    QUERY = """
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

    def test_returns_results(self, graph):
        results = list(graph.query(self.QUERY))
        assert len(results) > 0, "Should find filterable pharmacy variables"

    def test_drug_category_filter(self, graph):
        results = list(graph.query(self.QUERY))
        titles = [str(row.filterTitle) for row in results]
        assert "CanMED Drug Category" in titles


# ============================================================
# Test: DATMM structure (per NLM feedback)
# ============================================================

class TestDATMMStructure:
    """Validate DATMM records match NLM requirements."""

    def test_repository_exists(self, graph):
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT ?repo ?title WHERE {
                ?repo a datmm:Repository ;
                      dct:title ?title .
            }
        """))
        assert len(results) == 1
        assert "NCCR" in str(results[0].title)

    def test_nine_datasets_in_repository(self, graph):
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT ?ds ?title WHERE {
                ?ds a datmm:Dataset ;
                    dct:isPartOf <http://id.nlm.nih.gov/datmm/repository/nccr-data-platform> ;
                    dct:title ?title .
            }
        """))
        assert len(results) == 9, f"Expected 9 datasets in repository, got {len(results)}"

    def test_datasets_have_three_subjects(self, graph):
        """Every dataset must have exactly 3 subjects (Pediatrics + Neoplasms + specific)."""
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT ?ds ?title (COUNT(?subj) as ?n) WHERE {
                ?ds a datmm:Dataset ;
                    dct:title ?title ;
                    dct:subject ?subj .
            }
            GROUP BY ?ds ?title
        """))
        assert len(results) == 9, f"Expected 9 datasets, got {len(results)}"
        for row in results:
            assert int(row.n) == 3, f"{row.title} has {row.n} subjects, expected 3"

    def test_all_datasets_share_pediatrics_and_neoplasms(self, graph):
        """Every dataset must include the shared Pediatrics + Neoplasms concepts."""
        pediatrics = "http://id.nlm.nih.gov/datmm/concept/nccr-0001"
        neoplasms = "http://id.nlm.nih.gov/datmm/concept/nccr-0002"
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT ?ds (GROUP_CONCAT(STR(?subj); separator=",") as ?subjects) WHERE {
                ?ds a datmm:Dataset ;
                    dct:subject ?subj .
            }
            GROUP BY ?ds
        """))
        for row in results:
            subjects = str(row.subjects)
            assert pediatrics in subjects, f"{row.ds} missing Pediatrics"
            assert neoplasms in subjects, f"{row.ds} missing Neoplasms"

    def test_ten_concepts_defined(self, graph):
        """Exactly 10 MeSH-backed concepts should be defined."""
        results = list(graph.query("""
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            SELECT ?concept WHERE {
                ?concept a skos:Concept .
                FILTER(STRSTARTS(STR(?concept), "http://id.nlm.nih.gov/datmm/concept/"))
            }
        """))
        assert len(results) == 10, f"Expected 10 concepts, got {len(results)}"

    def test_concepts_follow_nlm_pattern(self, graph):
        """Each concept must have dct:source, rdfs:label, skos:inScheme 'MeSH RDF', and a MeSH dct:identifier."""
        results = list(graph.query("""
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?concept ?source ?label ?scheme ?id WHERE {
                ?concept a skos:Concept ;
                         dct:source ?source ;
                         rdfs:label ?label ;
                         skos:inScheme ?scheme ;
                         dct:identifier ?id .
                FILTER(STRSTARTS(STR(?concept), "http://id.nlm.nih.gov/datmm/concept/"))
            }
        """))
        assert len(results) == 10, f"Expected 10 fully-formed concepts, got {len(results)}"
        for row in results:
            assert str(row.source) == "repository_supplied", f"{row.concept} wrong dct:source"
            assert str(row.scheme) == "MeSH RDF", f"{row.concept} wrong skos:inScheme"
            assert str(row.id).startswith("http://id.nlm.nih.gov/mesh/D"), (
                f"{row.concept} dct:identifier is not a MeSH URI: {row.id}"
            )

    def test_pediatrics_and_neoplasms_mesh_ids(self, graph):
        """Verify the two shared concepts map to the correct MeSH descriptors."""
        results = list(graph.query("""
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?label ?id WHERE {
                ?concept rdfs:label ?label ;
                         dct:identifier ?id .
                FILTER(STRSTARTS(STR(?concept), "http://id.nlm.nih.gov/datmm/concept/"))
            }
        """))
        mesh = {str(row.label): str(row.id) for row in results}
        assert mesh.get("Pediatrics") == "http://id.nlm.nih.gov/mesh/D010372"
        assert mesh.get("Neoplasms") == "http://id.nlm.nih.gov/mesh/D009369"

    def test_single_seer_contributor(self, graph):
        """Every dataset must reference exactly one contribution: the SEER Program."""
        seer = "http://id.nlm.nih.gov/datmm/contribution/seer"
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX bf: <http://id.loc.gov/ontologies/bibframe/>
            SELECT ?ds ?title (COUNT(?contrib) as ?n) (GROUP_CONCAT(STR(?contrib); separator=",") as ?contribs) WHERE {
                ?ds a datmm:Dataset ;
                    dct:title ?title ;
                    bf:contribution ?contrib .
            }
            GROUP BY ?ds ?title
        """))
        assert len(results) == 9
        for row in results:
            assert int(row.n) == 1, f"{row.title} has {row.n} contributions, expected 1"
            assert seer in str(row.contribs), f"{row.title} does not reference SEER"

    def test_seer_contribution_structure(self, graph):
        """The SEER contribution must have bf:agent and bf:role (Wikidata contributor URI)."""
        results = list(graph.query("""
            PREFIX bf: <http://id.loc.gov/ontologies/bibframe/>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            SELECT ?agent ?role ?name WHERE {
                <http://id.nlm.nih.gov/datmm/contribution/seer> bf:agent ?agent ;
                    bf:role ?role .
                ?agent foaf:name ?name .
            }
        """))
        assert len(results) == 1, "SEER contribution should have exactly one agent"
        row = results[0]
        assert str(row.role) == "http://www.wikidata.org/entity/Q20204892"
        assert "SEER" in str(row.name)

    def test_repository_has_shared_subjects(self, graph):
        """The Repository must carry the shared Pediatrics + Neoplasms subjects."""
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?label WHERE {
                ?repo a datmm:Repository ;
                      dct:subject/rdfs:label ?label .
            }
        """))
        labels = sorted(str(r.label) for r in results)
        assert labels == ["Neoplasms", "Pediatrics"], f"Repository subjects: {labels}"

    def test_only_ctc_references_article(self, graph):
        """Only the CTC dataset should reference the PubMed article; it is the sole Documentation."""
        # Exactly one Documentation node, and it is the PMC article
        docs = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT ?doc ?type ?title WHERE {
                ?doc a datmm:Documentation ;
                     dct:type ?type ;
                     dct:title ?title .
            }
        """))
        assert len(docs) == 1, f"Expected 1 Documentation node, got {len(docs)}"
        assert str(docs[0].type) == "article"
        assert "Cancer Registries" in str(docs[0].title)

        # Only CTC references it
        refs = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT ?ds WHERE {
                ?ds a datmm:Dataset ;
                    dct:isReferencedBy ?doc .
            }
        """))
        ds_ids = [str(r.ds).split("/")[-1] for r in refs]
        assert ds_ids == ["nccr-ctc"], f"Expected only nccr-ctc to reference article, got {ds_ids}"

    def test_no_fabricated_dictionary_docs(self, graph):
        """The old made-up '-dictionary' Documentation nodes must be gone."""
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            SELECT ?doc WHERE {
                ?doc a datmm:Documentation .
                FILTER(CONTAINS(STR(?doc), "dictionary"))
            }
        """))
        assert len(results) == 0, f"Found {len(results)} leftover dictionary Documentation nodes"

    def test_no_funding_present(self, graph):
        """Funding was intentionally dropped — no schema:funding or Grant should exist."""
        results = list(graph.query("""
            PREFIX schema: <http://schema.org/>
            SELECT ?s ?o WHERE { ?s schema:funding ?o . }
        """))
        assert len(results) == 0, f"Found {len(results)} schema:funding triples; expected 0"
        grants = list(graph.query("""
            PREFIX schema: <http://schema.org/>
            SELECT ?g WHERE { ?g a schema:Grant . }
        """))
        assert len(grants) == 0, f"Found {len(grants)} Grant records; expected 0"

    def test_repository_has_no_url_identifier(self, graph):
        """Repository dct:identifier should be omitted (NLM assigns a linked-data URI)."""
        results = list(graph.query("""
            PREFIX datmm: <http://id.nlm.nih.gov/datmm/>
            PREFIX dct: <http://purl.org/dc/terms/>
            SELECT ?id WHERE {
                ?repo a datmm:Repository ;
                      dct:identifier ?id .
            }
        """))
        assert len(results) == 0, "Repository should not carry a URL as dct:identifier"


# ============================================================
# Run directly
# ============================================================

if __name__ == "__main__":
    # Allow running without pytest
    from rdflib import Graph as G
    g = G()
    g.parse(REPO_ROOT / "nccr_vocab.ttl", format="turtle")
    g.parse(REPO_ROOT / "nccr_instances.ttl", format="turtle")
    for ttl_file in (REPO_ROOT / "datmm").glob("*.ttl"):
        g.parse(ttl_file, format="turtle")
    print(f"Loaded {len(g)} triples")

    # Run each test class manually
    test_classes = [
        TestGraphIntegrity, TestVisibleCTCVariables, TestCohortFiltersCTC,
        TestPermissibleValuesSex, TestVariablesLinkedToNAACCR,
        TestDerivedBinnedVariables, TestValueDistributions,
        TestTotalRecordCounts, TestRareValues, TestFilterablePharmVariables,
        TestDATMMStructure,
    ]
    passed = 0
    failed = 0
    for cls in test_classes:
        instance = cls()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)(g)
                    passed += 1
                    print(f"  PASS: {cls.__name__}.{method_name}")
                except (AssertionError, Exception) as e:
                    failed += 1
                    print(f"  FAIL: {cls.__name__}.{method_name} — {e}")

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
