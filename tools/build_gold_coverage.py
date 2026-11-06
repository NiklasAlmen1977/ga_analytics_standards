"""Build the Gold Ticket Coverage documents for one landing zone: which Jira tickets gold
already covers, partly covers or still misses.

Run on request during development (not automated), through the ga-gold-coverage skill:
Claude reads the tickets with the Jira connector and writes tickets.json with a proposal of the
gold objects each ticket needs; this script checks the proposals against the gold catalogue from
build_lineage_inventory.py, sets the verdicts, keeps earlier approvals where nothing changed, and
writes one JSON file per page document plus batch.json for ArtifactData.

tickets.json: a list of
  {"key", "summary", "type", "status", "statusCategory", "assignee", "parent", "url", "note",
   "needs": [{"object": "dbo.fact_gl_pnl", "status": optional, "note": optional}]}
A need without a status gets one: "exists" when the object is in the gold catalogue, "missing" when
it looks like a gold object (schema.table, dim_, fact_) but is not there, otherwise "not-gold".
Give "partial" yourself when the object exists but a column or logic the ticket asks for does not.

Usage: python build_gold_coverage.py --lineage lineage_<lz>.json --tickets tickets.json
       --out <folder> [--existing <folder with tickets/<key>.json from ArtifactData list out_dir>]
       [--scope "text"] [--title "GA-540 Cost report"] [--description "what it is about"]
       [--questions questions.json]

questions.json: a list of {"ticket": "GA-630", "question": "Who adds sk_local_currency, and when?"}:
the open questions shown in the page's summary. The page itself computes "ready to develop"
and "waiting for gold, by assignee" from the tickets.
"""
import argparse
import datetime
import json
import pathlib
import re
import sys

E, P, M, N = "exists", "partial", "missing", "not-gold"
VALID = {E, P, M, N}


def gold_index(lineage):
    names = {}
    for o in lineage.get("objects", []):
        if o.get("layer") == "gold":
            names[o["name"].lower()] = o["name"]
            names[o["name"].split(".")[-1].lower()] = o["name"]
    return names


def looks_gold(obj):
    return bool(re.match(r"^[a-z_]+\.(dim|fact|agg|bridge)_", obj, re.I) or re.match(r"^(dim|fact)_", obj, re.I))


def resolve(need, gold):
    obj = need.get("object", "").strip()
    status = need.get("status")
    if status and status not in VALID:
        sys.exit(f"Unknown status {status!r} for {obj!r}; use one of {sorted(VALID)}")
    if status:
        return dict(need, object=obj, status=status)
    key = obj.lower()
    if key in gold or key.split(".")[-1] in gold:
        return dict(need, object=obj, status=E)
    return dict(need, object=obj, status=M if looks_gold(obj) else N)


def verdict(needs):
    st = {n["status"] for n in needs} - {N}
    if not st:
        return "no-gold-need"
    if st == {E}:
        return "in-gold"
    if st == {M}:
        return "missing"
    return "partial"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--lineage", required=True)
    ap.add_argument("--tickets", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--existing")
    ap.add_argument("--scope", default="")
    ap.add_argument("--title", default="")
    ap.add_argument("--description", default="")
    ap.add_argument("--questions")
    args = ap.parse_args()
    questions = json.loads(pathlib.Path(args.questions).read_text(encoding="utf-8")) if args.questions else []

    lineage = json.loads(pathlib.Path(args.lineage).read_text(encoding="utf-8"))
    tickets = json.loads(pathlib.Path(args.tickets).read_text(encoding="utf-8"))
    gold = gold_index(lineage)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today().isoformat()
    existing = pathlib.Path(args.existing) if args.existing else None

    writes = []
    rows = []
    for t in tickets:
        needs = [resolve(n, gold) for n in t.get("needs", [])]
        doc = {k: t.get(k, "") for k in ("key", "summary", "type", "status", "statusCategory", "assignee", "parent", "url", "note")}
        doc.update(needs=needs, verdict=verdict(needs), proposedBy="Claude", proposedOn=today, approved=False)
        old_file = existing / f"{t['key']}.json" if existing else None
        if old_file and old_file.exists():
            old = json.loads(old_file.read_text(encoding="utf-8"))
            old = old.get("data", old)
            if old.get("approved") and old.get("needs") == needs:
                doc.update(approved=True, approvedOn=old.get("approvedOn", ""), proposedOn=old.get("proposedOn", today))
        path = out / f"ticket_{t['key']}.json"
        path.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        writes.append({"op": "set", "collection": "tickets", "doc_id": t["key"], "file_path": str(path.resolve()).replace("\\", "/")})
        missing = [n["object"] for n in needs if n["status"] in (M, P)]
        rows.append((t["key"], doc["verdict"], doc["status"], ", ".join(missing)))

    lz = lineage.get("lz", "lz")
    gold_doc = {"lz": lz, "updated": lineage.get("updated", today), "commit": lineage.get("commit", ""),
                "objects": [{"name": o["name"], "builtBy": o.get("builtBy", ""), "usedBy": o.get("usedBy", []), "config": o.get("config", "")}
                            for o in lineage.get("objects", []) if o.get("layer") == "gold"]}
    gpath = out / f"gold_{lz}.json"
    gpath.write_text(json.dumps(gold_doc, ensure_ascii=False), encoding="utf-8")
    writes.append({"op": "set", "collection": "gold", "doc_id": lz, "file_path": str(gpath.resolve()).replace("\\", "/")})
    meta = {"scope": args.scope, "title": args.title, "description": args.description,
            "questions": questions, "updated": today,
            "goldFrom": f"{lz} gold configuration ({lineage.get('env', 'dev').upper()}), commit {lineage.get('commit', '')}",
            "method": "Claude read each ticket and proposed the gold objects it needs; the status is checked against the gold configuration, not the lakehouse."}
    mpath = out / "meta_summary.json"
    mpath.write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
    writes.append({"op": "set", "collection": "meta", "doc_id": "summary", "file_path": str(mpath.resolve()).replace("\\", "/")})
    (out / "batch.json").write_text(json.dumps(writes, indent=1), encoding="utf-8")

    width = max(len(r[0]) for r in rows) if rows else 6
    for key, v, st, miss in rows:
        print(f"{key:<{width}}  {v:<13} {st:<12} {miss}")
    print(f"\n{len(rows)} tickets -> {out} (batch.json has {len(writes)} writes; pin existing documents with if_version)")


if __name__ == "__main__":
    main()
