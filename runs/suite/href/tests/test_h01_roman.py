import pytest
from solution import to_roman, from_roman

def test_known():
    assert to_roman(1994) == "MCMXCIV"
    assert to_roman(4) == "IV" and to_roman(3999) == "MMMCMXCIX" and to_roman(58) == "LVIII"

def test_roundtrip():
    for n in range(1, 4000):
        assert from_roman(to_roman(n)) == n

@pytest.mark.parametrize("n", [0, -1, 4000])
def test_to_invalid(n):
    with pytest.raises(ValueError):
        to_roman(n)

@pytest.mark.parametrize("s", ["IIII", "VX", "", "abc", "IC", "mcm"])
def test_from_invalid(s):
    with pytest.raises(ValueError):
        from_roman(s)
