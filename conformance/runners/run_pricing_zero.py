#!/usr/bin/env python3
"""Runner for pricing-explicit-zero vectors: fallback may apply only to absence, never to explicit 0.0."""
from __future__ import annotations

import json
import sys
from pathlib import Path

VECTORS_DIR = Path(__file__).resolve().parents[1] / "vectors"
FAIL = "FAIL"
PASS = "PASS"


def _simulate(inp: dict) -> dict:
    row, rule = inp["row"], inp["fallback_rule"]
    mult = 1.25 if rule == "1.25x_input_when_missing" else 1.0
    field_present = "cache_creation_input_token_cost" in row
    if inp["consumer"] == "or_fallback":
        # truthiness idiom: 0.0 or fallback -> fallback
        price = row.get("cache_creation_input_token_cost") or row["input_cost"] * mult
        repriced = field_present and row["cache_creation_input_token_cost"] == 0.0
        return {"price": price, "repriced": repriced, "inferred": not field_present}
    # in-check guard: explicit value (incl. 0.0) always wins; fallback only on absence
    if field_present:
        price = row["cache_creation_input_token_cost"]
        return {"price": price, "repriced": False, "inferred": False}
    return {"price": row["input_cost"] * mult, "repriced": False, "inferred": True}


def _check(vec: dict) -> bool:
    inp, exp, cid = vec["input"], vec["expect"], vec["id"]
    out = _simulate(inp)
    if cid == "pz-001a-or-fallback-reprice":
        return (abs(out["price"] - exp["effective_cache_creation_price"]) < 1e-15
                and out["repriced"] is exp["repriced_from_explicit_zero"]
                and exp["verdict"] == FAIL)
    if cid == "pz-001b-in-check-guard":
        return (out["price"] == 0.0 and out["repriced"] is False
                and exp["verdict"] == PASS)
    if cid == "pz-001c-absent-fallback-marked":
        return (abs(out["price"] - exp["effective_cache_creation_price"]) < 1e-15
                and out["inferred"] is True and out["repriced"] is False
                and exp["verdict"] == PASS)
    return False


def main() -> int:
    ok = total = 0
    for vec_file in sorted(VECTORS_DIR.glob("pricing-explicit-zero*.json")):
        data = json.loads(vec_file.read_text(encoding="utf-8"))
        for family in data["vectors"]:
            for vec in family["vectors"]:
                total += 1
                good = _check(vec)
                print(f"  {'✓' if good else '✗'} [{family['id']}] {vec['id']}")
                ok += good
    print(f"\n{ok}/{total} pricing-explicit-zero vectors {'PASS' if ok == total else 'FAILED'}")
    return 0 if ok == total else 1


if __name__ == "__main__":
    sys.exit(main())
