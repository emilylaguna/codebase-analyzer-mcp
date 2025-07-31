#!/usr/bin/env python3
"""
Test to verify that unknown symbols are being filtered out by parsers.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import the parser
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.json_parser import JSONParser
from parsers.python_parser import PythonParser
from parsers.base_parser import BaseParser


def test_unknown_symbol_filtering():
    """Test that unknown symbols are filtered out."""
    print("Testing unknown symbol filtering...")
    
    # Test JSON parser
    json_parser = JSONParser()
    
    # Test with a known symbol type
    known_type = json_parser._get_symbol_type('object', 'json')
    assert known_type == 'object', f"Expected 'object', got {known_type}"
    
    # Test with an unknown symbol type
    unknown_type = json_parser._get_symbol_type('unknown_symbol_type', 'json')
    assert unknown_type is None, f"Expected None, got {unknown_type}"
    
    # Test Python parser
    python_parser = PythonParser()
    
    # Test with a known symbol type
    known_type = python_parser._get_symbol_type('function', 'python')
    assert known_type == 'function', f"Expected 'function', got {known_type}"
    
    # Test with an unknown symbol type
    unknown_type = python_parser._get_symbol_type('unknown_symbol_type', 'python')
    assert unknown_type is None, f"Expected None, got {unknown_type}"
    
    # Test base parser
    base_parser = BaseParser()
    
    # Test with a known symbol type
    known_type = base_parser._get_symbol_type('class', 'python')
    assert known_type == 'class', f"Expected 'class', got {known_type}"
    
    # Test with an unknown symbol type
    unknown_type = base_parser._get_symbol_type('unknown_symbol_type', 'python')
    assert unknown_type is None, f"Expected None, got {unknown_type}"
    
    print("✓ Unknown symbol filtering works correctly")


def test_symbol_extraction_with_unknown_symbols():
    """Test that symbols with unknown types are filtered out during extraction."""
    print("Testing symbol extraction with unknown symbols...")
    
    # Create a mock node-like object for testing
    class MockNode:
        def __init__(self, text, start_point, end_point):
            self.text = text.encode('utf-8')
            self.start_point = start_point
            self.end_point = end_point
    
    # Test with base parser
    base_parser = BaseParser()
    
    # Create a mock node with unknown symbol type
    unknown_node = MockNode("test_unknown", (0, 0), (0, 12))
    unknown_symbol = base_parser._extract_symbol_info(
        unknown_node, 'completely_unknown_symbol_type', ['test_unknown'], 'python', 'test.py'
    )
    
    # This should return None because 'completely_unknown_symbol_type' is not in the base parser's mapping
    assert unknown_symbol is None, f"Expected None for unknown symbol type, got {unknown_symbol}"
    
    # Test with a known symbol type in base parser
    known_node = MockNode("TestClass", (0, 0), (0, 9))
    known_symbol = base_parser._extract_symbol_info(
        known_node, 'class', ['class TestClass'], 'python', 'test.py'
    )
    
    # This should work because 'class' is in the base parser's mapping
    assert known_symbol is not None, "Expected symbol info for known type"
    assert known_symbol['symbol_type'] == 'class', f"Expected 'class', got {known_symbol['symbol_type']}"
    
    print("✓ Symbol extraction correctly filters unknown symbols")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Unknown Symbol Filtering Test Suite")
    print("=" * 60)
    
    try:
        test_unknown_symbol_filtering()
        test_symbol_extraction_with_unknown_symbols()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 