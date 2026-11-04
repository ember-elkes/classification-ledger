#!/usr/bin/env python3
"""Validate classification-ledger entries and compile them to JSON and CSV.

Usage:
    python build/compile.py                  validate, then write data/ledger.json and data/ledger.csv
    python build/compile.py --check          validate only
    python build/compile.py --include-stubs  include stub entries in the output files

Entries live in entries/*.md. Files whose names start with "_" (such as the
template) and README.md are ignored. Exit status is 0 on success, 1 if any entry
fails validation, and 2 if the entries directory cannot be found.

Licensed under the MIT License. See LICENSE.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required. Install it with: pip install -r requirements.txt")

ROOT = Path(__file__).resolve().parent.parent

SCHEMA_VERSION = 1

# Controlled vocabularies. Keep these in sync with METHOD.md.
STATUSES = ("stub", "draft", "published")
CLAIMED_IDENTITIES = ("hacktivist", "cybercriminal", "extortion", "state", "unknown", "other")
CONFIDENCE = ("low", "moderate", "high")
IMPACT = (
    "nuisance", "disruption", "destabilization", "harm_to_life",
    "information", "extortion", "theft", "intelligence",
)
ALIGNMENT = ("opposed", "agnostic", "aligned", "undetermined")
STATE_BANDS = ("tolerated", "influenced", "supported", "controlled")
HEALEY_POINTS = (
    "state_prohibited", "prohibited_but_inadequate", "state_ignored", "state_encouraged",
    "state_shaped", "state_coordinated", "state_ordered", "state_rogue_conducted",
    "state_executed", "state_integrated", "undetermined",
)
SAMUEL_TYPES = ("political_coding", "political_cracking", "performative_hacktivism", "unnamed_cell")
BL_LEVELS = ("loner", "colleagues", "peers", "teams", "formal_organization")
SOURCE_TIERS = (
    "primary_actor_controlled", "government_law_enforcement", "vendor_threat_intel",
    "journalism_specialist_media", "academic_think_tank", "aggregator_wiki",
)

# Placement name -> {value field: (kind, allowed values)}.
# kinds: "one" (required single value), "many" (required non-empty list),
#        "one_optional" (single value that may be omitted)
PLACEMENT_FIELDS = {
    "derbyshire": {
        "impact": ("many", IMPACT),
        "alignment": ("one", ALIGNMENT),
        "state_band": ("one_optional", STATE_BANDS),
    },
    "healey": {"point": ("one", HEALEY_POINTS)},
    "samuel": {"type": ("one", SAMUEL_TYPES)},
    "best_luckenbill": {"level": ("one", BL_LEVELS)},
}
REQUIRED_PLACEMENTS = ("derbyshire", "healey")
COMMON_PLACEMENT_FIELDS = ("confidence", "evidence", "would_change_if")

TOP_LEVEL_KEYS = {
    "id", "name", "claimed_identity", "aliases", "status",
    "last_reviewed", "sources", "placements", "history",
}
SOURCE_KEYS = {"id", "title", "url", "tier", "retrieved"}

ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}(-\d{2})?$")
FRONT_MATTER = re.compile(r"^---[ \t]*\n(.*?)\n---[ \t]*(?:\n|$)(.*)$", re.DOTALL)


def as_text(value):
    """Return a string for str or date values, otherwise None."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()[:10]
    return None


def split_front_matter(text):
    text = text.replace("\r\n", "\n")
    if not text.startswith("---"):
        raise ValueError("file must start with a '---' YAML front matter block")
    match = FRONT_MATTER.match(text)
    if not match:
        raise ValueError("front matter is not closed with a '---' line")
    return match.group(1), match.group(2)


def check_choice(value, allowed, label, errors):
    if value not in allowed:
        errors.append(f"{label}: {value!r} is not one of {', '.join(allowed)}")
        return False
    return True


