"""Pure mathematical functions. Invalid distributions are never normalized."""

from math import isclose, isfinite
from numbers import Real


def finite(value: float) -> float:
    """Require a finite real number, excluding booleans."""
    if isinstance(value, bool) or not isinstance(value, Real) or not isfinite(value):
        raise ValueError("Enter a finite number.")
    return float(value)


def probability(value: float) -> float:
    value = finite(value)
    if not 0 <= value <= 1:
        raise ValueError("Probabilities must be between 0 and 1.")
    return value


def count(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Counts must be nonnegative whole numbers.")
    return value


def expected_value(values: list[float], probabilities: list[float]) -> float:
    if not values or len(values) != len(probabilities):
        raise ValueError("Supply one probability for every outcome, and at least one outcome.")
    xs = [finite(x) for x in values]
    ps = [probability(p) for p in probabilities]
    if not isclose(sum(ps), 1.0, rel_tol=0, abs_tol=1e-9):
        raise ValueError(f"Probabilities total {sum(ps):.4f}; they must total 1. No normalization was applied.")
    return sum(x * p for x, p in zip(xs, ps))


def conditional(joint: float, given: float) -> float:
    joint, given = probability(joint), probability(given)
    if given == 0:
        raise ValueError("The conditioning event must have positive probability.")
    if joint > given:
        raise ValueError("The overlap cannot be larger than the conditioning event.")
    return joint / given


def from_counts(overlap: int, given: int, population: int) -> float:
    overlap, given, population = count(overlap), count(given), count(population)
    if not 0 <= overlap <= given <= population or given == 0:
        raise ValueError("Require 0 ≤ overlap ≤ given group ≤ population and a nonempty given group.")
    return overlap / given


def independent(p_a: float, p_b: float, p_both: float) -> bool:
    a, b, both = probability(p_a), probability(p_b), probability(p_both)
    if both < max(0, a + b - 1) - 1e-9 or both > min(a, b) + 1e-9:
        raise ValueError("These probabilities cannot describe a consistent population.")
    return isclose(both, a * b, rel_tol=0, abs_tol=1e-9)


def second_blue(blue: int, total: int, replacement: bool) -> float:
    """Probability of blue on draw two, given blue on draw one."""
    blue, total = count(blue), count(total)
    if not 1 <= blue <= total or total < 2:
        raise ValueError("Use at least two marbles, with at least one blue marble.")
    return blue / total if replacement else (blue - 1) / (total - 1)


def frequencies(population: int, prevalence: float, sensitivity: float, false_positive: float) -> dict:
    """Expected natural frequencies, which can be fractional for arbitrary inputs."""
    population = count(population)
    if population == 0:
        raise ValueError("Population must be positive.")
    p, s, f = map(probability, (prevalence, sensitivity, false_positive))
    target, other = population * p, population * (1 - p)
    true_clues, false_clues = target * s, other * f
    total_clues = true_clues + false_clues
    return {"target": target, "other": other, "true_clues": true_clues,
            "false_clues": false_clues, "total_clues": total_clues,
            "posterior": true_clues / total_clues if total_clues else None}
