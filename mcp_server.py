#!/usr/bin/env python3
"""
MCP Server using the official Model Context Protocol Python library.
This server provides two demo tools that can be used by OpenWebUI and other MCP clients.
"""
import json
from mcp.server.fastmcp import FastMCP

# Create MCP server with no authentication
mcp = FastMCP("Demo MCP Server")

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


@mcp.tool()
def get_weather() -> str:
    """Get current weather information for San Francisco.
    
    Returns constant demo data including temperature, conditions, humidity,
    wind information, and a 3-day forecast.
    """
    return json.dumps(WEATHER_DATA, indent=2)


@mcp.tool()
def get_user_info() -> str:
    """Get information about the current user.
    
    Returns constant demo data including user profile, projects, skills,
    and preferences.
    """
    return json.dumps(USER_INFO_DATA, indent=2)


if __name__ == "__main__":
    # Run the MCP server with SSE transport
    # The server will be accessible at http://0.0.0.0:8080
    mcp.run(transport="sse", host="0.0.0.0", port=8080)
