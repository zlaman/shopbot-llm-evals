"""Pass counts per run, mean latency and failing cases per provider (helper script, AI-assisted, M03.4).

Usage (from promptfoo-suite):
    npx promptfoo@0.125.1 eval -c compare.yaml --repeat 3 -o results-compare.json
    ../.venv/bin/python compare_report.py results-compare.json
"""

import json
import statistics
import sys
from collections import Counter, defaultdict

if len(sys.argv) != 2:
    sys.exit("Usage: python compare_report.py results-compare.json")

with open(sys.argv[1], encoding="utf-8") as f:
    results = json.load(f)["results"]["results"]

passes = defaultdict(Counter)  # provider -> {run index: passed cases}
cases = defaultdict(Counter)  # provider -> {run index: all cases}
latencies = defaultdict(list)  # provider -> latencies in ms
failed_runs = defaultdict(Counter)  # provider -> {case: failed runs}

for r in results:
    provider = r["provider"].get("label") or r["provider"]["id"]
    run = r.get("repeatIndex", 0)
    cases[provider][run] += 1
    passes[provider][run] += r["success"]
    latencies[provider].append(r.get("latencyMs", 0))
    if not r["success"]:
        failed_runs[provider][r["testCase"].get("description", "?")] += 1

for provider in sorted(passes):
    runs = sorted(passes[provider])
    per_run = ", ".join(f"{passes[provider][k]} of {cases[provider][k]}" for k in runs)
    print(f"{provider}")
    print(f"  cases passed per run: {per_run}")
    print(f"  mean latency: {statistics.mean(latencies[provider]):.0f} ms")
    failing = ", ".join(f"{case} ({n} of {len(runs)} runs)" for case, n in failed_runs[provider].most_common())
    print(f"  failing cases: {failing or 'none'}")
