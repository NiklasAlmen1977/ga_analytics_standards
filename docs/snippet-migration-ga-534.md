# Migrating a model to the GA-534 snippets and template

GA-534 (October 2026) renamed objects in the TMDL snippets and the Power BI domain template so they follow the Group Analytics naming conventions. It also fixed several bugs. Use this guide for a semantic model that was built from the earlier template or snippets.

New models do not need this guide. They start from the PBIP template in `ga_templates_pbi` (`Power BI templates/PBIP/`).

## Before you start

- Work in a feature branch (`feature_<ticketno>_<shortdescription>`) on the PBIP version of the model.
- Open the model in Power BI Desktop and rename objects there. Desktop then updates the DAX references and the visuals of the report in the same project at the same time.
- Thin reports that connect to the model from other projects are **not** updated. List them first, and fix their field references after the model is published.
- Check `tmdl/` for the current snippets. The tables below show the names that changed.

## 1. Power Query

### Query groups

| Old | New |
| --- | --- |
| `2. M Functions` | `2. Functions` |
| `3. Data Sources` | `3. Source` |
| `4. Staging Tables` | `4. Stage` |

`1. Parameters` and `5. Load to Data Model` keep their names. Each group decides the query prefix: `p_`, `fn_`, `src_`, `stg_`, and no prefix in `5. Load to Data Model`.

### Parameters, functions and queries

| Old | New | Snippet or template |
| --- | --- | --- |
| `Analytics_Metadata_SiteRoot_Path` | `p_analytics_metadata_site_root_path` | Metadata parameter (own snippet now) |
| `Environment_Manual` | `p_environment_manual` | Environment |
| `ReportName`, `SemanticModelName` (were not defined) | `p_report_name`, `p_semantic_model_name` | Report Info |
| `src_AnalyticsEnvironments` | `src_sharepoint_analytics_environment` | Environment |
| `src_AnalyticsEnvironments_SharePoint` | `stg_analytics_environment` | Environment |
| `src_AnalyticsReportInfo` | `src_sharepoint_analytics_report_info` | Report Info |
| `src_AnalyticsMetricsBusinessDefinition` | `src_sharepoint_analytics_metric_business_definition` | Metric business definition |
| `_fn_DateDimension` | `fn_generate_date_dimension` | Calendar |
| `stg_Calendar` | `stg_calendar` | Calendar |
| `Datawarehouse_ServerHostName` | `p_datawarehouse_server_host_name` (on-premises SQL Server, e.g. vitro-bicdev; kept while models still use it) | Template |
| (new) | `p_sql_endpoint_server_host_name` (Fabric SQL analytics endpoint) | Template |
| `Datawarehouse_HTTPPath`, `p_datawarehouse_http_path` | Removed (neither SQL Server nor a SQL analytics endpoint uses an HTTP path) | Template |
| `SharePoint_SiteRoot_Path` | `p_sharepoint_site_root_path` | Template |
| `SharePoint_Folder_Path` | `p_sharepoint_folder_path` | Template |
| `NullMember_String` | `p_null_member_string` | Template |

Values: the metadata parameter lists the DEV, TEST, ACC and PROD sites, with DEV selected. The earlier snippets selected PROD.

## 2. Tables

| Old | New |
| --- | --- |
| `_Metric info` | `_Metric Info` |
| `_Report info (domain)` | `_Report Info` (now with a `Message` column) |
| `_Info_Metric information` (referenced in the Definition page, did not exist) | `_Metric Info` |

`__Metrics`, `Calendar`, `_Helpers`, `__Time Intelligence`, `_Environment` and `_Metric business definition` keep their names.

## 3. Calendar columns

The Calendar now uses the friendly names from the calendar specification. The date range is 2020-01-01 to the end of next year, recalculated at every refresh. Month and weekday names use the en-US culture.

| Old | New |
| --- | --- |
| `CurrYearOffset` | `Current year offset` |
| `Quarter & Year` | `Year quarter` (format `2026 Q1`) |
| `CurrQuarterOffset` | `Current quarter offset` |
| `Month` | `Month number` |
| `Start of Month` | `Start of month` |
| `End of Month` | `End of month` |
| `Month Name` | `Month name` |
| `Month Short` | `Month short` |
| `Month Initial` | `Month initial` |
| `Month & Year` | `Year month` (format `2026 Mar`) |
| `MonthnYear` | `Year month number` (hidden) |
| `CurrMonthOffset` | `Current month offset` |
| `Week Number` | `Week number` |
| `Week & Year` | `Year week` (format `2026 W02`) |
| `WeeknYear` | `Year week number` (hidden) |
| `CurrWeekOffset` | `Current week offset` |
| `Day of Month` | `Day of month` |
| `Day of Week Number` | `Day of week number` |
| `Day of Week Name` | `Day of week name` |
| `Day of Week Initial` | `Day of week initial` |
| `CurrDayOffset` | `Current day offset` |
| `IsWeekDay` | `Is weekday` |
| `Quarter Number`, `QuarternYear` | Removed |
| (new) | `Month flag` |

