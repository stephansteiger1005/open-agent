# OpenWebUI Integration

This document describes how to use the OpenWebUI interface with the multi-agent system.

## Overview

OpenWebUI is integrated into the system and provides a user-friendly chat interface for interacting with the multi-agent system. The integration exposes each agent as a separate model in OpenWebUI:

- **Router/Planner** - Intelligent agent routing and task coordination
- **General Assistant** - General-purpose conversational AI
- **Tool Agent** - Executes MCP tool calls
- **SQL Agent** - Database queries and analysis
- **DevOps Agent** - Infrastructure and deployment tasks
- **Documentation Agent** - Documentation search and creation

All agents use OpenAI for chat completion via the integrated OpenAI provider.

## Quick Start

1. Make sure you have set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=sk-your-key-here
```

2. Start all services including OpenWebUI:
```bash
docker-compose up --build
```

3. Open OpenWebUI in your browser:
```
http://localhost:3000
```

4. The agents will be automatically available as models in the OpenWebUI interface.

## How It Works

The integration uses an OpenWebUI "pipe" (function) to bridge OpenWebUI with the multi-agent REST API:

```
OpenWebUI (UI) 
  ↓
openwebui_pipe.py (Bridge)
  ↓
API Service (FastAPI)
  ↓
Orchestrator (Agent Execution)
  ↓
OpenAI Provider (Chat Completion)
```

### Architecture

1. **OpenWebUI Service**: Runs the OpenWebUI frontend on port 3000
2. **Pipe Integration**: The `openwebui_pipe.py` file acts as a bridge between OpenWebUI and the agent API
3. **Model Discovery**: The pipe dynamically discovers available agents from the API and exposes them as models
4. **Chat Completion**: When you chat with a model, the pipe:
   - Creates a conversation in the API
   - Adds messages to the conversation
   - Executes a run with the selected agent
   - Streams the response back to OpenWebUI
5. **OpenAI Integration**: The agent uses the OpenAI provider for actual LLM responses

## Using the Interface

### Selecting an Agent

1. In OpenWebUI, click on the model dropdown (top of chat)
2. Under "Multi-Agent System", you'll see all available agents
3. Select the agent you want to chat with:
   - **Router/Planner** for complex tasks requiring coordination
   - **General Assistant** for general questions and conversation
   - **SQL Agent** for database-related queries
   - **DevOps Agent** for infrastructure questions
   - **Documentation Agent** for documentation tasks

### Chatting

Simply type your message and press Enter. The selected agent will:
1. Receive your message
2. Process it using OpenAI
3. Stream the response back in real-time

### Router Agent

The Router/Planner agent is special - it can:
- Analyze your request
- Determine which specialist agent is best suited
- Coordinate multiple agents for complex tasks
- Delegate work to other agents

Example: Ask the Router "How do I query the database for user statistics?" and it will route to the SQL Agent.

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# OpenAI API Key (required)
OPENAI_API_KEY=sk-your-key-here

# Agent API Configuration (used by the pipe)
AGENT_API_BASE_URL=http://api:8000
AGENT_API_KEY=dev_key_123456789

# Optional: Change OpenAI model
DEFAULT_MODEL=gpt-4

# Optional: Enable debug logging
LOG_LEVEL=DEBUG
```

### Customizing Agents

Edit `config/agents.yaml` to customize agents:

```yaml
agents:
  - id: my_custom_agent
    name: My Custom Agent
    role: specialist
    system_prompt: |
      You are a custom specialist agent.
      Your role is to...
    model: ${DEFAULT_MODEL}
    allowed_tools: []
```

After editing, restart the services:
```bash
docker-compose restart
```

## Troubleshooting

### OpenWebUI doesn't show agents

1. Check that the API service is running:
```bash
curl http://localhost:8000/health
```

2. Check OpenWebUI logs:
```bash
docker-compose logs openwebui
```

3. Verify the pipe is installed:
   - The pipe should be automatically mounted at container startup
   - Check `/app/backend/data/functions/multi_agent_pipe.py` in the container

