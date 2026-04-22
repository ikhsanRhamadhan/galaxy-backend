from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import hashlib
import jwt
from datetime import datetime, timedelta
import os # Import os module
from models import LoginRequest, UserCreate
from database import db

router = APIRouter()
security = HTTPBearer()
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "galaxy-multi-trans-secret-2024-fallback-key") # Load from env, provide fallback
ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def create_token(data: dict) -> str:
    payload = {**data, "exp": datetime.utcnow() + timedelta(hours=24)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user = db.get_by_id("users", user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login")
async def login(req: LoginRequest):
    users = db.get_all("users")
    user = next((u for u in users if u["username"] == req.username and u["password"] == hash_password(req.password)), None)
    if not user:
        raise HTTPException(status_code=401, detail="Username atau password salah")
    
    token = create_token({"user_id": user["id"], "username": user["username"], "role": user["role"]})
    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "name": user["name"],
            "role": user["role"],
            "email": user["email"]
        }
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return current_user

@router.get("/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak")
    users = db.get_all("users")
    return [{"id": u["id"], "username": u["username"], "name": u["name"], "role": u["role"], "email": u["email"], "created_at": u["created_at"]} for u in users]

@router.post("/users")
async def create_user(user: UserCreate, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak")
    existing = db.query("users", {"username": user.username})
    if existing:
        raise HTTPException(status_code=400, detail="Username sudah digunakan")
    new_user = {
        "username": user.username,
        "password": hash_password(user.password),
        "role": user.role,
        "name": user.name,
        "email": user.email
    }
    result = db.insert("users", new_user)
    del result["password"]
    return result

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Akses ditolak")
    if user_id == current_user["id"]:
        raise HTTPException(status_code=400, detail="Tidak bisa menghapus akun sendiri")
    deleted = db.delete("users", user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User tidak ditemukan")
    return {"message": "User berhasil dihapus"}
