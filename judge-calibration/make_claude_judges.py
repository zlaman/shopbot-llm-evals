# Helper script, AI-assisted (M04.4): builds the Claude judge configs and the 20-row subset.
# - outputs-20.csv: 20 rows of outputs.csv (all escalation fails, the v8 facts disagreements,
#   the hard escalation passes, 2 clean facts fails). Harder than the full 40 rows on purpose.
# - judge-claude-<model>.yaml: the SAME escalation + facts rubrics as judge-v8-escalation.yaml
#   (copied from it, so they can't drift), graded by Claude through the Agent SDK + Pro login.
# Usage (from judge-calibration): python3 make_claude_judges.py
import csv
from pathlib import Path

import yaml

HERE = Path(__file__).parent
ROWS = ["1", "2", "4", "5", "6", "7", "9", "12", "13", "14",
        "15", "16", "18", "19", "20", "24", "27", "30", "31", "39"]
MODELS = {  # file suffix -> model id
    "haiku": "claude-haiku-5-5",
    "sonnet": "claude-sonnet-5-5",
    "opus": "claude-opus-5-5",
    "fable": "claude-fable-5-2",
}

# 1. subset
with open(HERE / "outputs.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fields, rows = reader.fieldnames, [r for r in reader if r["row"] in ROWS]
with open(HERE / "outputs-20.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
assert len(rows) == 20, len(rows)

# 2. configs
v8 = yaml.safe_load(open(HERE / "judge-v8-escalation.yaml", encoding="utf-8"))
rubrics = [a for a in v8["defaultTest"]["assert"] if a.get("metric") in ("escalation", "facts")]


class Literal(str):
    pass


yaml.add_representer(Literal, lambda d, s: d.represent_scalar("tag:yaml.org,2002:str", s, style="|"))

for name, model in MODELS.items():
    cfg = {
        "description": f"Claude judge ({model}) on 20 rows, v8 escalation + facts rubrics",
        "prompts": ["{{answer}}"],
        "providers": ["echo"],
        "tests": "file://outputs-20.csv",
        "defaultTest": {
            "vars": {"kb": "file://kb-all.md"},
            "options": {"provider": {
                "id": "anthropic:claude-agent-sdk",
                "config": {
                    "model": model,
                    "apiKeyRequired": False,   # use the Claude Code login (Pro), not an API key
                    "tools": [],               # pure text judge: no file, bash or web tools
                    "max_turns": 1,
                    "setting_sources": [],     # don't load CLAUDE.md or project settings
                    "persist_session": False,  # don't save judge sessions to ~/.claude/projects
                    "custom_system_prompt": "",  # no Claude Code system prompt: the local judge has none either
                },
            }},
            "assert": [{"type": "llm-rubric", "metric": a["metric"], "value": Literal(a["value"])}
                       for a in rubrics],
        },
        "evaluateOptions": {"maxConcurrency": 1},
    }
    out = HERE / f"judge-claude-{name}.yaml"
    out.write_text(yaml.dump(cfg, sort_keys=False, allow_unicode=True, width=1000), encoding="utf-8")
    print("wrote", out.name)
print("wrote outputs-20.csv:", len(rows), "rows")
