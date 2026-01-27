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
- Build the MCP server using fastmcp
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

**For OpenWebUI configuration**, use the base URL above (without `/mcp`).

The server provides the MCP protocol endpoint at `/mcp`.

OpenWebUI automatically appends the correct paths.

## Step 3: Configure OpenWebUI to Use MCP Tools

### Direct MCP Connection

1. **Open OpenWebUI** at http://localhost:3000
2. **Navigate to Settings** and find "Externe Werkzeuge" (External Tools)
3. **Click** "Verbindung hinzufügen" (Add Connection)
4. **Configure** the MCP connection:
   - **Type**: Select "MCP - Streamables HTTP"
   - **URL**: Enter `http://mcp-server:8080` (base URL without `/mcp`)
   - **Authentication**: Select "None" (Keine)
   - **ID**: `demo-mcp-server`
   - **Name**: `Demo MCP Server`
   - **Description**: `Demo MCP server with weather and user info tools`
   - **Visibility**: Select "Public" (Öffentlich)
5. **Save** the connection

### Available Tools

Once configured, OpenWebUI will have access to three tools:
- **get_weather** - Returns weather data for a specified location (default: San Francisco)
  - Parameters: `location` (optional)
- **get_user_info** - Returns user profile information for a specified user ID (default: user-12345)
  - Parameters: `user_id` (optional)
- **get_time** - Returns current system time and timezone
  - Parameters: none

You can now use these tools in your chats by asking the AI to use them!

## Testing the Services

### Verify MCP Server is Running

```bash
# Test the MCP endpoint
curl http://localhost:8080/mcp
```

## That's It!

You now have:
- ✅ A working Ollama instance with llama3 model for chat interactions
- ✅ A working MCP server using fastmcp
- ✅ MCP server with 3 tools accessible via HTTP transport
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
5. The new tool will automatically be available in the MCP server

**Explore the code:**
- `mcp_server.py` - MCP server using fastmcp
- `docker-compose.yml` - Service configuration
- `Dockerfile.mcp` - MCP server container definition

See `README.md` for detailed documentation!
