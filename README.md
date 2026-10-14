# AgentMeasure

**Check Codex / Claude Code logs for duplicate records, retries and token anomalies. Verify agent metering with reproducible evidence.**

[Website](https://roy-tong.github.io/AgentMeasure/) · [中文](README.zh-CN.md) · [Healthcheck guide](healthcheck/README.md) · [Release notes](https://roy-tong.github.io/AgentMeasure/releases.html)

## Try it locally

```bash
pip install agentmeasure
agentmeasure demo                 # synthetic example; no account or upload
agentmeasure check                # inspect your local Codex / Claude Code sessions
```

The demo shows findings from a bundled synthetic session. Your own check reports
coverage, failures, retry chains and available token evidence. Missing evidence
stays unknown; a retry is not automatically a second logical operation.

Python 3.9+. CLI **0.7.1** on [PyPI](https://pypi.org/project/agentmeasure/);
Provider SDK **0.2.0** on [npm](https://www.npmjs.com/package/@agentmeasure/mcp),
verified 2026-10-15. These packages have separate version numbers.

Open the HTML report at the path printed by the command. On macOS/Linux use
`python3 -m pip` if needed; on Windows use `py -m pip`. For permission or
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

Buyer reconciliation tools remain available as [an experimental reference](https://roy-tong.github.io/AgentMeasure/first-look.html).
They are not one of the two current fixed-price services. Current development
priorities are in the [roadmap](ROADMAP.md).

## Evidence and limits

The [September audit report](campaigns/audit-report-2026-09.md) documents the
110-tool review. Individual findings and subsequent corrections are linked in
the claims index. Engineering evidence does not establish paid demand, customer
savings or a right to a refund. Customer value and repeat purchase remain under validation.

479 Healthcheck unit tests passed on 2026-10-15. See [CI](https://github.com/roy-tong/AgentMeasure/actions/workflows/conformance.yml)
for current results and [v0.7.1](https://github.com/roy-tong/AgentMeasure/releases/tag/v0.7.1)
for the release scope. Example fixtures are not production customer data.

## Open-source commitments

- MIT-licensed tools and public rules remain free. Paying does not change a verdict.
- Analysis runs locally. Sharing a sanitized sample is your explicit choice.
- No paid rankings or recommendation slots; no payment custody.

[Contributing](CONTRIBUTING.md) · [Security](SECURITY.md) · [Governance](GOVERNANCE.md) · [Agent instructions](AGENTS.md) · [Whitepaper](whitepaper/measuring-software-used-by-ai-agents.md)

[Developer guide](docs/developer-guide.md)
