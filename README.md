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
   docker-compose up --build
   ```

2. **Access OpenWebUI:**
   - Open your browser to http://localhost:3000
   - No authentication required (demo mode)

3. **Use the MCP Tools:**
   - The two tools are automatically available in OpenWebUI
   - Try asking about weather or user information
   - The tools return constant JSON data for demonstration

---

## Architecture

```
┌─────────────────┐
│   OpenWebUI     │  http://localhost:3000
│  (Chat UI)      │  
└────────┬────────┘
         │
         │ MCP Protocol
         │
┌────────▼────────┐
│   MCP Server    │
│                 │
│  • get_weather  │  Returns demo weather data
│  • get_user_info│  Returns demo user data
└─────────────────┘
```

---

## MCP Tools

### get_weather
Returns current weather information for San Francisco.

Example response:
```json
{
  "location": "San Francisco, CA",
  "temperature": 72,
  "conditions": "Sunny",
  "humidity": 65,
  "forecast": [...]
}
```

### get_user_info
Returns information about a demo user.

Example response:
```json
{
  "id": "user-12345",
  "name": "John Doe",
  "email": "john.doe@example.com",
  "role": "Developer",
  "projects": [...]
}
```

---

## Files Structure

- `docker-compose.yml` - Defines the 2 services
- `mcp_server.py` - Simple MCP server implementation
- `Dockerfile.mcp` - Dockerfile for MCP server
- `README.md` - This file

---

## Stopping the Demo

```bash
docker-compose down
```

To also remove volumes:
```bash
docker-compose down -v
```

---

## Extending the Demo

To add more tools to the MCP server:

1. Edit `mcp_server.py`
2. Add your tool definition in `list_tools()`
3. Implement the tool logic in `call_tool()`
4. Rebuild: `docker-compose up --build`

---

## Requirements

- Docker
- Docker Compose

No other dependencies needed - everything runs in containers!
