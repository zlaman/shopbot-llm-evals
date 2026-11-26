"""Print per-test latency from a Promptfoo results file (helper script, AI-assisted).

Usage:
    npx promptfoo@0.125.1 eval -c classify.yaml -o results.json
    ../.venv/bin/python latency_report.py results.json
"""

import json
import statistics
import sys
from collections import defaultdict

if len(sys.argv) != 2:
    sys.exit("Usage: python latency_report.py results.json")

with open(sys.argv[1], encoding="utf-8") as f:
    results = json.load(f)["results"]["results"]

by_provider = defaultdict(list)  # provider -> latencies in ms (M03.4 runs several providers)
print(f"{'test':<45} {'provider':<25} {'status':<6} {'latency':>10}")
for r in results:
    name = r["testCase"].get("description") or str(next(iter(r["vars"].values()), ""))
    provider = r["provider"].get("label") or r["provider"].get("id", "")
    latency_ms = r.get("latencyMs", 0)
    status = "PASS" if r["success"] else "FAIL"
    by_provider[provider].append(latency_ms)
    print(f"{name[:45]:<45} {provider[-25:]:<25} {status:<6} {latency_ms:>7.0f} ms")

print()
for provider, latencies in by_provider.items():
    print(
        f"{provider}: {len(latencies)} tests, latency min {min(latencies):.0f} ms, "
        f"median {statistics.median(latencies):.0f} ms, max {max(latencies):.0f} ms"
    )
