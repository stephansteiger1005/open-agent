from typing import Dict, List, Any, Optional
import json


class MCPClient:
    """Client for interacting with MCP servers"""
    
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._load_mock_tools()
    
    def _load_mock_tools(self):
        """Load mock tools for demonstration (replace with actual MCP implementation)"""
        self.tools = {
            "db_query": {
                "name": "db_query",
                "description": "Execute a SQL query on the database",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SQL query to execute"
                        }
                    },
                    "required": ["query"]
                }
            },
            "db_schema": {
                "name": "db_schema",
                "description": "Get database schema information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Optional table name to get schema for"
                        }
                    }
                }
            },
            "search_docs": {
                "name": "search_docs",
                "description": "Search documentation",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            },
            "read_file": {
                "name": "read_file",
                "description": "Read a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path"
                        }
                    },
                    "required": ["path"]
                }
            },
            "write_file": {
                "name": "write_file",
                "description": "Write to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "File path"
                        },
                        "content": {
                            "type": "string",
                            "description": "File content"
                        }
                    },
                    "required": ["path", "content"]
                }
            }
        }
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """Discover available tools from MCP servers"""
        return list(self.tools.values())
    
    async def invoke_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a tool via MCP"""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Mock implementation - replace with actual MCP invocation
        return {
            "success": True,
            "result": f"Mock result for {tool_name} with args {arguments}"
        }
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool schema by name"""
        return self.tools.get(tool_name)


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """Get or create the global MCP client"""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = MCPClient()
    return _mcp_client
