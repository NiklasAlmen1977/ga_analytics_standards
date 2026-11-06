---
name: ga-model-review
description: Review a Power BI semantic model (PBIP/TMDL folder) against Group Analytics standards - naming conventions, governance standards in standards.yaml, and the Group Analytics Tabular Editor Best Practice Analyzer (BPA) rules. Use when asked to review, validate, audit, lint or check a semantic model, or before a pull request or release.
---

# Group Analytics model review

Review a semantic model against the Group Analytics standards and report findings with
the ID of the standard or rule that is broken. This skill reviews and reports. Only
change the model when the user asks for fixes.

## Source files

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}` (the root of this repository).

| File | Use |
|---|---|
| `pbi-governance/standards.yaml` | The standards (`STD_*`) with their enforcement level (`blocking` or `warning`) and whether exceptions are allowed. |
| `pbi-governance/rule-mapping.yaml` | Which BPA rule implements which standard, and which standards are still `candidate` or `manual`. |
| `tabular-editor/bpa/BPARules-base.json` | The BPA rules (`GA_*`) with their Tabular Editor expressions. |
| `pbi-governance/group_analytics_naming_conventions.md` | Naming rules for the semantic model layer. Also load the `ga-naming-conventions` skill. |
| `pbi-governance/principles.yaml` | Principles (`P001`...) that the standards refer to. |

Read the YAML and JSON files at the start of every review. Do not rely on the examples in
this skill, because the rule set changes.

## Steps

1. **Locate the model.** Find the `*.SemanticModel/definition/` folder (TMDL) in the
   repository. Work on the files; the Power BI modeling MCP is blocked during the pilot.
   Read the exceptions the project documents (its `CLAUDE.md` and `docs/<model>.md`) and do
   not report them as new findings.
2. **Run the model check.** It needs only Python 3.8+ (Windows and macOS, no installation)
   and evaluates the BPA rules in `BPARules-base.json`, the mechanical naming checks
   (`NC_*`) and some standards (`STD_*`). It only reports and never blocks:

   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/validators/validate_model.py" "<model or repository folder>"
   ```

   On Windows use `python` if `python3` fails. If Python is not available, evaluate each
   rule's `Expression` yourself against the TMDL. Rules listed under "Not evaluated" have no
   Python check yet: evaluate those yourself. Tell the user which method you used.
   Findings that carry the annotation `BestPracticeAnalyzer_IgnoreRules` are counted as
   ignored; check that each such exception is documented.

   For a second opinion with a fresh context, the `ga-standards:ga-reviewer` agent runs this
   review read-only.
3. **Check the standards without a BPA rule.** For each standard in `standards.yaml` whose
   mapping is `candidate`, `manual` or `manual_or_bpa`, check what can be read from the
   metadata, for example:
   - star schema shape and snowflaked dimensions (`STD_STAR_SCHEMA_DEFAULT`)
   - one Calendar table for all date roles, with inactive relationships and
     `USERELATIONSHIP` (`STD_SINGLE_DATE_DIMENSION`)
   - relationship column data types (`STD_RELATIONSHIP_COLUMNS_INTEGER_WHERE_POSSIBLE`)
   - datetime columns that should be split (`STD_SPLIT_DATE_AND_TIME`)
   - sort by column and data categories (`STD_SORT_BY_AND_DATA_CATEGORY`)
   - `discourageImplicitMeasures` in `model.tmdl` (`STD_EXPLICIT_MEASURES_REQUIRED`)
   - Power Query query groups, prefixes and parameters in `expressions.tmdl` and the
     partitions (`STD_PQ_*`)

   Mark judgement calls as "needs human review" instead of pass or fail.
4. **Check naming** with the `ga-naming-conventions` skill: table, column and measure
   case, plural or singular table names, prefixes, `_v_` DAX variables, hidden `sk_`
   keys. The `NC_*` checks are heuristics: before you suggest a rename, check the warning
   against the naming page (for example, in `<Measure> vs <Measure>` each measure keeps its
   own first capital: `Sales vs Budget`). When the check is wrong, say so instead of renaming.
5. **Report** using the format below.

## Report format

Start with a one-line summary: number of blocking findings, warnings and items for human
review. List **blocking findings first** (see the header of `standards.yaml`); then warnings.
Group each list by category (Naming, Modeling, Power Query, Documentation, Usability,
Performance):

| Object | Finding | Rule / standard | Enforcement | Suggested fix |
|---|---|---|---|---|
| `'Sales*'[CustomerKey]` | Visible technical key | `GA_TECHNICAL_COLUMNS_SHOULD_BE_HIDDEN` / `STD_HIDE_TECHNICAL_KEY_COLUMNS` | blocking | Hide the column |

- Take the enforcement from the standard in `standards.yaml`, not from the rule. BPA
  severity 3 corresponds to blocking and 2 to warning.
- Where `exception_allowed: true`, say that an exception is possible if it is
  documented (`STD_DOCUMENT_EXCEPTIONS`).
- Group repeated findings (for example 40 measures without description) into one row
  with a count and list the objects below the table.
- End with gaps: standards that `rule-mapping.yaml` marks as `candidate` or
  `not_suitable_for_bpa` without `python_check`, so the team knows what the review could not
  cover automatically.

## Fix or exception

Tools never block. After the report, go through the
findings rule by rule, blocking standards first, and ask the user with clickable options:

- **Fix**: show the concrete change (for example the description text, the new name with
  the references it updates, or `summarizeBy: none`), and apply it only after the user agrees.
- **Document an exception**: only where the standard has `exception_allowed: true`. Add
  `annotation BestPracticeAnalyzer_IgnoreRules = {"RuleIDs":["<rule ID>"]}` to the object
  (or to the model for a model-wide exception) and a line with the rule, the objects and the
  reason under the exceptions in `docs/<semantic model name>.md` (`STD_DOCUMENT_EXCEPTIONS`).
- **Later**: keep it in the report; it is listed in the pull request.

Group repeated findings into one question (for example 12 measures without description).

## Fixing findings

Prefer the rule's `FixExpression` where one exists.
The Tabular Editor scripts in `tabular-editor/csharp-scripts/` can help, for example
`Hide columns on the many side of a relationship.csx`. Renames must follow the
`ga-naming-conventions` skill and update all references.
