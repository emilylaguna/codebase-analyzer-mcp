; =============================================================================
; Markdown Tree-sitter Query File
; Comprehensive queries for extracting Markdown structure and elements
; =============================================================================

; =============================================================================
; HEADINGS
; =============================================================================

; ATX headings (hash-based)
(atx_heading) @definition.heading

(atx_heading
  (atx_h1_marker)) @definition.heading.h1

(atx_heading
  (atx_h2_marker)) @definition.heading.h2

(atx_heading
  (atx_h3_marker)) @definition.heading.h3

(atx_heading
  (atx_h4_marker)) @definition.heading.h4

(atx_heading
  (atx_h5_marker)) @definition.heading.h5

(atx_heading
  (atx_h6_marker)) @definition.heading.h6

; Setext headings (underline-based)
(setext_heading) @definition.heading

(setext_heading
  (setext_h1_underline)) @definition.heading.h1

(setext_heading
  (setext_h2_underline)) @definition.heading.h2

; =============================================================================
; LISTS
; =============================================================================

; List containers
(list) @definition.list

; List items
(list_item) @definition.list_item

; List markers
(list_marker_minus) @definition.list_marker.unordered
(list_marker_plus) @definition.list_marker.unordered
(list_marker_star) @definition.list_marker.unordered
(list_marker_dot) @definition.list_marker.ordered
(list_marker_parenthesis) @definition.list_marker.ordered

; Task list markers
(task_list_marker_checked) @definition.task_list_marker.checked
(task_list_marker_unchecked) @definition.task_list_marker.unchecked

; =============================================================================
; CODE BLOCKS
; =============================================================================

; Fenced code blocks
(fenced_code_block) @definition.code_block.fenced

(fenced_code_block
  (fenced_code_block_delimiter)) @definition.code_block.delimiter

(fenced_code_block
  (info_string)) @definition.code_block.language

(fenced_code_block
  (code_fence_content)) @definition.code_block.content

; Indented code blocks
(indented_code_block) @definition.code_block.indented

; =============================================================================
; TABLES
; =============================================================================

; Pipe tables
(pipe_table) @definition.table

(pipe_table
  (pipe_table_header)) @definition.table.header

(pipe_table
  (pipe_table_row)) @definition.table.row

(pipe_table
  (pipe_table_delimiter_row)) @definition.table.delimiter_row

(pipe_table_header
  (pipe_table_cell)) @definition.table.header_cell

(pipe_table_row
  (pipe_table_cell)) @definition.table.cell

(pipe_table_delimiter_row
  (pipe_table_delimiter_cell)) @definition.table.delimiter_cell

; Table alignment
(pipe_table_align_left) @definition.table.alignment.left
(pipe_table_align_right) @definition.table.alignment.right

; =============================================================================
; BLOCKQUOTES
; =============================================================================

; Block quotes
(block_quote) @definition.blockquote

(block_quote
  (block_quote_marker)) @definition.blockquote.marker

; =============================================================================
; PARAGRAPHS AND TEXT
; =============================================================================

; Paragraphs
(paragraph) @definition.paragraph

; Inline content
(inline) @definition.inline

; =============================================================================
; LINKS AND REFERENCES
; =============================================================================

; Link reference definitions
(link_reference_definition) @definition.link_reference

(link_reference_definition
  (link_label)) @definition.link_reference.label

(link_reference_definition
  (link_destination)) @definition.link_reference.destination

(link_reference_definition
  (link_title)) @definition.link_reference.title

; Link components
(link_label) @definition.link.label
(link_destination) @definition.link.destination
(link_title) @definition.link.title

; =============================================================================
; THEMATIC BREAKS
; =============================================================================

; Thematic breaks (horizontal rules)
(thematic_break) @definition.thematic_break

; =============================================================================
; HTML BLOCKS
; =============================================================================

; HTML blocks
(html_block) @definition.html_block

; =============================================================================
; METADATA
; =============================================================================

; Metadata blocks
(minus_metadata) @definition.metadata.minus
(plus_metadata) @definition.metadata.plus

; =============================================================================
; ESCAPES AND ENTITIES
; =============================================================================

; Backslash escapes
(backslash_escape) @definition.escape.backslash

; Entity references
(entity_reference) @definition.escape.entity

; Numeric character references
(numeric_character_reference) @definition.escape.numeric

; =============================================================================
; LANGUAGE SPECIFICATIONS
; =============================================================================

; Language specifications in code blocks
(language) @definition.language

; =============================================================================
; BLOCK CONTINUATIONS
; =============================================================================

; Block continuations (for multi-line elements)
(block_continuation) @definition.block_continuation

; =============================================================================
; RELATIONSHIP QUERIES
; =============================================================================

; Document structure
(document) @definition.document

; Sections
(section) @definition.section

; Nested lists
(list
  (list_item
    (list))) @relationship.nested_list

; Nested blockquotes
(block_quote
  (block_quote)) @relationship.nested_blockquote

; Headings within sections
(section
  (atx_heading)) @relationship.heading_in_section

(section
  (setext_heading)) @relationship.heading_in_section

; Lists within sections
(section
  (list)) @relationship.list_in_section

; Code blocks within sections
(section
  (fenced_code_block)) @relationship.code_block_in_section

