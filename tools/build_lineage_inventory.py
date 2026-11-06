"""Build the lineage inventory of one landing zone repository for the GA Platform Lineage page.

Reads only metadata and code, never data:
- Engineering/ConfigFiles/environments/<env>/*.yml and *.yaml (the YAML orchestrator configuration:
  bronze entries in the included files, silver and gold entries with dependsOn)
- Data_models/ and Reports/: *.SemanticModel/definition (TMDL) and *.Report/definition.pbir

Writes one JSON document per landing zone, the body of the document zones/<lz_code> in the
page's database. Claude writes it with ArtifactData (set, file_path) at the finishing step.

Usage: python build_lineage_inventory.py <landing zone repo> [--env dev] [--out <file.json>]
Needs PyYAML (python -m pip install pyyaml).
"""
import argparse
import datetime
import json
import pathlib
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is missing: python -m pip install pyyaml")

LAYER_ORDER = ["source", "bronze", "silver", "gold", "model", "report"]


def load_yaml(path):
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def is_active(entry, default):
    value = entry.get("flagActive", default)
    return str(value).strip() not in ("0", "False", "false")


def ref_to_id(ref):
    """'silver.gl_entry' -> 'silver:gl_entry'"""
    layer, _, name = str(ref).partition(".")
    return f"{layer}:{name}"


def own_lakehouse(name, lz, keep_all):
    """Only objects written to the landing zone's own lakehouses (lh_<lz>_...). Configuration for
    other lakehouses, such as the ingestion framework's AdventureWorks test flow, is left out."""
    return keep_all or not name or lz.lower() in str(name).lower()


def read_engineering(repo, env, lz, keep_all=False):
    folder = repo / "Engineering" / "ConfigFiles" / "environments" / env
    if not folder.is_dir():
        return [], []
    objects, sources = [], {}
    for main in sorted(folder.glob("*.yml")):
        config = load_yaml(main)
        if not isinstance(config, dict) or not ({"bronze", "silver", "gold"} & set(config)):
            continue
        default_active = (config.get("defaults") or {}).get("flagActive", 1)

        bronze = config.get("bronze") or {}
        bronze_entries = {k: v for k, v in bronze.items() if k != "includes" and isinstance(v, dict)}
        for include in bronze.get("includes") or []:
            inc = folder / include
            if not inc.exists():
                inc = inc.with_suffix(".yml" if inc.suffix == ".yaml" else ".yaml")
            if inc.exists():
                bronze_entries.update({k: v for k, v in load_yaml(inc).items() if isinstance(v, dict)})
        for name, e in bronze_entries.items():
            if not own_lakehouse(e.get("destinationSystemName"), lz, keep_all):
                continue
            system = e.get("sourceSystemName", "unknown")
            src_id = f"source:{system}"
            s = sources.setdefault(src_id, {
                "id": src_id, "layer": "source", "name": system,
                "detail": e.get("sourceLocationName", ""), "type": e.get("sourceSystemType", ""),
                "builtBy": e.get("artifactName", ""), "from": [], "entries": 0, "active": True,
            })
            s["entries"] += 1
            objects.append({
                "id": f"bronze:{name}", "layer": "bronze", "name": name,
                "schema": (e.get("destinationDirectoryPattern") or "").split("/")[0],
                "lakehouse": e.get("destinationSystemName", ""),
                "detail": e.get("destinationDirectoryPattern", ""),
                "builtBy": e.get("artifactName", "") + (" via landing" if str(e.get("requiresLanding")).lower() == "true" else ""),
                "from": [src_id], "active": is_active(e, default_active), "config": main.name,
            })

        for layer in ("silver", "gold"):
            for name, e in (config.get(layer) or {}).items():
                if not isinstance(e, dict) or not own_lakehouse(e.get("destinationDatabase"), lz, keep_all):
                    continue
                pattern = e.get("destinationObjectPattern", "")
                deps = [ref_to_id(d) for d in e.get("dependsOn") or []]
                objects.append({
                    "id": f"{layer}:{name}", "layer": layer, "name": pattern.replace("/", ".") or name,
                    "schema": pattern.split("/")[0] if "/" in pattern else "",
                    "lakehouse": e.get("destinationDatabase", ""),
                    "detail": e.get("sourceDirectoryPattern", ""),
                    "builtBy": e.get("artifactName", ""), "from": deps,
                    "active": is_active(e, default_active), "config": main.name,
                })
    return list(sources.values()), objects


