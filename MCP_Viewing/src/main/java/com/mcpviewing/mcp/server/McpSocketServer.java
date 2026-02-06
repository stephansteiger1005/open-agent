package com.mcpviewing.mcp.server;

import com.mcpviewing.mcp.tools.ToolRegistry;
import com.mcpviewing.service.PartInfoService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import jakarta.annotation.PreDestroy;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

/**
 * MCP Server Socket Runner
 * Runs the MCP server in socket mode for integration with Claude Desktop
 * Allows parallel operation with REST API
 * 
 * Enable this by setting:
 * - mcp.server.enabled=true
 * - mcp.server.mode=socket (default)
 * - mcp.server.port=9000 (default)
 */
@Component
@ConditionalOnProperty(name = "mcp.server.enabled", havingValue = "true")
@Slf4j
public class McpSocketServer implements CommandLineRunner {

    @Autowired(required = false)
    private McpProtocolHandler protocolHandler;
    
    @Autowired(required = false)
    private PartInfoService partInfoService;
    
    @Autowired(required = false)
    private ToolRegistry toolRegistry;
    
    @Value("${mcp.server.port:9000}")
    private int mcpPort;
    
    @Value("${mcp.server.mode:socket}")
    private String mcpMode;
    
    private final ExecutorService executorService = Executors.newCachedThreadPool();
    
    /**
     * Shutdown the executor service when the application context is destroyed
     */
    @PreDestroy
    public void shutdown() {
        log.info("Shutting down MCP Server executor service...");
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

    @Override
    public void run(String... args) {
        // Initialize the protocol handler if not already autowired
        if (protocolHandler == null && partInfoService != null) {
            if (toolRegistry == null) {
                toolRegistry = new ToolRegistry(partInfoService);
            }
            protocolHandler = new McpProtocolHandler(toolRegistry);
        }
        
        if (protocolHandler == null) {
            log.error("MCP Protocol Handler not initialized. Cannot start MCP server.");
            return;
        }
        
        // Choose mode: socket or stdio
        if ("stdio".equalsIgnoreCase(mcpMode)) {
            runStdioMode();
        } else {
            runSocketMode();
        }
    }
    
    /**
     * Run MCP server in socket mode (for Docker/parallel with REST API)
     */
    private void runSocketMode() {
        log.info("Starting MCP Server in socket mode on port {}...", mcpPort);
        log.info("REST API continues to run on its configured port");
        
        // Run in separate thread to not block Spring Boot
        executorService.submit(() -> {
            try (ServerSocket serverSocket = new ServerSocket(mcpPort)) {
                log.info("MCP Server listening on port {}", mcpPort);
                log.info("Ready to accept connections from Claude Desktop");
                
                while (!Thread.currentThread().isInterrupted()) {
                    try {
                        Socket clientSocket = serverSocket.accept();
                        log.info("Client connected from {}", clientSocket.getRemoteSocketAddress());
                        
                        // Handle client in separate thread
                        executorService.submit(() -> handleClient(clientSocket));
                        
                    } catch (IOException e) {
                        if (!Thread.currentThread().isInterrupted()) {
                            log.error("Error accepting client connection: {}", e.getMessage());
                        }
                    }
                }
            } catch (IOException e) {
                log.error("Failed to start MCP server on port {}: {}", mcpPort, e.getMessage(), e);
            }
        });
    }
    
    /**
     * Handle individual client connection
     */
    private void handleClient(Socket clientSocket) {
        try (
            BufferedReader reader = new BufferedReader(
                new InputStreamReader(clientSocket.getInputStream(), StandardCharsets.UTF_8));
            PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true, StandardCharsets.UTF_8)
        ) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().isEmpty()) {
                    continue;
                }
                
                log.debug("Received MCP request: {}", line);
                
                try {
                    String response = protocolHandler.handleRequest(line);
                    writer.println(response);
                    writer.flush();
                    log.debug("Sent MCP response: {}", response);
                } catch (Exception e) {
                    log.error("Error processing MCP request: {}", e.getMessage(), e);
                }
            }
            
            log.info("Client disconnected from {}", clientSocket.getRemoteSocketAddress());
            
        } catch (IOException e) {
            log.error("IO error handling client: {}", e.getMessage());
        }
    }
    
    /**
     * Run MCP server in stdio mode (for direct Claude Desktop integration)
     */
    private void runStdioMode() {
        log.info("Starting MCP Server in stdio mode...");
        log.info("Ready to accept JSON-RPC requests from Claude Desktop via stdin/stdout");
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(System.in, StandardCharsets.UTF_8))) {
            
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().isEmpty()) {
                    continue;
                }
                
                try {
                    String response = protocolHandler.handleRequest(line);
                    System.out.println(response);
                    System.out.flush();
                } catch (Exception e) {
                    log.error("Error processing request: {}", e.getMessage(), e);
                }
            }
        } catch (IOException e) {
            log.error("IO error in MCP server: {}", e.getMessage(), e);
            throw new RuntimeException("MCP Server failed to start in stdio mode", e);
        }
        
        log.info("MCP Server shutting down");
    }
}
