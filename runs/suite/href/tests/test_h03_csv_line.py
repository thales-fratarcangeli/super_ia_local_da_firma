import pytest
from solution import parse_csv_line

def test_simple():
    assert parse_csv_line("a,b,c") == ["a", "b", "c"]
    assert parse_csv_line("a,,c") == ["a", "", "c"]
    assert parse_csv_line("") == [""]

def test_quotes():
    assert parse_csv_line('"a,b",c') == ["a,b", "c"]
    assert parse_csv_line('"he said ""hi""",x') == ['he said "hi"', "x"]
    assert parse_csv_line('""') == [""]

def test_spaces_and_trailing():
    assert parse_csv_line(" a , b ,") == [" a ", " b ", ""]

def test_unclosed():
    with pytest.raises(ValueError):
        parse_csv_line('"abc')