def validate_sources(meta, errors):
    """Validate the sources list. Returns the set of defined source ids."""
    sources = meta.get("sources", [])
    ids = set()
    if sources is None:
        sources = []
    if not isinstance(sources, list):
        errors.append("sources: must be a list")
        return ids
    for index, source in enumerate(sources, start=1):
        label = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{label}: must be a mapping")
            continue
        for key in source:
            if key not in SOURCE_KEYS:
                errors.append(f"{label}: unknown field {key!r}")
        for key in ("id", "title", "url", "tier", "retrieved"):
            if key not in source:
                errors.append(f"{label}: missing {key!r}")
        source_id = source.get("id")
        if isinstance(source_id, str) and source_id:
            if source_id in ids:
                errors.append(f"{label}: duplicate source id {source_id!r}")
            ids.add(source_id)
        elif "id" in source:
            errors.append(f"{label}: id must be a non-empty string")
        url = source.get("url")
        if "url" in source and not (isinstance(url, str) and url.startswith(("http://", "https://"))):
            errors.append(f"{label}: url must start with http:// or https://")
        if "title" in source and not (isinstance(source.get("title"), str) and source["title"].strip()):
            errors.append(f"{label}: title must be a non-empty string")
        if "tier" in source:
            check_choice(source["tier"], SOURCE_TIERS, f"{label}.tier", errors)
        if "retrieved" in source:
            retrieved = as_text(source["retrieved"])
            if retrieved is None or not DATE_PATTERN.match(retrieved):
                errors.append(f"{label}: retrieved must be a date like 2026-11-04")
    return ids


def validate_placement(name, placement, strict, source_ids, errors):
    label = f"placements.{name}"
    if not isinstance(placement, dict):
        errors.append(f"{label}: must be a mapping")
        return
    spec = PLACEMENT_FIELDS[name]
    allowed_keys = set(spec) | set(COMMON_PLACEMENT_FIELDS)
    for key in placement:
        if key not in allowed_keys:
            errors.append(f"{label}: unknown field {key!r}")

    # Value fields
    for field, (kind, allowed) in spec.items():
        present = field in placement and placement[field] is not None
        if not present:
            if kind in ("one", "many") and strict:
                errors.append(f"{label}.{field}: required for draft and published entries")
            continue
        value = placement[field]
        if kind == "many":
            if not isinstance(value, list) or not value:
                errors.append(f"{label}.{field}: must be a non-empty list")
            else:
                for item in value:
                    check_choice(item, allowed, f"{label}.{field}", errors)
        else:
            check_choice(value, allowed, f"{label}.{field}", errors)

    if name == "derbyshire":
        band = placement.get("state_band")
        if band is not None and placement.get("alignment") != "aligned":
            errors.append(f"{label}.state_band: only allowed when alignment is 'aligned'")

    # Confidence
    confidence = placement.get("confidence")
    if confidence is None:
        if strict:
            errors.append(f"{label}.confidence: required for draft and published entries")
    else:
        check_choice(confidence, CONFIDENCE, f"{label}.confidence", errors)

    # Evidence
    evidence = placement.get("evidence")
    if evidence is None:
        evidence_list = []
        if strict:
            errors.append(f"{label}.evidence: required for draft and published entries")
    elif not isinstance(evidence, list) or not all(isinstance(e, str) for e in evidence):
        evidence_list = []
        errors.append(f"{label}.evidence: must be a list of source ids")
    else:
        evidence_list = evidence
        if strict and not evidence_list:
            errors.append(f"{label}.evidence: needs at least one source id")
        for source_id in evidence_list:
            if source_id not in source_ids:
                errors.append(f"{label}.evidence: {source_id!r} is not defined in sources")
        if len(set(evidence_list)) != len(evidence_list):
            errors.append(f"{label}.evidence: contains duplicate ids")
    if confidence == "high" and len(set(evidence_list)) < 2:
        errors.append(f"{label}: 'high' confidence needs at least two distinct evidence ids")

    # Would change if
    change = placement.get("would_change_if")
    if change is None:
        if strict:
            errors.append(f"{label}.would_change_if: required for draft and published entries")
    elif not (isinstance(change, str) and change.strip()):
        errors.append(f"{label}.would_change_if: must be a non-empty string")


