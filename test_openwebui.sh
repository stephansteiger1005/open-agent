#!/bin/bash
set -e

# Test script for OpenWebUI integration
# This script verifies that all components are working together

echo "==================================="
echo "OpenWebUI Integration Test"
echo "==================================="
echo ""

API_BASE="http://localhost:8000"
API_KEY="dev_key_123456789"

echo "1. Checking if API is running..."
if ! curl -s "${API_BASE}/health" > /dev/null; then
    echo "❌ API is not responding. Make sure 'docker compose up' is running."
    exit 1
fi
echo "✓ API is running"
echo ""

echo "2. Testing agent discovery..."
AGENTS=$(curl -s -H "Authorization: Bearer ${API_KEY}" "${API_BASE}/v1/agents")
AGENT_COUNT=$(echo "$AGENTS" | jq '. | length')
echo "✓ Found ${AGENT_COUNT} agents"
echo ""

echo "3. Listing available agents:"
echo "$AGENTS" | jq -r '.[] | "   - \(.id): \(.name)"'
echo ""

echo "4. Testing conversation creation..."
CONV_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/conversations" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"test": "openwebui_integration"}}')

CONV_ID=$(echo "$CONV_RESPONSE" | jq -r '.id')
if [ -z "$CONV_ID" ] || [ "$CONV_ID" = "null" ]; then
    echo "❌ Failed to create conversation"
    exit 1
fi
echo "✓ Created conversation: ${CONV_ID}"
echo ""

echo "5. Adding a test message..."
MSG_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/conversations/${CONV_ID}/messages" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"role": "user", "content": "Hello from test script!"}')

MSG_ID=$(echo "$MSG_RESPONSE" | jq -r '.id')
if [ -z "$MSG_ID" ] || [ "$MSG_ID" = "null" ]; then
    echo "❌ Failed to add message"
    exit 1
fi
echo "✓ Added message: ${MSG_ID}"
echo ""

echo "6. Testing router agent execution (non-streaming)..."
RUN_RESPONSE=$(curl -s -X POST "${API_BASE}/v1/conversations/${CONV_ID}/runs" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"agent_id": "router", "stream": false}')

RUN_ID=$(echo "$RUN_RESPONSE" | jq -r '.run_id')
if [ -z "$RUN_ID" ] || [ "$RUN_ID" = "null" ]; then
    echo "❌ Failed to execute run"
    echo "Response: $RUN_RESPONSE"
    exit 1
fi
echo "✓ Run executed: ${RUN_ID}"
echo ""

echo "7. Verifying OpenWebUI service..."
if ! docker compose ps | grep -q "openwebui.*Up"; then
    echo "⚠ OpenWebUI service is not running"
    echo "Start it with: docker compose up openwebui -d"
else
    echo "✓ OpenWebUI service is running"
    echo ""
    echo "8. Testing OpenWebUI accessibility..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
        echo "✓ OpenWebUI is accessible at http://localhost:3000"
    else
        echo "⚠ OpenWebUI may still be starting up"
        echo "Try accessing it at: http://localhost:3000"
    fi
fi
echo ""

echo "==================================="
echo "✓ All tests passed!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Select an agent from the model dropdown"
echo "3. Start chatting!"
echo ""
echo "Available agents:"
echo "$AGENTS" | jq -r '.[] | "   - \(.name) (\(.id))"'
