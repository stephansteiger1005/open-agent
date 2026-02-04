#!/usr/bin/env python3
"""
MCP Server using the official Model Context Protocol Python library.
This server provides three demo tools that can be used by OpenWebUI and other MCP clients.
"""
import json
from fastmcp import FastMCP
from datetime import datetime

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

PART_INFO_DB = {
    "A1234567890":{
        "partnumber":"A1234567890",
        "j0_Nomenclature": "EB Testzeug",
        "j0_Nomenclature_EN": "EB testing stuff",
        "j0_Creator": "ststeig"
    },
    "A0123456789":{
        "partnumber":"A0123456789",
        "j0_Nomenclature": "EB HGH-Testzeug",
        "j0_Nomenclature_EN": "EB hgh testing stuff",
        "j0_Creator": "hghoehne"
    },
    "unknown":{
        "partnumber":"unknown",
        "j0_Nomenclature": "Unknown Part",
        "j0_Nomenclature_EN": "Unknown Part",
        "j0_Creator": "unknown"
    }
}

@mcp.tool()
def get_part_info(partnumber: str) -> str:
    """Get information on a given partnumber.
    
    Args:
        partnumber: The partnumber to get information on
    
    Returns information on the given partnumber.
    """
    # Return weather data with the requested location as JSON string
    result = PART_INFO_DB.get(partnumber, PART_INFO_DB["unknown"])
    return json.dumps(result, indent=2)

@mcp.tool()
def get_weather(location: str = "San Francisco, CA") -> str:
    """Get current weather information for a location.
    
    Args:
        location: The location to get weather for (default: "San Francisco, CA")
    
    Returns constant demo data including temperature, conditions, humidity,
    wind information, and a 3-day forecast.
    """
    # Return weather data with the requested location as JSON string
    result = {**WEATHER_DATA, "location": location}
    return json.dumps(result, indent=2)

@mcp.tool()
def get_time() -> str:
    """Get current time information.
    
    Returns system time and timezone information.
    """
    # Return system time and timezone information as JSON string
    now = datetime.now().astimezone()
    data = {
        "time": now.isoformat(),
        "timezone": str(now.tzinfo)
    }
    return json.dumps(data, indent=2)


@mcp.tool()
def get_user_info(user_id: str = "user-12345") -> str:
    """Get information about a specific user.
    
    Args:
        user_id: The user ID to get information for (default: "user-12345")
    
    Returns constant demo data including user profile, projects, skills,
    and preferences.
    """
    # Return user info data with the requested user_id as JSON string
    result = {**USER_INFO_DATA, "id": user_id}
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    # Run the MCP server with SSE transport
    # The server will be accessible at http://0.0.0.0:8080
    #import uvicorn
    
    # Get the ASGI app for SSE transport
    mcp.run(transport="http", host="0.0.0.0", port=8080, path="/mcp")
