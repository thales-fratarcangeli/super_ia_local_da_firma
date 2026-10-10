
from solution import two_sum

def test_basic():
    assert two_sum([2, 7, 11, 15], 9) == (0, 1)
    assert two_sum([3, 2, 4], 6) == (1, 2)

def test_duplicates_and_tiebreak():
    assert two_sum([3, 3], 6) == (0, 1)
    assert two_sum([1, 5, 5, 1], 6) == (0, 1)
    assert two_sum([4, 1, 3, 2, 5], 6) == (0, 3)

def test_none_and_empty():
    assert two_sum([1, 2], 10) is None
    assert two_sum([], 0) is None
    assert two_sum([5], 5) is None

def test_negatives_and_zero():
    assert two_sum([-3, 4, 3, 90], 0) == (0, 2)
    assert two_sum([0, 4, 0], 0) == (0, 2)
