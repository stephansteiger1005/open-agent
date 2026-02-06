package com.mcpviewing;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Main Spring Boot Application for MCP Viewing Backend
 * Provides REST API for managing PLMXML data in Derby database (PARTINFODB)
 */
@SpringBootApplication
public class McpViewingApplication {

    public static void main(String[] args) {
        SpringApplication.run(McpViewingApplication.class, args);
    }
}
