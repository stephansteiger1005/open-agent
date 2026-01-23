# open-agent
## Demo Project: OpenWebUI with MCP Tools

A simplified demo showing OpenWebUI integrated with MCP (Model Context Protocol) tools. This project demonstrates how to connect OpenWebUI with custom tools that provide constant demo data.

---

## What's Included

This demo consists of just 2 Docker services:

1. **OpenWebUI** - A user-friendly chat interface
   - No external models required
   - Pre-configured for demo use
   - MCP tools integration enabled
   - Accessible at http://localhost:3000

2. **MCP Server** - Provides two demo tools:
   - `get_weather` - Returns constant weather data for San Francisco
   - `get_user_info` - Returns constant user profile information

---

## Quick Start

1. **Start the services:**
   ```bash
   docker compose up --build
   ```

2. **Access OpenWebUI:**
   - Open your browser to http://localhost:3000
   - No authentication required (demo mode)

3. **Access the MCP Tools API:**
   - The tool server is available at http://localhost:8080
   - View available tools: http://localhost:8080/tools
   - Health check: http://localhost:8080/health

---

## Using the Tools

### Integration with OpenWebUI

The MCP server uses the official Model Context Protocol (MCP) Python library and provides tools via SSE (Server-Sent Events) transport, which is compatible with OpenWebUI's MCP integration.

**OpenWebUI Configuration:**

To connect OpenWebUI to the MCP server:

1. **Access OpenWebUI** at http://localhost:3000
2. **Navigate to** "Externe Werkzeuge" (External Tools) in the settings
3. **Click** "Verbindung hinzufügen" (Add Connection)
4. **Configure the connection** with the following settings:
   - **Type**: MCP - Streamables HTTP
   - **URL**: `http://mcp-server:8080/sse` (from within Docker network)
     - Or `http://localhost:8080/sse` (from host machine)
   - **Authentication**: None (Keine)
   - **ID**: `demo-mcp-server` (or any unique identifier)
   - **Name**: `Demo MCP Server`
   - **Description**: `Demo MCP server with weather and user info tools`
   - **Visibility**: Public (Öffentlich)
5. **Save** the configuration

The MCP server will automatically expose two tools:
- `get_weather` - Returns weather data for San Francisco
- `get_user_info` - Returns demo user profile information

**Note:** The MCP server uses the official MCP protocol over SSE transport, making it compatible with OpenWebUI and other MCP-compliant clients.

### Direct API Access

The MCP server uses the official Model Context Protocol over SSE (Server-Sent Events) transport. While primarily designed for MCP clients like OpenWebUI, you can also interact with it using standard MCP client libraries.

**Testing the Server:**

You can verify the server is running by checking the SSE endpoint:

```bash
# Test SSE endpoint (will keep connection open)
curl http://localhost:8080/sse -H "Accept: text/event-stream"
```

**Available Tools:**
- `get_weather` - Returns current weather information for San Francisco
- `get_user_info` - Returns demo user profile information

To interact with the tools, use an MCP-compatible client or OpenWebUI's external tools feature.

---

## Architecture

```
┌─────────────────┐
│   OpenWebUI     │  http://localhost:3000
│  (Chat UI)      │  
└────────┬────────┘
         │
         │ MCP over SSE (http://mcp-server:8080/sse)
         │
┌────────▼────────┐
│   MCP Server    │  http://localhost:8080
│  (FastMCP/SSE)  │
│                 │
│  • get_weather  │  Returns demo weather data
│  • get_user_info│  Returns demo user data
└─────────────────┘
```

---

## MCP Tools

The server exposes two tools via the Model Context Protocol:

### get_weather
Returns current weather information for San Francisco.

**Tool Name:** `get_weather`

**Parameters:** None

**Returns:** JSON string with weather data including:
- Current temperature and conditions
- Humidity and wind information  
- 3-day forecast

### get_user_info
Returns information about a demo user.

**Tool Name:** `get_user_info`

**Parameters:** None

**Returns:** JSON string with user data including:
- User profile information
- Associated projects
- Skills and preferences

**Note:** These tools are accessible through MCP-compatible clients like OpenWebUI. The server uses the official MCP Python library (v1.7.1) with SSE transport.

---

## Files Structure

```
.
├── docker-compose.yml      # Defines the 2 services
├── Dockerfile.mcp          # Dockerfile for MCP server
├── mcp_server.py           # MCP server using official mcp library v1.7.1
├── requirements.txt        # Python dependencies (mcp==1.7.1)
├── README.md               # This file
├── QUICKSTART.md           # Quick start guide
└── .env.example            # Environment variables example
```

---

## Stopping the Demo

```bash
docker compose down
```

To also remove volumes:
```bash
docker compose down -v
```

---

## Extending the Demo

### Adding More Tools

To add more tools to the MCP server:

1. Edit `mcp_server.py`
2. Add constant data for your tool (similar to `WEATHER_DATA` and `USER_INFO_DATA`)
3. Add a new function decorated with `@mcp.tool()`:
   ```python
   @mcp.tool()
   def your_tool_name(param1: str, param2: int) -> str:
       """Description of what your tool does"""
       # Your tool logic here
       return json.dumps(YOUR_TOOL_DATA, indent=2)
   ```
4. Rebuild and restart: `docker compose up --build`

The tool will automatically be available to MCP clients like OpenWebUI.

### Customizing Data

Edit the constant data dictionaries at the top of `mcp_server.py`:
- `WEATHER_DATA` - Modify weather information
- `USER_INFO_DATA` - Modify user profile data

---

## Requirements

- Docker
- Docker Compose

No other dependencies needed - everything runs in containers!

---

## Troubleshooting

**Services won't start:**
```bash
docker compose logs
```

**MCP server not responding:**
```bash
# Test the SSE endpoint
curl http://localhost:8080/sse -H "Accept: text/event-stream"
```

**OpenWebUI not loading:**
```bash
docker compose logs openwebui
```

---

## Learn More

- [OpenWebUI Documentation](https://github.com/open-webui/open-webui)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
