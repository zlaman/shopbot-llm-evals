# Helper script, AI-assisted (M04.4): checks a probe run against the expected_security column of the probe CSV.
# show_disagree.py can't do this: it reads labels.csv, which holds only the 40 real rows.
# A row's security result = fail if ANY security check fails (the LLM rubric or card-leak).
# Under each row it lists every check (all criteria) with its verdict and the judge's reason.
# Usage (from judge-calibration):
#   python3 check_probe.py judge-probe-v6.json
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
SECURITY_METRICS = ["security", "card-leak"]  # every check that belongs to the security criterion

results = json.load(open(HERE / sys.argv[1], encoding="utf-8"))["results"]["results"]
wrong = 0
for r in sorted(results, key=lambda r: int(r["vars"]["row"])):
    v = r["vars"]
    comps = r["gradingResult"]["componentResults"]
    checks = {c["assertion"].get("metric"): ("pass" if c["pass"] else "fail") for c in comps}
    found = {m: checks[m] for m in SECURITY_METRICS if m in checks}
    combined = "fail" if "fail" in found.values() else "pass"
    ok = combined == v["expected_security"]
    wrong += not ok
    parts = ", ".join(f"{m} {found[m]}" for m in found)
    # optional per-check expected columns, e.g. card-leak -> expected_card_leak
    # (expected_security is the combined result, so it is not compared with the LLM check alone)
    for m in found:
        if m == "security":
            continue
        col = "expected_" + m.replace("-", "_")
        if col in v and v[col] != found[m]:
            parts += f"; {m} expected {v[col]}"
    print(f"row {v['row']}: expected {v['expected_security']}, got {combined} ({parts}) {'OK' if ok else 'WRONG'}")
    for c in comps:
        verdict = "pass" if c["pass"] else "fail"
        print(f"    {c['assertion'].get('metric'):<11} {verdict}: {c.get('reason', '')[:250]}")
    print()
print(f"{len(results) - wrong} of {len(results)} probe rows right")
