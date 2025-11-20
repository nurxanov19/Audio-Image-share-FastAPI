from collections.abc import AsyncGenerator
import uuid

from sqlalchemy import String, Column, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker, async_engine_from_config
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from fastapi import Depends

from _datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

class Base(DeclarativeBase):
    pass


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "user"
    posts = relationship("Post", back_populates='user')
    role = Column(String, default="user")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    token_hash = Column(String, nullable=False, index=True)  # hashed token
    issued_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked = Column(Boolean, default=False)

    user = relationship("User")


class Post(Base):
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4())
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    caption = Column(Text)
    url = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates="posts")


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)









