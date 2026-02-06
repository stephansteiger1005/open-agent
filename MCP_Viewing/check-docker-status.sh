#!/bin/bash
# Docker Container Status Checker for MCP_Viewing
# This script checks the current state of the MCP_Viewing Docker container

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="mcp-viewing"
REST_API_PORT=8080
MCP_SERVER_PORT=9000

echo "============================================"
echo "MCP_Viewing - Docker Container Status Check"
echo "============================================"
echo ""

# Function to print status with color
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "${GREEN}✓${NC} $message"
            ;;
        "WARNING")
            echo -e "${YELLOW}⚠${NC} $message"
            ;;
        "ERROR")
            echo -e "${RED}✗${NC} $message"
            ;;
        "INFO")
            echo -e "${BLUE}ℹ${NC} $message"
            ;;
    esac
}

# Check if Docker is installed and running
echo "1. Checking Docker availability..."
if ! command -v docker &> /dev/null; then
    print_status "ERROR" "Docker is not installed on this system"
    echo ""
    echo "Please install Docker first:"
    echo "  https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker info &> /dev/null; then
    print_status "ERROR" "Docker daemon is not running"
    echo ""
    echo "Please start Docker daemon:"
    echo "  sudo systemctl start docker  (Linux)"
    echo "  Open Docker Desktop  (macOS/Windows)"
    exit 1
fi

print_status "OK" "Docker is installed and running"
echo ""

# Check if container exists
echo "2. Checking if container '$CONTAINER_NAME' exists..."
if ! docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    print_status "WARNING" "Container '$CONTAINER_NAME' does not exist"
    echo ""
    echo "To create and start the container, run:"
    echo "  docker-compose up -d"
    echo "  OR"
    echo "  docker build -t mcp-viewing:latest ."
    echo "  docker run -d --name mcp-viewing -p 8080:8080 -p 9000:9000 mcp-viewing:latest"
    exit 0
fi

print_status "OK" "Container '$CONTAINER_NAME' exists"
echo ""

# Get container status
echo "3. Container Status:"
# Optimize by using a single docker inspect call with multiple format strings
CONTAINER_INFO=$(docker inspect --format='{{.State.Status}}|{{.State.Running}}|{{.State.StartedAt}}|{{.State.ExitCode}}' "$CONTAINER_NAME" 2>/dev/null)
CONTAINER_STATUS=$(echo "$CONTAINER_INFO" | cut -d'|' -f1)
CONTAINER_RUNNING=$(echo "$CONTAINER_INFO" | cut -d'|' -f2)
CONTAINER_STARTED=$(echo "$CONTAINER_INFO" | cut -d'|' -f3)
CONTAINER_EXIT_CODE=$(echo "$CONTAINER_INFO" | cut -d'|' -f4)

echo "   Status: $CONTAINER_STATUS"
echo "   Running: $CONTAINER_RUNNING"
echo "   Started at: $CONTAINER_STARTED"

if [ "$CONTAINER_STATUS" = "running" ]; then
    print_status "OK" "Container is running"
elif [ "$CONTAINER_STATUS" = "exited" ]; then
    print_status "ERROR" "Container has exited (Exit Code: $CONTAINER_EXIT_CODE)"
    echo ""
    echo "To view exit logs:"
    echo "  docker logs $CONTAINER_NAME"
    echo ""
    echo "To restart the container:"
    echo "  docker start $CONTAINER_NAME"
    echo "  OR"
    echo "  docker-compose up -d"
elif [ "$CONTAINER_STATUS" = "created" ]; then
    print_status "WARNING" "Container is created but not started"
    echo ""
    echo "To start the container:"
    echo "  docker start $CONTAINER_NAME"
else
    print_status "WARNING" "Container is in '$CONTAINER_STATUS' state"
fi
echo ""

# Only continue if container is running
if [ "$CONTAINER_STATUS" != "running" ]; then
    echo "Skipping further checks as container is not running."
    exit 0
fi

# Check port mappings
echo "4. Port Mappings:"
PORTS=$(docker port "$CONTAINER_NAME" 2>/dev/null)
if [ -n "$PORTS" ]; then
    echo "$PORTS" | while read line; do
        print_status "INFO" "$line"
    done
else
    print_status "WARNING" "No ports are mapped"
fi
echo ""

# Check health status
echo "5. Health Check Status:"
HEALTH_STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null)
if [ "$HEALTH_STATUS" = "healthy" ]; then
    print_status "OK" "Container is healthy"
