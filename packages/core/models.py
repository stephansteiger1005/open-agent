from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Integer, Text, Enum
from sqlalchemy.orm import declarative_base, relationship
import enum

Base = declarative_base()


class RunStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)
    
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    runs = relationship("Run", back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    attachments = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_ = Column("metadata", JSON, default=dict)
    
    conversation = relationship("Conversation", back_populates="messages")


class Run(Base):
    __tablename__ = "runs"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    agent_id = Column(String)
    status = Column(String)  # queued, running, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    
    conversation = relationship("Conversation", back_populates="runs")
    steps = relationship("Step", back_populates="run", cascade="all, delete-orphan")


class Step(Base):
    __tablename__ = "steps"
    
    id = Column(String, primary_key=True)
    run_id = Column(String, ForeignKey("runs.id"))
    step_number = Column(Integer)
    agent_id = Column(String)
    status = Column(String)  # pending, running, completed, failed
    input_data = Column(JSON, default=dict)
    output_data = Column(JSON, default=dict)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    
    run = relationship("Run", back_populates="steps")
    tool_calls = relationship("ToolCall", back_populates="step", cascade="all, delete-orphan")


class ToolCall(Base):
    __tablename__ = "tool_calls"
    
    id = Column(String, primary_key=True)
    step_id = Column(String, ForeignKey("steps.id"))
    tool_name = Column(String)
    arguments = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    step = relationship("Step", back_populates="tool_calls")
