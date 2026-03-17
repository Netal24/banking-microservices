import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from common.db import get_session
from . import models, schemas
from .security import get_password_hash, verify_password, create_access_token, decode_access_token, oauth2_scheme

router = APIRouter(prefix="/user", tags=["User Service"])

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
    user = session.get(models.User, int(payload["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/register", response_model=schemas.UserRead, status_code=201)
async def register(user_in: schemas.UserCreate, session: Session = Depends(get_session)):
    if session.exec(select(models.User).where(models.User.email == user_in.email)).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/login", response_model=schemas.Token)
async def login(form: schemas.UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(models.User).where(models.User.email == form.email)).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return {"access_token": create_access_token({"sub": str(user.id)}), "token_type": "bearer"}

@router.get("/profile", response_model=schemas.UserRead)
async def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/{user_id}", response_model=schemas.UserRead)
async def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
