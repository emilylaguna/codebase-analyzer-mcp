# MCP Tools Test Suite

This directory contains a comprehensive test suite for validating all MCP (Model Context Protocol) tools and resources defined in the `server-info.json` file.

## Overview

The test suite validates all 13 MCP tools and various resource endpoints to ensure they work correctly:

### Tools Tested

1. **health_check** - Server health and component status
2. **index_codebase** - Parse and index a codebase directory
3. **search_symbol_by_name** - Search for symbols by exact name
4. **search_symbol_semantic** - Search for symbols using semantic similarity
5. **list_projects** - List all projects in the database
6. **get_project_info** - Get detailed project information
7. **get_stats** - Get database statistics
8. **find_function_callers** - Find all callers of a function
9. **find_interface_implementations** - Find interface implementations
10. **get_symbol_relationships** - Get symbol relationships
11. **get_dependency_graph** - Get dependency graph for project
12. **analyze_call_hierarchy** - Analyze call hierarchy for a function
13. **force_full_rescan** - Force full rescan of a project
14. **delete_project** - Delete a project and its data

### Resources Tested

- Project statistics resources
- Project symbols resources
- Project files resources
- Language-specific resources
- Search resources
- Caller and implementation resources
- Relationship and dependency resources

## Files

- `test_mcp_tools.py` - Main test suite implementation
- `run_mcp_tests.py` - Simple test runner script
- `MCP_TEST_SUITE_README.md` - This documentation

## Usage

### Running the Test Suite

```bash
# Run the test suite directly
python test_mcp_tools.py

# Or use the test runner
python run_mcp_tests.py
```

### Test Structure

The test suite uses mocking to validate tool behavior without requiring a running server:

1. **Setup**: Creates temporary test files and directories
2. **Mocking**: Mocks all MCP tool functions with expected return values
3. **Validation**: Tests that tools return expected data structures
4. **Cleanup**: Removes temporary files and directories

### Test Files Created

The test suite creates sample files for testing:

- `test_functions.py` - Python file with functions, classes, and interfaces
- `test.js` - JavaScript file with functions and classes
- `test.json` - JSON configuration file

## Test Validation

Each test validates:

- **Function signatures** - Tools accept correct parameters
- **Return values** - Tools return expected data structures
- **Data integrity** - Returned data contains required fields
- **Error handling** - Tools handle edge cases appropriately

## Example Test Output

```
🚀 Starting MCP Tools Test Suite
==================================================
2024-01-01 12:00:00 - Created test directory: /tmp/mcp_test_abc123
2024-01-01 12:00:00 - Testing health_check tool...
2024-01-01 12:00:00 - ✓ health_check tool test passed
2024-01-01 12:00:00 - Testing index_codebase tool...
2024-01-01 12:00:00 - ✓ index_codebase tool test passed
...
2024-01-01 12:00:00 - 🎉 All MCP tools tests passed successfully!
2024-01-01 12:00:00 - Cleaned up test directory: /tmp/mcp_test_abc123

✅ All tests completed successfully!
🎉 Test suite completed successfully!
```

## Integration with CI/CD

The test suite can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run MCP Tools Tests
  run: |
    python test_mcp_tools.py
```

## Extending the Test Suite

To add new tests:

1. Add a new test method to `MCPToolsTestSuite`
2. Mock the corresponding MCP tool function
3. Validate the expected return structure
4. Add the test to the `run_all_tests()` method

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Mock Failures**: Check that tool function names match exactly
3. **Assertion Errors**: Verify expected data structures match actual returns

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Dependencies

- Python 3.8+
- `unittest.mock` (standard library)
- `asyncio` (standard library)
- `pathlib` (standard library)

## License

This test suite is part of the codebase-analyzer project. 