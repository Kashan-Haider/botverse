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
from rag.chromaSetup import getCollection
from rag.GeminiSetup import llm


class ChatRequest(BaseModel):
    prompt: str
    chat_token: str


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

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
REFRESH_TOKEN_EXPIRE_MINUTES = int(os.environ["REFRESH_TOKEN_EXPIRE_MINUTES"])
ALGORITHM = os.environ["ALGORITHM"]
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


def get_current_username(token: str) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Username is not valid")
        return payload["sub"]
    except:
        raise HTTPException(status_code=403, detail="Token is invalid or expired")


def get_current_user(token: str, session: Session = Depends(get_session)) -> User:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid token: no subject")

        user = session.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return user
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=f"Token is invalid or expired: {str(e)}"
        )


@app.get("/")
def read_root():
    return {"message": "hello world"}


@app.get("/users")
def read_users(session: Session = Depends(get_session)):
    users = session.query(User).all()
    return users if users else "No users registered"


@app.post("/current-user")
def read_user(
    session: Session = Depends(get_session),
    Authorization: str = Header(None),
):

    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = Authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid token: no subject")

        user = session.query(User).filter(User.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "user": user.to_dict(),
            "chatbots": [
                {
                    "id": bot.id,
                    "name": bot.name,
                    "prompt": bot.prompt,
                    "token": bot.token,
                }
                for bot in user.chatbots
            ],
        }

    except Exception as e:
        raise HTTPException(
            status_code=403, detail=f"Token is invalid or expired: {str(e)}"
        )


@app.post("/signup")
def register_user(user: UserBase, session: Session = Depends(get_session)):

    existing_user = session.query(User).filter(User.username == user.username).first()
    existing_user_email = session.query(User).filter(User.email == user.email).first()
    if existing_user or existing_user_email:
        raise HTTPException(status_code=400, detail="Username/email already exists")

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


@app.post("/create-chatbot")
async def create_chatbot(
    chatbot_name: str = Form(...),
    chatbot_prompt: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    Authorization: str = Header(None),
):
    # Check authorization
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = Authorization.replace("Bearer ", "")
    try:
        users_username = get_current_username(token)

        # Check if a chatbot with the same name already exists for the user
        existing_chatbot = (
            session.query(Chatbot)
            .filter(Chatbot.username == users_username, Chatbot.name == chatbot_name)
            .first()
        )
        if existing_chatbot:
            raise HTTPException(
                status_code=400, detail="Chatbot with this name already exists"
            )

        # Read file content correctly
        content = await file.read()
        content_str = content.decode("utf-8")
        collection_name = chatbot_name.replace(" ", "_").lower()

        processed = file_handling(content_str, collection_name)

        payload = {
            "username": users_username,
            "chatbot_name": chatbot_name,
            "exp": int((datetime.now(timezone.utc) + timedelta(days=3650)).timestamp()),
        }
        bot_token = jwt.encode(payload, JWT_SECRET_KEY_FOR_CHATBOT, algorithm="HS256")

        if processed:
            bot = Chatbot(
                name=chatbot_name,
                prompt=chatbot_prompt,
                file_content=processed,
                username=users_username,
                token=bot_token,
            )
            session.add(bot)
            session.commit()
            session.refresh(bot)
            return {"bot_token": bot_token}
        else:
            raise HTTPException(status_code=400, detail="Failed to process file")
    except Exception as e:
        raise HTTPException(
            status_code=403, detail=f"Token is invalid or expired: {str(e)}"
        )


@app.post("/chat")
async def chat(
    prompt: str, chat_token: str = Header(None), session: Session = Depends(get_session)
):
    bot = session.query(Chatbot).filter(Chatbot.token == chat_token).first()
    if bot:
        collection_name = bot.name.replace(" ", "_").lower()
        collection = getCollection(collection_name)
        results = collection.query(
            query_texts=[prompt],
            n_results=10,
        )
        system_message = (
            f"{bot.prompt}. "
            "Answer the users query according to the following context and do not add anything other than context. Answer the user in like a human being in english language with a softer tone"
            "If the query is not related to the context then just return I DONT KNOW. "
            f"Context: {results['documents']}"
        )

        messages = [
            ("system", system_message),
            ("human", prompt),
        ]

        res = llm.invoke(messages)

        return res
    else:
        return "Bot not found"


@app.post("/test-chat")
async def chat(request: ChatRequest, session: Session = Depends(get_session)):
    bot: Chatbot = (
        session.query(Chatbot).filter(Chatbot.token == request.chat_token).first()
    )
    if bot:
        collection_name = bot.name.replace(" ", "_").lower()
        collection = getCollection(collection_name)
        results = collection.query(
            query_texts=[request.prompt],
            n_results=10,
        )
        system_message = (
            f"{bot.prompt}. "
            "Answer the users query according to the following context and do not add anything other than context. Answer the user in like a human being in english language with a softer tone"
            "If the query is not related to the context then just return I DONT KNOW. "
            f"Context: {results['documents']}"
        )

        messages = [
            ("system", system_message),
            ("human", request.prompt),
        ]

        res = llm.invoke(messages)

        return res
    else:
        return "Bot not found"