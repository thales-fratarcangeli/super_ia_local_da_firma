from solution import parse_qs

def test_basic():
    assert parse_qs("a=1&b=2") == {"a": ["1"], "b": ["2"]}

def test_leading_question_and_empty():
    assert parse_qs("?x=1") == {"x": ["1"]}
    assert parse_qs("") == {}

def test_repeated_and_decoding():
    assert parse_qs("t=a+b&t=c%20d&t=%C3%A7") == {"t": ["a b", "c d", "ç"]}

def test_no_equals_and_first_equals():
    assert parse_qs("flag&k=a=b") == {"flag": [""], "k": ["a=b"]}
