# Unknown model pricing — conformance case #34

## Purpose

A usage row with a model identifier that the pricing registry does not recognize must not inherit another model's price. The unknown row is visible and marked `UNPRICED` / `UNPROVABLE`; it must not be silently priced as zero or assigned a default model's rate.

This is a **synthetic, offline conformance fixture**. Rates below are deliberately test-only values, not published or current provider pricing.

## Run

From the repository root:

```bash
python3 conformance/evidence/unknown-model-pricing/run_case.py
```

The runner reads `fixture.jsonl` and checks `expected.json`. It uses the small explicit test registry in the expected outcomes to make the invariant independently reproducible without network access or a provider API.

## Fixture

The two JSONL records use the same token counts so their pricing outcomes are directly comparable:

- `known-model-001`: recognized test model, 1,000 input and 100 output tokens.
- `model-2099a`: deliberately unrecognized future model ID, same token counts.

The fixture uses a test-only registry rate of $2 per million input tokens and $8 per million output tokens for `known-model-001`. Its expected cost is `$0.0028`. No rate exists for `model-2099a`.

## Required outcomes

| Row | Verdict | Cost |
|---|---|---:|
| known model | `PRICED` | $0.0028 |
| unknown model | `UNPRICED` / `UNPROVABLE` | unavailable (not numeric zero) |

The unknown result must explicitly disclose the missing price. A numeric `0`, `0.0`, `$0.00`, the known model's cost, or any fallback-model cost is a conformance failure.

## What this runner proves

The runner is a compact executable oracle for the published case contract; it does not integrate with a third-party cost tracker. A real implementation can be tested against the same fixture by adapting its result into the documented outcome shape. The runner includes a deliberately faulty default-price fallback mutation and confirms that the mutation is rejected.

## Claim boundary

Synthetic test data only. The values do not represent live provider prices and do not assert that any named implementation currently has this behavior.
