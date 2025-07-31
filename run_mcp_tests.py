#!/usr/bin/env python3
"""
Test runner for MCP tools test suite.
This script demonstrates how to run the comprehensive test suite.
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from test_mcp_tools import MCPToolsTestSuite
except ImportError:
    print("Error: Could not import test_mcp_tools module")
    sys.exit(1)


def run_tests():
    """Run the MCP tools test suite."""
    print("🚀 Starting MCP Tools Test Suite")
    print("=" * 50)
    
    test_suite = MCPToolsTestSuite()
    
    try:
        test_suite.run_all_tests()
        print("\n✅ All tests completed successfully!")
        return True
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        return False


def main():
    """Main function."""
    print("MCP Tools Test Runner")
    print("This will test all MCP tools defined in server-info.json")
    print()
    
    # Run the tests
    success = run_tests()
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test suite failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 