#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sum a BOM current column and check power-supply margin.

Purpose: power budget as a machine check. Reads a BOM CSV with a current
column and optional peak column, sums steady-state and peak current, then
compares against a rated supply current and a required margin.

CSV columns (header required):
  name, qty, current_ma (steady-state), peak_ma (optional)
  Accepted header variants: [part, count, current_ma, peak_ma],
  [component, quantity, ma, peak_ma], [name, qty, current, peak].
  Rows without numbers are skipped (comments/headers).

Exit codes: 0 = PASS, 1 = FAIL, 2 = input error.

Usage:
  python power_budget.py bom.csv --rated-ma 1000 [--margin 30]
"""

import argparse
import csv
import sys


def parse_bom(path):
    """Return (steady_total_ma, peak_total_ma, rows) or (None, None, err)."""
    steady, peak = 0.0, 0.0
    rows = []
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if header is None:
                return None, None, "empty file"
            header = [h.strip().lower() for h in header]
            name_idx = qty_idx = cur_idx = peak_idx = None
            for i, h in enumerate(header):
                if h in ("name", "part", "component", "item"):
                    name_idx = i
                elif h in ("qty", "quantity", "count"):
                    qty_idx = i
                elif h in ("current_ma", "ma", "current", "steady_ma"):
                    cur_idx = i
                elif h in ("peak_ma", "peak"):
                    peak_idx = i
            if name_idx is None or cur_idx is None:
                return None, None, f"header not recognized: {header}"
            for line_no, row in enumerate(reader, start=2):
                if not row or not row[0].strip():
                    continue
                name = row[name_idx].strip()
                try:
                    qty = float(row[qty_idx]) if qty_idx is not None and len(row) > qty_idx and row[qty_idx].strip() else 1.0
                    cur = float(row[cur_idx]) if len(row) > cur_idx and row[cur_idx].strip() else 0.0
                    p = float(row[peak_idx]) if peak_idx is not None and len(row) > peak_idx and row[peak_idx].strip() else 0.0
                except ValueError:
                    continue  # skip non-numeric rows
                steady += cur * qty
                if p:
                    peak += p * qty
                rows.append((name, qty, cur, p))
    except OSError as exc:
        return None, None, f"cannot read: {exc}"
    except csv.Error as exc:
        return None, None, f"csv error: {exc}"
    return steady, peak, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bom", help="path to BOM CSV")
    parser.add_argument("--rated-ma", type=float, required=True,
                        help="rated supply current in mA (e.g. LDO or USB 1000mA)")
    parser.add_argument("--margin", type=float, default=30.0,
                        help="required margin in percent (default 30)")
    args = parser.parse_args()

    steady, peak, rows = parse_bom(args.bom)
    if steady is None:
        print(f"ERROR BOM: {peak}")
        sys.exit(2)

    peak = peak if peak > steady else steady
    margin_pct = (args.rated_ma - peak) / args.rated_ma * 100.0

    print(f"steady-state total: {steady:.1f} mA")
    print(f"peak total:         {peak:.1f} mA")
    print(f"rated supply:       {args.rated_ma:.1f} mA")
    print(f"margin:             {margin_pct:.1f}% (required >= {args.margin:.1f}%)")

    if peak > args.rated_ma:
        print("RESULT: FAIL - peak exceeds rated supply")
        sys.exit(1)
    if margin_pct < args.margin:
        print("RESULT: FAIL - margin below required")
        sys.exit(1)

    print("RESULT: PASS - margin OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
