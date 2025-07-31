import tree_sitter
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BaseParser:
    def __init__(self, grammars_dir: str = "grammars", 
                 queries_dir: str = "queries_scm"):
        """
        Initialize the base parser with Tree-sitter grammars and queries.
        
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
        # This should be overridden by language-specific parsers
        return {}
    
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
                
                # Get language-specific parser
                parser = self._get_language_parser(language)
                if parser:
                    symbols.extend(parser.extract_symbols_regex(lines, file_path, language))
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
            symbol_type = self._get_symbol_type(capture_name, language)
            
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
            
            # Get language-specific parser for better name extraction
            parser = self._get_language_parser(language)
            if parser:
                # Try language-specific symbol name extraction first
                if hasattr(parser, '_extract_bash_symbol_name') and language == 'bash':
                    return parser._extract_bash_symbol_name(node, capture_name, name)
                elif hasattr(parser, 'extract_symbol_name_from_definition'):
                    return parser.extract_symbol_name_from_definition(name, capture_name)
            
            # For Tree-sitter queries, we need to extract just the symbol name
            # The node might contain the entire definition, so we need to parse it
            
            # Handle different capture types
            if capture_name == 'name':
                # This is a name capture, so the node text should be the name
                return name if name else None
            elif capture_name.startswith('definition.'):
                # This is a definition capture, we need to extract the name from the definition
                # Fallback for other languages
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
    
    def _get_symbol_type(self, capture_name: str, language: str) -> str:
        """
        Map capture name to symbol type.
        
        Args:
            capture_name: Name of the capture
            language: Programming language
            
        Returns:
            Symbol type
        """

        
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
        # Get language-specific parser
        parser = self._get_language_parser(language)
        if parser:
            return parser.extract_relationships(content, symbols)
        else:
            # Fallback: try generic relationship extraction
            return self._extract_generic_relationships_simple(content, symbols)
    
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
    
    def _get_language_parser(self, language: str):
        """Get language-specific parser instance."""
        try:
            from .language_parser_factory import LanguageParserFactory
            return LanguageParserFactory.get_parser(language)
        except ImportError:
            # Fallback if factory is not available
            return None 