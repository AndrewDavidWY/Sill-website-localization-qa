#!/usr/bin/env python3
"""Generate a NOT_RUN regression plan. Offline; does not execute any tests."""

import argparse
import csv
import json
import re
import sys
from itertools import product
from pathlib import Path

FIELDS = [
    "case_id", "locale", "view", "viewport_width", "scenario", "expected",
    "status", "evidence", "observed", "tested_at", "environment", "revision",
    "browser", "data_snapshot", "reason",
]
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,79}\Z")
MAX_ROWS = 100_000


def keys(value, required, optional, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    missing = required - value.keys()
    unknown = value.keys() - required - optional
    if missing or unknown:
        raise ValueError(f"{label}: missing={sorted(missing)}, unknown={sorted(unknown)}")


def identifiers(value, label):
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty list")
    if any(not isinstance(v, str) or not ID.fullmatch(v) for v in value):
        raise ValueError(f"{label}: use short identifiers containing letters, digits, ., _, -")
    if len(value) != len(set(value)):
        raise ValueError(f"{label} contains duplicates")
    return value


def text_cell(value):
    # Preserve potentially formula-like text as literal text in spreadsheet apps.
    if value.lstrip().startswith(("=", "+", "-", "@")) or value.startswith(("\t", "\r", "\n")):
        return "'" + value
    return value


def build_rows(plan):
    keys(plan, {"locales", "views", "viewport_widths", "scenarios"}, set(), "plan")
    locales = identifiers(plan["locales"], "locales")
    views = identifiers(plan["views"], "views")
    widths = plan["viewport_widths"]
    if not isinstance(widths, list) or not widths:
        raise ValueError("viewport_widths must be a nonempty list")
    if any(type(w) is not int or not 1 <= w <= 16_384 for w in widths):
        raise ValueError("viewport_widths must be integers between 1 and 16384")
    if len(widths) != len(set(widths)):
        raise ValueError("viewport_widths contains duplicates")
    scenarios = plan["scenarios"]
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError("scenarios must be a nonempty list")
    seen = set()
    validated = []
    for s in scenarios:
        keys(s, {"id", "expected"}, {"views", "locales"}, "scenario")
        identifiers([s["id"]], "scenario.id")
        if s["id"] in seen:
            raise ValueError(f"duplicate scenario: {s['id']}")
        seen.add(s["id"])
        if not isinstance(s["expected"], str) or not s["expected"].strip():
            raise ValueError("scenario.expected must be nonempty text")
        sv = identifiers(s.get("views", views), "scenario.views")
        sl = identifiers(s.get("locales", locales), "scenario.locales")
        if not set(sv) <= set(views) or not set(sl) <= set(locales):
            raise ValueError(f"scenario {s['id']} refers to an unknown view or locale")
        validated.append((s, set(sv), set(sl)))
    count = sum(len(sv) * len(sl) * len(widths) for _, sv, sl in validated)
    if count > MAX_ROWS:
        raise ValueError(f"plan exceeds {MAX_ROWS} rows; split by a documented scope")
    rows = []
    for locale, view, width in product(locales, views, widths):
        for scenario, allowed_views, allowed_locales in validated:
            if view not in allowed_views or locale not in allowed_locales:
                continue
            row = dict.fromkeys(FIELDS, "")
            row.update(
                case_id=f"case-{len(rows)+1:06d}", locale=locale, view=view,
                viewport_width=width, scenario=scenario["id"],
                expected=text_cell(scenario["expected"]), status="NOT_RUN",
            )
            rows.append(row)
    return rows


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("plan", type=Path, help="UTF-8 JSON plan")
    parser.add_argument("--output", required=True, type=Path, help="New CSV path; existing files are never overwritten")
    args = parser.parse_args()
    created = False
    try:
        plan = json.loads(args.plan.read_text(encoding="utf-8-sig"), object_pairs_hook=no_duplicate_keys)
        rows = build_rows(plan)
        with args.output.open("x", encoding="utf-8-sig", newline="") as output:
            created = True
            writer = csv.DictWriter(output, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        if created:
            print(f"Incomplete new output; do not use it as a plan: {args.output}", file=sys.stderr)
        return 2
    print(f"Created {len(rows)} planned cases, all NOT_RUN: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
