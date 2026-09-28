#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check partition-table sizes against flash capacity and tensor arena vs PSRAM.

Exit codes: 0 = PASS, 1 = FAIL, 2 = input error.

Partition CSV format (like ESP-IDF partitions.csv):
  name,type,subtype,offset,size[,flags]
  offset may be empty (auto). Size values support K/M suffixes (e.g. 0x4000, 2M, 128K).

Tensor arena check: --tensor-arena-bytes must fit inside --psram-bytes with a
25% headroom recommendation (configurable via --tensor-headroom).

Usage:
  python check_flash_budget.py partitions.csv --flash-bytes 16M --psram-bytes 8M --tensor-arena-bytes 2M
"""

import argparse
import csv
import re
import sys


def parse_size(text):
    """Parse sizes like 0x4000, 4096, 2M, 128K into bytes. Returns None if invalid."""
    s = str(text).strip().upper()
    if not s:
        return None
    m = re.fullmatch(r"(0X[0-9A-F]+|\d+)([KM]?)", s)
    if not m:
        return None
    num = int(m.group(1), 0)
    mult = {"": 1, "K": 1024, "M": 1024 * 1024}[m.group(2)]
    return num * mult


def parse_partitions(path):
    """Return (entries, err). entries: list of (name, size_bytes)."""
    entries = []
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if header is None:
                return None, "empty file"
            header = [h.strip().lower() for h in header]
            if "size" not in header or "name" not in header:
                return None, f"header not recognized: {header}"
            size_idx = header.index("size")
            name_idx = header.index("name")
            for line_no, row in enumerate(reader, start=2):
                if not row or not row[0].strip() or row[0].strip().startswith("#"):
                    continue
                if len(row) <= max(size_idx, name_idx):
                    return None, f"row {line_no} too few columns: {row}"
                name = row[name_idx].strip()
                size = parse_size(row[size_idx])
                if size is None:
                    return None, f"row {line_no}: invalid size '{row[size_idx]}'"
                entries.append((name, size))
    except OSError as exc:
        return None, f"cannot read: {exc}"
    except csv.Error as exc:
        return None, f"csv error: {exc}"
    return entries, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("partitions", help="path to partitions CSV")
    parser.add_argument("--flash-bytes", required=True, help="flash capacity, e.g. 16M")
    parser.add_argument("--psram-bytes", required=True, help="PSRAM capacity, e.g. 8M")
    parser.add_argument("--tensor-arena-bytes", required=True, help="tensor arena size, e.g. 2M")
    parser.add_argument("--tensor-headroom", type=float, default=25.0,
                        help="required PSRAM headroom percent for tensor arena (default 25)")
    args = parser.parse_args()

    flash = parse_size(args.flash_bytes)
    psram = parse_size(args.psram_bytes)
    arena = parse_size(args.tensor_arena_bytes)
    if flash is None or psram is None or arena is None:
        print("ERROR: could not parse one of --flash-bytes/--psram-bytes/--tensor-arena-bytes")
        sys.exit(2)

    entries, err = parse_partitions(args.partitions)
    if entries is None:
        print(f"ERROR partitions: {err}")
        sys.exit(2)

    total = sum(sz for _, sz in entries)
    print(f"partition total:     {total} bytes ({total/1024/1024:.2f} MB)")
    print(f"flash capacity:      {flash} bytes ({flash/1024/1024:.2f} MB)")
    leftover = flash - total
    if leftover < 0:
        print(f"RESULT: FAIL - partitions exceed flash by {-leftover} bytes ({-leftover/1024:.1f} KB)")
        sys.exit(1)
    print(f"flash leftover:      {leftover} bytes ({leftover/1024/1024:.2f} MB)")

    arena_pct = arena / psram * 100.0
    print(f"tensor arena:        {arena} bytes = {arena_pct:.1f}% of PSRAM")
    if arena_pct > args.tensor_headroom:
        print(f"RESULT: FAIL - tensor arena uses {arena_pct:.1f}% of PSRAM, "
              f"above {args.tensor_headroom:.1f}% headroom guideline")
        sys.exit(1)

    print("RESULT: PASS - flash and PSRAM budgets OK")
    sys.exit(0)


if __name__ == "__main__":
    main()
