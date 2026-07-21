#!/usr/bin/env python3
"""Unit tests for merge_line_items."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from merge_items import merge_invoice, merge_line_items, verify_totals


ROOT = Path(__file__).resolve().parent


class MergeItemsTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(merge_line_items([]), [])

    def test_single_unchanged(self):
        items = [{"项目名称": "A", "金额": 10, "税额": 1, "数量": 1, "单价": 10}]
        out = merge_line_items(items)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["项目名称"], "A")
        self.assertEqual(out[0]["金额"], 10)

    def test_merge_keeps_first_name_and_sums(self):
        items = [
            {"项目名称": "*生产生活服务*代订机票", "金额": 2547.17, "税额": 152.83, "数量": 1},
            {"项目名称": "*生产生活服务*退改费用", "金额": 6606.60, "税额": 396.40, "数量": 1},
            {"项目名称": "*生产生活服务*代订附加产品", "金额": 64.15, "税额": 3.85, "数量": 1},
        ]
        out = merge_line_items(items)
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["项目名称"], "*生产生活服务*代订机票")
        self.assertEqual(out[0]["金额"], 9217.92)
        self.assertEqual(out[0]["税额"], 553.08)
        self.assertEqual(out[0]["_merged_count"], 3)

    def test_sample_invoices(self):
        data = json.loads((ROOT / "sample_invoices.json").read_text(encoding="utf-8"))
        for inv in data["invoices"]:
            before = len(inv["项目明细"])
            self.assertGreater(before, 1)
            first_name = inv["项目明细"][0]["项目名称"]
            merged = merge_invoice(inv)
            self.assertEqual(len(merged["项目明细"]), 1)
            self.assertEqual(merged["项目明细"][0]["项目名称"], first_name)
            check = verify_totals(merged)
            self.assertTrue(check["金额一致"], check)
            self.assertTrue(check["税额一致"], check)


if __name__ == "__main__":
    unittest.main()
