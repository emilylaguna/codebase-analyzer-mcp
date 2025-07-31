#!/usr/bin/env python3
"""
Test script for Markdown parser and SCM queries.
"""

import subprocess
import sys
from pathlib import Path


def run_tree_sitter_query(scm_path: str, markdown_file: str, 
                         query_name: str = None):
    """Run tree-sitter query command and return results."""
    try:
        cmd = ['tree-sitter', 'query', scm_path, markdown_file]
        if query_name:
            cmd.extend(['--captures', query_name])
        
        result = subprocess.run(cmd, capture_output=True, text=True, 
                              check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running tree-sitter query: {e}")
        print(f"stderr: {e.stderr}")
        return None


def test_headings():
    """Test heading queries."""
    print("=== Testing Heading Queries ===")
    
    # Test ATX headings
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.heading'
    )
    if result:
        print("ATX Headings found:")
        print(result)
    
    # Test specific heading levels
    for level in range(1, 7):
        result = run_tree_sitter_query(
            'queries_scm/markdown.scm',
            'test_codebase/test_markdown_file.md',
            f'definition.heading.h{level}'
        )
        if result:
            print(f"H{level} Headings found:")
            print(result)


def test_lists():
    """Test list queries."""
    print("\n=== Testing List Queries ===")
    
    # Test list containers
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.list'
    )
    if result:
        print("Lists found:")
        print(result)
    
    # Test list items
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.list_item'
    )
    if result:
        print("List items found:")
        print(result)
    
    # Test task lists
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.task_list_marker'
    )
    if result:
        print("Task list markers found:")
        print(result)


def test_code_blocks():
    """Test code block queries."""
    print("\n=== Testing Code Block Queries ===")
    
    # Test fenced code blocks
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.code_block.fenced'
    )
    if result:
        print("Fenced code blocks found:")
        print(result)
    
    # Test indented code blocks
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.code_block.indented'
    )
    if result:
        print("Indented code blocks found:")
        print(result)
    
    # Test code blocks with language
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.code_block.language'
    )
    if result:
        print("Code blocks with language found:")
        print(result)


def test_tables():
    """Test table queries."""
    print("\n=== Testing Table Queries ===")
    
    # Test pipe tables
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.table'
    )
    if result:
        print("Tables found:")
        print(result)
    
    # Test table headers
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.table.header'
    )
    if result:
        print("Table headers found:")
        print(result)
    
    # Test table cells
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.table.cell'
    )
    if result:
        print("Table cells found:")
        print(result)


def test_blockquotes():
    """Test blockquote queries."""
    print("\n=== Testing Blockquote Queries ===")
    
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.blockquote'
    )
    if result:
        print("Blockquotes found:")
        print(result)


def test_links():
    """Test link queries."""
    print("\n=== Testing Link Queries ===")
    
    # Test link references
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.link_reference'
    )
    if result:
        print("Link references found:")
        print(result)
    
    # Test link components
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.link'
    )
    if result:
        print("Link components found:")
        print(result)


def test_thematic_breaks():
    """Test thematic break queries."""
    print("\n=== Testing Thematic Break Queries ===")
    
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'definition.thematic_break'
    )
    if result:
        print("Thematic breaks found:")
        print(result)


def test_relationships():
    """Test relationship queries."""
    print("\n=== Testing Relationship Queries ===")
    
    # Test nested structures
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'relationship'
    )
    if result:
        print("Relationships found:")
        print(result)
    
    # Test section relationships
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'relationship.heading_in_section'
    )
    if result:
        print("Headings in sections found:")
        print(result)


def test_all_extractions():
    """Test all extraction queries."""
    print("\n=== Testing All Extractions ===")
    
    result = run_tree_sitter_query(
        'queries_scm/markdown.scm',
        'test_codebase/test_markdown_file.md',
        'extraction.all'
    )
    if result:
        print("All extractions found:")
        print(result)


def test_parser_integration():
    """Test the markdown parser integration."""
    print("\n=== Testing Parser Integration ===")
    
    try:
        # Import the parser
        import sys
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'parsers'))
        from markdown_parser import MarkdownParser
        
        # Create parser instance
        parser = MarkdownParser()
        
        # Test file extension mapping
        print("Supported file extensions:")
        for ext, lang in parser.language_map.items():
            print(f"  {ext} -> {lang}")
        
        # Test symbol type mapping
        test_captures = [
            'definition.heading.h1',
            'definition.list_item',
            'definition.code_block.fenced',
            'definition.table',
            'definition.blockquote'
        ]
        
        print("\nSymbol type mappings:")
        for capture in test_captures:
            symbol_type = parser._get_symbol_type(capture, 'markdown')
            print(f"  {capture} -> {symbol_type}")
        
        print("\nParser integration test completed successfully!")
        
    except ImportError as e:
        print(f"Error importing markdown parser: {e}")
    except Exception as e:
        print(f"Error testing parser integration: {e}")


def main():
    """Run all tests."""
    print("Markdown Parser and SCM Query Tests")
    print("=" * 50)
    
    # Check if files exist
    scm_path = Path('queries_scm/markdown.scm')
    markdown_file = Path('test_codebase/test_markdown_file.md')
    
    if not scm_path.exists():
        print(f"Error: SCM file not found at {scm_path}")
        return
    
    if not markdown_file.exists():
        print(f"Error: Markdown test file not found at {markdown_file}")
        return
    
    # Run tests
    test_headings()
    test_lists()
    test_code_blocks()
    test_tables()
    test_blockquotes()
    test_links()
    test_thematic_breaks()
    test_relationships()
    test_all_extractions()
    test_parser_integration()
    
    print("\n" + "=" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    main() 