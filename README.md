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

### From OpenWebUI

OpenWebUI can access the tools through its interface. The tools are exposed via the MCP server at `http://mcp-server:8080` (internal to Docker network).

**Note:** OpenWebUI's MCP integration depends on the specific version and configuration. The tools are accessible via the REST API documented below.

### Direct API Access

You can test the tools directly using curl:

**Get Weather Data:**
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_weather"}'
```

**Get User Info:**
```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_user_info"}'
```

**List Available Tools:**
```bash
curl http://localhost:8080/tools
```

---

## Architecture

```
┌─────────────────┐
│   OpenWebUI     │  http://localhost:3000
│  (Chat UI)      │  
└────────┬────────┘
         │
         │ HTTP API
         │
┌────────▼────────┐
│   MCP Server    │  http://localhost:8080
│   (FastAPI)     │
│                 │
│  • get_weather  │  Returns demo weather data
│  • get_user_info│  Returns demo user data
└─────────────────┘
```

---

## MCP Tools

### get_weather
Returns current weather information for San Francisco.

**Endpoint:** `POST /execute`

**Request:**
```json
{
  "tool": "get_weather"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "location": "San Francisco, CA",
    "temperature": 72,
    "unit": "fahrenheit",
    "conditions": "Sunny",
    "humidity": 65,
    "wind_speed": 8,
    "wind_direction": "NW",
    "forecast": [
      {
        "day": "Today",
        "high": 75,
        "low": 58,
        "conditions": "Sunny"
      }
    ]
  }
}
```

### get_user_info
Returns information about a demo user.

**Endpoint:** `POST /execute`

**Request:**
```json
{
  "tool": "get_user_info"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "id": "user-12345",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "Developer",
    "department": "Engineering",
    "projects": [
      {
        "id": "proj-1",
        "name": "MCP Demo",
        "role": "Lead Developer"
      }
    ],
    "skills": ["Python", "JavaScript", "Docker", "FastAPI"]
  }
}
```

---

## Files Structure

```
.
├── docker-compose.yml      # Defines the 2 services
├── Dockerfile.mcp          # Dockerfile for MCP server
├── mcp_server.py           # Simple MCP server implementation (FastAPI)
├── README.md               # This file
├── QUICKSTART.md           # Quick start guide
├── .env.example            # Environment variables example
└── requirements.txt        # Python dependencies (for reference)
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
3. Add tool definition in `list_tools()` function:
   ```python
   {
       "name": "your_tool_name",
       "description": "Description of what your tool does",
       "parameters": {}
   }
   ```
4. Add tool implementation in `execute_tool()` function:
   ```python
   elif request.tool == "your_tool_name":
       return ToolResponse(
           success=True,
           result=YOUR_TOOL_DATA
       )
   ```
5. Rebuild and restart: `docker compose up --build`

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
curl http://localhost:8080/health
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
