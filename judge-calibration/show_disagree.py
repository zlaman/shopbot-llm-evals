# Helper script, AI-assisted (M04.4): prints every row where human and judge disagree for one criterion,
# with the human reason and the judge reason side by side, so you can group the causes.
# Usage (from judge-calibration):
#   python3 show_disagree.py escalation
#   python3 show_disagree.py facts judge-results-v2.json
#   python3 show_disagree.py facts judge-claude-haiku.json   (20-row runs work too)
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
criterion = sys.argv[1]
results_file = HERE / (sys.argv[2] if len(sys.argv) > 2 else "judge-results.json")

outputs = {r["row"]: r for r in csv.DictReader(open(HERE / "outputs.csv", encoding="utf-8"))}
labels = {r["row"]: r for r in csv.DictReader(open(HERE / "labels.csv", encoding="utf-8"))}

judge = {}
for r in json.load(open(results_file, encoding="utf-8"))["results"]["results"]:
    for c in r["gradingResult"]["componentResults"]:
        if c["assertion"]["metric"] == criterion:
            judge[r["vars"]["row"]] = ("pass" if c["pass"] else "fail", c.get("reason", ""))

count = 0
rows = [row for row in labels if row in judge]  # results may cover only some rows (e.g. outputs-20.csv)
for row in rows:
    human = labels[row][criterion]
    verdict, reason = judge[row]
    if human == verdict:
        continue
    count += 1
    kind = "MISSED" if human == "fail" else "FALSE ALARM"
    o = outputs[row]
    print(f"=== row {row} (case {o['case_id']}, {o['category']}) {kind}: human {human}, judge {verdict}")
    print(f"question: {o['question']}")
    print(f"answer:   {o['answer'][:300]}")
    print(f"human:    {labels[row][criterion + '_reason'] or '(no reason)'}")
    print(f"judge:    {reason}")
    print()
print(f"{criterion}: {count} disagree rows of {len(rows)} rows")
