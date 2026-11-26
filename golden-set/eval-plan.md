# Eval plan (test strategy)

1. What can go wrong, ranked by risk
2. How we measure each risk (metric + grader)
3. The dataset and how it grows
4. Gates: concrete numbers, with the uncertainty
5. How often it runs (PR, nightly, release)
6. Who reviews failures, and the dashboard

## Summary

- Top risks are security and financial mismatch in the output.
- Release gate - block if bottom of the Wilson range for the run pass rate is < 80%.
- Regression gate - block if the top of the Wilson range is < 90%.
- Target test case count - 100, will relax the release and regression gate rules.

## Risks

Rank = impact × how often you saw it.
High risk = impact 3, high-impact risks with no evidence yet rank at the top until tested
Medium risk = impact 2
Low risk = impact 1

| Risk                                                                         | Failure category          | Impact                                                                  | Seen                    | Rank                                     |
| ---------------------------------------------------------------------------- | ------------------------- | ----------------------------------------------------------------------- | ----------------------- | ---------------------------------------- |
| Security                                                                     | Security                  | High: leaking of the system prompt, staff discount code, etc            | 0 (4 mild cases passed) | Top: high impact, not yet measured (M08) |
| Bot does not correctly reply the financial related information (costs, fees) | Financial mismatch        | High: causing customer dissatisfaction when gets cleared up, legal fees | 3                       | 9                                        |
| Bot does not respond with complete information about all cases               | Incomplete answer         | High: customer does not get full information                            | 2                       | 6                                        |
| Bot does not mention all the rule exception(s)                               | Missed rule exception     | High: customer does not get full information                            | 2                       | 6                                        |
| Bot does not escalate to human when required                                 | Missed human escalation   | Medium: customer does not get support                                   | 2                       | 4                                        |
| Bot does not communicate boundaries clearly                                  | Missed boundary           | High: customer does not get full information                            | 1                       | 3                                        |
| Bot replies in a contradictory way                                           | Contradictory information | Medium: causing customer confusion and escalations to support           | 1                       | 2                                        |

_Note_ Counts come from about 20 answers, so the ranking is a first estimate. Re-rank after the 100-case run.

## How we measure each risk

| Risk                      | Metric                                                       | Grader                                                |
| ------------------------- | ------------------------------------------------------------ | ----------------------------------------------------- |
| Financial mismatch        | pass rate on cases tagged money = yes                        | deterministic for amounts, rubric for the explanation |
| Missed rule exception     | pass rate on cases with missed rule exception category       | deterministic                                         |
| Incomplete answer         | pass rate on cases with incomplete answer category           | deterministic                                         |
| Missed human escalation   | pass rate on cases with "missed human escalation" category   | rubric                                                |
| Missed boundary           | pass rate on cases with "missed boundary" category           | mostly rubric                                         |
| Contradictory information | pass rate on cases with "contradictory information" category | rubric                                                |

_Note_ Case counts and ranges are shown in the run report, computed on every run.

## Dataset and how it changes

- Dataset: golden-set/golden.csv, 32 cases today, stored in git.
- Target: 100 cases, 80% of cases cover high-impact risks (impact 3 in the Risks table), at least 15 cases for each high-impact risk.
- New cases come from: every customer complaint, a thumbs-down, or a support ticket about a wrong answer in production becomes a new case. Plus 10 new edge cases per sprint, reviewed by a lead.
- Kept correct: when the knowledge base policy changes, review the cases it affects.

## Gates

### Release gate

The bottom of the Wilson range for the run pass rate must be >= 80%.
Passing results: 32/32 (bottom 89.3%) and 31/32 (bottom 84.3%).
Failing results: 30/32 (bottom 79.9%).

_Note_ With 32 cases this gate blocks most good builds. It becomes practical at 100 cases.

### Regression gate

Baseline = last accepted build, 90% on 32 cases as a first estimate. Block if the top of the new range is < 90%.
Passing results: 26/32 (top 91.1%).
Failing results: 25/32 (top 89.0%).

_Note_ Re-measure the baseline when the dataset is updated.

### Uncertainty

A gate is reliable if it catches the pass rate drop on at least 80 of 100 builds (team decision).
Our gate can miss real problems, and this section says which ones.
With 32 cases, it reliably catches big drops (90% → 70%), but misses small drops (90% → 80%) about half the time.
But we don't know the old build is at 90%. With 32 cases, it could be anywhere from 75% to 96%.

```
90% → 80% (10-point drop): caught on 48 of 100 builds → not reliable
90% → 70% (20-point drop): caught on 89 of 100 builds → reliable
```

With 100 cases, it catches small drops too. That's why the dataset target is 100.

- Pass rate drop from 90% to 80% (10 percentage points): caught on 87 of 100 builds.

## How often we run tests

- Every unmerged PR as part of VCS CI status checks: all deterministic cases, high risk cases with Jev as a judge, no LLM as a judge.
  -- When PR has a new model or system prompt update: we run fill set. Code owner(s) approves the big changes like a new model or system prompt.
- Every CI build after merging the PR to main: the full set, including deterministic cases, Jev and LLM judge.
- Before prod deployment: full set.

_Note_ for the gates, each case runs once. High-risk cases (money, security) also run 5 times after each merge, and each must pass all 5 runs.

## Who reviews the failures, dashboard

### Who reviews

Human is reviewing sample of judge grades every week to check that judge is still right.
On call eval suite developer reviews red builds within 2hrs.
Money failures are reviewed with lead eval developer.

### Observability dashboard

UI dashboard is created to present current and previous data for:

- Eval run actual pass rate (like 32/32)
- Eval run metrics like SUT model metrics, build metrics.
- Detailed result of every test in the eval run
- Wilson score intervals that show 95% chance pass rates - if regression (upper bound) and release (lower bound) gates are met

## Grader validation (before a judge gates anything)

### Labels — criteria.md, labels.csv, 40 rows

### Agreement bar — kappa per criterion, disagree-row review (agreement.md)

### Repeatability — reruns, changed verdicts, kappa as a range

### Bias probes — position, verbosity (biases.md)

### Judge choice — per criterion (judge-decision.md)

### When to re-validate — triggers
