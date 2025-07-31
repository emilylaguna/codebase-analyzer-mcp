from typing import Dict, List, Optional
from .base_parser import BaseParser


class ComprehensiveParser(BaseParser):
    """Comprehensive parser that supports all languages with their specific mappings."""
    
    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names for all supported languages."""
        return {
            # Python
            '.py': 'python',
            '.pyx': 'python',
            '.pyi': 'python',
            
            # JavaScript/TypeScript
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'tsx',
            
            # Java
            '.java': 'java',
            
            # C/C++
            '.c': 'c',
            '.h': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.hpp': 'cpp',
            
            # C#
            '.cs': 'c_sharp',
            
            # Go
            '.go': 'go',
            
            # Rust
            '.rs': 'rust',
            
            # Ruby
            '.rb': 'ruby',
            '.erb': 'ruby',
            
            # PHP
            '.php': 'php',
            
            # Swift
            '.swift': 'swift',
            
            # Kotlin
            '.kt': 'kotlin',
            '.kts': 'kotlin',
            
            # Scala
            '.scala': 'scala',
            
            # Lua
            '.lua': 'lua',
            
            # HTML/CSS
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            
            # JSON
            '.json': 'json',
            
            # YAML
            '.yml': 'yaml',
            '.yaml': 'yaml',
            
            # TOML
            '.toml': 'toml',
            
            # Vue
            '.vue': 'vue',
            
            # Solidity
            '.sol': 'solidity',
            
            # Zig
            '.zig': 'zig',
            
            # Elixir
            '.ex': 'elixir',
            '.exs': 'elixir',
            
            # OCaml
            '.ml': 'ocaml',
            '.mli': 'ocaml',
            
            # Elm
            '.elm': 'elm',
            
            # Bash
            '.sh': 'bash',
            '.bash': 'bash',
            '.zsh': 'bash',  # Zsh is similar enough to use bash grammar
            '.ksh': 'bash',  # Korn shell is similar enough to use bash grammar
            
            # Elisp
            '.el': 'elisp',
            
            # SystemRDL
            '.rdl': 'systemrdl',
            
            # TLA+
            '.tla': 'tlaplus',
            
            # QL
            '.ql': 'ql',
            
            # ReScript
            '.re': 'rescript',
            '.resi': 'rescript',
        }
    
    def _get_symbol_type(self, capture_name: str, language: str) -> str:
        """
        Map capture name to symbol type with language-specific handling.
        
        Args:
            capture_name: Name of the capture
            language: Programming language
            
        Returns:
            Symbol type
        """
        # Get language-specific parser for type mapping
        parser = self._get_language_parser(language)
        if parser and hasattr(parser, '_get_symbol_type'):
            return parser._get_symbol_type(capture_name)
        
        # Fallback to generic mapping
        # Handle Tree-sitter query capture names (e.g., "definition.class", "definition.function")
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
            'initializer': 'initializer',
            'deinitializer': 'deinitializer',
            'subscript': 'subscript',
            'computed_property': 'computed_property',
            'type_alias': 'type_alias',
            'protocol_property': 'protocol_property',
            'protocol_method': 'protocol_method',
            'static_method': 'static_method',
            'convenience_initializer': 'convenience_initializer',
            'identifier': 'identifier',
            'name': 'variable',  # Default for name captures
        }
        
        return type_mapping.get(capture_name, 'unknown') 