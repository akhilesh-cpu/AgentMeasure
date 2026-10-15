# v0.8.0 — Your AI bill, re-countable in one command

This release makes the buyer-side recount the product's front door.

`agentmeasure recount --sample` runs the bundled 5-row synthetic export under the Zendesk rule set with zero preparation — the README shows the same file, the command prints the same report. Every recount report now opens with a dollar headline (`billed $10.00 · net overcharge $2.00 · at USD 2.0/resolution`) before any detail.

Three reproducible showcase cases ship in `examples/showcase/` — an overcharge that refuses to guess, findings in both directions, and the contract lane as renewal leverage — each with a frozen expected output that CI compares on every change, so the showcase cannot drift from shipped behaviour.

Fork this repo, drop your vendor export into `.agentmeasure/`, and the new Monthly bill reconcile workflow re-counts your bill every month on GitHub Actions: no server, nothing leaves your fork, and a non-zero variance opens a tracking issue so the finding cannot be forgotten. Setup is five minutes in RECONCILE.md; six vendor rule sets ship today (intercom, zendesk, hubspot, ada, salesforce, generic), each printed with its public source and confidence grade.

The website claims index gains a vendor billing-rule scorecard: published price, billing trigger, dated rule source and how far each vendor is re-countable from a counts-only export — always matching the shipped registry.

What did not change: the free/paid boundary (the CLI answers IF; paid human services answer WHAT/WHY/NEXT), the evidence discipline (rows without enough evidence are `cannot settle`, removed from the claim and never zeroed), and no promise that a variance is a guaranteed refund.

Upgrade: `python -m pip install --upgrade agentmeasure`.

Validation: full Healthcheck suite plus the new showcase freeze tests; installed-wheel smoke covers `recount --sample`. SDK remains 0.2.0. Research feedback and test results do not establish payment or PMF.
