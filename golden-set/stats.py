from math import sqrt
import random


def wilson(passes, num_cases, z=1.96):
    """95% Wilson interval for the true pass rate, from `passes` out of `num_cases`. `num_cases` is a num of unique cases, not same one running repeatedly"""
    k, n = passes, num_cases  # short names keep the formula readable
    p_hat = k / n
    center = (p_hat + z**2 / (2 * n)) / (1 + z**2 / n)
    margin = z * sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
    return center - margin, center + margin


def run_build(true_pass_rate, num_cases):
    """Fake one eval run: each case passes with probability true_pass_rate. Returns the number of passes."""
    return sum(random.random() < true_pass_rate for _ in range(num_cases))


def detection_rate(true_pass_rate, num_cases, trials=2000):
    """Share of `trials` simulated runs where the gate says "regression" (upper bound < 90%)."""
    regressions_flagged = 0
    for _ in range(trials):
        passes = run_build(true_pass_rate, num_cases)
        low, high = wilson(passes=passes, num_cases=num_cases)
        if high < 0.9:  # 0.9 is a baseline result of 90%
            regressions_flagged += 1
    return regressions_flagged / trials


if __name__ == "__main__":  ## psvm in Python
    for passes, num_cases in [
        (1, 1),
        (2, 2),
        (6, 10),
        (7, 10),
        (8, 10),
        (9, 10),
        (10, 10),
        (32, 32),
        (31, 32),
        (30, 32),
        (29, 32),
        (28, 32),
        (27, 32),
        (26, 32),
        (25, 32),
        (45, 50),
        (90, 100),
        (95, 100),
        (99, 100),
        (100, 100),
        (300, 300),
    ]:
        low, high = wilson(passes, num_cases)
        print(f"{passes}/{num_cases}: {low:.1%} to {high:.1%}")

    for num_cases in [10, 25, 32, 50, 100, 200, 300]:
        caught = detection_rate(0.8, num_cases)  # broken build, true rate 80%
        false_alarm = detection_rate(0.9, num_cases)  # good build, true rate 90%
        print(f"{num_cases} runs: caught {caught:.0%}, false alarm {false_alarm:.0%}")