elif [ "$HEALTH_STATUS" = "unhealthy" ]; then
    print_status "ERROR" "Container is unhealthy"
    # Show last health check log
    HEALTH_LOG=$(docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' "$CONTAINER_NAME" 2>/dev/null | tail -n 3)
    if [ -n "$HEALTH_LOG" ]; then
        echo "   Last health check output:"
        echo "$HEALTH_LOG" | sed 's/^/     /'
    fi
elif [ "$HEALTH_STATUS" = "starting" ]; then
    print_status "WARNING" "Container is starting (health check in progress)"
elif [ -z "$HEALTH_STATUS" ] || [ "$HEALTH_STATUS" = "<no value>" ]; then
    print_status "INFO" "No health check configured for this container"
else
    print_status "WARNING" "Health status: $HEALTH_STATUS"
fi
echo ""

# Check resource usage
echo "6. Resource Usage:"
STATS=$(docker stats --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" "$CONTAINER_NAME" 2>/dev/null | tail -n 1)
if [ -n "$STATS" ]; then
    echo "   CPU %      Memory Usage       Memory %   Network I/O       Block I/O"
    echo "   $STATS"
    print_status "OK" "Resource usage retrieved successfully"
else
    print_status "WARNING" "Could not retrieve resource usage"
fi
echo ""

# Test REST API connectivity
echo "7. Testing REST API (Port $REST_API_PORT):"
HTTP_CODE="000"  # Initialize with default value
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$REST_API_PORT/actuator/health 2>/dev/null || echo "000")
    if [ "$HTTP_CODE" = "200" ]; then
        print_status "OK" "REST API is responding (HTTP $HTTP_CODE)"
        HEALTH_RESPONSE=$(curl -s http://localhost:$REST_API_PORT/actuator/health 2>/dev/null)
        if echo "$HEALTH_RESPONSE" | grep -q '"status":"UP"'; then
            print_status "OK" "Application health status: UP"
        fi
    elif [ "$HTTP_CODE" = "000" ]; then
        print_status "ERROR" "Cannot connect to REST API on port $REST_API_PORT"
        print_status "INFO" "Check if port is correctly mapped and firewall allows connections"
    else
        print_status "WARNING" "REST API responded with HTTP code: $HTTP_CODE"
    fi
else
    print_status "INFO" "curl not available - skipping REST API test"
    echo "   Install curl to test REST API connectivity"
fi
echo ""

# Test MCP Server connectivity
echo "8. Testing MCP Server (Port $MCP_SERVER_PORT):"
if command -v nc &> /dev/null; then
    # Test if port is listening
    if nc -z localhost $MCP_SERVER_PORT 2>/dev/null; then
        print_status "OK" "MCP Server port $MCP_SERVER_PORT is listening"
        
        # Try to send a test JSON-RPC request (using initialize or a simple test)
        # Note: This assumes the server implements a basic health check or initialize endpoint
        MCP_RESPONSE=$(echo '{"jsonrpc":"2.0","method":"initialize","params":{"capabilities":{}},"id":1}' | timeout 2 nc localhost $MCP_SERVER_PORT 2>/dev/null || echo "")
        if [ -n "$MCP_RESPONSE" ]; then
            print_status "OK" "MCP Server is responding to JSON-RPC requests"
        else
            print_status "WARNING" "MCP Server port is open but not responding to initialize request"
        fi
    else
        print_status "ERROR" "MCP Server port $MCP_SERVER_PORT is not listening"
        print_status "INFO" "Check MCP_SERVER_ENABLED environment variable"
    fi
else
    print_status "INFO" "netcat (nc) not available - skipping MCP Server test"
    echo "   Install netcat to test MCP Server connectivity"
fi
echo ""

# Show recent logs
echo "9. Recent Container Logs (last 15 lines):"
echo "-------------------------------------------"
docker logs --tail 15 "$CONTAINER_NAME" 2>&1
echo "-------------------------------------------"
echo ""

# Environment variables
echo "10. Important Environment Variables:"
# Optimize by running docker exec once and filtering
ENV_VARS=$(docker exec "$CONTAINER_NAME" env 2>/dev/null || echo "")
if [ -n "$ENV_VARS" ]; then
    # Use exact matching with ^ to avoid partial matches
    MCP_ENABLED=$(echo "$ENV_VARS" | grep '^MCP_SERVER_ENABLED=' || echo "   MCP_SERVER_ENABLED: Not set")
    MCP_PORT=$(echo "$ENV_VARS" | grep '^MCP_SERVER_PORT=' || echo "   MCP_SERVER_PORT: Not set")
    MCP_MODE=$(echo "$ENV_VARS" | grep '^MCP_SERVER_MODE=' || echo "   MCP_SERVER_MODE: Not set")
    JAVA_OPTS=$(echo "$ENV_VARS" | grep '^JAVA_OPTS=' || echo "   JAVA_OPTS: Not set")
    
    echo "   $MCP_ENABLED"
    echo "   $MCP_PORT"
    echo "   $MCP_MODE"
    echo "   $JAVA_OPTS"
else
    print_status "WARNING" "Could not retrieve environment variables"
fi
echo ""

# Summary and recommendations
echo "============================================"
echo "Summary"
echo "============================================"
echo ""

if [ "$CONTAINER_STATUS" = "running" ] && [ "$HTTP_CODE" = "200" ]; then
    print_status "OK" "Container is running and healthy"
    echo ""
    echo "Available endpoints:"
    echo "  • REST API: http://localhost:$REST_API_PORT"
    echo "  • Swagger UI: http://localhost:$REST_API_PORT/swagger-ui.html"
    echo "  • Health Check: http://localhost:$REST_API_PORT/actuator/health"
    echo "  • MCP Server: localhost:$MCP_SERVER_PORT (Socket connection)"
elif [ "$CONTAINER_STATUS" = "running" ]; then
    print_status "WARNING" "Container is running but may have issues"
    echo ""
    echo "Troubleshooting commands:"
    echo "  • View logs: docker logs -f $CONTAINER_NAME"
    echo "  • Restart: docker restart $CONTAINER_NAME"
    echo "  • Inspect: docker inspect $CONTAINER_NAME"
else
    print_status "ERROR" "Container is not running properly"
    echo ""
    echo "To start the container:"
    echo "  docker-compose up -d"
    echo "  OR"
    echo "  docker start $CONTAINER_NAME"
fi

echo ""
echo "For detailed troubleshooting, see: DOCKER_GUIDE.md"
echo "============================================"
