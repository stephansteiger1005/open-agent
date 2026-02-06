package com.mcpviewing.mcp.protocol;

import lombok.Data;

/**
 * JSON-RPC 2.0 Response message
 * Used for MCP protocol communication
 */
@Data
public class JsonRpcResponse {
    private String jsonrpc = "2.0";
    private Object result;
    private JsonRpcError error;
    private Object id;

    public static JsonRpcResponse success(Object id, Object result) {
        JsonRpcResponse response = new JsonRpcResponse();
        response.setId(id);
        response.setResult(result);
        return response;
    }

    public static JsonRpcResponse error(Object id, JsonRpcError error) {
        JsonRpcResponse response = new JsonRpcResponse();
        response.setId(id);
        response.setError(error);
        return response;
    }
}
