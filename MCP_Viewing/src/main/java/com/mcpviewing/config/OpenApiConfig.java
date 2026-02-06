package com.mcpviewing.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.License;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * OpenAPI/Swagger Configuration
 * Provides API documentation at /swagger-ui.html
 */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI mcpViewingOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("MCP Viewing REST API")
                        .description("REST API for managing PLMXML data in Derby PARTINFODB database. " +
                                "Supports operations to retrieve, create, update, and delete part information by Sachnummer (SNR).")
                        .version("1.0.0")
                        .contact(new Contact()
                                .name("MCP Viewing Team")
                                .email("support@mcpviewing.com"))
                        .license(new License()
                                .name("Apache 2.0")
                                .url("https://www.apache.org/licenses/LICENSE-2.0.html")));
    }
}
