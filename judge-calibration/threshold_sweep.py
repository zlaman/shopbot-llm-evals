# Helper script, AI-assisted (M04.6): try many pass thresholds on one Jev llm-rubric criterion and
# compare each with the human labels.
# Score = Jev P(true) saved by Promptfoo; verdict = pass if score >= threshold.
# Usage (from judge-calibration):
#   python3 threshold_sweep.py security judge-results-jev-v10.json
#   python3 threshold_sweep.py facts judge-results-jev-v10.json
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).parent


def kappa(human, judge):
    n = len(human)
    accuracy = sum(h == j for h, j in zip(human, judge)) / n
    human_pass = human.count("pass") / n
    judge_pass = judge.count("pass") / n
    expected = human_pass * judge_pass + (1 - human_pass) * (1 - judge_pass)
    return 0.0 if expected == 1 else (accuracy - expected) / (1 - expected)


criterion, results_file = sys.argv[1], sys.argv[2]

labels = {}
with open(HERE / "labels.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        labels[row["row"]] = row[criterion]

scores = {}
for result in json.loads((HERE / results_file).read_text(encoding="utf-8"))["results"]["results"]:
    for comp in result["gradingResult"]["componentResults"]:
        if comp["assertion"].get("metric") == criterion:
            scores[result["vars"]["row"]] = comp["score"]

rows = [r for r in labels if r in scores]
human = [labels[r] for r in rows]

fail_scores = sorted(scores[r] for r in rows if labels[r] == "fail")
pass_scores = sorted(scores[r] for r in rows if labels[r] == "pass")
print(f"{criterion}: {len(rows)} rows")
print(f"  human-fail rows ({len(fail_scores)} rows), Jev P(true): {', '.join(f'{s:.2f}' for s in fail_scores)}")
print(f"  human-pass rows ({len(pass_scores)} rows), Jev P(true): {', '.join(f'{s:.2f}' for s in pass_scores)}")
print()
print("threshold | missed fails (rows) | false alarms (rows) | kappa")
for step in range(5, 100, 5):
    t = step / 100
    judge = ["pass" if scores[r] >= t else "fail" for r in rows]
    missed = sum(h == "fail" and j == "pass" for h, j in zip(human, judge))
    false_alarm = sum(h == "pass" and j == "fail" for h, j in zip(human, judge))
    print(f"   {t:.2f}   |        {missed:2d}          |        {false_alarm:2d}          | {kappa(human, judge):5.2f}")
