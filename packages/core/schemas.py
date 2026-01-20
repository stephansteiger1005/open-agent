from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class RunStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# Request Models
class CreateConversationRequest(BaseModel):
    metadata: Optional[Dict[str, Any]] = {}


class CreateMessageRequest(BaseModel):
    role: MessageRole
    content: str
    attachments: Optional[List[Dict[str, Any]]] = []


class CreateRunRequest(BaseModel):
    agent_id: str = "router"
    stream: bool = False
    metadata: Optional[Dict[str, Any]] = {}


# Response Models
class ConversationResponse(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime
    metadata_: Dict[str, Any] = Field(alias="metadata")

    class Config:
        from_attributes = True
        populate_by_name = True


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    attachments: List[Dict[str, Any]]
    created_at: datetime
    metadata_: Dict[str, Any] = Field(alias="metadata")

    class Config:
        from_attributes = True
        populate_by_name = True


class RunResponse(BaseModel):
    id: str
    conversation_id: str
    agent_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata_: Dict[str, Any] = Field(alias="metadata")

    class Config:
        from_attributes = True
        populate_by_name = True


class StepResponse(BaseModel):
    id: str
    run_id: str
    step_number: int
    agent_id: str
    status: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        from_attributes = True


class ToolCallResponse(BaseModel):
    id: str
    step_id: str
    tool_name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    system_prompt: str
    model: str
    allowed_tools: List[str]


class ToolResponse(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]


# Event Models
class StreamEvent(BaseModel):
    event: str
    data: Dict[str, Any]
