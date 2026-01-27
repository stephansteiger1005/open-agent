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
- Build the Ollama container with llama3 model
- Build the MCP server using the official mcp library (v1.7.1)
- Build the MCP to OpenAPI proxy
- Pull and start OpenWebUI
- Configure everything automatically

**Note:** On first start, Ollama will automatically pull the llama3 model, which may take 5-10 minutes depending on your internet connection. Subsequent starts will be much faster.

## Step 2: Access the Services

### OpenWebUI (Chat Interface)
Open your browser and navigate to:
```
http://localhost:3000
```

No login required - the demo runs in open mode!

**Ollama with llama3 is automatically configured and ready to use.** You can start chatting immediately with the llama3 model.

### Ollama (LLM Backend)
The Ollama server with llama3 model is available at:
```
http://localhost:11434
```

This is automatically configured in OpenWebUI and provides the LLM backend for chat interactions.

### MCP Server (Tool Server)
The MCP server is available at:
```
http://localhost:8080
```

**For OpenWebUI configuration**, use the base URL above (without `/sse`).

The server provides these endpoints:
- GET `/sse` - SSE stream for server-to-client messages
- POST `/messages` - Client-to-server messages

OpenWebUI automatically appends the correct paths.

### MCP to OpenAPI Proxy
The OpenAPI proxy is available at:
```
http://localhost:8081
```

The proxy exposes MCP tools as REST endpoints:
- GET `/tools` - List available tools
- POST `/tools/{tool_name}` - Call a specific tool
- GET `/openapi.json` - OpenAPI specification
- GET `/docs` - Interactive API documentation

## Step 3: Configure OpenWebUI to Use MCP Tools

You have two options for connecting OpenWebUI to the tools:

### Option A: Direct MCP Connection (Recommended)

1. **Open OpenWebUI** at http://localhost:3000
2. **Navigate to Settings** and find "Externe Werkzeuge" (External Tools)
3. **Click** "Verbindung hinzufügen" (Add Connection)
4. **Configure** the MCP connection:
   - **Type**: Select "MCP - Streamables HTTP"
   - **URL**: Enter `http://mcp-server:8080` (base URL without `/sse`)
   - **Authentication**: Select "None" (Keine)
   - **ID**: `demo-mcp-server`
   - **Name**: `Demo MCP Server`
   - **Description**: `Demo MCP server with weather and user info tools`
   - **Visibility**: Select "Public" (Öffentlich)
5. **Save** the connection

### Option B: OpenAPI Proxy Connection

1. **Open OpenWebUI** at http://localhost:3000
2. **Navigate to Settings** and find "Externe Werkzeuge" (External Tools)
3. **Click** "Verbindung hinzufügen" (Add Connection)
4. **Configure** the OpenAPI connection:
   - **Type**: Select "OpenAPI"
   - **URL**: Enter `http://mcp-proxy:8081/openapi.json`
   - **Authentication**: Select "None" (Keine)
   - **ID**: `demo-openapi-proxy`
   - **Name**: `Demo OpenAPI Proxy`
   - **Description**: `OpenAPI proxy for MCP server tools`
   - **Visibility**: Select "Public" (Öffentlich)
5. **Save** the connection

**For detailed configuration instructions with screenshots and troubleshooting, see [OPENWEBUI_CONFIGURATION.md](OPENWEBUI_CONFIGURATION.md).**

### Available Tools

Once configured, OpenWebUI will have access to two tools:
- **get_weather** - Returns weather data for a specified location (default: San Francisco)
  - Parameters: `location` (optional)
- **get_user_info** - Returns user profile information for a specified user ID (default: user-12345)
  - Parameters: `user_id` (optional)

You can now use these tools in your chats by asking the AI to use them!

## Testing the Services

### Verify MCP Server is Running

```bash
# Test the SSE endpoint (will keep connection open)
curl http://localhost:8080/sse -H "Accept: text/event-stream"
```

Press Ctrl+C to stop the curl command.

### Verify OpenAPI Proxy is Running

```bash
# List available tools
curl http://localhost:8081/tools

# Call the weather tool
curl -X POST http://localhost:8081/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}'

# View OpenAPI specification
curl http://localhost:8081/openapi.json

# Or use the automated test script
python3 test_proxy_api.py
```

## That's It!

You now have:
- ✅ A working Ollama instance with llama3 model for chat interactions
- ✅ A working MCP server using the official mcp library (v1.7.1)
- ✅ MCP server with 2 tools accessible via SSE transport
- ✅ MCP to OpenAPI proxy exposing tools as REST endpoints
- ✅ OpenWebUI running with Ollama configured and ready to use
- ✅ A clean, minimal demo setup following MCP protocol standards

## Stopping the Demo

Press `Ctrl+C` in the terminal where docker compose is running, then:
```bash
docker compose down
```

## Next Steps

**Add your own tools:**
1. Edit `mcp_server.py`
2. Add constant data for your tool
3. Add a new function decorated with `@mcp.tool()`
4. Rebuild: `docker compose up --build`
5. The new tool will automatically be available in both MCP server and OpenAPI proxy

**Explore the code:**
- `mcp_server.py` - MCP server using official mcp library
- `mcp_openapi_proxy.py` - MCP to OpenAPI proxy server
- `docker-compose.yml` - Service configuration
- `Dockerfile.mcp` - MCP server container definition
- `Dockerfile.proxy` - OpenAPI proxy container definition

See `README.md` for detailed documentation!
