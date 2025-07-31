#!/usr/bin/env python3
"""
Simple test for comprehensive parser functionality.
"""

import sys
from pathlib import Path

# Add the parent directory to the path to import the parser
sys.path.insert(0, str(Path(__file__).parent.parent))

from parsers.comprehensive_parser import ComprehensiveParser


def test_comprehensive_parser_basic():
    """Test basic comprehensive parser functionality."""
    print("Testing comprehensive parser basic functionality...")
    
    # Create parser instance
    parser = ComprehensiveParser()
    
    # Test language detection for various languages
    assert parser.detect_language("test.py") == "python"
    assert parser.detect_language("test.js") == "javascript"
    assert parser.detect_language("test.json") == "json"
    assert parser.detect_language("test.txt") is None
    
    print("✓ Language detection works correctly")


def test_comprehensive_parser_symbol_types():
    """Test comprehensive parser symbol type mapping."""
    print("Testing comprehensive parser symbol type mapping...")
    
    parser = ComprehensiveParser()
    
    # Test known symbol types
    assert parser._get_symbol_type('function', 'python') == 'function'
    assert parser._get_symbol_type('class', 'python') == 'class'
    # Note: comprehensive parser only has generic mappings, not JSON-specific ones
    assert parser._get_symbol_type('variable', 'python') == 'variable'
    
    # Test unknown symbol types
    assert parser._get_symbol_type('unknown_type', 'python') is None
    assert parser._get_symbol_type('completely_unknown', 'json') is None
    
    print("✓ Symbol type mapping works correctly")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Comprehensive Parser Test Suite")
    print("=" * 60)
    
    try:
        test_comprehensive_parser_basic()
        test_comprehensive_parser_symbol_types()
        
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