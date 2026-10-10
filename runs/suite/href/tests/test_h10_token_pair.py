import datetime
import jwt
from solution import issue_pair, refresh_access, verify_access

S = "k" * 32

def test_pair_claims():
    p = issue_pair(7, S)
    a = jwt.decode(p["access"], S, algorithms=["HS256"])
    r = jwt.decode(p["refresh"], S, algorithms=["HS256"])
    assert a["type"] == "access" and r["type"] == "refresh" and a["sub"] == "7"
    da = a["exp"] - datetime.datetime.now(datetime.timezone.utc).timestamp()
    dr = r["exp"] - datetime.datetime.now(datetime.timezone.utc).timestamp()
    assert 14 * 60 < da <= 15 * 60 + 5 and 6.9 * 86400 < dr <= 7 * 86400 + 5

def test_verify_access_only():
    p = issue_pair(7, S)
    assert verify_access(p["access"], S) == 7
    assert verify_access(p["refresh"], S) is None
    assert verify_access("lixo", S) is None
    assert verify_access(p["access"], "o" * 32) is None

def test_refresh_flow():
    p = issue_pair(7, S)
    new = refresh_access(p["refresh"], S)
    assert new and verify_access(new, S) == 7
    assert refresh_access(p["access"], S) is None
    assert refresh_access("lixo", S) is None

def test_expired_refresh():
    old = jwt.encode({"sub": "7", "type": "refresh",
                      "exp": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=5)}, S, algorithm="HS256")
    assert refresh_access(old, S) is None
