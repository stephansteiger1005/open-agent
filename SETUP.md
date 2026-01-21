# Multi-Agent OpenWebUI System - Setup Guide

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+ (for local development)
- jq (for running curl examples)

### Running with Docker

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Edit `.env` and set your API keys:
```bash
# Required for OpenAI-powered agents
OPENAI_API_KEY=your_key_here

# Optional for development (defaults to mock responses if not set)
```

3. Start the system:
```bash
docker compose up --build
```

4. Access the services:
   - **OpenWebUI Interface**: `http://localhost:3000` - User-friendly chat interface with all agents
   - **API Server**: `http://localhost:8000` - REST API for programmatic access
   - **API Documentation**: `http://localhost:8000/docs` - Interactive API docs

**Note on Networking:** The system uses standard Docker networking for service communication. All services can communicate with each other using their service names (e.g., `api:8000`, `openwebui:8080`).

## Using OpenWebUI

Once the system is running, open your browser to `http://localhost:3000` to access the OpenWebUI interface.

### First Time Setup

1. OpenWebUI will automatically discover all available agents from the API
2. Select an agent from the model dropdown (top of the chat interface)
3. Start chatting!

### Available Agents

All agents are exposed as models in OpenWebUI:

- **Router/Planner** - Intelligent task routing and coordination
- **General Assistant** - General-purpose conversational AI
- **Tool Agent** - Executes MCP tool calls
- **SQL Agent** - Database queries and analysis
- **DevOps Agent** - Infrastructure and deployment tasks
- **Documentation Agent** - Documentation search and creation

See [OPENWEBUI.md](OPENWEBUI.md) for detailed usage instructions.

### Testing the API

Run the included curl examples:
```bash
./examples/curl_examples.sh
```

Run the OpenAI agent selection and chat completion example:
```bash
./examples/openai_agent_example.sh
```

Or test manually:
```bash
# Health check
curl http://localhost:8000/health

# Create a conversation
curl -X POST http://localhost:8000/v1/conversations \
  -H "Authorization: Bearer dev_key_123456789" \
  -H "Content-Type: application/json" \
  -d '{"metadata": {}}'
```

### Local Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set environment variables:
```bash
export DATABASE_URL=sqlite:///data/app.db
export AUTH_MODE=apikey
export API_KEYS=dev_key_123456789
```

4. Run the API server:
```bash
uvicorn apps.api.main:app --reload
```

## Architecture

The system consists of three main components:

### 1. API Service (`apps/api/`)
- FastAPI-based REST API
- Handles conversations, messages, runs
- Server-Sent Events (SSE) for streaming
- API key authentication

### 2. Orchestrator (`apps/orchestrator/`)
- Agent routing and execution
- Multi-step planning
- Tool invocation coordination
- Event streaming
- **OpenAI integration for intelligent agent responses**

### 3. MCP Gateway (`apps/mcp_gateway/`)
- Tool discovery from MCP servers
- Schema validation
- Tool invocation
- Security policies

## OpenAI Integration

The system supports OpenAI for two key use cases:

### 1. Agent Selection (Router Agent)
The router agent uses OpenAI to intelligently classify user requests and select the most appropriate specialist agent:
- Analyzes user intent
- Determines which agent(s) should handle the request
- Creates execution plans for multi-step tasks

### 2. General Purpose Chat Completion
The general purpose agent uses OpenAI for natural language interactions:
- Answers questions
- Engages in conversation
- Provides helpful assistance

### Configuration
Set your OpenAI API key in `.env`:
```bash
OPENAI_API_KEY=sk-...your-key-here
```

If `OPENAI_API_KEY` is not set, the system falls back to mock responses for testing.

### Example Usage
See `examples/openai_agent_example.sh` for a complete demonstration of:
- Router agent classifying a SQL query request
- General purpose agent answering a question about microservices

## API Documentation

Once running, visit:
- API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Key Endpoints

**Conversations**
- `POST /v1/conversations` - Create conversation
- `GET /v1/conversations/{id}` - Get conversation
- `POST /v1/conversations/{id}/messages` - Add message

