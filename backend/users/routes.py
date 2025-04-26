from fastapi import APIRouter, Depends, Header, HTTPException
from models.model import User, UserBase, UserLogin
from sqlalchemy.orm import Session
from auth.hashing import hash_password, verify_password
from auth.jwt_handler import create_access_token, create_refresh_token
from auth.dependencies import get_current_user
from database.db import get_session
from jose import jwt
from config import JWT_SECRET_KEY, ALGORITHM, JWT_REFRESH_SECRET_KEY
from models.model import BaseModel


router = APIRouter()

@router.post("/signup")
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

@router.post("/login")
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
    

@router.post("/current-user")
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


@router.get("/verify-token/{token}")
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
    
    
@router.post("/refresh")
def refresh_access_token(request: RefreshTokenRequest):
    try:
        payload = jwt.decode(request.refresh_token, JWT_REFRESH_SECRET_KEY, ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=403, detail="Invalid refresh token")
        return {"access_token": create_access_token(subject=username)}
    except:
        raise HTTPException(status_code=403, detail="Invalid or expired refresh token")
