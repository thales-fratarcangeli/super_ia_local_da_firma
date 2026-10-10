import datetime
import jwt
from solution import create_token, decode_token

def test_roundtrip():
    t = create_token(42, "s" * 32)
    assert decode_token(t, "s" * 32) == 42
    p = jwt.decode(t, "s" * 32, algorithms=["HS256"])
    assert p["sub"] == "42" and "exp" in p

def test_wrong_secret_and_garbage():
    t = create_token(1, "a" * 32)
    assert decode_token(t, "b" * 32) is None
    assert decode_token("garbage", "a" * 32) is None
    assert decode_token("", "a" * 32) is None

def test_expired():
    t = create_token(1, "a" * 32, minutes=-5)
    assert decode_token(t, "a" * 32) is None

def test_no_sub():
    t = jwt.encode({"exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)}, "a" * 32, algorithm="HS256")
    assert decode_token(t, "a" * 32) is None
