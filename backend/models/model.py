from sqlalchemy import Column, Integer, String, Table, MetaData
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr

Base = declarative_base()

class UserBase(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class User(Base):
    __tablename__ = "user"
    
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