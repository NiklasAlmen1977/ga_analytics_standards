---
name: ga-gold-coverage
description: Show how a Jira ticket (and its epic, sub-tasks and the tickets it refers to) is covered by the gold layer of a landing zone - what is already in gold, what is partly there and what is missing - and update the Gold Ticket Coverage page. Run on request during development, not automatically. Use when the developer asks what is in gold for a ticket, what a ticket still waits for, how the tickets track against gold, or wants the coverage page refreshed.
---

# Gold coverage for a Jira ticket

Gives the developer an overview, for the ticket they work on, of what gold already has and what
is still missing, and keeps the Gold Ticket Coverage page
(https://claude.ai/artifact/11PAqZuS6SYPPzVL1tybT5) up to date. The mechanical steps are two
scripts in `../ga_analytics_standards/tools/`; only the proposal of which gold objects a ticket
needs is your judgement, and a person approves it on the page.

## Steps

1. **Scope.** Take the ticket from the branch name (or ask). Read it with the Jira connector, plus
   its epic, its sub-tasks, and the tickets its description links to. Confirm the scope with the
   developer in one line (for example "GA-540, its 15 sub-tasks and GA-506, GA-507, GA-508, GA-630").
2. **Gold catalogue.** In the landing zone repository, run
   `python ../ga_analytics_standards/tools/build_lineage_inventory.py . --out <scratchpad>/lineage_<lz>.json`.
3. **Proposal.** Write `<scratchpad>/tickets.json`: one entry per ticket with key, summary, type,
   status, statusCategory, assignee, parent, url, a one-line note, and `needs`: the gold objects
   the ticket needs, named exactly as in the catalogue (`dbo.fact_gl_pnl`). Leave `status` out and
   the script decides exists or missing; set `partial` yourself, with a note, when the object exists
   but a column or logic the ticket asks for does not (check columns against the ticket or the STT,
   never against data). Bronze, silver, report and workspace work has no gold need. A ticket
   without a description gets no needs and the note "needs input".
4. **Open questions.** Write `<scratchpad>/questions.json`: at most about eight short questions
   that block or blur the work, each with its ticket (`{"ticket": "GA-630", "question": "..."}`),
   for example a ticket whose status does not match gold, a gold need without a ticket, a decision
   someone is waiting for, a ticket without a description.
5. **Coverage.** Read the page's current tickets with ArtifactData `list` and `out_dir`, then run
   `python ../ga_analytics_standards/tools/build_gold_coverage.py --lineage <scratchpad>/lineage_<lz>.json --tickets <scratchpad>/tickets.json --out <scratchpad>/coverage --existing <out_dir>/tickets --scope "<scope>" --title "<KEY> <summary>" --description "<two sentences: what the ticket delivers and for whom>" --questions <scratchpad>/questions.json`.
   Earlier checks are kept when the needs did not change. The page shows the title and
   description as its heading, and a short summary: ready to develop, waiting for gold by
   assignee, and the open questions.
6. **Tell the developer** in plain language: what can start now, what waits for gold and on which
   ticket, gold objects no ticket asks for, and the open questions. Do not paste the whole table.
7. **Update the page** only with the developer's OK: ArtifactData `batch` with the writes from
   `<scratchpad>/coverage/batch.json`, adding `if_version` for documents that already exist.
   On the page, an editor marks each proposal as checked; that only changes the page.
8. **Never change Jira.** This skill only reads tickets. Status, assignee, comments and new
   tickets are changed by the developer in Jira; suggest them in the overview instead.

## Rules

- Metadata and ticket text only: never read lakehouse data to decide a status. The status reflects
  the gold configuration in the repository, not what is loaded.
- Names of people come from Jira (assignee) and are work data; nothing else about them goes on the
  page.
- One landing zone per page update (`gold/<lz>`); the ticket documents are shared.
