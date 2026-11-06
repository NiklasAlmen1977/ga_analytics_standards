# Group Analytics instructions for Claude

Imported by the `CLAUDE.md` of every Group Analytics development repository (see
`project-template/` in ga_analytics_standards). Applies to all Group Analytics repositories.

## When you are uncertain

Ask the developer instead of guessing: when a request can be read in more than one way, when
two options are offered ("A or B"), or when a change would affect other pages, models or
standards. Ask one short question with the options, then continue.

## Precedence (highest first)

1. Group Analytics naming conventions
   @../pbi-governance/group_analytics_naming_conventions.md
2. Group Analytics governance: `pbi-governance/*.yaml` in ga_analytics_standards
3. Fabric skills and any other external guidance

If guidance conflicts, follow the highest-ranked source. Never apply a lower-ranked
naming rule that contradicts the Group Analytics naming conventions.

## Clarifications to the naming conventions

- Plural table names: fact tables (optionally marked with `*`, e.g. `Sales*`) and
  technical tables such as `__Metrics` and `_Helpers`. Pure dimensions are singular.
- camelCase inside an otherwise snake_case name is an accepted exception for
  readability (e.g. `job_load_csvToParquet`).
- Prefixed technical fields in the semantic model keep the SQL name, in lowercase
  (e.g. `sk_customer`), and are normally hidden.
- GitHub repository names use lowercase snake_case (e.g. `ga_templates_pbi`).

## Templates

New Power BI reports and semantic models start from the approved template in the
`ga_templates_pbi` clone next to the repository
(https://vitrolife-group.ghe.com/group-analytics/ga_templates_pbi). Copy the template into
the project repository; never edit the template repository as part of project work. After
the copy, ask whether to add the PBIP `.gitignore` and the `.gitattributes` from
`project-template/` in ga_analytics_standards if the repository has none.

## Branches

Use `feature_<ticketno>_<shortdescription>`, e.g. `feature_GA-612_sales_model`. Never commit
to `main`; changes reach `main` through a pull request.

## Shell commands

Run read-only `git` and `gh` commands (status, diff, log, branch, show, fetch, `gh pr view`)
with the Bash tool, one command per call. The project settings pre-approve them for Bash; the
VS Code extension asks for every PowerShell command even when an allow rule matches, and a
combined command is only pre-approved when every part matches a rule.

Developers are not expected to read git or shell syntax. Describe every command in plain
language: what it does, whether it changes anything (files, branches, GitHub, Fabric) and
whether that can be undone; no flags or paths in the description. After a command, explain
the result in one or two plain sentences instead of repeating the raw output.

## Finishing work

When the developer says the work is done, or asks for a commit, push or pull request for a
semantic model or report, offer the `ga-release-checklist` skill. It runs the review, the
documentation and the checklist, and drafts the pull request description. Offer it again
only while the pull request description does not list the finishing steps yet.

## Plain language in answers

Write every answer to the developer in plain language, not only command descriptions. This
matters most for review findings, checklist results and summaries. For each finding say what
the user of the report would notice, how much it matters, and what to do; put the technical
detail (rule ID, file, position, z-order, DAX or M) after that, or leave it out. Explain a
technical term the first time it is needed. The pull request description is for the Group
Analytics reviewer and may keep technical detail, but its summary is in plain language.
