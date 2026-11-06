---
name: ga-governance-maintenance
description: Change the Group Analytics standards repository (ga_analytics_standards) - add, change or remove a principle, standard, BPA rule, rule mapping, release checklist item, Tabular Editor script, TMDL snippet or skill, while keeping the chain from principle to standard to BPA rule to checklist consistent. Use when working in ga_analytics_standards or when the user wants to change a Group Analytics rule or standard.
---

# Maintaining the Group Analytics standards

The repository keeps one chain intact:

```
Principle -> Standard -> Validation (BPA rule or manual) -> Rule mapping -> Checklist -> Review -> main
```

Every change must leave the chain consistent. The full guide is
`${CLAUDE_PLUGIN_ROOT}/How-To-work-with-this-repo.md`. Read it before making a change,
and follow the scenario that matches.

## Files

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}` (the root of this repository).

| File | Holds | ID pattern |
|---|---|---|
| `pbi-governance/principles.yaml` | Principles | `P001` |
| `pbi-governance/standards.yaml` | Standards | `STD_<SUBJECT>_<RULE>` |
| `tabular-editor/bpa/BPARules-base.json` | BPA rules | `GA_<OBJECT>_<RULE>` |
| `pbi-governance/rule-mapping.yaml` | Standard to BPA rule mapping and status | |
| `pbi-governance/release-checklist.yaml` | Checklist items | `CHK_<AREA>_<ITEM>` |
| `pbi-governance/report-design.yaml` | Report design specification (theme, layout, pages, chart choice) behind the `STD_REPORT_*` standards | |
| `pbi-governance/code-style.yaml` | Code style for DAX and Power Query M (formatting, comments, step and variable names) behind `STD_DAX_CODE_STYLE`, `STD_PQ_CODE_STYLE` and `STD_PQ_NAMED_AND_COMMENTED_STEPS` | |
| `report-design/Vitrolife_theme.json` | The approved report theme. Change it together with `report-design.yaml` and the template. | |
| `pbi-governance/group_analytics_naming_conventions.md` | Copy of the Confluence naming page | |
| `skills/`, `agents/`, `hooks/` and `.claude-plugin/` | The Claude plugin with these skills, the reviewer agents and hooks | |
| `tools/build_lineage_inventory.py` | Lineage of one landing zone repository (configuration and PBIP metadata) as JSON for the GA Platform Lineage page | |
| `tools/build_gold_coverage.py` | Gold coverage of Jira tickets for the Gold Ticket Coverage page (ga-gold-coverage skill) | |
| `tools/md_to_pdf.py` | Makes the PDF of a data product documentation file, with Mermaid diagrams (Edge headless, no installation) | |
| `validators/validate_model.py` | The model check in Python (BPA rules, naming, standards). Change it together with the BPA rules. | |
| `claude/` | Instructions imported by development repositories, and the Vitrolife AI rules | |
| `project-template/` | The files a new development repository copies. Keep it in step with the instructions and `docs/getting-started.md`. | |

## Rules

Follow `How-To-work-with-this-repo.md` for the scenario. The points that are easiest to miss:

- **Naming conventions:** Confluence is the source of truth; the Markdown copy is only re-synced.
- **BPA rules:** only for safe, low-noise checks (How-To, "BPA rule or manual?"), always with a
  standard, a mapping and the same check in `validators/validate_model.py`.
- **Removing:** set the mapping to `deprecated` first; never remove a rule silently.
- **Scripts and snippets:** C# scripts start with the Purpose, Scope, Safe to rerun and
  Requires review header; TMDL snippets say whether they are additive or destructive.
- **Scaffold items and template in sync, on the latest version:** change a TMDL snippet
  (scaffold item), change the template in `ga_templates_pbi` in the same way (and the other
  way around): same lineageTags, names, order, descriptions and expressions. Then run the
  read-only `ga-template-reviewer` agent; it says which side is older and must be brought up
  to the latest.
- **Plugin version:** raise it in `.claude-plugin/plugin.json` when a skill, agent or hook
  changes.

## Before the pull request

1. Parse every changed YAML and JSON file.
2. Cross-check IDs: every `standard_id` and `bpa_rule_id` in `rule-mapping.yaml` exists in
   `standards.yaml` and the BPA file; every checklist `standard_refs` entry exists.
3. Run `validators/validate_model.py` on a model where a changed rule should fire and on one
   where it should not (and in Tabular Editor when you change a BPA rule).
4. Branch per the instructions and open a pull request to `main`; the description answers
   `.github/pull_request_template.md`.
