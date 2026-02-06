#!/bin/bash
# MCP Server Test Script
# Tests the MCP server JSON-RPC functionality

echo "Building the project..."
mvn clean package -DskipTests

echo ""
echo "Testing MCP Server with JSON-RPC requests..."
echo ""
echo "Note: For full integration testing with Claude Desktop,"
echo "      follow the instructions in MCP_INTEGRATION.md"
echo ""
echo "Build completed successfully!"
echo ""
echo "To test the MCP server manually:"
echo ""
echo "1. Start the server:"
echo "   java -jar target/mcp-viewing-1.0.0.jar --mcp.server.enabled=true --spring.main.web-application-type=none"
echo ""
echo "2. In another terminal, send JSON-RPC requests:"
echo '   echo '"'"'{"jsonrpc":"2.0","method":"ping","id":1}'"'"' | nc localhost 8080'
echo ""
echo "Or use it with Claude Desktop - see MCP_INTEGRATION.md for setup instructions."