### Agent responses are slow

1. Check OpenAI API connectivity from the container:
```bash
docker-compose exec api curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

2. Increase timeout in `.env`:
```bash
OPENAI_TIMEOUT=120
```

3. Check logs for detailed timing information:
```bash
docker-compose logs orchestrator | grep "OpenAI"
```

### Authentication errors

The OpenWebUI interface is configured with `WEBUI_AUTH=false` for easier setup. The pipe authenticates with the agent API using the API key from `.env`.

If you get authentication errors:
1. Verify `API_KEYS` in `.env` matches `AGENT_API_KEY`
2. Check API logs: `docker-compose logs api`

## Advanced Usage

### Streaming vs Non-Streaming

By default, responses are streamed for a better user experience. To disable streaming, modify the pipe:

```python
stream = body.get("stream", False)  # Change True to False
```

### Custom Prompts

You can customize the system prompts for each agent in `config/agents.yaml`. This affects how the agent behaves in OpenWebUI.

### Adding More Agents

1. Add the agent definition to `config/agents.yaml`
2. Restart the services
3. The new agent will automatically appear in OpenWebUI

### Integration with External Tools

The agents can use MCP tools. To add tools:

1. Configure MCP servers in `.env`:
```bash
MCP_SERVERS=stdio://path/to/mcp/server
```

2. Grant tool access in `config/agents.yaml`:
```yaml
allowed_tools: [tool_name]
```

3. Configure security policies in `config/tool_policies.yaml`

## API Direct Access

While OpenWebUI provides the UI, you can also access the agent API directly:

```bash
# List available agents
curl http://localhost:8000/v1/agents \
  -H "Authorization: Bearer dev_key_123456789"

# Create a conversation and chat
CONV_ID=$(curl -X POST http://localhost:8000/v1/conversations \
  -H "Authorization: Bearer dev_key_123456789" \
  -H "Content-Type: application/json" \
  -d '{"metadata":{}}' | jq -r '.id')

# Add a message
curl -X POST http://localhost:8000/v1/conversations/$CONV_ID/messages \
  -H "Authorization: Bearer dev_key_123456789" \
  -H "Content-Type: application/json" \
  -d '{"role":"user","content":"Hello!"}'

# Execute with router agent
curl -X POST http://localhost:8000/v1/conversations/$CONV_ID/runs \
  -H "Authorization: Bearer dev_key_123456789" \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"router","stream":false}'
```

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                   User Browser                      │
│                 http://localhost:3000                │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              OpenWebUI Container                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         Multi-Agent Pipe (Python)            │  │
│  │  - Model discovery                           │  │
│  │  - Conversation management                   │  │
│  │  - Response streaming                        │  │
│  └──────────────┬───────────────────────────────┘  │
└─────────────────┼───────────────────────────────────┘
                  │ HTTP
                  ▼
┌─────────────────────────────────────────────────────┐
│              API Service (FastAPI)                   │
│  Endpoints: /v1/conversations, /v1/agents, /v1/runs │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│            Orchestrator Service                      │
│  ┌──────────────────────────────────────────────┐  │
│  │          Agent Registry                      │  │
│  │  - router, general, tool, sql, devops, docs │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐  │
│  │         OpenAI Provider                      │  │
│  │  - Chat completion                           │  │
│  │  - Streaming support                         │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
          OpenAI API (api.openai.com)
```

## Next Steps

1. **Explore Different Agents**: Try chatting with different specialized agents
2. **Test Router Agent**: Ask complex questions to see agent routing in action
3. **Configure Custom Agents**: Add your own specialized agents
4. **Enable MCP Tools**: Connect MCP servers for tool execution
5. **Deploy to Production**: See SETUP.md for production deployment guide

## Support

For issues or questions:
1. Check the logs: `docker-compose logs`
2. Review SETUP.md for detailed configuration
3. Check the API docs: http://localhost:8000/docs
