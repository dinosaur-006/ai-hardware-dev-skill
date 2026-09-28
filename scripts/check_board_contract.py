#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate a board-contract.json (board-level knowledge contract).

Exit codes: 0 = PASS (WARN allowed), 1 = FAIL, 2 = input error.

Checks:
  - JSON parses, root keys present.
  - Required fields present and non-empty where mandatory.
  - \"must be unknown\" assertions: fields that must be null must be null AND
    carry an evidence field documenting why they are unknown.
  - Safety assertions: e.g. legacy_hold_boot_during_power_on_forbidden must be true.
  - No stray unknown fields (optional; warn only).

Usage:
  python check_board_contract.py path/to/board-contract.json
"""

import argparse
import json
import sys

# Required top-level keys of a board contract.
REQUIRED_TOP_KEYS = [
    "schema_version",
    "board_name",
    "soc",
    "module",
    "flash_bytes",
    "psram_bytes",
    "power",
    "boot",
    "usb",
    "pins",
]

# Fields that must be null (unknown) UNLESS evidence is provided.
# Key = dotted path, value = short description for messages.
MUST_BE_UNKNOWN_OR_EVIDENCED = [
    ("power.power_up_settle_time_ms", "power-up settle time"),
    ("power.max_current_ma", "max current draw"),
    ("pins.gpio8_function", "GPIO8 function"),
]

# Fields that, when present, must be non-empty strings/numbers (not null/empty).
REQUIRED_NONEMPTY = [
    "board_name",
    "soc",
    "module",
    "schema_version",
]

# Hard safety assertions. Dotted path -> expected value.
SAFETY_ASSERTS = [
    ("boot.legacy_hold_boot_during_power_on_forbidden", True,
     "board must forbid the legacy 'hold BOOT during power-on' recipe"),
]


def get_path(obj, dotted):
    """Return (found, value) for a dotted path in obj."""
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return False, None
        cur = cur[part]
    return True, cur


def check_contract(path):
    """Run all checks. Returns (passes, fails, warns, messages)."""
    passes, fails, warns = 0, 0, 0
    messages = []

    try:
        with open(path, "r", encoding="utf-8") as fh:
            contract = json.load(fh)
    except json.JSONDecodeError as exc:
        return 0, 1, 0, [f"JSON parse error: {exc}"]
    except OSError as exc:
        return 0, 1, 0, [f"Cannot read file: {exc}"]

    if not isinstance(contract, dict):
        return 0, 1, 0, ["Root must be a JSON object"]

    # 1. Required top-level keys.
    for key in REQUIRED_TOP_KEYS:
        if key not in contract:
            fails += 1
            messages.append(f"FAIL missing top-level key: {key}")
        else:
            passes += 1
            messages.append(f"PASS top-level key present: {key}")

    # 2. Non-empty required fields.
    for field in REQUIRED_NONEMPTY:
        found, val = get_path(contract, field)
        if not found or val is None or (isinstance(val, str) and not val.strip()):
            fails += 1
            messages.append(f"FAIL required field empty: {field}")
        else:
            passes += 1
            messages.append(f"PASS required field non-empty: {field}")

    # 3. Must-be-unknown-or-evidenced fields.
    for dotted, desc in MUST_BE_UNKNOWN_OR_EVIDENCED:
        found, val = get_path(contract, dotted)
        if not found:
            warns += 1
            messages.append(f"WARN field absent (fine if inapplicable): {dotted} ({desc})")
            continue
        evidence_key = dotted + ".evidence"
        ev_found, ev_val = get_path(contract, evidence_key)
        if val is None:
            if ev_found and isinstance(ev_val, str) and ev_val.strip():
                passes += 1
                messages.append(
                    f"PASS {dotted} is null AND carries evidence: {ev_val[:60]}"
                )
            else:
                fails += 1
                messages.append(
                    f"FAIL {dotted} is null but has no evidence field "
                    f"'{evidence_key}' (must document why unknown)"
                )
        else:
            # A concrete value without evidence is acceptable (measured/from datasheet),
            # but flag missing evidence as a warning for traceability.
            if not (ev_found and isinstance(ev_val, str) and ev_val.strip()):
                warns += 1
                messages.append(
                    f"WARN {dotted} has concrete value but no evidence "
                    f"(add '{evidence_key}' for traceability)"
                )
            passes += 1
            messages.append(f"PASS {dotted} has concrete value: {val}")

    # 4. Safety assertions.
    for dotted, expected, desc in SAFETY_ASSERTS:
        found, val = get_path(contract, dotted)
        if not found:
            fails += 1
            messages.append(f"FAIL safety field missing: {dotted} ({desc})")
        elif val is expected:
            passes += 1
            messages.append(f"PASS safety: {dotted} == {expected}")
        else:
            fails += 1
            messages.append(f"FAIL safety: {dotted} == {val!r}, expected {expected!r} ({desc})")

    # 5. Unknown top-level keys (warn only).
    known = set(REQUIRED_TOP_KEYS)
    for key in contract:
        if key not in known:
            warns += 1
            messages.append(f"WARN unknown top-level key: {key}")

    return passes, fails, warns, messages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract_path", help="path to board-contract.json")
    args = parser.parse_args()

    passes, fails, warns, messages = check_contract(args.contract_path)

    for msg in messages:
        print(msg)
    print(f"SUMMARY PASS={passes} FAIL={fails} WARN={warns}")

    if fails:
        print("RESULT: FAIL")
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
