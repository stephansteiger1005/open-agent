# Quick Start Guide

Get up and running with the OpenWebUI MCP demo in 3 simple steps!

## Prerequisites

- Docker installed
- Docker Compose installed

## Step 1: Start the Services

```bash
cp .env.example .env
```

Open .env and insert your `OPENAI_API_KEY=`

```bash
docker compose up --build
```

This will:
- Build and start the MCP server using fastmcp
- Build and start MCP_Viewing
- Pull and start OpenAPI-proxy (preconfigured for MCP server and MCP_Viewing)
- Pull and start OpenWebUI

## Step 2: Access the Services

### OpenWebUI (Chat Interface)
Open your browser and navigate to:
```
http://localhost:3000
```

No login required - the demo runs in open mode!


### MCP Server (Tool Server)
The OpenAPI proxy server is available at:
```
http://localhost:8080/docs
```

**For OpenWebUI configuration**, use the base URL above (without `/mcp`).

The server provides the MCP protocol endpoint at `/mcp`.

OpenWebUI automatically appends the correct paths.

## Step 3: Configure OpenWebUI to Use MCP Tools

See ./OPENWEBUI_CONFIGURATION.md