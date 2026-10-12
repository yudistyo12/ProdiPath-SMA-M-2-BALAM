from fastapi import APIRouter, HTTPException, Depends
from backend.schemas.models import LoginRequest, Token
from backend.database import get_db_connection
import os
import passlib.hash
import jwt
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/auth", tags=["auth"])

SECRET_KEY = os.getenv(
    "PRODIPATH_SECRET_KEY",
    "prodipath-local-development-secret-change-before-deployment",
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=Token)
def login(request: LoginRequest):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (request.username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not passlib.hash.bcrypt.verify(request.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(data={"sub": user['username'], "role": user.get('role', 'mahasiswa')})
    return {"access_token": access_token, "token_type": "bearer"}

from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.get("/me")
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role", "mahasiswa")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username, "role": role}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc:
        raise HTTPException(
            status_code=401,
            detail="Sesi tidak valid atau sudah kedaluwarsa.",
        ) from exc

    if not payload.get("sub"):
        raise HTTPException(status_code=401, detail="Sesi tidak valid.")
    if payload.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="Akses hanya tersedia untuk administrator.",
        )

    return payload.get("sub")
