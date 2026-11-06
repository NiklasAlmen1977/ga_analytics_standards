# How to work with this repository

For Group Analytics maintainers who change the standards, rules, snippets, skills or hooks.
Developers who use the setup read [docs/getting-started.md](docs/getting-started.md).

In Claude Code, the `ga-governance-maintenance` skill follows this guide for you. Ask it to
add, change or remove a principle, standard, BPA rule, checklist item, snippet or skill.

## The chain

Every change keeps this chain consistent:

```text
Principle -> Standard -> Validation (BPA rule or manual) -> Rule mapping -> Checklist -> Review -> main
```

| Question | File |
|---|---|
| Why do we do this? | `pbi-governance/principles.yaml` (`P001`...) |
| What is the rule, and is it blocking or a warning? | `pbi-governance/standards.yaml` (`STD_<SUBJECT>_<RULE>`) |
| Can a tool check it? | `tabular-editor/bpa/BPARules-base.json` (`GA_<OBJECT>_<RULE>`) |
| Which tool checks which standard? | `pbi-governance/rule-mapping.yaml` |
| What do people confirm before release? | `pbi-governance/release-checklist.yaml` (`CHK_<AREA>_<ITEM>`) |
| Detailed specifications | `pbi-governance/report-design.yaml`, `pbi-governance/code-style.yaml` |
| Branches, pull requests, publishing | `pbi-governance/ways-of-working.yaml` |

**Enforcement.** Blocking and warning are defined once, in the header of `standards.yaml`. A
BPA rule uses severity 3 for blocking and 2 for warning. Changing a standard from warning to
blocking affects existing models: say so in the pull request.

**BPA rule or manual?** A small, trusted rule set beats a large, noisy one. Create a BPA rule
(and the same check in `validators/validate_model.py`) only when the rule can be checked safely
and consistently, has a low false-positive risk, supports a broadly agreed standard, and was
tested on real models. Keep it manual (a checklist item) when it needs business judgement,
depends heavily on context, or would create noise.

## Workflow

1. Branch from `main` as `feature_<ticketno>_<shortdescription>`, for example
   `feature_GA-612_add_measure_description_rule`.
2. Make the change (see below) and test it.
3. Open a pull request to `main`. The [pull request template](.github/pull_request_template.md)
   holds the questions to answer. Group Analytics reviews it ([CODEOWNERS](.github/CODEOWNERS)).
4. Squash merge. Delete the branch.

Two pull requests that both change the plugin version conflict on `.claude-plugin/plugin.json`
once the first is squash merged. Merge them one at a time and rebase the second.

## Adding, changing or removing a rule

1. **Standard.** Add or update it in `standards.yaml` with `principle_id`, `description`,
   `enforcement`, `validation` (`bpa`, `manual` or `manual_or_bpa`) and `exception_allowed`.
   If only the technical check changes, leave the standard alone.
2. **BPA rule**, if the standard can be checked safely. Test it in Tabular Editor on a model
   where it should fire and on one where it should not. Check severity and message. Add the
   same check to `validators/validate_model.py` (it lists BPA rules without one as "not
   evaluated") and run the script on both models. A check that only the script can do (for
   example Power Query groups) gets `python_check: true` in the mapping.
3. **Mapping.** Every standard and every BPA rule has a row in `rule-mapping.yaml`. When you
   remove a rule, first set its mapping to `status: "deprecated"` (with `replaced_by` if
   something replaces it). Never remove a rule silently.
4. **Checklist.** Add or update a `CHK_*` item when people must confirm it before release.
   It takes the strictest enforcement of the standards it refers to.

## Scripts and snippets

- **C# scripts** (`tabular-editor/csharp-scripts/`) start with this header and are tested in
  Tabular Editor:

  ```csharp
  // Purpose: what the script does.
  // Scope: model / table / column / measure / selected objects.
  // Safe to rerun: Yes/No.
  // Requires review: Yes/No.
  ```

- **TMDL snippets** (`tmdl/`) are `createOrReplace` scripts. State in the pull request whether
  a snippet is additive or destructive, apply it to a copy of a model in Power BI Desktop, and
  update the template in `ga_templates_pbi` when the snippet is part of it. Follow
  `code-style.yaml` for the DAX and M inside.
- **Snippet and template stay in sync.** A snippet and the template object it creates have the
  same lineageTags, names, order, descriptions and expressions, so a model can swap one for the
  other without losing column identity. Change both in the same change (one branch in each
  repository), then run the read-only `ga-template-reviewer` agent. It lists the expected
  differences (for example the `_Report Info` DATATABLE in the template).

## Skills, hooks and the plugin

- Raise `version` in `.claude-plugin/plugin.json` whenever a skill or hook changes; installed
  plugins only update when the version changes. Instructions in `claude/` need no version:
  they are read from the local clone.
- Skills read the governance files at run time. Change a skill only when the workflow changes,
  a file moves, or a new snippet or script must be listed.
- Hooks always exit 0. The AI rules and the two guards act wherever the plugin is enabled; the
  work area guard only in repositories with `.claude/work_areas.conf`; the other hooks only in
  repositories whose `CLAUDE.md` imports these standards.
  Test every path of a changed hook in a short folder path (long paths break `git` on Windows).
- Run `claude plugin validate . --strict` before the pull request.

## Naming conventions

Confluence is the source of truth. Change `pbi-governance/group_analytics_naming_conventions.md`
only to re-sync it, and update its "Synced from Confluence" line. A substantive change needs a
new or superseding ADR (GA-ADR001).

## Environments

See `pbi-governance/ways-of-working.yaml` (`environments`). Snippets and the template still
accept TEST and PROD as values; remove TEST when the move to ACC is done.
