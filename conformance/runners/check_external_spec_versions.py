#!/usr/bin/env python3
"""External spec drift check — compares pinned spec versions against their live VERSION files.

Not part of CI (tests stay hermetic); run manually or weekly. Drift is not an error in itself —
it means a vector may be testing a moved spec; re-pin only after reading the changelog.
"""
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PINS = [
    ("chenhz01-001", "result-consumption-semantics",
     "https://raw.githubusercontent.com/chenhz01/result-consumption-semantics/main/VERSION"),
]

def main() -> int:
    drifted = 0
    for vec, spec, url in PINS:
        pin_file = ROOT / "conformance" / "vectors" / "external" / vec / "SPEC-VERSION"
        if not pin_file.exists():
            print(f"{vec}: no SPEC-VERSION pin (add one)")
            drifted += 1
            continue
        pinned = pin_file.read_text().splitlines()[0].strip()
        try:
            live = urllib.request.urlopen(url, timeout=15).read().decode().strip()
        except Exception as exc:
            print(f"{vec}: live fetch failed ({exc}); pinned={pinned}")
            continue
        status = "in sync" if pinned == live else "DRIFT"
        print(f"{vec} [{spec}]: pinned={pinned} live={live} -> {status}")
        if pinned != live:
            drifted += 1
    if drifted:
        print(f"\n{drifted} pin(s) drifted. Review the spec changelog before re-pinning.")
    return 1 if drifted else 0

if __name__ == "__main__":
    sys.exit(main())
