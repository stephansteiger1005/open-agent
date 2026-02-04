# OpenWebUI Configuration Guide

This guide explains how to configure OpenWebUI to connect to the MCP tools using the MCP protocol.

## Prerequisites

- Docker Compose services running: `docker compose up -d`
- OpenWebUI accessible at http://localhost:3000
- MCPO running at http://localhost:8080

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
| **Type** | OpenAPI | Select this from the dropdown |
| **URL** | `http://host.docker.internal:8000` | Base URL for MCP server (Docker network) |
| **Authentication** | None (Keine) | No authentication required |
| **ID** | `demo-mcp-server` | Unique identifier for this connection |
| **Name** | `Demo MCP Server` | Display name |
| **Description** | `Demo MCP server with weather and user info tools` | Brief description |
| **Visibility** | Public (Öffentlich) | Make tools available to all users |

#### 4. Save Configuration

Click **"Speichern"** (Save) to save the connection.

#### 5. Verify Connection

After saving, you should see the MCP server connection listed in your external tools. The connection status should show as active/connected.

---

---

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

## Technical Details

### MCP Protocol

The MCP server uses:
- **Protocol:** Model Context Protocol (MCP)
- **Transport:** HTTP
- **Endpoint:** `/mcp`
- **Library:** FastMCP (Python library for MCP)
- **Note:** Configure clients with base URL only; the client automatically appends the correct endpoint paths
