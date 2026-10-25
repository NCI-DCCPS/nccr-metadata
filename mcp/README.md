# NCCR Metadata MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that
exposes the National Childhood Cancer Registry (NCCR) Data Platform metadata as
tools an AI assistant can call directly. Ask natural-language questions about
NCCR data in any MCP-capable client (Claude Desktop, Cursor, Windsurf, VS Code,
Kiro) and get grounded, factual answers — no authentication and no patient-level
data access required.

The server reads the published metadata in this repository (`nccr_instances.ttl`,
`nccr_vocab.ttl`, `datmm/`). For a few high-cardinality fields (e.g., individual
drug names) it fetches aggregate frequency data from the public NCCR data-browser
endpoint on demand.

## Tools

| Tool | What it does |
|------|--------------|
| `list_datasources` | Overview of all 9 datasources with record and filter counts |
| `discover_filters` | Filterable variables for a datasource (title, type, variable) |
| `get_values` | Permissible values + record counts for a variable |
| `top_values` | Top values by frequency (incl. drug names, cancer sites) |
| `search_by_subject` | Which datasets carry a given MeSH subject |
| `get_dataset_info` | Full DATMM profile of a dataset |
| `list_data_elements` | Every variable in a datasource, with source column and type |
| `build_cohort` | Generate a portable cohort definition (RDF/Turtle) |
| `list_request_fields` | The NCCR data request form's fields and character limits |
| `list_research_areas` | Permissible Research Area values for a request |
| `validate_request_draft` | Check a drafted request against the form's rules |

Eleven tools. The first seven are read-only lookups over the published metadata.
`list_request_fields`, `list_research_areas` and `validate_request_draft` support
drafting an actual NCCR data request. `build_cohort` is the only tool that writes
a file.

## Install

```bash
git clone https://github.com/NCI-DCCPS/nccr-metadata.git
cd nccr-metadata/mcp

# Recommended: uv
uv venv --python 3.12
uv pip install -r requirements.txt

# or with the Python you already have
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Use `python3 -m pip`, not a bare `pip` — on macOS the `pip` command is frequently
absent even when pip is installed. See [the tools guide](../docs/tools-guide.md)
for troubleshooting.

## Register with your AI client

Add the server to your client's MCP config, pointing at the script in your
clone. Examples are in `mcp-config-examples/`.

### Claude Desktop
`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):
```json
{
  "mcpServers": {
    "nccr-metadata": {
      "command": "/absolute/path/to/nccr-metadata/mcp/.venv/bin/python3",
      "args": ["/absolute/path/to/nccr-metadata/mcp/nccr_mcp_server.py"]
    }
  }
}
```

### Cursor / Windsurf
Add the same `mcpServers` block to the client's MCP settings file.

### Kiro / VS Code (agent)
Add to `.kiro/settings/mcp.json` (workspace) or the user-level MCP config:
```json
{
  "mcpServers": {
    "nccr-metadata": {
      "command": "/absolute/path/to/nccr-metadata/mcp/.venv/bin/python3",
      "args": ["/absolute/path/to/nccr-metadata/mcp/nccr_mcp_server.py"],
      "disabled": false,
      "autoApprove": [
        "list_datasources", "discover_filters", "get_values", "top_values",
        "search_by_subject", "get_dataset_info", "list_data_elements",
        "list_request_fields", "list_research_areas", "validate_request_draft"
      ]
    }
  }
}
```

Point `command` at the interpreter **inside the virtual environment**, not a bare
`python3` — the system interpreter will not have `mcp` or `rdflib` installed.

Restart the client; the NCCR tools will appear.

## Controlling what runs without asking

`autoApprove` lists the tools the assistant may call without prompting. The
example above approves the ten read-only tools and deliberately omits
`build_cohort`, which is the only tool that writes a file — so exploration is
uninterrupted while anything producing an artifact stops for confirmation.

To make **every** tool prompt, use an empty list or remove the key:

```json
"autoApprove": []
```

This is the only control over MCP tool approval. It is per-server, and it is not
affected by client-level autonomy settings, which govern the client's own file and
shell operations rather than MCP tools.

## Try it

Once registered, just talk to your assistant:

> "What data does NCCR have on radiation therapy for kids?"
>
> "Show me the most common drugs dispensed to pediatric cancer patients."
>
> "Which NCCR datasets are about clinical trials?"
>
> "Build me a cohort of brain tumor patients under 15 who received radiation."

The assistant calls the tools behind the scenes and answers from the real
published metadata.

## Test locally (no client needed)

```bash
.venv/bin/python3 test_server.py
```

This exercises all seven tools and prints their output.

## Notes

- The metadata in this repo is the source of truth. If you run the script from
  outside the repo, it falls back to fetching the published files from GitHub.
- No patient-level data is ever accessed. All results are metadata and aggregate,
  privacy-suppressed statistics (counts below 16 are suppressed).
