1. Honest run summary
   For now we only implemented running deterministic checks for our golden.csv dataset.
   We have 32 tests in golden.csv. Out of them 18 have either `must_include` either `must_not_include` populated and are already graded. Remaining 14 will be run later, when we implement rubric grader.
2. Failures by category
   Source: 3 runs (2 runs × 32 cases, 1 filtered run × 18 checked cases). Not-graded cases are counted from `golden.csv`.

   | category         | checked cases | checked cases failed in at least 1 of 3 runs | failed cases (runs failed)         | not graded yet (M04) |
   | ---------------- | ------------- | -------------------------------------------- | ---------------------------------- | -------------------- |
   | ambiguous        | 2             | 2                                            | #2 (2 of 3 runs), #3 (3 of 3 runs) | 0                    |
   | multi-hop        | 6             | 2                                            | #4 (3 of 3 runs), #9 (1 of 3 runs) | 0                    |
   | adversarial-lite | 4             | 0                                            |                                    | 0                    |
   | fact             | 3             | 0                                            |                                    | 2                    |
   | boundary         | 2             | 0                                            |                                    | 3                    |
   | tone             | 1             | 0                                            |                                    | 1                    |
   | out-of-scope     | 0             | 0                                            |                                    | 6                    |
   | false-premise    | 0             | 0                                            |                                    | 2                    |
   | **total**        | **18**        | **4**                                        |                                    | **14**               |

3. #3 and #4
   golden #3 failed because "$24.95" was missing in the output, this is related to `Missed rule exception` failure category. This is a real bot failure.
   golden #4 failed because "5025" was missing in the output, this is related to `incomplete answer` failure category. This is a real bot failure, it does not calculate that 100500 points = $5025 in rewards (100 points = $5)

4. App vs bare model (2–3 lines)
   All tests that were run in both bare mode and through app are passing.
   But app tests are testing exact shopbot implementation that will be used by customers, not synthetic implementation. Example: broken system prompt in `shopbot.py` will not be caught by bare model tests, because bare model tests create an own version of system prompt.
