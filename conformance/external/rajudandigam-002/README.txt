AgentInspect 6.31.20 maintainer review. Source commit 8c7f674eeb0c3db1b7851b05ae93a2277826a011. Node v24.19.0. Synthetic/local scope unless stated otherwise. No independent reviewer acceptance is implied.
For repository recipes: clone https://github.com/rajudandigam/agent-inspect, checkout 8c7f674eeb0c3db1b7851b05ae93a2277826a011, install with pnpm 9.15.0 using pnpm install --frozen-lockfile, then pnpm build.
PARTIAL HANDOFF: do not treat the generator exit status as full conformance. The ordinary identity round trip passes. At maxAttempts=2 the repeated-delivery JSONL fails duplicate-attempt-id while its OTLP export passes. At maxAttempts=1 both fail, masking the mismatch in the generator. Identity collision is a distinct control; partial identity remains unknown.

Generator: node scripts/f04-otlp-identity-evidence.mjs ./otlp-evidence
To reproduce the additional boundary, put the generated files in a sibling ../otlp-evidence folder relative to a fresh consumer containing agent-inspect@6.31.20, rename the probe .mjs.txt to .mjs and run it in the consumer. It should exit 1 until the mismatch is fixed. No customer billing impact or financial cost was measured.

