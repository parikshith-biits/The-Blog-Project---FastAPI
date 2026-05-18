from sqlalchemy import Column,Integer,String,Text,ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(100), unique=True)
    hashed_password = Column(String(255))
    role = Column(String(20), default="user")

    posts = relationship("Post", back_populates="owner")

class Post(Base):
    __tablename__="posts"
    id = Column(Integer,primary_key=True)
    title = Column(String(200))
    content = Column(Text)
    owner_id =Column(Integer,ForeignKey("users.id"))
    owner = relationship("User",back_populates="posts")

    