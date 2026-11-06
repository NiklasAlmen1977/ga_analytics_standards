# BPA rules

This folder contains Tabular Editor BPA rule files.

Rule file: `BPARules-base.json`.

Do not create BPA rules for everything. Only create BPA rules for standards that can be validated safely and consistently.

Use `pbi-governance/rule-mapping.yaml` to map standards to implemented or candidate BPA rules.

`validators/validate_model.py` evaluates the same rules in Python, so the check runs without
Tabular Editor (also on macOS). Keep the two in step: a new or changed rule here needs the same
change in the script. Tabular Editor 2 runs only on Windows; it can run this file in CI later.
