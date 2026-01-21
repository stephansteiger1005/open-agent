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
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        if hasattr(obj, 'metadata_'):
            data = {
                'id': obj.id,
                'created_at': obj.created_at,
                'updated_at': obj.updated_at,
                'metadata': obj.metadata_ or {}
            }
            return cls(**data)
        return super().model_validate(obj)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    attachments: List[Dict[str, Any]]
    created_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        if hasattr(obj, 'metadata_'):
            data = {
                'id': obj.id,
                'conversation_id': obj.conversation_id,
                'role': obj.role,
                'content': obj.content,
                'attachments': obj.attachments or [],
                'created_at': obj.created_at,
                'metadata': obj.metadata_ or {}
            }
            return cls(**data)
        return super().model_validate(obj)


class RunResponse(BaseModel):
    id: str
    conversation_id: str
    agent_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        
    @classmethod
    def model_validate(cls, obj):
        if hasattr(obj, 'metadata_'):
            data = {
                'id': obj.id,
                'conversation_id': obj.conversation_id,
                'agent_id': obj.agent_id,
                'status': obj.status,
                'started_at': obj.started_at,
                'completed_at': obj.completed_at,
                'error': obj.error,
                'metadata': obj.metadata_ or {}
            }
            return cls(**data)
        return super().model_validate(obj)


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
