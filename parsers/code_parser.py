from typing import Dict, Optional
from .comprehensive_parser import ComprehensiveParser
from .swift_parser import SwiftParser
from .python_parser import PythonParser
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
from .bash_parser import BashParser


class CodeParser(ComprehensiveParser):
    """Main code parser that uses language-specific parsers."""
    
    def __init__(self, grammars_dir: str = "grammars", queries_dir: str = "queries_scm"):
        super().__init__(grammars_dir, queries_dir)
        self._init_language_parsers()
    
    def _init_language_parsers(self):
        """Initialize language-specific parsers."""
        self.language_parsers: Dict[str, ComprehensiveParser] = {
            'swift': SwiftParser(self.grammars_dir, self.queries_dir),
            'python': PythonParser(self.grammars_dir, self.queries_dir),
            'javascript': JavaScriptParser(self.grammars_dir, self.queries_dir),
            'typescript': JavaScriptParser(self.grammars_dir,
                                         self.queries_dir),
            'tsx': JavaScriptParser(self.grammars_dir, self.queries_dir),
            'java': JavaParser(self.grammars_dir, self.queries_dir),
            'c': CppParser(self.grammars_dir, self.queries_dir),
            'cpp': CppParser(self.grammars_dir, self.queries_dir),
            'c_sharp': CSharpParser(self.grammars_dir, self.queries_dir),
            'go': GoParser(self.grammars_dir, self.queries_dir),
            'rust': RustParser(self.grammars_dir, self.queries_dir),
            'ruby': RubyParser(self.grammars_dir, self.queries_dir),
            'php': PhpParser(self.grammars_dir, self.queries_dir),
            'kotlin': KotlinParser(self.grammars_dir, self.queries_dir),
            'scala': ScalaParser(self.grammars_dir, self.queries_dir),
            'lua': LuaParser(self.grammars_dir, self.queries_dir),
            'html': HtmlParser(self.grammars_dir, self.queries_dir),
            'css': CssParser(self.grammars_dir, self.queries_dir),
            'vue': VueParser(self.grammars_dir, self.queries_dir),
            'solidity': SolidityParser(self.grammars_dir, self.queries_dir),
            'zig': ZigParser(self.grammars_dir, self.queries_dir),
            'elixir': ElixirParser(self.grammars_dir, self.queries_dir),
            'ocaml': OcamlParser(self.grammars_dir, self.queries_dir),
            'elisp': ElispParser(self.grammars_dir, self.queries_dir),
            'systemrdl': SystemRdlParser(self.grammars_dir,
                                       self.queries_dir),
            'tlaplus': TlaplusParser(self.grammars_dir, self.queries_dir),
            'bash': BashParser(self.grammars_dir, self.queries_dir),
        }
    
    def _get_language_parser(self, language: str) -> Optional[ComprehensiveParser]:
        """Get language-specific parser instance."""
        # First try to get from our initialized parsers
        parser = self.language_parsers.get(language)
        if parser:
            return parser
        
        # Fallback to factory if not found
        try:
            from .language_parser_factory import LanguageParserFactory
            return LanguageParserFactory.get_parser(language)
        except ImportError:
            return None 