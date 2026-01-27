# OpenWebUI Configuration Guide

This guide explains how to configure OpenWebUI to connect to the MCP tools using the MCP protocol.

## Prerequisites

- Docker Compose services running: `docker compose up -d`
- OpenWebUI accessible at http://localhost:3000
- Ollama with llama3 model running at http://localhost:11434 (automatically configured)
- MCP Server running at http://localhost:8080

**Note:** Ollama with llama3 model is automatically configured in OpenWebUI through the `OLLAMA_BASE_URL` environment variable. You can start chatting immediately without additional configuration.

## Integration Options

### Built-in: Ollama with llama3 Model

OpenWebUI is automatically configured to use Ollama with the llama3 model through the `OLLAMA_BASE_URL` environment variable. No additional configuration is needed - you can start chatting immediately!

### MCP Server Connection

Connect directly to the MCP server using the MCP protocol over HTTP.

---

## MCP Server Connection

### Step-by-Step Configuration

#### 1. Access OpenWebUI Settings

1. Open your browser and navigate to http://localhost:3000
2. Click on the user icon or settings icon in the interface
3. Navigate to **"Externe Werkzeuge"** (External Tools) or **"External Tools"** section

#### 2. Add MCP Server Connection

Click on **"Verbindung hinzufügen"** (Add Connection) or **"Add Connection"** button.

#### 3. Configure Connection Settings

Fill in the following fields:

| Field | Value | Description |
|-------|-------|-------------|
| **Type** | MCP - Streamables HTTP | Select this from the dropdown |
| **URL** | `http://mcp-server:8080` | Base URL for MCP server (Docker network) |
| **Authentication** | None (Keine) | No authentication required |
| **ID** | `demo-mcp-server` | Unique identifier for this connection |
| **Name** | `Demo MCP Server` | Display name |
| **Description** | `Demo MCP server with weather and user info tools` | Brief description |
| **Visibility** | Public (Öffentlich) | Make tools available to all users |

**Important Notes:**
- Use `http://mcp-server:8080` when connecting from within the Docker network
- Use `http://localhost:8080` when connecting from your host machine
- Do NOT include `/sse` in the URL - OpenWebUI will automatically append the correct paths (`/sse` for SSE stream, `/messages` for client messages)

#### 4. Save Configuration

Click **"Speichern"** (Save) to save the connection.

#### 5. Verify Connection

After saving, you should see the MCP server connection listed in your external tools. The connection status should show as active/connected.

---

---

## Available Tools

Once configured, the following tools will be available in your OpenWebUI chats:

### 1. get_weather

**Description:** Get current weather information for a specified location

**Parameters:**
- `location` (optional): The location to get weather for (default: "San Francisco, CA")

**Returns:** Weather data including:
- Current temperature and conditions
- Humidity levels
- Wind speed and direction
- 3-day forecast

**Example Usage:**
```
"Can you get the current weather for me?"
"What's the weather like in New York?"
"Get weather for Paris, France"
```

### 2. get_user_info

**Description:** Get information about a specific user

**Parameters:**
- `user_id` (optional): The user ID to get information for (default: "user-12345")

**Returns:** User profile data including:
- User ID, name, and email
- Role and department
- Associated projects
- Skills and preferences

**Example Usage:**
```
"Show me my user profile information"
```

### 3. get_time

**Description:** Get current system time and timezone information

**Parameters:** None

**Returns:** Current time including:
- ISO 8601 formatted timestamp
- Timezone information

**Example Usage:**
```
"What time is it?"
"Can you get the current time?"
```

## Using Tools in Conversations

Once the MCP server is configured:

1. Start a new chat in OpenWebUI
2. Ask the AI to use one of the available tools
3. The AI will automatically call the appropriate MCP tool
4. Results will be displayed in the conversation

**Example Conversation:**
```
User: "What's the weather like?"
AI: [Uses get_weather tool]
AI: "Based on the weather data, it's currently 72°F and sunny in San Francisco..."
```

## Troubleshooting

### Connection Failed

If the connection fails:

1. **Check Service Status:**
   ```bash
   # Check MCP server
   docker ps --filter "name=demo-mcp-server"
   ```

2. **View Logs:**
   ```bash
   # MCP server logs
   docker logs demo-mcp-server
   ```

3. **Test Endpoint:**
   ```bash
   # Test MCP server
   curl http://localhost:8080/mcp
   ```

### Tools Not Appearing

If tools don't appear in OpenWebUI:

1. Verify the connection is saved and active
2. Refresh the OpenWebUI page
3. Check that visibility is set to "Public"
4. Verify the URL is correct: `http://mcp-server:8080` (without `/mcp`)

### Authentication Errors

The demo server has **no authentication**. Ensure:
- Authentication is set to "None" (Keine)
- No headers or API keys are configured

## Technical Details

### MCP Protocol

The MCP server uses:
- **Protocol:** Model Context Protocol (MCP)
- **Transport:** HTTP
- **Endpoint:** `/mcp`
- **Library:** FastMCP (Python library for MCP)
- **Note:** Configure clients with base URL only; the client automatically appends the correct endpoint paths

### Network Configuration

Within Docker Compose:
- Ollama: `ollama:11434`
- MCP Server: `mcp-server:8080`
- OpenWebUI: `openwebui:8080`
- All services are on the same Docker network

From host machine:
- Ollama: `localhost:11434`
- MCP Server: `localhost:8080`
- OpenWebUI: `localhost:3000`

## Advanced Configuration

### Adding Custom Headers

If you need to add custom headers (for authentication in production):

1. In the OpenWebUI connection settings, find the "Header" field
2. Add headers in JSON format:
   ```json
   {
     "Authorization": "Bearer your-token-here",
     "X-Custom-Header": "value"
   }
   ```

### Environment Variables

The MCP server can be configured via environment variables in `docker-compose.yml`:

```yaml
mcp-server:
  environment:
    - MCP_SERVER_HOST=0.0.0.0
    - MCP_SERVER_PORT=8080
```

The Ollama instance can be configured similarly:

```yaml
ollama:
  environment:
    - OLLAMA_HOST=0.0.0.0:11434
```

## Security Considerations

**⚠️ Important:** This demo configuration has no authentication and is intended for development/testing only.

For production use:
1. Enable authentication on the MCP server
2. Use HTTPS/TLS encryption
3. Implement proper access controls
4. Use secure credential management
5. Restrict network access appropriately

## Additional Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [OpenWebUI Documentation](https://github.com/open-webui/open-webui)
- [MCP Python SDK](https://pypi.org/project/mcp/)

## Support

For issues or questions:
1. Check the [README.md](README.md) for general information
2. Review the [QUICKSTART.md](QUICKSTART.md) for setup instructions
3. View Docker logs: `docker compose logs`
