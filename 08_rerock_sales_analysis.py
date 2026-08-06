#!/usr/bin/env python3
"""
ReRock Weekly Sales Analysis

Usage:
    python rerock_sales_analysis.py
    python rerock_sales_analysis.py --csv 07_sales_data.csv

This script calculates weekly sales metrics and writes:
    output_sales_report.txt
    output_sales_analysis.json
    output_weekly_sales_chart.png  (if matplotlib is installed)
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_SALES = [
    {"week": 1, "period": "May 4-May 10, 2026", "sales": 3140.97},
    {"week": 2, "period": "May 11-May 17, 2026", "sales": 3577.61},
    {"week": 3, "period": "May 18-May 24, 2026", "sales": 4014.98},
    {"week": 4, "period": "May 25-May 31, 2026", "sales": 6171.99},
]

TOP_PRODUCTS = [
    "Supreme socks",
    "In Glock We Trust tees",
    "Fear of God shorts",
    "$15 vintage tees",
    "$25 vintage t-shirts",
]


def money(value: float) -> str:
    return f"${value:,.2f}"


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def load_sales_from_csv(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            week = int(row.get("Week") or row.get("week") or row.get("week_number"))
            period = row.get("Period") or row.get("period")
            sales_raw = row.get("Sales") or row.get("sales")
            if sales_raw is None:
                raise ValueError("CSV must contain a Sales column.")
            sales = float(str(sales_raw).replace("$", "").replace(",", ""))
            rows.append({"week": week, "period": period, "sales": sales})
    return rows


def analyze_sales(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if len(rows) < 2:
        raise ValueError("Need at least two weeks of sales data.")

    sales = [float(row["sales"]) for row in rows]
    total = sum(sales)
    average = total / len(sales)
    prior_baseline = sum(sales[:-1]) / (len(sales) - 1)
    latest = sales[-1]
    latest_lift = latest - prior_baseline
    latest_lift_pct = latest / prior_baseline - 1 if prior_baseline else 0

    weekly = []
    for i, row in enumerate(rows):
        item = dict(row)
        if i == 0:
            item["wow_change"] = None
            item["wow_growth_pct"] = None
        else:
            item["wow_change"] = sales[i] - sales[i - 1]
            item["wow_growth_pct"] = sales[i] / sales[i - 1] - 1 if sales[i - 1] else None
        weekly.append(item)

    scenarios = [
        {
            "name": "Conservative baseline",
            "weekly_target": prior_baseline,
            "four_week_total": prior_baseline * 4,
        },
        {
            "name": "Hold 50% of latest lift",
            "weekly_target": prior_baseline + 0.5 * latest_lift,
            "four_week_total": (prior_baseline + 0.5 * latest_lift) * 4,
        },
        {
            "name": "Hold 75% of latest lift",
            "weekly_target": prior_baseline + 0.75 * latest_lift,
            "four_week_total": (prior_baseline + 0.75 * latest_lift) * 4,
        },
        {
            "name": "Repeat latest week",
            "weekly_target": latest,
            "four_week_total": latest * 4,
        },
    ]

    return {
        "weekly": weekly,
        "total_sales": total,
        "average_weekly_sales": average,
        "prior_baseline_average": prior_baseline,
        "latest_week_sales": latest,
        "latest_lift_vs_baseline": latest_lift,
        "latest_lift_pct_vs_baseline": latest_lift_pct,
        "top_products": TOP_PRODUCTS,
        "seasonal_hypothesis": {
            "claim": "School being out and graduation parties likely contributed to the latest spike.",
            "confidence": "medium",
            "validation_needed": [
                "daily sales",
                "transaction count",
                "average order value",
                "customer count",
                "promotion calendar",
                "margin by product",
            ],
        },
        "scenarios": scenarios,
    }


def write_report(analysis: dict[str, Any], out_path: Path) -> None:
    lines = []
    lines.append("ReRock Weekly Sales Analysis")
    lines.append("=" * 35)
    lines.append("")
    lines.append(f"Total sales: {money(analysis['total_sales'])}")
    lines.append(f"Average weekly sales: {money(analysis['average_weekly_sales'])}")
    lines.append(f"Latest week sales: {money(analysis['latest_week_sales'])}")
    lines.append(
        "Latest lift vs baseline: "
        f"{money(analysis['latest_lift_vs_baseline'])} / "
        f"{pct(analysis['latest_lift_pct_vs_baseline'])}"
    )
    lines.append("")
    lines.append("Weekly data:")
    for row in analysis["weekly"]:
        wow = "-"
        if row["wow_change"] is not None:
            wow = f"{money(row['wow_change'])} / {pct(row['wow_growth_pct'])}"
        lines.append(f"- Week {row['week']} ({row['period']}): {money(row['sales'])}; WoW {wow}")
    lines.append("")
    lines.append("Top products:")
    for product in analysis["top_products"]:
        lines.append(f"- {product}")
    lines.append("")
    lines.append("Recommended next action:")
    lines.append("Run a 14-day Summer Break / Graduation Party Fits campaign with bundles, daily posts, and SMS/email follow-up.")
    out_path.write_text("\n".join(lines))


def write_chart(rows: list[dict[str, Any]], out_path: Path) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception:
        return

    labels = [row["period"].replace(", 2026", "") for row in rows]
    values = [float(row["sales"]) for row in rows]

    plt.figure(figsize=(8, 4.5))
    plt.plot(labels, values, marker="o")
    plt.title("ReRock Weekly Sales Trend")
    plt.ylabel("Sales ($)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=None, help="Optional CSV with Week, Period, Sales columns.")
    args = parser.parse_args()

    rows = load_sales_from_csv(args.csv) if args.csv else DEFAULT_SALES
    analysis = analyze_sales(rows)

    Path("output_sales_analysis.json").write_text(json.dumps(analysis, indent=2))
    write_report(analysis, Path("output_sales_report.txt"))
    write_chart(rows, Path("output_weekly_sales_chart.png"))

    print("ReRock analysis complete.")
    print(f"Total sales: {money(analysis['total_sales'])}")
    print(f"Average weekly sales: {money(analysis['average_weekly_sales'])}")
    print(f"Latest week sales: {money(analysis['latest_week_sales'])}")
    print(
        "Latest lift vs baseline: "
        f"{money(analysis['latest_lift_vs_baseline'])} / "
        f"{pct(analysis['latest_lift_pct_vs_baseline'])}"
    )


if __name__ == "__main__":
    main()
