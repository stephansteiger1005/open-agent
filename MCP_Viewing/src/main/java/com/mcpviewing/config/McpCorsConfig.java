package com.mcpviewing.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;

import java.util.Arrays;
import java.util.List;

/**
 * CORS Configuration for MCP HTTP Transport
 * Enables cross-origin requests to the /mcp endpoint
 * Required for integration with OpenAI proxy and web-based MCP clients
 */
@Configuration
@ConditionalOnProperty(name = "mcp.server.enabled", havingValue = "true")
public class McpCorsConfig {

    @Value("${mcp.cors.allowed-origins:*}")
    private String allowedOrigins;

    @Bean
    public CorsFilter mcpCorsFilter() {
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        CorsConfiguration config = new CorsConfiguration();
        
        // Allow configured origins (default: all for development)
        // For production, set mcp.cors.allowed-origins to specific domains
        if ("*".equals(allowedOrigins)) {
            config.setAllowedOriginPatterns(List.of("*"));
            // Don't allow credentials with wildcard origins for security
            config.setAllowCredentials(false);
        } else {
            config.setAllowedOrigins(Arrays.asList(allowedOrigins.split(",")));
            config.setAllowCredentials(true);
        }
        
        // Allow specific HTTP methods
        config.setAllowedMethods(Arrays.asList("GET", "POST", "OPTIONS"));
        
        // Allow specific headers
        config.setAllowedHeaders(Arrays.asList(
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin"
        ));
        
        // Cache preflight response for 1 hour
        config.setMaxAge(3600L);
        
        // Expose headers that clients can read
        config.setExposedHeaders(Arrays.asList(
            "Content-Type",
            "Content-Length"
        ));
        
        // Apply CORS configuration to /mcp endpoints
        source.registerCorsConfiguration("/mcp/**", config);
        
        return new CorsFilter(source);
    }
}
