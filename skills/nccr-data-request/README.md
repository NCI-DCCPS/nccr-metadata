# NCCR Data Request Skill — Installation

A skill that helps a researcher draft and validate an **NCCR Data Request**: the
narrative sections, Research Areas, collaborator rules, and data element selection.

It is a single portable file, **`SKILL.md`**, with YAML frontmatter (`name`,
`description`). Most agent frameworks that support skills read that format.

## What it pairs with

The skill supplies *judgment* (how to write a good request, the rules, the
prerequisites). The **MCP server** in `../../mcp/` supplies *facts* (form fields,
character limits, research areas, available data elements, draft validation).

Use both together for the full experience. The skill is still useful on its own.

Relevant MCP tools: `list_request_fields`, `list_research_areas`,
`validate_request_draft`, `list_data_elements`.

---

## Install

### Kiro
Copy the skill folder into either location:

```bash
# workspace-level (this project only)
mkdir -p .kiro/skills
cp -R skills/nccr-data-request .kiro/skills/

# or user-level (available in every workspace)
mkdir -p ~/.kiro/skills
cp -R skills/nccr-data-request ~/.kiro/skills/
```

Kiro picks it up on the next session. Ask it something like *"help me write an NCCR
data request"* and it will activate.

### Claude Code
```bash
mkdir -p ~/.claude/skills
cp -R skills/nccr-data-request ~/.claude/skills/
```
(Use `.claude/skills/` inside a project for project-scoped installation.)

### Claude Desktop / claude.ai
Upload or add `SKILL.md` through the app's Skills interface (naming and location vary
by version — see Anthropic's current Skills documentation).

### Strands Harness / other agent frameworks
Strands Harness can load pre-existing skills; point it at this folder. For frameworks
without a formal skill mechanism, include the contents of `SKILL.md` in the system
prompt or supply it as context.

### No skill support at all
Paste the contents of `SKILL.md` into the conversation before you start. It is
written to work that way too.

---

## Verify it's working

Ask your assistant:

> "I need to request NCCR data for a study of late cardiac effects in AYA CNS tumor
> survivors."

You should see it:
1. raise prerequisites (IRB, SEER Research Plus accounts, CCDI mappings approval PDF),
2. **warn that four fields are publicly displayed** before drafting them,
3. report character counts against the 1500-character limits,
4. explain that external collaborators must file their own referencing request.

If it skips the public-display warning, the skill probably isn't loaded.

---

## Keeping it current

The form's fields and limits are also described structurally in
[`../../request-form.ttl`](../../request-form.ttl). **If the live form changes, update
both** that file and `SKILL.md`.

"Recommended" means two different things, and only one of them is metadata:

- **Baseline defaults** the form selects for a source regardless of the science. These
  are recorded in `request-form.ttl` and reported by `list_data_elements`. Confirmed
  for CTC; other sources report none until their defaults are confirmed.
- **Aim-specific recommendations** that NCCR staff raise when they review a submitted
  request, flagging variables the research aims imply but the request left out. That is
  per-request judgement, so it isn't modelled as metadata. `SKILL.md` instructs the
  assistant to run the same coverage check while the draft is still editable.
