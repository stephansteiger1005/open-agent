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


@mcp.prompt()
def analyze_weather():
    """Analyze the demo weather data.
    
    Provides a prompt template for analyzing the demo weather data
    (San Francisco) and making recommendations based on the conditions.
    """
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": """Please analyze the demo weather conditions.

Use the get_weather tool to retrieve the weather data, then provide:
1. A summary of current conditions
2. Analysis of the 3-day forecast
3. Recommendations for outdoor activities
4. Any weather alerts or notable conditions

Please format your response in a clear, easy-to-read manner."""
            }
        }
    ]


@mcp.prompt()
def review_user_profile(focus_area: str = "general"):
    """Review and analyze a user's profile information.
    
    Provides a prompt template for reviewing user profile data with
    different focus areas.
    
    Args:
        focus_area: What aspect to focus on - 'general', 'projects', 'skills', or 'preferences'
    """
    focus_instructions = {
        "general": "Provide a comprehensive overview of the user's profile",
        "projects": "Focus on the user's project involvement and contributions",
        "skills": "Analyze the user's skill set and expertise areas",
        "preferences": "Review the user's preferences and settings"
    }
    
    instruction = focus_instructions.get(focus_area, focus_instructions["general"])
    
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""Please review the user profile using the get_user_info tool.

Focus: {instruction}

Provide insights on:
1. Key information about the user
2. Notable aspects based on the focus area
3. Suggestions or observations
4. Any areas that might need attention

Please present your analysis in a structured format."""
            }
        }
    ]


@mcp.prompt()
def daily_briefing():
    """Generate a daily briefing combining weather and user context.
    
    Provides a prompt template for creating a comprehensive daily briefing
    that includes both weather information and user profile context.
    """
    return [
        {
            "role": "user",
            "content": {
                "type": "text",
                "text": """Please create a daily briefing by using both the get_weather and get_user_info tools.

Your briefing should include:
1. Current weather conditions and forecast
2. User context (name, role, current projects)
3. Recommendations for the day based on weather and user's work
4. Any notable items that might affect the user's day

Format the briefing in a friendly, professional manner suitable for starting the day."""
            }
        }
    ]


if __name__ == "__main__":
    # Run the MCP server with SSE transport
    # The server will be accessible at http://0.0.0.0:8080
    import uvicorn
    
    # Get the ASGI app for SSE transport
    # sse_app() returns a Starlette ASGI application configured for MCP over SSE
    app = mcp.sse_app()
    
    # Run with uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
