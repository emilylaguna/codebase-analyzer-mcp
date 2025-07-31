import tree_sitter
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
import logging
import os
import platform
import re

logger = logging.getLogger(__name__)


class CodeParser:
    def __init__(self, grammars_dir: str = "grammars", queries_dir: str = "queries_scm"):
        """
        Initialize the code parser with Tree-sitter grammars and queries.
        
        Args:
            grammars_dir: Directory containing Tree-sitter WASM grammars
            queries_dir: Directory containing language-specific SCM query files
        """
        self.grammars_dir = Path(grammars_dir)
        self.queries_dir = Path(queries_dir)
        self.language_map = self._build_language_map()
        self.parsers: Dict[str, tree_sitter.Parser] = {}
        self.queries: Dict[str, str] = {}
        self.relationship_queries: Dict[str, str] = {}
        
    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names."""
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
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """
        Detect the language for a given file based on its extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Language name or None if not supported
        """
        ext = Path(file_path).suffix.lower()
        return self.language_map.get(ext)
    
    def _load_parser(self, language: str) -> Optional[tree_sitter.Parser]:
        """
        Load Tree-sitter parser for a specific language.
        
        Args:
            language: Language name
            
        Returns:
            Tree-sitter parser or None if not available
        """
        if language in self.parsers:
            return self.parsers[language]
        
        try:
            # Try to import the language package
            module_name = f"tree_sitter_{language}"
            try:
                lang_module = __import__(module_name)
                language_obj = tree_sitter.Language(lang_module.language())
            except ImportError:
                logger.error(f"Language package '{module_name}' not found. Install it with: pip install {module_name}")
                return None
            
            parser = tree_sitter.Parser()
            parser.language = language_obj
            
            self.parsers[language] = parser
            logger.info(f"Loaded parser for language: {language}")
            return parser
            
        except Exception as e:
            logger.error(f"Error loading parser for {language}: {e}")
            return None
    
    def _load_query(self, language: str) -> Optional[str]:
        """
        Load SCM query file for a specific language.
        
        Args:
            language: Language name
            
        Returns:
            Query string or None if not available
        """
        if language in self.queries:
            return self.queries[language]
        
        try:
            # Try minimal query first for problematic languages
            query_path = self.queries_dir / f"{language}.scm"
            logger.info(f"Loading query for language: {language} from {query_path}")
            with open(query_path, 'r', encoding='utf-8') as f:
                query = f.read().strip()
            
            self.queries[language] = query
            logger.info(f"Loaded query for language: {language}")
            return query
            
        except Exception as e:
            logger.error(f"Error loading query for {language}: {e}")
            return None
    
    def parse_file(self, file_path: str) -> List[Dict]:
        """
        Parse a file and extract symbols.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            List of symbol dictionaries
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return []
        
        language = self.detect_language(file_path)
        if not language:
            logger.warning(f"Could not detect language for {file_path}")
            return []
        
        parser = self._load_parser(language)
        if not parser:
            logger.warning(f"Could not load parser for language {language}")
            return []
        
        try:
            tree = parser.parse(bytes(content, 'utf8'))
            query = self._load_query(language)
            if not query:
                logger.warning(f"Could not load query for language {language}")
                return []
            
            # Extract symbols
            symbols = self._extract_symbols(tree, query, content, language, file_path)
            
            # Extract relationships
            relationships = self._extract_relationships(tree, content, language, file_path, symbols)
            
            # Add relationship info to symbols
            for symbol in symbols:
                symbol['relationships'] = relationships.get(symbol['name'], [])
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            return []
    
    def _extract_symbols(self, tree: tree_sitter.Tree, query: str, content: str, 
                        language: str, file_path: str) -> List[Dict]:
        """
        Extract symbols from the parse tree using the query.
        
        Args:
            tree: Tree-sitter parse tree
            query: Query string for extracting symbols
            content: File content
            language: Programming language
            file_path: Path to the file
            
        Returns:
            List of symbol dictionaries
        """
        try:
            # Try to use Tree-sitter query first
            symbols = self._extract_symbols_with_query(tree, query, content, language, file_path)
            
            # If Tree-sitter query extraction fails or returns no symbols, fall back to regex
            if not symbols:
                logger.info(f"Tree-sitter query extraction failed for {language}, falling back to regex")
                lines = content.split('\n')
                
                # Language-specific regex patterns
                if language == 'python':
                    symbols.extend(self._extract_python_symbols(lines, file_path, language))
                elif language == 'swift':
                    symbols.extend(self._extract_swift_symbols(lines, file_path, language))
                elif language in ['javascript', 'typescript', 'tsx']:
                    symbols.extend(self._extract_js_symbols(lines, file_path, language))
                elif language == 'java':
                    symbols.extend(self._extract_java_symbols(lines, file_path, language))
                elif language in ['c', 'cpp']:
                    symbols.extend(self._extract_cpp_symbols(lines, file_path, language))
                elif language == 'c_sharp':
                    symbols.extend(self._extract_csharp_symbols(lines, file_path, language))
                elif language == 'go':
                    symbols.extend(self._extract_go_symbols(lines, file_path, language))
                elif language == 'rust':
                    symbols.extend(self._extract_rust_symbols(lines, file_path, language))
                else:
                    # Fallback: try to extract basic symbols for any language
                    symbols.extend(self._extract_generic_symbols(lines, file_path, language))
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error extracting symbols: {e}")
            return []
    
    def _extract_symbols_with_query(self, tree: tree_sitter.Tree, query: str, content: str, 
                                   language: str, file_path: str) -> List[Dict]:
        """
        Extract symbols using Tree-sitter query.
        
        Args:
            tree: Tree-sitter parse tree
            query: Query string for extracting symbols
            content: File content
            language: Programming language
            file_path: Path to the file
            
        Returns:
            List of symbol dictionaries
        """
        try:
            # Get the language object from the tree
            language_obj = tree.language
            
            # Create a query object
            query_obj = tree_sitter.Query(language_obj, query)
            
            # Execute the query using QueryCursor
            query_cursor = tree_sitter.QueryCursor(query_obj)
            captures = query_cursor.captures(tree.root_node)
            
            symbols = []
            lines = content.split('\n')
            
            # captures is a dictionary where keys are capture names and values are lists of nodes
            for capture_name, nodes in captures.items():
                for node in nodes:
                    symbol_info = self._extract_symbol_info(node, capture_name, lines, language, file_path)
                    if symbol_info:
                        symbols.append(symbol_info)
            
            logger.info(f"Extracted {len(symbols)} symbols using Tree-sitter query for {language}")
            return symbols
            
        except Exception as e:
            logger.error(f"Error extracting symbols with Tree-sitter query: {e}")
            return []
    
    def _extract_python_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract Python symbols using regex patterns."""
        import re
        symbols = []
        
        # Find function definitions
        func_pattern = r'^def\s+(\w+)\s*\('
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
        
        return symbols
    
    def _extract_swift_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract Swift symbols using regex patterns."""
        import re
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
    
    def _extract_js_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract JavaScript/TypeScript symbols using regex patterns."""
        import re
        symbols = []
        
        # Find function declarations
        func_pattern = r'^function\s+(\w+)\s*\('
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
        
        # Find arrow functions and const functions
        arrow_pattern = r'^const\s+(\w+)\s*=\s*\([^)]*\)\s*=>'
        for i, line in enumerate(lines):
            match = re.match(arrow_pattern, line.strip())
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
        
        return symbols
    
    def _extract_java_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract Java symbols using regex patterns."""
        import re
        symbols = []
        
        # Find method definitions
        method_pattern = r'^\s*(?:public|private|protected)?\s*(?:static\s+)?(?:final\s+)?(?:synchronized\s+)?(?:native\s+)?(?:abstract\s+)?(?:strictfp\s+)?(?:<[^>]+>\s+)?(?:[\w\[\]]+\s+)?(\w+)\s*\([^)]*\)'
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
    
    def _extract_cpp_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract C/C++ symbols using regex patterns."""
        import re
        symbols = []
        
        # Find function definitions
        func_pattern = r'^(?:[\w\*&\s]+\s+)?(\w+)\s*\([^)]*\)\s*(?:const\s*)?(?:override\s*)?(?:noexcept\s*)?(?:=\s*(?:0|default|delete)\s*)?;?$'
        for i, line in enumerate(lines):
            match = re.match(func_pattern, line.strip())
            if match:
                func_name = match.group(1)
                # Skip common C++ keywords
                if func_name not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'class', 'struct', 'enum', 'namespace', 'template', 'typename']:
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
        class_pattern = r'^(?:class|struct)\s+(\w+)'
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
        
        return symbols
    
    def _extract_csharp_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract C# symbols using regex patterns."""
        import re
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
    
    def _extract_go_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract Go symbols using regex patterns."""
        import re
        symbols = []
        
        # Find function definitions
        func_pattern = r'^func\s+(?:\(\s*[\w\*]+\s+[\w\*]+\s*\)\s+)?(\w+)\s*\('
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
        
        # Find type definitions
        type_pattern = r'^type\s+(\w+)'
        for i, line in enumerate(lines):
            match = re.match(type_pattern, line.strip())
            if match:
                type_name = match.group(1)
                symbols.append({
                    'name': type_name,
                    'symbol_type': 'type',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def _extract_rust_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract Rust symbols using regex patterns."""
        import re
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
    
    def _extract_generic_symbols(self, lines: List[str], file_path: str, language: str) -> List[Dict]:
        """Extract generic symbols for unsupported languages."""
        import re
        symbols = []
        
        # Try to find function-like patterns
        func_patterns = [
            r'^def\s+(\w+)',  # Python
            r'^func\s+(\w+)',  # Swift, Go
            r'^function\s+(\w+)',  # JavaScript
            r'^fn\s+(\w+)',  # Rust
            r'^(\w+)\s*\([^)]*\)\s*{',  # Generic function
        ]
        
        for pattern in func_patterns:
            for i, line in enumerate(lines):
                match = re.match(pattern, line.strip())
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
        
        # Try to find class-like patterns
        class_patterns = [
            r'^class\s+(\w+)',  # Python, JavaScript, Java, C#
            r'^struct\s+(\w+)',  # Swift, Rust, C++
            r'^trait\s+(\w+)',  # Rust
            r'^protocol\s+(\w+)',  # Swift
            r'^interface\s+(\w+)',  # Java, C#
        ]
        
        for pattern in class_patterns:
            for i, line in enumerate(lines):
                match = re.match(pattern, line.strip())
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
        
        return symbols
    
    def _extract_symbol_info(self, node: tree_sitter.Node, capture_name: str, 
                           lines: List[str], language: str, file_path: str) -> Optional[Dict]:
        """
        Extract information about a symbol from a parse tree node.
        
        Args:
            node: Tree-sitter node
            capture_name: Name of the capture
            lines: File content as list of lines
            language: Programming language
            file_path: Path to the file
            
        Returns:
            Symbol information dictionary or None
        """
        try:
            # Get symbol name
            name = self._extract_symbol_name(node, capture_name, language)
            if not name:
                return None
            
            # Get symbol type
            symbol_type = self._get_symbol_type(capture_name)
            
            # Special handling for Swift type declarations
            if language == 'swift' and symbol_type in ['class', 'struct', 'enum', 'actor', 'extension']:
                # For Swift type declarations, we need to get the actual declaration kind
                # Find the parent class_declaration node
                current_node = node
                while current_node and current_node.type != 'class_declaration':
                    current_node = current_node.parent
                
                if current_node:
                    declaration_kind = self._extract_swift_declaration_kind(current_node)
                    if declaration_kind:
                        symbol_type = declaration_kind
            
            # Get line numbers
            line_start = node.start_point[0] + 1
            line_end = node.end_point[0] + 1
            
            # Get code snippet
            code_snippet = node.text.decode('utf-8') if node.text else ""
            
            return {
                'name': name,
                'symbol_type': symbol_type,
                'line_start': line_start,
                'line_end': line_end,
                'code_snippet': code_snippet,
                'language': language,
                'file_path': file_path,
                'file_hash': ''  # Will be set by the main processing code
            }
            
        except Exception as e:
            logger.error(f"Error extracting symbol info: {e}")
            return None
    
    def _extract_symbol_name(self, node: tree_sitter.Node, capture_name: str, 
                           language: str) -> Optional[str]:
        """
        Extract the name of a symbol from a parse tree node.
        
        Args:
            node: Tree-sitter node
            capture_name: Name of the capture
            language: Programming language
            
        Returns:
            Symbol name or None
        """
        try:
            # For most cases, the node text is the name
            name = node.text.decode('utf-8') if node.text else ""
            
            # Clean up the name
            name = name.strip()
            
            # For Tree-sitter queries, we need to extract just the symbol name
            # The node might contain the entire definition, so we need to parse it
            
            # Handle different capture types
            if capture_name == 'name':
                # This is a name capture, so the node text should be the name
                return name if name else None
            elif capture_name.startswith('definition.'):
                # This is a definition capture, we need to extract the name from the definition
                if language == 'swift':
                    # For Swift, look for patterns like "class Name", "func Name", "struct Name"
                    import re
                    
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
                        if word and word[0].isalpha() and word not in ['public', 'private', 'class', 'struct', 'func', 'let', 'var', 'init']:
                            return word
                
                # For other languages, try generic patterns
                import re
                
                # Remove common prefixes/suffixes
                if name.startswith('def '):
                    name = name[4:]
                elif name.startswith('class '):
                    name = name[6:]
                elif name.startswith('function '):
                    name = name[9:]
                elif name.startswith('func '):
                    name = name[5:]
                
                # Extract first word as name
                words = name.split()
                if words:
                    return words[0]
            
            return name if name else None
            
        except Exception as e:
            logger.error(f"Error extracting symbol name: {e}")
            return None
    
    def _extract_swift_declaration_kind(self, node: tree_sitter.Node) -> Optional[str]:
        """
        Extract the declaration_kind from a Swift class_declaration node.
        
        Args:
            node: Tree-sitter node (should be a class_declaration)
            
        Returns:
            Declaration kind ("class", "struct", "enum", "actor", "extension") or None
        """
        try:
            # Look for the declaration_kind field in the node
            for child in node.children:
                if child.type == 'declaration_kind':
                    return child.text.decode('utf-8')
            
            # If not found, try to infer from the node text
            node_text = node.text.decode('utf-8') if node.text else ""
            
            # Check for keywords in the text
            if 'class ' in node_text:
                return 'class'
            elif 'struct ' in node_text:
                return 'struct'
            elif 'enum ' in node_text:
                return 'enum'
            elif 'actor ' in node_text:
                return 'actor'
            elif 'extension ' in node_text:
                return 'extension'
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting Swift declaration kind: {e}")
            return None
    
    def _get_symbol_type(self, capture_name: str) -> str:
        """
        Map capture name to symbol type.
        
        Args:
            capture_name: Name of the capture
            
        Returns:
            Symbol type
        """
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
            # Swift-specific capture names from our SCM file
            'class_name': 'class',
            'struct_name': 'struct',
            'enum_name': 'enum',
            'actor_name': 'actor',
            'extension_type_name': 'extension',
            'protocol_name': 'protocol',
            'function_name': 'function',
            'initializer_name': 'initializer',
            'deinitializer_name': 'deinitializer',
            'property_name': 'property',
            'subscript_param_name': 'subscript',
            'type_alias_name': 'type_alias',
            'attribute_name': 'attribute'
        }
        
        # Special handling for Swift: @name captures in property patterns should be variables
        if capture_name == 'name':
            return 'variable'
        
        return type_mapping.get(capture_name, 'unknown')
    
    def _extract_relationships(self, tree: tree_sitter.Tree, content: str, 
                             language: str, file_path: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Extract relationships between symbols in the code.
        
        Args:
            tree: Tree-sitter parse tree
            content: File content
            language: Programming language
            file_path: Path to the file
            symbols: List of extracted symbols
            
        Returns:
            Dictionary mapping symbol names to their relationships
        """
        relationships = {}
        
        # Create symbol lookup by name and line
        symbol_lookup = {}
        for symbol in symbols:
            key = (symbol['name'], symbol['line_start'])
            symbol_lookup[key] = symbol
        
        # Language-specific relationship extraction
        if language == 'python':
            relationships.update(self._extract_python_relationships_simple(content, symbols))
        elif language == 'swift':
            relationships.update(self._extract_swift_relationships_simple(content, symbols))
        elif language in ['javascript', 'typescript', 'tsx']:
            relationships.update(self._extract_js_relationships_simple(content, symbols))
        elif language == 'java':
            relationships.update(self._extract_java_relationships_simple(content, symbols))
        elif language in ['c', 'cpp']:
            relationships.update(self._extract_cpp_relationships_simple(content, symbols))
        elif language == 'c_sharp':
            relationships.update(self._extract_csharp_relationships_simple(content, symbols))
        elif language == 'go':
            relationships.update(self._extract_go_relationships_simple(content, symbols))
        elif language == 'rust':
            relationships.update(self._extract_rust_relationships_simple(content, symbols))
        else:
            # Fallback: try generic relationship extraction
            relationships.update(self._extract_generic_relationships_simple(content, symbols))
        
        return relationships
    
    def _extract_python_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Python relationships using regex patterns."""
        import re
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common Python keywords and built-ins
                if func_call not in ['if', 'for', 'while', 'with', 'def', 'class', 'import', 'from', 'return', 'print']:
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
        
        # Find class inheritance
        for i, line in enumerate(lines):
            inheritance_match = re.match(r'^class\s+(\w+)\s*\(([^)]+)\)', line.strip())
            if inheritance_match:
                class_name = inheritance_match.group(1)
                parent_name = inheritance_match.group(2).strip()
                
                if class_name not in relationships:
                    relationships[class_name] = []
                relationships[class_name].append({
                    'type': 'inherits',
                    'target': parent_name,
                    'target_type': 'class',
                    'line': i + 1
                })
        
        return relationships
    
    def _extract_swift_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Swift relationships using regex patterns."""
        import re
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common Swift keywords
                if func_call not in ['if', 'for', 'while', 'switch', 'guard', 'func', 'class', 'struct', 'enum', 'protocol', 'import', 'return', 'print']:
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
            inheritance_match = re.match(r'^class\s+(\w+)\s*:\s*(\w+)', line.strip())
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
            protocol_match = re.match(r'^class\s+(\w+)\s*,\s*(\w+)', line.strip())
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
    
    def _extract_js_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract JavaScript/TypeScript relationships using regex patterns."""
        import re
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common JS keywords
                if func_call not in ['if', 'for', 'while', 'switch', 'function', 'class', 'import', 'export', 'return', 'console']:
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
        
        # Find class inheritance
        for i, line in enumerate(lines):
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
        
        return relationships
    
    def _extract_java_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Java relationships using regex patterns."""
        import re
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
    
    def _extract_cpp_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract C/C++ relationships using regex patterns."""
        import re
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common C++ keywords
                if func_call not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'class', 'struct', 'enum', 'namespace', 'template', 'typename', 'return']:
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
        
        # Find class inheritance
        for i, line in enumerate(lines):
            inheritance_match = re.match(r'^class\s+(\w+)\s*:\s*(?:public\s+)?(\w+)', line.strip())
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
        
        return relationships
    
    def _extract_csharp_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract C# relationships using regex patterns."""
        import re
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
    
    def _extract_go_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Go relationships using regex patterns."""
        import re
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common Go keywords
                if func_call not in ['if', 'for', 'range', 'switch', 'select', 'func', 'type', 'struct', 'interface', 'import', 'return', 'fmt']:
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
        
        return relationships
    
    def _extract_rust_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Rust relationships using regex patterns."""
        import re
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
    
    def _extract_generic_relationships_simple(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract generic relationships for unsupported languages."""
        import re
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find function calls (generic pattern)
        for i, line in enumerate(lines):
            func_calls = re.findall(r'(\w+)\s*\(', line)
            for func_call in func_calls:
                # Skip common keywords
                if func_call not in ['if', 'for', 'while', 'switch', 'try', 'catch', 'return', 'print', 'console']:
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
        
        return relationships 