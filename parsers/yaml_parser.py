import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class YamlParser(BaseParser):
    """YAML-specific parser for extracting symbols and relationships."""
    
    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names for YAML."""
        return {
            '.yml': 'yaml',
            '.yaml': 'yaml',
        }

    def should_extract_relationships(self, language: str) -> bool:
        """
        Check if relationships should be extracted for YAML.
        
        Args:
            language: Programming language
            
        Returns:
            False for YAML as it doesn't have meaningful relationships
        """
        return False
    
    def _get_symbol_type(self, capture_name: str, language: str) -> Optional[str]:
        """Map capture name to symbol type for YAML."""
        # Handle Tree-sitter query capture names
        if capture_name.startswith('definition.'):
            return capture_name.split('.')[1]
        
        # Handle direct capture names
        type_mapping = {
            'document': 'document',
            'mapping': 'mapping',
            'sequence': 'sequence',
            'scalar': 'scalar',
            'key': 'key',
            'value': 'value',
            'anchor': 'anchor',
            'alias': 'alias',
            'tag': 'tag',
            'comment': 'comment',
            'directive': 'directive',
            'name': 'variable',  # Default for name captures
        }
        
        return type_mapping.get(capture_name, None)
    
    def extract_symbols_regex(self, lines: List[str], file_path: str,
                             language: str) -> List[Dict]:
        """Extract YAML symbols using regex patterns."""
        symbols = []
        
        # Find YAML keys (simple key-value pairs)
        key_pattern = r'^(\s*)([^:\s]+)\s*:'
        for i, line in enumerate(lines):
            match = re.match(key_pattern, line)
            if match:
                key = match.group(2)
                symbols.append({
                    'name': key,
                    'symbol_type': 'key',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find YAML anchors
        anchor_pattern = r'^(\s*)([^:\s]+)\s*:&([^\s]+)'
        for i, line in enumerate(lines):
            match = re.search(anchor_pattern, line)
            if match:
                key = match.group(2)
                anchor = match.group(3)
                symbols.append({
                    'name': anchor,
                    'symbol_type': 'anchor',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find YAML aliases
        alias_pattern = r'^\s*\*([^\s]+)'
        for i, line in enumerate(lines):
            match = re.search(alias_pattern, line)
            if match:
                alias = match.group(1)
                symbols.append({
                    'name': alias,
                    'symbol_type': 'alias',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract YAML relationships using regex patterns."""
        # YAML doesn't have meaningful relationships between symbols
        return {}
    
    def extract_symbol_name_from_definition(self, name: str,
                                           capture_name: str) -> Optional[str]:
        """Extract symbol name from YAML definition."""
        # For YAML, the name is often the key or value itself
        return name if name else None 