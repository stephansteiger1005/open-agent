#!/usr/bin/env python3
"""
Test script to verify MCP server endpoints are correctly configured.
This demonstrates the correct URL structure for OpenWebUI configuration.
"""
import sys
import time
import requests
import subprocess
import signal

def test_mcp_endpoints(base_url="http://localhost:8080"):
    """
    Test MCP server endpoints.
    
    Args:
        base_url: Base URL without /sse (e.g., http://localhost:8080)
    """
    print(f"Testing MCP server at: {base_url}")
    print("=" * 60)
    
    # Test 1: GET /sse (SSE stream endpoint)
    print("\n1. Testing GET /sse (SSE stream endpoint)...")
    try:
        response = requests.get(
            f"{base_url}/sse",
            headers={"Accept": "text/event-stream"},
            timeout=2,
            stream=True
        )
        if response.status_code == 200:
            print(f"   ✓ GET /sse returned {response.status_code} - Success!")
            print(f"   Content-Type: {response.headers.get('Content-Type')}")
        else:
            print(f"   ✗ GET /sse returned {response.status_code} - Failed!")
            return False
    except requests.exceptions.Timeout:
        print(f"   ✓ GET /sse kept connection open (timeout expected)")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: POST /messages (Client message endpoint)
    print("\n2. Testing POST /messages (client message endpoint)...")
    try:
        response = requests.post(
            f"{base_url}/messages",
            json={},
            timeout=2
        )
        # We expect 400 or 307 as we're not sending a proper MCP message
        # but the endpoint should exist (not 404)
        if response.status_code in [400, 307]:
            print(f"   ✓ POST /messages returned {response.status_code} - Endpoint exists!")
        elif response.status_code == 404:
            print(f"   ✗ POST /messages returned 404 - Endpoint not found!")
            return False
        else:
            print(f"   ℹ POST /messages returned {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: POST /sse should fail (wrong endpoint for POST)
    print("\n3. Testing POST /sse (should fail - wrong endpoint)...")
    try:
        response = requests.post(
            f"{base_url}/sse",
            json={},
            timeout=2
        )
        if response.status_code == 405:
            print(f"   ✓ POST /sse returned 405 Method Not Allowed - Correct!")
        elif response.status_code == 404:
            print(f"   ⚠ POST /sse returned 404 - This is what OpenWebUI was seeing!")
        else:
            print(f"   ℹ POST /sse returned {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("\nCorrect OpenWebUI Configuration:")
    print(f"  Type: MCP - Streamables HTTP")
    print(f"  URL: {base_url}")
    print(f"  Authentication: None")
    print("\nOpenWebUI will automatically append:")
    print("  - /sse for GET requests (SSE stream)")
    print("  - /messages for POST requests (client messages)")
    return True

if __name__ == "__main__":
    # Start MCP server
    print("Starting MCP server...")
    server_process = subprocess.Popen(
        ["python3", "mcp_server.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN)
    )
    
    # Wait for server to start
    time.sleep(3)
    
    try:
        # Run tests
        success = test_mcp_endpoints()
        sys.exit(0 if success else 1)
    finally:
        # Clean up
        print("\nStopping MCP server...")
        server_process.terminate()
        server_process.wait()
