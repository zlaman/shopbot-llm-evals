# Position bias

## Setup

`pairs.csv` with 32 pairs of question,expected_behavior both having 2 options in A B and B A order.
Answers: M03.4 runs, E4B with old prompt = x, prompt B = y.

`position.yaml` config with local Gemma 4 12B judge model configured to chose A and B answers when they come in 2 different orders
32 pairs × 2 orders = 64 calls

## Results

winner changed: 19 of 32 pairs - judge chosen different answer after flipping the order of answers
same winner: 13 of 32 pairs - judge kept the same choice after flipping the order of answers

picked position A: 49 of 64 verdicts, position B: 15 of 64 verdicts.

Order xy only: x wins 25 of 32 pairs
Order yx only: y wins 24 of 32 pairs
Same judge, opposite conclusions because of answers position.

## Conclusion

If the judge should compare 2 versions, grade each version pointwise (separately) and compare pass rates. If you have to use pairwise (comparing 2 versions at one call), perform A to B and B to A comparison, find stable answers and flipping.
Flipping means there is a tie (draw), so none of A or B wins the criteria.

One order eval is order bias affected, the judge choses position A more often than position B
Stable winner is know in only 13 cases.
Winner is unclear (tie scenario) in 19 cases.

## Mitigation

- Rule: run each pair in both orders. Same winner = verdict; winner changed = tie (winner unclear).
- Result: old prompt 7 pairs, prompt B 6 pairs, tie 19 pairs → no clear difference.
- Cost: 2 judge calls per pair (64 calls for 32 pairs).

## Test with Haiku 5.5

```
winner changed: 7 of 32 pairs; same winner: 25 of 32 pairs
picked position A: 39 of 64 verdicts, position B: 25 of 64 verdicts
both orders (changed winner = tie): x wins 10, y wins 15, tie 7 of 32 pairs
order xy only: said A 17 of 32 pairs -> x wins 17, y wins 15 of 32 pairs
order yx only: said A 22 of 32 pairs -> x wins 10, y wins 22 of 32 pairs
```

7 Haiku pairs are all among the 12B's 19 → near-equal pairs
Pairs 9 and 20: same winner in both orders but opposite judges. In case of 9 - answers are unclear and hard to measure. In case of 20 - the criteria don't cover security, and which answers are good or bad.

## Next steps

Clear-winner pairs to measure position errors and accuracy

# Verbosity bias

## Setup

Below prefix and suffix applied to 15 rows where both label and 12B say fail in `outputs.csv` producing answer column in `padded.csv`
Used `judge-v8-escalation.yaml` as a base with just facts rubric - `verbosity.yaml`

```
Thank you so much for reaching out to Pebble & Pine, I'm happy to help you with this!
I hope this helps, and please don't hesitate to contact us if you need anything else. Have a wonderful day!
```

Limits - 1 filler text, 15 rows, 12B only. Vague rubrics and pairwise judges not tested

## Results

The padding changed 0 of 15 judge verdicts

```
sanity: plain answers still fail on 15 of 15 rows
verdict changed by padding: 0 of 15 rows (fail -> pass 0 rows, pass -> fail 0 rows)
```

## Conclusion

Judge is safe from verbosity bias.

Why there is no effect?
The rubric is specific - is any fail condition met or not, 5 fail conditions, KB, expected answer.
Judge has clear and specific rubric to decide, so that extra text in the prompt does not affect the result.

## Mitigation

- Keep rubrics binary and reference-based
- Add the 15 padded rows to the calibration set as a regression probe
