from typing import List, Dict, Optional
from .base_parser import BaseParser


class BashParser(BaseParser):
    """Bash-specific parser for extracting symbols and relationships."""

    def __init__(self, grammars_dir: str = "grammars", 
                 queries_dir: str = "queries_scm"):
        """Initialize the bash parser with tree-sitter support."""
        super().__init__(grammars_dir, queries_dir)

    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names for Bash."""
        return {
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',  # Zsh is similar enough to use bash grammar
            '.ksh': 'bash',  # Korn shell is similar enough to use bash grammar
        }

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
            'variable.expansion': 'variable',
            'command.argument': 'argument',
            'raw.string': 'string',
            'translated.string': 'string',
            'ansi.string': 'string',
            'expansion': 'variable',
            'arithmetic.expansion': 'expression',
            'command.substitution': 'command',
            'process.substitution': 'command',
            'array': 'array',
            'subscript': 'subscript',
            'file.redirect': 'redirect',
            'heredoc.redirect': 'redirect',
            'herestring.redirect': 'redirect',
            'redirected.statement': 'statement',
            'binary.expression': 'expression',
            'unary.expression': 'expression',
            'ternary.expression': 'expression',
            'postfix.expression': 'expression',
            'parenthesized.expression': 'expression',
            'compound.statement': 'statement',
            'subshell': 'statement',
            'brace.expression': 'expression',
            'identifier': 'identifier',
            'file.descriptor': 'descriptor',
            'test.operator': 'operator',
            'regex': 'regex',
            'extglob.pattern': 'pattern',
            'concatenation': 'expression',
            'unset.command': 'command',
            'declaration.command': 'command',
            'if.statement': 'statement',
            'elif.clause': 'statement',
            'else.clause': 'statement',
            'for.statement': 'statement',
            'c.for.statement': 'statement',
            'while.statement': 'statement',
            'case.statement': 'statement',
            'case.item': 'statement',
            'do.group': 'statement',
            'test.command': 'command',
            'pipeline': 'command',
            'list': 'command',
            'negated.command': 'command'
        }
        return type_mapping.get(capture_name, 'unknown')

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

    def _extract_bash_symbol_name(self, node, capture_name: str, name: str) -> Optional[str]:
        """
        Extract symbol name for bash-specific captures.
        
        Args:
            node: Tree-sitter node
            capture_name: Name of the capture
            name: Node text
            
        Returns:
            Symbol name or None
        """
        try:
            # Handle different bash capture types
            if capture_name == 'function.name':
                # Function name is usually the first word after 'function' or the word before '('
                if name.startswith('function '):
                    return name.split()[1] if len(name.split()) > 1 else None
                # For function_name() style, extract the name before parentheses
                if '(' in name:
                    return name.split('(')[0].strip()
                return name
            
            elif capture_name == 'variable.name':
                # Variable name is usually the text as-is
                return name
            
            elif capture_name == 'variable.expansion':
                # Variable expansion like $VAR_NAME - extract the variable name
                if name.startswith('$'):
                    return name[1:]  # Remove the $ prefix
                return name
            
            elif capture_name == 'command.name':
                # Command name is usually the first word
                words = name.split()
                return words[0] if words else None
            
            elif capture_name == 'string.content':
                # String content - return as-is for now
                return name
            
            elif capture_name in ['if.statement', 'for.statement', 'while.statement', 
                                'case.statement', 'do.group']:
                # Control structures - use the keyword as identifier
                keywords = ['if', 'for', 'while', 'case', 'do']
                for keyword in keywords:
                    if name.startswith(keyword):
                        return keyword
                return name
            
            elif capture_name in ['test.command', 'pipeline', 'list', 'negated.command']:
                # Complex commands - extract the main command name
                words = name.split()
                if words:
                    # Skip negation operator
                    if words[0] == '!':
                        return words[1] if len(words) > 1 else None
                    return words[0]
                return name
            
            elif capture_name in ['binary.expression', 'unary.expression', 
                                'ternary.expression', 'parenthesized.expression']:
                # Expressions - try to extract a meaningful identifier
                # For now, return the first word that looks like an identifier
                import re
                words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', name)
                return words[0] if words else name
            
            elif capture_name == 'comment':
                # Comments - extract first word after #
                if name.startswith('#'):
                    content = name[1:].strip()
                    words = content.split()
                    return words[0] if words else 'comment'
                return name
            
            # Default case
            return name if name else None
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error extracting bash symbol name: {e}")
            return name if name else None

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
