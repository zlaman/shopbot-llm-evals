import csv
import json
from pathlib import Path
import sys


def confusion(human, judge):
    assert len(human) == len(judge), f"length differ: {len(human)} vs {len(judge)}"
    both_fail = sum(1 for h, j in zip(human, judge) if h == "fail" and j == "fail")
    missed = sum(1 for h, j in zip(human, judge) if h == "fail" and j == "pass")
    false_alarm = sum(1 for h, j in zip(human, judge) if h == "pass" and j == "fail")
    both_pass = sum(1 for h, j in zip(human, judge) if h == "pass" and j == "pass")
    return {
        "both_fail": both_fail,
        "missed": missed,
        "false_alarm": false_alarm,
        "both_pass": both_pass,
    }


def scores(c):
    n = c["both_fail"] + c["missed"] + c["false_alarm"] + c["both_pass"]
    accuracy = (c["both_fail"] + c["both_pass"]) / n
    human_fail = (c["both_fail"] + c["missed"]) / n  # human said fail rows
    judge_fail = (c["both_fail"] + c["false_alarm"]) / n  # judge said fail rows
    expected = (
        human_fail * judge_fail + (1 - human_fail) * (1 - judge_fail)
    )  # human fail × judge fail + human pass × judge pass, where pass share = 1 − fail share
    kappa = (accuracy - expected) / (1 - expected)
    return {"accuracy": accuracy, "expected": expected, "kappa": kappa}


def load_labels():
    rows = {}
    labels_csv = Path(__file__).parent / "labels.csv"
    with open(labels_csv, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            r = {
                "security": row["security"],
                "escalation": row["escalation"],
                "facts": row["facts"],
            }
            rows[row["row"]] = r
    return rows


def load_judge(filename):
    rows = {}
    judge_results = Path(__file__).parent / filename
    with open(judge_results, encoding="utf-8") as f:
        results = json.load(f)["results"]["results"]
    for row in results:
        r = {}
        for component_result in row["gradingResult"]["componentResults"]:
            metric = component_result["assertion"]["metric"]
            r[metric] = "pass" if component_result["pass"] else "fail"
        rows[row["vars"]["row"]] = r
    return rows


def process_labels_and_judge(human, judge):
    criteria = ["security", "escalation", "facts"]
    for criterion in criteria:
        if not all(criterion in judge[row] for row in human):
            print(criterion, "not in this judge file, skipped")
            continue
        human_list = [human[row][criterion] for row in human]
        judge_list = [judge[row][criterion] for row in human]
        disagree = [
            row for row in human if human[row][criterion] != judge[row][criterion]
        ]
        c = confusion(human=human_list, judge=judge_list)
        s = scores(c)
        print(
            criterion,
            c,
            "accuracy",
            round(s["accuracy"], 2),
            "expected",
            round(s["expected"], 2),
            "kappa",
            round(s["kappa"], 2),
            disagree,
        )


ex_human = ["fail", "fail", "pass", "pass", "pass", "pass"]
ex_judge = ["fail", "pass", "fail", "pass", "pass", "pass"]
# print(scores(confusion(human=ex_human, judge=ex_judge)))

human = load_labels()
judge = load_judge(sys.argv[1] if len(sys.argv) > 1 else "judge-results.json")
process_labels_and_judge(human=human, judge=judge)
