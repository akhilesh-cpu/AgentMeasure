#!/usr/bin/env python3
"""Executable conformance case for unknown model IDs inheriting a default price.

Run from the repository root:
    python3 conformance/evidence/unknown-model-pricing/run_case.py

This is an offline contract/oracle, not an adapter to a vendor cost tracker.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.jsonl"
EXPECTED = HERE / "expected.json"


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path.name}:{line_number}: each JSONL row must be an object")
        rows.append(row)
    return rows


def price_row(row: dict, registry: dict) -> dict:
    """Reference behavior: price known IDs; abstain for unknown IDs."""
    model_id = row.get("model_id")
    rate = registry.get(model_id)
    if rate is None:
        return {
            "row_id": row.get("row_id"),
            "model_id": model_id,
            "verdict": "UNPRICED",
            "cost_usd": None,
            "reason": "unknown_model_id; no registered price",
        }

    cost = (
        row["input_tokens"] * rate["input_usd_per_million_tokens"]
        + row["output_tokens"] * rate["output_usd_per_million_tokens"]
    ) / 1_000_000
    return {
        "row_id": row.get("row_id"),
        "model_id": model_id,
        "verdict": "PRICED",
        "cost_usd": round(cost, 10),
    }


def reject_silent_or_fallback_pricing(result: dict, expected: dict) -> list[str]:
    errors = []
    verdict = str(result.get("verdict", "")).upper()
    cost = result.get("cost_usd")

    if verdict not in {"UNPRICED", "UNPROVABLE"}:
        errors.append(f"unknown row verdict must be UNPRICED/UNPROVABLE, got {verdict!r}")
    if cost is not None:
        if isinstance(cost, bool) or not isinstance(cost, (int, float)):
            errors.append(f"unknown row cost must be unavailable/null, got {cost!r}")
        elif not math.isfinite(cost) or cost == 0:
            errors.append(f"unknown row must not render a numeric zero cost, got {cost!r}")
        else:
            errors.append(f"unknown row must not inherit a fallback price, got {cost!r}")
    if result.get("row_id") != expected["row_id"]:
        errors.append("unknown row_id does not match the expected row")
    if result.get("model_id") != expected["model_id"]:
        errors.append("unknown model_id does not match the expected future ID")
    return errors


def main() -> int:
    fixture = load_jsonl(FIXTURE)
    contract = json.loads(EXPECTED.read_text(encoding="utf-8"))
    expected_rows = contract["expected"]
    registry = contract["test_registry"]

    if len(fixture) != 2:
        print(f"FAIL: expected exactly 2 JSONL rows, found {len(fixture)}")
        return 1
    if len(expected_rows) != 2:
        print("FAIL: expected.json must define exactly 2 outcomes")
        return 1

    results = [price_row(row, registry) for row in fixture]
    known, unknown = results
    expected_known, expected_unknown = expected_rows

    known_ok = (
        known.get("row_id") == expected_known["row_id"]
        and known.get("model_id") == expected_known["model_id"]
        and known.get("verdict") == expected_known["verdict"]
        and isinstance(known.get("cost_usd"), (int, float))
        and not isinstance(known.get("cost_usd"), bool)
        and math.isclose(known["cost_usd"], expected_known["cost_usd"], rel_tol=0, abs_tol=1e-12)
    )
    if known_ok:
        print("PASS known model: priced at the registered synthetic test rate ($0.0028)")
    else:
        print(f"FAIL known model: expected {expected_known}, got {known}")

    unknown_errors = reject_silent_or_fallback_pricing(unknown, expected_unknown)
    if not unknown_errors and unknown.get("reason"):
        print("PASS unknown model: explicitly UNPRICED, with no numeric cost")
    else:
        print("FAIL unknown model:")
        for error in unknown_errors or ["unknown model outcome must disclose a reason"]:
            print(f"  - {error}")

    # Mutation test: emulate the bug described in #34 by assigning the unknown
    # row the known model's rate. The contract must reject that output.
    faulty = {
        "row_id": unknown["row_id"],
        "model_id": unknown["model_id"],
        "verdict": "PRICED",
        "cost_usd": known["cost_usd"],
        "reason": "fault injection: default-model fallback",
    }
    mutation_errors = reject_silent_or_fallback_pricing(faulty, expected_unknown)
    if mutation_errors:
        print("PASS mutation guard: default-model fallback is rejected")
    else:
        print("FAIL mutation guard: a fallback-priced unknown model was accepted")

    # Another mutation: a silent $0.00 output must also be rejected.
    zero_mutation = {
        "row_id": unknown["row_id"],
        "model_id": unknown["model_id"],
        "verdict": "PRICED",
        "cost_usd": 0.0,
    }
    zero_errors = reject_silent_or_fallback_pricing(zero_mutation, expected_unknown)
    if zero_errors:
        print("PASS mutation guard: silent zero cost is rejected")
    else:
        print("FAIL mutation guard: a zero-priced unknown model was accepted")

    ok = known_ok and not unknown_errors and bool(unknown.get("reason")) and bool(mutation_errors) and bool(zero_errors)
    print("\nCONFORMANT" if ok else "\nNON-CONFORMANT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