(section
  (indented_code_block)) @relationship.code_block_in_section

; Tables within sections
(section
  (pipe_table)) @relationship.table_in_section

; Blockquotes within sections
(section
  (block_quote)) @relationship.blockquote_in_section

; Paragraphs within sections
(section
  (paragraph)) @relationship.paragraph_in_section

; =============================================================================
; ADVANCED PATTERNS
; =============================================================================

; Mixed content in paragraphs
(paragraph
  (inline)) @definition.paragraph_content

; Code blocks with language specification
(fenced_code_block
  (info_string
    (language))) @definition.code_block_with_language

; Tables with alignment
(pipe_table_delimiter_cell
  (pipe_table_align_left)) @definition.table_cell_aligned_left

(pipe_table_delimiter_cell
  (pipe_table_align_right)) @definition.table_cell_aligned_right

; Task lists with nested content
(list_item
  (task_list_marker_checked)
  (paragraph)) @definition.task_list_item_checked

(list_item
  (task_list_marker_unchecked)
  (paragraph)) @definition.task_list_item_unchecked

; =============================================================================
; STRUCTURAL PATTERNS
; =============================================================================

; Document with metadata
(document
  (minus_metadata)) @definition.document_with_metadata

(document
  (plus_metadata)) @definition.document_with_metadata

; Document with sections
(document
  (section)) @definition.document_with_sections

; Section with multiple elements
(section
  (atx_heading)
  (paragraph)) @relationship.heading_with_content

(section
  (setext_heading)
  (paragraph)) @relationship.heading_with_content

; =============================================================================
; CONTENT EXTRACTION PATTERNS
; =============================================================================

; Extract heading content
(atx_heading
  heading_content: (inline)) @definition.heading_content

(setext_heading
  heading_content: (paragraph)) @definition.heading_content

; Extract list item content
(list_item
  (paragraph)) @definition.list_item_content

; Extract blockquote content
(block_quote
  (paragraph)) @definition.blockquote_content

; Extract table cell content
(pipe_table_cell) @definition.table_cell_content

; Extract code block content
(fenced_code_block
  (code_fence_content)) @definition.code_block_content

(indented_code_block) @definition.code_block_content

; =============================================================================
; MARKER PATTERNS
; =============================================================================

; Heading markers
(atx_h1_marker) @definition.marker.heading.h1
(atx_h2_marker) @definition.marker.heading.h2
(atx_h3_marker) @definition.marker.heading.h3
(atx_h4_marker) @definition.marker.heading.h4
(atx_h5_marker) @definition.marker.heading.h5
(atx_h6_marker) @definition.marker.heading.h6

; List markers
(list_marker_minus) @definition.marker.list.unordered
(list_marker_plus) @definition.marker.list.unordered
(list_marker_star) @definition.marker.list.unordered
(list_marker_dot) @definition.marker.list.ordered
(list_marker_parenthesis) @definition.marker.list.ordered

; Task list markers
(task_list_marker_checked) @definition.marker.task_list.checked
(task_list_marker_unchecked) @definition.marker.task_list.unchecked

; Blockquote markers
(block_quote_marker) @definition.marker.blockquote

; Code block delimiters
(fenced_code_block_delimiter) @definition.marker.code_block

; Table delimiters
(pipe_table_delimiter_row) @definition.marker.table

; Thematic break markers
(thematic_break) @definition.marker.thematic_break

; =============================================================================
; COMPOSITE PATTERNS
; =============================================================================

; Complete document structure
(document
  (section
    (atx_heading)
    (paragraph)
    (list)
    (block_quote)
    (fenced_code_block)
    (pipe_table)
    (thematic_break))) @definition.complete_document

; Section with all major elements
(section
  (atx_heading)
  (paragraph)
  (list)
  (block_quote)
  (fenced_code_block)
  (pipe_table)
  (thematic_break)) @definition.complete_section

; =============================================================================
; SPECIALIZED PATTERNS
; =============================================================================

; Code blocks with specific languages
(fenced_code_block
  (info_string
    (language) @language.name)) @definition.code_block.language_specific

; Tables with specific alignments
(pipe_table_delimiter_cell
  (pipe_table_align_left)
  (pipe_table_align_right)) @definition.table.mixed_alignment

; Nested structures
(list_item
  (list
    (list_item))) @definition.nested_list_item

(block_quote
  (block_quote
    (paragraph))) @definition.nested_blockquote_content

; =============================================================================
; REFERENCE PATTERNS
; =============================================================================

; Link references
(link_reference_definition
  (link_label) @reference.link.label
  (link_destination) @reference.link.destination
  (link_title) @reference.link.title) @reference.link_definition

; =============================================================================
; UTILITY PATTERNS
; =============================================================================

; All named nodes for general extraction
(atx_heading) @extraction.all
(setext_heading) @extraction.all
(list) @extraction.all
(list_item) @extraction.all
(fenced_code_block) @extraction.all
(indented_code_block) @extraction.all
(pipe_table) @extraction.all
(block_quote) @extraction.all
(paragraph) @extraction.all
(inline) @extraction.all
(thematic_break) @extraction.all
(html_block) @extraction.all
(link_reference_definition) @extraction.all
(minus_metadata) @extraction.all
(plus_metadata) @extraction.all
(document) @extraction.all
(section) @extraction.all 