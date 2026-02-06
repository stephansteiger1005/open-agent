package com.mcpviewing.mcp.controller;

import com.mcpviewing.mcp.server.McpProtocolHandler;
import jakarta.annotation.PreDestroy;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * MCP HTTP Controller
 * Implements HTTP transport for MCP (Model Context Protocol)
 * Supports both regular POST requests and Server-Sent Events (SSE)
 * for streaming responses
 * 
 * This enables integration with OpenAI proxy and other HTTP-based MCP clients
 * that use the /mcp endpoint with "Streamable HTTP" transport.
 */
@RestController
@RequestMapping("/mcp")
@RequiredArgsConstructor
@ConditionalOnProperty(name = "mcp.server.enabled", havingValue = "true")
@Slf4j
public class McpHttpController {

    private final McpProtocolHandler protocolHandler;
    private final ExecutorService executorService = Executors.newCachedThreadPool();

    /**
     * Shutdown the executor service when the bean is destroyed
     */
    @PreDestroy
    public void shutdown() {
        log.info("Shutting down MCP HTTP Controller executor service...");
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(10, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }

    /**
     * POST endpoint for MCP JSON-RPC requests
     * Handles standard HTTP POST requests with JSON-RPC 2.0 payload
     * 
     * @param requestBody JSON-RPC 2.0 request as string
     * @return JSON-RPC 2.0 response
     */
    @PostMapping(
        consumes = MediaType.APPLICATION_JSON_VALUE,
        produces = MediaType.APPLICATION_JSON_VALUE
    )
    public ResponseEntity<String> handleMcpRequest(@RequestBody String requestBody) {
        log.info("Received MCP HTTP request");
        log.debug("Request body: {}", requestBody);
        
        try {
            String response = protocolHandler.handleRequest(requestBody);
            log.debug("Response: {}", response);
            return ResponseEntity.ok()
                .contentType(MediaType.APPLICATION_JSON)
                .body(response);
        } catch (Exception e) {
            log.error("Error processing MCP HTTP request: {}", e.getMessage(), e);
            return ResponseEntity.internalServerError()
                .body("{\"jsonrpc\":\"2.0\",\"error\":{\"code\":-32603,\"message\":\"Internal error\"},\"id\":null}");
        }
    }

    /**
     * GET endpoint for Server-Sent Events (SSE) streaming
     * Allows bidirectional communication via HTTP streaming
     * Used by some MCP clients for long-lived connections
     * 
     * @return SSE emitter for streaming responses
     */
    @GetMapping(produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter handleSseConnection() {
        log.info("SSE connection established for MCP");
        
        // 30 minute timeout for SSE connections
        SseEmitter emitter = new SseEmitter(30 * 60 * 1000L);
        
        emitter.onCompletion(() -> log.info("SSE connection completed"));
        emitter.onTimeout(() -> {
            log.warn("SSE connection timed out");
            emitter.complete();
        });
        emitter.onError(e -> log.error("SSE connection error: {}", e.getMessage()));
        
        // Send initial connection event
        executorService.execute(() -> {
            try {
                emitter.send(SseEmitter.event()
                    .name("connected")
                    .data("{\"status\":\"connected\",\"protocol\":\"MCP\",\"version\":\"0.1.0\"}"));
            } catch (IOException e) {
                log.error("Error sending SSE event: {}", e.getMessage());
                emitter.completeWithError(e);
            }
        });
        
        return emitter;
    }

    /**
     * Health check endpoint for MCP service
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok()
            .contentType(MediaType.APPLICATION_JSON)
            .body("{\"status\":\"ok\",\"service\":\"mcp-viewing\",\"transport\":\"http\"}");
    }
}
