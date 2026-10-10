import pytest
from pydantic import ValidationError
from solution import SignUp

def test_ok_and_normalization():
    u = SignUp(username="Ana_01", password="secret1")
    assert u.username == "ana_01" and u.role == "member" and u.age is None

def test_username_rules():
    for bad in ["ab", "x" * 21, "a b c", "ana!", ""]:
        with pytest.raises(ValidationError):
            SignUp(username=bad, password="secret1")

def test_password_age_role():
    with pytest.raises(ValidationError):
        SignUp(username="ana", password="123")
    for age in (12, 121):
        with pytest.raises(ValidationError):
            SignUp(username="ana", password="secret1", age=age)
    assert SignUp(username="ana", password="secret1", age=13, role="admin").role == "admin"
    with pytest.raises(ValidationError):
        SignUp(username="ana", password="secret1", role="root")
