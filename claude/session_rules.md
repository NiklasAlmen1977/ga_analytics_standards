Vitrolife AI rules (VIT-AID) for Claude - Group Analytics pilot

Never paste, upload or let Claude read:
- Patient or embryo data (names, embryo or cycle IDs, outcomes, medical history).
- Genetic data (sequencing, PGT, mutation reports).
- MAR inside information: non-public, price-sensitive information about Vitrolife Group or its share.
- Stricter for the GA pilot: employee personal data (salaries, performance, HR matters) and confidential business data (M&A, board material, unreleased financials, audit findings). Business contact data (name, work email, job title) is allowed.
Internal strategy, pricing, roadmaps and partner negotiations only in anonymised or generalised form (stricter for the GA pilot).
Use anonymised or fictional examples. A combination of IDs, clinic codes and dates can still identify a person.
In doubt, do not paste it and ask Data Protection: dataprotection@vitrolife.com

Everything Claude produces is a draft that you own and review. Clinical, regulatory, quality (QMS), legal, financial and HR output must be validated by a qualified person and follow the normal review and approval process.
Say that AI was used when it contributed significantly to a deliverable for external parties.
Do not copy or lightly reword copyrighted external content.

Pilot rules (until Group Analytics ends the pilot):
- You choose the mode at the start of each session: Ask before edits (approve every change) or Edit automatically (file changes in the repository without asking; commands still ask; review with git diff before you commit). Auto mode and bypass mode are off.
- Data files (.abf, .pbix, .csv, .xlsx, .parquet and similar) and the Power BI and Fabric MCP servers are blocked. Claude works on the PBIP files (metadata) only.
- Everything that is blocked, and what to do instead: docs/getting-started.md in ga_analytics_standards, "What is blocked".
