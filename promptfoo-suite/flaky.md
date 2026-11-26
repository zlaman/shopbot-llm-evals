The 3 classes (from the curriculum):

- consistent fail: fails in every run → likely a product bug
- flaky: fails in some runs → the system is probabilistic, so you track a pass rate
- test bug: the assertion is wrong, so a correct answer fails (like #4's "$5,025")

| Case                  | Provider(s)                       | Failed runs | Class           | Evidence (short output quote or reason)                                                                                  | Action                  |
| --------------------- | --------------------------------- | ----------- | --------------- | ------------------------------------------------------------------------------------------------------------------------ | ----------------------- |
| golden #2 ambiguous   | E4B original, E2B original, E2B B | 4 / 12      | test bug        | Asked what the item is (spec allows it): "Could you tell me which item…?"                                                | Fix the grader          |
| golden #2 ambiguous   | E4B original, E4B B, E2B original | 6 / 12      | flaky (product) | No 15% fee: "Return shipping costs $6.95 for most customers…"                                                            | Fix the product         |
| golden #2 ambiguous   | E4B B, E2B B                      | 2 / 12      | flaky (product) | No fee, asked membership: "Are you a Trail Club member…?"                                                                | Fix the product         |
| golden #3 ambiguous   | all                               | 12 / 12     | consistent fail | No Alaska and Hawaii shipping cost "$24.95"                                                                              | Fix the product         |
| golden #4 multi-hop   | E2B prompt B                      | 1 / 12      | test bug        | "5025" not found in right answer "you would get 1,005 rewards, totaling $5,025."                                         | Fix the grader          |
| golden #4 multi-hop   | all                               | 11 / 12     | consistent fail | "5025" calculated value not found in answer "have 100,500 points, which earns you a $5 reward (100 points = $5 reward)"  | Fix the product         |
| golden #9 multi-hop   | E4B prompt original               | 35 / 100    | flaky           | Standard shipping "$5.95" not found in answer "With your $80 cart total, you qualify for free standard shipping"         | Fix the product + track |
| golden #9 multi-hop   | E4B prompt B                      | 21 / 100    | flaky           | Standard shipping "$5.95" not found in answer "your total after the discount is over $75, you qualify for free standard" | Fix the product + track |
| golden #16 multi-hop  | E4B prompt original               | 5 / 100     | flaky           | "180" points calculation not found in the answer "1 point per $160 spent, which equals 160 points."                      | Track a pass rate       |
| golden #16 multi-hop  | E4B prompt B                      | 1 / 100     | flaky           | "180" points calculation not found in the answer "you would earn 1 point per $160"                                       | Track a pass rate       |
| 5, 12, 17, 18, 20, 21 | E2B prompt original / B           | -           | not classified  | test bugs checked, none found, with one example (#18: "you have spent $499 … reached the Summit status").                | No action               |
