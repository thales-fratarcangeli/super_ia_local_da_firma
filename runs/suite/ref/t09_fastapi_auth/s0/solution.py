from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

app = FastAPI()
bearer = HTTPBearer(auto_error=False)

def auth(creds: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if creds is None or creds.credentials != "secret-token":
        raise HTTPException(401, "Unauthorized", headers={"WWW-Authenticate": "Bearer"})
    return "admin"

@app.get("/me")
def me(user: str = Depends(auth)):
    return {"user": user}

@app.get("/health")
def health():
    return {"status": "ok"}
