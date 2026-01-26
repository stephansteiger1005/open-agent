#!/usr/bin/env python3
"""
MCP to OpenAPI Proxy Server

This proxy server connects to an MCP server and exposes its tools as OpenAPI/REST endpoints.
This allows OpenWebUI and other clients to use MCP tools via standard REST API calls.
"""
import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolCallRequest(BaseModel):
    """Request model for tool calls"""
    arguments: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tool arguments")


class ToolCallResponse(BaseModel):
    """Response model for tool calls"""
    content: List[Dict[str, Any]]


class MCPClient:
    """Client for communicating with MCP server over SSE"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.sse_url = f"{self.base_url}/sse"
        self.messages_url = f"{self.base_url}/messages"
        self.tools = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        self._initialized = False
    
    async def initialize(self):
        """Initialize connection and fetch available tools"""
        if self._initialized:
            return
        
        try:
            logger.info(f"Connecting to MCP server at {self.base_url}")
            
            # Send initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "mcp-openapi-proxy",
                        "version": "1.0.0"
                    }
                }
            }
            
            response = await self.client.post(self.messages_url, json=init_request)
            response.raise_for_status()
            init_result = response.json()
            
            logger.info(f"MCP server initialized: {init_result}")
            
            # Send initialized notification
            initialized_notification = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            await self.client.post(self.messages_url, json=initialized_notification)
            
            # List available tools
            list_tools_request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await self.client.post(self.messages_url, json=list_tools_request)
            response.raise_for_status()
            tools_result = response.json()
            
            if "result" in tools_result and "tools" in tools_result["result"]:
                for tool in tools_result["result"]["tools"]:
                    tool_name = tool.get("name")
                    self.tools[tool_name] = tool
                    logger.info(f"Discovered tool: {tool_name}")
            
            self._initialized = True
            logger.info(f"MCP client initialized with {len(self.tools)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}")
            raise
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        if not self._initialized:
            await self.initialize()
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Send tool call request
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            response = await self.client.post(self.messages_url, json=call_request)
            response.raise_for_status()
            result = response.json()
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return result.get("result", {})
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling tool {tool_name}: {e}")
            raise HTTPException(status_code=502, detail=f"Error communicating with MCP server: {str(e)}")
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_tools(self) -> Dict[str, Any]:
        """Get list of available tools"""
        if not self._initialized:
            await self.initialize()
        return self.tools
    
    async def close(self):
        """Close the client connection"""
        await self.client.aclose()


# Global MCP client instance
mcp_client: Optional[MCPClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    global mcp_client
    
    # Startup
    mcp_url = "http://mcp-server:8080"
    logger.info(f"Starting MCP OpenAPI proxy, connecting to {mcp_url}")
    mcp_client = MCPClient(mcp_url)
    
    try:
        await mcp_client.initialize()
        logger.info("MCP client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP client: {e}")
        # Continue anyway, will retry on first request
    
    yield
    
    # Shutdown
    if mcp_client:
        await mcp_client.close()
        logger.info("MCP client closed")


# Create FastAPI app
app = FastAPI(
    title="MCP to OpenAPI Proxy",
    description="Proxy server that exposes MCP tools as OpenAPI/REST endpoints",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "MCP to OpenAPI Proxy",
        "version": "1.0.0",
        "description": "Exposes MCP tools as OpenAPI endpoints",
        "endpoints": {
            "tools": "/tools",
            "openapi": "/openapi.json",
            "docs": "/docs"
        }
    }


@app.get("/tools")
async def list_tools():
    """List all available tools from the MCP server"""
    try:
        tools = await mcp_client.get_tools()
        return {
            "tools": [
                {
                    "name": name,
                    "description": tool.get("description", ""),
                    "inputSchema": tool.get("inputSchema", {}),
                    "endpoint": f"/tools/{name}"
                }
                for name, tool in tools.items()
            ]
        }
    except Exception as e:
        logger.error(f"Error listing tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools/{tool_name}")
async def call_tool(tool_name: str, request: ToolCallRequest):
    """Call a specific tool"""
    try:
        result = await mcp_client.call_tool(tool_name, request.arguments)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        tools = await mcp_client.get_tools()
        return {
            "status": "healthy",
            "mcp_connected": True,
            "tools_count": len(tools)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "mcp_connected": False,
            "error": str(e)
        }


# Generate dynamic OpenAPI schema that includes tool endpoints
@app.get("/openapi.json")
async def get_openapi_schema():
    """
    Generate OpenAPI schema dynamically based on available MCP tools.
    This endpoint can be used by OpenWebUI to discover available tools.
    """
    try:
        tools = await mcp_client.get_tools()
        
        # Base OpenAPI schema
        openapi_schema = {
            "openapi": "3.1.0",
            "info": {
                "title": "MCP Tools API",
                "description": "OpenAPI proxy for MCP server tools",
                "version": "1.0.0"
            },
            "servers": [
                {
                    "url": "http://localhost:8081",
                    "description": "MCP OpenAPI Proxy Server"
                }
            ],
            "paths": {}
        }
        
        # Add tool endpoints to schema
        for tool_name, tool_info in tools.items():
            path = f"/tools/{tool_name}"
            
            # Extract schema information
            input_schema = tool_info.get("inputSchema", {})
            properties = input_schema.get("properties", {})
            required = input_schema.get("required", [])
            
            # Build request body schema
            request_body = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "arguments": {
                                    "type": "object",
                                    "properties": properties,
                                    "required": required
                                }
                            }
                        }
                    }
                }
            }
            
            openapi_schema["paths"][path] = {
                "post": {
                    "summary": tool_info.get("description", f"Call {tool_name} tool"),
                    "description": tool_info.get("description", ""),
                    "operationId": f"call_{tool_name}",
                    "requestBody": request_body,
                    "responses": {
                        "200": {
                            "description": "Successful response",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "content": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object"
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        "404": {
                            "description": "Tool not found"
                        },
                        "500": {
                            "description": "Server error"
                        }
                    }
                }
            }
        
        return openapi_schema
    
    except Exception as e:
        logger.error(f"Error generating OpenAPI schema: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info"
    )
