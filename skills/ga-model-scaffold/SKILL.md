---
name: ga-model-scaffold
description: Add the standard Group Analytics components to a Power BI semantic model from the approved TMDL snippets - Calendar date dimension, __Time Intelligence calculation group, _Environment detection, header and footer label measures, _Report Info, _Metric Info, _Metric business definition, and the VLG format string DAX functions with _Scale. Use when setting up a new semantic model, or when the user asks to add a calendar, time intelligence, environment banner, report or metric metadata, or dynamic format strings.
---

# Group Analytics model scaffold

New models start from the approved template in
https://vitrolife-group.ghe.com/group-analytics/ga_templates_pbi (principle `P001`).
Copy the template into the project repository and never edit the template repository
as part of project work. Use this skill to add the standard components to a model that
lacks them.

## Right after copying the template

The template is a starting point with placeholders. Ask the developer these questions with
clickable options (the same text is in the README of `ga_templates_pbi`), apply the answers,
and note them for the documentation:

1. **What is the product?** (`STD_REPORT_LANDING_AND_START_PAGE`)
   - *Analytics report*: as in the template: Definition, Welcome, then the analysis pages;
     the report opens on Overview.
   - *Semantic model only (sm)*: make the Welcome page the landing page (`landingPageName`
     in `pages.json`) and remove Overview and Details. With RLS, point
     `_Helpers[Your access]` at the RLS dimension. The Welcome page is required.
   - *Validation report*: the Welcome page is the landing page (it may be renamed "What can
     I find in this report?").

   In every case, resize the page navigator on the Welcome page to the pages that are left
   (64 px plus 48 px per page).
2. **Report info: where does it come from?**
   - *Keep the manual table (start quickly)*: the template's `_Report Info` is a calculated
     table; fill in the placeholder values (owner, refresh, overview, documentation link)
     by hand. Can be switched to the list later.
   - *Connect to the MS list Analytics Report Info (recommended before release)*: apply the
     Metadata parameter and Report info snippets, set `p_report_name` and
     `p_semantic_model_name`, and make sure the list has a row with both Report and Semantic
     model filled in (the combination selects the row).
3. **What to add now or later** (multi-select; everything else is already in the template):
   Environment from SharePoint, Metric business definition, Format strings with `_Scale`.
   Say what each adds and what it needs (table below), and that it can also be added later
   with this skill.

## Snippets

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}` (the root of this repository). Each
file is a `createOrReplace` TMDL script.

| Component | File | Creates | Depends on |
|---|---|---|---|
| Metadata parameter | `tmdl/Create-Analytics-Metadata-Parameter-TMDL.tmdl` | Parameter `p_analytics_metadata_site_root_path`, set to the PROD metadata site (the metadata lists live there for every environment) | Nothing |
| Calendar | `tmdl/Create-Calendar-TMDL.tmdl` | M function `fn_generate_date_dimension`, staging query `stg_calendar`, and the `Calendar` table marked as date table, with the friendly names from the calendar specification. Range 2020-01-01 to the end of next year, recalculated at refresh. | Nothing |
| Time intelligence | `tmdl/Create-__Time-Intelligence-TMDL.tmdl` | Calculation group `__Time Intelligence` (MTD, QTD, YTD, PY, YoY, MoM, rolling 3/6/12 months, and more) | `Calendar[Date]` |
| Environment | `tmdl/Create-Environment-TMDL.tmdl` | Queries `src_sharepoint_analytics_environment` and `stg_analytics_environment`, parameter `p_environment_manual`, table `_Environment` with the environment banner label and `_cf_` colour measures | Metadata parameter |
| Report info | `tmdl/Create-_Report-Info-TMDL.tmdl` | Parameters `p_report_name` and `p_semantic_model_name`, query `src_sharepoint_analytics_report_info`, table `_Report Info` from SharePoint | Metadata parameter, SharePoint metadata list |
| Header and footer labels | `tmdl/Create-_Helpers-Report-Labels-TMDL.tmdl` | Measures `Label - Footer user`, `Label - Footer period`, `Label - Footer last date` (placeholder to point at the fact table), `Label - Instructions`, and `Welcome user` and `Your access` (placeholder to point at the RLS dimension) for the start page, in `_Helpers` (additive) | `_Helpers` from the template, `Calendar` |
| Metric business definition | `tmdl/Create-_Metric business definition-TMDL` (no file extension) | Query `src_sharepoint_analytics_metric_business_definition`, table `_Metric business definition` | Metadata parameter, SharePoint metadata list |
| Metric info | `tmdl/Create-_Metric-Info-TMDL.tmdl` | Hidden calculated table `_Metric Info` listing the visible measures in `__Metrics` with description, DAX and display folder (`INFO.VIEW.MEASURES()`) | `_Report Info` with a `Message` column |
| Format strings | `tmdl/Create-vlg-udf-formatstring-TMDL.tmdl` | DAX functions `VLG.FormatString.RelativeToTarget.Numeric.DynamicUnits`, `DaxLib.FormatString.Component.*`, table `_Scale` | A Power BI version and model compatibility level that support DAX user-defined functions |

Read the snippet before applying it. The files are the source of truth, and this table
can fall behind.

## Order and dependencies

1. **Metadata parameter first**, and only once per model. It is the only snippet that
   defines `p_analytics_metadata_site_root_path`; the other snippets only refer to it.
2. **Calendar, then `__Time Intelligence`.**
3. **SharePoint snippets** (`_Environment`, `_Report Info`, `_Metric business definition`)
   in any order after the parameter. Set `p_report_name` and `p_semantic_model_name` after
   applying `_Report Info`.
4. **`_Report Info` from SharePoint replaces the template's `_Report Info`**, which is a
   calculated DATATABLE you fill in by hand. Both have the same columns, including
   `Message` and `Documentation link` (data category Web URL, shown as a link in the Report
   info matrix), so the Definition page works with either. Power BI Desktop cannot switch a
   calculated partition to Power Query while the model is open, and not with "Apply external
   changes": close Desktop, rename `.pbi/cache.abf` (the developer does this, it is a data
   file), reopen the PBIP and refresh.

## The Calendar table

- Column names are the friendly names from the Group Analytics calendar specification
  (for example `Current year offset`, `Year month`, `Is weekday`). Do not rename them in a
  project.
- Month and weekday names are in English, independent of the model's locale.
- The date range starts on 2020-01-01. If a model needs older dates, change `Start_Date`
  in `stg_calendar`, not `fn_generate_date_dimension`.
- Disable auto date/time for the model if it is still on.

## How to apply

**Option A - Power BI Desktop (recommended for the user).** Open the model, go to the
TMDL view, paste the snippet and select Apply. Desktop resolves lineage tags and
`ref` entries itself.

**Option B - edit the PBIP files (when you make the change).**

1. Find the `*.SemanticModel/definition/` folder.
2. Split the `createOrReplace` script into the PBIP file layout:
   - `table` blocks into `tables/<table name>.tmdl`
   - `expression` blocks into `expressions.tmdl`
   - `function` blocks into `functions.tmdl`
3. Remove one level of indentation, since `createOrReplace` adds one.
4. Add `ref table '<name>'` lines to `model.tmdl` if the model lists table references.
5. Keep the lineage tags from the snippet unless the object already exists in the
   model.
6. Ask the user to open the project in Power BI Desktop to validate it and refresh.


## After applying

- Leave the technical `_` and `__` tables as they are in the snippet. If a snippet
  conflicts with the naming conventions, raise it as a change to this repository
  instead of renaming it in one project.
- The SharePoint snippets need credentials for the Group Analytics metadata site and
  a refresh before data appears.
- Run the `ga-model-review` skill to check the result.
