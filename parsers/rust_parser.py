import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class RustParser(BaseParser):
    """Rust-specific parser for extracting symbols and relationships."""
    
    def extract_symbols_regex(self, lines: List[str], file_path: str, 
                            language: str) -> List[Dict]:
        """Extract Rust symbols using regex patterns."""
        symbols = []
        
        # Find function definitions
        func_pattern = r'^fn\s+(\w+)\s*\('
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
        
        # Find struct definitions
        struct_pattern = r'^struct\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(struct_pattern, line.strip())
            if match:
                struct_name = match.group(1)
                symbols.append({
                    'name': struct_name,
                    'symbol_type': 'struct',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find trait definitions
        trait_pattern = r'^trait\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(trait_pattern, line.strip())
            if match:
                trait_name = match.group(1)
                symbols.append({
                    'name': trait_name,
                    'symbol_type': 'trait',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Rust relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common Rust keywords
                if func_call not in ['if', 'for', 'while', 'match', 'fn', 'struct', 'enum', 'trait', 'impl', 'use', 'return', 'println']:
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
        
        # Find trait implementation
        for i, line in enumerate(lines):
            impl_match = re.match(r'^impl\s+(\w+)\s+for\s+(\w+)', line.strip())
            if impl_match:
                trait_name = impl_match.group(1)
                type_name = impl_match.group(2)
                
                if type_name not in relationships:
                    relationships[type_name] = []
                relationships[type_name].append({
                    'type': 'implements',
                    'target': trait_name,
                    'target_type': 'trait',
                    'line': i + 1
                })
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str, 
                                          capture_name: str) -> Optional[str]:
        """Extract symbol name from Rust definition."""
        # Remove common prefixes
        if name.startswith('fn '):
            name = name[3:]
        elif name.startswith('struct '):
            name = name[7:]
        elif name.startswith('trait '):
            name = name[6:]
        
        # Extract first word as name
        words = name.split()
        if words:
            return words[0]
        
        return None