def validate_entry(meta, stem):
    """Return a list of error strings for one entry's front matter."""
    errors = []
    if not isinstance(meta, dict):
        return ["front matter must be a YAML mapping"]

    for key in meta:
        if key not in TOP_LEVEL_KEYS:
            errors.append(f"unknown field {key!r}")

    # id and name
    entry_id = meta.get("id")
    if not isinstance(entry_id, str) or not ID_PATTERN.match(entry_id):
        errors.append("id: required; use lowercase letters, numbers, and hyphens")
    elif entry_id != stem:
        errors.append(f"id: {entry_id!r} must match the file name {stem!r}")
    name = meta.get("name")
    if not (isinstance(name, str) and name.strip()):
        errors.append("name: required")

    # claimed_identity and status
    if "claimed_identity" not in meta:
        errors.append("claimed_identity: required")
    else:
        check_choice(meta["claimed_identity"], CLAIMED_IDENTITIES, "claimed_identity", errors)
    status = meta.get("status")
    if status is None:
        errors.append("status: required")
    else:
        check_choice(status, STATUSES, "status", errors)
    strict = status in ("draft", "published")

    # last_reviewed
    reviewed = as_text(meta.get("last_reviewed"))
    if reviewed is None or not DATE_PATTERN.match(reviewed):
        errors.append("last_reviewed: required, as YYYY-MM or YYYY-MM-DD")

    # aliases
    aliases = meta.get("aliases", [])
    if aliases is None:
        aliases = []
    if not isinstance(aliases, list) or not all(isinstance(a, str) and a.strip() for a in aliases):
        errors.append("aliases: must be a list of non-empty strings")

    # sources and placements
    source_ids = validate_sources(meta, errors)
    placements = meta.get("placements") or {}
    if not isinstance(placements, dict):
        errors.append("placements: must be a mapping")
        placements = {}
    for key in placements:
        if key not in PLACEMENT_FIELDS:
            errors.append(f"placements: unknown framework {key!r}")
    if strict:
        for required in REQUIRED_PLACEMENTS:
            if required not in placements:
                errors.append(f"placements.{required}: required for draft and published entries")
    for name_, placement in placements.items():
        if name_ in PLACEMENT_FIELDS:
            validate_placement(name_, placement, strict, source_ids, errors)

    # history
    history = meta.get("history", [])
    if history is None:
        history = []
    if not isinstance(history, list):
        errors.append("history: must be a list")
    else:
        for index, item in enumerate(history, start=1):
            label = f"history[{index}]"
            if not isinstance(item, dict) or set(item) - {"date", "change"}:
                errors.append(f"{label}: must be a mapping with 'date' and 'change'")
                continue
            item_date = as_text(item.get("date"))
            if item_date is None or not DATE_PATTERN.match(item_date):
                errors.append(f"{label}.date: required, as YYYY-MM or YYYY-MM-DD")
            if not (isinstance(item.get("change"), str) and item["change"].strip()):
                errors.append(f"{label}.change: required")
    return errors


def build_record(meta, path, base):
    """Return a normalized, JSON-safe record for one valid entry."""
    placements = {}
    for name, placement in (meta.get("placements") or {}).items():
        record = {}
        for field in PLACEMENT_FIELDS[name]:
            if placement.get(field) is not None:
                record[field] = placement[field]
        for field in COMMON_PLACEMENT_FIELDS:
            if placement.get(field) is not None:
                record[field] = placement[field]
        placements[name] = record
    sources = [
        {
            "id": s["id"],
            "title": s["title"],
            "url": s["url"],
            "tier": s["tier"],
            "retrieved": as_text(s["retrieved"]),
        }
        for s in (meta.get("sources") or [])
    ]
    history = [
        {"date": as_text(h["date"]), "change": h["change"]}
        for h in (meta.get("history") or [])
    ]
    try:
        rel_path = path.relative_to(base).as_posix()
    except ValueError:
        rel_path = path.name
    return {
        "id": meta["id"],
        "name": meta["name"],
        "claimed_identity": meta["claimed_identity"],
        "aliases": list(meta.get("aliases") or []),
        "status": meta["status"],
        "last_reviewed": as_text(meta["last_reviewed"]),
        "placements": placements,
        "sources": sources,
        "history": history,
        "path": rel_path,
    }


