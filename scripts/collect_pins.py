#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compare pin usage between a netlist/CSV export and the board contract.

Purpose: machine-extract real pin assignments from an EDA export and diff them
against docs/board-contract.json, instead of letting the AI read text and
report PASS by itself (anti-hallucination layer).

Input files:
  1. netlist CSV: one row per net/pin, columns: net, pin (e.g. GPIO8), or
     columns: signal, function, pin. Header row required.
     Accepted header variants: [net, pin], [signal, function, pin],
     [net_name, pin_number], [signal_name, pin_name].
  2. board contract JSON: docs/board-contract.json with a "pins" section:
     {"pins": {"used": ["GPIO0", "GPIO19", "GPIO20", ...],
              "reserved": ["GPIO3", "GPIO45", "GPIO46"],
              "notes": "..."}}

Exit codes: 0 = PASS (no conflict), 1 = FAIL (conflict found), 2 = input error.

Usage:
  python collect_pins.py pins.netlist.csv docs/board-contract.json
"""

import argparse
import csv
import json
import re
import sys


def normalize_pin(name):
    """Normalize a pin label: GPIO8 -> GPIO8; GPIO 8 -> GPIO8; gpio8 -> GPIO8."""
    s = str(name).strip().upper()
    s = re.sub(r"\s+", "", s)
    return s


def parse_netlist(path):
    """Parse the netlist CSV, returning a list of (net, pin) tuples."""
    rows = []
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if header is None:
                return rows, "empty file"
            header = [h.strip().lower() for h in header]
            # Find column indices by accepted header names.
            pin_idx = None
            net_idx = None
            for i, h in enumerate(header):
                if h in ("pin", "pin_number", "pin_name", "pin num"):
                    pin_idx = i
                elif h in ("net", "net_name", "signal", "signal_name", "function"):
                    net_idx = i
            if pin_idx is None or net_idx is None:
                return rows, f"header not recognized: {header}"
            for line_no, row in enumerate(reader, start=2):
                if not row or not row[0].strip():
                    continue
                if len(row) <= max(pin_idx, net_idx):
                    return rows, f"row {line_no} has too few columns: {row}"
                net = row[net_idx].strip()
                pin = row[pin_idx].strip()
                if net and pin:
                    rows.append((net, normalize_pin(pin)))
    except OSError as exc:
        return rows, f"cannot read: {exc}"
    except csv.Error as exc:
        return rows, f"csv error: {exc}
    return rows, None


def load_contract(path):
    """Load board contract JSON and extract the pin usage set."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            contract = json.load(fh)
    except (json.JSONDecodeError, OSError) as exc:
        return None, f"cannot read contract: {exc}"
    pins = contract.get("pins", {})
    if not isinstance(pins, dict):
        return None, "contract 'pins' must be an object"
    used = pins.get("used", [])
    reserved = pins.get("reserved", [])
    if not isinstance(used, list) or not isinstance(reserved, list):
        return None, "contract 'pins.used' / 'pins.reserved' must be lists"
    return {
        "used": {normalize_pin(p) for p in used},
        "reserved": {normalize_pin(p) for p in reserved},
    }, None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("netlist", help="path to netlist CSV export")
    parser.add_argument("contract", help="path to board-contract.json")
    args = parser.parse_args()

    rows, err = parse_netlist(args.netlist)
    if err:
        print(f"ERROR netlist: {err}")
        sys.exit(2)
    pins, err = load_contract(args.contract)
    if err:
        print(f"ERROR contract: {err}")
        sys.exit(2)

    contract_pins = pins["used"] | pins["reserved"]
    conflicts = []
    seen = set()
    for net, pin in rows:
        if pin in seen:
            continue
        seen.add(pin)
        if pin in pins["reserved"]:
            conflicts.append((net, pin, "reserved"))
        elif pin in pins["used"]:
            pass  # expected usage
        else:
            conflicts.append((net, pin, "not-in-contract"))

    if conflicts:
        for net, pin, kind in conflicts:
            print(f"CONFLICT net={net} pin={pin} kind={kind}")
        print(f"SUMMARY: {len(conflicts)} pin conflict(s) between netlist and contract")
        sys.exit(1)

    print(f"PASS: all {len(seen)} pins in netlist are accounted for by the board contract")
    print(f"INFO: contract declares {len(contract_pins)} pins total (used+reserved)")
    sys.exit(0)


if __name__ == "__main__":
    main()
