from solution import check_brackets

def test_ok():
    assert check_brackets("") == -1
    assert check_brackets("a(b[c]{d})e") == -1

def test_wrong_close():
    assert check_brackets("(]") == 1
    assert check_brackets("a)") == 1
    assert check_brackets("([)]") == 2

def test_unclosed_reports_oldest_open():
    assert check_brackets("((") == 0
    assert check_brackets("x{[a]") == 1
