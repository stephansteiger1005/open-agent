#!/usr/bin/env python3
"""
Test script for MCP server prompts.
Validates that all prompts are accessible and return valid content.
"""
import asyncio
import sys
from mcp_server import mcp


async def test_prompts():
    """Test all MCP prompts."""
    print("Testing MCP Server Prompts")
    print("=" * 60)
    
    # List prompts
    prompts = await mcp.list_prompts()
    print(f"\n✓ Found {len(prompts)} prompts:")
    for prompt in prompts:
        print(f"  - {prompt.name}")
    
    # Test analyze_weather
    print("\n1. Testing analyze_weather prompt...")
    result = await mcp.get_prompt("analyze_weather", {})
    assert len(result.messages) > 0, "analyze_weather should return messages"
    assert "get_weather" in result.messages[0].content.text, "Should reference get_weather tool"
    print("   ✓ analyze_weather works correctly")
    
    # Test review_user_profile
    print("\n2. Testing review_user_profile prompt...")
    result = await mcp.get_prompt("review_user_profile", {"focus_area": "skills"})
    assert len(result.messages) > 0, "review_user_profile should return messages"
    print("   ✓ review_user_profile works with focus area")
    
    # Test daily_briefing
    print("\n3. Testing daily_briefing prompt...")
    result = await mcp.get_prompt("daily_briefing", {})
    assert len(result.messages) > 0, "daily_briefing should return messages"
    assert "get_weather" in result.messages[0].content.text
    assert "get_user_info" in result.messages[0].content.text
    print("   ✓ daily_briefing references both tools")
    
    print("\n" + "=" * 60)
    print("✓ All prompt tests passed!")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(test_prompts())
    sys.exit(exit_code)
