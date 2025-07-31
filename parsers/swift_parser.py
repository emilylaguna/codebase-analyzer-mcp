import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class SwiftParser(BaseParser):
    """Swift-specific parser for extracting symbols and relationships."""
    
    def extract_symbols_regex(self, lines: List[str], file_path: str, 
                            language: str) -> List[Dict]:
        """Extract Swift symbols using regex patterns."""
        symbols = []
        
        # Find function definitions
        func_pattern = r'^func\s+(\w+)\s*\('
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
        
        # Find protocol definitions
        protocol_pattern = r'^protocol\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(protocol_pattern, line.strip())
            if match:
                protocol_name = match.group(1)
                symbols.append({
                    'name': protocol_name,
                    'symbol_type': 'protocol',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find variable declarations (let and var)
        var_pattern = r'^(let|var)\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(var_pattern, line.strip())
            if match:
                var_name = match.group(2)
                symbols.append({
                    'name': var_name,
                    'symbol_type': 'variable',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Swift relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common Swift keywords
                if func_call not in ['if', 'for', 'while', 'switch', 'guard', 
                                   'func', 'class', 'struct', 'enum', 'protocol', 
                                   'import', 'return', 'print']:
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
        
        # Find class inheritance and protocol conformance
        for i, line in enumerate(lines):
            # Class inheritance: class Name: Parent
            inheritance_match = re.match(r'^class\s+(\w+)\s*:\s*(\w+)', 
                                       line.strip())
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
            
            # Protocol conformance: class Name: Protocol
            protocol_match = re.match(r'^class\s+(\w+)\s*,\s*(\w+)', 
                                    line.strip())
            if protocol_match:
                class_name = protocol_match.group(1)
                protocol_name = protocol_match.group(2)
                
                if class_name not in relationships:
                    relationships[class_name] = []
                relationships[class_name].append({
                    'type': 'implements',
                    'target': protocol_name,
                    'target_type': 'protocol',
                    'line': i + 1
                })
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str, 
                                          capture_name: str) -> Optional[str]:
        """Extract symbol name from Swift definition."""
        # For Swift, look for patterns like "class Name", "func Name", "struct Name"
        
        # Class/Struct definition: class/struct Name
        class_match = re.match(r'^(?:public\s+)?(?:class|struct)\s+(\w+)', name)
        if class_match:
            return class_match.group(1)
        
        # Function definition: func Name
        func_match = re.match(r'^(?:public\s+)?func\s+(\w+)', name)
        if func_match:
            return func_match.group(1)
        
        # Property definition: let/var Name
        prop_match = re.match(r'^(?:public\s+)?(?:let|var)\s+(\w+)', name)
        if prop_match:
            return prop_match.group(1)
        
        # Initializer: init
        if 'init' in name:
            return 'init'
        
        # If no pattern matches, try to extract the first word after keywords
        words = name.split()
        for i, word in enumerate(words):
            if word in ['class', 'struct', 'func', 'let', 'var', 'init'] and i + 1 < len(words):
                return words[i + 1]
        
        # Fallback: return the first word that looks like a name
        for word in words:
            if (word and word[0].isalpha() and 
                word not in ['public', 'private', 'class', 'struct', 'func', 
                           'let', 'var', 'init']):
                return word
        
        return None