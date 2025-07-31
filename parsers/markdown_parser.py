import re
from typing import List, Dict, Optional
from .base_parser import BaseParser


class MarkdownParser(BaseParser):
    """Markdown-specific parser for extracting symbols and relationships."""
    
    def _build_language_map(self) -> Dict[str, str]:
        """Build mapping from file extensions to language names for Markdown."""
        return {
            '.md': 'markdown',
            '.markdown': 'markdown',
            '.mdown': 'markdown',
            '.mkd': 'markdown',
            '.mkdn': 'markdown',
            '.mdwn': 'markdown',
            '.mdtxt': 'markdown',
            '.mdtext': 'markdown',
        }
    
    def _get_symbol_type(self, capture_name: str, language: str) -> Optional[str]:
        """Map capture name to symbol type for Markdown."""
        # Handle Tree-sitter query capture names
        if capture_name.startswith('definition.'):
            return capture_name.split('.')[1]
        
        # Handle direct capture names
        type_mapping = {
            'heading': 'heading',
            'list': 'list',
            'list_item': 'list_item',
            'code_block': 'code_block',
            'table': 'table',
            'blockquote': 'blockquote',
            'paragraph': 'paragraph',
            'inline': 'inline',
            'thematic_break': 'thematic_break',
            'html_block': 'html_block',
            'link_reference': 'link_reference',
            'metadata': 'metadata',
            'escape': 'escape',
            'language': 'language',
            'block_continuation': 'block_continuation',
            'document': 'document',
            'section': 'section',
            'name': 'variable',  # Default for name captures
        }
        
        return type_mapping.get(capture_name, None)
    
    def extract_symbols_regex(self, lines: List[str], file_path: str,
                            language: str) -> List[Dict]:
        """Extract Markdown symbols using regex patterns."""
        symbols = []
        
        # Find headings (ATX style)
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        for i, line in enumerate(lines):
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                symbols.append({
                    'name': title,
                    'symbol_type': f'heading_h{level}',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find headings (Setext style)
        setext_pattern = r'^(.+)\n([=-]+)$'
        for i, line in enumerate(lines):
            if i < len(lines) - 1:
                combined = line.strip() + '\n' + lines[i + 1].strip()
                match = re.match(setext_pattern, combined)
                if match:
                    title = match.group(1).strip()
                    underline = match.group(2)
                    level = 1 if underline.startswith('=') else 2
                    symbols.append({
                        'name': title,
                        'symbol_type': f'heading_h{level}',
                        'line_start': i + 1,
                        'line_end': i + 2,
                        'code_snippet': f"{line.strip()}\n{lines[i + 1].strip()}",
                        'file_path': file_path,
                        'language': language
                    })
        
        # Find code blocks (fenced)
        code_block_pattern = r'^```(\w*)$'
        in_code_block = False
        code_block_start = 0
        code_block_lang = ''
        
        for i, line in enumerate(lines):
            if not in_code_block:
                match = re.match(code_block_pattern, line.strip())
                if match:
                    in_code_block = True
                    code_block_start = i + 1
                    code_block_lang = match.group(1)
            else:
                if line.strip() == '```':
                    in_code_block = False
                    code_content = '\n'.join(lines[code_block_start:i])
                    symbols.append({
                        'name': f'code_block_{code_block_lang or "text"}',
                        'symbol_type': 'code_block',
                        'line_start': code_block_start,
                        'line_end': i + 1,
                        'code_snippet': f"```{code_block_lang}\n{code_content}\n```",
                        'file_path': file_path,
                        'language': language
                    })
        
        # Find lists
        list_pattern = r'^(\s*)([-*+]|\d+[.)])\s+(.+)$'
        for i, line in enumerate(lines):
            match = re.match(list_pattern, line.strip())
            if match:
                marker = match.group(2)
                content = match.group(3).strip()
                list_type = 'ordered' if marker[0].isdigit() else 'unordered'
                symbols.append({
                    'name': content,
                    'symbol_type': f'list_item_{list_type}',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find task lists
        task_list_pattern = r'^(\s*)([-*+])\s+\[([ xX])\]\s+(.+)$'
        for i, line in enumerate(lines):
            match = re.match(task_list_pattern, line.strip())
            if match:
                marker = match.group(2)
                checked = match.group(3).lower() == 'x'
                content = match.group(4).strip()
                task_status = 'checked' if checked else 'unchecked'
                symbols.append({
                    'name': content,
                    'symbol_type': f'task_list_item_{task_status}',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find blockquotes
        blockquote_pattern = r'^>\s+(.+)$'
        for i, line in enumerate(lines):
            match = re.match(blockquote_pattern, line.strip())
            if match:
                content = match.group(1).strip()
                symbols.append({
                    'name': content,
                    'symbol_type': 'blockquote',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find thematic breaks
        thematic_break_pattern = r'^([*\-_])\s*\1\s*\1\s*$'
        for i, line in enumerate(lines):
            match = re.match(thematic_break_pattern, line.strip())
            if match:
                symbols.append({
                    'name': 'thematic_break',
                    'symbol_type': 'thematic_break',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find link references
        link_ref_pattern = r'^\[([^\]]+)\]:\s*(.+)$'
        for i, line in enumerate(lines):
            match = re.match(link_ref_pattern, line.strip())
            if match:
                label = match.group(1).strip()
                symbols.append({
                    'name': label,
                    'symbol_type': 'link_reference',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        # Find tables
        table_pattern = r'^\|(.+)\|$'
        for i, line in enumerate(lines):
            match = re.match(table_pattern, line.strip())
            if match:
                symbols.append({
                    'name': 'table_row',
                    'symbol_type': 'table',
                    'line_start': i + 1,
                    'line_end': i + 1,
                    'code_snippet': line.strip(),
                    'file_path': file_path,
                    'language': language
                })
        
        return symbols
    
    def extract_relationships(self, content: str, symbols: List[Dict]) -> Dict[str, List[Dict]]:
        """Extract Markdown relationships using regex patterns."""
        relationships: Dict[str, List[Dict]] = {}
        lines = content.split('\n')
        
        # Find links within content
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        for i, line in enumerate(lines):
            links = re.findall(link_pattern, line)
            for link_text, link_url in links:
                # Find which section/heading this link is in
                for symbol in symbols:
                    if symbol['line_start'] <= i + 1 <= symbol['line_end']:
                        if symbol['name'] not in relationships:
                            relationships[symbol['name']] = []
                        relationships[symbol['name']].append({
                            'type': 'link',
                            'target': link_url,
                            'text': link_text,
                            'line': i + 1
                        })
        
        # Find code blocks within sections
        in_code_block = False
        code_block_start = 0
        current_section = None
        
        for i, line in enumerate(lines):
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = i + 1
                    # Find the current section
                    for symbol in symbols:
                        if symbol['symbol_type'].startswith('heading_') and symbol['line_start'] <= i + 1:
                            current_section = symbol['name']
                else:
                    in_code_block = False
                    if current_section:
                        if current_section not in relationships:
                            relationships[current_section] = []
                        relationships[current_section].append({
                            'type': 'contains_code_block',
                            'target': f'code_block_lines_{code_block_start}_{i + 1}',
                            'line_start': code_block_start,
                            'line_end': i + 1
                        })
        
        # Find lists within sections
        for symbol in symbols:
            if symbol['symbol_type'].startswith('list_item_'):
                # Find the parent section/heading
                for section_symbol in symbols:
                    if (section_symbol['symbol_type'].startswith('heading_') and 
                        section_symbol['line_start'] <= symbol['line_start']):
                        if section_symbol['name'] not in relationships:
                            relationships[section_symbol['name']] = []
                        relationships[section_symbol['name']].append({
                            'type': 'contains_list_item',
                            'target': symbol['name'],
                            'line': symbol['line_start']
                        })
        
        return relationships
    
    def extract_symbol_name_from_definition(self, name: str, 
                                          capture_name: str) -> Optional[str]:
        """Extract symbol name from definition for Markdown."""
        # For markdown, the name is often the content itself
        if capture_name.startswith('definition.heading'):
            return name.strip()
        elif capture_name.startswith('definition.list_item'):
            return name.strip()
        elif capture_name.startswith('definition.code_block'):
            return name.strip()
        elif capture_name.startswith('definition.blockquote'):
            return name.strip()
        elif capture_name.startswith('definition.link_reference'):
            return name.strip()
        else:
            return name.strip()
    
    def get_symbol_metadata(self, symbol: Dict, capture_name: str) -> Dict:
        """Get additional metadata for Markdown symbols."""
        metadata = super().get_symbol_metadata(symbol, capture_name)
        
        # Add markdown-specific metadata
        if capture_name.startswith('definition.heading'):
            # Extract heading level
            if 'h1' in capture_name:
                metadata['heading_level'] = 1
            elif 'h2' in capture_name:
                metadata['heading_level'] = 2
            elif 'h3' in capture_name:
                metadata['heading_level'] = 3
            elif 'h4' in capture_name:
                metadata['heading_level'] = 4
            elif 'h5' in capture_name:
                metadata['heading_level'] = 5
            elif 'h6' in capture_name:
                metadata['heading_level'] = 6
        
        elif capture_name.startswith('definition.code_block'):
            metadata['code_block_type'] = 'fenced' if 'fenced' in capture_name else 'indented'
            if 'language' in capture_name:
                metadata['language'] = symbol.get('name', '').split('_')[-1]
        
        elif capture_name.startswith('definition.list_item'):
            if 'ordered' in capture_name:
                metadata['list_type'] = 'ordered'
            elif 'unordered' in capture_name:
                metadata['list_type'] = 'unordered'
            elif 'task' in capture_name:
                metadata['list_type'] = 'task'
                if 'checked' in capture_name:
                    metadata['task_status'] = 'checked'
                else:
                    metadata['task_status'] = 'unchecked'
        
        elif capture_name.startswith('definition.table'):
            metadata['table_type'] = 'pipe_table'
        
        return metadata 