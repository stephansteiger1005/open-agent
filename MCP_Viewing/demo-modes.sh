#!/bin/bash
# Demonstration script showing both REST API and MCP Server modes

echo "============================================"
echo "MCP_Viewing - Dual Mode Demonstration"
echo "============================================"
echo ""

# Build the project
echo "Building the project..."
mvn clean package -DskipTests
echo ""

# Check if build was successful
if [ ! -f target/mcp-viewing-1.0.0.jar ]; then
    echo "Build failed! JAR file not found."
    exit 1
fi

echo "Build successful! JAR file created."
echo ""
echo "============================================"
echo "Mode 1: REST API Server"
echo "============================================"
echo ""
echo "To run as REST API server (default mode):"
echo ""
echo "  java -jar target/mcp-viewing-1.0.0.jar"
echo ""
echo "The REST API will be available at:"
echo "  - http://localhost:8080/api/partinfo"
echo "  - http://localhost:8080/swagger-ui.html"
echo ""

echo "============================================"
echo "Mode 2: MCP Server (Claude Desktop)"
echo "============================================"
echo ""
echo "To run as MCP server for Claude Desktop:"
echo ""
echo "  java -jar target/mcp-viewing-1.0.0.jar \\"
echo "    --mcp.server.enabled=true \\"
echo "    --spring.main.web-application-type=none"
echo ""
echo "Claude Desktop Configuration:"
echo "  File: ~/.config/Claude/claude_desktop_config.json"
echo ""
echo '  {'
echo '    "mcpServers": {'
echo '      "mcp-viewing": {'
echo '        "command": "java",'
echo '        "args": ['
echo '          "-jar",'
echo "          \"$(pwd)/target/mcp-viewing-1.0.0.jar\","
echo '          "--mcp.server.enabled=true",'
echo '          "--spring.main.web-application-type=none"'
echo '        ]'
echo '      }'
echo '    }'
echo '  }'
echo ""

echo "============================================"
echo "Quick Test - MCP Protocol"
echo "============================================"
echo ""
echo "Testing MCP server with a ping request..."
echo ""

# Start MCP server in background and send a ping
(echo '{"jsonrpc":"2.0","method":"ping","id":1}' | \
  timeout 5 java -jar target/mcp-viewing-1.0.0.jar \
    --mcp.server.enabled=true \
    --spring.main.web-application-type=none 2>/dev/null) || true

echo ""
echo "============================================"
echo "For more information, see:"
echo "  - README.md"
echo "  - MCP_INTEGRATION.md"
echo "  - MCP_COMPLIANCE_SUMMARY.md"
echo "============================================"
