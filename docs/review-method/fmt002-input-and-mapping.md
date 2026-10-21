# FMT-002 input & mapping — arbitrary event stream → conformance-ready JSONL

> The method behind shape B of a free measurement run. The mode follows the
> proven mapping-document practice (`conformance/vectors/external/` precedents).

## 1. Three intake verdicts (the answer to give before any work)

| Situation | Verdict | Note |
|---|---|---|
| Event grain: one call/attempt per line, stable id, outcome | **Accept** | Real session/task + operation/attempt ownership required; run only the invariants the fields support |
| Aggregate counts only (daily table / counters), no event stream | **Refuse** | Operation/retry invariants all UNPROVABLE — say so up front; that is a legitimate answer, not a failure |
| Half-events (call stream without operation ownership) | **Narrowed scope** | Cannot be mapped as-is; fix real ownership first — stated in advance, never discovered after |

## 2. FMT-002 minimum requirements (v1.0.0, schema at `lab/schemas/funnel-event.schema.json`)

- **11 envelope fields per line** (schema/schema_version auto): `event`,
  `experiment_id`, `assignment_id`, `harness_id`, `task_id`, `variant_id`,
  `replicate`, `subject_id`, `rules_version`. `assignment_id` must come from
  real session/task ownership — never a sample constant merging sessions.
- **5 event branches** (each line exactly one): `reach`→`candidate_ids`;
  `choice`→`selected_id`+`selected_subject`; `attempt`→`operation_index`,
  `attempt_index`, `outcome`, `steps`, `latency_ms`, `cost_units`;
  `operation_result`→`operation_index`, `outcome`, `attempts`;
  `consumption`→`operation_index`, `consumed`, `signal`.
- Minimal samples usually need just `attempt` + `operation_result` to support
  the three core invariants (execution-grain, retry-reconciliation,
  operation-grain).

## 3. The mapping table (`map.json`, fed to `scripts/map_to_fmt002.py`)

```json
{
  "identity_field": "session_id",
  "envelope": {
    "experiment_id": "acme-20261021",
    "harness_id": "acme-meter",
    "task_id": "sample",
    "variant_id": "default",
    "replicate": 1,
    "subject_id": "redacted",
    "rules_version": "acme/1.0"
  },
  "event_rules": [
    {
      "when": {"field": "type", "equals": "tool_call"},
      "event": "attempt",
      "map": {
        "operation_index": "op_seq", "attempt_index": "call_seq",
        "outcome": "status", "steps": "steps",
        "latency_ms": "latency_ms", "cost_units": "cost_usd"
      },
      "translate": {"outcome": {"failed": "failure", "succeeded": "success", "ok": "success"}}
    },
    {
      "when": {"field": "type", "equals": "op_close"},
      "event": "operation_result",
      "map": {"operation_index": "op_seq", "outcome": "status", "attempts": "n_calls"},
      "translate": {"outcome": {"failed": "failure", "succeeded": "success"}}
    }
  ]
}
```

- `map` values name source fields; `"@literal"` = a literal. `translate` =
  enum normalization (nearly every real source hits this step: your
  `succeeded/failed/ok` → schema's `success/failure/unresolved`).
- Integer fields auto-cast; `cost_units` keeps decimals (0.03 truncated to 0
  would fake cost-invariant UNPROVABLE — a rehearsed, real lesson).
- The mapper only moves and normalizes, **never infers**: any missing required
  field, duplicate identity, or schema error refuses the whole input and
  leaves the old output untouched — defects are handled by a human, never
  silently zero-filled.

## 4. The fixed four steps

1. Schema + first lines in → fill `map.json` (≈10 min).
2. `python3 scripts/map_to_fmt002.py --mapping map.json --input sample.jsonl --out fmt002.jsonl` — continue only on `dropped=0`.
3. `python3 conformance/pack/run_pack.py conformance --fixture fmt002.jsonl --claims claims.json --json res.json`.
4. Fill the report template; archive `map.json` for the requester's next sample.

## 5. Known boundaries

- Without a reported claims number, omit `--claims`: baseline adjudication,
  sample-internal consistency only — difference claims need claims.
- token-subset / cache-distinction are NOT-SUPPORTED on core FMT-002 — say it
  before the run, not after.
- operation-grain steps = **sum over all attempts of the operation (retries
  included)**; reporting only the successful attempt's steps is the canonical
  undercount shape.

## 6. Rule-coverage table

All mapped records pass the schema first; complete fields still don't
guarantee a PASS.

| Rule | Evidence needed | Verdict boundary |
|---|---|---|
| execution-grain | real assignment/operation/attempt identity, attempts + operation_result | Attempt/operation ownership within the sample; refuse mapping without real ownership |
| retry-reconciliation | the above + attempt_index + operation_result.attempts/outcome | Retry count vs declared final state |
| cost-preservation | attempt.cost_units + real operation ownership | Arithmetic conservation of input costs only — not price tables or invoices |
| operation-grain | attempt.steps + ownership; differences need claims | Operation-grain aggregation; baseline only without claims |
| token-subset / cache-distinction | semantics core FMT-002 does not carry | NOT-SUPPORTED |
