---
name: ga-data-product-documentation
description: Write or update the documentation of a Group Analytics BI data product (semantic model and reports) from the PBIP metadata, git history, the Jira ticket and the model review - purpose, ownership, access and RLS, lineage, environments, model, measures, data quality, best practice review result, warnings and things to consider, and change log. Use when development is finished, before a pull request or release, or when the user asks to document a model or report.
---

# Group Analytics data product documentation

Write the documentation of a data product as a Markdown file in the project repository,
from the template in this repository. The document has a part for report users and owners
and a technical part for maintainers. It is a draft that the developer and the business
owner review in the same pull request as the model.

## Source files

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}` (the root of this repository).

| File | Use |
|---|---|
| `docs/templates/data-product-documentation.md` | The template: sections, tables and guidance comments. |
| `pbi-governance/standards.yaml` | `STD_DOCUMENT_*` standards and the enforcement of any standard the review reports. |
| `pbi-governance/release-checklist.yaml` | `CHK_DOC_*` items that this document provides evidence for. |

## Data protection

Use metadata only: TMDL, PBIR, `expressions.tmdl`, git and the Jira ticket. Never read data
files and never copy data values, query results or screenshots with data into the document.
Names of people are limited to business contact data (name, work email, role). If the user
offers data for the document, explain why it is left out.

## Steps

1. **Find the project.** Locate the `*.SemanticModel` and `*.Report` folders, the branch and
   the Jira ticket key (from the branch name `feature_<ticketno>_...`). If the Atlassian
   connector is available, read the ticket description and use it for the purpose and the
   business questions. Otherwise ask the user.
2. **Run or reuse the review.** Use a `ga-model-review` result from this session if the model
   has not changed since; otherwise ask the user whether to run it now. Use a
   `ga-release-checklist` result if there is one. Summarise both in "Best practice review".
   Never mark a manual check as passed on the user's behalf.
3. **Read the metadata** and fill in the technical part:
   - lineage from the partitions and `src_`/`stg_` queries to the source objects (server,
     database, schema, view or file), with the query group of each query;
   - a high-level lineage diagram (the Mermaid outline in the template): source systems,
     landing zone and medallion layer (bronze, silver, gold with lakehouse and schema), model
     tables, measure groups and consumers. Take the gold object from the `src_` queries. When
     the landing zone's `Engineering/` folder is in the repository, read (never change) its
     config files (`destinationDatabase`, `destinationObjectPattern`, `dependsOn`,
     `sourceSystemName`, `sourceDirectoryPattern`) for the silver and bronze layers and the
     source systems. Otherwise ask the user, or write "(not documented yet)". SharePoint lists
     and Excel files that skip the medallion layers go straight to the model, labelled
     "no medallion". Keep it high level: one box per layer, measures in groups;
   - parameters with their values per environment, and the environment detection;
   - tables with type, storage mode and grain, relationships, calculation groups and field
     parameters;
   - measures with their descriptions, display folders and, for non-trivial ones, the logic
     in one sentence;
   - RLS roles, their filter expressions and where the access list comes from;
   - report pages with their purpose (from titles and visuals) and main filters.
4. **Write the warnings.** Collect them from what you read, for example:
   - hard-coded values, placeholder parameter values, personal or local paths;
   - amounts that must not be summed (currencies), measures that return blank by design;
   - manual dependencies (Excel or SharePoint lists maintained by hand) and who maintains them;
   - standards that fail or have exceptions, and items to fix before production;
   - RLS limits (workspace Admins, Members and Contributors see everything).
   Put user-facing warnings in Part 1 and maintainer warnings in Part 2.
5. **Ask for what metadata cannot tell you**: owners, audience, refresh schedule, how the
   numbers were validated and by whom. Write "Not documented yet" for anything the user
   cannot answer now, and list those items at the end of your reply.
6. **Save** as `docs/<semantic model name>.md` in the project repository (create `docs/` if
   needed). If the file exists, update it: keep sections the user wrote, update generated
   sections, and add a change log row.
7. **Report** what you documented, the open items, and the warnings you added. Remind the
   user to review the document in the pull request and to copy it to the Confluence wiki
   page of the model when the Confluence structure is ready.
8. **Publish steps for the developer** (manual for now; the Markdown file is the master and
   the PDF is a copy for business users):
   - Make a PDF of `docs/<semantic model name>.md` with
     `python ../ga_analytics_standards/tools/md_to_pdf.py "docs/<semantic model name>.md" "<folder>/<semantic model name>.pdf"`
     (Edge in headless mode; it also draws the Mermaid diagrams) and save it in the Group Analytics
     [Data Product Documentation](https://vitrolifeglobal.sharepoint.com/sites/GroupAnalytics/Shared%20Documents/Group%20Analytics%20Collaboration/Data%20Product%20Documentation)
     folder on the Collaboration Teams site (or the synced OneDrive folder). Never in git.
   - Copy the link to the PDF ("Copy link" in SharePoint).
   - In the MS list [Analytics | Report info](https://vitrolifeglobal.sharepoint.com/sites/GroupAnalytics-Infiles-PROD/Lists/Analytics%20%20Report%20Info/AllItems.aspx),
     add or update the row of the report: paste the link in `Documentation link`. Write out,
     ready to copy and paste, the texts for `Report overview` and `Data model description`
     (plain language, from the documentation), and the other columns as a table.
   - Make the PDF again after every change to the Markdown file. The link stays the same
     when the file name stays the same.

## Style

- Follow the naming conventions for every object name you write, and write names exactly as
  they are in the model.
- Short sentences, tables for lists of objects, no screenshots.
- Keep the AI-assistance note under the title until the owner has approved the document.
