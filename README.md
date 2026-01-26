# open-agent
## Demo Project: OpenWebUI with MCP Tools

A simplified demo showing OpenWebUI integrated with MCP (Model Context Protocol) tools. This project demonstrates how to connect OpenWebUI with custom tools that provide constant demo data.

---

## What's Included

This demo consists of 4 Docker services:

1. **OpenWebUI** - A user-friendly chat interface
   - Integrated with Ollama for LLM capabilities
   - Pre-configured for demo use
   - MCP tools integration enabled
   - OpenAPI tools integration enabled
   - Accessible at http://localhost:3000

2. **Ollama** - Local LLM backend with llama3 model:
   - Provides llama3 model for chat interactions
   - Automatically pulls llama3 model on first start
   - Accessible at http://localhost:11434

3. **MCP Server** - Provides demo tools and prompts via MCP protocol:
   - **Tools:**
     - `get_weather` - Returns constant weather data for San Francisco
     - `get_user_info` - Returns constant user profile information
   - **Prompts:**
     - `analyze_weather` - Template for weather analysis
     - `review_user_profile` - Template for user profile review
     - `daily_briefing` - Template for daily summary combining weather and user info
   - Accessible at http://localhost:8080

4. **MCP to OpenAPI Proxy** - Exposes MCP tools as OpenAPI/REST endpoints:
   - Connects to the MCP server and translates MCP protocol to OpenAPI
   - Provides OpenAPI specification at `/openapi.json`
   - Interactive API docs at `/docs`
   - Accessible at http://localhost:8081

---

## Quick Start

1. **Start the services:**
   ```bash
   docker compose up --build
   ```

   Note: On first start, Ollama will automatically pull the llama3 model, which may take a few minutes depending on your internet connection.

2. **Access OpenWebUI:**
   - Open your browser to http://localhost:3000
   - No authentication required (demo mode)
   - Ollama with llama3 model is automatically configured and ready to use

3. **Access the MCP Tools API:**
   - The MCP server is available at http://localhost:8080 (MCP protocol over SSE)
   - The OpenAPI proxy is available at http://localhost:8081 (REST API)
   - View the [OpenWebUI Configuration Guide](OPENWEBUI_CONFIGURATION.md) for detailed setup instructions

---

## Using the Tools

### Integration with OpenWebUI

OpenWebUI supports two methods for connecting to the demo tools:

#### Option 1: MCP Protocol (Direct Connection)

The MCP server uses the official Model Context Protocol (MCP) Python library and provides tools via SSE (Server-Sent Events) transport, which is compatible with OpenWebUI's MCP integration.

**OpenWebUI Configuration:**

To connect OpenWebUI to the MCP server:

1. **Access OpenWebUI** at http://localhost:3000
2. **Navigate to** "Externe Werkzeuge" (External Tools) in the settings
3. **Click** "Verbindung hinzufügen" (Add Connection)
4. **Configure the connection** with the following settings:
   - **Type**: MCP - Streamables HTTP
   - **URL**: `http://mcp-server:8080` (from within Docker network)
     - Or `http://localhost:8080` (from host machine)
     - **Important**: Use base URL without `/sse` - OpenWebUI automatically appends the correct paths
   - **Authentication**: None (Keine)
   - **ID**: `demo-mcp-server` (or any unique identifier)
   - **Name**: `Demo MCP Server`
   - **Description**: `Demo MCP server with weather and user info tools`
   - **Visibility**: Public (Öffentlich)
5. **Save** the configuration

The MCP server will automatically expose two tools:
- `get_weather` - Returns weather data for San Francisco
- `get_user_info` - Returns demo user profile information

#### Option 2: OpenAPI/REST (Via Proxy)

The MCP to OpenAPI proxy exposes the same tools as standard REST endpoints with OpenAPI specification.

**OpenWebUI Configuration:**

To connect OpenWebUI to the OpenAPI proxy:

