#!/usr/bin/env python3
"""Offline behavior tests for the plan generator; no site tests are performed."""

import copy
import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from build_regression_matrix import build_rows, no_duplicate_keys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/build_regression_matrix.py"
PLAN = ROOT / "assets/regression-plan.example.json"


class MatrixTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads(PLAN.read_text())

    def test_coverage_and_unexecuted_status(self):
        rows = build_rows(self.plan)
        self.assertEqual(len(rows), 66)
        self.assertEqual(len({row["case_id"] for row in rows}), 66)
        self.assertEqual({r["status"] for r in rows}, {"NOT_RUN"})
        self.assertTrue(all(not r["evidence"] and not r["tested_at"] for r in rows))
        self.assertEqual(len([r for r in rows if r["scenario"] == "carousel"]), 6)
        self.assertFalse(any(r["view"] == "details" and r["scenario"] == "carousel" for r in rows))
        self.assertEqual(build_rows(self.plan), rows)

    def test_locale_filter(self):
        self.plan["scenarios"] = [{"id": "locked-route", "expected": "保持现有回退", "locales": ["en"]}]
        rows = build_rows(self.plan)
        self.assertEqual(len(rows), 6)
        self.assertEqual({r["locale"] for r in rows}, {"en"})

    def test_invalid_dimensions(self):
        for key, value in [("locales", []), ("views", ["overview", "overview"]), ("viewport_widths", [True]), ("viewport_widths", [390, 390]), ("viewport_widths", [0]), ("locales", ["=evil"]), ("scenarios", [])]:
            with self.subTest(key=key, value=value):
                plan = copy.deepcopy(self.plan)
                plan[key] = value
                with self.assertRaises(ValueError):
                    build_rows(plan)

    def test_unknown_fields_and_duplicate_scenarios(self):
        self.plan["scenario"] = []
        with self.assertRaises(ValueError):
            build_rows(self.plan)
        del self.plan["scenario"]
        self.plan["scenarios"].append(copy.deepcopy(self.plan["scenarios"][0]))
        with self.assertRaises(ValueError):
            build_rows(self.plan)

    def test_unknown_scope_and_empty_expectation(self):
        self.plan["scenarios"][0]["views"] = ["typo"]
        with self.assertRaises(ValueError):
            build_rows(self.plan)
        del self.plan["scenarios"][0]["views"]
        self.plan["scenarios"][0]["expected"] = "  "
        with self.assertRaises(ValueError):
            build_rows(self.plan)

    def test_formula_text_is_literal(self):
        self.plan["scenarios"][0]["expected"] = " =1+1"
        self.assertEqual(build_rows(self.plan)[0]["expected"], "' =1+1")

    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(ValueError):
            json.loads('{"locales": [], "locales": ["zh"]}', object_pairs_hook=no_duplicate_keys)

    def test_cli_utf8_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "matrix.csv"
            command = [sys.executable, str(SCRIPT), str(PLAN), "--output", str(output)]
            first = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            original = output.read_bytes()
            with output.open(encoding="utf-8-sig", newline="") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(len(rows), 66)
            self.assertIn("页面", rows[0]["expected"])
            again = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(again.returncode, 2)
            self.assertEqual(output.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
