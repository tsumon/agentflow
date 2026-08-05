"""SQLAlchemy async models for AgentFlow."""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey, create_engine
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.config import settings


class Base(DeclarativeBase):
    pass


# --- Models ---

class AgentRecord(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # planner, executor, reviewer
    description = Column(Text, default="")
    system_prompt = Column(Text, default="")
    config = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("TaskRecord", back_populates="agent")


class TaskRecord(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    plan = Column(JSON, default=list)
    result = Column(Text, default="")
    error = Column(Text, default="")
    execution_log = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    agent = relationship("AgentRecord", back_populates="tasks")
    messages = relationship("MessageRecord", back_populates="task", order_by="MessageRecord.created_at")


class MessageRecord(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, default="")
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    task = relationship("TaskRecord", back_populates="messages")


class KnowledgeRecord(Base):
    __tablename__ = "knowledge"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(String(100), unique=True, nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, default="")
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)


# --- Async Engine ---

sync_engine = create_engine(
    settings.database_url.replace("+aiosqlite", ""),
    echo=False,
)

async_engine = create_async_engine(
    settings.database_url,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Create all tables."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
