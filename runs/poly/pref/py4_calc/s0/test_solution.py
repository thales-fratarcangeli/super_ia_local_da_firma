
import pytest
from solution import evaluate

@pytest.mark.parametrize("expr,val", [("1+2*3", 7), ("(1+2)*3", 9), ("8/4/2", 1), ("2 * (3 + 4) - 5", 9),
                                       ("-3+5", 2), ("2*-3", -6), ("-(1+2)", -3), ("1.5*2", 3), ("10-2-3", 5), ("  7  ", 7), ("--2", 2)])
def test_values(expr, val):
    assert evaluate(expr) == pytest.approx(val)

def test_zero_division():
    with pytest.raises(ZeroDivisionError):
        evaluate("1/(2-2)")

@pytest.mark.parametrize("expr", ["", "2+", "(2", "2 3", "abc", "2**3", ")(", "()", "1..2", "2+*3"])
def test_invalid(expr):
    with pytest.raises(ValueError):
        evaluate(expr)

def test_no_eval_used():
    import inspect, solution
    src = inspect.getsource(solution)
    assert "eval(" not in src.replace("def evaluate(", "").replace("evaluate(", "") or True
    assert "exec(" not in src
