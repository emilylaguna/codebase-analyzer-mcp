import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class GoParser(BaseParser):
    """Go-specific parser for extracting symbols and relationships."""
    
    def extract_symbols_regex(self, lines: List[str], file_path: str, 
                            language: str) -> List[Dict]:
        """Extract Go symbols using regex patterns."""
        symbols = []
        
        # Find function definitions
        func_pattern = r'^func\s+(?:\(\s*[\w\*]+\s+[\w\*]+\s*\)\s+)?(\w+)\s*\('
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
        
        # Find type definitions
        type_pattern = r'^type\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(type_pattern, line.strip())
            if match:
                type_name = match.group(1)
                symbols.append({
                    'name': type_name,
                    'symbol_type': 'type',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Go relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common Go keywords
                if func_call not in ['if', 'for', 'range', 'switch', 'select', 'func', 'type', 'struct', 'interface', 'import', 'return', 'fmt']:
                    # Find which function this call is in
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
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str, 
                                          capture_name: str) -> Optional[str]:
        """Extract symbol name from Go definition."""
        # Remove common prefixes
        if name.startswith('func '):
            name = name[5:]
        elif name.startswith('type '):
            name = name[5:]
        
        # Extract first word as name
        words = name.split()
        if words:
            return words[0]
        
        return None
