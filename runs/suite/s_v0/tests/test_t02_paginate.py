import pytest
from solution import paginate

def test_first_page():
    r = paginate(list(range(25)))
    assert r == {"items": list(range(10)), "total": 25, "page": 1, "page_size": 10}

def test_last_partial():
    assert paginate(list(range(25)), 3, 10)["items"] == [20, 21, 22, 23, 24]

def test_beyond():
    assert paginate(list(range(5)), 9, 10)["items"] == []

@pytest.mark.parametrize("p,s", [(0, 10), (1, 0), (1, 51), (-1, 5)])
def test_invalid(p, s):
    with pytest.raises(ValueError):
        paginate([1], p, s)