**Runs**
- `POST /v1/conversations/{id}/runs` - Execute with agent
- `GET /v1/runs/{id}` - Get run details
- `GET /v1/runs/{id}/steps` - Get execution steps

**Agents**
- `GET /v1/agents` - List all agents
- `GET /v1/agents/{id}` - Get agent details

**Tools**
- `GET /v1/tools` - List available tools
- `GET /v1/tools/{name}` - Get tool schema

## Configuration

### Agents (`config/agents.yaml`)
Define your agents:
```yaml
agents:
  - id: custom_agent
    name: Custom Agent
    role: specialist
    system_prompt: "Your custom prompt"
    model: gpt-4
    allowed_tools: [tool1, tool2]
```

### Tool Policies (`config/tool_policies.yaml`)
Configure security policies:
```yaml
policies:
  - tool_pattern: "db_*"
    rules:
      - type: sql_safety
        block_keywords: [DROP, DELETE]
```

## OpenWebUI Integration

OpenWebUI is **fully integrated** and runs automatically with `docker compose up`.

### Quick Access

- **UI**: http://localhost:3000
- **Features**: 
  - All agents available as models
  - Real-time streaming responses
  - No additional configuration needed
  - Uses OpenAI for chat completion

### How It Works

The integration uses a custom pipe (`apps/openwebui_pipe.py`) that:
1. Discovers agents from the API automatically
2. Exposes each agent as a model in OpenWebUI
3. Routes chat messages through the API to the orchestrator
4. Streams responses back using OpenAI

For detailed usage instructions, see [OPENWEBUI.md](OPENWEBUI.md).

### Manual Integration (Advanced)

If you want to set up OpenWebUI separately or customize the integration, here's the reference implementation:

```python
# openwebui_pipe.py
import requests

class MultiAgentPipe:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.api_key = "dev_key_123456789"
    
    def pipe(self, user_message: str, model_id: str, messages: list):
        # Create conversation
        conv_response = requests.post(
            f"{self.api_base}/v1/conversations",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"metadata": {}}
        )
        conv_id = conv_response.json()["id"]
        
        # Add message
        requests.post(
            f"{self.api_base}/v1/conversations/{conv_id}/messages",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"role": "user", "content": user_message}
        )
        
        # Create run with streaming
        response = requests.post(
            f"{self.api_base}/v1/conversations/{conv_id}/runs",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"agent_id": "router", "stream": true},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                # Parse SSE and yield
                yield line.decode()
```

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run specific tests:
```bash
pytest tests/test_core.py -v
```

## Extending the System

### Adding a New Agent

1. Edit `config/agents.yaml`:
```yaml
- id: my_agent
  name: My Custom Agent
  role: specialist
  system_prompt: "Your prompt here"
  model: ${DEFAULT_MODEL}
  allowed_tools: []
```

2. Restart the services

### Adding a New Tool

1. Implement the tool in your MCP server
2. The tool will be auto-discovered on startup
3. Configure policies in `config/tool_policies.yaml` if needed

### Custom Model Provider

Set environment variables:
```bash
MODEL_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama2
```

## Troubleshooting

**Database locked errors**
- Stop all services: `docker-compose down`
- Remove data: `rm -rf data/`
- Restart: `docker-compose up --build`

**Authentication errors**
- Check API_KEYS in `.env`
- Verify Authorization header format: `Bearer <key>`

**Agent not found**
- Verify agent ID in `config/agents.yaml`
- Check for YAML syntax errors

**OpenAI API connection errors**
- The system uses host networking mode to avoid connectivity issues in Docker/WSL environments
- Verify `OPENAI_API_KEY` is set correctly in `.env`
- Test API key on host: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`
- Check logs with `docker-compose logs api` or `docker-compose logs orchestrator`
- Set `LOG_LEVEL=DEBUG` for detailed OpenAI request/response logging

## Production Deployment

1. Use PostgreSQL instead of SQLite:
```bash
DATABASE_URL=postgresql://user:pass@localhost/dbname
```

2. Enable JWT authentication:
```bash
AUTH_MODE=jwt
JWT_SECRET=your_secret_key
```

3. Configure rate limiting and security policies

4. Use a reverse proxy (nginx, Caddy) for HTTPS

## License

MIT License - See LICENSE file for details
