from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from app.auth import create_user, authenticate_user, get_current_user
from app.schemas import UserCreate, UserResponse, TokenResponse
from app.database import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db, user)

@router.post("/login", response_model=TokenResponse)
def login_user(username: str, password: str, db: Session = Depends(get_db)):
    user = authenticate_user(db, username, password)
    access_token = jwt.encode({"sub": str(user.id), "exp": datetime.utcnow() + timedelta(minutes=60)}, JWT_SECRET, algorithm="HS256")
    return {"access_token": access_token, "token_type": "bearer"}
