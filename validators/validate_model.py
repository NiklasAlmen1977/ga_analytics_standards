#!/usr/bin/env python3
"""Validate Power BI semantic models (PBIP / TMDL) against the Group Analytics standards.

Runs without installation: Python 3.8 or later, standard library only, on Windows and macOS.

What it checks:
  * the BPA rules in tabular-editor/bpa/BPARules-base.json (same IDs as in Tabular Editor),
  * naming conventions that can be checked mechanically (NC_*),
  * standards without a BPA rule that can be read from the metadata (STD_*).
Enforcement (blocking or warning) comes from pbi-governance/standards.yaml through
rule-mapping.yaml. Naming checks (NC_*) are warnings, because names can hold proper nouns.

Exceptions: the Tabular Editor annotation BestPracticeAnalyzer_IgnoreRules on the object or on
the model, for example  annotation BestPracticeAnalyzer_IgnoreRules = {"RuleIDs":["GA_TABLE_DESC_RECOMMENDED"]}
It works for every check ID in this script. Document the reason (STD_DOCUMENT_EXCEPTIONS).

Usage:
  python validate_model.py [PATH ...]      PATH = repository, PBIP folder, *.SemanticModel or its definition folder
  python validate_model.py PATH --json     machine-readable result
  python validate_model.py PATH --blocking-only
  python validate_model.py --hook          PostToolUse hook: reads the hook payload on stdin

It only reports. The exit code is always 0, so it never stops a commit, an edit or a session.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BPA_FILE = os.path.join(ROOT, "tabular-editor", "bpa", "BPARules-base.json")
STANDARDS_FILE = os.path.join(ROOT, "pbi-governance", "standards.yaml")
MAPPING_FILE = os.path.join(ROOT, "pbi-governance", "rule-mapping.yaml")

IGNORE_ANNOTATION = "BestPracticeAnalyzer_IgnoreRules"

# Checks that are not BPA rules. Enforcement of STD_* checks is read from standards.yaml.
EXTRA_CHECKS = {
    "NC_TABLE_TITLE_CASE": "Table names use Title Case, without underscores (naming conventions)",
    "NC_FIELD_SENTENCE_CASE": "Visible columns and measures use Sentence case, without underscores or camelCase (naming conventions)",
    "NC_SK_COLUMN_LOWERCASE": "Surrogate key columns keep the SQL name in lowercase, e.g. sk_customer (naming conventions)",
    "NC_DAX_VARIABLE_PREFIX": "DAX variables start with _v_ (naming conventions)",
    "NC_DISPLAY_FOLDER_SUBFOLDER_PREFIX": "Every display folder level starts with a dot, e.g. .Base\\.Time intelligence (naming conventions)",
    "NC_NO_TEMPORARY_MEASURES": "Temporary _tmp_ measures are for development only and are removed before publishing (naming conventions)",
    "STD_EXPLICIT_MEASURES_REQUIRED": "The model discourages implicit measures (discourageImplicitMeasures)",
    "STD_PQ_QUERY_GROUPS_AND_PREFIXES": "Power Query queries sit in the template query groups with the matching prefix",
    "STD_SINGLE_DATE_DIMENSION": "One Calendar table serves all date roles",
}

# Words that stay lowercase inside a Title Case table name.
TITLE_SMALL_WORDS = {"a", "an", "and", "as", "at", "by", "for", "from", "in", "of", "on", "or", "per", "the", "to", "vs", "with"}
# Power Query group number -> required prefix.
PQ_GROUP_PREFIX = {"1": "p_", "2": "fn_", "3": "src_", "4": "stg_"}
OBJECT_KEYWORDS = {
    "model", "table", "column", "measure", "partition", "hierarchy", "level", "calculationGroup",
    "calculationItem", "relationship", "role", "tablePermission", "expression", "queryGroup",
    "perspective", "culture", "cultureInfo", "dataSource", "function", "annotation",
    "extendedProperty", "changedProperty", "variation", "formatStringDefinition",
    "detailRowsDefinition", "member", "database", "calendar", "linguisticMetadata",
}


# ---------------------------------------------------------------- TMDL parsing

class Node:
    def __init__(self, kind, name, indent, parent, desc):
        self.kind, self.name, self.indent, self.parent = kind, name, indent, parent
        self.desc = desc
        self.props = {}
        self.expr = ""
        self.children = []
        self.file = ""

    def child_list(self, kind):
        return [c for c in self.children if c.kind == kind]

    def annotation(self, name):
        for c in self.children:
            if c.kind == "annotation" and c.name == name:
                return c.expr
        return None


def _indent(line):
    return len(line) - len(line.lstrip("\t"))


def _parse_name(rest):
    """Split 'Name = expr' or "'Quoted ''name''' = expr" into (name, expr or None)."""
    rest = rest.strip()
    if rest.startswith("'"):
        i, name = 1, ""
        while i < len(rest):
            if rest[i] == "'":
                if i + 1 < len(rest) and rest[i + 1] == "'":
                    name += "'"
                    i += 2
                    continue
                break
            name += rest[i]
            i += 1
        tail = rest[i + 1:].strip()
    else:
        m = re.match(r"([^=]*?)\s*(=.*)?$", rest)
        name, tail = m.group(1).strip(), (m.group(2) or "").strip()
    expr = tail[1:].strip() if tail.startswith("=") else None
    return name, expr


def _read_expression(lines, i, base_indent, first):
    """Read a multi-line expression that starts after '=' on line i-1. Returns (text, next i)."""
    if first.startswith("```"):
        body = []
        while i < len(lines) and lines[i].strip() != "```":
            body.append(lines[i].strip("\r\n"))
            i += 1
        return "\n".join(body), i + 1
    if first:
        return first, i
    body = []
    while i < len(lines):
        line = lines[i].rstrip("\r\n")
        if line.strip() and _indent(line) < base_indent + 2:
            break
        body.append(line)
        i += 1
    return "\n".join(body).strip(), i


def parse_tmdl_file(path, root):
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()
    stack, desc, i = [root], [], 0
    while i < len(lines):
        raw = lines[i].rstrip("\r\n")
        i += 1
        stripped = raw.strip()
        if not stripped:
            continue
        ind = _indent(raw)
        if stripped.startswith("///"):
            desc.append(stripped[3:].strip())
            continue
        word = stripped.split(None, 1)[0]
        if word == "ref":
            desc = []
            continue
        if word in OBJECT_KEYWORDS and (len(stripped.split(None, 1)) > 1 or word in ("model", "database")):
            while len(stack) > 1 and stack[-1].indent >= ind:
                stack.pop()
            rest = stripped.split(None, 1)[1] if " " in stripped else ""
            name, expr = _parse_name(rest)
            node = Node(word, name, ind, stack[-1], " ".join(desc))
            node.file = path
            desc = []
            if expr is not None:
                node.expr, i = _read_expression(lines, i, ind, expr)
            stack[-1].children.append(node)
            stack.append(node)
            continue
        desc = []
        while len(stack) > 1 and stack[-1].indent >= ind:
            stack.pop()
        m = re.match(r"([A-Za-z]+)\s*(:|=)\s*(.*)$", stripped)
        if m:
            key, sep, value = m.group(1), m.group(2), m.group(3)
            if sep == "=":
                value, i = _read_expression(lines, i, ind, value)
            stack[-1].props[key] = value.strip()
        else:
            stack[-1].props[stripped] = True


class Model:
    def __init__(self, definition_dir):
        self.dir = definition_dir
        self.name = os.path.basename(os.path.dirname(definition_dir)).replace(".SemanticModel", "")
        self.root = Node("root", "", -1, None, "")
        for base, _, files in os.walk(definition_dir):
            for fn in sorted(files):
                if fn.endswith(".tmdl"):
                    parse_tmdl_file(os.path.join(base, fn), self.root)
        models = self.root.child_list("model")
        self.model = models[0] if models else Node("model", "Model", 0, None, "")
        # In model.tmdl the model's annotations sit at the root level, next to "model Model".
        self.model.children += [n for n in self.root.child_list("annotation") if n.file.endswith("model.tmdl")]
        self.tables = self.root.child_list("table")
        self.relationships = self.root.child_list("relationship")
        self.expressions = self.root.child_list("expression")
        self.roles = self.root.child_list("role")

    def columns(self):
        for t in self.tables:
            for c in t.child_list("column"):
                yield t, c

    def measures(self):
        for t in self.tables:
            for m in t.child_list("measure"):
                yield t, m

    def calculation_items(self):
        for t in self.tables:
            for g in t.child_list("calculationGroup"):
                for item in g.child_list("calculationItem"):
                    yield t, item

    def dax_texts(self):
        """All model DAX that can reference columns, without the third-party UDF library."""
        for _, m in self.measures():
            yield m.expr
            for fs in m.child_list("formatStringDefinition"):
                yield fs.expr
        for _, c in self.columns():
            if c.expr:
                yield c.expr
        for _, item in self.calculation_items():
            yield item.expr
        for t in self.tables:
            for p in t.child_list("partition"):
                if p.expr.strip().lower() == "calculated":
                    yield str(p.props.get("source", ""))
        for r in self.roles:
            for tp in r.child_list("tablePermission"):
                yield tp.expr


# ---------------------------------------------------------------- governance files

def load_bpa_rules():
    with open(BPA_FILE, encoding="utf-8-sig") as f:
        return {r["ID"]: r for r in json.load(f)}


def _yaml_blocks(path, key):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    for m in re.finditer(r"-\s+%s:\s*\"?([^\"\n]+)\"?(.*?)(?=\n\s*-\s+\w+:|\Z)" % key, text, re.S):
        fields = dict(re.findall(r"\n\s+(\w+):\s*\"?([^\"\n]*)\"?", m.group(2)))
        yield m.group(1).strip(), fields


def load_enforcement(bpa_rules):
    """Map every check ID to (enforcement, standard ID)."""
    standards = {sid: f.get("enforcement", "warning") for sid, f in _yaml_blocks(STANDARDS_FILE, "id")}
    result = {}
    for sid, f in _yaml_blocks(MAPPING_FILE, "standard_id"):
        rule = f.get("bpa_rule_id", "null")
        if rule and rule != "null":
            result[rule] = (standards.get(sid, "warning"), sid)
    for rid, rule in bpa_rules.items():
        result.setdefault(rid, ("blocking" if rule.get("Severity", 2) >= 3 else "warning", None))
    for cid in EXTRA_CHECKS:
        if cid.startswith("STD_"):
            result[cid] = (standards.get(cid, "warning"), cid)
        else:
            result[cid] = ("warning", None)
    return result


# ---------------------------------------------------------------- checks

def is_hidden(node):
    return node.props.get("isHidden") is True


def obj_label(table, obj=None):
    if obj is None:
        return "'%s'" % table.name
    if obj.kind == "measure":
        return "'%s'[%s] (measure)" % (table.name, obj.name)
    return "'%s'[%s]" % (table.name, obj.name)


def check_bpa_rules(model):
    """Python versions of the rules in BPARules-base.json. Yields (rule ID, node, label, detail)."""
    for t in model.tables:
        if not is_hidden(t) and not t.desc:
            yield "GA_TABLE_DESC_RECOMMENDED", t, obj_label(t), ""
        if t.name.lower().startswith("fact"):
            yield "GA_FACT_TABLE_NO_FACT_PREFIX", t, obj_label(t), ""
        if t.name.lower().startswith("dim"):
            yield "GA_DIM_TABLE_NO_DIM_PREFIX", t, obj_label(t), ""
        if t.name.startswith(("DateTableTemplate_", "LocalDateTable_")):
            yield "GA_MODEL_NO_AUTO_DATE_TABLES", t, obj_label(t), ""
        for obj in [t] + t.child_list("column") + t.child_list("measure") + t.child_list("hierarchy"):
            if obj.name != obj.name.strip():
                yield "GA_OBJECT_NAME_NO_LEADING_TRAILING_SPACES", obj, obj_label(t, None if obj is t else obj), ""

    for t, m in model.measures():
        if not is_hidden(m) and not m.desc:
            yield "GA_MEASURE_DESC_REQUIRED", m, obj_label(t, m), ""
        folder = str(m.props.get("displayFolder", "")).strip()
        if not folder:
            yield "GA_MEASURE_DISPLAY_FOLDER_REQUIRED", m, obj_label(t, m), ""
        elif not folder.startswith("."):
            yield "GA_MEASURE_DISPLAY_FOLDER_PREFIX", m, obj_label(t, m), "folder " + folder

    referenced = _referenced_columns(model)
    for t, c in model.columns():
        name = c.name
        summarize = str(c.props.get("summarizeBy", "default")).lower()
        if (name.endswith("Key") or name.endswith("ID")) and summarize != "none":
            yield "GA_KEY_COLUMNS_NO_SUMMARIZE", c, obj_label(t, c), "summarizeBy " + summarize
        low = name.lower()
        if ("key" in low or low.startswith("pq_sk_") or low.startswith("sk_")) and not is_hidden(c) and not is_hidden(t):
            yield "GA_TECHNICAL_COLUMNS_SHOULD_BE_HIDDEN", c, obj_label(t, c), ""
        if str(c.props.get("dataType", "")).lower() == "double":
            yield "GA_COLUMN_NO_FLOATING_POINT", c, obj_label(t, c), ""
        if is_hidden(c) and (t.name.lower(), name.lower()) not in referenced and name.lower() not in referenced:
            yield "GA_HIDDEN_UNUSED_COLUMNS_REVIEW", c, obj_label(t, c), "not used in the model (check the report before removing)"

    for r in model.relationships:
        label = "relationship %s -> %s" % (r.props.get("fromColumn", "?"), r.props.get("toColumn", "?"))
        if str(r.props.get("crossFilteringBehavior", "")).lower() == "bothdirections":
            yield "GA_RELATIONSHIP_SINGLE_DIRECTION", r, label, ""
        if (str(r.props.get("fromCardinality", "many")).lower() == "many"
                and str(r.props.get("toCardinality", "one")).lower() == "many"):
            yield "GA_RELATIONSHIP_NO_MANY_TO_MANY", r, label, ""

    # Fact tables: on the many side of a relationship and never on the one side
    many_side, one_side = set(), set()
    for r in model.relationships:
        from_pair = _split_column_ref(str(r.props.get("fromColumn", "")))
        to_pair = _split_column_ref(str(r.props.get("toColumn", "")))
        if from_pair:
            many_side.add(from_pair[0])
        if to_pair:
            one_side.add(to_pair[0])
    for t in model.tables:
        low = t.name.lower()
        if low in many_side and low not in one_side and not t.name.startswith("_") and not t.name.endswith("*"):
            yield "GA_FACT_TABLE_ASTERISK_SUFFIX", t, obj_label(t), "fact table (many side only) without * at the end"

    marked = any(
        str(t.props.get("dataCategory", "")).lower() == "time"
        and any(c.props.get("isKey") is True and str(c.props.get("dataType", "")).lower() == "datetime"
                for c in t.child_list("column"))
        for t in model.tables)
    if not marked:
        yield "GA_MODEL_DATE_TABLE_MARKED", model.model, "model", "no table with dataCategory Time and a dateTime key column"


def _split_column_ref(ref):
    """'Table'.'Column' or Table.Column -> (table, column), lowercase."""
    m = re.match(r"\s*('(?:[^']|'')*'|[^.]+)\.('(?:[^']|'')*'|.+?)\s*$", ref)
    if not m:
        return None
    unq = lambda s: s.strip().strip("'").replace("''", "'").lower()
    return unq(m.group(1)), unq(m.group(2))


def _referenced_columns(model):
    """Columns used by relationships, sort by, hierarchies, variations or DAX. Lenient by design:
    an unqualified [Column] in DAX counts for every table, so the review rule does not over-report."""
    refs = set()
    for r in model.relationships:
        for key in ("fromColumn", "toColumn"):
            pair = _split_column_ref(str(r.props.get(key, "")))
            if pair:
                refs.add(pair)
    for t in model.tables:
        for c in t.child_list("column"):
            if "sortByColumn" in c.props:
                refs.add((t.name.lower(), str(c.props["sortByColumn"]).strip("'").lower()))
            for v in c.child_list("variation"):
                refs.add((t.name.lower(), c.name.lower()))
        for h in t.child_list("hierarchy"):
            for lvl in h.child_list("level"):
                col = str(lvl.props.get("column", "")).strip("'")
                refs.add((t.name.lower(), col.lower()))
    for text in model.dax_texts():
        for col in re.findall(r"\[([^\]]+)\]", text or ""):
            refs.add(col.lower())
    return refs


def _is_title_case(name):
    core = name.lstrip("_").rstrip("*").strip()
    if not core or "_" in core:
        return False
    for idx, word in enumerate(core.split()):
        first = word[0]
        if not first.isalpha():
            continue
        if first.islower() and not (idx > 0 and word in TITLE_SMALL_WORDS):
            return False
    return True


def _sentence_case_problem(name):
    if "_" in name:
        return "underscore"
    # Comparison measures (<Measure> vs <Measure>, e.g. Actuals vs Budget): each side is a
    # measure name in Sentence case and keeps its own first capital.
    parts = re.split(r"\s+vs\s+", name)
    if len(parts) > 1:
        for part in parts:
            problem = _sentence_case_part_problem(part)
            if problem:
                return problem + " (in a comparison, each measure name keeps its first capital)"
        return None
    return _sentence_case_part_problem(name)


def _sentence_case_part_problem(name):
    words = name.split()
    for idx, word in enumerate(words):
        letters = re.sub(r"[^A-Za-z]", "", word)
        if letters[:1].islower() and re.search(r"[a-z][A-Z]", letters):
            return "camelCase in '%s'" % word
        if idx > 0 and len(letters) > 1 and letters[0].isupper() and letters[1:].islower():
            return "capital in '%s' (fine if it is a proper noun)" % word
    if words and words[0][0].isalpha() and words[0][0].islower():
        return "starts with a lowercase letter"
    return None


def check_naming(model):
    for t in model.tables:
        if not _is_title_case(t.name):
            yield "NC_TABLE_TITLE_CASE", t, obj_label(t), ""
    for t, c in model.columns():
        if c.name.lower().startswith("sk_") and c.name != c.name.lower():
            yield "NC_SK_COLUMN_LOWERCASE", c, obj_label(t, c), ""
        if is_hidden(c) or is_hidden(t) or c.name.lower().startswith("sk_"):
            continue
        problem = _sentence_case_problem(c.name)
        if problem:
            yield "NC_FIELD_SENTENCE_CASE", c, obj_label(t, c), problem
    for t, m in model.measures():
        if m.name.startswith("_tmp_"):
            yield "NC_NO_TEMPORARY_MEASURES", m, obj_label(t, m), ""
        if not (is_hidden(m) or m.name.startswith(("_", "Label -"))):
            problem = _sentence_case_problem(m.name)
            if problem:
                yield "NC_FIELD_SENTENCE_CASE", m, obj_label(t, m), problem
        folder = str(m.props.get("displayFolder", "")).strip()
        if folder.startswith(".") and any(not part.startswith(".") for part in re.split(r"[\\/]", folder) if part):
            yield "NC_DISPLAY_FOLDER_SUBFOLDER_PREFIX", m, obj_label(t, m), "folder " + folder
    dax_objects = [(t, m) for t, m in model.measures()]
    dax_objects += [(t, c) for t, c in model.columns() if c.expr]
    dax_objects += list(model.calculation_items())
    for t, obj in dax_objects:
        bad = sorted({v for v in re.findall(r"(?i)\bVAR\s+([A-Za-z_][A-Za-z0-9_.]*)", obj.expr or "")
                      if not v.startswith("_v_")})
        if bad:
            yield "NC_DAX_VARIABLE_PREFIX", obj, obj_label(t, obj), ", ".join(bad)


def check_standards(model):
    if model.model.props.get("discourageImplicitMeasures") is not True:
        yield "STD_EXPLICIT_MEASURES_REQUIRED", model.model, "model", "discourageImplicitMeasures is not set in model.tmdl"

    time_tables = [t.name for t in model.tables if str(t.props.get("dataCategory", "")).lower() == "time"]
    if len(time_tables) > 1:
        yield "STD_SINGLE_DATE_DIMENSION", model.model, "model", "date tables: " + ", ".join(time_tables)

    for e in model.expressions:
        group = str(e.props.get("queryGroup", "")).strip("'")
        label = "query %s" % e.name
        if not group:
            yield "STD_PQ_QUERY_GROUPS_AND_PREFIXES", e, label, "no query group"
            continue
        number = group.split(".", 1)[0].strip()
        prefix = PQ_GROUP_PREFIX.get(number)
        if prefix and not e.name.startswith(prefix):
            yield "STD_PQ_QUERY_GROUPS_AND_PREFIXES", e, label, "in '%s', expected prefix %s" % (group, prefix)
        if re.search(r"IsParameterQuery\s*=\s*true", e.expr or "", re.I) and not e.name.startswith("p_"):
            yield "STD_PQ_QUERY_GROUPS_AND_PREFIXES", e, label, "parameter without p_ prefix"
    for t in model.tables:
        for p in t.child_list("partition"):
            if p.expr.strip().lower() != "m":
                continue
            group = str(p.props.get("queryGroup", "")).strip("'")
            if not group.startswith("5."):
                yield "STD_PQ_QUERY_GROUPS_AND_PREFIXES", t, obj_label(t), "loaded table not in '5. Load to Data Model' (%s)" % (group or "no group")
            if t.name.lower().startswith(("src_", "stg_", "p_", "fn_")):
                yield "STD_PQ_QUERY_GROUPS_AND_PREFIXES", t, obj_label(t), "loaded table with a query prefix"


# ---------------------------------------------------------------- running

def _ignored_rules(node):
    value = node.annotation(IGNORE_ANNOTATION) if node is not None else None
    if not value:
        return set()
    try:
        return set(json.loads(value).get("RuleIDs", []))
    except (ValueError, AttributeError):
        return set(re.findall(r"[A-Z][A-Z0-9_]+", value))


def validate(model, bpa_rules, enforcement):
    model_ignored = _ignored_rules(model.model)
    findings, ignored = [], 0
    for check in (check_bpa_rules, check_naming, check_standards):
        for rule_id, node, label, detail in check(model):
            if rule_id in model_ignored or rule_id in _ignored_rules(node):
                ignored += 1
                continue
            level, standard = enforcement.get(rule_id, ("warning", None))
            title = bpa_rules[rule_id]["Name"] if rule_id in bpa_rules else EXTRA_CHECKS.get(rule_id, rule_id)
            findings.append({
                "rule": rule_id, "standard": standard, "enforcement": level, "title": title,
                "object": label, "detail": detail,
                "file": os.path.relpath(node.file, model.dir) if node.file else "",
            })
    implemented = {
        "GA_MEASURE_DESC_REQUIRED", "GA_TABLE_DESC_RECOMMENDED", "GA_MEASURE_DISPLAY_FOLDER_REQUIRED",
        "GA_MEASURE_DISPLAY_FOLDER_PREFIX", "GA_KEY_COLUMNS_NO_SUMMARIZE", "GA_TECHNICAL_COLUMNS_SHOULD_BE_HIDDEN",
        "GA_FACT_TABLE_NO_FACT_PREFIX", "GA_DIM_TABLE_NO_DIM_PREFIX", "GA_HIDDEN_UNUSED_COLUMNS_REVIEW",
        "GA_OBJECT_NAME_NO_LEADING_TRAILING_SPACES", "GA_RELATIONSHIP_SINGLE_DIRECTION",
        "GA_RELATIONSHIP_NO_MANY_TO_MANY", "GA_MODEL_DATE_TABLE_MARKED", "GA_MODEL_NO_AUTO_DATE_TABLES",
        "GA_COLUMN_NO_FLOATING_POINT", "GA_FACT_TABLE_ASTERISK_SUFFIX",
    }
    return {
        "model": model.name,
        "path": model.dir,
        "blocking": sum(1 for f in findings if f["enforcement"] == "blocking"),
        "warnings": sum(1 for f in findings if f["enforcement"] != "blocking"),
        "ignored": ignored,
        "not_evaluated": sorted(set(bpa_rules) - implemented),
        "findings": findings,
    }


def find_models(paths):
    found = []
    for path in paths:
        path = os.path.abspath(path)
        if os.path.basename(path) == "definition" and os.path.isdir(path):
            found.append(path)
            continue
        if path.endswith(".SemanticModel") and os.path.isdir(os.path.join(path, "definition")):
            found.append(os.path.join(path, "definition"))
            continue
        for base, dirs, _ in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
            if base.endswith(".SemanticModel") and "definition" in dirs:
                found.append(os.path.join(base, "definition"))
                dirs[:] = []
    return sorted(set(found))


def model_of_file(file_path):
    """The definition folder of the semantic model a .tmdl file belongs to, or None."""
    parts = os.path.abspath(file_path).replace("\\", "/").split("/")
    for idx in range(len(parts) - 1, 0, -1):
        if parts[idx] == "definition" and parts[idx - 1].endswith(".SemanticModel"):
            return "/".join(parts[:idx + 1])
    return None


def format_report(result, blocking_only=False, limit=15):
    out = ["Model: %s" % result["model"],
           "Blocking: %d, warnings: %d, ignored by annotation: %d"
           % (result["blocking"], result["warnings"], result["ignored"])]
    for level, heading in (("blocking", "BLOCKING STANDARDS (fix or document an exception before merge)"),
                           ("warning", "WARNING STANDARDS")):
        if blocking_only and level != "blocking":
            continue
        items = [f for f in result["findings"] if (f["enforcement"] == "blocking") == (level == "blocking")]
        if not items:
            continue
        out.append("")
        out.append(heading)
        by_rule = {}
        for f in items:
            by_rule.setdefault(f["rule"], []).append(f)
        for rule, group in by_rule.items():
            std = " / " + group[0]["standard"] if group[0]["standard"] and group[0]["standard"] != rule else ""
            out.append("  %s%s (%d): %s" % (rule, std, len(group), group[0]["title"]))
            for f in group[:limit]:
                out.append("    - %s%s" % (f["object"], " - " + f["detail"] if f["detail"] else ""))
            if len(group) > limit:
                out.append("    - ... and %d more" % (len(group) - limit))
    if result["not_evaluated"] and not blocking_only:
        out.append("")
        out.append("Not evaluated (no Python check yet): " + ", ".join(result["not_evaluated"]))
    return "\n".join(out)


def run_hook(bpa_rules, enforcement):
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        return 0
    file_path = (payload.get("tool_input") or {}).get("file_path", "")
    if not file_path.endswith(".tmdl"):
        return 0
    definition = model_of_file(file_path)
    if not definition or not os.path.isdir(definition):
        return 0
    try:
        result = validate(Model(definition), bpa_rules, enforcement)
    except Exception as exc:  # never break the session because of the validator
        print("validate_model.py could not read %s: %s" % (definition, exc), file=sys.stderr)
        return 0
    # Only findings in the edited file, so a model with known, documented deviations does not
    # repeat them after every edit.
    edited = os.path.normcase(os.path.relpath(os.path.abspath(file_path), definition))
    result["findings"] = [f for f in result["findings"] if os.path.normcase(f["file"]) == edited]
    result["blocking"] = sum(1 for f in result["findings"] if f["enforcement"] == "blocking")
    result["warnings"] = len(result["findings"]) - result["blocking"]
    if result["blocking"] == 0:
        return 0
    text = ("Group Analytics model check of the edited file (a warning, nothing is blocked): %d finding(s) on "
            "standards that are blocking for merge. Unless the project documents them as exceptions, propose "
            "a concrete fix or a documented exception (annotation %s plus a line under exceptions in the data "
            "product documentation), and ask before changing anything.\n"
            % (result["blocking"], IGNORE_ANNOTATION))
    text += format_report(result, blocking_only=True)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": text}}))
    return 0


def main():
    parser = argparse.ArgumentParser(description="Validate Power BI semantic models against the Group Analytics standards.")
    parser.add_argument("paths", nargs="*", default=["."], help="repository, PBIP folder, *.SemanticModel or definition folder")
    parser.add_argument("--json", action="store_true", help="print the result as JSON")
    parser.add_argument("--blocking-only", action="store_true", help="show only blocking findings")
    parser.add_argument("--hook", action="store_true", help="run as a Claude Code PostToolUse hook")
    args = parser.parse_args()

    bpa_rules = load_bpa_rules()
    enforcement = load_enforcement(bpa_rules)
    if args.hook:
        return run_hook(bpa_rules, enforcement)

    models = find_models(args.paths)
    if not models:
        print("No semantic model (*.SemanticModel/definition) found in: " + ", ".join(args.paths))
        return 0
    results = [validate(Model(d), bpa_rules, enforcement) for d in models]
    if args.json:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2, ensure_ascii=False))
    else:
        print("\n\n".join(format_report(r, args.blocking_only) for r in results))
    return 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
