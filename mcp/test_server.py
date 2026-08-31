#!/usr/bin/env python3
"""Smoke test for the NCCR MCP server tools (calls tool functions directly)."""
import json
import nccr_mcp_server as s

def show(title, result):
    print(f"\n{'='*60}\n{title}\n{'='*60}")
    try:
        parsed = json.loads(result)
        print(json.dumps(parsed, indent=2)[:900])
    except (json.JSONDecodeError, TypeError):
        print(result[:900])

# FastMCP wraps functions; the original callables are accessible via .fn
def call(tool_name, **kwargs):
    tool = tool_fns[tool_name]
    return tool(**kwargs)

# Grab underlying functions
tool_fns = {
    "list_datasources": s.list_datasources.fn if hasattr(s.list_datasources, "fn") else s.list_datasources,
    "discover_filters": s.discover_filters.fn if hasattr(s.discover_filters, "fn") else s.discover_filters,
    "get_values": s.get_values.fn if hasattr(s.get_values, "fn") else s.get_values,
    "top_values": s.top_values.fn if hasattr(s.top_values, "fn") else s.top_values,
    "search_by_subject": s.search_by_subject.fn if hasattr(s.search_by_subject, "fn") else s.search_by_subject,
    "get_dataset_info": s.get_dataset_info.fn if hasattr(s.get_dataset_info, "fn") else s.get_dataset_info,
    "build_cohort": s.build_cohort.fn if hasattr(s.build_cohort, "fn") else s.build_cohort,
}

show("list_datasources", call("list_datasources"))
show("discover_filters(RO)", call("discover_filters", datasource="RO"))
show("get_values(Sex)", call("get_values", variable="Sex"))
show("top_values(canmedNonProprietaryName, 5, PHARM)",
     call("top_values", field="canmedNonProprietaryName", limit=5, datasource="PHARM"))
show("search_by_subject(Radiation)", call("search_by_subject", mesh_term="Radiation"))
show("get_dataset_info(ctc)", call("get_dataset_info", dataset_id="ctc"))
show("build_cohort", call("build_cohort", name="Pediatric CNS 0-14",
     datasources=["RO", "PHARM"],
     filters=[{"filter": "Min Age (Yrs)", "values": [0]},
              {"filter": "Max Age (Yrs)", "values": [14]},
              {"filter": "ICCC Major (Level 1)", "values": ["03"]},
              {"filter": "Sex", "values": ["ALL"]}]))
print("\n\nALL TOOLS EXECUTED")
