# Getting started with Claude Code in Group Analytics

For developers who build Fabric and Power BI solutions in a landing zone repository
(`ga_<lz_code>`): what you need, how to start, the workflow, and what is blocked. The one-page
version (the flow and what to type) is
[project-template/docs/quick-guide.md](../project-template/docs/quick-guide.md). Maintainers of
the standards read [How-To-work-with-this-repo.md](../How-To-work-with-this-repo.md).

## Prerequisites

**Installed** (check with the command):

| What | Check |
|---|---|
| VS Code with the Claude Code extension | Claude Code opens in VS Code |
| Claude Code CLI (for plugin updates) | `claude --version` |
| Git (Windows: Git for Windows, which also gives `bash` for the hooks) | `git --version`, `bash --version` |
| GitHub CLI, signed in to Vitrolife GHE | `gh auth status --hostname vitrolife-group.ghe.com` (sign in: `gh auth login --hostname vitrolife-group.ghe.com`) |
| Python 3.8 or later (for the model check) | `python --version` (macOS: `python3 --version`) |
| Power BI Desktop, with the preview features *Power BI Project (.pbip) save option*, *Store semantic model using TMDL format* and *Store reports using enhanced metadata format (PBIR)* | Options > Preview features |

**Access** (ask your manager; requests go as a ticket to servicedesk@vitrolifegroup.com with
your manager as approver):

| What | Why |
|---|---|
| Claude in the Vitrolife organization (claude.ai account) | Claude Code sign-in |
| GHE organization `group-analytics`: write on your landing zone repository, read on `ga_analytics_standards`, `ga_templates_pbi` and `skills-for-fabric` | Code, standards, template, plugins |
| Atlassian connector in claude.ai (Jira, Confluence) | Claude reads the ticket |
| SharePoint `GroupAnalytics-Infiles-*` with the lists *Analytics environments* and *Analytics Report Info* | Environment card and report info |
| Fabric workspaces `DEV_<lz_code>_*` and their SQL endpoint | Data for the model, checking the deployed items |
| The landing zone's service account (used in the Power BI service, never personally) | Refresh and connections |

## Folder layout

Keep all Group Analytics repositories side by side in one folder:

```text
Group-Analytics/
  ga_<lz_code>/              your development repository
  ga_analytics_standards/    cloned and updated automatically
  ga_templates_pbi/          cloned and updated automatically
```

## First time you open a development repository

1. Open the repository folder in VS Code, open Claude Code and trust the folder.
2. Accept the two marketplaces and install the plugins `ga-standards` and `powerbi-authoring`
   when Claude Code offers them. If it does not, run in a terminal in the repository folder:

   ```text
   claude plugin marketplace add https://vitrolife-group.ghe.com/group-analytics/ga_analytics_standards.git
   claude plugin install ga-standards@ga-collection -s project
   ```

3. Restart Claude Code when it says that `ga_analytics_standards` was cloned (VS Code: open a
   new Claude Code tab). The shared instructions load only after a restart.

## Every session

At start Claude Code shows:

- **ACTION** lines first, when something needs you: restart after an update, or the two
  commands to update the plugin. Run them as shown.
- The **Vitrolife AI rules** ([session_rules.md](../claude/session_rules.md)): in full at
  startup, as a short reminder on resume.
- **Where you are**: repository, branch, Jira ticket, uncommitted changes, plugin version.
- **The work area**, in repositories with `.claude/work_areas.conf` (landing zone repositories:
  Engineering, Data models, Reports): Claude asks which one you work on, and edits in the
  folders blocked for it are stopped (Engineering blocks `Data_models/` and `Reports/`; Data
  models and Reports block `Engineering/` and `.github/`, which belongs to Engineering). Switch
  by typing `work area: <name>`.

- **The mode**, and Claude asks once which one you want:

| Mode | What happens | When |
|---|---|---|
| *Ask before edits* | You approve every file change and command | New to the setup, or sensitive work |
| *Edit automatically* | File changes in the repository are made without asking; commands, web access and other folders still ask | You know the setup and review the result with `git diff` before you commit (git can undo) |
| *Auto*, *Bypass permissions* | Commands run without asking too | Not allowed in the pilot |

Switch in the mode menu under the prompt box (terminal: Shift+Tab); Claude cannot switch it
for you. Common read-only commands (`git status`, `git diff`, `git log`, `gh pr view` and
similar) and reading the shared repositories are pre-approved in the project settings, so there
are fewer clicks in both modes. On Windows this works only when Claude runs them with the Bash
tool (the instructions tell it to): the VS Code extension still asks for PowerShell commands
that match an allow rule (tested 2026-10-19).

Then type `/ga-standards:ga-start`, or just write, for example:

- *"Start GA-612: new semantic model for sales."*
- *"Continue GA-612 where I stopped."*
- *"I'm done with GA-612."*

## The workflow

```text
Jira ticket -> feature branch -> template + scaffold -> model, measures, report
            -> "I'm done" (ga-release-checklist) -> pull request -> merge -> publish
```

**Finishing.** Say *"I'm done"*. `ga-release-checklist` runs the review, updates
`docs/<semantic model name>.md`, goes through the checklist and drafts the pull request
description, including the steps you skip.

**Blocking and warning.** Defined once, in the header of
[standards.yaml](../pbi-governance/standards.yaml): tools never stop you; a blocking finding
must be fixed, or have a documented exception, before the pull request is merged.

