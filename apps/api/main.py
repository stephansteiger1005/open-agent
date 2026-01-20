from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
import os
import json

from packages.core.database import init_db, get_session
from packages.core.models import Conversation, Message, Run, Step
from packages.core.schemas import (
    CreateConversationRequest,
    CreateMessageRequest,
    CreateRunRequest,
    ConversationResponse,
    MessageResponse,
    RunResponse,
    StepResponse,
    AgentResponse,
    ToolResponse,
    StreamEvent,
)
from apps.orchestrator.agents import get_agent_registry
from apps.orchestrator.engine import get_orchestrator
from apps.mcp_gateway.client import get_mcp_client


app = FastAPI(
    title="Multi-Agent OpenWebUI API",
    description="Production-ready multi-agent system with MCP and REST API",
    version="1.0.0",
)


# Authentication dependency
async def verify_api_key(authorization: Optional[str] = Header(None)):
    """Verify API key authentication"""
    auth_mode = os.getenv("AUTH_MODE", "apikey")
    
    if auth_mode == "apikey":
        api_keys = os.getenv("API_KEYS", "").split(",")
        
        if not authorization:
            raise HTTPException(status_code=401, detail="Missing authorization header")
        
        # Support both "Bearer <key>" and raw key
        token = authorization.replace("Bearer ", "").strip()
        
        if token not in api_keys:
            raise HTTPException(status_code=401, detail="Invalid API key")
    
    return True


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    await init_db()
    # Initialize agent registry and MCP client
    get_agent_registry()
    get_mcp_client()


# Conversation endpoints
@app.post("/v1/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(verify_api_key),
):
    """Create a new conversation"""
    conversation = Conversation(
        id=str(uuid.uuid4()),
        metadata_=request.metadata,
    )
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    return ConversationResponse.model_validate(conversation)


@app.get("/v1/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(verify_api_key),
):
    """Get conversation by ID"""
    result = await session.execute(
        select(Conversation).filter(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return ConversationResponse.model_validate(conversation)


@app.post("/v1/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: str,
    request: CreateMessageRequest,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(verify_api_key),
):
    """Add a message to a conversation"""
    # Verify conversation exists
    result = await session.execute(
        select(Conversation).filter(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        role=request.role.value,
        content=request.content,
        attachments=request.attachments or [],
        metadata_={},
    )
    session.add(message)
    await session.commit()
    await session.refresh(message)
    return MessageResponse.model_validate(message)


# Run endpoints
@app.post("/v1/conversations/{conversation_id}/runs")
async def create_run(
    conversation_id: str,
    request: CreateRunRequest,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(verify_api_key),
):
    """Create and execute a run"""
    # Verify conversation exists
    result = await session.execute(
        select(Conversation).filter(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Create run
    run = Run(
        id=str(uuid.uuid4()),
        conversation_id=conversation_id,
        agent_id=request.agent_id,
        status="queued",
        metadata_=request.metadata,
    )
    session.add(run)
    await session.commit()
    await session.refresh(run)
    
    # Execute run
    orchestrator = get_orchestrator()
    
    if request.stream:
        # Return streaming response
        async def event_generator():
            async for event in orchestrator.execute_run(session, run, stream=True):
                yield f"event: {event.event}\ndata: {json.dumps(event.data)}\n\n"
        
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
        )
    else:
        # Execute synchronously
        events = []
        async for event in orchestrator.execute_run(session, run, stream=False):
            events.append(event)
        
        return {"run_id": run.id, "status": run.status}


@app.get("/v1/runs/{run_id}", response_model=RunResponse)
async def get_run(
    run_id: str,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(verify_api_key),
):
    """Get run by ID"""
    result = await session.execute(
        select(Run).filter(Run.id == run_id)
    )
    run = result.scalar_one_or_none()
    
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    
    return RunResponse.model_validate(run)


@app.get("/v1/runs/{run_id}/steps", response_model=List[StepResponse])
async def get_run_steps(
    run_id: str,
    session: AsyncSession = Depends(get_session),
    _: bool = Depends(verify_api_key),
):
    """Get steps for a run"""
    result = await session.execute(
        select(Step).filter(Step.run_id == run_id).order_by(Step.step_number)
    )
    steps = result.scalars().all()
    return steps


# Agent endpoints
@app.get("/v1/agents", response_model=List[AgentResponse])
async def list_agents(
    _: bool = Depends(verify_api_key),
):
    """List all agents"""
    registry = get_agent_registry()
    agents = registry.list_agents()
    return [agent.to_dict() for agent in agents]


@app.get("/v1/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    _: bool = Depends(verify_api_key),
):
    """Get agent by ID"""
    registry = get_agent_registry()
    agent = registry.get_agent(agent_id)
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent.to_dict()


# Tool endpoints
@app.get("/v1/tools", response_model=List[ToolResponse])
async def list_tools(
    _: bool = Depends(verify_api_key),
):
    """List all available tools"""
    mcp_client = get_mcp_client()
    tools = await mcp_client.discover_tools()
    return tools


@app.get("/v1/tools/{tool_name}", response_model=ToolResponse)
async def get_tool(
    tool_name: str,
    _: bool = Depends(verify_api_key),
):
    """Get tool by name"""
    mcp_client = get_mcp_client()
    tool = mcp_client.get_tool(tool_name)
    
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    return tool


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
