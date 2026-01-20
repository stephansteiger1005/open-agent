import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from packages.core.models import Base, Conversation, Message
import uuid


@pytest.fixture
async def test_db():
    """Create a test database"""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    async with AsyncSessionLocal() as session:
        yield session
    
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_conversation(test_db):
    """Test creating a conversation"""
    conversation = Conversation(
        id=str(uuid.uuid4()),
        metadata={"test": "data"},
    )
    test_db.add(conversation)
    await test_db.commit()
    await test_db.refresh(conversation)
    
    assert conversation.id is not None
    assert conversation.metadata["test"] == "data"


@pytest.mark.asyncio
async def test_create_message(test_db):
    """Test creating a message"""
    # Create conversation first
    conversation = Conversation(
        id=str(uuid.uuid4()),
        metadata={},
    )
    test_db.add(conversation)
    await test_db.commit()
    
    # Create message
    message = Message(
        id=str(uuid.uuid4()),
        conversation_id=conversation.id,
        role="user",
        content="Hello world",
        attachments=[],
    )
    test_db.add(message)
    await test_db.commit()
    await test_db.refresh(message)
    
    assert message.id is not None
    assert message.conversation_id == conversation.id
    assert message.content == "Hello world"


def test_agent_registry():
    """Test agent registry"""
    from apps.orchestrator.agents import AgentRegistry
    
    # Create a temporary test config
    import tempfile
    import yaml
    
    config = {
        "agents": [
            {
                "id": "test_agent",
                "name": "Test Agent",
                "role": "test",
                "system_prompt": "Test prompt",
                "model": "gpt-4",
                "allowed_tools": ["tool1", "tool2"],
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        config_path = f.name
    
    registry = AgentRegistry(config_path)
    
    # Test getting agent
    agent = registry.get_agent("test_agent")
    assert agent is not None
    assert agent.name == "Test Agent"
    
    # Test listing agents
    agents = registry.list_agents()
    assert len(agents) == 1
    
    # Test tool allowlist
    assert registry.is_tool_allowed("test_agent", "tool1")
    assert not registry.is_tool_allowed("test_agent", "tool3")
    
    # Cleanup
    import os
    os.unlink(config_path)


@pytest.mark.asyncio
async def test_mcp_client():
    """Test MCP client"""
    from apps.mcp_gateway.client import MCPClient
    
    client = MCPClient()
    
    # Test discovering tools
    tools = await client.discover_tools()
    assert len(tools) > 0
    
    # Test getting a specific tool
    tool = client.get_tool("db_query")
    assert tool is not None
    assert tool["name"] == "db_query"
    
    # Test invoking a tool
    result = await client.invoke_tool("db_query", {"query": "SELECT 1"})
    assert result["success"] is True
