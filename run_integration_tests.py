#!/usr/bin/env python3
"""
Integration test runner for MCP tools using FastMCP Client.
This script runs real integration tests against the actual MCP server.
"""

import asyncio
import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from test_mcp_integration import MCPIntegrationTestSuite
except ImportError as e:
    print(f"Error: Could not import test_mcp_integration module: {e}")
    sys.exit(1)


def run_tests():
    """Run the MCP integration test suite."""
    print("🚀 Starting MCP Integration Test Suite")
    print("This will test all MCP tools against the actual server")
    print("=" * 60)
    
    test_suite = MCPIntegrationTestSuite()
    
    try:
        asyncio.run(test_suite.run_all_tests())
        print("\n✅ All integration tests completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Integration test suite failed: {e}")
        return False


def main():
    """Main function."""
    print("MCP Integration Test Runner")
    print("This connects to the actual MCP server and tests all tools")
    print()
    
    # Run the tests
    success = run_tests()
    
    if success:
        print("\n🎉 Integration test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Integration test suite failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 