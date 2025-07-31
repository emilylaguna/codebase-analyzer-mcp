from typing import List, Dict, Optional
import re
from .base_parser import BaseParser


class KotlinParser(BaseParser):
    """Kotlin-specific parser for extracting symbols and relationships."""

    def extract_symbols_regex(
        self, lines: List[str], file_path: str, language: str
    ) -> List[Dict]:
        """Extract Kotlin symbols using regex patterns."""
        symbols = []
        
        # Package declaration
        package_pattern = r'package\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
        
        # Import declarations
        import_pattern = (
            r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
            r'(?:\s+as\s+([a-zA-Z_][a-zA-Z0-9_]*))?'
        )
        
        # Class declarations
        class_pattern = (
            r'(?:public\s+|private\s+|internal\s+|protected\s+)?'
            r'(?:abstract\s+|sealed\s+|data\s+|annotation\s+)?'
            r'(?:open\s+|final\s+)?class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        )
        
        # Interface declarations
        interface_pattern = (
            r'(?:public\s+|private\s+|internal\s+|protected\s+)?'
            r'interface\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        )
        
        # Object declarations
        object_pattern = (
            r'(?:public\s+|private\s+|internal\s+|protected\s+)?'
            r'object\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        )
        
        # Enum class declarations
        enum_pattern = (
            r'(?:public\s+|private\s+|internal\s+|protected\s+)?'
            r'enum\s+class\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        )
        
        # Function declarations
        function_pattern = (
            r'(?:public\s+|private\s+|internal\s+|protected\s+)?'
            r'(?:abstract\s+|open\s+|final\s+)?'
            r'(?:suspend\s+|operator\s+|infix\s+|inline\s+|tailrec\s+|external\s+)?'
            r'fun\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        )
        
        # Property declarations
        property_pattern = (
            r'(?:public\s+|private\s+|internal\s+|protected\s+)?'
            r'(?:abstract\s+|open\s+|final\s+)?'
            r'(?:const\s+|lateinit\s+)?(?:val|var)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        )
        
        # Type alias declarations
        type_alias_pattern = r'typealias\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        
        # Companion object
        companion_pattern = (
            r'companion\s+object(?:\s+([a-zA-Z_][a-zA-Z0-9_]*))?'
        )
        
        # Secondary constructor
        constructor_pattern = r'constructor\s*\([^)]*\)'
        
        # Primary constructor (simplified)
        primary_constructor_pattern = r'class\s+[a-zA-Z_][a-zA-Z0-9_]*\s*\([^)]*\)'
        
        patterns = [
            (package_pattern, 'package'),
            (import_pattern, 'import'),
            (class_pattern, 'class'),
            (interface_pattern, 'interface'),
            (object_pattern, 'object'),
            (enum_pattern, 'enum_class'),
            (function_pattern, 'function'),
            (property_pattern, 'property'),
            (type_alias_pattern, 'type_alias'),
            (companion_pattern, 'companion_object'),
            (constructor_pattern, 'constructor'),
            (primary_constructor_pattern, 'primary_constructor')
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern, symbol_type in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    symbol_name = match.group(1) if match.groups() else match.group(0)
                    if symbol_name:
                        symbols.append({
                            'name': symbol_name,
                            'type': symbol_type,
                            'line': line_num,
                            'file': file_path,
                            'language': language
                        })
        
        return symbols

    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Kotlin relationships using regex patterns."""
        relationships = {
            'inheritance': [],
            'implementation': [],
            'composition': [],
            'dependency': [],
            'usage': []
        }
        
        lines = content.split('\n')
        
        # Inheritance relationships
        inheritance_pattern = (
            r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*'
            r'([a-zA-Z_][a-zA-Z0-9_.]*)'
        )
        
        # Interface implementation
        interface_pattern = (
            r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*'
            r'([a-zA-Z_][a-zA-Z0-9_.]*)\s*,\s*([a-zA-Z_][a-zA-Z0-9_.]*)'
        )
        
        # Function calls
        function_call_pattern = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\)'
        
        # Property access
        property_access_pattern = (
            r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\.\s*'
            r'([a-zA-Z_][a-zA-Z0-9_]*)'
        )
        
        # Import relationships
        import_pattern = r'import\s+([a-zA-Z_][a-zA-Z0-9_.]*)'
        
        for line_num, line in enumerate(lines, 1):
            # Inheritance
            inheritance_matches = re.finditer(inheritance_pattern, line)
            for match in inheritance_matches:
                child_class = match.group(1)
                parent_class = match.group(2)
                relationships['inheritance'].append({
                    'from': child_class,
                    'to': parent_class,
                    'line': line_num,
                    'type': 'inheritance'
                })
            
            # Interface implementation
            interface_matches = re.finditer(interface_pattern, line)
            for match in interface_matches:
                implementing_class = match.group(1)
                interface_name = match.group(3)
                relationships['implementation'].append({
                    'from': implementing_class,
                    'to': interface_name,
                    'line': line_num,
                    'type': 'implementation'
                })
            
            # Function calls
            function_matches = re.finditer(function_call_pattern, line)
            for match in function_matches:
                caller = self._extract_context_symbol(line, symbols)
                callee = match.group(1)
                if caller and callee:
                    relationships['usage'].append({
                        'from': caller,
                        'to': callee,
                        'line': line_num,
                        'type': 'function_call'
                    })
            
            # Property access
            property_matches = re.finditer(property_access_pattern, line)
            for match in property_matches:
                object_name = match.group(1)
                property_name = match.group(2)
                relationships['usage'].append({
                    'from': object_name,
                    'to': property_name,
                    'line': line_num,
                    'type': 'property_access'
                })
            
            # Import relationships
            import_matches = re.finditer(import_pattern, line)
            for match in import_matches:
                imported = match.group(1)
                relationships['dependency'].append({
                    'from': 'current_file',
                    'to': imported,
                    'line': line_num,
                    'type': 'import'
                })
        
        return relationships

    def extract_symbol_name_from_definition(self, name: str, capture_name: str) -> Optional[str]:
        """Extract symbol name from Kotlin definition."""
        # Handle different capture patterns
        if capture_name.startswith('name.definition.'):
            return name
        elif capture_name == 'identifier':
            return name
        elif capture_name == 'identifier.type':
            return name
        elif capture_name == 'identifier.label':
            return name
        return name

    def _extract_context_symbol(self, line: str, symbols: List[Dict]) -> Optional[str]:
        """Extract the context symbol from a line."""
        # This is a simplified approach - in practice, you'd need more sophisticated
        # parsing to determine the exact context
        for symbol in symbols:
            if symbol['name'] in line:
                return symbol['name']
        return None

    def get_supported_extensions(self) -> List[str]:
        """Get supported file extensions for Kotlin."""
        return ['.kt', '.kts']

    def get_language_name(self) -> str:
        """Get the language name."""
        return 'kotlin'
