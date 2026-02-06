package com.mcpviewing.mcp.protocol;

import com.google.gson.JsonObject;
import lombok.Data;

/**
 * JSON-RPC 2.0 Request message
 * Used for MCP protocol communication
 */
@Data
public class JsonRpcRequest {
    private String jsonrpc = "2.0";
    private String method;
    private JsonObject params;
    private Object id;
}
