---
name: ga-report-design
description: Design, build or review Power BI report pages according to the Group Analytics report design standards - Vitrolife theme, 1280x720 page layout on a 16 px grid, header, KPI row and footer, Definition and Validation pages (and a Data quality page when issues are known), at most 1-2 slicers per page with filters in the filter pane and visuals that also filter, bookmarks only for the filter pane, tab order, chart choice (pie and donut charts with at most 5 categories), and conditional formatting through the _cf_ measures. Use when planning, designing, editing (PBIR) or reviewing a report page or visual, and before following design advice from other skills.
---

# Group Analytics report design

Use this skill together with Microsoft's `powerbi-report-cli` skill, which handles
planning, PBIR editing, preview and publishing. This skill adds the Group Analytics design
rules, which take precedence where the two differ. Microsoft's design mode may suggest its
own palette, fonts or layout. Use the Vitrolife theme and the layout below instead.

## Source files

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}` (the root of this repository).

| File | Use |
|---|---|
| `pbi-governance/report-design.yaml` | The design specification: theme values, canvas, grid, positions of header, KPI row, content area and footer, pages, chart selection. |
| `pbi-governance/standards.yaml` | The enforceable rules, `STD_REPORT_*`. |
| `pbi-governance/release-checklist.yaml` | The `report` section of the checklist. |
| `report-design/Vitrolife_theme.json` | The theme file. Apply it as the report's custom theme. |

Read `report-design.yaml` before you design or review a page. The values in this skill are
a summary and can fall behind.

## The rules people miss most

Read `report-design.yaml` for every value; it is the specification. Enforcement (blocking or
warning) is defined in the header of `standards.yaml`. These are the rules most often missed:

- **Theme:** the Vitrolife theme with Arial; no colours or fonts set on single visuals.
  Good, bad and neutral colours come from `_cf_Good color`, `_cf_Bad color`, `_cf_Neutral color`.
- **Template chrome on every page:** environment card at the top centre, info line under the
  title, footer card, and the information and filter pane buttons in their fixed positions.
  Copy a template page instead of building them.
- **The right landing page:** an analytics report opens on Overview; a semantic model only
  (sm) and a validation report open on the start page "Welcome" (a validation report may
  call it "What can I find in this report?"). For a semantic model only it is required and
  shows the user's access when the model has RLS. Its page navigator is sized to the number
  of pages (64 px plus 48 px per page).
- **Definition page first**, then the Welcome page, with `_Report Info` and `_Metric Info`;
  a Validation page; and development pages hidden or removed before publishing.
- **At most 1-2 slicers per page:** other filters go in the filter pane; visuals filter
  through cross-filtering.
- **Pie and donut charts only with at most 5 categories**, and business terms (no bronze,
  silver, gold) in every visible text.
- **Tables and matrices show all their columns:** a column width for every field, together
  fitting the visual width minus padding, word wrap on, no Grow to fit. Check again after
  every field change.

Field and visual names follow the `ga-naming-conventions` skill.

## Building a page

1. Start from the template (the `ga_templates_pbi` clone next to the repository). Copy an
   existing page such as Overview, so the environment card, info line, footer and buttons are
   already in place.
2. Plan the content: which questions the page answers, which measures go in the KPI row, and
   which visuals fill the content area. For a new report, use the planning mode of
   `powerbi-report-cli` and get the user's approval first.
3. Choose chart types with the `chart_selection` section of `report-design.yaml`. Count the
   categories before you choose a pie or donut chart.
4. Place visuals on the grid with the positions from `report-design.yaml`.
5. Validate the PBIR and preview the page with `powerbi-report-cli`.

## Reviewing a report

Read the PBIR files (`*.Report/definition/`) and report findings per page in a table,
blocking findings first:

| Page | Visual | Finding | Standard | Enforcement | Suggested fix |
|---|---|---|---|---|---|

Check at least:

- **Theme:** `report.json` uses the Vitrolife custom theme.
- **Canvas:** page size is 1280 x 720 in `page.json`.
- **Layout:** the header, KPI row and footer elements are present and positioned as in
  `report-design.yaml`. Allow small deviations and flag visuals that overlap or fall
  outside the canvas.
- **Tables and matrices:** for each `tableEx` and `pivotTable`, list the projected fields
  (`queryRef`) and the `objects.columnWidth` entries. Flag a field without a width, widths
  whose sum is larger than the visual width minus the padding, widths for fields that are no
  longer in the visual (stale selectors, often copied from the template),
  `columnAdjustment` `'growToFit'`, and word wrap that is off. Suggest widths that fit
  (`tables_and_matrices` in `report-design.yaml`).
- **Pie and donut charts:** for each `pieChart` or `donutChart`, find the category field and
  check the number of distinct values in the model. Flag more than 5, or ask the user if you
  cannot count them.
- **Hard-coded colours:** colour literals (`#RRGGBB`) in visual `objects`, other than theme
  references and `_cf_` measures.
- **Landing and start page:** `landingPageName` in `pages.json` is Overview for an analytics
  report and the Welcome page for a validation report or a semantic model only (with
  `Welcome user` and `Your access` when the model has RLS). The Welcome page is second in
  `pageOrder`, and its page navigator height is 64 px plus 48 px per visible page.
- **Required pages:** Definition is first in `pages.json` and linked from every page;
  a Validation page exists, and a Data quality page if the report has known data quality
  issues; development pages are hidden
  (`visibility` in `page.json`) or removed.
- **Slicers:** more than 2 slicer visuals (`slicer`, `advancedSlicerVisual`, `textSlicer`,
  custom slicers) on a page. Suggest which filters can move to the filter pane and which
  visuals can filter through cross-filtering instead.
- **Filters:** visual-level filters that are not hidden in the filter pane.
- **Bookmarks:** bookmarks other than the one that shows the filter pane.
- **Tab order:** the `tabOrder` of the visuals in each page follows the reading order.
- **Broken fields:** fields that do not exist in the semantic model.

Mark layout and chart choices that need judgement as "needs human review" instead of
pass or fail.
