#!/usr/bin/env python3
"""Merge all invoice line items into the first row.

Keeps the first 项目名称, sums 金额 / 税额, recalculates 单价 from
quantity (default 1), and drops remaining rows. Invoice totals are unchanged.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


TWOPLACES = Decimal("0.01")


def d(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def money(value: Decimal) -> Decimal:
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def merge_line_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Collapse every line item into the first one."""
    if not items:
        return []
    if len(items) == 1:
        return [deepcopy(items[0])]

    first = deepcopy(items[0])
    total_amount = money(sum(d(item.get("金额", 0)) for item in items))
    total_tax = money(sum(d(item.get("税额", 0)) for item in items))
    quantity = d(first.get("数量") or 1)
    if quantity == 0:
        quantity = Decimal("1")

    unit_price = (total_amount / quantity).quantize(
        Decimal("0.000000000000001"), rounding=ROUND_HALF_UP
    )

    first["金额"] = float(total_amount)
    first["税额"] = float(total_tax)
    first["数量"] = float(quantity)
    first["单价"] = float(unit_price)
    # Keep tax rate / unit from the first row; names of dropped rows stay out.
    first.pop("_merged_from", None)
    first["_merged_count"] = len(items)
    first["_merged_names"] = [item.get("项目名称", "") for item in items]

    return [first]


def merge_invoice(invoice: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(invoice)
    original_items = list(result.get("项目明细") or [])
    result["项目明细"] = merge_line_items(original_items)
    result["_original_item_count"] = len(original_items)
    return result


def verify_totals(invoice: dict[str, Any]) -> dict[str, Any]:
    items = invoice.get("项目明细") or []
    amount = money(sum(d(item.get("金额", 0)) for item in items))
    tax = money(sum(d(item.get("税额", 0)) for item in items))
    expected_amount = money(d(invoice.get("合计金额", amount)))
    expected_tax = money(d(invoice.get("合计税额", tax)))
    return {
        "金额一致": amount == expected_amount,
        "税额一致": tax == expected_tax,
        "明细金额合计": float(amount),
        "明细税额合计": float(tax),
        "发票合计金额": float(expected_amount),
        "发票合计税额": float(expected_tax),
    }


def load_invoices(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "invoices" in data:
        return data["invoices"]
    if isinstance(data, dict):
        return [data]
    raise ValueError(f"Unsupported JSON shape in {path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="将发票项目明细合并到第一项（保留首项项目名称，金额税额求和）"
    )
    parser.add_argument(
        "-i",
        "--input",
        type=Path,
        default=Path(__file__).with_name("sample_invoices.json"),
        help="输入发票 JSON（单张、数组、或 {invoices:[...]})",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path(__file__).with_name("merged_invoices.json"),
        help="合并后的输出 JSON",
    )
    args = parser.parse_args(argv)

    invoices = load_invoices(args.input)
    merged = []
    for inv in invoices:
        out = merge_invoice(inv)
        out["_校验"] = verify_totals(out)
        merged.append(out)

        no = inv.get("发票号码", "?")
        before = len(inv.get("项目明细") or [])
        after_item = out["项目明细"][0] if out["项目明细"] else {}
        print(f"发票 {no}: {before} 项 → 1 项")
        print(f"  项目名称: {after_item.get('项目名称')}")
        print(f"  金额: {after_item.get('金额')}  税额: {after_item.get('税额')}")
        print(f"  校验: {out['_校验']}")

    payload = {"invoices": merged}
    args.output.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\n已写入 {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
