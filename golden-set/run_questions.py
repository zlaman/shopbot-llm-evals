"""M02.1 runner (helper script, AI-assisted): ask ShopBot each question once and save a notes template.

Input:  golden-set/questions.txt, groups separated by blank lines; the first line of a group is its name.
Output: golden-set/error-analysis.md (one section per question, with an empty Note line to fill in)
        golden-set/answers.json     (raw run record, so later steps can diff against it)
Usage:  .venv/bin/python golden-set/run_questions.py [--force]
"""

import json
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "shopbot"))
from shopbot import answer

HERE = Path(__file__).parent
QUESTIONS_FILE = HERE / "questions.txt"
REPORT_FILE = HERE / "error-analysis.md"
RAW_FILE = HERE / "answers.json"


def load_questions():
    cases, group, new_group = [], None, True
    for line in QUESTIONS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            new_group = True
        elif new_group:
            group, new_group = line, False
        else:
            cases.append({"id": len(cases) + 1, "group": group, "question": line})
    return cases


def main():
    if REPORT_FILE.exists() and "--force" not in sys.argv:
        sys.exit(f"{REPORT_FILE.name} exists; it may hold your notes. Use --force to overwrite.")

    cases = load_questions()
    for case in cases:
        print(f"[{case['id']}/{len(cases)}] {case['question']}", flush=True)
        case["answer"] = answer(case["question"]).strip()

    RAW_FILE.write_text(json.dumps(cases, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# M02.1 · Error analysis",
        "",
        f"- Date: {date.today()}. ShopBot v1, Gemma 4 E4B Q4_0, temp 1.0, one sample per question.",
        "- Goal: find *kinds* of failure, not rates.",
        "",
        "## Questions, answers, notes",
        "",
    ]
    for case in cases:
        quoted = "\n".join(f"> {row}" if row else ">" for row in case["answer"].splitlines())
        lines += [
            f"### {case['id']} · {case['group']} · {case['question']}",
            "",
            quoted,
            "",
            "**Note:** ",
            "",
        ]
    lines += [
        "## Failure taxonomy",
        "",
        "| Category | Count | Example (#) |",
        "|---|---|---|",
        "",
        "**Highest business risk:** ",
        "",
    ]
    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Saved {REPORT_FILE} and {RAW_FILE}")


if __name__ == "__main__":
    main()
