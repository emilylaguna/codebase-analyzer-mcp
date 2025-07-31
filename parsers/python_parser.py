import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class PythonParser(BaseParser):
    """Python-specific parser for extracting symbols and relationships."""
    
    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names for Python."""
        return {
            '.py': 'python',
            '.pyx': 'python',
            '.pyi': 'python',
        }
    
    def _get_symbol_type(self, capture_name: str, language: str) -> Optional[str]:
        """Map capture name to symbol type for Python."""
        # Handle Tree-sitter query capture names
        if capture_name.startswith('definition.'):
            return capture_name.split('.')[1]
        
        # Handle direct capture names
        type_mapping = {
            'function': 'function',
            'method': 'method',
            'class': 'class',
            'interface': 'interface',
            'variable': 'variable',
            'constant': 'constant',
            'enum': 'enum',
            'struct': 'struct',
            'trait': 'trait',
            'protocol': 'protocol',
            'module': 'module',
            'namespace': 'namespace',
            'property': 'property',
            'identifier': 'identifier',
            'name': 'variable',  # Default for name captures
        }
        
        return type_mapping.get(capture_name, None)
    
    def extract_symbols_regex(self, lines: List[str], file_path: str, 
                            language: str) -> List[Dict]:
        """Extract Python symbols using regex patterns."""
        symbols = []
        
        # Find function definitions
        func_pattern = r'^def\s+(\w+)\s*\('
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line.strip())
            if match:
                func_name = match.group(1)
                symbols.append({
                    'name': func_name,
                    'symbol_type': 'function',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find class definitions
        class_pattern = r'^class\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(class_pattern, line.strip())
            if match:
                class_name = match.group(1)
                symbols.append({
                    'name': class_name,
                    'symbol_type': 'class',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Python relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common Python keywords and built-ins
                skip_keywords = ['if', 'for', 'while', 'with', 'def', 'class',
                                'import', 'from', 'return', 'print']
                if func_call not in skip_keywords:
                    # Find which function/class this call is in
                    for symbol in symbols:
                        if symbol['line_start'] <= i + 1 <= symbol['line_end']:
                            if symbol['name'] not in relationships:
                                relationships[symbol['name']] = []
                            relationships[symbol['name']].append({
                                'type': 'calls',
                                'target': func_call,
                                'target_type': 'function',
                                'line': i + 1
                            })
                            break
        
        # Find class inheritance
        for i, line in enumerate(lines):
            inheritance_match = re.match(r'^class\s+(\w+)\s*\(([^)]+)\)', 
                                       line.strip())
            if inheritance_match:
                class_name = inheritance_match.group(1)
                parent_name = inheritance_match.group(2).strip()
                
                if class_name not in relationships:
                    relationships[class_name] = []
                relationships[class_name].append({
                    'type': 'inherits',
                    'target': parent_name,
                    'target_type': 'class',
                    'line': i + 1
                })
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str, 
                                          capture_name: str) -> Optional[str]:
        """Extract symbol name from Python definition."""
        # Remove common prefixes
        if name.startswith('def '):
            name = name[4:]
        elif name.startswith('class '):
            name = name[6:]
        
        # Extract first word as name
        words = name.split()
        if words:
            return words[0]
        
        return None 