from sqlalchemy import Column, Integer, String, Table, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import relationship

Base = declarative_base()

class ChatbotCreate(BaseModel):
    chatbot_name: str
    chatbot_prompt: str

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
    chatbots = relationship("Chatbot", back_populates="user")

class Admin(Base):
    __tablename__ = "admin"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
        
class Chatbot(Base):
    __tablename__ = "chatbots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    prompt = Column(String, nullable=False)
    file_content = Column(String, nullable=False)
    username = Column(String, ForeignKey("users.username"))

    user = relationship("User", back_populates="chatbots")