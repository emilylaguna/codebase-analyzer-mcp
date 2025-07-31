#!/usr/bin/env python3
"""
Simple test for Python parser functionality.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import the parser
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.python_parser import PythonParser


def test_python_parser_basic():
    """Test basic Python parser functionality."""
    print("Testing Python parser basic functionality...")
    
    # Create parser instance
    parser = PythonParser()
    
    # Test language detection
    assert parser.detect_language("test.py") == "python"
    assert parser.detect_language("test.pyi") == "python"
    assert parser.detect_language("test.txt") is None
    
    print("✓ Language detection works correctly")


def test_python_parser_symbol_types():
    """Test Python parser symbol type mapping."""
    print("Testing Python parser symbol type mapping...")
    
    parser = PythonParser()
    
    # Test known symbol types
    assert parser._get_symbol_type('function', 'python') == 'function'
    assert parser._get_symbol_type('class', 'python') == 'class'
    assert parser._get_symbol_type('variable', 'python') == 'variable'
    
    # Test unknown symbol types
    assert parser._get_symbol_type('unknown_type', 'python') is None
    assert parser._get_symbol_type('completely_unknown', 'python') is None
    
    print("✓ Symbol type mapping works correctly")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Python Parser Simple Test Suite")
    print("=" * 60)
    
    try:
        test_python_parser_basic()
        test_python_parser_symbol_types()
        
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