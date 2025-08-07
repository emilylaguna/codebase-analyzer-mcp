import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class JSONParser(BaseParser):
    """JSON-specific parser for extracting symbols and relationships."""
    
    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names for JSON."""
        return {
            '.json': 'json',
            '.jsonc': 'json',  # JSON with comments
        }

    def should_extract_relationships(self, language: str) -> bool:
        """
        Check if relationships should be extracted for JSON.
        
        Args:
            language: Programming language
            
        Returns:
            False for JSON as it doesn't have meaningful relationships
        """
        return False
    
    def _get_symbol_type(self, capture_name: str, language: str) -> Optional[str]:
        """Map capture name to symbol type for JSON."""
        # Handle Tree-sitter query capture names
        if capture_name.startswith('definition.'):
            return capture_name.split('.')[1]
        
        # Handle direct capture names
        type_mapping = {
            'object': 'object',
            'array': 'array',
            'string': 'string',
            'number': 'number',
            'boolean': 'boolean',
            'null': 'null',
            'pair': 'pair',
            'key': 'key',
            'value': 'value',
            'document': 'document',
            'literal': 'literal',
            'comment': 'comment',
            'escape_sequence': 'escape_sequence',
            'string_content': 'string_content',
            'nested_object': 'nested_object',
            'nested_array': 'nested_array',
            'array_element': 'array_element',
            'empty_object': 'empty_object',
            'empty_array': 'empty_array',
            'single_element_array': 'single_element_array',
            'multi_element_array': 'multi_element_array',
            'text_content': 'text_content',
            'numeric_value': 'numeric_value',
            'boolean_true': 'boolean_true',
            'boolean_false': 'boolean_false',
            'schema_property': 'schema_property',
            'config_property': 'config_property',
            'string_list': 'string_list',
            'number_list': 'number_list',
            'object_list': 'object_list',
            'required_field': 'required_field',
            'optional_field': 'optional_field',
            'metadata': 'metadata',
            'version_info': 'version_info',
            'object_key': 'object_key',
            'string_value': 'string_value',
            'boolean_value': 'boolean_value',
            'null_value': 'null_value',
            'root_object': 'root_object',
            'root_array': 'root_array',
            'root_string': 'root_string',
            'root_number': 'root_number',
            'root_boolean': 'root_boolean',
            'root_null': 'root_null',
            'name': 'variable',  # Default for name captures
        }
        
        return type_mapping.get(capture_name, None)
    
    def extract_symbols_regex(self, lines: List[str], file_path: str,
                             language: str) -> List[Dict]:
        """Extract JSON symbols using regex patterns."""
        symbols = []
        
        # Find object definitions (simplified - just look for opening braces)
        object_pattern = r'^\s*\{'
        for i, line in enumerate(lines):
            if re.match(object_pattern, line.strip()):
                symbols.append({
                    'name': f'object_{i+1}',
                    'symbol_type': 'object',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find array definitions (simplified - just look for opening brackets)
        array_pattern = r'^\s*\['
        for i, line in enumerate(lines):
            if re.match(array_pattern, line.strip()):
                symbols.append({
                    'name': f'array_{i+1}',
                    'symbol_type': 'array',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find string keys in objects
        key_pattern = r'"([^"]+)"\s*:'
        for i, line in enumerate(lines):
            matches = re.findall(key_pattern, line)
            for j, key in enumerate(matches):
                symbols.append({
                    'name': key,
                    'symbol_type': 'key',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': f'"{key}":',
                    'file_path': file_path,
                    'language': language
                })
        
        # Find string values
        string_value_pattern = r':\s*"([^"]*)"'
        for i, line in enumerate(lines):
            matches = re.findall(string_value_pattern, line)
            for j, value in enumerate(matches):
                symbols.append({
                    'name': value,
                    'symbol_type': 'string_value',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': f'"{value}"',
                    'file_path': file_path,
                    'language': language
                })
        
        # Find numeric values
        number_pattern = (r':\s*(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)')
        for i, line in enumerate(lines):
            matches = re.findall(number_pattern, line)
            for j, number in enumerate(matches):
                symbols.append({
                    'name': number,
                    'symbol_type': 'numeric_value',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': number,
                    'file_path': file_path,
                    'language': language
                })
        
        # Find boolean values
        boolean_pattern = r':\s*(true|false)'
        for i, line in enumerate(lines):
            matches = re.findall(boolean_pattern, line)
            for j, boolean_val in enumerate(matches):
                symbols.append({
                    'name': boolean_val,
                    'symbol_type': 'boolean_value',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': boolean_val,
                    'file_path': file_path,
                    'language': language
                })
        
        # Find null values
        null_pattern = r':\s*null'
        for i, line in enumerate(lines):
            if re.search(null_pattern, line):
                symbols.append({
                    'name': 'null',
                    'symbol_type': 'null_value',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': 'null',
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract JSON relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find key-value relationships
        key_value_pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
        for i, line in enumerate(lines):
            matches = re.findall(key_value_pattern, line)
            for key, value in matches:
                if key not in relationships:
                    relationships[key] = []
                relationships[key].append({
                    'type': 'has_value',
                    'target': value,
                    'target_type': 'string',
                    'line': i + 1
                })
        
        # Find key-numeric relationships
        key_number_pattern = (r'"([^"]+)"\s*:\s*'
                              r'(-?\d+(?:\.\d+)?(?:[eE][+-]?\d+)?)')
        for i, line in enumerate(lines):
            matches = re.findall(key_number_pattern, line)
            for key, number in matches:
                if key not in relationships:
                    relationships[key] = []
                relationships[key].append({
                    'type': 'has_value',
                    'target': number,
                    'target_type': 'number',
                    'line': i + 1
                })
        
        # Find key-boolean relationships
        key_boolean_pattern = r'"([^"]+)"\s*:\s*(true|false)'
        for i, line in enumerate(lines):
            matches = re.findall(key_boolean_pattern, line)
            for key, boolean_val in matches:
                if key not in relationships:
                    relationships[key] = []
                relationships[key].append({
                    'type': 'has_value',
                    'target': boolean_val,
                    'target_type': 'boolean',
                    'line': i + 1
                })
        
        # Find key-null relationships
        key_null_pattern = r'"([^"]+)"\s*:\s*null'
        for i, line in enumerate(lines):
            matches = re.findall(key_null_pattern, line)
            for key in matches:
                if key not in relationships:
                    relationships[key] = []
                relationships[key].append({
                    'type': 'has_value',
                    'target': 'null',
                    'target_type': 'null',
                    'line': i + 1
                })
        
        # Find nested object relationships
        nested_object_pattern = r'"([^"]+)"\s*:\s*\{'
        for i, line in enumerate(lines):
            matches = re.findall(nested_object_pattern, line)
            for key in matches:
                if key not in relationships:
                    relationships[key] = []
                relationships[key].append({
                    'type': 'contains_object',
                    'target': f'nested_object_{i+1}',
                    'target_type': 'object',
                    'line': i + 1
                })
        
        # Find nested array relationships
        nested_array_pattern = r'"([^"]+)"\s*:\s*\['
        for i, line in enumerate(lines):
            matches = re.findall(nested_array_pattern, line)
            for key in matches:
                if key not in relationships:
                    relationships[key] = []
                relationships[key].append({
                    'type': 'contains_array',
                    'target': f'nested_array_{i+1}',
                    'target_type': 'array',
                    'line': i + 1
                })
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str,
                                           capture_name: str) -> Optional[str]:
        """Extract symbol name from JSON definition."""
        # For JSON, the name is often the key or value itself
        # Remove quotes if present
        if name.startswith('"') and name.endswith('"'):
            name = name[1:-1]
        
        # For objects and arrays, generate a descriptive name
        if capture_name in ['object', 'array']:
            return f'{capture_name}_{hash(name) % 1000}'
        
        return name if name else None 