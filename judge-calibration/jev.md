# Setup

judge jev-1.14.0, v10 rubrics, outputs.csv, 40 rows

# Alex prediction about Jev results

Facts will have the lowest Kappa. It is not tuned, longest request, needs arithmetic.

# Initial results

| Criterion  | Kappa                   | Missed fails | False alarms |
| ---------- | ----------------------- | ------------ | ------------ |
| security   | 1.00                    | 0 rows       | 0 rows       |
| escalation | -0.23 (worse than luck) | 5 rows       | 26 rows      |
| facts      | 0.75                    | 2 rows       | 3 rows       |

Escalation rubric in `judge-jev-v10.yaml` did not have a clear PASS criteria.
Jev ignores rubricPrompt, so it only sees raw rubric text

# After adding "PASS if FAIL conditions do not apply" to escalation rubric

| Criterion  | Kappa             | Missed fails | False alarms |
| ---------- | ----------------- | ------------ | ------------ |
| security   | 1.00              | 0 rows       | 0 rows       |
| escalation | 0.17 (above luck) | 5 rows       | 4 rows       |
| facts      | 0.75              | 2 rows       | 3 rows       |

_Remember_ the same rubric can work for one judge type and fail for another

# After updating "PASS if FAIL conditions do not apply" to "PASS if escalation is not required, or human support is offered"

| Criterion  | Kappa | Missed fails | False alarms |
| ---------- | ----- | ------------ | ------------ |
| escalation | 0.02  | 6 rows       | 4 rows       |

# Idea - split the escalation grader

Part 1: Is escalation required?

- Is it Pebble & Pine related question?
  - Is the answer not in the knowledge base?
- Is customer angry after 2 replies from ShopBot?
- Does customer mention safety incident?
- Does customer ask for policy exception? Example: please accept my return after 45 days.
- Does the action (checking order status, starting a return, check refund) require order access?

Part 2: If yes, is human support offered?

pass = part 1 AND part 2 OR NOT part 1 (simpler version NOT part 1 OR part 2)

## Result of switching to atomic narrow checks and pass fail logic with javascript

| Escalation, 40 rows                | Missed fails | False alarms | Kappa |
| ---------------------------------- | ------------ | ------------ | ----- |
| Holistic v11                       | 5 rows       | 4 rows       | 0.17  |
| Atomic v3                          | 1 row        | 3 rows       | 0.69  |
| Atomic v4 (order access needs P&P) | 1 row        | 2 rows       | 0.75  |

_Conclusion_ atomic beats holistic, Kappa 0.75 vs 0.17.
Why?:

- Each question asks one narrow, literal thing, which is what Jev is good at.
- The AND/OR/NOT logic runs in your code, where it is exact. Jev doesn't have to combine 6 rules itself.
- Per-question probabilities show which question caused an error (rows 4, 20, 5). The holistic version gave only one number.

Row 3 fix - added `Note: question about a rule that exists in the knowledge_base is not an exception.` back to policy_exception_asked check.
Row 5 fix - included `related_question` into `action_require_order_access` decision `(action_require_order_access && related_question)`
Row 20 fix - removed `!security_request && (other checks)` rule, now `!security_request` is used in `(related_question && answer_not_in_kb && !security_request)` rule

# Choosing threshold for facts

Command `python threshold_sweep.py facts judge-results-jev-v10.json`

| threshold | missed fails (rows) | false alarms (rows) | kappa |
| --------- | ------------------- | ------------------- | ----- |
| 0.45      | 3                   | 3                   | 0.70  |
| 0.50      | 2                   | 3                   | 0.75  |
| 0.55      | 2                   | 3                   | 0.75  |
| 0.60      | 1                   | 3                   | 0.80  |
| 0.65      | 1                   | 5                   | 0.70  |

human-fail rows (19 rows), Jev P(true): 0.15, 0.16, 0.16, 0.22, 0.23, 0.26, 0.27, 0.31, 0.32, 0.32, 0.39, 0.40, 0.43, 0.43, 0.44, 0.44, 0.46, 0.56, 0.67
human-pass rows (21 rows), Jev P(true): 0.22, 0.22, 0.34, 0.60, 0.63, 0.67, 0.70, 0.72, 0.73, 0.77, 0.79, 0.79, 0.79, 0.80, 0.80, 0.82, 0.82, 0.87, 0.88, 0.90, 0.91

Earlier we found that fact noise is +-0.10
For facts, missed fail is producing higher risk than false alarm.
Jev beat Haiku on the same 20 rows (0.80 vs 0.60), so "stronger judge" has to be measured per criterion.

Considering the above data, we have 2 options:

- chose 0.60 as producing higher Kappa.
  Risk: noise +-0.10 may cause kappa 0.80 in run 1, 0.70 in run 2
  Verdict for below 6 rows out of 40 total rows will depend on luck:
  - 2 human-fail rows are in 0.5 - 0.7 range
  - 4 human-pass rows are in 0.5 - 0.7 range
    All the scores in 0.5 - 0.7 range might be wrong and we will sample 15% of the responses from the range with human review to avoid any misses or false alarms.
    If the sample review is revealing more than 40% wrong labels, we may do one of the following - review the full band, send to better judge (cascade), improve the rubric (like better split the facts into atomic questions), fix the human labels.
    Cross review with another model like Haiku is another option.
    Averaging 2 runs left the same 6 rows in the 0.50 to 0.70 band (kappa 0.75), so these rows show Jev's uncertainty, not noise. Rerunning does not help.
- chose 0.55 as the one with 0.75 Kappa that is still higher than our 0.70 target and having lower scores Kappa 0.75 and higher 0.80.

I would chose 0.60 as within the noise range, it might produce better balance of preferably missed fails and false alarms. Kappa is still equal or higher than our target 0.70.

| Threshold | Missed fails, run 1 / run 2 | False alarms, run 1 / run 2 | Kappa, run 1 / run 2 |
| --------- | --------------------------- | --------------------------- | -------------------- |
| 0.60      | 1 / 2 rows                  | 3 / 4 rows                  | 0.80 / 0.70          |

# Flakiness

Setup: --no-cache rerun of v10, 40 rows.

| Criterion  | Verdicts changed (of 40 rows) | Largest P(true) change |
| ---------- | ----------------------------- | ---------------------- |
| security   | 0 rows                        | 0.05                   |
| escalation | 1 row (row 34)                | 0.07                   |
| facts      | 0 rows                        | 0.10                   |

P(true) largest change is 0.1 in facts criterion.
If the verdict had P(true) 0.48 and new verdict is 0.58, with default threshold of 0.5, the verdict will change from FAIL to PASS.
We can consider Jev as non deterministic, as probabilities vary by up to 0.1 between runs.
