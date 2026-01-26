#!/usr/bin/env python3
"""
MCP to OpenAPI Proxy Server

This proxy server connects to an MCP server and exposes its tools as OpenAPI/REST endpoints.
This allows OpenWebUI and other clients to use MCP tools via standard REST API calls.

This is a production-ready implementation using the official MCP Python SDK.
"""
import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from mcp import ClientSession
from mcp.client import sse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolCallRequest(BaseModel):
    """Request model for tool calls"""
    arguments: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Tool arguments")


class ToolCallResponse(BaseModel):
    """Response model for tool calls"""
    content: List[Dict[str, Any]]


class ProductionMCPClient:
    """
    Production-ready MCP client that connects to an MCP server via SSE transport.
    Uses the official MCP Python SDK for full protocol support.
    """
    
    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url
        self.tools = {}
        self._initialized = False
        self._session: Optional[ClientSession] = None
        self._connection_task = None
    
    async def initialize(self):
        """Initialize connection to MCP server and fetch available tools"""
        if self._initialized:
            return
        
        try:
            logger.info(f"Connecting to MCP server at {self.mcp_server_url}")
            
            # Construct SSE endpoint URL
            sse_url = f"{self.mcp_server_url}/sse"
            
            # Start the connection in a background task
            self._connection_task = asyncio.create_task(self._maintain_connection(sse_url))
            
            # Wait for initialization to complete with a timeout
            max_wait = 30  # seconds
            for _ in range(max_wait * 10):
                if self._initialized:
                    break
                await asyncio.sleep(0.1)
            else:
                raise TimeoutError("Failed to initialize MCP connection within 30 seconds")
            
            logger.info(f"MCP client initialized with {len(self.tools)} tools: {list(self.tools.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP client: {e}", exc_info=True)
            await self.cleanup()
            raise
    
    async def _maintain_connection(self, sse_url: str):
        """Maintain persistent connection to MCP server"""
        try:
            # Create SSE client connection using proper async context manager
            async with sse.sse_client(sse_url) as (read_stream, write_stream):
                # Create MCP client session using proper async context manager
                async with ClientSession(read_stream, write_stream) as session:
                    self._session = session
                    
                    # Initialize the MCP session
                    init_result = await session.initialize()
                    logger.info(f"Connected to MCP server: {init_result.serverInfo.name}")
                    logger.info(f"Protocol version: {init_result.protocolVersion}")
                    
                    # Fetch available tools from the server
                    tools_result = await session.list_tools()
                    
                    # Store tools in a dictionary for easy lookup
                    for tool in tools_result.tools:
                        self.tools[tool.name] = {
                            "name": tool.name,
                            "description": tool.description or "",
                            "inputSchema": tool.inputSchema or {"type": "object", "properties": {}}
                        }
                    
                    self._initialized = True
                    
                    # Keep the connection alive - this will block until cleanup is called
                    # The session stays open as long as we're in this async with block
                    await asyncio.Event().wait()  # Wait indefinitely
                    
        except asyncio.CancelledError:
            logger.info("MCP connection task cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in MCP connection: {e}", exc_info=True)
            raise
        finally:
            self._session = None
            self._initialized = False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a tool on the MCP server and return its result.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            Dict with 'content' key containing list of content items
        """
        if not self._initialized:
            await self.initialize()
        
        if tool_name not in self.tools:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        if not self._session:
            raise RuntimeError("MCP session is not connected")
        
        try:
            logger.info(f"Calling tool '{tool_name}' with arguments: {arguments}")
            
            # Call the tool via MCP protocol
            result = await self._session.call_tool(tool_name, arguments)
            
            # Convert MCP result to our response format
            content = []
            for item in result.content:
                content_item = {
                    "type": item.type
                }
                # Add text if it's a text content
                if hasattr(item, 'text'):
                    content_item["text"] = item.text
                # Add other attributes as needed
                if hasattr(item, 'annotations') and item.annotations:
                    content_item["annotations"] = item.annotations
                    
                content.append(content_item)
            
            return {"content": content}
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_tools(self) -> Dict[str, Any]:
        """Get list of available tools"""
        if not self._initialized:
            await self.initialize()
        return self.tools
    
    async def cleanup(self):
        """Clean up MCP client resources"""
        try:
            if self._connection_task:
                self._connection_task.cancel()
                try:
                    await self._connection_task
                except asyncio.CancelledError:
                    pass
                self._connection_task = None
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        self._initialized = False


# Global MCP client instance
mcp_client: Optional[ProductionMCPClient] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI"""
    global mcp_client
    
    # Startup
    logger.info("Starting MCP OpenAPI proxy")
    
    # Get MCP server URL from environment or use default
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:8080")
    logger.info(f"MCP server URL: {mcp_server_url}")
    
    mcp_client = ProductionMCPClient(mcp_server_url)
    
    try:
        await mcp_client.initialize()
        logger.info("MCP client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP client: {e}")
        # Continue anyway, will retry on first request
    
    yield
    
    # Shutdown
    logger.info("Shutting down MCP OpenAPI proxy")
    if mcp_client:
        await mcp_client.cleanup()


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
