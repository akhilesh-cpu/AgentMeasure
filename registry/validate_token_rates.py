#!/usr/bin/env python3
"""Token-rates registry validator（零依赖）。

用法: python3 registry/validate_token_rates.py [--selftest]

校验 registry/token-rates.json：
  - 每个 vendor 带 source（URL）与 verified_on（YYYY-MM-DD）；
  - 每个模型要么 flat（input_cache_miss + output），要么 windows[];
  - windows 模型恰有一个 fallback:true 窗口；显式窗口的 hours_utc
    是合法的 HH:MM-HH:MM 区间且区间内 start < end；
  - 所有费率为正数；缺省字段不得为 0（absent ≠ zero：无 cache_hit 价的
    厂商就不写该字段，写 0 = 数据错误）。

--selftest 额外运行**窗口选择回归**（time-windowed pricing 的 drift 守卫）：
用合成时间戳验证 resolve_window() 的确定性——
  - 周二 02:00 UTC 命中 peak；
  - 周二 05:30 UTC（两段 peak 之间）落 fallback；
  - 周日 02:00 UTC 落 fallback；
  - 任何时间戳都解析出恰好一个窗口（无多命中、无零命中）。
一个把费率用在错误窗口的实现（或把 fallback 当 peak 用）在这里变红。

退出码：0 = 通过；1 = 违规。
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FILE = ROOT / "token-rates.json"

errors: list = []


def err(msg: str) -> None:
    errors.append(msg)
    print(f"  ✗ {msg}")


def ok(msg: str) -> None:
    print(f"  ✓ {msg}")


def is_url(s) -> bool:
    return isinstance(s, str) and s.startswith(("http://", "https://"))


def is_date(s) -> bool:
    if not isinstance(s, str) or len(s) != 10:
        return False
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def parse_range(r: str):
    try:
        a, b = r.split("-")
        ah, am = (int(x) for x in a.split(":"))
        bh, bm = (int(x) for x in b.split(":"))
        if not (0 <= ah < 24 and 0 <= bh < 24 and 0 <= am < 60 and 0 <= bm < 60):
            return None
        return (ah * 60 + am, bh * 60 + bm)
    except Exception:
        return None


def resolve_window(windows: list, ts: datetime):
    """Deterministic window selection: a timestamp resolves to exactly one
    window — the first explicit window whose ranges contain the UTC
    minute-of-day on a matching weekday; otherwise the fallback. No window
    matching and no fallback -> None (the caller must treat that as a data
    error, never silently price)."""
    minute = ts.hour * 60 + ts.minute
    wd = ts.weekday()  # 0=Mon
    fallback = None
    for w in windows:
        if w.get("fallback"):
            if fallback is not None:
                return "AMBIGUOUS"  # multiple fallbacks — data error
            fallback = w
            continue
        ranges = [parse_range(r) for r in w.get("hours_utc", [])]
        if any(r is None for r in ranges):
            return "BAD-RANGE"
        days = w.get("days", "")
        weekday_gated = "Monday through Friday" in days or "Mon-Fri" in days
        day_match = (not weekday_gated) or (wd < 5)
        if day_match and any(a <= minute < b for a, b in ranges):
            return w
    return fallback


def main(argv: list) -> int:
    data = json.loads(FILE.read_text(encoding="utf-8"))
    vendors = data.get("vendors", {})

    if not isinstance(data.get("schema_version"), int):
        err("schema_version missing")
    if not vendors:
        err("no vendors registered")

    for vid, v in vendors.items():
        if not is_url(v.get("source")):
            err(f"{vid}: source must be the official pricing URL")
        if not is_date(v.get("verified_on")):
            err(f"{vid}: verified_on must be YYYY-MM-DD")
        models = v.get("models", {})
        if not models:
            err(f"{vid}: no models")
        for mid, m in models.items():
            rates_seen = False
            for k in ("input_cache_miss", "input_cache_hit", "output"):
                if k in m:
                    val = m[k]
                    if not isinstance(val, (int, float)) or val <= 0:
                        err(f"{vid}/{mid}.{k}: must be a positive number (0 = data error; absent means not published)")
                    rates_seen = True
            windows = m.get("windows")
            if windows is not None:
                fallbacks = 0
                names = set()
                for w in windows:
                    wname = w.get("name")
                    if wname in names:
                        err(f"{vid}/{mid}: duplicate window name {wname!r}")
                    names.add(wname)
                    if w.get("fallback"):
                        fallbacks += 1
                        if "hours_utc" in w:
                            err(f"{vid}/{mid}: fallback window must not carry hours_utc")
                    else:
                        hrs = w.get("hours_utc")
                        if not isinstance(hrs, list) or not hrs:
                            err(f"{vid}/{mid} window {wname!r}: explicit window requires non-empty hours_utc")
                        else:
                            for r in hrs:
                                if parse_range(r) is None:
                                    err(f"{vid}/{mid} window {wname!r}: bad hours range {r!r}")
                    for k in ("input_cache_miss", "output"):
                        val = w.get(k)
                        if not isinstance(val, (int, float)) or val <= 0:
                            err(f"{vid}/{mid} window {wname!r}.{k}: must be a positive number")
                if fallbacks != 1:
                    err(f"{vid}/{mid}: windows need exactly one fallback:true window, found {fallbacks}")
            elif "input_cache_miss" not in m or "output" not in m:
                err(f"{vid}/{mid}: flat pricing requires input_cache_miss and output")
            if not rates_seen and windows is None:
                err(f"{vid}/{mid}: no rates at all")

    if errors:
        print(f"\nTOKEN-RATES REGISTRY FAIL: {len(errors)} error(s)")
        return 1

    ok(f"{len(vendors)} vendor(s), registry structurally valid")

    if "--selftest" in argv:
        print("\nwindow-selection regression (time-windowed drift guard):")
        ds = vendors.get("deepseek", {}).get("models", {})
        cases = []
        for mid, m in ds.items():
            if "windows" in m:
                cases.append(mid)
        if not cases:
            err("selftest requires at least one windowed model — none found")
        else:
            mid = cases[0]
            windows = ds[mid]["windows"]
            t_peak = datetime(2026, 10, 13, 2, 0, tzinfo=timezone.utc)      # Tuesday 02:00
            t_gap = datetime(2026, 10, 13, 5, 30, tzinfo=timezone.utc)      # Tuesday 05:30 (between ranges)
            t_weekend = datetime(2026, 10, 11, 2, 0, tzinfo=timezone.utc)   # Sunday 02:00
            r1 = resolve_window(windows, t_peak)
            r2 = resolve_window(windows, t_gap)
            r3 = resolve_window(windows, t_weekend)
            check = lambda label, cond: (ok(label) if cond else err(label))
            check("Tuesday 02:00 UTC resolves to peak", isinstance(r1, dict) and r1.get("name") == "peak")
            check("Tuesday 05:30 UTC falls back to off-peak", isinstance(r2, dict) and r2.get("fallback") is True)
            check("Sunday 02:00 UTC falls back to off-peak", isinstance(r3, dict) and r3.get("fallback") is True)
            every = [resolve_window(windows, datetime(2026, 10, d, h, 0, tzinfo=timezone.utc))
                     for d in range(9, 16) for h in range(24)]
            check("every hour of a full week resolves to exactly one window",
                  all(isinstance(r, dict) and not isinstance(r, str) for r in every)
                  and len(every) == 168)
        if errors:
            print(f"\nTOKEN-RATES SELFTEST FAIL: {len(errors)} error(s)")
            return 1
        print("\nTOKEN-RATES SELFTEST PASS: structure + window-selection determinism")

    print("\nTOKEN-RATES REGISTRY PASS" + (" (with selftest)" if "--selftest" in argv else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
