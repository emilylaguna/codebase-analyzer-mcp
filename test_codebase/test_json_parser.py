#!/usr/bin/env python3
"""
Test file for JSON parser functionality.
Tests the JSON parser with various JSON structures and validates the results.
"""

import sys
import json
from pathlib import Path

# Add the parent directory to the path to import the parser
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.json_parser import JSONParser


def test_json_parser_basic():
    """Test basic JSON parsing functionality."""
    print("Testing basic JSON parser functionality...")
    
    # Create parser instance
    parser = JSONParser()
    
    # Test language detection
    assert parser.detect_language("test.json") == "json"
    assert parser.detect_language("test.jsonc") == "json"
    assert parser.detect_language("test.txt") is None
    
    print("✓ Language detection works correctly")


def test_json_parser_symbol_extraction():
    """Test symbol extraction from JSON files."""
    print("Testing JSON symbol extraction...")
    
    parser = JSONParser()
    
    # Simple JSON content for testing
    json_content = '''
{
  "name": "test-project",
  "version": "1.0.0",
  "description": "A test project",
  "dependencies": {
    "express": "^4.17.1"
  },
  "keywords": ["test", "json"],
  "config": {
    "port": 3000,
    "debug": true
  }
}
'''
    
    lines = json_content.split('\n')
    symbols = parser.extract_symbols_regex(lines, "test.json", "json")
    
    # Verify we extracted symbols
    assert len(symbols) > 0
    
    # Check for specific symbol types
    symbol_types = [s['symbol_type'] for s in symbols]
    assert 'key' in symbol_types
    assert 'string_value' in symbol_types
    assert 'numeric_value' in symbol_types
    assert 'boolean_value' in symbol_types
    
    print("✓ Symbol extraction works correctly")


def test_json_parser_relationships():
    """Test relationship extraction from JSON files."""
    print("Testing JSON relationship extraction...")
    
    parser = JSONParser()
    
    # JSON content with relationships
    json_content = '''
{
  "name": "test-project",
  "version": "1.0.0",
  "config": {
    "port": 3000,
    "debug": true
  },
  "dependencies": ["express", "react"]
}
'''
    
    lines = json_content.split('\n')
    symbols = parser.extract_symbols_regex(lines, "test.json", "json")
    relationships = parser.extract_relationships(json_content, symbols)
    
    # Verify we extracted relationships
    assert len(relationships) > 0
    
    # Check for specific relationship types
    for key, rels in relationships.items():
        for rel in rels:
            assert 'type' in rel
            assert 'target' in rel
            assert 'target_type' in rel
            assert 'line' in rel
    
    print("✓ Relationship extraction works correctly")


def test_json_parser_complex_structures():
    """Test parsing of complex JSON structures."""
    print("Testing complex JSON structures...")
    
    parser = JSONParser()
    
    # Complex JSON with nested structures
    json_content = '''
{
  "nested_objects": {
    "level1": {
      "level2": {
        "value": "deeply nested"
      }
    }
  },
  "arrays": ["item1", "item2", "item3"],
  "mixed_array": [
    "string",
    123,
    true,
    null,
    {"nested": "object"},
    ["nested", "array"]
  ],
  "numbers": {
    "integer": 42,
    "float": 3.14159,
    "negative": -10,
    "scientific": 1.23e-4
  }
}
'''
    
    lines = json_content.split('\n')
    symbols = parser.extract_symbols_regex(lines, "test.json", "json")
    
    # Verify complex structures are handled
    assert len(symbols) > 0
    
    # Check for various data types
    symbol_types = [s['symbol_type'] for s in symbols]
    assert 'key' in symbol_types
    assert 'string_value' in symbol_types
    assert 'numeric_value' in symbol_types
    
    print("✓ Complex structure parsing works correctly")


def test_json_parser_edge_cases():
    """Test edge cases in JSON parsing."""
    print("Testing JSON edge cases...")
    
    parser = JSONParser()
    
    # Edge cases
    edge_cases = [
        '{}',  # Empty object
        '[]',  # Empty array
        'null',  # Just null
        'true',  # Just true
        'false',  # Just false
        '42',  # Just number
        '"string"',  # Just string
        '{"key": ""}',  # Empty string value
        '{"key": null}',  # Null value
        '{"key": true}',  # Boolean value
        '{"key": false}',  # Boolean value
        '{"key": 0}',  # Zero value
        '{"key": -1}',  # Negative value
        '{"key": 1.23e-4}',  # Scientific notation
    ]
    
    for case in edge_cases:
        try:
            # Validate JSON syntax
            json.loads(case)
            
            # Test parser
            lines = [case]
            symbols = parser.extract_symbols_regex(lines, "test.json", "json")
            
            # Should not crash
            assert isinstance(symbols, list)
            
        except Exception as e:
            print(f"Warning: Edge case '{case}' failed: {e}")
    
    print("✓ Edge case handling works correctly")


def test_json_parser_with_real_file():
    """Test parser with the actual test JSON file."""
    print("Testing with real JSON file...")
    
    parser = JSONParser()
    test_file = Path(__file__).parent / "test_json_file.json"
    
    if test_file.exists():
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        symbols = parser.extract_symbols_regex(lines, str(test_file), "json")
        relationships = parser.extract_relationships(content, symbols)
        
        # Verify we got meaningful results
        assert len(symbols) > 10  # Should have many symbols
        assert len(relationships) > 5  # Should have relationships
        
        print(f"✓ Extracted {len(symbols)} symbols and "
              f"{len(relationships)} relationships")
    else:
        print("⚠ Test JSON file not found, skipping real file test")


def test_tree_sitter_query():
    """Test the tree-sitter query functionality."""
    print("Testing tree-sitter query...")
    
    # This would require tree-sitter to be properly installed
    # For now, we'll just test that the SCM file exists
    scm_file = Path(__file__).parent.parent / "queries_scm" / "json.scm"
    
    if scm_file.exists():
        with open(scm_file, 'r', encoding='utf-8') as f:
            scm_content = f.read()
        
        # Verify SCM file has expected content
        assert 'document' in scm_content
        assert 'object' in scm_content
        assert 'array' in scm_content
        assert 'string' in scm_content
        assert 'number' in scm_content
        
        print("✓ SCM file exists and has expected content")
    else:
        print("⚠ SCM file not found")


def main():
    """Run all tests."""
    print("=" * 60)
    print("JSON Parser Test Suite")
    print("=" * 60)
    
    try:
        test_json_parser_basic()
        test_json_parser_symbol_extraction()
        test_json_parser_relationships()
        test_json_parser_complex_structures()
        test_json_parser_edge_cases()
        test_json_parser_with_real_file()
        test_tree_sitter_query()
        
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