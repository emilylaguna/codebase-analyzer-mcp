import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class TomlParser(BaseParser):
    """TOML-specific parser for extracting symbols and relationships."""
    
    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names for TOML."""
        return {
            '.toml': 'toml',
        }

    def should_extract_relationships(self, language: str) -> bool:
        """
        Check if relationships should be extracted for TOML.
        
        Args:
            language: Programming language
            
        Returns:
            False for TOML as it doesn't have meaningful relationships
        """
        return False
    
    def _get_symbol_type(self, capture_name: str, language: str) -> Optional[str]:
        """Map capture name to symbol type for TOML."""
        # Handle Tree-sitter query capture names
        if capture_name.startswith('definition.'):
            return capture_name.split('.')[1]
        
        # Handle direct capture names
        type_mapping = {
            'document': 'document',
            'table': 'table',
            'array_of_tables': 'array_of_tables',
            'key_value': 'key_value',
            'key': 'key',
            'value': 'value',
            'string': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'date_time': 'date_time',
            'array': 'array',
            'inline_table': 'inline_table',
            'comment': 'comment',
            'name': 'variable',  # Default for name captures
        }
        
        return type_mapping.get(capture_name, None)
    
    def extract_symbols_regex(self, lines: List[str], file_path: str,
                             language: str) -> List[Dict]:
        """Extract TOML symbols using regex patterns."""
        symbols = []
        
        # Find TOML tables
        table_pattern = r'^\[([^\]]+)\]'
        for i, line in enumerate(lines):
            match = re.match(table_pattern, line.strip())
            if match:
                table_name = match.group(1)
                symbols.append({
                    'name': table_name,
                    'symbol_type': 'table',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find TOML array of tables
        array_table_pattern = r'^\[\[([^\]]+)\]\]'
        for i, line in enumerate(lines):
            match = re.match(array_table_pattern, line.strip())
            if match:
                table_name = match.group(1)
                symbols.append({
                    'name': table_name,
                    'symbol_type': 'array_of_tables',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find TOML key-value pairs
        key_value_pattern = r'^([^=]+)\s*=\s*(.+)$'
        for i, line in enumerate(lines):
            match = re.match(key_value_pattern, line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                symbols.append({
                    'name': key,
                    'symbol_type': 'key',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract TOML relationships using regex patterns."""
        # TOML doesn't have meaningful relationships between symbols
        return {}
    
    def extract_symbol_name_from_definition(self, name: str,
                                           capture_name: str) -> Optional[str]:
        """Extract symbol name from TOML definition."""
        # For TOML, the name is often the key or table name itself
        return name if name else None 