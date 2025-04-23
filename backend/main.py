from fastapi import FastAPI, Depends, HTTPException, Form, UploadFile, File, Header
from sqlalchemy.orm import Session
from models.model import User, UserBase, UserLogin, Chatbot
from database.db import create_db_and_tables, get_session
from passlib.context import CryptContext
import os
from datetime import datetime, timedelta, timezone
from typing import Union, Any
from jose import jwt
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag.user_file_handling import file_handling

load_dotenv()


async def lifespan_handler(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_SECRET_KEY_FOR_CHATBOT = os.environ["JWT_SECRET_KEY_FOR_CHATBOT"]
JWT_REFRESH_SECRET_KEY = os.environ["JWT_REFRESH_SECRET_KEY"]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)


def create_refresh_token(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expires = datetime.now(timezone.utc) + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expires, "sub": str(subject)}
    return jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)


@app.get("/")
def read_root():
    return {"message": "hello world"}


@app.get("/users")
def read_users(session: Session = Depends(get_session)):
    users = session.query(User).all()
    return users if users else "No users registered"


@app.get("/users/{id}")
def read_user(id: int, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.id == id).first()
    return user if user else {"detail": "No user with such id"}


@app.post("/signup")
def register_user(user: UserBase, session: Session = Depends(get_session)):
    existing_user = session.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = User(
        username=user.username, email=user.email, password=hash_password(user.password)
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User registered successfully"}


@app.post("/login")
def login_user(user: UserLogin, session: Session = Depends(get_session)):
    registered_user = session.query(User).filter(User.username == user.username).first()
    if not registered_user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, registered_user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")

    return {
        "access_token": create_access_token(subject=user.username),
        "refresh_token": create_refresh_token(subject=user.username),
    }


@app.get("/verify-token/{token}")
def verify_user_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
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
        return {"access_token": create_access_token(subject=username)}
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")


def get_current_user(token: str) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Username is not valid")
        return payload["sub"]
    except:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")


@app.post("/create-chatbot")
async def create_chatbot(
    chatbot_name: str = Form(...),
    chatbot_prompt: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    authorization: str = Header(None),
):
    # Check authorization
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = authorization.replace("Bearer ", "")

    try:
        users_username = get_current_user(token)

        # Read file content correctly - UploadFile needs to be handled differently
        content = await file.read()
        content_str = content.decode("utf-8")
        processed = file_handling(content_str)
        print(processed)

        payload = {
            "username": users_username,
            "exp": int((datetime.now(timezone.utc) + timedelta(days=3650)).timestamp()),
        }
        bot_token = jwt.encode(payload, JWT_SECRET_KEY_FOR_CHATBOT, algorithm="HS256")

        if processed:
            bot = Chatbot(
                name=chatbot_name,
                prompt=chatbot_prompt,
                file_content=processed,
                username=users_username,
                token=bot_token,  # Uncommented this line
            )
            session.add(bot)
            session.commit()
            session.refresh(bot)
            return {bot_token}
        else:
            raise HTTPException(status_code=400, detail="Failed to process file")
    except Exception as e:
        # Include the actual error message for debugging
        raise HTTPException(
            status_code=403, detail=f"Token is invalid or expired: {str(e)}"
        )
