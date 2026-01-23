#!/usr/bin/env python3
"""
Simple MCP-style tool server with two constant data tools for demo purposes.
This provides a REST API that OpenWebUI can call.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import uvicorn

app = FastAPI(title="Demo MCP Tool Server")


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


class ToolRequest(BaseModel):
    tool: str
    arguments: Dict[str, Any] = {}


class ToolResponse(BaseModel):
    success: bool
    result: Any


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "Demo MCP Tool Server",
        "version": "1.0.0",
        "tools": ["get_weather", "get_user_info"]
    }


@app.get("/tools")
async def list_tools():
    """List all available tools."""
    return {
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather information for San Francisco. Returns constant demo data including temperature, conditions, and 3-day forecast.",
                "parameters": {}
            },
            {
                "name": "get_user_info",
                "description": "Get information about the current user. Returns constant demo data including profile, projects, and preferences.",
                "parameters": {}
            }
        ]
    }


@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a tool and return its result."""
    if request.tool == "get_weather":
        return ToolResponse(
            success=True,
            result=WEATHER_DATA
        )
    elif request.tool == "get_user_info":
        return ToolResponse(
            success=True,
            result=USER_INFO_DATA
        )
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown tool: {request.tool}"
        )


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
