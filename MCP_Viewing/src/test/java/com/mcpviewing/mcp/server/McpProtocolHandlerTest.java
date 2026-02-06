package com.mcpviewing.mcp.server;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.mcpviewing.mcp.tools.ToolRegistry;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

import static org.assertj.core.api.Assertions.assertThat;

/**
 * Test for McpProtocolHandler to ensure proper JSON-RPC ID handling
 */
class McpProtocolHandlerTest {

    @Mock
    private ToolRegistry toolRegistry;

    private McpProtocolHandler handler;
    private Gson gson = new Gson();

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        handler = new McpProtocolHandler(toolRegistry);
    }

    @Test
    void testInitializeWithIntegerId() {
        // Test that integer IDs are preserved as integers in the response
        String request = "{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"id\":0}";
        
        String response = handler.handleRequest(request);
        
        // Parse the response to verify ID format
        JsonObject responseObj = gson.fromJson(response, JsonObject.class);
        
        // Verify the ID is present and is numeric
        assertThat(responseObj.has("id")).isTrue();
        assertThat(responseObj.get("id").isJsonPrimitive()).isTrue();
        assertThat(responseObj.get("id").getAsJsonPrimitive().isNumber()).isTrue();
        
        // Check that the ID value is correct
        assertThat(responseObj.get("id").getAsInt()).isEqualTo(0);
        
        // Most importantly: verify the serialized form doesn't contain "0.0"
        // This is what the MCP client library validates
        assertThat(response).doesNotContain("\"id\": 0.0");
        assertThat(response).contains("\"id\": 0");
    }

    @Test
    void testInitializeWithStringId() {
        // Test that string IDs are preserved as strings
        String request = "{\"jsonrpc\":\"2.0\",\"method\":\"initialize\",\"id\":\"test-id\"}";
        
        String response = handler.handleRequest(request);
        
        JsonObject responseObj = gson.fromJson(response, JsonObject.class);
        
        assertThat(responseObj.has("id")).isTrue();
        assertThat(responseObj.get("id").getAsString()).isEqualTo("test-id");
    }

    @Test
    void testPingWithIntegerId() {
        // Test ping method with integer ID
        String request = "{\"jsonrpc\":\"2.0\",\"method\":\"ping\",\"id\":1}";
        
        String response = handler.handleRequest(request);
        
        JsonObject responseObj = gson.fromJson(response, JsonObject.class);
        
        assertThat(responseObj.has("id")).isTrue();
        assertThat(responseObj.get("id").getAsInt()).isEqualTo(1);
        
        // Verify the serialized form uses integer format
        assertThat(response).doesNotContain("\"id\": 1.0");
        assertThat(response).contains("\"id\": 1");
        
        // Verify response contains the result
        assertThat(responseObj.has("result")).isTrue();
    }
}