1. **Access OpenWebUI** at http://localhost:3000
2. **Navigate to** "Externe Werkzeuge" (External Tools) in the settings
3. **Click** "Verbindung hinzufügen" (Add Connection)
4. **Configure the connection** with the following settings:
   - **Type**: OpenAPI
   - **URL**: `http://mcp-proxy:8081/openapi.json` (from within Docker network)
     - Or `http://localhost:8081/openapi.json` (from host machine)
   - **Authentication**: None (Keine)
   - **ID**: `demo-openapi-proxy` (or any unique identifier)
   - **Name**: `Demo OpenAPI Proxy`
   - **Description**: `OpenAPI proxy for MCP server tools`
   - **Visibility**: Public (Öffentlich)
5. **Save** the configuration

The proxy will automatically expose the same two tools via REST API.

**Note:** Both methods provide access to the same tools. Use MCP protocol for direct integration with MCP-compliant clients, or use the OpenAPI proxy for standard REST API access. For detailed setup instructions, see [OPENWEBUI_CONFIGURATION.md](OPENWEBUI_CONFIGURATION.md).

### Direct API Access

#### MCP Protocol

The MCP server uses the official Model Context Protocol over SSE (Server-Sent Events) transport. While primarily designed for MCP clients like OpenWebUI, you can also interact with it using standard MCP client libraries.

**Testing the MCP Server:**

You can verify the server is running by checking the SSE endpoint:

```bash
# Test SSE endpoint (will keep connection open)
curl http://localhost:8080/sse -H "Accept: text/event-stream"
```

#### OpenAPI/REST

The OpenAPI proxy provides standard REST endpoints for the same tools.

**Testing the OpenAPI Proxy:**

```bash
# Get list of available tools
curl http://localhost:8081/tools

# Get OpenAPI specification
curl http://localhost:8081/openapi.json

# Call a tool
curl -X POST http://localhost:8081/tools/get_weather \
  -H "Content-Type: application/json" \
  -d '{"arguments": {}}'

# Access interactive API documentation
# Open in browser: http://localhost:8081/docs
```

**Available Tools:**
- `get_weather` - Returns current weather information for San Francisco
- `get_user_info` - Returns demo user profile information

To interact with the tools, use an MCP-compatible client, OpenWebUI's external tools feature, or make direct REST API calls to the proxy.

---

## Architecture

