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
- Build the MCP server using the official mcp library (v1.7.1)
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

### MCP Server (Tool Server)
The MCP server is available at:
```
http://localhost:8080
```

The server uses the Model Context Protocol over SSE transport at:
```
http://localhost:8080/sse
```

## Step 3: Configure OpenWebUI to Use MCP Tools

### Connecting OpenWebUI to the MCP Server

1. **Open OpenWebUI** at http://localhost:3000
2. **Navigate to Settings** and find "Externe Werkzeuge" (External Tools)
3. **Click** "Verbindung hinzufügen" (Add Connection)
4. **Configure** the MCP connection:
   - **Type**: Select "MCP - Streamables HTTP"
   - **URL**: Enter `http://mcp-server:8080/sse`
   - **Authentication**: Select "None" (Keine)
   - **ID**: `demo-mcp-server`
   - **Name**: `Demo MCP Server`
   - **Description**: `Demo MCP server with weather and user info tools`
   - **Visibility**: Select "Public" (Öffentlich)
5. **Save** the connection

### Available Tools

Once configured, OpenWebUI will have access to two tools:
- **get_weather** - Returns weather data for San Francisco
- **get_user_info** - Returns demo user profile information

You can now use these tools in your chats by asking the AI to use them!

## Testing the MCP Server

### Verify Server is Running

```bash
# Test the SSE endpoint (will keep connection open)
curl http://localhost:8080/sse -H "Accept: text/event-stream"
```

Press Ctrl+C to stop the curl command.

## That's It!

You now have:
- ✅ A working MCP server using the official mcp library (v1.7.1)
- ✅ MCP server with 2 tools accessible via SSE transport
- ✅ OpenWebUI running and ready to connect to the MCP server
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
5. The new tool will automatically be available in OpenWebUI

**Explore the code:**
- `mcp_server.py` - MCP server using official mcp library
- `docker-compose.yml` - Service configuration
- `Dockerfile.mcp` - MCP server container definition

See `README.md` for detailed documentation!
