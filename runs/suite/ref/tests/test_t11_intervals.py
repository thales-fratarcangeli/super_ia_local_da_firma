import pytest
from solution import merge_intervals

def test_merge():
    assert merge_intervals([(5, 8), (1, 3), (2, 4)]) == [(1, 4), (5, 8)]

def test_touching_and_contained():
    assert merge_intervals([(1, 3), (3, 5), (2, 2), (10, 12), (11, 11)]) == [(1, 5), (10, 12)]

def test_empty_and_input_untouched():
    assert merge_intervals([]) == []
    x = [(3, 4), (1, 2)]
    merge_intervals(x)
    assert x == [(3, 4), (1, 2)]

def test_invalid():
    with pytest.raises(ValueError):
        merge_intervals([(4, 1)])
