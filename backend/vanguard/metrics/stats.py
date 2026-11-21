"""Small statistics helpers shared by the metrics and the results tables.

Adapted from Synthetic Users (synthusers/analyze.py, same author; see NOTICE.md):
wilson_interval and the Shannon entropy of a count distribution. Changes: the
interval is returned as proportions (0..1), not percent, and both functions are typed.
"""

import math
from collections.abc import Iterable


def wilson_interval(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion k/n (95% by default), as (low, high) in 0..1.

    Preferred over the normal approximation because Vanguard's groups are small (often
    5 to 20 runs) and rates near 0 or 1 are common (for example executed leakage under
    the gate).
    """
    if n <= 0:
        return (0.0, 0.0)
    if not 0 <= k <= n:
        raise ValueError(f"k must be between 0 and n, got k={k}, n={n}")
    p = k / n
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return (max(0.0, centre - margin), min(1.0, centre + margin))


def entropy_bits(counts: Iterable[int]) -> float:
    """Shannon entropy, in bits, of a distribution given as counts (zeros are ignored).

    Used for diversity, for example over the action types a persona chooses across runs.
    """
    values = [count for count in counts if count > 0]
    total = sum(values)
    if total == 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in values)
