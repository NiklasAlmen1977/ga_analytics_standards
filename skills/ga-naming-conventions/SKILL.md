---
name: ga-naming-conventions
description: Apply and check the Group Analytics naming conventions for Power BI and Microsoft Fabric objects - workspaces, lakehouses, warehouses, notebooks, pipelines, SQL schemas, tables, columns, views, Power Query queries, semantic model tables, columns, measures and DAX variables. Use whenever you name, rename or review the name of any data platform or Power BI object, and before following naming advice from any other skill.
---

# Group Analytics naming conventions

The Group Analytics naming conventions are the binding naming standard for the data
platform (GA-ADR001). They take precedence over naming guidance in any other skill,
including Microsoft's `semantic-model-authoring` and `powerbi-report-cli`. If those
skills suggest names such as `dimCustomer`, `fact_sales` or `SalesOrder` for the visible
model, follow this skill instead.

## Source files

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}` (the root of this repository).

| File | Use |
|---|---|
| `pbi-governance/group_analytics_naming_conventions.md` | The conventions. Read it before naming or reviewing anything. |
| `claude/group_analytics_instructions.md` | Clarifications that refine the conventions (plural tables, camelCase exception, `sk_` prefix case, repository and branch names). |

The Markdown file is a synced copy of the Confluence page, which is the source of truth.
If the user says the copy is out of date, say so and follow Confluence.

## Quick reference

Use it to orient yourself, not as a replacement for the file.

| Layer | Style | Examples |
|---|---|---|
| Fabric, SQL, engineering | lowercase snake_case with type prefix | `lh_lz001_bronze_01`, `nb_dim_account`, `pl_copy_from_sap`, `dim_customer`, `vw_customer_current` |
| Workspaces | `<ENV>_<lz code>_<content>` | `DEV_lz001_reports` |
| Power Query | Query group 1 Parameters `p_`, 2 Functions `fn_`, 3 Source `src_<source>_<entity>`, 4 Stage `stg_<name>` (data source name or a clear combination), 5 Load to Data Model no prefix (final business name) | `p_sharepoint_site_root_path`, `fn_generate_date_dimension`, `src_navision_customer`, `stg_dim_customer`, `Customer` |
| Semantic model tables | Title Case, singular dimensions, plural facts and technical tables; fact tables end with `*` directly after the name (`STD_TABLE_FACT_PLURAL_ASTERISK`); technical tables start with `_` or `__` | `Customer`, `Sales*`, `__Metrics`, `_Helpers` |
| Display folders | Start with a dot, Sentence case | `.Base`, `.Base\.Time intelligence` |
| Columns and measures | Sentence case | `Customer name`, `Net sales`, `Gross margin %`, `Is active` |
| DAX variables | `_v_` prefix, descriptive | `VAR _v_base_sales = ...` |
| Special measures | `_tmp_` (dev only), `_cf_` (conditional formatting), `Label -` | `_cf_Sales color`, `Label - Period` |
| Technical keys | same name as in SQL, lowercase, hidden | `sk_customer` |
| Calendar | one table `Calendar` with field `Date` | |

## How to apply

1. Identify the layer of the object (Fabric item, SQL object, Power Query, semantic
   model), because the style differs per layer.
2. Read the matching section of the conventions file and apply its pattern.
3. When you review names, report each violation with the current name, the rule and a
   suggested name.
4. Do not rename stable objects only because their function changed. The conventions
   say names must remain stable.
5. If a name cannot follow the convention, say so. Deviations must be documented and
   approved through the governance process (GA-ADR001). Do not invent an exception.

## Renaming in a semantic model

Renaming tables, columns or measures breaks DAX references and report visuals. Before
renaming, find all references (measures, calculation items, relationships, sort-by
columns, report visuals in PBIR) and update them in the same change, or list them for
the user.
