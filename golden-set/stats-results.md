# M02.3 · Statistics for pass rates: results

Script: `golden-set/stats.py` (95% Wilson interval).

## Intervals

```
1/1: 20.7% to 100.0%
2/2: 34.2% to 100.0%
9/10: 59.6% to 98.2%
45/50: 78.6% to 95.7%
90/100: 82.6% to 94.5%
100/100: 96.3% to 100.0%
300/300: 98.7% to 100.0%
```

## What they mean

The Wilson interval gives the range where the real pass rate lies, with 95% confidence. The lower bound
should be used for the quality gate.

In numbers: 9/10, 45/50 and 90/100 are all "90%", but with 10 runs the real rate could be as low as 60%;
with 100 runs it is at least 83%. More runs raise the lower bound and narrow the range. One green run (1/1)
proves almost nothing: 21% to 100%.

## How many runs to tell 90% from 80%

Simulation (`detection_rate` in `stats.py`, 2000 trials per row). Gate: flag a regression if the upper
bound of the 95% Wilson interval is below 90%.

| Runs per build | Regressed build caught (true rate 80%) | False alarm on good build (true rate 90%) |
|---|---|---|
| 10 | 32% | 8% |
| 25 | 40% | 3% |
| 50 | 54% | 3% |
| 100 | 86% | 4% |
| 200 | 99% | 3% |
| 300 | 100% | 2% |

**Answer:** about 100 runs per build catch a 90% → 80% drop at least 80% of the time; 200 runs catch it
almost always. Warm-up guess was 300: the right order of magnitude, more than needed.
A smaller drop (90% → 85%) needs about 4× as many runs.

**Drop size sets the run count.** Any real drop is a regression; the team first agrees on the smallest drop
that matters (a risk decision), and that sets the dataset size. Simulation for a bigger drop, 90% → 70%:
10 runs catch it 62%, 25 runs 81%, 50 runs 96%, 100 runs 100%. So 25 runs reach 80% power vs 100 for a
10-point drop: twice the drop, about 4× fewer runs (runs needed grow with 1 / drop²).

Two different "80%" numbers: *true pass rate 80%* is the regressed build in the scenario; *caught 80% of the
time* is the power target, a common convention (accept missing 1 in 5). 99% power needs about 200 runs.

**Caveat: unique cases vs repeats.** Wilson assumes independent runs. 100 runs = 100 *unique* cases run once.
32 cases × 3 repeats is *not* 96 independent runs: a case that fails once (e.g. the Hawaii exception) tends to
fail again, so the real evidence is between 32 and 96 runs and Wilson with n = 96 is too narrow. Use unique
cases to measure overall quality; use repeats to measure how flaky a single case is (pass^k for high-risk cases).

## Why 10 runs are not enough to call a regression

1. **We can't prove it.** 9/10 gives 59.6% to 98.2% and 8/10 gives about 49% to 94%. The two ranges overlap,
   so the true pass rate could be the same in both builds (for example 80%). We cannot confirm that the second
   build has a regression; the drop could be bad luck.
2. **We can't catch it.** Even when the regression is real (true rate 90% → 80%), 10 runs per build catch it
   in only 32% of builds. The other 68 of every 100 regressed builds pass the gate unnoticed, because an 80%
   build often scores 8/10 or 9/10, the same as a good 90% build.
3. **What to do instead.** Run about 100 *unique* test cases per build (grow the golden set from 32 with
   real user questions, failure categories and reviewed generated cases). That catches a real 90% → 80% drop
   at least 80% of the time (the usual convention); 200 cases catch it about 99% of the time. Repeating the
   same cases doesn't add independent evidence; use repeats only to measure flakiness of single cases.
