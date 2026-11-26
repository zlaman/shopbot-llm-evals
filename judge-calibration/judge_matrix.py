# Helper script, AI-assisted (M04.4): one table per criterion with every judge's verdict side by side,
# for the rows where at least one judge disagrees with your label. "X" marks a disagreement.
# Add --reasons to print each judge's reason for the rows it got wrong.
# Usage (from judge-calibration):
#   python3 judge_matrix.py
#   python3 judge_matrix.py --reasons
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
JUDGES = {  # name -> results file (all on the same 20 rows)
    "local": "judge-local-20.json",
    "haiku": "judge-claude-haiku.json",
    "sonnet": "judge-claude-sonnet.json",
    "opus": "judge-claude-opus.json",
    "fable": "judge-claude-fable.json",
}
show_reasons = "--reasons" in sys.argv

rows20 = [r["row"] for r in csv.DictReader(open(HERE / "outputs-20.csv", encoding="utf-8"))]
labels = {r["row"]: r for r in csv.DictReader(open(HERE / "labels.csv", encoding="utf-8"))}
outputs = {r["row"]: r for r in csv.DictReader(open(HERE / "outputs.csv", encoding="utf-8"))}

verdicts = {}  # (judge, row, criterion) -> (verdict, reason)
for name, path in JUDGES.items():
    for r in json.load(open(HERE / path, encoding="utf-8"))["results"]["results"]:
        for c in r["gradingResult"]["componentResults"]:
            verdicts[(name, r["vars"]["row"], c["assertion"].get("metric"))] = (
                "pass" if c["pass"] else "fail", c.get("reason", ""))

for crit in ["escalation", "facts"]:
    print(f"\n=== {crit}: rows where at least one judge disagrees with your label ===")
    print(f"{'row':>4} {'human':<6} " + " ".join(f"{n:<7}" for n in JUDGES))
    for row in rows20:
        human = labels[row][crit]
        cells = []
        for n in JUDGES:
            v = verdicts[(n, row, crit)][0]
            cells.append((v + (" X" if v != human else "")).ljust(7))
        if any("X" in c for c in cells):
            print(f"{row:>4} {human:<6} " + " ".join(cells))
            if show_reasons:
                o = outputs[row]
                print(f"       question: {o['question']}")
                print(f"       answer:   {o['answer'][:200]}")
                print(f"       human:    {labels[row][crit + '_reason'] or '(no reason)'}")
                for n in JUDGES:
                    v, reason = verdicts[(n, row, crit)]
                    if v != human:
                        print(f"       {n:<7} {reason[:220]}")
                print()
