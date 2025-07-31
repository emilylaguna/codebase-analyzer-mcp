; Bash Tree-sitter Queries for Codebase Analysis
; Comprehensive version with all major bash constructs

; =============================================================================
; FUNCTION DEFINITIONS
; =============================================================================

; Function definitions (both styles)
(function_definition
  (word) @function.name)

; =============================================================================
; VARIABLE DECLARATIONS AND ASSIGNMENTS
; =============================================================================

; Variable assignments
(variable_assignment
  (variable_name) @variable.name)

; Variable declarations with declare/export/local/etc
(declaration_command
  (variable_assignment
    (variable_name) @variable.name))

; Variable assignments in commands
(command
  (variable_assignment
    (variable_name) @variable.name))

; =============================================================================
; COMMANDS AND PIPELINES
; =============================================================================

; Simple commands
(command
  (command_name) @command.name)

; Pipelines
(pipeline) @pipeline

; Lists (&& and ||)
(list) @list

; Negated commands
(negated_command) @negated.command

; =============================================================================
; CONTROL STRUCTURES
; =============================================================================

; If statements
(if_statement) @if.statement

; Elif clauses
(elif_clause) @elif.clause

; Else clauses
(else_clause) @else.clause

; For loops
(for_statement) @for.statement

; C-style for loops
(c_style_for_statement) @c.for.statement

; While loops
(while_statement) @while.statement

; Case statements
(case_statement) @case.statement

; Case items
(case_item) @case.item

; Do groups
(do_group) @do.group

; =============================================================================
; TEST COMMANDS
; =============================================================================

; Test commands [ ], [[ ]], (( ))
(test_command) @test.command

; =============================================================================
; STRINGS AND LITERALS
; =============================================================================

; String literals
(string
  (string_content) @string.content)

; Raw strings
(raw_string) @raw.string

; Translated strings
(translated_string) @translated.string

; ANSI C strings
(ansi_c_string) @ansi.string

; Number literals
(number) @number

; =============================================================================
; VARIABLE EXPANSIONS
; =============================================================================

; Simple variable expansions
(simple_expansion
  (variable_name) @variable.expansion)

; Complex expansions
(expansion) @expansion

; Arithmetic expansions
(arithmetic_expansion) @arithmetic.expansion

; Command substitutions
(command_substitution) @command.substitution

; Process substitutions
(process_substitution) @process.substitution

; =============================================================================
; ARRAYS AND SUBSCRIPTS
; =============================================================================

; Array definitions
(array) @array

; Array subscripts
(subscript) @subscript

; =============================================================================
; REDIRECTIONS
; =============================================================================

; File redirects
(file_redirect) @file.redirect

; Heredoc redirects
(heredoc_redirect) @heredoc.redirect

; Here string redirects
(herestring_redirect) @herestring.redirect

; Redirected statements
(redirected_statement) @redirected.statement

; =============================================================================
; EXPRESSIONS
; =============================================================================

; Binary expressions
(binary_expression) @binary.expression

; Unary expressions
(unary_expression) @unary.expression

; Ternary expressions
(ternary_expression) @ternary.expression

; Postfix expressions
(postfix_expression) @postfix.expression

; Parenthesized expressions
(parenthesized_expression) @parenthesized.expression

; =============================================================================
; COMPOUND STATEMENTS
; =============================================================================

; Compound statements (curly braces)
(compound_statement) @compound.statement

; Subshells
(subshell) @subshell

; =============================================================================
; BRACE EXPRESSIONS
; =============================================================================

; Brace expressions {1..10}
(brace_expression) @brace.expression

; =============================================================================
; COMMENTS AND SHEBANGS
; =============================================================================

; Comments
(comment) @comment

; =============================================================================
; UTILITY PATTERNS
; =============================================================================

; Word patterns for general identifiers
(word) @identifier

; Command names
(command_name) @command.name

; Variable names
(variable_name) @variable.name

; File descriptors
(file_descriptor) @file.descriptor

; Test operators
(test_operator) @test.operator

; Regex patterns
(regex) @regex

; Extglob patterns
(extglob_pattern) @extglob.pattern

; =============================================================================
; SPECIAL PATTERNS
; =============================================================================

; Concatenations
(concatenation) @concatenation

; Unset commands
(unset_command) @unset.command

; Declaration commands (declare, export, etc.)
(declaration_command) @declaration.command
