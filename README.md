# ShopBot LLM evals

Evaluation and testing work for **ShopBot**, a customer-support chatbot for a fictional outdoor-gear
store, Pebble & Pine Outfitters. ShopBot answers policy questions (returns, shipping, warranty, loyalty
points) from a small knowledge base. It runs on a local model, so every eval here is free to run.

This repo shows how I test an LLM app the way I test any other system: risk first, real failure data,
deterministic checks where they work, and an LLM judge only after it is measured against human labels.

| Folder | What it shows |
| --- | --- |
| [`shopbot/`](shopbot/) | The app under test: one Python file, OpenAI-compatible client, whole knowledge base in the prompt |
| [`assets/`](assets/) | The fictional company: knowledge base, system prompt, mock orders |
| [`golden-set/`](golden-set/) | Error analysis, a 32-case golden dataset, pass-rate statistics, the eval plan |
| [`promptfoo-suite/`](promptfoo-suite/) | Promptfoo suites that call the real app, a prompt × model comparison, flaky-test triage |
| [`judge-calibration/`](judge-calibration/) | Human labels, an LLM judge, agreement (kappa), bias probes, a judge comparison with cost |
| [`scripts/`](scripts/) | Start and stop the local `llama-server` processes |

## Stack

- **Model under test:** Gemma 4 E4B (4-bit), served by llama.cpp `llama-server` on a laptop GPU (8 GB VRAM)
- **Local judge:** Gemma 4 12B (4-bit), temperature 0
- **Eval tools:** Promptfoo 0.125.1, Python 3.12
- **Other judges compared (small runs):** Claude Haiku 5.5 (`claude-haiku-5-5`), Claude Sonnet 5.5
  (`claude-sonnet-5-5`), Claude Opus 5.5 (`claude-opus-5-5`), Claude Fable 5.2 (`claude-fable-5-2`),
  TypeSafe Jev 1.14.0 (`typesafe:jev-1.14.0`)

## Results

### 1. Golden set and eval plan ([`golden-set/`](golden-set/))

- **Error analysis first:** I read about 20 real ShopBot answers before choosing any metric. The result
  is 7 failure categories, such as "financial mismatch", "missed rule exception" and "missed human
  escalation" ([`error-analysis.md`](golden-set/error-analysis.md)).
- **Golden dataset:** 32 cases in 8 case types (fact, boundary, multi-hop, ambiguous, false-premise,
  out-of-scope, adversarial-lite, tone). Each case has an expected behavior and a grader type
  ([`golden.csv`](golden-set/golden.csv)).
- **Pass-rate statistics:** a 95% Wilson interval shows how little a small run proves. A pass rate of 90%
  from 10 runs has a real pass rate between 59.6% and 98.2%; from 100 runs, between 82.6% and 94.5%
  ([`stats-results.md`](golden-set/stats-results.md)).
- **Eval plan:** risks ranked by impact × how often they were seen, one metric and grader per risk, and
  gates on the Wilson lower bound, not on the raw pass rate ([`eval-plan.md`](golden-set/eval-plan.md)).

### 2. Promptfoo suite ([`promptfoo-suite/`](promptfoo-suite/))

- **Test the app, not the bare model:** the suite calls `shopbot.py` through a Python provider. A broken
  system prompt in the app is caught; a bare-model test would build its own prompt and miss it.
- **Prompt × model comparison:** 2 system prompts × 2 models × 3 runs × 32 cases. Prompt B adds one
  line: "calculate the final number and state it".

  | Case | Original prompt | Prompt B |
  | --- | --- | --- |
  | golden #9 (shipping after a discount), E4B, 100 runs each | 35 of 100 runs failed | 21 of 100 runs failed |
  | golden #16 (points calculation), E4B, 100 runs each | 5 of 100 runs failed | 1 of 100 runs failed |

  Decision: prompt B is now in production. It failed no case that the original prompt passed.
  The smaller E2B model is faster (mean latency 517 ms vs 868 ms per answer) but **leaked the staff
  discount code in 3 of 12 runs**, so it is unsafe to ship ([`comparison.md`](promptfoo-suite/comparison.md)).
- **Flaky-test triage:** each failing case is sorted into "consistent fail", "flaky (product)" or
  "test bug", with a quoted output as evidence. Example: golden #4 failed once because the grader wanted
  "5025" and the right answer said "$5,025": a test bug, not a product bug ([`flaky.md`](promptfoo-suite/flaky.md)).