`Date`, `Year`, `Year flag` and `Quarter` keep their names. Apply the new Calendar snippet (it replaces `stg_calendar` and the `Calendar` table), then update DAX and visuals that use the old column names.

## 4. Measures, folders and calculation items

| Old | New |
| --- | --- |
| `Sales_Example`, `Budget_Example` | `Sales`, `Budget` (template examples) |
| `Text Sales`, `Text Budget Sales` | `Label - Sales`, `Label - Budget` |
| `Label Sales PY` | `Label - Sales PY` |
| `Data Bar (squared) - Sales  vs Budget` | `Label - Sales vs Budget bar (squared)` |
| `Data Bar (round) - Sales vs budget` | `Label - Sales vs Budget bar (round)` |
| `DateToUse`, `DateToUse (text)`, `DateToUse_EndDateOfMonth` | `Date to use`, `Date to use (text)`, `Date to use end of month` |
| `Icon direction UP`, `Icon direction DOWN` | `Icon direction up`, `Icon direction down` |
| `Report or Semantic model message` | `Report or semantic model message` |
| `_Connected environment` | `Label - Connected environment` |
| `_cf BackgroundHex`, `_cf TextHex` | `_cf_Environment background`, `_cf_Environment text` |
| Display folder `.Base\.Time Intelligence` | `.Base\.Time intelligence` (all display folders start with a dot) |
| Calculation items `3M Rolling`, `3M Rolling Avg`, `6M Rolling`, `6M Rolling Avg`, `12M Rolling`, `12M Rolling Avg`, `Accumulated (Dynamic)` | `3M rolling`, `3M rolling avg`, `6M rolling`, `6M rolling avg`, `12M rolling`, `12M rolling avg`, `Accumulated (dynamic)` |

DAX variables use the `_v_` prefix, for example `VAR _v_previous_year_value`. Rename them when you touch a measure. They are local to the measure, so nothing else breaks.

## 5. Other columns

| Table | Old | New |
| --- | --- | --- |
| `_Metric Info` | `Desc` | `Description` |
| `_Environment` | `DisplayName`, `BackgroundHex`, `TextHex`, `IsProd`, `SharePoint_SiteRoot_Path`, `Datawarehouse_ServerHostName` | `Display name`, `Background hex`, `Text hex`, `Is prod`, `SharePoint site root path`, `Data warehouse server host name`, and the new `SQL endpoint server host name` and `SQL database name` (from the list columns `SqlEndpoint` and `SqlDatabaseName`) |
| `_Metric business definition` | `Approval Status`, `Unit of Measure`, `Leading/Lagging` | `Approval status`, `Unit of measure`, `Leading/lagging` |

The SharePoint list columns keep their names; the snippets rename them in Power Query. The Environment snippet also reads the list columns `SqlEndpoint` and `SqlDatabaseName` (the Fabric SQL analytics endpoint and its database for each environment), next to `Datawarehouse_ServerHostName` (the on-premises SQL Server, for example vitro-bicdev). `Datawarehouse_ServerHostName` stays while models still read from the on-premises data warehouse.

## 6. Bugs fixed by the new snippets

Applying the new snippets also fixes these issues in older models:

- **Metadata parameter:** two snippets defined `Analytics_Metadata_SiteRoot_Path`. Its value was PROD instead of DEV.
- **Environment detection:** it compared against the domain's SharePoint parameter instead of the metadata site.
- **`_cf TextHex`:** it returned the background colour instead of the text colour.
- **Report Info:** it referred to `ReportName` and `SemanticModelName`, which were never defined.
- **Template `__Metrics` measures:** `Sales vs Budget`, `Sales vs Budget %` and `Data Bar (round)` had garbled DAX.
- **Calendar range:** the template's Calendar ended on 2025-12-31.

## Steps

1. Create a feature branch and open the PBIP in Power BI Desktop.
2. Rename the Power Query groups, parameters and queries in sections 1 and 2.
3. Apply the new snippets in the TMDL view. Apply the metadata parameter first, then Calendar, `__Time Intelligence` and the SharePoint snippets.
4. Delete objects that the snippets replaced and that are still in the model, for example the old `Analytics_Metadata_SiteRoot_Path`, `src_Analytics*` queries or `_fn_DateDimension`. A `createOrReplace` script does not remove objects whose name changed.
5. Rename the remaining tables, columns and measures in the model view, using sections 2 to 5. Desktop updates DAX and the visuals in the same report.
6. Refresh, and check every report page for broken visuals.
7. Run the `ga-model-review` skill (it runs the model check, `validators/validate_model.py`).
8. Fix field references in thin reports that use the model, then create the pull request.

Claude Code can do steps 2 to 5 on the PBIP files with the `ga-model-scaffold` and `ga-naming-conventions` skills. Always open and refresh the result in Power BI Desktop before you commit.
