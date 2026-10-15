# Reconcile your vendor's bill every month, hands-free

This repo ships a GitHub Actions workflow (`Monthly bill reconcile`) that
re-counts an AI support bill under the vendor's own published rules on a
monthly schedule. Fork the repo, drop in your export, and the recount happens
by itself: GitHub Actions is the compute, there is no server, and nothing
leaves your fork.

## Setup (5 minutes, one time)

1. **Fork this repo.** A private fork keeps your export file to yourself.
2. **Copy the config template**:
   - `examples/reconcile.example.json` → `.agentmeasure/reconcile.json`
   - set `"vendor"` to your vendor's id — `agentmeasure recount --list-vendors`
     prints every id with its rule source (intercom, zendesk, hubspot, ada,
     salesforce, generic).
3. **Save your export** as `.agentmeasure/recount-export.csv` — the vendor's
   resolution-counts export with these columns (5 required, 2 optional):

   ```
   conversation_id, human_agent_participated, issue_addressed,
   customer_recontacted_within_window[, customer_recontacted_at, closed_at],
   vendor_billed
   ```

   `agentmeasure prepare --export <native export> --vendor <id>` maps a native
   Intercom or Zendesk export onto these columns; judgement columns stay empty
   for a human to review — the tool never invents a value.
4. **Commit both files** to your fork.
5. **Run it once manually**: your fork → Actions → *Monthly bill reconcile* →
   *Run workflow*. Confirm the report looks right, then let the schedule take
   over (3rd of each month, 09:00 UTC).

## What each run does

- Re-counts your export under the vendor's own published billing rules.
- Pins the full report to the run summary and uploads the machine-readable
  result (`recount-result.json`) as an artifact.
- When the net variance is not zero, opens (or updates) one tracking issue
  per state, so the finding cannot be forgotten.

## What it deliberately does not do

- It does not guess. Rows without enough evidence land in `cannot settle` and
  are removed from the claim, never zeroed.
- It does not call the vendor, request a refund, or assert wrongdoing. The
  variance is arithmetic under the vendor's own published rules — evidence for
  a conversation with the vendor, not a guaranteed refund. When you want the
  negotiable pack, `agentmeasure dispute` builds it.
- It does not upload anything anywhere. The report and the artifact live in
  your fork only.

## Cost

Zero. The workflow installs the CLI from PyPI on GitHub's runners and exits in
under a minute; the free tier's monthly minutes cover it comfortably.
