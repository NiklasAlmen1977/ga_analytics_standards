---
name: ga-measure-authoring
description: Write or change DAX measures in a Power BI semantic model according to Group Analytics standards - measure naming, _v_ variables, descriptions, display folders, explicit measures, time intelligence through the __Time Intelligence calculation group, and dynamic format strings. Use when creating, renaming, documenting or refactoring measures or calculation items.
---

# Group Analytics measure authoring

Use this skill together with Microsoft's `semantic-model-authoring` skill. That skill
covers DAX correctness and performance (`dax-guidelines.md`, `dax-perf-patterns.md`) and
how to edit the model. This skill adds the Group Analytics rules, which take precedence
where the two differ.

## Source files

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}` (the root of this repository).

| File | Use |
|---|---|
| `pbi-governance/group_analytics_naming_conventions.md` | Section "Measures - Sentence case". |
| `pbi-governance/standards.yaml` | `STD_EXPLICIT_MEASURES_REQUIRED`, `STD_VISIBLE_MEASURES_HAVE_DESCRIPTIONS`, `STD_MEASURES_USE_DISPLAY_FOLDERS`, `STD_DAX_CODE_STYLE`. |
| `pbi-governance/code-style.yaml` | Section `dax`: formatting, `_v_` variables and comments, with an example. Follow it for every measure you write or change. |
| `tabular-editor/bpa/BPARules-base.json` | The exact display folder and description rules that the review checks. |

## Rules for every measure

| Topic | Rule | Example |
|---|---|---|
| Name | Sentence case, business terms | `Net sales`, `Gross margin %`, `Order count` |
| Comparison | `<Measure> vs <Measure>` | `Actuals vs Budget` |
| Time intelligence | Base name + established suffix | `Net sales PY`, `Actuals YTD` |
| Variables | `_v_` prefix with a descriptive name, never `_v_x` | `VAR _v_net_sales = ...` |
| Description | Required on visible measures. Explain the business meaning, not the formula. | "Revenue after discounts and returns, excluding VAT." |
| Display folder | Required. Folders and subfolders start with a dot, as checked by `GA_MEASURE_DISPLAY_FOLDER_PREFIX`. | `.Base`, `.Base\.Time intelligence` |
| Location | Measures table `__Metrics`; helper measures in `_Helpers` | |
| Explicit | Business logic as explicit measures. Hide numeric columns that report authors should not aggregate directly. | |
| Special measures | `_tmp_` for temporary measures (never published), `_cf_` for hidden conditional formatting, `Label -` for label measures | `_cf_Margin color` |

In TMDL the description is written as `///` lines directly above the `measure` line.

## Time intelligence

Before writing separate YTD, PY or rolling measures, check whether the model has the
`__Time Intelligence` calculation group (added by the `ga-model-scaffold` skill). If it
does, the base measure is often enough and users pick the time calculation in the
report. Write a dedicated time intelligence measure only when the user needs it as a
separate field, for example in a table with both values side by side, and name it with
the suffix pattern.

## Format strings

For comparison measures (vs target, vs PY) the model may contain
`VLG.FormatString.RelativeToTarget.Numeric.DynamicUnits` from the format string
snippet. Use it in a dynamic format string expression for arrows, plus/minus or colour
symbols instead of writing custom format logic. Read the parameter comments in
`tmdl/Create-vlg-udf-formatstring-TMDL.tmdl` before calling it.

## Checklist before you finish

- [ ] Name, variables and special prefixes follow the rules above
- [ ] DAX is formatted and commented as in `code-style.yaml`
- [ ] Visible measures have a business description
- [ ] Display folder is set and matches the BPA rule
- [ ] Format string is set
- [ ] All references are updated after a rename
- [ ] The user has validated the numbers against a known source. Do not present a new
      measure as correct until it has been checked against real data.
