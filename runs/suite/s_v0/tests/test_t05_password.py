import base64
from solution import hash_password, verify_password

def test_roundtrip():
    h = hash_password("secret123")
    assert verify_password("secret123", h)
    assert not verify_password("wrong", h)

def test_format_and_salt():
    h1, h2 = hash_password("x"), hash_password("x")
    assert h1 != h2
    parts = h1.split("$")
    assert parts[0] == "pbkdf2" and parts[1] == "100000" and len(parts) == 4
    assert len(base64.b64decode(parts[2])) == 16

def test_malformed():
    for bad in ["", "abc", "pbkdf2$x$y", "pbkdf2$abc$!!$!!"]:
        assert verify_password("x", bad) is False
