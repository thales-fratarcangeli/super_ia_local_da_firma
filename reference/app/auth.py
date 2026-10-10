import datetime
import os

import bcrypt
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

SECRET = os.environ.get("JWT_SECRET", "dev-secret")
bearer = HTTPBearer(auto_error=False)  # auto_error=False: sem header => nós devolvemos 401 (o padrão seria 403)


def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()


def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=60)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET, algorithm="HS256")


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> User:
    if creds is None:
        raise HTTPException(401, "Not authenticated")
    try:
        payload = jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])
        user = db.get(User, int(payload["sub"]))
    except (jwt.PyJWTError, KeyError, ValueError):
        raise HTTPException(401, "Invalid token")
    if user is None:
        raise HTTPException(401, "Invalid token")
    return user
