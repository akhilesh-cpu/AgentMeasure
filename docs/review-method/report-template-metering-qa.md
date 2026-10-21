# Metering QA check — report template (free run)

> Deliver the whole report to the requester; `【】` marks required fields.
> Every verdict binds to the invariant that produced it; NOT-SUPPORTED is
> reported as-is.

---

**Metering QA Check — run 【run id】 · 【date】**

## 0. Scope and decision

- The requester's decision and agreed question:【】
- What the free pack already answered:【】
- Added human work in this run:【field-mapping review / rule applicability / declared-number comparison】
- The actual mapping, field sources, unmappable items:【attach rerunnable material; never guess operation ownership】

## 1. Sample and rules

- Sample:【event count, time window, source system, sanitization policy】.
- The requester's reported numbers (claims):【JSON verbatim, e.g. {"median_steps_per_operation": 5.0}】.
- Rules: the FMT-002 invariant set (same vocabulary as the public claims index: PASS / FAIL / UNPROVABLE).

## 2. Verdict table

| Invariant | Verdict | Basis (recomputation reference) |
|---|---|---|
| execution-grain | 【PASS/FAIL/UNPROVABLE】 | 【e.g. operations=2, attempts=4, attempts_per_operation=2.0】 |
| retry-reconciliation | 【…】 | 【declared/reconciled/failed】 |
| operation-grain | 【…】 | 【recomputed vs claimed + grain】 |
| cost-preservation | 【…】 | 【arithmetic conservation recomputation】 |
| evidence-boundary | 【…】 | 【decidability_coverage etc.】 |
| token-subset / cache-distinction | 【NOT-SUPPORTED: name the missing fields】 | — |

**Total difference**:【any FAIL → what differs, by how much, at which grain; no FAIL → no finding: the sample is internally consistent across the checked invariants】.

## 3. Actual errors (only if any FAIL)

- Reproduction:【minimal event sequence or construction steps the requester can replay】.
- Fix direction on the requester's side:【…】.

## 4. What you can rerun yourself

```bash
# 【the exact command line of this run, including --fixture/--claims/--json】
```

Exit codes: 0 = no FAIL; 1 = FAIL or a required invariant not PROVEN; 2 = input error.

## 5. Evidence boundary

- Not covered:【e.g. core events carry no token fields → token-subset NOT-SUPPORTED】.
- This report does not judge pricing or commercial terms — only whether the
  numbers and the event stream agree.

---
*Subsets never summed · UNPROVABLE is a result, not an error. If the check was
useful, a star on the repo helps others find it — never required, never a condition.*
