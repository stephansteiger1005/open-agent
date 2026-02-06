package com.mcpviewing.mcp.server;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.google.gson.JsonObject;
import com.google.gson.JsonSyntaxException;
import com.mcpviewing.mcp.protocol.JsonRpcError;
import com.mcpviewing.mcp.protocol.JsonRpcRequest;
import com.mcpviewing.mcp.protocol.JsonRpcResponse;
import com.mcpviewing.mcp.tools.McpTool;
import com.mcpviewing.mcp.tools.ToolRegistry;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * MCP Protocol Handler
 * Implements the Model Context Protocol (MCP) JSON-RPC interface
 * for integration with Claude Desktop and other MCP clients
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class McpProtocolHandler {

    private final ToolRegistry toolRegistry;
    private final Gson gson = new GsonBuilder().setPrettyPrinting().create();
    
    private static final String MCP_VERSION = "0.1.0";
    private static final String SERVER_NAME = "mcp-viewing";
    private static final String SERVER_VERSION = "1.0.0";

    /**
     * Process a JSON-RPC request and return a JSON-RPC response
     */
    public String handleRequest(String requestJson) {
        log.debug("Received MCP request: {}", requestJson);
        
        try {
            JsonRpcRequest request = gson.fromJson(requestJson, JsonRpcRequest.class);
            JsonRpcResponse response = processRequest(request);
            String responseJson = gson.toJson(response);
            log.debug("Sending MCP response: {}", responseJson);
            return responseJson;
        } catch (JsonSyntaxException e) {
            log.error("Invalid JSON in request: {}", e.getMessage());
            JsonRpcResponse errorResponse = JsonRpcResponse.error(
                null,
                new JsonRpcError(JsonRpcError.PARSE_ERROR, "Invalid JSON")
            );
            return gson.toJson(errorResponse);
        } catch (Exception e) {
            log.error("Error processing MCP request: {}", e.getMessage(), e);
            JsonRpcResponse errorResponse = JsonRpcResponse.error(
                null,
                new JsonRpcError(JsonRpcError.INTERNAL_ERROR, "Internal server error: " + e.getMessage())
            );
            return gson.toJson(errorResponse);
        }
    }

    private JsonRpcResponse processRequest(JsonRpcRequest request) {
        String method = request.getMethod();
        
        if (method == null) {
            return JsonRpcResponse.error(
                request.getId(),
                new JsonRpcError(JsonRpcError.INVALID_REQUEST, "Missing method")
            );
        }
        
        try {
            Object result;
            switch (method) {
                case "initialize":
                    result = handleInitialize(request.getParams());
                    break;
                case "tools/list":
                    result = handleToolsList();
                    break;
                case "tools/call":
                    result = handleToolsCall(request.getParams());
                    break;
                case "ping":
                    result = handlePing();
                    break;
                default:
                    return JsonRpcResponse.error(
                        request.getId(),
                        new JsonRpcError(JsonRpcError.METHOD_NOT_FOUND, "Method not found: " + method)
                    );
            }
            
            return JsonRpcResponse.success(request.getId(), result);
        } catch (IllegalArgumentException e) {
            return JsonRpcResponse.error(
                request.getId(),
                new JsonRpcError(JsonRpcError.INVALID_PARAMS, e.getMessage())
            );
        } catch (Exception e) {
            log.error("Error executing method {}: {}", method, e.getMessage(), e);
            return JsonRpcResponse.error(
                request.getId(),
                new JsonRpcError(JsonRpcError.INTERNAL_ERROR, "Error: " + e.getMessage())
            );
        }
    }

    private Object handleInitialize(JsonObject params) {
        log.info("MCP server initializing with version {}", MCP_VERSION);
        
        Map<String, Object> result = new HashMap<>();
        result.put("protocolVersion", MCP_VERSION);
        result.put("serverInfo", Map.of(
            "name", SERVER_NAME,
            "version", SERVER_VERSION
        ));
        result.put("capabilities", Map.of(
            "tools", Map.of("supportsProgress", false)
        ));
        
        return result;
    }

    private Object handleToolsList() {
        log.debug("Listing available MCP tools");
        List<McpTool> tools = toolRegistry.getTools();
        return Map.of("tools", tools);
    }

    private Object handleToolsCall(JsonObject params) {
        if (params == null || !params.has("name")) {
            throw new IllegalArgumentException("Missing tool name in params");
        }
        
        String toolName = params.get("name").getAsString();
        JsonObject arguments = params.has("arguments") ? 
            params.get("arguments").getAsJsonObject() : new JsonObject();
        
        log.info("Calling tool: {} with arguments: {}", toolName, arguments);
        
        Object result = toolRegistry.executeTool(toolName, arguments);
        
        return Map.of(
            "content", List.of(
                Map.of(
                    "type", "text",
                    "text", gson.toJson(result)
                )
            )
        );
    }

    private Object handlePing() {
        return Map.of("status", "ok");
    }
}
