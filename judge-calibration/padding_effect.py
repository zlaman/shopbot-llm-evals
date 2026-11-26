# Helper script, AI-assisted (M04.5): verbosity-bias report from a verbosity.yaml run on padded.csv.
# For each row: the facts verdict on the plain answer vs on the padded answer (same run, same judge).
# Sanity check first: all 15 plain answers should still be "fail" (they were in the v8 run).
#   A plain "pass" means the judge's verdict changed between runs (repeatability), not padding.
# Usage (from judge-calibration): python3 padding_effect.py verbosity-results.json
import json
import sys
from pathlib import Path

data = json.loads((Path(__file__).parent / sys.argv[1]).read_text(encoding="utf-8"))
verdict = {}  # row -> {"plain": True/False, "padded": True/False}  (True = pass)
for result in data["results"]["results"]:
    v = result["vars"]
    for comp in result["gradingResult"]["componentResults"]:
        if comp["assertion"].get("metric") == "facts":
            verdict.setdefault(int(v["row"]), {})[v["version"]] = comp["pass"]

word = {True: "pass", False: "fail"}
rows = sorted(r for r, o in verdict.items() if len(o) == 2)
plain_pass = [r for r in rows if verdict[r]["plain"]]
print(f"sanity: plain answers still fail on {len(rows) - len(plain_pass)} of {len(rows)} rows" +
      (f" (plain pass on rows {plain_pass}: judge verdict changed between runs)" if plain_pass else ""))
changed = [r for r in rows if verdict[r]["plain"] != verdict[r]["padded"]]
for r in changed:
    print(f"row {r}: plain {word[verdict[r]['plain']]} -> padded {word[verdict[r]['padded']]}")
to_pass = sum(1 for r in changed if verdict[r]["padded"])
print(f"verdict changed by padding: {len(changed)} of {len(rows)} rows "
      f"(fail -> pass {to_pass} rows, pass -> fail {len(changed) - to_pass} rows)")