### 3. Judge calibration ([`judge-calibration/`](judge-calibration/))

- **Human labels first:** 40 saved answers × 3 criteria (security, escalation, facts) = 120 human labels,
  with a written label guide ([`criteria.md`](judge-calibration/criteria.md), [`labels.csv`](judge-calibration/labels.csv)).
- **Agreement measured with Cohen's kappa**, which counts only agreement above luck. My own script
  ([`agreement.py`](judge-calibration/agreement.py)) also lists missed fails and false alarms per row.
- **Before and after rubric work**, local 12B judge, same 40 answers:

  | Criterion | Kappa, first rubric (`judge.yaml`) | Kappa, calibrated rubric (`judge-v8-escalation.yaml`) |
  | --- | --- | --- |
  | security | 0.72 | 1.00 |
  | escalation | 0.15 | 1.00 |
  | facts | 0.28 | 0.65 |

  Honest limit: the rubrics were tuned and measured on the same 40 answers (no hold-out set yet), and
  security has only 5 failing answers, so kappa 1.00 is optimistic ([`agreement.md`](judge-calibration/agreement.md)).
- **Bias probes** ([`biases.md`](judge-calibration/biases.md)):
  - Position bias, 32 answer pairs × 2 orders = 64 judge calls: the 12B judge gave the same winner in
    both orders for only 13 of 32 pairs. One order alone gave opposite conclusions about which prompt is
    better. Rule: run both orders; a changed winner counts as a tie.
  - Verbosity bias: polite filler text around 15 failing answers changed 0 of 15 verdicts.
- **Judge comparison with cost** ([`judge-decision.md`](judge-calibration/judge-decision.md), [`jev.md`](judge-calibration/jev.md)):

  | Judge | Escalation kappa | Facts kappa | $ per 1000 judgments | Latency per call |
  | --- | --- | --- | --- | --- |
  | Local Gemma 4 12B | 1.00 | 0.26 | free | 2160 ms (mean) |
  | Claude Haiku 5.5 | 0.63 | 0.60 | 0.916 (API estimate) | 5250 ms (mean) |
  | TypeSafe Jev, one rubric per criterion | −0.52 | 0.80 | 0.048 | 200 ms (mean) |
  | TypeSafe Jev, atomic escalation questions | 0.68 | n/a | 0.060 | 53 ms (median) |

  Kappa here is on the same 20 hard answers for every judge. Splitting the escalation rubric into small
  yes/no questions with pass/fail logic in code raised Jev's escalation kappa from 0.17 to 0.75 on 40
  answers. Lesson: the same rubric can work for one judge type and fail for another, so every judge
  needs its own check against the labels.

  I wrote up the Jev part of this comparison in a LinkedIn article:
  [I tested TypeSafe Jev as an eval judge: cost, speed and one rubric lesson](https://www.linkedin.com/pulse/i-tested-typesafe-jev-eval-judge-cost-speed-one-rubric-zaika-1jqwc/).

## Setup

Requirements: Python 3.12, Node.js (for Promptfoo), llama.cpp `llama-server`, a GPU with about 8 GB VRAM.

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
npm install                      # Promptfoo 0.125.1 (pinned in package.json)
cp .env.example .env             # local server URLs; a Jev key only if you run the Jev configs
```

`scripts/start-servers.sh` starts the Windows build of `llama-server` from WSL. On Linux or macOS, use
the same flags with your own `llama-server` binary.

```bash
bash scripts/start-servers.sh sut      # model under test, port 8080
.venv/bin/python shopbot/shopbot.py "Is shipping free on a \$74.99 order?"

# Promptfoo suite against the live app (run from its folder)
cd promptfoo-suite && npx promptfoo eval -c shopbot-golden.yaml

# Judge calibration on saved answers (stop the model under test first: the 12B judge needs the GPU)
bash scripts/start-servers.sh stop && bash scripts/start-servers.sh judge
cd judge-calibration
npx promptfoo eval -c judge-v8-escalation.yaml -o judge-results-v8.json
../.venv/bin/python agreement.py judge-results-v8.json
```

## About this repo

I built this repo as part of a self-directed AI quality-engineering study plan. File comments with step
IDs like `M03.4` refer to steps of that plan. Helper scripts marked "AI-assisted" were written with an AI
coding assistant; the test design, labels, rubrics, analysis and decisions are my own work.
All company names, policies, codes and contact details are invented.

The repo grows with each module. Next: DeepEval test suites, RAG evaluation, agent testing, red-teaming
and CI regression gates.
