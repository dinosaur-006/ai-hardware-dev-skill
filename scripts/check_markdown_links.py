#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scan Markdown files for dead links (local and remote).

Purpose: keep the Skill's own references healthy. Local links are checked
against the filesystem; remote links are checked with a HEAD request.

Rules:
  - Skip links that are placeholder tokens like <board-contract:...> or
    <你的...> or URLs containing 'xxx'.
  - --skip-hosts accepts a comma-separated list of hosts to skip
    (e.g. waytoagi.feishu.cn which requires login).
  - Remote check uses urllib; failures mark the link broken unless skipped.

Exit codes: 0 = all OK (or only skipped), 1 = broken links found, 2 = input error.

Usage:
  python check_markdown_links.py README.md [more.md ...] [--skip-hosts host1,host2]
"""

import argparse
import os
import re
import sys
import urllib.request

LINK_RE = re.compile(r"\]\\(([^)\\s]+)(?:\s+\"[^\"]*\"\\)?\\)")
PLACEHOLDER_MARKERS = ("board-contract:", "<你的", "xxx", "<项目根目录>", "<你的项目目录>")


def is_placeholder(url):
    return any(m in url for m in PLACEHOLDER_MARKERS) or url.startswith("<")


def check_local(url, base_dir):
    """Return True if local relative link resolves."""
    path = os.path.normpath(os.path.join(base_dir, url))
    return os.path.exists(path)


def check_remote(url):
    """Return (ok, note). Uses GET with a short timeout; accepts 2xx/3xx."""
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "skill-link-check"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            code = resp.getcode()
            return 200 <= code < 400, f"HTTP {code}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


def scan_file(path, skip_hosts):
    """Scan one markdown file. Returns (broken, checked, skipped)."""
    broken, checked, skipped = [], 0, 0
    base_dir = os.path.dirname(path) or "."
    try:
        with open(path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        return [(f"(file read error)", str(exc))], 0, 0

    for m in LINK_RE.finditer(text):
        url = m.group(1).strip()
        if is_placeholder(url):
            skipped += 1
            continue
        if url.startswith(("http://", "https://")):
            host = url.split("/")[2] if "/" in url[8:] else url
            if host in skip_hosts:
                skipped += 1
                continue
            ok, note = check_remote(url)
            checked += 1
            if not ok:
                broken.append((url, note))
        elif url.startswith("#"):
            skipped += 1  # in-page anchor; not checked here
        else:
            if check_local(url, base_dir):
                checked += 1
            else:
                broken.append((url, "local file not found"))
    return broken, checked, skipped


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="markdown files to scan")
    parser.add_argument("--skip-hosts", default="",
                        help="comma-separated hosts to skip (e.g. waytoagi.feishu.cn)")
    args = parser.parse_args()

    skip_hosts = {h.strip() for h in args.skip_hosts.split(",") if h.strip()}
    all_broken = []
    total_checked = total_skipped = 0
    for path in args.files:
        if not os.path.isfile(path):
            print(f"ERROR: file not found: {path}")
            sys.exit(2)
        broken, checked, skipped = scan_file(path, skip_hosts)
        total_checked += checked
        total_skipped += skipped
        print(f"{path}: checked={checked} skipped={skipped} broken={len(broken)}")
        all_broken.extend(broken)

    for url, note in all_broken:
        print(f"BROKEN: {url}  ({note})")

    if all_broken:
        print(f"RESULT: FAIL - {len(all_broken)} broken link(s)")
        sys.exit(1)
    print(f"RESULT: PASS - {total_checked} links checked, {total_skipped} skipped")
    sys.exit(0)


if __name__ == "__main__":
    main()
