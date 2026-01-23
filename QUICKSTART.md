# Quick Start Guide

Get up and running with the OpenWebUI MCP demo in 3 simple steps!

## Prerequisites

- Docker installed
- Docker Compose installed

## Step 1: Start the Services

```bash
docker-compose up --build
```

This will:
- Build the MCP server with 2 demo tools
- Pull and start OpenWebUI
- Configure everything automatically

## Step 2: Open OpenWebUI

Open your browser and navigate to:
```
http://localhost:3000
```

No login required - the demo runs in open mode!

## Step 3: Try the MCP Tools

In the OpenWebUI chat:

1. **Ask about the weather:**
   ```
   What's the weather like?
   ```
   The `get_weather` tool will return San Francisco weather data.

2. **Ask about user info:**
   ```
   Who am I? Show me my profile.
   ```
   The `get_user_info` tool will return demo user information.

## That's It!

You now have a working OpenWebUI instance with MCP tools integration.

## Stopping the Demo

Press `Ctrl+C` in the terminal, then:
```bash
docker-compose down
```

## Next Steps

Want to add more tools? Edit `mcp_server.py` and add your own tool implementations!