## Validation along the way

| When | What runs | How |
|---|---|---|
| After every model edit by Claude | Model check on the edited file (BPA rules, naming, some standards) | Automatic; silent unless a blocking standard is broken in that file |
| Any time | Full review | `ga-model-review`, or *"run the ga-reviewer agent"* for an independent, read-only review |
| Any time | "Where am I, what is missing, what next?" and improvements for Group Analytics | *"run the ga-workflow-reviewer agent"* |
| "I'm done" | Review, documentation, checklist, pull request text | `ga-release-checklist` |

The model check needs Python 3.8+ and nothing else:
`python3 ../ga_analytics_standards/validators/validate_model.py .` (on Windows `python`).
An exception is the annotation `BestPracticeAnalyzer_IgnoreRules` on the object plus a line in
the documentation (the same annotation Tabular Editor uses).

## Which skill when

Skills are called `ga-standards:<skill>`. Claude usually picks the right one; name it to be sure.

| When you want to | Skill |
|---|---|
| Start or continue work | `ga-start` |
| Name anything (workspace, table, column, measure, query) | `ga-naming-conventions` |
| Add Calendar, time intelligence, environment, header and footer labels, metadata tables | `ga-model-scaffold` |
| Write or change measures | `ga-measure-authoring` |
| Design or review report pages | `ga-report-design` |
| Change tables, relationships, Power Query | `semantic-model-authoring` (Microsoft), on the PBIP files |
| Review a model | `ga-model-review` (or the `ga-reviewer` agent) |
| See what gold already has for your Jira ticket, and what is missing | `ga-gold-coverage` (on request) |
| Finish: review, documentation, checklist, pull request | `ga-release-checklist` |
| Change a standard, rule, snippet or skill (maintainers) | `ga-governance-maintenance` |

Code style for DAX and Power Query is in [code-style.yaml](../pbi-governance/code-style.yaml).
Environments: DEV, ACC, PRD (TEST is being retired).

## After merge

Merging to `main` is the point where the change is accepted.

**With workflows (the normal path).** The landing zone repository's GitHub Actions
(fabric-cicd, from ga_github_automation) deploy the changed `Data_models/` and `Reports/` items
to the DEV workspaces on merge (`DEV_<lz_code>_data_models` and `DEV_<lz_code>_reports`), and
promote them to ACC and PRD with each environment's parameter values. With agentic development
there is no manual publish from Power BI Desktop and no personal `_na` workspace: test in Power
BI Desktop before the merge, and let the workflow be the only writer to the workspace. After the
deploy:

1. In the Power BI service, set the data source credentials (the domain's service account,
   never a personal account) and the scheduled refresh, unless the landing zone's release
   configuration does it.
2. Add the Entra group (or the users) to the RLS roles and test with *Test as role*.
3. Give access through the app; workspace Admins, Members and Contributors are not
   restricted by RLS.
4. Check the environment card: the Analytics environments list must hold the workspace's SQL
   endpoint (`SqlEndpoint`), otherwise the environment is not detected.

The change log line in `docs/<semantic model name>.md` is part of the pull request. The publish
items of the release checklist (`gate: publish`) are confirmed at this point.

**Without workflows.** Until a landing zone repository has workflows, the developer publishes
by hand: open the PBIP from `main` in Power BI Desktop, refresh, and publish the semantic model
and the report to the DEV workspaces. Then do steps 1 to 4 above.

## Updates

| What changed | What you do |
|---|---|
| Standards, instructions or template | Nothing: a new session updates the clones. Restart when the ACTION line says so. Resumed sessions do not update. |
| Plugin version (skills, agents, hooks) | Usually nothing: the marketplaces auto-update. If an ACTION line shows two commands, run them in a terminal in the repository folder, then restart. |

## New landing zone repository

Copy everything in [project-template/](../project-template/) into the new repository, replace
the `<...>` placeholders in `README.md` and `CLAUDE.md`, and commit. Rules, skills and hooks
come from the shared repositories.

## What is blocked, and why

| Blocked | Why | Instead | Questions |
|---|---|---|---|
| Reading data files (`.abf`, `.pbix`, `.csv`, `.xlsx`, `.parquet` and similar) | They can hold business or personal data | Describe the structure, or use an anonymised sample | dataprotection@vitrolife.com |
| Power BI and Fabric MCP servers | Not approved during the pilot; they can query model data | Claude works on the PBIP files (TMDL and PBIR) | Group Analytics |
| Auto and bypass mode | Commands would run without your approval | *Ask before edits* or *Edit automatically* | Group Analytics |
| Changing `ga_analytics_standards` or `ga_templates_pbi` from a landing zone repository | Shared by every landing zone; changed through their own pull requests | Ask Group Analytics, or open an issue in that repository | Group Analytics |
| Changes outside your work area (repositories with `.claude/work_areas.conf`) | Engineering items and Power BI items are developed and reviewed separately | Type `work area: <name>` to switch; the folders and rules are in `.claude/work_areas.conf` | Group Analytics |
| Committing to `main` | Every change goes through a pull request | A feature branch per ticket | Group Analytics |
| Restricted data in prompts (patient, genetic, MAR inside information, and stricter for the pilot) | Vitrolife AI rules | See the rules shown at startup | dataprotection@vitrolife.com |
