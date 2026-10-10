import datetime
import jwt

def create_token(user_id, secret, minutes=60):
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=minutes)
    return jwt.encode({"sub": str(user_id), "exp": exp}, secret, algorithm="HS256")

def decode_token(token, secret):
    try:
        return int(jwt.decode(token, secret, algorithms=["HS256"])["sub"])
    except Exception:
        return None
