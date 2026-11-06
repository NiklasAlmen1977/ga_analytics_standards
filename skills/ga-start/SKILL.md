---
name: ga-start
description: Start a Group Analytics development session - show which repository, branch and Jira ticket the session is connected to, ask what to work on with clickable options, read the Jira ticket, create the feature branch, and hand over to the right skill. Use at the start of a session, when the user types /ga-start, or says start, new ticket, continue, or what next.
---

# Start a Group Analytics session

Get the developer from "I opened the repository" to "I am working on the right ticket, on
the right branch, with the right skill" in a few questions. Ask with the AskUserQuestion
tool when it is available, with 2-4 options and the recommended option first. Ask one
question at a time and act on the answer before you ask the next.

## 1. Show where the session is

The session start already showed the repository, branch, ticket and uncommitted changes.
Add only what it does not show: the last commit and whether the branch is behind
`origin/main` (after `git fetch`). One line, for example: "Last commit yesterday, 2 commits
behind `main`."

## 2. Ask what to do

On `main`, or on a branch without a ticket:

| Option | Then |
|---|---|
| Start a Jira ticket (recommended) | Ask for the ticket key. Read the ticket with the Atlassian connector if it is available, summarise it in 3-5 lines, propose a branch name per the instructions (for example `feature_GA-612_sales_model`), and after the user agrees: update `main` and create the branch from it. |
| Continue on an existing branch | List the local `feature_*` branches with their last commit date, and switch to the chosen one. Stop and ask first if there are uncommitted changes. |
| Look around / ask a question | Answer the question; no branch needed. |

On a feature branch:

| Option | Then |
|---|---|
| Continue this ticket (recommended) | Read the ticket, summarise the last commits and the uncommitted changes, and propose the next step. When the developer asks what is missing or what comes next, the `ga-standards:ga-workflow-reviewer` agent gives an independent answer. |
| Finish the work | `ga-release-checklist`: review, documentation, checklist and the pull request description. |
| Start another ticket | As on `main`. Stop and ask first if there are uncommitted changes. |

## 3. Ask what kind of work it is

Only when it is not clear from the ticket:

| Work | Hand over to |
|---|---|
| New semantic model or report | Copy the PBIP template from the `ga_templates_pbi` clone, add the PBIP `.gitignore` and `.gitattributes` from `project-template/` if the repository has none (ask first), then `ga-model-scaffold`, which starts with the questions "Right after copying the template" (product type, where Report info comes from, what to add). |
| Change a model: tables, relationships, Power Query | Microsoft's `semantic-model-authoring` on the PBIP files (the MCP is blocked during the pilot), with `ga-naming-conventions`. |
| Measures | `ga-measure-authoring`. |
| Report pages | `ga-report-design`. |
| Review only | `ga-model-review` (or the read-only `ga-standards:ga-reviewer` agent). |
| What is in gold for this ticket, what is missing | `ga-gold-coverage`. |
| Finish, release or documentation | `ga-release-checklist`. |
| Change a standard, rule, snippet or skill | `ga-governance-maintenance`, in `ga_analytics_standards`. |

## Rules

- Never switch branches, pull or create a branch without the user's OK, and never discard
  uncommitted changes.
- Follow the Vitrolife AI rules shown at session start: work on metadata, never on data.
- Keep it short. The goal is to start working, not to explain the setup.
