#!/usr/bin/env python3
"""
Test script to verify the MCP to OpenAPI proxy endpoints.
This demonstrates how OpenWebUI can use the proxy via standard REST API calls.
"""
import json
import sys
import requests


def test_proxy_endpoints(base_url="http://localhost:8081"):
    """
    Test MCP to OpenAPI proxy endpoints.
    
    Args:
        base_url: Base URL for the proxy (e.g., http://localhost:8081)
    """
    print(f"Testing MCP to OpenAPI Proxy at: {base_url}")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing GET / (root endpoint)...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ GET / returned {response.status_code}")
            print(f"   Name: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"   ✗ GET / returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: List tools
    print("\n2. Testing GET /tools (list available tools)...")
    try:
        response = requests.get(f"{base_url}/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"   ✓ GET /tools returned {response.status_code}")
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool['name']}: {tool['description']}")
        else:
            print(f"   ✗ GET /tools returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Call get_weather tool
    print("\n3. Testing POST /tools/get_weather (call weather tool)...")
    try:
        response = requests.post(
            f"{base_url}/tools/get_weather",
            json={"arguments": {}},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ POST /tools/get_weather returned {response.status_code}")
            if 'content' in data and len(data['content']) > 0:
                weather_data = json.loads(data['content'][0]['text'])
                print(f"   Location: {weather_data.get('location')}")
                print(f"   Temperature: {weather_data.get('temperature')}°{weather_data.get('unit', 'F')[0]}")
                print(f"   Conditions: {weather_data.get('conditions')}")
        else:
            print(f"   ✗ POST /tools/get_weather returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Call get_user_info tool
    print("\n4. Testing POST /tools/get_user_info (call user info tool)...")
    try:
        response = requests.post(
            f"{base_url}/tools/get_user_info",
            json={"arguments": {}},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ POST /tools/get_user_info returned {response.status_code}")
            if 'content' in data and len(data['content']) > 0:
                user_data = json.loads(data['content'][0]['text'])
                print(f"   Name: {user_data.get('name')}")
                print(f"   Role: {user_data.get('role')}")
                print(f"   Department: {user_data.get('department')}")
        else:
            print(f"   ✗ POST /tools/get_user_info returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 5: Get OpenAPI specification
    print("\n5. Testing GET /openapi.json (OpenAPI specification)...")
    try:
        response = requests.get(f"{base_url}/openapi.json", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ GET /openapi.json returned {response.status_code}")
            print(f"   OpenAPI version: {data.get('openapi')}")
            print(f"   Title: {data.get('info', {}).get('title')}")
            print(f"   Paths: {len(data.get('paths', {}))} endpoints")
        else:
            print(f"   ✗ GET /openapi.json returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 6: Health check
    print("\n6. Testing GET /health (health check)...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ GET /health returned {response.status_code}")
            print(f"   Status: {data.get('status')}")
            print(f"   MCP Connected: {data.get('mcp_connected')}")
            print(f"   Tools Count: {data.get('tools_count')}")
        else:
            print(f"   ✗ GET /health returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("\nOpenWebUI Configuration (OpenAPI Method):")
    print("  Type: OpenAPI")
    print(f"  URL: {base_url}/openapi.json")
    print("  Authentication: None")
    print("\nThe proxy exposes the MCP tools as standard REST endpoints,")
    print("making them accessible to any OpenAPI-compatible client.")
    print("\nYou can also view the interactive API docs at:")
    print(f"  {base_url}/docs")
    return True


if __name__ == "__main__":
    try:
        success = test_proxy_endpoints()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(1)
