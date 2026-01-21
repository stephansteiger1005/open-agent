#!/bin/bash
# Example demonstrating OpenAI-powered agent selection and chat completion
# This shows:
# 1. The router agent classifying and selecting which agent to use
# 2. The general purpose agent providing a chat completion response

# Check for required dependencies
if ! command -v jq &> /dev/null; then
    echo "Error: jq is not installed. Please install it first."
    echo "  Ubuntu/Debian: sudo apt-get install jq"
    echo "  macOS: brew install jq"
    echo "  CentOS/RHEL 8+: sudo dnf install jq"
    echo "  CentOS/RHEL 7: sudo yum install jq"
    exit 1
fi

API_BASE="http://0.0.0.0:8000"
API_KEY="dev_key_123456789"

echo "=========================================================="
echo "OpenAI Agent Selection and Chat Completion Example"
echo "=========================================================="
echo ""
echo "This example demonstrates:"
echo "1. Router agent using OpenAI for agent selection/classification"
echo "2. General purpose agent using OpenAI for chat completion"
echo ""

# Health check
echo "Checking API health..."
HEALTH=$(curl -s -X GET "$API_BASE/health")
if [ $? -ne 0 ]; then
    echo "Error: API is not reachable. Make sure the server is running."
    exit 1
fi
echo "✓ API is healthy"
echo ""

# ======================================
# Scenario 1: Router Agent Classification
# ======================================
echo "=========================================================="
echo "SCENARIO 1: Agent Selection (Router)"
echo "=========================================================="
echo ""

# Create a conversation for routing
echo "Creating conversation for agent selection..."
CONV1_RESPONSE=$(curl -s -X POST "$API_BASE/v1/conversations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"scenario": "routing_example"}}')
CONV1_ID=$(echo "$CONV1_RESPONSE" | jq -r '.id')

if [ -z "$CONV1_ID" ] || [ "$CONV1_ID" = "null" ]; then
    echo "Error: Failed to create conversation"
    echo "Response: $CONV1_RESPONSE"
    exit 1
fi
echo "✓ Conversation created: $CONV1_ID"
echo ""

# Add a user message that requires routing/classification
echo "User message: 'I need help writing a SQL query to get all users from the database'"
curl -s -X POST "$API_BASE/v1/conversations/$CONV1_ID/messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "I need help writing a SQL query to get all users from the database",
    "attachments": []
  }' > /dev/null
echo "✓ Message added to conversation"
echo ""

# Execute the router agent to classify and select appropriate agent
echo "Executing Router Agent (OpenAI-powered classification)..."
echo "---"
RUN1_RESPONSE=$(curl -s -X POST "$API_BASE/v1/conversations/$CONV1_ID/runs" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "router",
    "stream": false,
    "metadata": {}
  }')
RUN1_ID=$(echo "$RUN1_RESPONSE" | jq -r '.run_id')

if [ -z "$RUN1_ID" ] || [ "$RUN1_ID" = "null" ]; then
    echo "Error: Failed to create run"
    echo "Response: $RUN1_RESPONSE"
    exit 1
fi
echo "✓ Router run completed: $RUN1_ID"
echo ""

# Get the router's response
echo "Router Agent Response (Agent Classification):"
echo "---"
MESSAGES1=$(curl -s -X GET "$API_BASE/v1/conversations/$CONV1_ID" \
  -H "Authorization: Bearer $API_KEY" | jq -r '.metadata')
curl -s -X GET "$API_BASE/v1/runs/$RUN1_ID/steps" \
  -H "Authorization: Bearer $API_KEY" | jq -r '.[0].output_data.content'
echo "---"
echo ""

# ======================================
# Scenario 2: General Purpose Agent
# ======================================
echo "=========================================================="
echo "SCENARIO 2: General Purpose Chat Completion"
echo "=========================================================="
echo ""

# Create a conversation for general chat
echo "Creating conversation for general chat..."
CONV2_RESPONSE=$(curl -s -X POST "$API_BASE/v1/conversations" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"metadata": {"scenario": "general_chat_example"}}')
CONV2_ID=$(echo "$CONV2_RESPONSE" | jq -r '.id')

if [ -z "$CONV2_ID" ] || [ "$CONV2_ID" = "null" ]; then
    echo "Error: Failed to create conversation"
    echo "Response: $CONV2_RESPONSE"
    exit 1
fi
echo "✓ Conversation created: $CONV2_ID"
echo ""

# Add a general user message
echo "User message: 'What are the benefits of using microservices architecture?'"
curl -s -X POST "$API_BASE/v1/conversations/$CONV2_ID/messages" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "role": "user",
    "content": "What are the benefits of using microservices architecture?",
    "attachments": []
  }' > /dev/null
echo "✓ Message added to conversation"
echo ""

# Execute the general purpose agent
echo "Executing General Purpose Agent (OpenAI-powered chat completion)..."
echo "---"
RUN2_RESPONSE=$(curl -s -X POST "$API_BASE/v1/conversations/$CONV2_ID/runs" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "general",
    "stream": false,
    "metadata": {}
  }')
RUN2_ID=$(echo "$RUN2_RESPONSE" | jq -r '.run_id')

if [ -z "$RUN2_ID" ] || [ "$RUN2_ID" = "null" ]; then
    echo "Error: Failed to create run"
    echo "Response: $RUN2_RESPONSE"
    exit 1
fi
echo "✓ General agent run completed: $RUN2_ID"
echo ""

# Get the general agent's response
echo "General Purpose Agent Response (Chat Completion):"
echo "---"
curl -s -X GET "$API_BASE/v1/runs/$RUN2_ID/steps" \
  -H "Authorization: Bearer $API_KEY" | jq -r '.[0].output_data.content'
echo "---"
echo ""

# ======================================
# Summary
# ======================================
echo "=========================================================="
echo "SUMMARY"
echo "=========================================================="
echo ""
echo "✓ Router Agent (Scenario 1):"
echo "  - Analyzed user request about SQL queries"
echo "  - Used OpenAI to classify intent and select appropriate specialist agent"
echo "  - Demonstrated agent selection/routing capabilities"
echo ""
echo "✓ General Purpose Agent (Scenario 2):"
echo "  - Responded to general question about microservices"
echo "  - Used OpenAI for natural language chat completion"
echo "  - Demonstrated conversational AI capabilities"
echo ""
echo "Both scenarios used OpenAI API for intelligent agent responses!"
echo "=========================================================="
