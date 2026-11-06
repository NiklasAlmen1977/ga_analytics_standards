# ga_analytics_standards

The shared Group Analytics standards for Fabric and Power BI development, and the Claude Code
plugin (`ga-standards`) that applies them. Development repositories (`ga_<lz_code>`) do not copy
anything from here: they import the instructions and enable the plugin.

## Start here

| You want to | Read |
|---|---|
| Develop with Claude Code in a landing zone repository | [project-template/docs/quick-guide.md](project-template/docs/quick-guide.md), then [docs/getting-started.md](docs/getting-started.md) |
| Set up a new landing zone repository | [getting-started](docs/getting-started.md#new-landing-zone-repository) |

For maintainers:

| You want to | Read |
|---|---|
| Change a standard, rule, snippet, skill, agent or hook | [How-To-work-with-this-repo.md](How-To-work-with-this-repo.md) |
| See how the files connect, from session start onwards, incl. the hooks | [docs/setup-lineage.md](docs/setup-lineage.md) |

## What is in this repository

| Folder | Holds |
|---|---|
| `pbi-governance/` | Principles, standards, release checklist, ways of working, rule mapping, report design, code style, and the copy of the naming conventions (Confluence is the source of truth) |
| `tabular-editor/` | Best Practice Analyzer rules (`bpa/`) and C# scripts |
| `validators/` | `validate_model.py`: the model check (BPA rules, naming, standards) in Python, no installation |
| `tmdl/` | TMDL snippets for the standard model components |
| `report-design/` | The approved Vitrolife report theme |
| `claude/` | Instructions imported by every development repository, and the Vitrolife AI rules shown at session start |
| `skills/`, `agents/`, `hooks/`, `.claude-plugin/` | The `ga-standards` plugin and the `ga-collection` marketplace |
| `project-template/` | What a new development repository copies: `CLAUDE.md`, `README.md`, `.gitignore`, `.gitattributes`, `.claude/settings.json`, `.github/pull_request_template.md`, `docs/quick-guide.md` |
| `docs/` | Getting started, setup lineage, documentation template, migration guide |

## The plugin

Skills: [which skill when](docs/getting-started.md#which-skill-when). Agents, all read-only
with a fresh context: `ga-reviewer` reviews a model; `ga-workflow-reviewer` reviews the
developer's workflow and suggests improvements for Group Analytics; `ga-template-reviewer`
reviews the PBIP template and checks that the TMDL snippets and the template agree. Hooks:
[setup-lineage](docs/setup-lineage.md#ga_analytics_standards-plugin). `GA_ALLOW_DATA_FILES=1`
switches the data guard off, for maintainers' tests only.

The guards reduce risk; they are not a complete control. Rules that users must not switch
off belong in Claude Code managed settings, set by IT, and in GHE permissions (landing zone
developers have read access to the shared repositories).

## Ownership

Group Analytics owns this repository ([CODEOWNERS](.github/CODEOWNERS)). Changes go through a
pull request to `main` and a Group Analytics review.
