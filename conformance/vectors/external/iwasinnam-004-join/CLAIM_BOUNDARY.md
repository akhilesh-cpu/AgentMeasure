# iwasinnam-004 — join vector, claim boundary

Status: **cut 13 Oct 2026 from the live pipe (`api.metrecept.co.uk`, gateway
`iwasinnam2/ohm@b4d440e`), run tag `20261013b`.** Fixture:
`agentmeasure_iwasinnam_join_fixture_004.json`. Cutting script:
`scripts/cut_agentmeasure_vectors.py`; CI pin: `tests/test_agentmeasure_vectors.py`.
Reserved by Roy Tong (AgentMeasure) as `conformance/vectors/external/iwasinnam-004`
on 2026-10-13; claim boundary ours to state, mapping theirs.

## What the run did

One session id planted in `X-Metrecept-Session`. Four crossings on `model: mock`:

| n | tag | kind | plane | pipe_usd |
|---|-----|------|-------|----------|
| 1 | tagged | `cache_miss` (prompt A fills) | python | 0.0015 |
| 2 | tagged | `cache_hit` (prompt A, byte-identical, replayed) | rust-edge | 0.006 |
| 3 | tagged | `cache_miss` (prompt B, changed bytes) | python | 0.0015 |
| 4 | **untagged** | `cache_bypass` (`cache_control: no_store`, no session header) | python | 0.0015 |

Then one read of `GET /v1/sessions/<id>`: `event_count 3, cache_hits 1,
cache_misses 2, pipe_usd 0.009`.

## What the fixture claims

1. Every JWS verifies against the public key directory
   (`/.well-known/http-message-signatures-directory`), `kid` = RFC 7638 thumbprint.
2. `event_count == 3` = the number of tagged crossing receipts;
   `pipe_usd == 0.0015 + 0.006 + 0.0015`; per-kind counts equal the member kinds.
3. Crossing 4 is metered (own `meter_event_id`, `kind: cache_bypass`) and is
   **absent** from the aggregate. Its absence is the correct result; inventing
   it in would be the error. This is the 9 Oct 2026 shape from the other side.
4. Every member and the bypass carry distinct `meter_event_id`s: cover, not collapse.
5. `session_sha256 == sha256(planted id)`; the raw id is not in any signed payload.
6. Each receipt is a leaf of the hour named under its `clock` block
   (`/v1/public/clock/inclusion?receipt=<jws>` returns the proof). The hour's
   sealed/committed state is whatever the public clock shows at read time;
   `--refresh-clock` rewrites those blocks from the clock, never by hand.

## What it does not claim

- Anything about the model output. The receipt records the hop, not the work.
- Provider cost or avoided spend (not in any signed surface).
- Wall-clock truth of `iat` beyond the hour the clock seals.
- Anything about crossings the tenant made outside this run.

## Mutation expectation (the vector's teeth)

Drop a member, duplicate a member, change a member's `pipe_usd`, or insert the
untagged bypass into the member set: the join fails (count, sum, distinctness)
while the aggregate's own signature still verifies. **Signature is not the
join.** `tests/test_agentmeasure_vectors.py::test_join_fixture_mutations_fail_the_join_not_the_signature`
proves each case from the fixture alone.

## Stranger's path

```bash
git clone https://github.com/iwasinnam2/metrecept-opensource
python metrecept-opensource/demo/verify_receipt.py "<raw_jws>" --base https://api.metrecept.co.uk
curl "https://api.metrecept.co.uk/v1/public/clock/inclusion?receipt=<raw_jws>"
```
