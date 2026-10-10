import pytest
from solution import toposort

def test_basic():
    assert toposort({"app": ["lib", "db"], "lib": ["core"], "db": ["core"]}) == ["core", "db", "lib", "app"]

def test_implicit_nodes_and_ties():
    assert toposort({"b": ["a"], "c": []}) == ["a", "b", "c"]

def test_empty():
    assert toposort({}) == []

def test_cycle():
    with pytest.raises(ValueError):
        toposort({"a": ["b"], "b": ["c"], "c": ["a"]})
    with pytest.raises(ValueError):
        toposort({"a": ["a"]})
