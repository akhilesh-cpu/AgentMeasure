# iwasinnam-005 — replay vector, claim boundary

Status: **cut 13 Oct 2026 from the live pipe (`api.metrecept.co.uk`, gateway
`iwasinnam2/ohm@b4d440e`), run tag `20261013b`.** Fixture:
`agentmeasure_iwasinnam_replay_fixture_005.json`. Cutting script:
`scripts/cut_agentmeasure_vectors.py`; CI pin: `tests/test_agentmeasure_vectors.py`.
Reserved by Roy Tong (AgentMeasure) as `conformance/vectors/external/iwasinnam-005`
on 2026-10-13; claim boundary ours to state, mapping theirs.

## What the run did

Five crossings on `model: mock`, one session tag.

JSON carriage:

| label | kind | plane | request_sha256 | response_sha256 |
|---|---|---|---|---|
| fill | `cache_miss` | python | R | S |
| replay | `cache_hit` | rust-edge | R (equal) | S (equal) |
| changed | `cache_miss` | python | R' (differs) | S' (differs) |

Streamed carriage (`stream: true`), one request sent twice:

| label | kind | chunks | request_sha256 | response_sha256 |
|---|---|---|---|---|
| fill | `cache_miss` | 15 | Q | T |
| replay | `cache_hit` | 5 | Q (equal) | T (equal) |

Two chunkings (15 and 5 data chunks) assembled by the published rule to one
completion with one digest.

## What the fixture claims

1. Every JWS verifies against the public key directory, `kid` = RFC 7638 thumbprint.
2. JSON fill and JSON replay carry one `request_sha256` and one
   `response_sha256`, signed by two different planes (`python`, `rust-edge`).
3. A stranger recomputes `response_sha256` from the served JSON body
   (`served_body` in the fixture) and from each stored SSE stream
   (`sse_lines`) with `open-repo/demo/response_digest.py` and gets the
   receipts' values. The receipt chunk that rides in the stream does not
   change the assembly.
4. The changed payload carries different request and response digests and
   its own `meter_event_id`.
5. Five crossings, five `meter_event_id`s. A replay is a distinct metered
   crossing: summed, never merged.
6. Each receipt is a leaf of the hour named under its `clock` block.

## What it does not claim

- That a **JSON** carriage and a **streamed** carriage of one stored body
  share a response digest. `response_sha256` names the completion *as
  served*; a stream drops provider extras the JSON body keeps, so the two
  carriages of one blob may honestly differ. This fixture compares JSON to
  JSON and stream to stream. If a synthetic vector treats the two carriages
  as one digest it is stronger than a live pipe can promise.
- Anything about the correctness of the completion.
- Provider cost.

## Mutation expectation

Change one byte of a served body or of a stream's content delta and the
stranger's digest leaves the receipt's; change the request and the records
separate. The signatures still verify on every mutated-input run, because the
receipt is honest about what it signed. Pinned in
`tests/test_agentmeasure_vectors.py::test_replay_fixture_mutation_leaves_the_receipt_digest`.

## Stranger's path

```bash
git clone https://github.com/iwasinnam2/metrecept-opensource
python metrecept-opensource/demo/verify_receipt.py "<raw_jws>" --base https://api.metrecept.co.uk
python metrecept-opensource/demo/response_digest.py served_body.json --receipt "<raw_jws>"
python metrecept-opensource/demo/response_digest.py --sse stream.txt --receipt "<raw_jws>"
```
