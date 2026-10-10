import pytest
from solution import shortest_path

G = ["..#.",
     "..#.",
     "....",
     "#..."]

def test_basic():
    assert shortest_path(G, (0, 0), (0, 3)) == 7
    assert shortest_path(G, (0, 0), (0, 0)) == 0

def test_no_path():
    assert shortest_path(["..#.", "..#."], (0, 0), (0, 3)) == -1

def test_invalid():
    with pytest.raises(ValueError):
        shortest_path(G, (0, 2), (0, 0))
    with pytest.raises(ValueError):
        shortest_path(G, (0, 0), (9, 9))
    with pytest.raises(ValueError):
        shortest_path(G, (-1, 0), (0, 0))
