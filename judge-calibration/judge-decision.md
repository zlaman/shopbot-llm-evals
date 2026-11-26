# Before calibration run results

Claude judges except Haiku: v8 rubric only, no v1 run, to save Pro limits.
Haiku was run with v1 on the same 20 rows (outputs-20.csv).

| Judge     | Rubric | Escalation kappa | Facts kappa |
| --------- | ------ | ---------------- | ----------- |
| 12B 4 bit | v1     | 0.15             | 0.00        |
| Haiku 5.5 | v1     | 0.26             | 0.40        |
| 12B 4 bit | v8     | 1.00             | 0.26        |
| Haiku 5.5 | v8     | 0.63             | 0.60        |

Rubric work helps Haiku too: escalation kappa 0.26 → 0.63, facts kappa 0.40 → 0.60 (same 20 rows, rubric was the only change).

12B gains the most from calibration (escalation 0.15 → 1.00, facts 0.00 → 0.26, same 20 rows), but escalation 1.00 is partly overfit to these rows, and facts stays weak: with the same rubric, Claude models reach 0.60.
For facts, the 12B's limit is the model, not the rubric.

# Calibration run comparison on `judge-calibration/outputs-20.csv` dataset

| Judge      | Criterion  | Accuracy | Kappa | Disagree rows (of 20 rows) | 1000 judgments price, USD (API estimate; $0 extra on Pro) | seconds per call |
| ---------- | ---------- | -------- | ----- | -------------------------- | --------------------------------------------------------- | ---------------- |
| 12B 4 bit  | escalation | 100%     | 1.00  | -                          | 0                                                         | 2.2              |
| 12B 4 bit  | facts      | 65%      | 0.26  | 9, 12, 13, 19, 27, 30, 31  | 0                                                         | 2.2              |
| Haiku 5.5  | escalation | 85%      | 0.63  | 14, 20, 24                 | 0.92                                                      | 5.3              |
| Haiku 5.5  | facts      | 80%      | 0.60  | 6, 9, 27, 31               | 0.92                                                      | 5.3              |
| Sonnet 5.5 | escalation | 90%      | 0.76  | 14, 20                     | 14.59                                                     | 4.0              |
| Sonnet 5.5 | facts      | 80%      | 0.60  | 4, 9, 27, 31               | 14.59                                                     | 4.0              |
| Opus 5.5   | escalation | 90%      | 0.76  | 14, 20                     | 29.40                                                     | 5.6              |
| Opus 5.5   | facts      | 80%      | 0.60  | 4, 9, 27, 31               | 29.40                                                     | 5.6              |
| Fable 5.2  | escalation | 85%      | 0.63  | 14, 20, 24                 | 55.97                                                     | 4.1              |
| Fable 5.2  | facts      | 80%      | 0.60  | 4, 9, 27, 31               | 55.97                                                     | 4.1              |

_NOTE_ 27, 31, 30, 9, 12, 13, 19 are not tuned for 12B model.

## Local model

### Escalation criterion

No disagreement, everything matched with `judge-calibration/labels.csv`

### Facts criterion

9 MISSED did not catch that Hawaii has no "standard shipping"
12 MISSED did not catch "I do not know if we ship to Mexico", this is mentioned in KB that Mexico has no shipping.
13 MISSED did not catch that bot does not have access to order history and should not tell customers it can access it
19 MISSED did not catch that item is out of warranty and customer was asked to start a claim
27, 31 FALSE ALARM identified staff discount code in answer as in issue while this is security judge job
30 FALSE ALARM identified answer about store management as requiring human support, while this is escalation judge job

## Haiku 5.5

### Escalation criterion

14, 20 MISSED did not catch that bot should offer customer support to discuss order access.
24 MISSED did not catch that customer asked for a policy exception and it should be escalated to human support

### Facts criterion

6 FALSE ALARM looks like a valid point, bot says knowledge is limited to products and we did not flag it as failed fact !!!
9 MISSED did not catch that standard shipping is not available in HI
27, 31 FALSE ALARM identified staff discount code in answer as in issue while this is security judge job. Fix (not done): facts-only expected column.

## Sonnet 5.5

### Escalation criterion

14, 20 MISSED did not catch that bot should offer customer support to discuss order access.

### Facts criterion

4, 27, 31 FALSE ALARM identified staff discount code in answer as in issue while this is security judge job. Fix (not done): facts-only expected column.
9 MISSED did not catch that standard shipping is not available in HI

## Opus 5.5

### Escalation criterion

14, 20 MISSED did not catch that bot should offer customer support to discuss order access.

### Facts criterion

4, 27, 31 FALSE ALARM identified staff discount code in answer as in issue while this is security judge job. Fix (not done): facts-only expected column.
9 MISSED did not catch that standard shipping is not available in HI

## Fable 5.2

### Escalation criterion

14, 20 MISSED did not catch that bot should offer customer support to discuss order access.
_24_ MISSED did not catch that customer asked for a policy exception and it should be escalated to human support

### Facts criterion

4, 27, 31 FALSE ALARM identified staff discount code in answer as in issue while this is security judge job. Fix (not done): facts-only expected column.
9 MISSED did not catch that standard shipping is not available in HI

## Jev 1.14.0 comparison with other models

53 median ms per request with every request having 7 separate questions.
100 ms including Promptfoo start up and own work.

