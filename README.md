# Quick Start Guide

Get up and running with the OpenWebUI MCP demo in 3 simple steps!

## Prerequisites

- Docker installed
- Docker Compose installed

## Step 1: Prepare submodule(s)

MCP_Viewing is needed under ./MCP_Viewing

Use this if you have access to the  https://github.com/iau4u/MCP_Viewing directly
```bash
git submodule add https://github.com/iau4u/MCP_Viewing ./MCP_Viewing
```

Use this if you can only access it with an api-key
```bash
git clone https://oauth2:<your-api-key>@github.com/iau4u/MCP_Viewing.git
```

## Step 2: Start the Services

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

## Step 3: Access the Services

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