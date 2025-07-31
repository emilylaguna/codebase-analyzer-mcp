from typing import Optional, Dict, Type
from .base_parser import BaseParser
from .python_parser import PythonParser
from .swift_parser import SwiftParser
from .bash_parser import BashParser
from .javascript_parser import JavaScriptParser
from .java_parser import JavaParser
from .cpp_parser import CppParser
from .csharp_parser import CSharpParser
from .go_parser import GoParser
from .rust_parser import RustParser
from .ruby_parser import RubyParser
from .php_parser import PhpParser
from .kotlin_parser import KotlinParser
from .scala_parser import ScalaParser
from .lua_parser import LuaParser
from .html_parser import HtmlParser
from .css_parser import CssParser
from .vue_parser import VueParser
from .solidity_parser import SolidityParser
from .zig_parser import ZigParser
from .elixir_parser import ElixirParser
from .ocaml_parser import OcamlParser
from .elisp_parser import ElispParser
from .systemrdl_parser import SystemRdlParser
from .tlaplus_parser import TlaplusParser


class LanguageParserFactory:
    """Factory for creating language-specific parsers."""
    
    _parsers: Dict[str, Type[BaseParser]] = {
        'python': PythonParser,
        'swift': SwiftParser,
        'bash': BashParser,
        'javascript': JavaScriptParser,
        'typescript': JavaScriptParser,  # TypeScript uses JavaScript parser
        'tsx': JavaScriptParser,  # TSX uses JavaScript parser
        'java': JavaParser,
        'c': CppParser,  # C uses C++ parser
        'cpp': CppParser,
        'c_sharp': CSharpParser,
        'go': GoParser,
        'rust': RustParser,
        'ruby': RubyParser,
        'php': PhpParser,
        'kotlin': KotlinParser,
        'scala': ScalaParser,
        'lua': LuaParser,
        'html': HtmlParser,
        'css': CssParser,
        'vue': VueParser,
        'solidity': SolidityParser,
        'zig': ZigParser,
        'elixir': ElixirParser,
        'ocaml': OcamlParser,
        'elisp': ElispParser,
        'systemrdl': SystemRdlParser,
        'tlaplus': TlaplusParser,
    }
    
    @classmethod
    def get_parser(cls, language: str) -> Optional[BaseParser]:
        """
        Get a language-specific parser instance.
        
        Args:
            language: Language name
            
        Returns:
            Language-specific parser instance or None if not supported
        """
        parser_class = cls._parsers.get(language)
        if parser_class:
            return parser_class()
        return None
    
    @classmethod
    def get_supported_languages(cls) -> list:
        """Get list of supported languages."""
        return list(cls._parsers.keys())
    
    @classmethod
    def register_parser(cls, language: str, parser_class: Type[BaseParser]):
        """Register a new language parser."""
        cls._parsers[language] = parser_class 