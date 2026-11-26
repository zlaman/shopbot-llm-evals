# Helper script, AI-assisted (M04.5): position-bias report from a pairwise judge run on pairs.csv.
# The judge output must start with the letter A or B as a whole word. We map the letter back to the answer it picked:
#   order xy: A = x, B = y      order yx: A = y, B = x
# "Winner changed": after the swap the judge picked a different answer, because it said the same letter
# both times (it followed the position). "Same winner": the same answer won in both orders (it followed the content).
# Usage (from judge-calibration): python3 position_flips.py position-results.json
import json
import re
import sys
from pathlib import Path

data = json.loads((Path(__file__).parent / sys.argv[1]).read_text(encoding="utf-8"))
picks = {}  # pair -> {"xy": "x" or "y", "yx": ...}
letters = {"A": 0, "B": 0}
bad = []
for result in data["results"]["results"]:
    v = result["vars"]
    text = ((result.get("response") or {}).get("output") or "").strip()
    match = re.match(r"(A|B)\b", text)  # "A" or "B." counts; "Answer B" does not (it starts with A!)
    letter = match.group(1) if match else None
    if letter not in letters:
        bad.append((v["pair"], v["order"], text[:60]))
        continue
    letters[letter] += 1
    first, second = v["order"][0], v["order"][1]
    picks.setdefault(int(v["pair"]), {})[v["order"]] = (first if letter == "A" else second, letter)

complete = {p: o for p, o in picks.items() if len(o) == 2}
changed = sorted(p for p, o in complete.items() if o["xy"][0] != o["yx"][0])
for p in changed:
    (xy_pick, xy_letter), (yx_pick, yx_letter) = complete[p]["xy"], complete[p]["yx"]
    print(f"pair {p}: winner changed: order xy said {xy_letter} (picked {xy_pick}), order yx said {yx_letter} (picked {yx_pick})")
total = letters["A"] + letters["B"]
print(f"winner changed: {len(changed)} of {len(complete)} pairs; same winner: {len(complete) - len(changed)} of {len(complete)} pairs")
print(f"picked position A: {letters['A']} of {total} verdicts, position B: {letters['B']} of {total} verdicts")
same = [o["xy"][0] for o in complete.values() if o["xy"][0] == o["yx"][0]]
print(f"both orders (changed winner = tie): x wins {same.count('x')}, y wins {same.count('y')}, tie {len(changed)} of {len(complete)} pairs")
for order in ("xy", "yx"):
    wins = {"x": 0, "y": 0}
    for o in complete.values():
        wins[o[order][0]] += 1
    said_a = sum(1 for o in complete.values() if o[order][1] == "A")
    print(f"order {order} only: said A {said_a} of {len(complete)} pairs -> x wins {wins['x']}, y wins {wins['y']} of {len(complete)} pairs")
for p, o, t in bad:
    print(f"bad output (not A/B): pair {p} order {o}: {t!r}")
