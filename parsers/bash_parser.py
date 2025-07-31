from typing import List, Dict, Optional
from .base_parser import BaseParser


class BashParser(BaseParser):
    """Bash-specific parser for extracting symbols and relationships."""

    def __init__(self, grammars_dir: str = "grammars", 
                 queries_dir: str = "queries_scm"):
        """Initialize the bash parser with tree-sitter support."""
        super().__init__(grammars_dir, queries_dir)
        # Add bash file extensions to the language map
        self.language_map.update({
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',  # Zsh is similar enough to use bash grammar
            '.ksh': 'bash',  # Korn shell is similar enough to use bash grammar
        })

    def parse_file(self, file_path: str) -> List[Dict]:
        """Parse a bash file using tree-sitter with fallback to regex."""
        try:
            # Try tree-sitter parsing first
            symbols = super().parse_file(file_path)
            if symbols:
                return symbols
        except Exception:
            # Fall back to regex parsing if tree-sitter fails
            pass
        
        # Fallback to regex parsing
        return self.extract_symbols_regex(
            self._read_file_lines(file_path), file_path, 'bash'
        )

    def extract_symbols_regex(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract Bash symbols using regex patterns as fallback."""
        symbols = []
        
        import re
        
        # Function definitions
        function_patterns = [
            r'^\s*function\s+(\w+)\s*\(\)\s*\{',  # function name() {
            r'^\s*function\s+(\w+)\s*\{',         # function name {
            r'^\s*(\w+)\s*\(\)\s*\{',             # name() {
            r'^\s*(\w+)\s*\(\)\s*\(',             # name() (
            r'^\s*(\w+)\s*\(\)\s*\[\[',           # name() [[
        ]
        
        for i, line in enumerate(lines):
            for pattern in function_patterns:
                match = re.match(pattern, line)
                if match:
                    function_name = match.group(1)
                    symbols.append({
                        'name': function_name,
                        'type': 'function',
                        'line': i + 1,
                        'file': file_path,
                        'language': language,
                        'scope': 'global'
                    })
                    break
        
        # Variable assignments
        var_patterns = [
            r'^\s*(\w+)=',                    # var=
            r'^\s*declare\s+(\w+)=',          # declare var=
            r'^\s*typeset\s+(\w+)=',          # typeset var=
            r'^\s*local\s+(\w+)=',            # local var=
            r'^\s*readonly\s+(\w+)=',         # readonly var=
            r'^\s*export\s+(\w+)=',           # export var=
        ]
        
        for i, line in enumerate(lines):
            for pattern in var_patterns:
                match = re.match(pattern, line)
                if match:
                    var_name = match.group(1)
                    symbols.append({
                        'name': var_name,
                        'type': 'variable',
                        'line': i + 1,
                        'file': file_path,
                        'language': language,
                        'scope': 'global'
                    })
                    break
        
        return symbols

    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Bash relationships using tree-sitter with fallback to regex."""
        try:
            # Try tree-sitter relationships first
            relationships = super()._extract_relationships(
                self._parse_content(content, 'bash'), 
                content, 
                'bash', 
                'memory', 
                symbols
            )
            if relationships:
                return relationships
        except Exception:
            # Fall back to regex relationships if tree-sitter fails
            pass
        
        # Fallback to regex relationships
        return self._extract_relationships_regex(content, symbols)

    def _extract_relationships_regex(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Bash relationships using regex patterns."""
        relationships = {
            'calls': [],
            'uses': [],
            'defines': [],
            'imports': []
        }
        
        import re
        
        # Find function calls
        function_symbols = [s for s in symbols if s['type'] == 'function']
        for func in function_symbols:
            func_name = func['name']
            # Look for function calls in the content
            call_pattern = rf'\b{re.escape(func_name)}\b'
            matches = re.finditer(call_pattern, content)
            for match in matches:
                relationships['calls'].append({
                    'caller': 'unknown',
                    'callee': func_name,
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'function_call'
                })
        
        # Find variable usage
        variable_symbols = [s for s in symbols if s['type'] == 'variable']
        for var in variable_symbols:
            var_name = var['name']
            # Look for variable usage (excluding definitions)
            usage_pattern = rf'\$\{{?{re.escape(var_name)}\}}?'
            matches = re.finditer(usage_pattern, content)
            for match in matches:
                relationships['uses'].append({
                    'user': 'unknown',
                    'used': var_name,
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'variable_usage'
                })
        
        # Find source/include relationships
        source_patterns = [
            r'^\s*source\s+([^\s]+)',
            r'^\s*\.\s+([^\s]+)',
        ]
        
        for pattern in source_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                source_file = match.group(1).strip('"\'')
                relationships['imports'].append({
                    'importer': 'current_file',
                    'imported': source_file,
                    'line': content[:match.start()].count('\n') + 1,
                    'type': 'source'
                })
        
        return relationships

    def extract_symbol_name_from_definition(self, name: str, capture_name: str) -> Optional[str]:
        """Extract symbol name from Bash definition."""
        # For bash, the name is usually the first word in the capture
        if capture_name in ['function.name', 'variable.name', 'command.name']:
            return name.strip()
        return None

    def _get_symbol_type(self, capture_name: str) -> str:
        """Map capture names to symbol types for bash."""
        type_mapping = {
            'function.name': 'function',
            'function.full_name': 'function',
            'variable.name': 'variable',
            'command.name': 'command',
            'command.env_var': 'variable',
            'special_variable.name': 'variable',
            'array.name': 'variable',
            'string.content': 'string',
            'string.raw': 'string',
            'number': 'number',
            'comment': 'comment',
            'shebang': 'directive',
        }
        return type_mapping.get(capture_name, 'unknown')

    def _read_file_lines(self, file_path: str) -> List[str]:
        """Read file lines for regex fallback."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except Exception:
            return []

    def _parse_content(self, content: str, language: str):
        """Parse content for tree-sitter analysis."""
        parser = self._get_language_parser(language)
        if parser:
            return parser.parse(bytes(content, 'utf8'))
        return None
