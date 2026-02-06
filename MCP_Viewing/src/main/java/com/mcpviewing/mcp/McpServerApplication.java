package com.mcpviewing.mcp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;

/**
 * MCP Server Application
 * Standalone application that runs the MCP server in stdio mode
 * 
 * Usage: java -jar mcp-viewing.jar --mcp.server.enabled=true
 */
@SpringBootApplication
@ComponentScan(basePackages = "com.mcpviewing")
public class McpServerApplication {

    public static void main(String[] args) {
        // Set MCP server mode
        System.setProperty("mcp.server.enabled", "true");
        // Disable web server for stdio mode
        System.setProperty("spring.main.web-application-type", "none");
        
        SpringApplication.run(McpServerApplication.class, args);
    }
}
