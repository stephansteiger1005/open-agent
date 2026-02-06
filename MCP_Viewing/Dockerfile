# Multi-stage build for MCP Viewing Spring Boot Application
FROM maven:3.9.5-eclipse-temurin-17 AS build

# Set working directory
WORKDIR /app

# Copy pom.xml and download dependencies
COPY pom.xml .
RUN mvn dependency:go-offline -B

# Copy source code
COPY src ./src

# Build the application
RUN mvn clean package -DskipTests

# Runtime stage
FROM eclipse-temurin:17-jre

# Set working directory
WORKDIR /app

# Copy the built JAR from build stage
COPY --from=build /app/target/*.jar app.jar

# Expose ports
# 8080 - REST API
# 9000 - MCP Server
EXPOSE 8080 9000

# Set JVM options
ENV JAVA_OPTS="-Xms256m -Xmx512m"

# MCP Server configuration
ENV MCP_SERVER_ENABLED=true
ENV MCP_SERVER_PORT=9000
ENV MCP_SERVER_MODE=socket

# Health check for REST API
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8080/actuator/health || exit 1

# Run the application with both REST API and MCP Server
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar app.jar --mcp.server.enabled=${MCP_SERVER_ENABLED} --mcp.server.port=${MCP_SERVER_PORT} --mcp.server.mode=${MCP_SERVER_MODE}"]
