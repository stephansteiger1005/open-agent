#!/usr/bin/env python3
"""
Simple MCP Server with two constant data tools for demo purposes.
"""
import asyncio
import json
from typing import Any, Dict

# Install mcp if needed: pip install mcp
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("Error: mcp package not found. Install with: pip install mcp")
    exit(1)


# Constant data for tools
WEATHER_DATA = {
    "location": "San Francisco, CA",
    "temperature": 72,
    "unit": "fahrenheit",
    "conditions": "Sunny",
    "humidity": 65,
    "wind_speed": 8,
    "wind_direction": "NW",
    "forecast": [
        {"day": "Today", "high": 75, "low": 58, "conditions": "Sunny"},
        {"day": "Tomorrow", "high": 73, "low": 56, "conditions": "Partly Cloudy"},
        {"day": "Friday", "high": 70, "low": 54, "conditions": "Cloudy"}
    ]
}

USER_INFO_DATA = {
    "id": "user-12345",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "role": "Developer",
    "department": "Engineering",
    "location": "San Francisco",
    "joined_date": "2020-01-15",
    "status": "active",
    "projects": [
        {"id": "proj-1", "name": "MCP Demo", "role": "Lead Developer"},
        {"id": "proj-2", "name": "OpenWebUI Integration", "role": "Contributor"}
    ],
    "skills": ["Python", "JavaScript", "Docker", "FastAPI"],
    "preferences": {
        "theme": "dark",
        "notifications": True,
        "language": "en-US"
    }
}


# Create MCP server instance
app = Server("demo-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_weather",
            description="Get current weather information for San Francisco. Returns constant demo data including temperature, conditions, and 3-day forecast.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="get_user_info",
            description="Get information about the current user. Returns constant demo data including profile, projects, and preferences.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "get_weather":
        return [
            TextContent(
                type="text",
                text=json.dumps(WEATHER_DATA, indent=2)
            )
        ]
    elif name == "get_user_info":
        return [
            TextContent(
                type="text",
                text=json.dumps(USER_INFO_DATA, indent=2)
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
