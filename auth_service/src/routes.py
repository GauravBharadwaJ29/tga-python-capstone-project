from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from passlib.hash import bcrypt
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
from .database import SessionLocal
from .models import User, UserRole
from .config import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRY_MINUTES
from .logger_config import logger

router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: str
    role: UserRole

    model_config = {"from_attributes": True}  # Pydantic v2 style

def create_jwt(user: User):
    payload = {
        "sub": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role.value,
        "exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRY_MINUTES)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_db():
    async with SessionLocal() as session:
        yield session

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        logger.warning("No or invalid Authorization header")
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = auth.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload["sub"]
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            logger.warning(f"User not found for token sub={user_id}")
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(status_code=401, detail="Token expired")
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check for unique email
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        logger.warning(f"Signup failed: email already in use ({user_in.email})")
        raise HTTPException(status_code=400, detail="Email already registered")
    # Check for unique username
    result = await db.execute(select(User).where(User.username == user_in.username))
    if result.scalar_one_or_none():
        logger.warning(f"Signup failed: username already in use ({user_in.username})")
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=bcrypt.hash(user_in.password),
        role=UserRole.customer
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    logger.info(f"User created: {user.email}")
    return user

@router.post("/login")
async def login(login_in: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    if not user or not bcrypt.verify(login_in.password, user.password_hash):
        logger.warning(f"Login failed for {login_in.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(user)
    logger.info(f"User logged in: {user.email}")
    return {"token": token, "user": UserOut.model_validate(user)}

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# --- For future use (commented out) ---
# @router.post("/reset-password")
# async def reset_password(...):
#     pass
# @router.post("/verify-email")
# async def verify_email(...):
#     pass