```
                   ┌─────────────────┐
                   │   OpenWebUI     │  http://localhost:3000
                   │  (Chat UI)      │  
                   └────────┬────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          │ Ollama API      │                 │ MCP/OpenAPI
          │                 │                 │
┌─────────▼─────────┐       │       ┌─────────▼─────────┐
│     Ollama        │       │       │   MCP Server      │  http://localhost:8080
│   (LLM Backend)   │       │       │  (FastMCP/SSE)    │
│                   │       │       │                   │
│ http://localhost: │       │       │  Endpoints:       │
│          11434    │       │       │  • GET /sse       │
│                   │       │       │  • POST /messages │
│ Model: llama3     │       │       │                   │
└───────────────────┘       │       │  Tools:           │
                            │       │  • get_weather    │
                            │       │  • get_user_info  │
                            │       │                   │
                            │       │  Prompts:         │
                            │       │  • analyze_weather    │
                            │       │  • review_user_profile│
                            │       │  • daily_briefing     │
                            │       └───────────┬───────┘
                            │                   │
                            │ OpenAPI/REST      │ MCP Protocol
                            │                   │
                  ┌─────────▼───────────────────▼─────────┐
                  │       MCP→OpenAPI Proxy               │  http://localhost:8081
                  │         (FastAPI)                     │
                  │                                       │
                  │  Endpoints:                           │
                  │  • GET  /tools      List tools        │
                  │  • POST /tools/{}   Call tool         │
                  │  • GET  /openapi    OpenAPI spec      │
                  │  • GET  /docs       API docs          │
                  └───────────────────────────────────────┘

Integration Options:
1. Chat with Ollama: OpenWebUI → Ollama (LLM responses with llama3 model)
2. Direct MCP: OpenWebUI → MCP Server (MCP protocol over SSE)
3. Via Proxy: OpenWebUI → OpenAPI Proxy → MCP Server (REST → MCP)
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

## MCP Prompts

The server also provides reusable prompt templates via the Model Context Protocol. These prompts help guide interactions with the tools:

### analyze_weather
Generates a prompt for analyzing the demo weather data and making recommendations.

**Prompt Name:** `analyze_weather`

**Parameters:** None

**Description:** Provides a structured template for analyzing the demo weather data (San Francisco) using the `get_weather` tool and making activity recommendations based on conditions.

### review_user_profile
Generates a prompt for reviewing and analyzing user profile information.

**Prompt Name:** `review_user_profile`

**Parameters:**
- `focus_area` (optional): What aspect to focus on - 'general', 'projects', 'skills', or 'preferences' (default: "general")

**Description:** Provides a template for reviewing user data using the `get_user_info` tool with different analysis focuses.

### daily_briefing
Generates a prompt for creating a comprehensive daily briefing.

**Prompt Name:** `daily_briefing`

**Parameters:** None

**Description:** Creates a daily briefing template that combines weather information and user context from both tools to provide a complete start-of-day summary.

**Note:** Prompts are accessible through MCP-compatible clients that support the prompts feature. They provide pre-structured guidance for using the server's tools effectively.

---

## Files Structure

```
.
├── docker-compose.yml          # Defines the 4 services (Ollama, OpenWebUI, MCP Server, MCP Proxy)
├── Dockerfile.ollama           # Dockerfile for Ollama with llama3 model
├── ollama-entrypoint.sh        # Entrypoint script to pull llama3 model
├── Dockerfile.mcp              # Dockerfile for MCP server
├── Dockerfile.proxy            # Dockerfile for OpenAPI proxy
├── mcp_server.py               # MCP server using official mcp library v1.7.1
├── mcp_openapi_proxy.py        # MCP to OpenAPI proxy server
├── requirements.txt            # Python dependencies for MCP server
├── requirements-proxy.txt      # Python dependencies for proxy
├── README.md                   # This file
├── QUICKSTART.md               # Quick start guide
├── OPENWEBUI_CONFIGURATION.md  # Detailed OpenWebUI setup guide
└── .env.example                # Environment variables example
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

### Adding More Prompts

To add more prompts to the MCP server:

1. Edit `mcp_server.py`
2. Add a new function decorated with `@mcp.prompt()`:
   ```python
   @mcp.prompt()
   def your_prompt_name(param1: str = "default"):
       """Description of what your prompt does"""
       return [
           {
               "role": "user",
               "content": {
                   "type": "text",
                   "text": f"Your prompt text using {param1}"
               }
           }
       ]
   ```
3. Rebuild and restart: `docker compose up --build`

The prompt will automatically be available to MCP clients that support prompts.

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

**Verify MCP endpoint configuration:**
```bash
# Run the automated test script
python3 test_mcp_connection.py
```
This will verify that:
- GET /sse endpoint works (SSE stream)
- POST /messages endpoint exists (client messages)
- POST /sse correctly returns 405 (not the right endpoint)

**OpenWebUI not loading:**
```bash
docker compose logs openwebui
```

**Connection Issues:**

If you see `POST /sse HTTP/1.1" 404` or `405` errors in logs, this means:
- The URL in OpenWebUI is incorrectly configured with `/sse` suffix
- **Solution**: Remove `/sse` from the URL in OpenWebUI settings
- Use `http://mcp-server:8080` (base URL only)
- OpenWebUI will automatically append the correct paths

---

## Learn More

- [OpenWebUI Documentation](https://github.com/open-webui/open-webui)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