def read_models(repo, gold_by_pattern):
    objects = []
    for folder in ("Data_models", "Reports"):
        base = repo / folder
        if not base.is_dir():
            continue
        for sm in sorted(base.glob("*.SemanticModel")):
            name = sm.name[: -len(".SemanticModel")]
            text = "\n".join(p.read_text(encoding="utf-8") for p in (sm / "definition").rglob("*.tmdl"))
            froms, external = [], set()
            for m in re.finditer(r'Sql\.Database\([^,]+,\s*"([^"]+)"\)[\s\S]{0,400}?Schema\s*=\s*"([^"]+)",\s*Item\s*=\s*"([^"]+)"', text):
                lakehouse, schema, item = m.groups()
                gold = gold_by_pattern.get(f"{schema}/{item}")
                froms.append(gold or f"external:{lakehouse}.{schema}.{item}")
            if "SharePoint.Tables(" in text:
                external.add("SharePoint lists")
            if "SharePoint.Files(" in text or "Excel.Workbook(" in text:
                external.add("SharePoint files")
            tables = sorted(set(re.findall(r"^table (?:'([^']+)'|(\S+))", text, re.M)))
            objects.append({
                "id": f"model:{name}", "layer": "model", "name": name, "schema": folder,
                "lakehouse": "", "detail": ", ".join(a or b for a, b in tables),
                "builtBy": "Power Query (import)" if "mode: import" in text else "",
                "from": sorted(set(froms)), "external": sorted(external), "active": True,
            })
        for rep in sorted(base.glob("*.Report")):
            pbir = rep / "definition.pbir"
            if not pbir.exists():
                continue
            ref = json.loads(pbir.read_text(encoding="utf-8")).get("datasetReference", {})
            model = None
            if "byPath" in ref:
                model = pathlib.PurePosixPath(ref["byPath"]["path"]).name.removesuffix(".SemanticModel")
            elif "byConnection" in ref:
                conn = ref["byConnection"].get("connectionString", "")
                found = re.search(r'initial catalog="?([^";]+)', conn, re.I)
                model = found.group(1) if found else None
            objects.append({
                "id": f"report:{rep.name[: -len('.Report')]}", "layer": "report",
                "name": rep.name[: -len(".Report")], "schema": folder, "lakehouse": "", "detail": "",
                "builtBy": "PBIR", "from": [f"model:{model}"] if model else [], "active": True,
            })
    return objects


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo")
    ap.add_argument("--env", default="dev")
    ap.add_argument("--out")
    ap.add_argument("--all-lakehouses", action="store_true",
                    help="also include configuration for lakehouses outside the landing zone (test and template flows)")
    args = ap.parse_args()

    repo = pathlib.Path(args.repo).resolve()
    lz = re.sub(r"^ga_", "", repo.name)
    sources, eng = read_engineering(repo, args.env, lz, args.all_lakehouses)
    gold_by_pattern = {}
    for o in eng:
        if o["layer"] == "gold":
            gold_by_pattern[o["name"].replace(".", "/", 1)] = o["id"]
    objects = sources + eng + read_models(repo, gold_by_pattern)

    by_id = {o["id"]: o for o in objects}
    for o in objects:
        o["usedBy"] = []
    for o in objects:
        for f in o["from"]:
            if f in by_id:
                by_id[f]["usedBy"].append(o["id"])
    objects.sort(key=lambda o: (LAYER_ORDER.index(o["layer"]), o["id"].lower()))

    try:
        commit = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h %cs"],
                                capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = ""
    doc = {
        "lz": lz, "repo": repo.name, "env": args.env, "commit": commit,
        "updated": datetime.date.today().isoformat(),
        "counts": {layer: sum(1 for o in objects if o["layer"] == layer) for layer in LAYER_ORDER},
        "objects": objects,
    }
    out = json.dumps(doc, ensure_ascii=False, indent=1)
    if len(out.encode("utf-8")) > 250_000:
        sys.exit(f"Inventory is {len(out.encode('utf-8'))} bytes; the page stores at most 256 KiB per landing zone.")
    if args.out:
        pathlib.Path(args.out).write_text(out, encoding="utf-8")
        print(f"{lz}: {doc['counts']} -> {args.out} ({len(out.encode('utf-8'))} bytes)")
    else:
        print(out)


if __name__ == "__main__":
    main()
