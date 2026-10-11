# v0.6.0 — distribution assets, drill-down, and the three value books

Since v0.5.0: the verification system gained its public distribution layer
and closed the two product gaps BP r32 named. Both package channels are now
live — this release ships to GitHub, PyPI, and npm in one push.

## Re-check one finding

`agentmeasure drilldown` replays a single conversation on screen: the row
exactly as the buyer exported it, every vendor rule step that fired in plain
language, the verdict with its three-state, the amount at issue, and the
exact command to reproduce it. The explanation walks the same branches as
the recount in the same order — a test replays the whole fixture through
both engines and asserts the verdicts agree, so the explanation and the
judgement cannot drift apart. This is the "ask the customer to re-check one
finding" promise, as an artifact.

## The third value book

Cash (recovery ledger) and hours (delivery journal) are joined by
`agentmeasure decisions`: an append-only journal of how the buyer used the
verification in a business decision — payment approved or held, discount
requested, renewal signed, vendor review. Types are enum-validated, entries
link back to the finding they rest on, outcomes are stated, and amounts are
context that is never summed with recovered cash. Three kinds of value,
three separate books.

## Distribution layer

- **Vendor rule cards** (website/rules/) — one public, linkable card per
  vendor: price, billing trigger, reopen handling, silence behaviour,
  closure timers, source link, registry version. Generated from the same
  registry the CLI and browser recount read, with a CI check so the page
  can never drift.
- **AMS-1 badges** (website/badges.html) — the four-stage adoption ladder
  as embeddable SVGs with markdown snippets, an adopters snapshot listing
  external conformance authors with links, and an explicit statement of
  what we refuse: no composite score, no A–F grade.
- The website now mirrors to gh-pages on every green CI run, so new pages
  ship themselves.

## Also in this release

Three new external conformance vectors/cards (iwasinnam-003 Metrecept
session-aggregate receipts; rksharma-001 contribution card; chenhz01-001 —
the first availability-certification vector, contributed via PR #32), a
release-smoke CI job that installs the built wheel into a fresh venv and
runs the first-user paths (`--version` / `demo` / `selftest`), and an
idempotent release workflow (PyPI and npm steps skip already-published
versions, so re-runs never fail).

466 tests. Zero runtime dependencies; no network code; judgement stays
100% rule-based; no message text is ever read.
