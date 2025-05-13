from fastapi import APIRouter, Depends, UploadFile, Form, Header, HTTPException, File
from sqlalchemy.orm import Session
from rag.user_file_handling import file_handling
from rag.chromaSetup import getCollection
from rag.GeminiSetup import llm
from auth.dependencies import get_current_username
from models.model import Chatbot
from config import JWT_SECRET_KEY_FOR_CHATBOT
from jose import jwt
from datetime import datetime, timezone, timedelta
from database.db import get_session
from models.model import BaseModel

class ChatRequest(BaseModel):
    prompt: str
    chat_token: str
    
class ExternalChatRequest(BaseModel):
    prompt: str
    
router = APIRouter()

@router.post("/create-chatbot")
async def create_chatbot(
    chatbot_name: str = Form(...),
    chatbot_prompt: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    Authorization: str = Header(None),
):
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    token = Authorization.replace("Bearer ", "")
    try:
        users_username = get_current_username(token)
        existing_chatbot = (
            session.query(Chatbot)
            .filter(Chatbot.username == users_username, Chatbot.name == chatbot_name)
            .first()
        )
        if existing_chatbot:
            raise HTTPException(
                status_code=400, detail="Chatbot with this name already exists"
            )
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


@router.post("/chat")
async def chat(
    request: ExternalChatRequest, chatToken: str = Header(None), session: Session = Depends(get_session)
):
    bot = session.query(Chatbot).filter(Chatbot.token == chatToken).first()
    
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
        raise HTTPException( status_code=404 , detail  = "Bot not found") 


@router.post("/test-chat")
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
    
    