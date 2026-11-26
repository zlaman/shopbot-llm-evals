# Helper script, AI-assisted (M04.5): builds padded.csv for the verbosity-bias probe.
# Rows: the 15 outputs.csv rows where BOTH your facts label and the 12B v8 facts verdict are "fail"
#   (2, 10, 16, 17, 23, 24, 26, 28, 29, 32, 33, 34, 35, 39, 40), so a later "pass" can only come from the padding.
# Each row appears twice: version "plain" (original answer) and version "padded" (filler + answer + filler).
# filler.txt: line 1 = text added BEFORE the answer, line 2 = text added AFTER the answer.
# 15 rows x 2 versions = 30 rows. Usage (from judge-calibration): python3 make_padded.py
import csv
from pathlib import Path

HERE = Path(__file__).parent
ROWS = {2, 10, 16, 17, 23, 24, 26, 28, 29, 32, 33, 34, 35, 39, 40}
before, after = (HERE / "filler.txt").read_text(encoding="utf-8").splitlines()[:2]

out = []
for row in csv.DictReader(open(HERE / "outputs.csv", encoding="utf-8")):
    if int(row["row"]) in ROWS:
        for version in ("plain", "padded"):
            answer = row["answer"] if version == "plain" else f"{before} {row['answer']} {after}"
            out.append({"row": row["row"], "version": version, "question": row["question"],
                        "expected_behavior": row["expected_behavior"], "answer": answer})

with open(HERE / "padded.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(out[0]))
    writer.writeheader()
    writer.writerows(out)
print(f"padded.csv: {len(out) // 2} rows x 2 versions = {len(out)} rows")