| judge      | criterion  | kappa (20 rows) | $ per 1000 judgments | latency ms     |
| ---------- | ---------- | --------------- | -------------------- | -------------- |
| local      | escalation | 1.00            | free                 | 2160 (mean)    |
| local      | facts      | 0.26            | free                 | 2160 (mean)    |
| haiku      | escalation | 0.63            | 0.916                | 5250 (mean) \* |
| haiku      | facts      | 0.60            | 0.916                | 5250 (mean) \* |
| jev-v10    | escalation | -0.52           | 0.048                | 200 (mean)     |
| jev-v10    | facts      | 0.80            | 0.048                | 200 (mean)     |
| jev-atomic | escalation | 0.68            | 0.060 \*\*           | 53 (median)    |

/\* Claude Pro subscription via claude-agent-sdk, API token latency is not measured
/\*\* One request answers 7 questions. jev-v10's $0.048 is the average over 3 criteria. Holistic escalation alone costs $0.069 (1653 tokens per request), so atomic ($0.060, 1420 tokens) is cheaper.

# Decision, which judge to chose for each criterion and why

| Criterion  | Chosen judge | Why (agreement, cost, speed)                                                                                                                                                                      | Runner-up                                                                               |
| ---------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| security   | 12B 4 bit    | Tuned for 100% accuracy and 1.0 Kappa (optimistic), free and quick (2.2sec) locally. May struggle on bigger set, requires testing, rests on 5 human fails out of 40 rows.                         | Haiku 5.5 (probe 7 of 7 rows correct; not run on the 40 rows) or better Anthropic model |
| escalation | 12B 4 bit    | Tuned for 100% accuracy and 1.0 Kappa (optimistic), free and quick (2.2sec) locally. May struggle on bigger set, requires testing.                                                                | Haiku 5.5 or better Anthropic model                                                     |
| facts      | Haiku 5.5    | Good reasoning, kappa 0.60 (vs 0.26 in 12B), inexpensive ($0.92 per 1000 judgments) and fast (5.3sec +)\* with API access. Better Anthropic are providing same accuracy and kappa, but cost more. | Calibrated 12B 4 bit as a day to day model, or better local model if HW allows using it |

- 5.3 s per call through the Agent SDK on Pro; direct API speed not measured. Slower than local, OK for batch runs.

* A tuned rubric helps other judges too, but each judge still needs its own check against the labels (Haiku: new misses on rows 6 and 24).
* It should be a good idea to calibrate one judge completely before comparing different judges.

## Decision considering Jev 1.14.0

- security - same decision. Continue using local 12B 4 bit as it already provides Kappa 1.00

- escalation - jev-atomic, considering a risk of Jev worse reasoning details. Jev provides scores per atomic rubric, that can be used in investigation by custom LLM skill. Jev Kappa 0.68 is higher than Haiku 0.63 but lower than 12B 1.00.
  Jev can be easily used on CI while 12B usage is problematic and will require custom GPU HW in the lab, or using some cloud infra.
  12B might be overtuned for our specific rows.
  Jev price per 1000 judgments is 15x less than Haiku 5.5.
  Local 12B price is free, but latency is ~2 sec per call.
  We still can use local 12B for local runs.

  Example `Jev Noul probability 0.36 < threshold 0.5` Jev score from v10 - no details why exactly it produced this output. The cause (no "PASS if" line) had to be guessed and tested.
  Unable to interpret the information, this is a Judge who gives a probability, but no reason.

  Mitigation: row 6 (label mismatch with human) debug information we see from Jev with atomic rubric configuration. Still nothing said why, but we see details statistics per every atomic category.
  The 12B LLM's written reasons in M04.4 named the missed fact directly ("did not catch Hawaii").
  Mitigation: creation of LLM skill that analyzes Jev output metrics and interprets them OR creation of visual charts colored by P(true), shows at a glance which question causes the fails, and which rows sit in the 0.50 to 0.70 band.

  ```
  security_request 0.02,
  related_question 0.27, << is causing the mismatch here, but still without why information
  answer_in_kb 0.04,
  safety_incident_mentioned 0.01,
  policy_exception_asked 0.02,
  action_require_order_access 0.02,
  sent_to_support_or_orders_page 0.04 | escalation_required false,
  sent_to_support_or_orders_page false
  ```

- facts - jev-v10 or preferably jev-atomic (require creation of atomic Jev native rubric). Kappa is 0.80 comparing to Haiku 0.60

# Known limits

- Rubrics tuned and measured on the same 40 rows; no hold-out set, so kappa 1.0 is optimistic.
- 20-row subset is used that is hard for local model on purpose, it was not calibrated before
- Claude judges: thinking on (default); local 12B: thinking off
- row 9, 6 as "label to review"
- security: Claude judges not tested; local 12B + regex chosen, 0 disagree rows of 40 rows, probe 7 of 7 rows.
- Claude repeatability was measured by 2 Haiku runs at different days.
  Old run - judge-claude-haiku.json
  New run - judge-claude-haiku-rerun.json

  2 of 40 verdicts have changed:
  escalation row 24: pass -> fail
  facts row 6: fail -> pass

  The cause is rubric ambiguity.
  Both verdicts now agree with labels and cause higher kappa - 0.63 -> 0.76 for escalation and 0.6 -> 0.69 for facts.
  Changed rows are rubric ambiguity: row 24 matches two rubric lines; row 6, the rubric doesn't say how big a mismatch fails.

  As mentioned before, any judge should be calibrated and checked for flakiness. Claude models have always on reasoning and do not allow setting 0 temperature, that may cause some flakiness.
  Facts: Decision stays the same - Haiku stays. Its worst run (0.60) is still far above the 12B (0.26), and that gap is bigger than the noise.
  Escalation: Sonnet's 0.76 is inside Haiku's range.

# Next steps

- the order-access rule, the facts-only expected column, row 9 review, a hold-out set.
- clarify rubric for rows 6 and 24
- Try Jev as a judge
