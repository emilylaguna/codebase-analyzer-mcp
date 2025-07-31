#!/usr/bin/env python3
"""
Test script to verify Swift parsing with comprehensive SCM query
"""

import json
import sys
import traceback
from pathlib import Path

# Add the current directory to the path so we can import parser
sys.path.insert(0, str(Path(__file__).parent))

from parsers.code_parser import CodeParser


def test_swift_parsing():
    """Test parsing the Swift test file with comprehensive SCM query."""
    
    # Initialize the parser
    parser = CodeParser()
    
    # Test file path
    test_file = "test_swift_file.swift"
    
    print(f"Testing Swift parsing with file: {test_file}")
    print("=" * 60)
    
    try:
        # Parse the file
        symbols = parser.parse_file(test_file)
        
        print(f"Found {len(symbols)} symbols:")
        print("-" * 40)
        
        # Group symbols by type
        symbols_by_type = {}
        for symbol in symbols:
            symbol_type = symbol.get('symbol_type', 'unknown')
            if symbol_type not in symbols_by_type:
                symbols_by_type[symbol_type] = []
            symbols_by_type[symbol_type].append(symbol)
        
        # Print summary by type
        for symbol_type, type_symbols in symbols_by_type.items():
            print(f"\n{symbol_type.upper()} ({len(type_symbols)}):")
            for symbol in type_symbols:
                name = symbol.get('name', 'Unknown')
                line_start = symbol.get('line_start', 0)
                line_end = symbol.get('line_end', 0)
                snippet = symbol.get('code_snippet', '')
                if len(snippet) > 50:
                    snippet = snippet[:50] + "..."
                
                print(f"  - {name} (lines {line_start}-{line_end})")
                print(f"    Snippet: {snippet}")
                
                # Print relationships if any
                relationships = symbol.get('relationships', [])
                if relationships:
                    print("    Relationships:")
                    for rel in relationships:
                        rel_type = rel.get('type', 'unknown')
                        target = rel.get('target', 'unknown')
                        target_type = rel.get('target_type', 'unknown')
                        line = rel.get('line', 0)
                        print(f"      - {rel_type} -> {target} "
                              f"({target_type}) at line {line}")
        
        # Print detailed JSON for first few symbols
        print("\n\nDetailed JSON for first 3 symbols:")
        print("-" * 40)
        for i, symbol in enumerate(symbols[:3]):
            print(f"\nSymbol {i+1}:")
            print(json.dumps(symbol, indent=2, default=str))
        
        # Test specific symbol types we expect
        expected_types = [
            'protocol', 'enum', 'struct', 'class', 'function', 
            'property', 'variable', 'type_alias'
        ]
        found_types = set(symbols_by_type.keys())
        
        print("\n\nSymbol Type Coverage:")
        print("-" * 40)
        for expected_type in expected_types:
            status = "✓" if expected_type in found_types else "✗"
            count = len(symbols_by_type.get(expected_type, []))
            print(f"{status} {expected_type}: {count}")
        
        # Check for specific expected symbols
        expected_symbols = [
            'DataProcessor', 'NetworkDelegate',  # Protocols
            'NetworkError', 'UserRole',  # Enums
            'User', 'NetworkResponse',  # Structs
            'NetworkManager', 'UserManager',  # Classes
            'createTestUser', 'validateUser',  # Global functions
            'AsyncDataProcessor',  # Actor
            'ValidatedEmail', 'ValidatedUser'  # Property wrappers
        ]
        
        found_symbols = [s.get('name', '') for s in symbols]
        print("\n\nExpected Symbol Coverage:")
        print("-" * 40)
        for expected_symbol in expected_symbols:
            status = "✓" if expected_symbol in found_symbols else "✗"
            print(f"{status} {expected_symbol}")
        
        return len(symbols) > 0
        
    except Exception as e:
        print(f"Error parsing Swift file: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_swift_parsing()
    if success:
        print("\n✅ Swift parsing test completed successfully!")
    else:
        print("\n❌ Swift parsing test failed!")
        sys.exit(1) 