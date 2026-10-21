---

# chenhz01-001 — mapping note (five answers + claim boundary)

Provider: **chenhz01** (single-user local agent runtime, Guangzhou)
Sample: `chenhz01-001.events.jsonl` — 74 canonical rows, `spec_version: agentmeasure-0.4`
Validated: `python3 schemas/validate_jsonl.py chenhz01-001.events.jsonl` → exit 0 (74/74)
Submitted against: issue #6 (path A — raw JSONL), onboarding doc `docs/provider-onboarding.md`

---

## 1. What is one attempt on your surface?

**One tool invocation** — a `function_call` event and its paired `function_call_result`,
identified by the runtime's own `callId`.

- `payload.tool_call_id = "tc-" + sha256(callId)[:16]` (hashed; the raw call id is runtime-internal)
- `attempt_started.observed_at` = `function_call.timestamp`
- `attempt_completed.observed_at` = `function_call_result.timestamp`; `duration_ms` = the delta
- `outcome` = `success` when a result body exists, `failure` with `error_type: user_interrupt`
  when the runtime recorded `error.message == "Interrupted by user"`

22 attempts in the sample window. One `failure` (the user interrupt), 21 `success`.

## 2. What groups attempts into one operation?

**The billed model request** — `conversationRequestId` (== `traceId` on every row in this runtime),
emitted as `operation_id = op-req-<seq>`. 22 attempts fall inside 2 operations (7 + 15).

This is deliberately the *billing* grain, not the "logical task" grain: it is the grouping my
surface can actually observe. Anything finer (e.g. "these three calls were one logical edit")
is not observable here and is not claimed.

## 3. Where do retries hide on your surface?

**They do not hide — they are never labelled, which is worse.** The runtime has no retry field.
Repeated invocations are *observable as duplicate executions* (same tool, same turn, adjacent),
but whether a duplicate is a retry of the previous attempt is an interpretation, not an
observation.

Per the honest-absence discipline: **no row carries `retry_of` (0/22).** I am not asserting
"zero retries"; I am asserting "retry linkage is UNPROVABLE here". If AgentMeasure wants a
derived rule (duplicate-adjacency ⇒ retry), that is your call to make and the fixture will
accept it — but it should be recorded as a derived rule, not read off my rows.

## 4. Can you see outcomes?

- **Attempt outcomes: yes** (result body present / interrupt recorded).
- **Task outcome: only self-attested.** The sample carries one `task_outcome` with
  `outcome_class: assumed_resolved` and `outcome_observer_grade: self_attested`.
  Nothing external corroborates it. I did not map `resolved`.
- **Result consumption: partially, and the boundary is the interesting part.** I emit
  `result_consumed` only where a tool result is followed by a later model request with
  **no context-compaction boundary in between**. Where a compaction boundary intervenes, the
  result may have been evicted from the context that built the next request — so inclusion is
  unprovable and the row is **absent**: 7 emitted, 15 withheld.

  That asymmetry is the finding I am most interested in your read on: on this surface,
  *availability of a tool result to a later model call is not a property of the result — it is a
  property of whether a compaction ran in between.* It is the runtime analogue of the
  availability/influence split discussed in #11.

## 5. What do you bill on?

**Per model request, token-metered** (`usage.requests` / `inputTokens` / `outputTokens` per
request). Not per tool call, not per resolution.

Consequence, stated against my own billable unit: **22 attempts executed inside 2 billed
requests.** Any per-attempt reading of this window inflates my billable unit by ~11x. That is an
inflation finding I am reporting against myself, not a complaint.

---

## Claim boundary

**Production-derived.** Sourced from a real local agent session on my own machine (a working
session, not a staged run), window = a contiguous slice of 22 attempts chosen **because it is
where the session's only user-interrupt occurred**. Not selected for clean shapes — the failure
and the compaction gap are in it on purpose.

**Anonymization:** no payload content, no file paths, no command text, no prompt or response
bodies leave the machine. Tool *names* are retained (`mcp_tool:bash`, `mcp_tool:write`,
`mcp_tool:read`, `mcp_tool:edit`) because surface identity is the point of the exercise; call
ids, session id and project id are SHA-256 hashed with a fixed local salt. Timestamps are real
and in UTC — they carry no content, and the duration/grain findings depend on them.

**What this sample is NOT:** not a conformance pass, not a claim about AgentMeasure's
correctness, not evidence about anyone else's metering. It is one surface, described as
honestly as I can describe it, offered so the measurement layer can disagree with me in public.

## Three things I chose not to emit

| Not emitted | Why |
|---|---|
| `presentation` rows | I see the call the model issued, not the tool list shown to it. Emitting a `candidate_set_id` would be inventing identity. |
| `retry_of` | Duplicate execution is observable; "retry" is an interpretation. |
| `result_consumed` across compaction | Inclusion in the next request payload is unprovable there. Absence = unknown, not "not consumed". |

## Reproduction / provenance

- Source: local runtime session transcript (JSONL), `type: function_call` / `function_call_result` pairs
- Mapper: deterministic; re-running on the same transcript reproduces byte-identical rows
- Envelope validation: `schemas/validate_jsonl.py` → exit 0 (74/74)
- Expected verdicts: `chenhz01-001.expected.json` — four `must_report_unprovable` entries and
  four `must_not_invent` entries; disagreement with any `must_assert` value is a welcome finding

---
