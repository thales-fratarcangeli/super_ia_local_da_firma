import jwt
import bcrypt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.main import get_db, get_current_user

def get_token(authorization: Annotated[str, Header(...)]):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.split(" ")[1]
    return token

def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTP
