import math
from collections import Counter

import pytest

from vanguard.batch import next_group, remaining
from vanguard.metrics.stats import entropy_bits, wilson_interval


def test_wilson_interval_known_values():
    low, high = wilson_interval(5, 10)
    assert low == pytest.approx(0.2366, abs=1e-3)
    assert high == pytest.approx(0.7634, abs=1e-3)
    low, high = wilson_interval(0, 10)
    assert low == 0.0 and high == pytest.approx(0.2775, abs=1e-3)
    assert wilson_interval(0, 0) == (0.0, 0.0)
    with pytest.raises(ValueError):
        wilson_interval(3, 2)


def test_entropy_bits():
    assert entropy_bits([]) == 0.0
    assert entropy_bits([7]) == 0.0
    assert entropy_bits([1, 1]) == pytest.approx(1.0)
    assert entropy_bits([1, 1, 1, 1, 0]) == pytest.approx(2.0)
    assert entropy_bits([3, 1]) == pytest.approx(-(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25)))


def test_next_group_balances_and_resumes():
    targets = {"prompt_only": 2, "gate": 2}
    done: Counter = Counter()
    order = []
    while (group := next_group(done, targets)) is not None:
        order.append(group)
        done[group] += 1
    assert order == ["prompt_only", "gate", "prompt_only", "gate"]
    # A stopped batch continues with the group that is behind.
    assert next_group({"prompt_only": 2, "gate": 0}, targets) == "gate"
    assert remaining({"prompt_only": 1}, targets) == 3
