# Quick Start Guide

Get up and running with the OpenWebUI MCP demo in 3 simple steps!

## Prerequisites

- Docker installed
- Docker Compose installed

## Step 1: Start the Services

```bash
docker compose up --build
```

This will:
- Build the MCP server with 2 demo tools
- Pull and start OpenWebUI
- Configure everything automatically

Wait about 30 seconds for services to fully start.

## Step 2: Access the Services

### OpenWebUI (Chat Interface)
Open your browser and navigate to:
```
http://localhost:3000
```

No login required - the demo runs in open mode!

### MCP Server (Tool API)
The tool server is available at:
```
http://localhost:8080
```

Check available tools:
```
http://localhost:8080/tools
```

## Step 3: Try the MCP Tools

### Option A: Using the API Directly

**Test the weather tool:**
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_weather"}'
```

**Test the user info tool:**
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_user_info"}'
```

**List all available tools:**
```bash
curl http://localhost:8080/tools
```

### Option B: Using OpenWebUI

The tools are accessible via the MCP server API endpoint configured in OpenWebUI. You can integrate them through OpenWebUI's function/tool system depending on your OpenWebUI version.

## That's It!

You now have:
- ✅ A working MCP server with 2 tools returning constant JSON data
- ✅ OpenWebUI running and accessible
- ✅ A clean, minimal demo setup

## Testing the Tools

### Weather Tool Response
```json
{
  "success": true,
  "result": {
    "location": "San Francisco, CA",
    "temperature": 72,
    "conditions": "Sunny",
    "humidity": 65,
    "forecast": [...]
  }
}
```

### User Info Tool Response
```json
{
  "success": true,
  "result": {
    "id": "user-12345",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "Developer",
    "projects": [...]
  }
}
```

## Stopping the Demo

Press `Ctrl+C` in the terminal where docker compose is running, then:
```bash
docker compose down
```

## Next Steps

**Add your own tools:**
1. Edit `mcp_server.py`
2. Add constant data for your tool
3. Add tool definition in `list_tools()`
4. Add tool handler in `execute_tool()`
5. Rebuild: `docker compose up --build`

**Explore the code:**
- `mcp_server.py` - Simple FastAPI server with 2 tools
- `docker-compose.yml` - Service configuration
- `Dockerfile.mcp` - MCP server container definition

See `README.md` for detailed documentation!
