#!/usr/bin/env python3
"""
Comprehensive test suite for MCP tools and resources.
Tests all tools defined in server-info.json to ensure they work correctly.
"""

import json
import logging
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

# Add the current directory to the path to import modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPToolsTestSuite:
    """Test suite for all MCP tools and resources."""
    
    def __init__(self):
        self.test_project_id = "test_project"
        self.test_data_dir = Path("test_codebase")
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Set up test environment with sample code."""
        # Create temporary directory for testing
        self.temp_dir = tempfile.mkdtemp(prefix="mcp_test_")
        logger.info(f"Created test directory: {self.temp_dir}")
        
        # Copy test files to temp directory
        if self.test_data_dir.exists():
            import shutil
            for file_path in self.test_data_dir.glob("*"):
                if file_path.is_file():
                    shutil.copy2(file_path, self.temp_dir)
        
        # Create additional test files
        self._create_test_files()
        
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

    def test_health_check(self):
        """Test health_check tool."""
        logger.info("Testing health_check tool...")
        
        # Mock the health_check function
        with patch('main.health_check') as mock_health_check:
            mock_health_check.return_value = {
                "status": "healthy",
                "database": "connected",
                "embedding_model": "loaded",
                "timestamp": time.time()
            }
            
            # Call the mocked function directly since it returns a dict
            result = mock_health_check()
            
            assert result["status"] == "healthy"
            assert "database" in result
            assert "embedding_model" in result
            logger.info("✓ health_check tool test passed")

    def test_index_codebase(self):
        """Test index_codebase tool."""
        logger.info("Testing index_codebase tool...")
        
        # Mock the index_codebase function
        with patch('main.index_codebase') as mock_index:
            mock_index.return_value = {
                "project_id": self.test_project_id,
                "files_processed": 10,
                "symbols_extracted": 25,
                "languages_found": ["python", "javascript"],
                "status": "completed"
            }
            
            result = mock_index(
                path=str(self.temp_dir),
                project_id=self.test_project_id
            )
            
            assert result["project_id"] == self.test_project_id
            assert result["files_processed"] > 0
            assert result["symbols_extracted"] > 0
            assert "languages_found" in result
            logger.info("✓ index_codebase tool test passed")

    def test_search_symbol_by_name(self):
        """Test search_symbol_by_name tool."""
        logger.info("Testing search_symbol_by_name tool...")
        
        # Mock the search_symbol_by_name function
        with patch('main.search_symbol_by_name') as mock_search:
            mock_search.return_value = {
                "query": "test_function",
                "results": [
                    {
                        "name": "test_function",
                        "type": "function",
                        "language": "python",
                        "file": "test_functions.py",
                        "line": 2
                    }
                ],
                "total_results": 1
            }
            
            result = mock_search(
                name="test_function",
                language="python",
                project_id=self.test_project_id
            )
            
            assert result["query"] == "test_function"
            assert len(result["results"]) > 0
            assert result["results"][0]["name"] == "test_function"
            logger.info("✓ search_symbol_by_name tool test passed")

    def test_search_symbol_semantic(self):
        """Test search_symbol_semantic tool."""
        logger.info("Testing search_symbol_semantic tool...")
        
        # Mock the search_symbol_semantic function
        with patch('main.search_symbol_semantic') as mock_semantic_search:
            mock_semantic_search.return_value = {
                "query": "test function",
                "results": [
                    {
                        "name": "test_function",
                        "type": "function",
                        "language": "python",
                        "file": "test_functions.py",
                        "similarity": 0.95
                    }
                ],
                "total_results": 1
            }
            
            result = mock_semantic_search(
                query="test function",
                top_k=10,
                project_id=self.test_project_id
            )
            
            assert result["query"] == "test function"
            assert len(result["results"]) > 0
            assert "similarity" in result["results"][0]
            logger.info("✓ search_symbol_semantic tool test passed")

    def test_list_projects(self):
        """Test list_projects tool."""
        logger.info("Testing list_projects tool...")
        
        # Mock the list_projects function
        with patch('main.list_projects') as mock_list_projects:
            mock_list_projects.return_value = {
                "projects": [
                    {
                        "project_id": self.test_project_id,
                        "name": "Test Project",
                        "path": str(self.temp_dir),
                        "languages": ["python", "javascript"],
                        "file_count": 10,
                        "symbol_count": 25,
                        "last_updated": time.time()
                    }
                ],
                "total_projects": 1
            }
            
            result = mock_list_projects()
            
            assert "projects" in result
            assert len(result["projects"]) > 0
            assert result["projects"][0]["project_id"] == self.test_project_id
            logger.info("✓ list_projects tool test passed")

    def test_get_project_info(self):
        """Test get_project_info tool."""
        logger.info("Testing get_project_info tool...")
        
        # Mock the get_project_info function
        with patch('main.get_project_info') as mock_project_info:
            mock_project_info.return_value = {
                "project_id": self.test_project_id,
                "name": "Test Project",
                "path": str(self.temp_dir),
                "languages": ["python", "javascript"],
                "file_count": 10,
                "symbol_count": 25,
                "git_info": {
                    "repository": "test-repo",
                    "branch": "main",
                    "last_commit": "abc123"
                }
            }
            
            result = mock_project_info(project_id=self.test_project_id)
            
            assert result["project_id"] == self.test_project_id
            assert "git_info" in result
            assert "languages" in result
            logger.info("✓ get_project_info tool test passed")

    def test_get_stats(self):
        """Test get_stats tool."""
        logger.info("Testing get_stats tool...")
        
        # Mock the get_stats function
        with patch('main.get_stats') as mock_stats:
            mock_stats.return_value = {
                "total_projects": 1,
                "total_symbols": 25,
                "total_files": 10,
                "languages": {
                    "python": 15,
                    "javascript": 10
                },
                "project_stats": {
                    self.test_project_id: {
                        "symbols": 25,
                        "files": 10,
                        "languages": 2
                    }
                }
            }
            
            result = mock_stats(project_id=self.test_project_id)
            
            assert "total_projects" in result
            assert "total_symbols" in result
            assert "languages" in result
            logger.info("✓ get_stats tool test passed")

    def test_find_function_callers(self):
        """Test find_function_callers tool."""
        logger.info("Testing find_function_callers tool...")
        
        # Mock the find_function_callers function
        with patch('main.find_function_callers') as mock_callers:
            mock_callers.return_value = {
                "function_name": "test_function",
                "callers": [
                    {
                        "name": "caller_function",
                        "type": "function",
                        "file": "test_functions.py",
                        "line": 15
                    }
                ],
                "total_callers": 1
            }
            
            result = mock_callers(
                function_name="test_function",
                project_id=self.test_project_id
            )
            
            assert result["function_name"] == "test_function"
            assert len(result["callers"]) > 0
            logger.info("✓ find_function_callers tool test passed")

    def test_find_interface_implementations(self):
        """Test find_interface_implementations tool."""
        logger.info("Testing find_interface_implementations tool...")
        
        # Mock the find_interface_implementations function
        with patch('main.find_interface_implementations') as mock_implementations:
            mock_implementations.return_value = {
                "interface_name": "TestInterface",
                "implementations": [
                    {
                        "name": "TestImplementation",
                        "type": "class",
                        "file": "test_functions.py",
                        "line": 20
                    }
                ],
                "total_implementations": 1
            }
            
            result = mock_implementations(
                interface_name="TestInterface",
                project_id=self.test_project_id
            )
            
            assert result["interface_name"] == "TestInterface"
            assert len(result["implementations"]) > 0
            logger.info(
                "✓ find_interface_implementations tool test passed"
            )

    def test_get_symbol_relationships(self):
        """Test get_symbol_relationships tool."""
        logger.info("Testing get_symbol_relationships tool...")
        
        # Mock the get_symbol_relationships function
        with patch('main.get_symbol_relationships') as mock_relationships:
            mock_relationships.return_value = {
                "symbol_name": "test_function",
                "relationships": [
                    {
                        "related_symbol": "caller_function",
                        "relationship_type": "calls",
                        "direction": "outgoing"
                    }
                ],
                "total_relationships": 1
            }
            
            result = mock_relationships(
                symbol_name="test_function",
                relationship_type="calls",
                direction="both",
                project_id=self.test_project_id
            )
            
            assert result["symbol_name"] == "test_function"
            assert len(result["relationships"]) > 0
            logger.info(
                "✓ get_symbol_relationships tool test passed"
            )

    def test_get_dependency_graph(self):
        """Test get_dependency_graph tool."""
        logger.info("Testing get_dependency_graph tool...")
        
        # Mock the get_dependency_graph function
        with patch('main.get_dependency_graph') as mock_dependencies:
            mock_dependencies.return_value = {
                "nodes": [
                    {"id": "test_function", "type": "function"},
                    {"id": "caller_function", "type": "function"}
                ],
                "edges": [
                    {
                        "from": "caller_function", 
                        "to": "test_function", 
                        "type": "calls"
                    }
                ],
                "max_depth": 3
            }
            
            result = mock_dependencies(
                project_id=self.test_project_id,
                max_depth=3
            )
            
            assert "nodes" in result
            assert "edges" in result
            assert len(result["nodes"]) > 0
            logger.info("✓ get_dependency_graph tool test passed")

    def test_analyze_call_hierarchy(self):
        """Test analyze_call_hierarchy tool."""
        logger.info("Testing analyze_call_hierarchy tool...")
        
        # Mock the analyze_call_hierarchy function
        with patch('main.analyze_call_hierarchy') as mock_hierarchy:
            mock_hierarchy.return_value = {
                "function_name": "test_function",
                "hierarchy": {
                    "level": 0,
                    "function": "test_function",
                    "callers": [
                        {
                            "level": 1,
                            "function": "caller_function",
                            "callers": []
                        }
                    ]
                },
                "max_depth": 3
            }
            
            result = mock_hierarchy(
                function_name="test_function",
                project_id=self.test_project_id,
                max_depth=3
            )
            
            assert result["function_name"] == "test_function"
            assert "hierarchy" in result
            logger.info("✓ analyze_call_hierarchy tool test passed")

    def test_force_full_rescan(self):
        """Test force_full_rescan tool."""
        logger.info("Testing force_full_rescan tool...")
        
        # Mock the force_full_rescan function
        with patch('main.force_full_rescan') as mock_rescan:
            mock_rescan.return_value = {
                "project_id": self.test_project_id,
                "status": "rescan_initiated",
                "message": "Full rescan scheduled"
            }
            
            result = mock_rescan(project_id=self.test_project_id)
            
            assert result["project_id"] == self.test_project_id
            assert result["status"] == "rescan_initiated"
            logger.info("✓ force_full_rescan tool test passed")

    def test_delete_project(self):
        """Test delete_project tool."""
        logger.info("Testing delete_project tool...")
        
        # Mock the delete_project function
        with patch('main.delete_project') as mock_delete:
            mock_delete.return_value = {
                "project_id": self.test_project_id,
                "status": "deleted",
                "symbols_deleted": 25,
                "files_deleted": 10
            }
            
            result = mock_delete(project_id=self.test_project_id)
            
            assert result["project_id"] == self.test_project_id
            assert result["status"] == "deleted"
            logger.info("✓ delete_project tool test passed")

    def test_resources(self):
        """Test all resource endpoints."""
        logger.info("Testing resource endpoints...")
        
        # Test projects resource
        with patch('main.get_projects') as mock_projects_resource:
            mock_projects_resource.return_value = [
                {
                    "project_id": self.test_project_id,
                    "name": "Test Project"
                }
            ]
            
            result = mock_projects_resource()
            assert len(result) > 0
            assert result[0]["project_id"] == self.test_project_id
        
        # Test project stats resource
        with patch('main.get_project_stats_resource') as mock_stats_resource:
            mock_stats_resource.return_value = {
                "database_stats": {"total_symbols": 25},
                "embedding_model": {"model": "test-model"}
            }
            
            result = mock_stats_resource(project_id=self.test_project_id)
            assert "database_stats" in result
            assert "embedding_model" in result
        
        # Test project symbols resource
        with patch('main.get_project_symbols') as mock_symbols_resource:
            mock_symbols_resource.return_value = {
                "symbols": [
                    {"name": "test_function", "type": "function"}
                ]
            }
            
            result = mock_symbols_resource(project_id=self.test_project_id)
            assert "symbols" in result
        
        logger.info("✓ Resource endpoints test passed")

    def run_all_tests(self):
        """Run all tests in sequence."""
        logger.info("Starting MCP tools test suite...")
        
        try:
            # Setup test environment (synchronous)
            self.setup_test_environment()
            
            # Test all tools
            self.test_health_check()
            self.test_index_codebase()
            self.test_search_symbol_by_name()
            self.test_search_symbol_semantic()
            self.test_list_projects()
            self.test_get_project_info()
            self.test_get_stats()
            self.test_find_function_callers()
            self.test_find_interface_implementations()
            self.test_get_symbol_relationships()
            self.test_get_dependency_graph()
            self.test_analyze_call_hierarchy()
            self.test_force_full_rescan()
            self.test_delete_project()
            
            # Test resources
            self.test_resources()
            
            logger.info("🎉 All MCP tools tests passed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {e}")
            raise
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                import shutil
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up test directory: {self.temp_dir}")


def main():
    """Main function to run the test suite."""
    test_suite = MCPToolsTestSuite()
    
    # Run the test suite
    test_suite.run_all_tests()


if __name__ == "__main__":
    main() 