CSV_COLUMNS = [
    "id", "name", "claimed_identity", "aliases", "status", "last_reviewed",
    "derbyshire_impact", "derbyshire_alignment", "derbyshire_state_band", "derbyshire_confidence",
    "healey_point", "healey_confidence",
    "samuel_type", "samuel_confidence",
    "best_luckenbill_level", "best_luckenbill_confidence",
    "source_count", "path",
]


def csv_row(record):
    placements = record["placements"]
    derbyshire = placements.get("derbyshire", {})
    healey = placements.get("healey", {})
    samuel = placements.get("samuel", {})
    bl = placements.get("best_luckenbill", {})
    return {
        "id": record["id"],
        "name": record["name"],
        "claimed_identity": record["claimed_identity"],
        "aliases": "; ".join(record["aliases"]),
        "status": record["status"],
        "last_reviewed": record["last_reviewed"],
        "derbyshire_impact": "; ".join(derbyshire.get("impact", [])),
        "derbyshire_alignment": derbyshire.get("alignment", ""),
        "derbyshire_state_band": derbyshire.get("state_band", ""),
        "derbyshire_confidence": derbyshire.get("confidence", ""),
        "healey_point": healey.get("point", ""),
        "healey_confidence": healey.get("confidence", ""),
        "samuel_type": samuel.get("type", ""),
        "samuel_confidence": samuel.get("confidence", ""),
        "best_luckenbill_level": bl.get("level", ""),
        "best_luckenbill_confidence": bl.get("confidence", ""),
        "source_count": len(record["sources"]),
        "path": record["path"],
    }


def load_entries(entries_dir):
    """Return (records, errors). Errors are 'file: message' strings."""
    records = []
    errors = []
    seen_ids = {}
    for path in sorted(entries_dir.glob("*.md")):
        if path.name.startswith("_") or path.name.lower() == "readme.md":
            continue
        try:
            raw_meta, _body = split_front_matter(path.read_text(encoding="utf-8"))
            meta = yaml.safe_load(raw_meta)
        except (ValueError, yaml.YAMLError, UnicodeDecodeError) as exc:
            errors.append(f"{path.name}: {exc}")
            continue
        entry_errors = validate_entry(meta, path.stem)
        if entry_errors:
            errors.extend(f"{path.name}: {message}" for message in entry_errors)
            continue
        if meta["id"] in seen_ids:
            errors.append(f"{path.name}: duplicate id {meta['id']!r} (also in {seen_ids[meta['id']]})")
            continue
        seen_ids[meta["id"]] = path.name
        records.append(build_record(meta, path, entries_dir.parent))
    return records, errors


def write_outputs(records, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {"schema_version": SCHEMA_VERSION, "count": len(records), "entries": records}
    (out_dir / "ledger.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    with (out_dir / "ledger.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow(csv_row(record))


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate and compile classification-ledger entries.")
    parser.add_argument("--check", action="store_true", help="validate only; write no files")
    parser.add_argument("--include-stubs", action="store_true", help="include stub entries in the output files")
    parser.add_argument("--entries", type=Path, default=ROOT / "entries", help="entries directory")
    parser.add_argument("--out", type=Path, default=ROOT / "data", help="output directory")
    args = parser.parse_args(argv)

    if not args.entries.is_dir():
        print(f"Entries directory not found: {args.entries}", file=sys.stderr)
        return 2

    records, errors = load_entries(args.entries)
    if errors:
        print(f"{len(errors)} problem(s) found:", file=sys.stderr)
        for message in errors:
            print(f"  {message}", file=sys.stderr)
        return 1

    counts = {status: sum(1 for r in records if r["status"] == status) for status in STATUSES}
    summary = (
        f"Validated {len(records)} entries "
        f"({counts['published']} published, {counts['draft']} draft, {counts['stub']} stub)."
    )
    if args.check:
        print(summary)
        return 0

    output = records if args.include_stubs else [r for r in records if r["status"] != "stub"]
    write_outputs(output, args.out)
    skipped = len(records) - len(output)
    note = f" Left out {skipped} stub(s); use --include-stubs to include them." if skipped else ""
    print(f"{summary} Wrote {len(output)} entries to {args.out}.{note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
