# Group Analytics Naming Conventions

> **Source of truth:** [Naming Conventions – Group Analytics (Confluence)](https://vitrolifegroup.atlassian.net/wiki/spaces/GA/pages/838467604/Naming+Conventions)
> **Decision record:** [GA-ADR001 – Unified naming convention for Power BI and Microsoft Fabric objects](https://vitrolifegroup.atlassian.net/wiki/spaces/GA/pages/839680003/GA-ADR001+-+Unified+naming+convention+for+Power+BI+and+Microsoft+Fabric+objects)
> **Synced from Confluence:** 2026-10-08 (page version 32)
>
> This file is a repository copy of the Confluence page. Confluence remains the source of truth. If the two differ, Confluence wins, and this file should be re-synced via a pull request.

This page is the single canonical naming convention for Power BI and Microsoft Fabric objects on the data platform, merging what were previously two separate pages. It is the naming convention referenced by **GA-ADR001**, which decided that this convention must be used across the data platform regardless of which domain or team is building within it.

## Terminology

- **MUST**: mandatory requirement
- **SHOULD**: recommended best practice
- **MAY**: optional / situational

## General principles

- Fabric/SQL/engineering-layer object names MUST be lowercase, snake_case, with words separated by underscores. Special characters, spaces, and accented characters MUST NOT be used. Exception: the environment prefix in workspace names is upper case (`DEV_`, `ACC_`, `PRD_`). Note that parameters use CamelCase in the framework.
- The Power BI semantic model layer (the user-facing layer — tables, fields, measures) is the documented exception: it uses Title Case for tables and Sentence case for fields/measures, using spaces rather than underscores, per the [Power BI semantic model layer](#power-bi-semantic-model-layer) section below. This exception is explicitly permitted under the general Fabric rule that UI-level, business-facing artifacts (e.g. Semantic Models) MAY use Sentence case & Title Case.
- Names MUST reflect business meaning rather than technical implementation details wherever the object is business-facing.
- Numbers MUST only be used for sequence elements and landing zone codes (e.g. `lz001`).
- Naming SHOULD favour singular nouns to represent logical concepts, even when the underlying data is a collection. Exception in the Power BI layer is Measures table, Helpers tables and Fact table that uses plural.
- Object names SHOULD reflect their logical role and MUST remain stable over time. Functional changes alone MUST NOT trigger renaming unless the object's purpose fundamentally changes.
- Any deviation from this naming convention MUST be explicitly documented and approved as part of the platform governance process (see GA-ADR001).

## Workspaces

Pattern: `<environment>_<lz_code>_<content>`

| Environment | Pattern | Example | Remarks |
| --- | --- | --- | --- |
| Dev | `DEV_<lz_code>_<content>` | `DEV_lz001_reports` | Content hints at the artifact type in the workspace: reports, data_models, engineering, playground |
| Acc | `ACC_<lz_code>_<content>` | `ACC_lz001_reports` | |
| Prd | `PRD_<lz_code>_<content>` | `PRD_lz001_reports` | |

This replaces the earlier "Domain/Team code" (`ai0xx`) pattern used by some existing workspaces. Existing `ai0xx` workspaces are migrated to the `lz0xx` format per GA-ADR001; this is not a new/parallel pattern.

Workspace name also contains a hint of artefact type:

- engineering: for all backend artefacts as well as the lakehouse
- data_models: where we keep all the semantic models. this way we can separate access for analysts vs engineers.
- reports: the visualisations/reports shown in Power BI. this is the most common layer for consuming reports
- playground: one offs of reports for adhoc purposes or for testing things. this workspace does not have the production level the other environments require.

Workspace items should be organized into folders named by item type, with logical/functional sub-folders where useful. Projects not using Medallion architecture MAY adopt a different logical organization — the essential requirement is consistency and clarity for current and future users.

## Data engineering & data stores (Fabric items)

Use short, systematic prefixes and include `<lz_code>` (the landing zone code), `<layer>` (bronze/silver/gold, MAY be used when the project follows Medallion architecture), and `<object>` in object names.

| Item (UI) | Prefix | Naming pattern | Example | Remarks |
| --- | --- | --- | --- | --- |
| Lakehouse | `lh` | `lh_<lz_code>[_<layer>][_<sequence>]` | `lh_lz001_bronze_01` | Layer MUST be used for projects with Medallion architecture. |
| Warehouse | `wh` | `wh_<lz_code>[_<sequence>]` | `wh_lz001` | |
| Notebook | `nb` | `nb_<purpose>` | `nb_dim_account` | Utility notebooks MAY omit the prefix if stored in a dedicated utilities folder |
| Spark Job Definition | `job` | `job_<purpose>` | `job_load_csvToParquet` | |
| Environment | `cfg` | `cfg_<lz_code>_<purpose>` | `cfg_lz001_orchestrator` | |
| SQL Database | `sql` | `sql_<lz_code>[_<sequence>]` | `sql_datahub` | |
| User Data Functions | `fn` | `fn_<lz_code>_<purpose>` | | |
| Variable Library | `vl` | `vl_<lz_code>_<sequence>` | `vl_datahub_01` | |
| Shortcut | `sc` | `sc_<source>_<entity>` | `sc_adls_customer`, `lz001.navision_account` | MUST reflect external source and shared entity. For tables: namespace should be the originating landing zone and the table name should reflect the namespace. In gold default is dbo and can be omitted. |

## SQL objects

Applies to Lakehouse SQL Endpoints, Warehouses, and SQL Databases, regardless of whether the project follows Medallion architecture.

- Object names MUST be lowercase, snake_case, no special/accented characters.
- Abbreviations SHOULD be avoided unless widely recognized.
- Names MUST reflect business meaning rather than technical implementation.

### Schemas

| Object | Pattern | Example | Remarks |
| --- | --- | --- | --- |
| Schema Bronze | NA | | Bronze is in files |
| Schema Silver | `<source_system>` | `navision` | references the source system where the data is originating |
| Schema Gold | `<consumer>` | `dbo.table_name`, `aaro_integration.table_name` | default is dbo as schema for general consumption for eg. Power BI. If there is a data product developed for a specific usecase this can be put in a separate schema where specific access rights can be applied. |

### Tables

| Object | Pattern | Example | Remarks |
| --- | --- | --- | --- |
| Table (generic) | `<entity>` | `customer` | Represents a business entity. There will at minimum be one table in silver reflecting names from Bronze |
| Table (typed, gold layer) | `<type>_<entity>` | `dim_customer`, `fact_sales` | `<type>` is dim, fact, bridge, or agg |
| Staging table | `stg_<source>_<entity>` | `stg_moodys_rating` | Landing/ingested data ahead of transformation into dim/fact tables — conceptually silver-equivalent, not a gold-layer table type |

**Note on `stg`:** `stg` refers to landing/ingestion-stage data, not a table type that lives inside the gold layer. A staging table holds raw or lightly processed source data prior to being modeled into dimension/fact tables; it should not be confused with the dim/fact/bridge/agg types used for gold-layer tables.

### Columns

| Object | Pattern | Example | Remarks |
| --- | --- | --- | --- |
| Business key | `bk_<entity>` | `bk_customer` | Used for business keys in dimensional models (refers to the natural key) |
| Surrogate key | `sk_<entity>[_<roleplay>]` | `sk_customer` | Used for surrogate keys in dimensional models |
| Date column | `<event>_date` | `as_of_date` | Use `_timestamp` for datetime |
| Timestamp column | `<event>_timestamp` | `created_timestamp` | |
| Boolean column | `is_<condition>` / `has_<condition>` | `is_active`, `has_defaulted` | |
| Amount column | `<metric>_amount[_<currency>]` | `sales_amount_eur` | Currency optional |
| Generic column | `<business_term>` | `risk_weight` | snake_case |

## Column abbreviations and standard names

Abbreviations in Gold layer column names should be limited to approved terms. The same concept must always use the same abbreviation across Gold models.

| Meaning | Pattern | Example | Remarks |
| --- | --- | --- | --- |
| Number | `<entity>_no` | `product_area_no` | use for recognizable business numbers |
| Quantity | `<metric>_qty` | | |
| Percentage | `<metric>_pct` | | |
| Average | `<measure>_avg` | | |
| Minimum | `<metric>_min` | | |
| Maximum | `<metric>_max` | | |
| Count | `<metric>_count` | | |
| Amount | `<metric>_amount` | `sales_amount` | |
| Amount Currency | `<metric>_amount[_<currency>]` | `sales_amount_eur` | Currency optional |
| Year to date | `_ytd` | | |
| Month to date | `_mtd` | | |

## Technical metadata columns

Framework-managed technical columns use the `ctr_` prefix to distinguish them from source and business attributes. Their presence depends on the layer and configured processing pattern.

| Column | Layer | Processing method | Purpose |
| --- | --- | --- | --- |
| `ctr_hash_key` | Bronze / Silver | Change detection / Merge / History | Hash of the configured key columns used to identify and match records. |
| `ctr_hash_validate` | Bronze / Silver / Gold | Change detection / Merge / History / Dimension | Hash of record attributes used to detect changes. |
| `ctr_is_bronze_deleted` | Bronze | Change detection | Indicates a source deletion identified during Landing-to-Bronze change detection. |
| `ctr_file_name` | Silver | Overwrite / Append / Merge / History | Identifies the source file associated with the record, where available. |
| `ctr_ins_timestamp` | Silver / Gold | All standard loads | Timestamp when the record was inserted into the layer. |
| `ctr_last_operation_timestamp` | Silver / Gold | Merge / History / Gold loads | Timestamp of the latest framework operation affecting the record. |
| `ctr_partition_key` | Silver | Append | Technical partitioning value used for applicable append loads. |
| `ctr_action` | Silver | Merge | Identifies the action performed during merge processing. |
| `ctr_is_deleted` | Silver | Merge | Indicates whether a record has been logically deleted during merge processing (soft delete). |
| `ctr_hash_validate_history` | Silver / Gold | History / SCD | Hash used to detect changes in historically tracked attributes. |
| `ctr_hash_validate_non_history` | Silver / Gold | History / SCD | Hash used to detect changes in non-historically tracked attributes. |
| `ctr_is_active` | Silver | History | Indicates the currently active version of a historical record. |
| `ctr_start_timestamp` | Silver | History | Start of validity for a historical record version. |
| `ctr_end_timestamp` | Silver | History | End of validity for a historical record version. |
| `ctr_hash_dim_key` | Gold | Dimension | Technical hash key used to uniquely identify dimension records. |

**Note:** Bronze technical columns are added when **change detection** is enabled during Landing-to-Bronze processing, allowing new, changed and deleted source records to be identified. Silver and Gold technical columns vary according to the configured load type (e.g. overwrite, append, merge or history) and are not expected to be present in every table.

### Views, functions, stored procedures, keys & indexes

| Object | Pattern | Example |
| --- | --- | --- |
| View | `vw_<entity>[_<purpose>]` | `vw_customer_current` |
| Function | `fn_<purpose>` | `fn_calculate_conversion_rate` |
| Stored Procedure | `sp_<verb>_<object>[_<purpose>]` | `sp_refresh_risk_snapshot` |
| Primary Key | `pk_<table>` | `pk_dim_customer` |
| Foreign Key | `fk_<table>_<referenced_table>` | `fk_fact_exposure_dim_customer` |

## Data Factory (ingestion & orchestration)

| Item | Prefix | Pattern | Example |
| --- | --- | --- | --- |
| Pipeline | `pl` | `pl_<purpose>` | `pl_copy_from_sap` |
| Copy Job | `cj` | `cj_<source>_to_<target>` | |
| Dataflow Gen2 | `df` | `df_<purpose>` | |

`<purpose>` SHOULD start with a verb describing the action.

## Real-Time Intelligence & Data Science

| Item | Prefix | Pattern | Example |
| --- | --- | --- | --- |
| Eventhouse | `eh` | `eh_<lz_code>[_<sequence>]` | `eh_lz036_01` |
| Eventstream | `es` | `es_<lz_code>[_<sequence>]` | |
| ML Experiment | `exp` | `exp_<lz_code>_<sequence>` | |
| ML Model | `ml` | `ml_<lz_code>_<sequence>` | |

## Parameters & variables

The prefix (`p_` or `v_`) is separated by an underscore; logical names use snake case (e.g. `data_date`). Avoid abbreviations, cryptic names, or environment-specific suffixes.

| Context | Element | Prefix | Example |
| --- | --- | --- | --- |
| Pipeline | Parameter | `p_` | `p_model` |
| Pipeline | Variable | `v_` | `v_output_json` |
| Notebook | Parameter | `p_` | `p_model` |
| Variable Library | Variable name | (lower snake case, no prefix) | `workspace_name` |

## YAML configuration files

YAML configuration files must use lowercase snake_case.

All the files must start with the model name. Include files can be used and must also start with the model name and an identifier, e.g. `finance_gl_argentina.yaml`.

## Access groups & accounts

**TBD.** Naming for Entra ID access groups, service accounts and service principals is not decided yet. The earlier draft pattern (`aad-<domain>-<scope>-<role>`, `svc-`, `spn-`) is no longer used.

## Power BI semantic model layer

This is the user-facing layer exposed to report builders and business users: tables, columns, measures, hierarchies, display folders, and hidden technical objects. This is the documented exception to the lowercase/snake_case rule above.

- Use business terms; avoid exposing technical source-system names unless already established business terms.
- Do not use prefixes such as `dim`, `fact`, `dm`, or `tbl` in the visible model. These layer prefixes belong to the SQL/staging layer, not the semantic model loaded tables.

### Power Query

Queries are organised in the query groups of the Power BI template. The query group decides the prefix of the query name:

| Query group | Prefix | Purpose | Example |
| --- | --- | --- | --- |
| **1. Parameters** | `p_` | Parameters for source paths, connections and environment-related values, so a change is made in one place. Name = `p_` followed by snake_case. | `p_sharepoint_site_root_path` |
| **2. Functions** | `fn_` | Reusable Power Query (M) functions. Same pattern as SQL functions: `fn_<purpose>` in snake_case, where `<purpose>` starts with a verb. | `fn_generate_date_dimension` |
| **3. Source** | `src_` | Base connection queries for credentials, paths, and raw typing. Name = data source name. | `src_navision_customer` |
| **4. Stage** | `stg_` | If needed — intermediate cleansing, type conversions, and star schema preparation. This should not be needed if coming from backend/engineering. Name = data source name, or if a combination, adapt but make the purpose and source clear. | `stg_dim_customer` |
| **5. Load to Data Model** | *None* | Final curated dimension and fact tables loaded to the data model, in the subgroups Fact Tables, Dimension Tables and Disconnected Tables. | `Customer`, `Sales*` |

Note that **only** final business-ready tables in **5. Load to Data Model** are loaded into the model, using the normal table naming format without a prefix.

### Tables — Title Case

Recommended: `Customer`, `Product`, `Sales Order`, `Forecast Version`.
Avoid: `dimCustomer`, `dm_customer`, `fact_sales`, `SalesOrder`.

Singular for dimensions, plural for facts and where it fits (on non-dimension tables).

Fact tables: business-oriented name in Title Case; append `*` if the model standard requires facts to be visually marked (e.g. `Sales*`).

Technical tables start with underscores, so they sort above the business tables in the field list and are recognisable as technical:

| Table | Name | Remarks |
| --- | --- | --- |
| Measures table | `__Metrics` | Holds the measures. Two underscores keep it at the top of the field list. Plural, like other non-dimension tables. |
| Time intelligence calculation group | `__Time Intelligence` | |
| Helper measures | `_Helpers` | Measures for layout, dates, icons and conditional formatting colours. |

### Columns / fields — Sentence case

Recommended: `Customer name`, `Order date`, `Net sales amount`, `Is active`.
Avoid: `Customer Name`, `customerName`, `customer_name`.

### Measures — Sentence case

Recommended: `Net sales`, `Gross margin %`, `Order count`.
Avoid: `netSales`, `measure_net_sales`, `Measure 1`.

- **Measure variables** (DAX): `_v_` prefix, e.g. `VAR _v_base = ...`. Use descriptive names, not `_v_x` / `_v_y` / `_v_z`.
- **Comparison measures**: `<Measure name> vs <Measure name>`, e.g. `Actuals vs Budget`.
- **Time intelligence measures**: base name + suffix, e.g. `Actuals YTD`, `Net sales PY`. Established abbreviations (YTD, MTD, QTD, PY, YoY, MoM, 12M) are acceptable.
- **Temporary measures** (dev only, not published): prefix `_tmp_`.
- **Conditional formatting measures**: prefix `_cf_`, normally hidden.
- **Label measures**: prefix `Label -`.
- All visible measures SHOULD have a description explaining business meaning, not just the calculation.

### Display folders

Display folders start with a dot, so they sort above the measures in the same table, and use Sentence case. Subfolders also start with a dot.

Examples: `.Base`, `.Base\.Time intelligence`, `.Base\.Comparisons`, `.Labels & conditional formatting`.

### Technical keys, booleans, dates

Technical keys (e.g. `sk_customer`) should normally be hidden. Boolean fields: `Is active`, `Is deleted` (not `Active`, `Flag1`). The single standard Calendar dimension's date field should be named `Date`; the dimension itself should be named `Calendar`.

## Placeholder definitions

| Placeholder | Description | Example |
| --- | --- | --- |
| `<lz_code>` | Landing zone code | `lz001` |
| `<purpose>` | Functional intent of the object | ingestion, analysis, logging |
| `<layer>` | Medallion layer | bronze, silver, gold |
| `<sequence>` | Numeric discriminator when multiple objects exist | `01`, `02` |
| `<environment>` | Deployment environment, upper case in workspace names | DEV, ACC, PRD |
| `<entity>` | Business entity the object represents, singular | customer, sales_order |
| `<source>` | Originating source system or storage | navision, adls, moodys |
| `<metric>` | Business quantity being measured | sales, discount, order |
| `<currency>` | ISO 4217 currency code, lowercase | eur, sek, usd |
| `<event>` | Business event a date or timestamp column marks | created, as_of, shipped |
| `<consumer>` | Consuming use case or data product for a gold schema | dbo (default), aaro_integration |

## What changed

**2026-10-08: Power BI Semantic Model Layer**

- Technical table name changed according to what is currently being implemented: measures table `__Metrics`.

**2026-10-05: Placeholder clean-up**

- Landing zone placeholder standardised to `<lz_code>` everywhere (previously mixed with `<lz code>` and `<Landing Zone code>`). Workspace pattern now reads `<environment>_<lz_code>_<content>`.
- Missing closing brackets added: `fn_<lz_code>_<purpose>` and `<metric>[_<currency>]` (Columns and Column Abbreviations tables).
- Placeholder Definitions extended with `<environment>`, `<entity>`, `<source>`, `<metric>`, `<currency>`, `<event>` and `<consumer>`.
- `<domain>` removed from Placeholder Definitions, as no pattern on this page uses it any more.
- Typos fixed (consumption, conversion, If needed) and the Shortcut row examples split onto separate lines.
- Power BI technical key example aligned with SQL: `sk_customer` (previously `sk_Customer`).
- Upper case environment prefix in workspace names (`DEV_`, `ACC_`, `PRD_`) documented as an explicit exception to the lowercase rule in General Principles.
- Amount with currency aligned with the Amount row: pattern `<metric>_amount[_<currency>]`, example `sales_amount_eur` (previously `<metric>[_<currency>]` / `amount_eur`), in both the Columns and Column Abbreviations tables.
- Amount row pattern in Column Abbreviations changed to `<metric>_amount` (previously `_amount`), so Amount and Amount Currency read the same way.
- General Principles: numbers rule now also allows landing zone codes (e.g. `lz001`), which previously contradicted "Numbers MUST only be used for sequence elements".

## Governance

Any deviation from this convention MUST be documented and approved through the analytics governance process before implementation (see GA-ADR001). Additive changes (new object types, clarified examples) are made directly to the Confluence page. Substantive changes (e.g. changing a delimiter, redefining an object type) require a new or superseding ADR.
