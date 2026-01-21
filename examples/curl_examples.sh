#!/bin/bash
# Example curl commands for testing the Multi-Agent OpenWebUI API

# Check for required dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it first."
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  macOS: brew install jq"
    echo "  CentOS/RHEL: sudo yum install jq"
    exit 1
fi

API_BASE="http://localhost:8000"
API_KEY="dev_key_123456789"

echo "=== Multi-Agent OpenWebUI API Examples ==="
echo

# Health check
echo "1. Health Check"
curl -X GET "$API_BASE/health"
echo -e "\n"

# Create a conversation
echo "2. Create Conversation"
CONVERSATION_RESPONSE=$(curl -s -X POST "$API_BASE/v1/conversations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"user": "test_user"}}')
CONVERSATION_ID=$(echo "$CONVERSATION_RESPONSE" | jq -r '.id')

if [ -z "$CONVERSATION_ID" ] || [ "$CONVERSATION_ID" = "null" ]; then
    echo "Error: Failed to create conversation"
    echo "Response: $CONVERSATION_RESPONSE"
    exit 1
fi

echo "Created conversation: $CONVERSATION_ID"
echo

# Add a user message
echo "3. Add User Message"
curl -X POST "$API_BASE/v1/conversations/$CONVERSATION_ID/messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "Hello, I need help with a SQL query",
    "attachments": []
  }' | jq
echo

# Create a run (non-streaming)
echo "4. Create Run (Non-Streaming)"
RUN_RESPONSE=$(curl -s -X POST "$API_BASE/v1/conversations/$CONVERSATION_ID/runs" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "router",
    "stream": false,
    "metadata": {}
  }')
RUN_ID=$(echo "$RUN_RESPONSE" | jq -r '.run_id')

if [ -z "$RUN_ID" ] || [ "$RUN_ID" = "null" ]; then
    echo "Error: Failed to create run"
    echo "Response: $RUN_RESPONSE"
    exit 1
fi

echo "Created run: $RUN_ID"
echo

# Get run details
echo "5. Get Run Details"
curl -X GET "$API_BASE/v1/runs/$RUN_ID" \
  -H "Authorization: Bearer $API_KEY" | jq
echo

# Get run steps
echo "6. Get Run Steps"
curl -X GET "$API_BASE/v1/runs/$RUN_ID/steps" \
  -H "Authorization: Bearer $API_KEY" | jq
echo

# List all agents
echo "7. List Agents"
curl -X GET "$API_BASE/v1/agents" \
  -H "Authorization: Bearer $API_KEY" | jq
echo

# Get specific agent
echo "8. Get Router Agent"
curl -X GET "$API_BASE/v1/agents/router" \
  -H "Authorization: Bearer $API_KEY" | jq
echo

# List tools
echo "9. List Tools"
curl -X GET "$API_BASE/v1/tools" \
  -H "Authorization: Bearer $API_KEY" | jq
echo

# Get conversation
echo "10. Get Conversation"
curl -X GET "$API_BASE/v1/conversations/$CONVERSATION_ID" \
  -H "Authorization: Bearer $API_KEY" | jq
echo

# Streaming example (requires different handling)
echo "11. Create Run (Streaming) - Note: This will stream events"
echo "curl -X POST \"$API_BASE/v1/conversations/CONV_ID/runs\" \\"
echo "  -H \"Authorization: Bearer $API_KEY\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"agent_id\": \"router\", \"stream\": true}'"
echo

echo "=== Examples Complete ==="
