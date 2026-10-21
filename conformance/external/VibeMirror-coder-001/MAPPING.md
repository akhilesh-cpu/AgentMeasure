---

# VibeMirror-coder-001 — mapping note (five answers + claim boundary)

Provider: **VibeMirror-coder** (== chenhz01) — HumanMirror x402 MCP gateway, Base
Sample: `events.jsonl` — 56 canonical rows, `spec_version: agentmeasure-0.4`
Validated: `python3 schemas/validate_jsonl.py VibeMirror-coder-001.jsonl` → **exit 0 (56/56)**
Sidecar: `provider-native.jsonl` — 32 raw provider events (NOT canonical; does not pass the gate)
Submitted against: issue #6 (Path C — assisted mapping), onboarding doc `docs/provider-onboarding.md`

**Claim boundary (verbatim, as declared):** `synthetic, provider-side, Base x402`

---

## 1. What is one attempt on your surface?

**One tool request after a validated settlement.** A 402 challenge on its own is not an attempt.

- `payload.tool_call_id` = the provider's own request id (`exec-req-NN`)
- `attempt_started.observed_at` / `attempt_completed.observed_at` = the request lifecycle; `duration_ms` = the delta
- `outcome` from the enum: `success` / `failure` (`error_type: upstream_timeout`) / `unknown` (`error_type: unmapped_termination`)

**13 attempts** in the sample, matching **13 validated settlements**. Billable unit: *one validated x402 call*.
The two unpaid challenges produce **zero** attempts — they are `presentation` rows with no `selection`,
never inflated into attempts.

## 2. What groups attempts into one operation?

**Nothing does — and this is the finding, not a gap.** The gateway observes payer, tool, amount and
time, and **no buyer-side operation id**. Therefore:

- `operation_id` present on **0 of 13** rows
- `retry_of` present on **0 of 13** rows
- `operation_resolution_coverage` = **0.0**; every attempt resolves to `operation_resolution = unknown`

Two settlements from the same payer for the same tool inside the declared window are reported as
*"indistinguishable from two intended calls on this surface"* — **grouping UNPROVABLE** — not as a
double charge. This sample contains **2 such pairs** inside the 120s window, deliberately in two
different shapes: one failed-then-settled sequence, and one pair of two successes.

## 3. Where do retries hide on your surface?

They hide in the same place as operations: there is no retry field at the provider boundary. The
gateway sees a failed call (`exec-req-06`, `upstream_timeout`, 5000 ms) and a later settled call
(`exec-req-07`), and **nothing that says the later one was a retry of the earlier one**.

So `retry_of` is absent on all rows — **absent, not zero**. A report that prints
`retry_inflation = 0` has converted an unknown into a zero.

## 4. What is observable about the effect of a result?

**Nothing about consumption, and nothing about agent action.** The gateway returns an advisory and
separately observes whether a later action request arrives. It does not observe that the caller
read the advice, nor that any later action was influenced by it.

- **No `effect_confirmed` row and no `task_outcome` row is emitted** — a returned report does not establish agent action
- **`result_consumed` is absent, not zero** — the provider never sees the caller's next request
- For Safe Preflight: one `selection` row per advisory decision where a subsequent action by the same
  payer arrives inside the window; `decision_authority: unknown` and
  `selection_reason_observable: false` on every one

4 advisory decisions in this sample, **2 with an observed selection**. The other 2 have no
subsequent action inside the window, and silence is ambiguous — a deliberate hold, a departure, or a
slow caller. **2/4 must not be published as a selection rate**; the observed 2 are a lower bound.

## 5. What is the identity of the caller?

**Opaque.** The provider sees an MCP client and a payer wallet, not a chooser.

- `caller.type: unknown`, `identity_strength: unknown` on every row
- `decision_authority: unknown` on every selection row
- Only a hashed payer key is carried (`client_key`), per the guide

Whether the choice was made by a model, a workflow, a policy engine or a human is **not observable**.

---

## Shapes included (as requested)

| Shape | Present |
|---|---|
| Clean chain: challenge → settlement → request → report returned | ✅ 13 |
| Challenge with no settlement (abandoned at payment) | ✅ 2 (`pay-02`, `pay-13`) |
| Validated settlement → failed/timed-out request → retry | ✅ `exec-req-06` (timeout) → `exec-req-07` (settled again) |
| Selection row per advisory decision (Safe Preflight) | ✅ 4 decisions, 2 observed selections |

**On the retry shape specifically:** yes, the retry required a **second settlement**. On a per-call
billable unit that is the double-billing case the audit tracks — and on this surface it is
**indistinguishable from two intended calls**, so it is reported as grouping UNPROVABLE rather than
as an overcharge.

## Row inventory

| Type | Count |
|---|---|
| `presentation` | 15 |
| `selection` | 15 |
| `attempt_started` | 13 |
| `attempt_completed` | 13 |
| `result_consumed` | 0 (absent, not zero) |
| `task_outcome` | 0 (absent, not zero) |

Attempt outcomes: 11 `success`, 1 `failure`, 1 `unknown`.
Two prices, both from the provider-native log and never invented: 0.001 USDC
(`mcp_tool:humanmirror.safe_preflight`), 0.002 USDC (`mcp_tool:humanmirror.action.release`).
Per-tool revenue 0.004 and 0.018; total **0.022 USDC on Base**. Two payers, hashed.

## Optional note 1 — unpaid challenges: which shape I chose

I took the **rows** option, not the mapping-note aggregate: a `presentation` row per challenge (the
decision point — terms shown), a `selection` row only when a settlement is actually validated, and
`attempt_started` / `attempt_completed` on the settled call. Reason: the aggregate makes the funnel
shape invisible to the checker, and the funnel is one of the things worth being able to see.

## Optional note 2 — second payments

See §2. The two same-payer same-tool pairs inside the 120s window are carried in the rows, and the
**absence of any linking field is itself carried in the rows** (`operation_id` 0/13, `retry_of` 0/13,
coverage 0.0). That is what makes grouping UNPROVABLE measurable here rather than asserted.

## Must not invent

- no default price — every amount comes from the provider-native log
- no zero for absence — unresolved grouping stays UNPROVABLE, never 0
- no fabricated identity — `caller.type` / `decision_authority` stay unknown
- no outcome upgrade — a returned report never becomes `effect_confirmed` or `task_outcome`
- no double-charge claim — a repeated settlement is grouping UNPROVABLE, never an overcharge
- no settlement invented for an unpaid challenge — an unpaid challenge carries a presentation and nothing else

## Negative results policy

A report that disagrees with any `must_assert` value in `expected.json` is a finding about my mapping
or your measurement — either is welcome; both are more useful than agreement.
