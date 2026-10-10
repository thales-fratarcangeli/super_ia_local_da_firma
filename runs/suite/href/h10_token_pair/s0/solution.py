import datetime
import jwt

def _tok(uid, secret, kind, delta):
    exp = datetime.datetime.now(datetime.timezone.utc) + delta
    return jwt.encode({"sub": str(uid), "type": kind, "exp": exp}, secret, algorithm="HS256")

def issue_pair(user_id, secret):
    return {"access": _tok(user_id, secret, "access", datetime.timedelta(minutes=15)),
            "refresh": _tok(user_id, secret, "refresh", datetime.timedelta(days=7))}

def _decode(token, secret, kind):
    try:
        p = jwt.decode(token, secret, algorithms=["HS256"])
        if p.get("type") != kind:
            return None
        return int(p["sub"])
    except Exception:
        return None

def refresh_access(refresh_token, secret):
    uid = _decode(refresh_token, secret, "refresh")
    return None if uid is None else _tok(uid, secret, "access", datetime.timedelta(minutes=15))

def verify_access(token, secret):
    return _decode(token, secret, "access")
