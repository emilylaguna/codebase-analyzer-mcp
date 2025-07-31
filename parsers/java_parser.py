import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class JavaParser(BaseParser):
    """Java-specific parser for extracting symbols and relationships."""
    
    def extract_symbols_regex(self, lines: List[str], file_path: str, 
                            language: str) -> List[Dict]:
        """Extract Java symbols using regex patterns."""
        symbols = []
        
        # Find method definitions
        method_pattern = (r'^\s*(?:public|private|protected)?\s*(?:static\s+)?'
                          r'(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?'
                          r'(?:abstract\s+)?(?:strictfp\s+)?(?:<[^>]+>\s+)?'
                          r'(?:[\w\[\]]+\s+)?(\w+)\s*\([^)]*\)')
        for i, line in enumerate(lines):
            match = re.match(method_pattern, line.strip())
            if match:
                method_name = match.group(1)
                # Skip constructors (same name as class)
                if method_name not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'finally']:
                    symbols.append({
                        'name': method_name,
                        'symbol_type': 'method',
                        'line_start': i + 1,
                        'line_end': i + 1,
                        'code_snippet': line.strip(),
                        'file_path': file_path,
                        'language': language
                    })
        
        # Find class definitions
        class_pattern = r'^(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(?:strictfp\s+)?class\s+(\w+)'
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
        
        # Find interface definitions
        interface_pattern = r'^(?:public\s+)?interface\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(interface_pattern, line.strip())
            if match:
                interface_name = match.group(1)
                symbols.append({
                    'name': interface_name,
                    'symbol_type': 'interface',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Java relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find method calls
        for i, line in enumerate(lines):
            method_calls = re.findall(r'(\w+)\s*\(', line)
            for method_call in method_calls:
                # Skip common Java keywords
                if method_call not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'finally', 'public', 'private', 'protected', 'static', 'return']:
                    # Find which method/class this call is in
                    for symbol in symbols:
                        if symbol['line_start'] <= i + 1 <= symbol['line_end']:
                            if symbol['name'] not in relationships:
                                relationships[symbol['name']] = []
                            relationships[symbol['name']].append({
                                'type': 'calls',
                                'target': method_call,
                                'target_type': 'method',
                                'line': i + 1
                            })
                            break
        
        # Find class inheritance and interface implementation
        for i, line in enumerate(lines):
            # Class inheritance: class Name extends Parent
            inheritance_match = re.match(r'^class\s+(\w+)\s+extends\s+(\w+)', line.strip())
            if inheritance_match:
                class_name = inheritance_match.group(1)
                parent_name = inheritance_match.group(2)
                
                if class_name not in relationships:
                    relationships[class_name] = []
                relationships[class_name].append({
                    'type': 'inherits',
                    'target': parent_name,
                    'target_type': 'class',
                    'line': i + 1
                })
            
            # Interface implementation: class Name implements Interface
            interface_match = re.match(r'^class\s+(\w+)\s+implements\s+(\w+)', line.strip())
            if interface_match:
                class_name = interface_match.group(1)
                interface_name = interface_match.group(2)
                
                if class_name not in relationships:
                    relationships[class_name] = []
                relationships[class_name].append({
                    'type': 'implements',
                    'target': interface_name,
                    'target_type': 'interface',
                    'line': i + 1
                })
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str, 
                                          capture_name: str) -> Optional[str]:
        """Extract symbol name from Java definition."""
        # Remove common prefixes
        if name.startswith('public '):
            name = name[7:]
        elif name.startswith('private '):
            name = name[8:]
        elif name.startswith('protected '):
            name = name[10:]
        
        # Remove other modifiers
        modifiers = ['static ', 'final ', 'abstract ', 'synchronized ', 'native ']
        for modifier in modifiers:
            if name.startswith(modifier):
                name = name[len(modifier):]
        
        # Extract first word as name
        words = name.split()
        if words:
            return words[0]
        
        return None 