#!/usr/bin/env python3
"""Build a Mihomo domain/text list from HaGeZi exact + wildcard sources."""
from __future__ import annotations
import argparse
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/wildcard"
TIERS = ("light", "pro.mini", "pro")
DOMAIN_RE = re.compile(r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$", re.I)


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "flclash-hagezi-builder/1.0"})
    last = None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                if response.status != 200:
                    raise RuntimeError(f"HTTP {response.status}: {url}")
                return response.read().decode("utf-8-sig")
        except Exception as exc:  # network retry for CI reliability
            last = exc
            if attempt < 3:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def entries(text: str):
    for raw in text.splitlines():
        line = raw.strip().lower()
        if not line or line.startswith("#") or line.startswith("//"):
            continue
        yield line


def version(text: str) -> str:
    match = re.search(r"^# Version: (.+)$", text, re.M)
    return match.group(1).strip() if match else "unknown"


def build(tier: str) -> tuple[str, int, int]:
    exact_url = f"{BASE}/{tier}-onlydomains.txt"
    wildcard_url = f"{BASE}/{tier}.txt"
    exact_text = fetch(exact_url)
    wildcard_text = fetch(wildcard_url)
    exact = set()
    for domain in entries(exact_text):
        if not DOMAIN_RE.fullmatch(domain):
            raise RuntimeError(f"invalid exact domain in {exact_url}: {domain!r}")
        exact.add(domain)

    suffixes = set()
    for pattern in entries(wildcard_text):
        if not pattern.startswith("*.") or not DOMAIN_RE.fullmatch(pattern[2:]):
            raise RuntimeError(f"unexpected wildcard pattern in {wildcard_url}: {pattern!r}")
        suffixes.add("." + pattern[2:])  # Mihomo dot-prefix = subdomains only

    rules = sorted(exact | suffixes)
    header = [
        f"# Generated Mihomo domain/text rules from HaGeZi Multi {tier}",
        f"# Exact source: {exact_url}",
        f"# Exact version: {version(exact_text)}",
        f"# Wildcard source: {wildcard_url}",
        f"# Wildcard version: {version(wildcard_text)}",
        "# Mapping: bare domain = exact host; .domain = subdomains only",
        f"# Exact entries: {len(exact)}; subdomain entries: {len(suffixes)}; total unique rules: {len(rules)}",
        "# Do not edit by hand; run tools/build_hagezi.py",
        "",
    ]
    return "\n".join(header + rules) + "\n", len(exact), len(suffixes)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="rulesets")
    parser.add_argument("--tiers", nargs="+", choices=TIERS, default=list(TIERS))
    args = parser.parse_args()
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        for tier in args.tiers:
            payload, exact_count, suffix_count = build(tier)
            destination = out_dir / f"hagezi-{tier.replace('.', '-')}-mihomo.txt"
            temporary = destination.with_suffix(destination.suffix + ".tmp")
            temporary.write_text(payload, encoding="utf-8", newline="\n")
            temporary.replace(destination)
            print(f"{destination}: exact={exact_count}, subdomains={suffix_count}, bytes={destination.stat().st_size}")
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
