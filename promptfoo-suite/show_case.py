"""Print every run of one golden case: provider, run, failed assertions, full output (helper script, AI-assisted, M03.5).

Usage (from promptfoo-suite):
    ../.venv/bin/python show_case.py results-compare.json 2
    ../.venv/bin/python show_case.py results-compare.json 2 E4B     # only providers whose label contains "E4B"
    ../.venv/bin/python show_case.py results-compare.json 2 --short # one line per run: the first 100 characters
"""

import json
import sys

args = [a for a in sys.argv[1:] if a != "--short"]
short = "--short" in sys.argv
if len(args) not in (2, 3):
    sys.exit("Usage: python show_case.py results.json <case id> [provider filter] [--short]")

results_file, case_id = args[0], args[1]
provider_filter = args[2] if len(args) == 3 else ""

with open(results_file, encoding="utf-8") as f:
    results = json.load(f)["results"]["results"]

# description looks like "golden #2 ambiguous"; the space stops "#2" from matching "#21"
prefix = f"golden #{case_id} "
runs = [
    r
    for r in results
    if r["testCase"].get("description", "").startswith(prefix)
    and provider_filter in r["provider"].get("label", "")
]
runs.sort(key=lambda r: (r["provider"].get("label", ""), r.get("repeatIndex", 0)))

for r in runs:
    label = r["provider"].get("label", "")
    run = r.get("repeatIndex", 0) + 1
    status = "PASS" if r["success"] else "FAIL"
    components = (r.get("gradingResult") or {}).get("componentResults", [])
    failed = [
        f'{c["assertion"]["type"]} "{c["assertion"].get("value", "")}"'
        for c in components
        if not c["pass"] and c.get("assertion")
    ]
    output = " ".join(r["response"]["output"].split())  # one line, no extra spaces
    if short:
        missing = ", ".join(f.split(" ", 1)[1] for f in failed) or "-"
        print(f"{label:<20} run {run}  {status}  failed: {missing:<18} {output[:100]}")
        continue
    print(f"=== {label}, run {run}: {status}" + (f"   failed: {', '.join(failed)}" if failed else ""))
    print(r["response"]["output"].strip())
    print()

print(f"{len(runs)} runs, {sum(not r['success'] for r in runs)} failed")
