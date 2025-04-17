# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from models.model import User, UserLogin
from database.db import create_db_and_tables, get_session
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta, timezone
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["*"] for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Hashing functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


ACCESS_TOKEN_EXPIRE_MINUTES = 0.05  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]  # should be kept secret


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt

    

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def read_root():
    return {"message": "hello world"}


@app.get("/users")
def read_users(session: Session = Depends(get_session)):
    statement = select(User)
    users = session.exec(statement).all()
    if users:
        return users
    else:
        return "No users registered"


@app.get("/users/{id}")
def read_user(id: int, session: Session = Depends(get_session)):
    statement = select(User).where(User.id == id)
    user = session.exec(statement).first()
    if user:
        return user
    else:
        return {"detail": "No user with such id"}


@app.post("/signup")
def register_user(user: User, session: Session = Depends(get_session)):
    # Check if username already exists
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Hash the user's password before storing
    user.password = hash_password(user.password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(user: UserLogin, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    registered_user = session.exec(statement).first()

    if not registered_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(user.password, registered_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    access_token = create_access_token(subject=user)
    refresh_token = create_refresh_token(subject=user)
    
    return ({'access_token' : access_token, 'refresh_token': refresh_token})

@app.get('/verify-token/{token}')
def verify_user_token(token:str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Username is not valid")
        return payload
    except:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")



class RefreshTokenRequest(BaseModel):
    refresh_token: str

@app.post("/refresh")
def refresh_access_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, JWT_REFRESH_SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid refresh token")
        new_access_token = create_access_token(subject=username)
        return {"access_token": new_access_token}
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")