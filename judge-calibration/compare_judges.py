# Helper script, AI-assisted (M04.4): compares judges on the same 20 rows (outputs-20.csv) against labels.csv.
# For each judge and criterion: disagree rows, accuracy and kappa on the 20 rows.
# Also: seconds per judge call and an API-price estimate (local = $0; use a --no-cache run for real timing).
#   The estimate uses list prices per 1M tokens (input / output) and ignores cache discounts,
#   so it's "about what 1000 judgments would cost with an API key". With the Pro login you pay $0 extra;
#   the calls use your Pro limits instead.
# Usage (from judge-calibration):
#   python3 compare_judges.py local=judge-results-v8.json haiku=judge-claude-haiku.json ...
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
CRITERIA = ["escalation", "facts"]
PRICE = {"local": (0.0, 0.0), "haiku": (0.10, 0.50), "sonnet": (2.00, 10.00), "opus": (4.00, 20.00), "fable": (8.00, 40.00), "jev": (0.042, 0.0)}  # $ per 1M tokens (Jev: input only)
# M04.6: names starting with "jev" use the jev price; criteria missing in a file print "-".

rows20 = [r["row"] for r in csv.DictReader(open(HERE / "outputs-20.csv", encoding="utf-8"))]
labels = {r["row"]: r for r in csv.DictReader(open(HERE / "labels.csv", encoding="utf-8"))}


def kappa(human, judge):
    n = len(human)
    agree = sum(h == j for h, j in zip(human, judge))
    p_fail = (human.count("fail") / n) * (judge.count("fail") / n)
    p_pass = (human.count("pass") / n) * (judge.count("pass") / n)
    expected = p_fail + p_pass
    acc = agree / n
    return acc, (acc - expected) / (1 - expected) if expected < 1 else 0.0


print(f"{'judge':<8} {'criterion':<11} {'accuracy':>9} {'kappa':>6}  disagree rows (of 20 rows)")
summary = []
for arg in sys.argv[1:]:
    name, path = arg.split("=", 1)
    data = json.load(open(HERE / path, encoding="utf-8"))
    verdicts = {}
    for r in data["results"]["results"]:
        for c in r["gradingResult"]["componentResults"]:
            verdicts[(r["vars"]["row"], c["assertion"].get("metric"))] = "pass" if c["pass"] else "fail"
    for crit in CRITERIA:
        human = [labels[row][crit] for row in rows20]
        if any((row, crit) not in verdicts for row in rows20):
            print(f"{name:<8} {crit:<11} {'-':>9} {'-':>6}  not in this file")
            continue
        judge = [verdicts[(row, crit)] for row in rows20]
        acc, k = kappa(human, judge)
        bad = [row for row, h, j in zip(rows20, human, judge) if h != j]
        print(f"{name:<8} {crit:<11} {acc:>8.0%} {k:>6.2f}  {', '.join(bad) or '-'}")
    price_name = "jev" if name.startswith("jev") else name
    if price_name in PRICE:
        stats = data["results"]["stats"]
        tok = stats["tokenUsage"]["assertions"]
        if not tok.get("numRequests"):  # Jev as provider under test (atomic): tokens are on the provider
            tok = stats["tokenUsage"]
        calls = tok["numRequests"]
        sec = stats["durationMs"] / 1000 / calls
        pin, pout = PRICE[price_name]
        per_1000 = (tok["prompt"] * pin + tok["completion"] * pout) / 1e6 / calls * 1000
        lat = sorted(r.get("latencyMs") or 0 for r in data["results"]["results"])
        median_ms = lat[len(lat) // 2] if price_name == "jev" and tok is stats["tokenUsage"] else None  # provider runs only
        summary.append((name, calls, sec, per_1000, median_ms))

if summary:
    print(f"\n{'judge':<10} {'calls':>5} {'s per call':>11} {'API estimate $ per 1000 judgments':>34} {'median ms per request':>22}")
    for name, calls, sec, cost, median_ms in summary:
        ms = f"{median_ms:.0f}" if median_ms is not None else "-"
        print(f"{name:<10} {calls:>5} {sec:>11.2f} {cost:>34.3f} {ms:>22}")
    print("(cached runs show 0 s and $0: use a --no-cache run for timing and cost)")
