import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True)
    password_hash = Column(String)
    daily_count = Column(Integer, default=0)

    chats = relationship("Chat", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, ForeignKey("users.username"))

    question = Column(Text)
    answer = Column(Text)

    user = relationship("User", back_populates="chats")


def init_db():
    Base.metadata.create_all(bind=engine)

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True)
    filename = Column(String)
    content = Column(Text)
