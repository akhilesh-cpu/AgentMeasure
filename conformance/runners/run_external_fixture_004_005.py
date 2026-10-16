#!/usr/bin/env python3
"""External fixture conformance: iwasinnam-004 (join) and iwasinnam-005 (replay).

Source: fixtures cut 2026-10-13 from the live Metrecept pipe by Ivan Karpusheff
(@iwasinnam2), received 2026-10-14 in the Roy Tong mail thread, contributed free
under the existing conformance collaboration. Claim boundary per each fixture's
CLAIM_BOUNDARY.md: the boundary is theirs to state, the recomputation is ours.

This runner INDEPENDENTLY recomputes every check from the raw fixture bytes and
the fetched key directory. It never reads the fixture's embedded `guards` block
for a verdict — that block is the contributor's own claim, not evidence here.

Method notes:
  - Signatures: Ed25519 (EdDSA) over the JWS signing input, public key from
    api.metrecept.co.uk/.well-known/http-message-signatures-directory (pinned
    copy next to each fixture; --live re-fetches and cross-checks).
  - kid: RFC 7638 thumbprint of the Ed25519 JWK, recomputed here.
  - Money: Decimal, never float accumulation.
  - Canonical JSON (response_sha256 rule, from the -005 field semantics):
    sorted keys, no whitespace, UTF-8, non-ASCII unescaped.
  - Stream assembly (published rule, open-repo/demo/response_digest.py):
    content deltas concatenated; role/finish from the deltas; usage from the
    final usage-bearing chunk; id/created/model from the first chunk.

Claim boundary: recomputation of contributed fixtures proves arithmetic and
signature checks on these bytes. It is not an endorsement of Metrecept, not a
certification of the live service, and says nothing about crossings outside
this run. Per -005's stated boundary, a JSON-carriage digest and a streamed-
carriage digest of one stored body MAY honestly differ; this runner compares
JSON to JSON and stream to stream, and records the cross-carriage difference
as a boundary, not a failure.

Exit 0 = all guards pass.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import urllib.request
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
V004 = ROOT / "vectors" / "external" / "iwasinnam-004-join"
V005 = ROOT / "vectors" / "external" / "iwasinnam-005-replay"
KEY_DIR_URL = "https://api.metrecept.co.uk/.well-known/http-message-signatures-directory"

RESULTS: list = []


def b64u_decode(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def rfc7638_thumbprint(jwk: dict) -> str:
    """Thumbprint over the required-members JWK {crv, kty, x}, sorted keys."""
    core = {k: jwk[k] for k in ("crv", "kty", "x")}
    return b64u(hashlib.sha256(canonical(core)).digest())


def check(gid: str, desc: str, ok: bool, detail: str = "") -> bool:
    RESULTS.append((gid, desc, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {gid} {desc}" + (f" — {detail}" if detail else ""))
    return ok


def jws_verify(raw_jws: str, ed_pub, expected_kid: str) -> bool:
    """Ed25519 detached-payload-free compact JWS: verify over 'h.p'."""
    h_b64, p_b64, s_b64 = raw_jws.split(".")
    signing_input = f"{h_b64}.{p_b64}".encode()
    try:
        ed_pub.verify(b64u_decode(s_b64), signing_input)
        return True
    except Exception:
        return False


def load_keys(live: bool):
    """Return (keys_by_kid, source_note). Pinned fallback; live cross-check."""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

    def parse(doc: dict) -> dict:
        out = {}
        for jwk in doc["keys"]:
            key = Ed25519PublicKey.from_public_bytes(b64u_decode(jwk["x"]))
            out[jwk["kid"]] = (key, rfc7638_thumbprint(jwk), jwk)
        return out

    pinned = parse(json.loads((V004 / "key-directory-fetched-20261016.json").read_text()))
    note = f"pinned 2026-10-16 fetch ({len(pinned)} key)"
    if live:
        try:
            with urllib.request.urlopen(KEY_DIR_URL, timeout=15) as r:
                live_doc = json.loads(r.read())
            live_keys = parse(live_doc)
            same = {k: v[2] for k, v in pinned.items()} == {k: v[2] for k, v in live_keys.items()}
            note = f"live fetch matches pinned copy: {same}"
        except Exception as exc:
            note = f"live fetch FAILED ({exc}); using pinned copy"
    return pinned, note


def money(v) -> Decimal:
    return Decimal(str(v))


def run_004(keys, note) -> bool:
    fx = json.loads((V004 / "agentmeasure_iwasinnam_join_fixture_004.json").read_text())
    receipts = fx["crossing_receipts"]
    session = fx["session_receipt"]
    tagged = [r for r in receipts if r.get("session_tagged")]
    untagged = [r for r in receipts if not r.get("session_tagged")]
    sp = session["decoded_payload"]
    ok = True

    ok &= check("A1", f"all 5 JWS verify vs key directory ({note}); kid = RFC 7638 thumbprint",
                all(jws_verify(r["raw_jws"], keys[r["jws_header"]["kid"]][0],
                               r["jws_header"]["kid"]) for r in receipts + [session])
                and all(keys[k][1] == k for k in keys))

    ok &= check("A2", "event_count == number of tagged member receipts",
                sp["event_count"] == len(tagged),
                f"aggregate says {sp['event_count']}, members = {len(tagged)}")

    member_sum = sum((money(r["decoded_payload"]["pipe_usd"]) for r in tagged), Decimal(0))
    ok &= check("A3", "session pipe_usd == sum of tagged members (Decimal)",
                money(sp["pipe_usd"]) == member_sum,
                f"aggregate {sp['pipe_usd']} vs sum {member_sum}")

    ok &= check("A4", "per-kind counts match members",
                sp["cache_hits"] == sum(1 for r in tagged if r["decoded_payload"]["kind"] == "cache_hit")
                and sp["cache_misses"] == sum(1 for r in tagged if r["decoded_payload"]["kind"] == "cache_miss")
                and sp["cache_bypasses"] == 0 and sp["api_calls"] == 0 and sp["fetches"] == 0)

    u = untagged[0]
    u_meter = u["decoded_payload"]["meter_event_id"]
    tagged_meters = {r["decoded_payload"]["meter_event_id"] for r in tagged}
    with_bypass = member_sum + money(u["decoded_payload"]["pipe_usd"])
    ok &= check("A5", "untagged bypass: metered with own id, correctly ABSENT from the aggregate",
                u["decoded_payload"]["kind"] == "cache_bypass" and bool(u_meter)
                and u_meter not in tagged_meters and sp["event_count"] == len(tagged),
                f"bypass meter id {u_meter[:8]}…; sum with bypass would be {with_bypass}")

    all_meters = [r["decoded_payload"]["meter_event_id"] for r in receipts]
    ok &= check("A6", "four crossings, four distinct meter_event_ids (cover, not collapse)",
                len(all_meters) == 4 and len(set(all_meters)) == 4)

    planted = fx["scenario"]["session_header"].split(": ", 1)[1]
    ok &= check("A7", "session_sha256 == sha256(planted id)",
                sp["session_sha256"] == sha256_hex(planted.encode("utf-8")))

    raw_leak = any(planted in json.dumps(r["decoded_payload"]) for r in receipts + [session])
    ok &= check("A8", "raw session id appears in NO signed payload", not raw_leak)

    # Mutation negative controls: the join must fail while the session's own
    # signature (untouched bytes) still verifies — signature is not the join.
    def join_holds(members):
        return (sp["event_count"] == len(members)
                and money(sp["pipe_usd"]) == sum((money(m["pipe_usd"]) for m in members), Decimal(0)))

    sig_still_ok = jws_verify(session["raw_jws"], keys[session["jws_header"]["kid"]][0],
                              session["jws_header"]["kid"])
    payloads = [r["decoded_payload"] for r in tagged]
    ok &= check("M1", "drop a member -> join fails, session signature still verifies",
                sig_still_ok and not join_holds(payloads[:2]))
    ok &= check("M2", "reprice a member -> join fails, signature still verifies",
                sig_still_ok and not join_holds([payloads[0], {**payloads[1], "pipe_usd": 0.007},
                                                 payloads[2]]))
    ok &= check("M3", "insert the bypass into the member set -> join fails",
                sig_still_ok and not join_holds(payloads + [u["decoded_payload"]]))
    return ok


def assemble_sse(lines):
    """Published rule: concatenate content deltas; role/finish from deltas;
    usage from the last usage-bearing chunk; envelope from the first chunk."""
    chunks = []
    for line in lines:
        if not line.startswith("data:"):
            continue
        body = line[5:].strip()
        if body == "[DONE]":
            continue
        chunks.append(json.loads(body))
    content, role, finish, usage = "", "assistant", None, None
    for ch in chunks:
        if ch.get("choices"):
            d = ch["choices"][0].get("delta", {})
            role = d.get("role", role)
            content += d.get("content", "")
            finish = ch["choices"][0].get("finish_reason") or finish
        if ch.get("usage"):
            usage = ch["usage"]
    first = next(c for c in chunks if c.get("choices"))
    return {"id": first["id"], "object": "chat.completion", "created": first["created"],
            "model": first["model"],
            "choices": [{"index": 0, "message": {"role": role, "content": content},
                         "finish_reason": finish}],
            "usage": usage}


def run_005(keys, note) -> bool:
    fx = json.loads((V005 / "agentmeasure_iwasinnam_replay_fixture_005.json").read_text())
    jrs, srs = fx["json_receipts"], fx["streamed_receipts"]
    ok = True

    ok &= check("B1", f"all 5 JWS verify vs key directory ({note})",
                all(jws_verify(r["raw_jws"], keys[r["jws_header"]["kid"]][0],
                               r["jws_header"]["kid"]) for r in jrs + srs))

    def dig(r):
        return r["decoded_payload"]["request_sha256"], r["decoded_payload"]["response_sha256"]

    fill, replay, changed = jrs[0], jrs[1], jrs[2]
    ok &= check("B2", "JSON: fill and replay share request and response digests",
                dig(fill) == dig(replay), f"{dig(fill)} == {dig(replay)}")
    ok &= check("B3", "JSON: changed payload carries different digests",
                dig(changed)[0] != dig(fill)[0] and dig(changed)[1] != dig(fill)[1])
    ok &= check("B4", "JSON: two different planes signed fill (python) and replay (rust-edge)",
                fill["decoded_payload"]["plane"] == "python"
                and replay["decoded_payload"]["plane"] == "rust-edge")

    ok &= check("B5", "JSON: stranger recomputes response_sha256 from served_body (canonical JSON)",
                all(sha256_hex(canonical(r["served_body"])) == r["decoded_payload"]["response_sha256"]
                    for r in (fill, replay, changed)))

    s_fill, s_replay = srs[0], srs[1]
    ok &= check("B6", "Stream: fill (15 chunks) and replay (5 chunks) share request and response digests",
                dig(s_fill) == dig(s_replay), f"{dig(s_fill)} == {dig(s_replay)}")

    a1, a2 = assemble_sse(s_fill["sse_lines"]), assemble_sse(s_replay["sse_lines"])
    ok &= check("B7", "Stream: our independent assembly reproduces BOTH receipts' response_sha256",
                sha256_hex(canonical(a1)) == s_fill["decoded_payload"]["response_sha256"]
                and sha256_hex(canonical(a2)) == s_replay["decoded_payload"]["response_sha256"],
                f"assembled digest {sha256_hex(canonical(a1))}")

    meters = [r["decoded_payload"]["meter_event_id"] for r in jrs + srs]
    ok &= check("B8", "five crossings, five distinct meter_event_ids (a replay is summed, never merged)",
                len(meters) == 5 and len(set(meters)) == 5)

    # Cross-carriage boundary: NOT a claim. Record it explicitly.
    differs = dig(fill)[1] != dig(s_fill)[1]
    check("BNDRY", "JSON digest differs from streamed digest of the same body — expected per "
          "claim boundary (stream drops provider extras); recorded, not failed", differs)

    mutated = {**fill["served_body"], "model": "mutated"}
    check("M4", "one mutated served byte -> recomputed digest leaves the receipt",
          sha256_hex(canonical(mutated)) != fill["decoded_payload"]["response_sha256"])
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="re-fetch the key directory live")
    args = ap.parse_args()
    keys, note = load_keys(args.live)
    print(f"key directory: {note}")
    ok = run_004(keys, note) & run_005(keys, note)
    fails = [r for r in RESULTS if not r[2] and not r[0].startswith(("BNDRY", "M"))]
    print(f"\n{len(RESULTS)} checks, {len(fails)} hard failures"
          + (" — ALL PASS" if not fails else ""))
    return 0 if ok and not fails else 1


if __name__ == "__main__":
    sys.exit(main())
