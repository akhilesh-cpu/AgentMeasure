# AgentMeasure

**Every usage- or outcome-billed AI invoice should be independently re-countable by the party paying it — in one command.**

AgentMeasure re-counts an AI support bill against the vendor's own published
billing rules, prints the dollar variance, and builds the evidence pack you
can put in front of the vendor. It runs locally; nothing uploads.

[Website](https://roy-tong.github.io/AgentMeasure/) · [中文](README.zh-CN.md) · [Healthcheck guide](healthcheck/README.md) · [Release notes](https://roy-tong.github.io/AgentMeasure/releases.html)

## Re-count a bill in 60 seconds

Save this five-line sample as `export.csv` (synthetic data, real command):

```csv
conversation_id,human_agent_participated,issue_addressed,customer_recontacted_within_window,vendor_billed
c-001,N,Y,N,Y
c-002,N,Y,N,Y
c-003,N,Y,N,Y
c-004,Y,Y,N,Y
c-005,N,Y,Y,Y
```

```bash
pip install agentmeasure
agentmeasure recount --export export.csv --vendor zendesk
```

The output prints the vendor's rule with its public source, findings in both
directions, then the dollars:

```
billed $10.00 · net overcharge $2.00 · at USD 2.0/resolution
...
Dollars (at USD 2.0 per resolution)
overcharge identified       2.00
undercharge (vendor favour) 0.00
net variance                2.00
```

No CSV at hand yet? `agentmeasure recount --sample` runs the bundled 5-row
synthetic export with the Zendesk rule set — the same file as above.

Three reproducible showcase cases (overcharge with refused guesses, findings
in both directions, the contract lane) live in
[examples/showcase](examples/showcase/README.md) with frozen expected outputs
that CI compares on every change.

## Reconcile monthly, hands-free

Fork this repo, drop your vendor export into `.agentmeasure/`, and the
[Monthly bill reconcile](.github/workflows/reconcile.yml) workflow re-counts
your bill on a schedule — GitHub Actions is the compute, no server, nothing
leaves your fork, and a non-zero variance opens a tracking issue so the
finding cannot be forgotten. Setup is five minutes:
[RECONCILE.md](RECONCILE.md).

Six vendor rule sets ship today — Intercom Fin, Zendesk AI Agents, HubSpot
Breeze, Salesforce Agentforce, Ada and a generic per-resolution baseline —
each citing its source and confidence grade
(`agentmeasure recount --list-vendors`). When a recount disagrees with the
invoice: `agentmeasure prepare` maps a native Intercom or Zendesk export onto
the canonical columns, `agentmeasure dispute` builds the Dispute & Recovery
Pack, and `agentmeasure recovery` records what the vendor actually conceded,
counted separately from the claim.

A recount is arithmetic, not a verdict: rows without enough evidence land in
`cannot settle` and are removed from the claim, never zeroed. "No finding" is
a valid outcome. Vendor recounting is a free CLI capability, not one of the
two paid services below.

## Start with your own machine (free)

`agentmeasure check` inspects your local Codex / Claude Code sessions for
duplicate records, retry amplification and token anomalies — the same evidence
discipline pointed at your own logs. `agentmeasure demo` runs a bundled
synthetic session with no account and no upload. Missing evidence stays
unknown; a retry is not automatically a second logical operation.

Python 3.9+. CLI **0.7.2** on [PyPI](https://pypi.org/project/agentmeasure/);
Provider SDK **0.2.0** on [npm](https://www.npmjs.com/package/@agentmeasure/mcp),
verified 2026-10-15. These packages have separate version numbers.
On macOS/Linux use `python3 -m pip` if needed; on Windows use `py -m pip`.
For permission or
“externally managed” errors, use the [virtual-environment instructions](https://roy-tong.github.io/AgentMeasure/#install-help).
With both runtimes present, auto-discovery prefers Codex; use
`agentmeasure check --runtime claude` for Claude Code. No logs in the default
seven-day window? Try `--all` or an explicit `--dir` and `--runtime`. A missing
input is not a passing check. [More recovery steps](https://roy-tong.github.io/AgentMeasure/#how).

## Get help with one question

| Option | Price | What you get |
|---|---|---|
| Run the open-source tools | Free | Local Healthcheck, conformance checks, SDK and published rules |
| Healthcheck Diagnosis | **$10** | One anomaly on one machine: interpretation of your sanitized summary, evidence limits and next checks |
| Metering QA | **$20** | One event sample, one ruleset and one metering question: supported checks, findings and a rerun command |

[See scope, input requirements and apply by email](https://roy-tong.github.io/AgentMeasure/services.html).
No subscription or sales call. First response within 24 hours. Delivery within
24 hours after payment, fit approval and complete input; queue changes are agreed
before payment. A confirmation reserves a place; it does not start paid work.
Card checkout is being set up; applications and price acceptance are separate from payment.

**$10:** counts alone support interpretation and general triage. Specific
troubleshooting needs an optional manually redacted error excerpt; a root cause
is not guaranteed. **$20:** fit is checked free before payment. Core FMT-002
checks operation/attempt accounting and sample cost conservation; it does not
verify token/cache semantics, vendor invoices or pricing accuracy.

To prepare a summary locally:

```bash
agentmeasure check --json report.json
agentmeasure share report.json --out summary.json
agentmeasure validate summary.json
```

`--out` writes immediately on your machine. Inspect the file before you choose to
send it. Nothing is automatically uploaded. Refund terms and evidence limits are
on the service page; “no finding” and “not enough evidence” are valid outcomes.

No local mail app? [Download an application template or copy the email](https://roy-tong.github.io/AgentMeasure/services.html#after-apply).
Attachments are manual. Do not send the full report.json, HTML report or raw logs
when only a summary is requested. Tool bugs can be reported free in
[Issues](https://github.com/roy-tong/AgentMeasure/issues/new), with a redacted reproduction.

## For tool maintainers and providers

| Resource | Use it for |
|---|---|
| [Conformance pack](conformance/pack/README.md) | Check fixtures and reported metrics; PASS / FAIL / UNPROVABLE |
| [Provider SDK](sdk/README.md) | Capture canonical observations from MCP tool handlers: `npm install @agentmeasure/mcp` |
| [Core specification](standard/CORE.md) and [AMS-1](standard/SETTLEMENT.md) | Define measurement grains and the evidence needed for claims |
| [Claims index](https://roy-tong.github.io/AgentMeasure/claims.html) | Inspect dated findings, reproductions and upstream responses |
| [Lab](lab/README.md) | Existing experimental tooling; no hosted product commitment |

The buyer tools above (`recount`, `prepare`, `dispute`, `recovery`) share one
[end-to-end walkthrough](https://roy-tong.github.io/AgentMeasure/first-look.html).
They are free CLI capabilities, not one of the two current fixed-price
services. Current development priorities are in the [roadmap](ROADMAP.md).

## Evidence and limits

The [September audit report](campaigns/audit-report-2026-09.md) documents the
110-tool review. Individual findings and subsequent corrections are linked in
the claims index. Engineering evidence does not establish paid demand, customer
savings or a right to a refund. Customer value and repeat purchase remain under validation.

487 Healthcheck unit tests passed on 2026-10-15. See [CI](https://github.com/roy-tong/AgentMeasure/actions/workflows/conformance.yml)
for current results and [v0.7.2](https://github.com/roy-tong/AgentMeasure/releases/tag/v0.7.2)
for the release scope. Example fixtures are not production customer data.

## Open-source commitments

- MIT-licensed tools and public rules remain free. Paying does not change a verdict.
- Analysis runs locally. Sharing a sanitized sample is your explicit choice.
- No paid rankings or recommendation slots; no payment custody.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Governance](GOVERNANCE.md) · [Agent instructions](AGENTS.md) · [Whitepaper](whitepaper/measuring-software-used-by-ai-agents.md)

[Developer guide](docs/developer-guide.md)
