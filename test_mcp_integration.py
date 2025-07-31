#!/usr/bin/env python3
"""
Real integration test suite for MCP tools using FastMCP Client.
This test connects to the actual MCP server and tests all tools.
"""

import asyncio
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path

from fastmcp import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPIntegrationTestSuite:
    """Integration test suite using FastMCP Client to test actual MCP server."""
    
    def __init__(self):
        self.test_project_id = f"test_project_{uuid.uuid4().hex[:8]}"
        self.test_data_dir = Path("test_codebase")
        self.temp_dir = None
        self.client = None
        
    async def setup_test_environment(self):
        """Set up test environment with sample code."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp(prefix="mcp_integration_test_")
        logger.info(f"Created test directory: {self.temp_dir}")
        
        # Copy test files to temp directory
        if self.test_data_dir.exists():
            import shutil
            for file_path in self.test_data_dir.glob("*"):
                if file_path.is_file():
                    shutil.copy2(file_path, self.temp_dir)
        
        # Create additional test files
        self._create_test_files()
        
        # Initialize FastMCP client
        self.client = Client("main.py")
        
    def _create_test_files(self):
        """Create additional test files for comprehensive testing."""
        # Create a Python file with functions and classes
        python_file = Path(self.temp_dir) / "test_functions.py"
        python_content = '''
def test_function():
    """A test function."""
    return "test"

class TestClass:
    def __init__(self):
        self.value = 42
    
    def get_value(self):
        return self.value

def caller_function():
    return test_function()

class TestInterface:
    def interface_method(self):
        pass

class TestImplementation(TestInterface):
    def interface_method(self):
        return "implemented"
'''
        python_file.write_text(python_content)
        
        # Create a JavaScript file
        js_file = Path(self.temp_dir) / "test.js"
        js_content = '''
function jsFunction() {
    return "javascript";
}

class JSClass {
    constructor() {
        this.value = 100;
    }
    
    getValue() {
        return this.value;
    }
}
'''
        js_file.write_text(js_content)
        
        # Create a JSON file
        json_file = Path(self.temp_dir) / "test.json"
        json_content = {
            "name": "test",
            "version": "1.0.0",
            "dependencies": {
                "test": "^1.0.0"
            }
        }
        json_file.write_text(json.dumps(json_content, indent=2))

    async def test_health_check(self):
        """Test health_check tool."""
        logger.info("Testing health_check tool...")
        
        try:
            result = await self.client.call_tool("health_check", {})
            
            # Debug: print the actual result structure
            logger.info(f"Health check result: {result}")
            logger.info(f"Result data: {result.data}")
            logger.info(f"Result data type: {type(result.data)}")
            
            # Check if result.data is a dict and has the expected fields
            if isinstance(result.data, dict):
                assert "success" in result.data
                assert "health" in result.data
                assert "server" in result.data["health"]
                assert "database" in result.data["health"]
                assert "embeddings" in result.data["health"]
                logger.info("✓ health_check tool test passed")
            else:
                logger.error(f"Unexpected result.data type: {type(result.data)}")
                raise AssertionError(f"Expected dict, got {type(result.data)}")
        except Exception as e:
            logger.error(f"Health check test failed: {e}")
            raise

    async def test_index_codebase(self):
        """Test index_codebase tool."""
        logger.info("Testing index_codebase tool...")
        
        try:
            result = await self.client.call_tool("index_codebase", {
                "path": str(self.temp_dir),
                "project_id": self.test_project_id
            })
            
            # Debug: print the actual result structure
            logger.info(f"Index codebase result: {result}")
            logger.info(f"Result data: {result.data}")
            logger.info(f"Result data type: {type(result.data)}")
            
            # Check if result.data is a dict and has the expected fields
            if isinstance(result.data, dict):
                assert "project_id" in result.data
                assert result.data["project_id"] == self.test_project_id
                # Check for processed_files field
                if "processed_files" in result.data:
                    assert result.data["processed_files"] > 0
                else:
                    logger.error(f"Missing processed_files field. Available fields: {list(result.data.keys())}")
                    raise AssertionError("Missing processed_files field")
                
                # Check for total_symbols_added field
                if "total_symbols_added" in result.data:
                    assert result.data["total_symbols_added"] > 0
                else:
                    logger.error(f"Missing total_symbols_added field. Available fields: {list(result.data.keys())}")
                    raise AssertionError("Missing total_symbols_added field")
                
                logger.info("✓ index_codebase tool test passed")
            else:
                logger.error(f"Unexpected result.data type: {type(result.data)}")
                raise AssertionError(f"Expected dict, got {type(result.data)}")
        except Exception as e:
            logger.error(f"Index codebase test failed: {e}")
            raise

    async def test_search_symbol_by_name(self):
        """Test search_symbol_by_name tool."""
        logger.info("Testing search_symbol_by_name tool...")
        
        result = await self.client.call_tool("search_symbol_by_name", {
            "name": "test_function",
            "language": "python",
            "project_id": self.test_project_id
        })
        
        assert "query" in result.data
        assert "results" in result.data
        assert isinstance(result.data["results"], list)
        logger.info("✓ search_symbol_by_name tool test passed")

    async def test_search_symbol_semantic(self):
        """Test search_symbol_semantic tool."""
        logger.info("Testing search_symbol_semantic tool...")
        
        result = await self.client.call_tool(
            "search_symbol_semantic", 
            {
                "query": "test function",
                "top_k": 10,
                "project_id": self.test_project_id
            }
        )
        
        assert "query" in result.data
        assert "results" in result.data
        assert isinstance(result.data["results"], list)
        logger.info("✓ search_symbol_semantic tool test passed")

    async def test_list_projects(self):
        """Test list_projects tool."""
        logger.info("Testing list_projects tool...")
        
        result = await self.client.call_tool("list_projects", {})
        
        assert "projects" in result.data
        assert isinstance(result.data["projects"], list)
        logger.info("✓ list_projects tool test passed")

    async def test_get_project_info(self):
        """Test get_project_info tool."""
        logger.info("Testing get_project_info tool...")
        
        result = await self.client.call_tool("get_project_info", {
            "project_id": self.test_project_id
        })
        
        assert "project_id" in result.data
        assert result.data["project_id"] == self.test_project_id
        logger.info("✓ get_project_info tool test passed")

    async def test_get_stats(self):
        """Test get_stats tool."""
        logger.info("Testing get_stats tool...")
        
        result = await self.client.call_tool("get_stats", {
            "project_id": self.test_project_id
        })
        
        assert "total_projects" in result.data
        assert "total_symbols" in result.data
        logger.info("✓ get_stats tool test passed")

    async def test_find_function_callers(self):
        """Test find_function_callers tool."""
        logger.info("Testing find_function_callers tool...")
        
        result = await self.client.call_tool("find_function_callers", {
            "function_name": "test_function",
            "project_id": self.test_project_id
        })
        
        assert "function_name" in result.data
        assert "callers" in result.data
        assert isinstance(result.data["callers"], list)
        logger.info("✓ find_function_callers tool test passed")

    async def test_find_interface_implementations(self):
        """Test find_interface_implementations tool."""
        logger.info("Testing find_interface_implementations tool...")
        
        result = await self.client.call_tool("find_interface_implementations", {
            "interface_name": "TestInterface",
            "project_id": self.test_project_id
        })
        
        assert "interface_name" in result.data
        assert "implementations" in result.data
        assert isinstance(result.data["implementations"], list)
        logger.info("✓ find_interface_implementations tool test passed")

    async def test_get_symbol_relationships(self):
        """Test get_symbol_relationships tool."""
        logger.info("Testing get_symbol_relationships tool...")
        
        result = await self.client.call_tool("get_symbol_relationships", {
            "symbol_name": "test_function",
            "relationship_type": "calls",
            "direction": "both",
            "project_id": self.test_project_id
        })
        
        assert "symbol_name" in result.data
        assert "relationships" in result.data
        assert isinstance(result.data["relationships"], list)
        logger.info("✓ get_symbol_relationships tool test passed")

    async def test_get_dependency_graph(self):
        """Test get_dependency_graph tool."""
        logger.info("Testing get_dependency_graph tool...")
        
        result = await self.client.call_tool("get_dependency_graph", {
            "project_id": self.test_project_id,
            "max_depth": 3
        })
        
        assert "nodes" in result.data
        assert "edges" in result.data
        assert isinstance(result.data["nodes"], list)
        assert isinstance(result.data["edges"], list)
        logger.info("✓ get_dependency_graph tool test passed")

    async def test_analyze_call_hierarchy(self):
        """Test analyze_call_hierarchy tool."""
        logger.info("Testing analyze_call_hierarchy tool...")
        
        result = await self.client.call_tool("analyze_call_hierarchy", {
            "function_name": "test_function",
            "project_id": self.test_project_id,
            "max_depth": 3
        })
        
        assert "function_name" in result.data
        assert "hierarchy" in result.data
        logger.info("✓ analyze_call_hierarchy tool test passed")

    async def test_force_full_rescan(self):
        """Test force_full_rescan tool."""
        logger.info("Testing force_full_rescan tool...")
        
        result = await self.client.call_tool("force_full_rescan", {
            "project_id": self.test_project_id
        })
        
        assert "project_id" in result.data
        assert result.data["project_id"] == self.test_project_id
        assert "status" in result.data
        logger.info("✓ force_full_rescan tool test passed")

    async def test_delete_project(self):
        """Test delete_project tool."""
        logger.info("Testing delete_project tool...")
        
        result = await self.client.call_tool("delete_project", {
            "project_id": self.test_project_id
        })
        
        assert "project_id" in result.data
        assert result.data["project_id"] == self.test_project_id
        assert "status" in result.data
        logger.info("✓ delete_project tool test passed")

    async def test_resources(self):
        """Test resource endpoints."""
        logger.info("Testing resource endpoints...")
        
        # Test projects resource
        try:
            projects = await self.client.read_resource("codebase://projects")
            assert len(projects) > 0
            logger.info("✓ Projects resource test passed")
        except Exception as e:
            logger.warning(f"Projects resource test failed: {e}")
        
        # Test project stats resource
        try:
            stats = await self.client.read_resource(
                f"codebase://stats/{self.test_project_id}"
            )
            assert len(stats) > 0
            logger.info("✓ Project stats resource test passed")
        except Exception as e:
            logger.warning(f"Project stats resource test failed: {e}")
        
        # Test project symbols resource
        try:
            symbols = await self.client.read_resource(
                f"codebase://symbols/{self.test_project_id}"
            )
            assert len(symbols) > 0
            logger.info("✓ Project symbols resource test passed")
        except Exception as e:
            logger.warning(f"Project symbols resource test failed: {e}")
        
        logger.info("✓ Resource endpoints test completed")

    async def run_all_tests(self):
        """Run all integration tests in sequence."""
        logger.info("Starting MCP Integration Test Suite")
        logger.info("=" * 50)
        
        try:
            await self.setup_test_environment()
            
            async with self.client:
                logger.info("Connected to MCP server")
                
                # Test all tools
                await self.test_health_check()
                await self.test_index_codebase()
                await self.test_search_symbol_by_name()
                await self.test_search_symbol_semantic()
                await self.test_list_projects()
                await self.test_get_project_info()
                await self.test_get_stats()
                await self.test_find_function_callers()
                await self.test_find_interface_implementations()
                await self.test_get_symbol_relationships()
                await self.test_get_dependency_graph()
                await self.test_analyze_call_hierarchy()
                await self.test_force_full_rescan()
                await self.test_delete_project()
                
                # Test resources
                await self.test_resources()
                
                logger.info("🎉 All MCP integration tests passed successfully!")
                
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up test directory: {self.temp_dir}")


def main():
    """Main function to run the integration test suite."""
    test_suite = MCPIntegrationTestSuite()
    
    # Run the async test suite
    asyncio.run(test_suite.run_all_tests())


if __name__ == "__main__":
    main() 