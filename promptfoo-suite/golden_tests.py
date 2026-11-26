import csv
from pathlib import Path

CSV_FILE = Path(__file__).parent.parent / "golden-set" / "golden.csv"


def create_tests():
    tests = []
    with open(CSV_FILE, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            test = {
                "description": f"golden #{row['id']} {row['category']}",
                "vars": {"question": row["question"]},
                "metadata": {
                    "category": row["category"],
                    "failure_category": row["failure_category"],
                    "grader": row["grader"],
                },
                "assert": [],
            }

            for include in row["must_include"].split(";"):
                if include:
                    test["assert"].append(
                        {"type": "icontains", "value": include}
                    )  # why: populate icontains assert only in case it is present in CSV (to avoid empty asserts that will fail the test)
            for not_include in row["must_not_include"].split(";"):
                if not_include:
                    test["assert"].append(
                        {
                            "type": "not-icontains",
                            "value": not_include,
                        }  # why: populate not-icontains assert only in case it is present in CSV (to avoid empty asserts that will fail the test)
                    )
            if row["must_match"]:
                test["assert"].append(
                    {"type": "regex", "value": row["must_match"]}
                )  # why: populate regex assert only in case it is present in CSV
            if "reference" in row["grader"]:
                test["assert"].append(
                    {
                        "type": "similar",
                        "value": row["expected_behavior"],
                        "threshold": 0.70,  # why: this is off-topic check, not correctness
                    },
                )
            tests.append(test)
    return tests
