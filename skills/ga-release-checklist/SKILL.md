---
name: ga-release-checklist
description: Finish Group Analytics work on a semantic model or report - run or reuse the model review, update the data product documentation, go through the release checklist and draft the pull request description with skipped steps and exceptions. The one entry point when the developer says the work is done, asks for a commit, push or pull request, or asks if a model is ready for release or publishing.
---

# Finish the work: review, documentation, checklist, pull request

This is the one finishing step. It ends with a pull request description the developer can
use as it is. Check automatically what can be read from the files or git, and ask about the
rest. Never mark a manual item as passed on the developer's behalf.

## Source files

Paths are relative to the plugin root, `${CLAUDE_PLUGIN_ROOT}`. Read them at the start;
items and IDs change.

| File | Use |
|---|---|
| `pbi-governance/release-checklist.yaml` | The checklist items (`CHK_*`) with `enforcement`, `gate` and `standard_refs`. |
| `pbi-governance/ways-of-working.yaml` | Branch, pull request, quality gate and publishing rules. |
| `pbi-governance/standards.yaml` | The standards the items refer to; the header defines blocking and warning. |

## Steps

Ask once, with clickable options, which steps to run (all are recommended). Skipped steps
go into the pull request description.

1. **Review.** Run the `ga-model-review` skill, or reuse a review from this session if the
   model has not changed since. Offer the read-only `ga-standards:ga-reviewer` agent when the
   developer wants an independent review.
   **Then go through the findings with the developer.** List every blocking finding and
   warning with a proposed fix, in plain language (what the user would notice, how much it
   matters, the fix). Ask with clickable options (multi-select, grouped by area) which fixes
   to apply; the rest becomes a documented exception or an open warning. Apply the chosen
   fixes and run the model check again. Things only the developer can do (Power BI Desktop,
   a person's confirmation) are listed separately, not offered as fixes.
2. **Documentation.** Run the `ga-data-product-documentation` skill to write or update
   `docs/<semantic model name>.md`, including the review result and the exceptions.
   **Platform lineage:** when the pull request changes `Engineering/`, `Data_models/` or
   `Reports/` of a landing zone repository, run
   `python ../ga_analytics_standards/tools/build_lineage_inventory.py . --out <scratchpad>/lineage_<lz_code>.json`
   and, with the developer's OK, replace the document `zones/<lz_code>` of the GA Platform
   Lineage page (https://claude.ai/artifact/2pAdcZ9WGAh8jP1rRZMcQQ) with it (ArtifactData
   `set` with `file_path`, pinned to the version you read). Mention new objects that nothing
   uses in the pull request.
3. **Checklist.** Evaluate the items with `gate: pr` now. Items with `gate: publish`
   (service account, domain workspace, app) are confirmed when publishing; list them as
   "At publish".
   - Model, DAX, usability: map the review findings through `standard_refs`.
   - Power Query and report: read the model and PBIR (`ga-report-design` for pages). For
     `CHK_REPORT_LAYOUT`, check every table and matrix: all columns visible, with column
     widths that fit the visual and word wrap on. For `CHK_REPORT_LANDING_AND_START_PAGE`,
     ask what the product is (clickable options: analytics report, validation report,
     semantic model only) when it is not clear from the files. For a semantic model only,
     the Welcome page is required and is the landing page; with RLS it must show the
     signed-in user and what they can see (`Your access` pointed at the RLS dimension, not the
     template placeholder). Without RLS, still recommend the Welcome page.
   - Semantic model and report in one PBIP: depending on how mature the product is, it may
     be time to split them. Ask when a project has a report with real analysis pages next to
     its model. Example: if Aaro endpoint (sm) became a normal report, the semantic model
     "Aaro endpoint (sm)" stays in `Data_models/`, and a thin report "Aaro endpoint" in
     `Reports/` connects to it (live connection). Mention it as a suggestion in the pull
     request; it is not a checklist failure.
   - Version control: branch name per the instructions, changes committed and pushed.
   - Documentation and validation: look for evidence, then ask. Business and technical
     validation are always confirmed by a person.
4. **Pull request.** Draft the description from the project's
   `.github/pull_request_template.md` (if there is none: ticket, what changed, finishing
   steps run or skipped, exceptions, open warnings, business validation by). The pull
   request reviewer must get the review result as the developer approved it: start with a
   short plain-language summary, then the result of each finishing step (model check counts,
   review findings fixed and left, checklist verdict), the decisions the reviewer has to make,
   and every open warning with its reason. Show the description to the developer before it is
   used. Commit, push and open or update the pull request with `gh` only when the developer
   agrees.

## Report format

| Area | Item | Enforcement | Status | Evidence / action |
|---|---|---|---|---|
| model | `CHK_MODEL_TECHNICAL_COLUMNS_HIDDEN` | blocking | Fail | 3 visible `sk_` columns, see review |
| validation | `CHK_VALIDATION_BUSINESS` | blocking | Needs confirmation | Ask the business owner |
| platform | `CHK_PLATFORM_SERVICE_ACCOUNTS` | blocking | At publish | Confirm when publishing |

Status: Pass, Fail, Exception (documented), Needs confirmation, At publish, Not applicable
(with a reason).

Verdict for the pull request (`gate: pr` items only):

- **Ready**: every blocking item passes, has a documented exception, or is not applicable.
- **Ready with warnings**: as Ready, but some warning items fail; list them in the pull
  request description.
- **Not ready**: list the blocking items that fail or are unconfirmed, most important first.
  Nothing is blocked by a tool: the reviewer decides on the pull request.

After the merge, the "After merge" section of `docs/getting-started.md` says how to publish.
