import pytest
from solution import parse_duration, format_duration

def test_parse_ok():
    assert parse_duration("1h30m") == 5400
    assert parse_duration("2d") == 172800
    assert parse_duration("1d2h3m4s") == 93784
    assert parse_duration("45s") == 45 and parse_duration("90") == 90

@pytest.mark.parametrize("s", ["", "abc", "-5s", "1.5h", "30m1h", "1h1h", "1h 30m", "h", "5x"])
def test_parse_invalid(s):
    with pytest.raises(ValueError):
        parse_duration(s)

def test_format():
    assert format_duration(5400) == "1h30m"
    assert format_duration(0) == "0s"
    assert format_duration(93784) == "1d2h3m4s"
    assert format_duration(86400) == "1d"
    with pytest.raises(ValueError):
        format_duration(-1)

def test_roundtrip():
    for n in [1, 59, 60, 3599, 3600, 86399, 86400, 100000]:
        assert parse_duration(format_duration(n)) == n
