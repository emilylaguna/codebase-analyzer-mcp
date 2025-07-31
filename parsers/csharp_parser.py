import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class CSharpParser(BaseParser):
    """C#-specific parser for extracting symbols and relationships."""
    
    def extract_symbols_regex(self, lines: List[str], file_path: str, 
                            language: str) -> List[Dict]:
        """Extract C# symbols using regex patterns."""
        symbols = []
        
        # Find method definitions
        method_pattern = r'^(?:public|private|protected|internal)?\s*(?:static\s+)?(?:virtual\s+)?(?:abstract\s+)?(?:override\s+)?(?:sealed\s+)?(?:async\s+)?(?:[\w\[\]<>]+\s+)?(\w+)\s*\([^)]*\)'
        for i, line in enumerate(lines):
            match = re.match(method_pattern, line.strip())
            if match:
                method_name = match.group(1)
                if method_name not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'finally', 'using']:
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
        class_pattern = r'^(?:public|private|protected|internal)?\s*(?:abstract\s+)?(?:sealed\s+)?(?:static\s+)?(?:partial\s+)?class\s+(\w+)'
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
        interface_pattern = r'^(?:public|private|protected|internal)?\s*(?:partial\s+)?interface\s+(\w+)'
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
        """Extract C# relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find method calls
        for i, line in enumerate(lines):
            method_calls = re.findall(r'(\w+)\s*\(', line)
            for method_call in method_calls:
                # Skip common C# keywords
                if method_call not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'finally', 'public', 'private', 'protected', 'internal', 'static', 'return']:
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
            # Class inheritance: class Name : Parent
            inheritance_match = re.match(r'^class\s+(\w+)\s*:\s*(\w+)', line.strip())
            if inheritance_match:
                class_name = inheritance_match.group(1)
                parent_name = inheritance_match.group(2)
                
                # Determine if it's inheritance or interface implementation
                if parent_name.startswith('I'):  # Common C# convention
                    relationships.setdefault(class_name, []).append({
                        'type': 'implements',
                        'target': parent_name,
                        'target_type': 'interface',
                        'line': i + 1
                    })
                else:
                    relationships.setdefault(class_name, []).append({
                        'type': 'inherits',
                        'target': parent_name,
                        'target_type': 'class',
                        'line': i + 1
                    })
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str, 
                                          capture_name: str) -> Optional[str]:
        """Extract symbol name from C# definition."""
        # Remove common prefixes
        if name.startswith('public '):
            name = name[7:]
        elif name.startswith('private '):
            name = name[8:]
        elif name.startswith('protected '):
            name = name[10:]
        elif name.startswith('internal '):
            name = name[9:]
        
        # Remove other modifiers
        modifiers = ['static ', 'virtual ', 'abstract ', 'override ', 'sealed ', 'async ']
        for modifier in modifiers:
            if name.startswith(modifier):
                name = name[len(modifier):]
        
        # Extract first word as name
        words = name.split()
        if words:
            return words[0]
        
        return None
