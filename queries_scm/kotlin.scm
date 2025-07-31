; =============================================================================
; Kotlin Tree-sitter Queries
; =============================================================================

; =============================================================================
; DECLARATIONS
; =============================================================================

; Package declarations
(package_header
  (identifier) @name.definition.package
) @definition.package

; Import declarations
(import_header
  (identifier) @name.definition.import
) @definition.import

; Type alias declarations
(type_alias
  (type_identifier) @name.definition.type_alias
) @definition.type_alias

; Class declarations
(class_declaration
  (type_identifier) @name.definition.class
) @definition.class

; Data class declarations
(class_declaration
  (modifiers
    (class_modifier) @_modifier (#eq? @_modifier "data"))
  (type_identifier) @name.definition.data_class
) @definition.data_class

; Abstract class declarations
(class_declaration
  (modifiers
    (inheritance_modifier) @_modifier (#eq? @_modifier "abstract"))
  (type_identifier) @name.definition.abstract_class
) @definition.abstract_class

; Sealed class declarations
(class_declaration
  (modifiers
    (class_modifier) @_modifier (#eq? @_modifier "sealed"))
  (type_identifier) @name.definition.sealed_class
) @definition.sealed_class

; Enum class declarations
(class_declaration
  (type_identifier) @name.definition.enum_class
  (enum_class_body)
) @definition.enum_class

; Enum entries
(enum_entry
  (simple_identifier) @name.definition.enum_entry
) @definition.enum_entry

; Interface declarations (fun interface)
(class_declaration
  (modifiers
    (function_modifier) @_modifier (#eq? @_modifier "fun"))
  (type_identifier) @name.definition.interface
) @definition.interface

; Annotation class declarations
(class_declaration
  (modifiers
    (class_modifier) @_modifier (#eq? @_modifier "annotation"))
  (type_identifier) @name.definition.annotation_class
) @definition.annotation_class

; Object declarations
(object_declaration
  (type_identifier) @name.definition.object
) @definition.object

; Companion object declarations
(companion_object
  (type_identifier)? @name.definition.companion_object
) @definition.companion_object

; Function declarations
(function_declaration
  (simple_identifier) @name.definition.function
) @definition.function

; Suspend function declarations
(function_declaration
  (modifiers
    (function_modifier) @_modifier (#eq? @_modifier "suspend"))
  (simple_identifier) @name.definition.suspend_function
) @definition.suspend_function

; Extension function declarations
(function_declaration
  (receiver_type)
  (simple_identifier) @name.definition.extension_function
) @definition.extension_function

; Operator function declarations
(function_declaration
  (modifiers
    (function_modifier) @_modifier (#eq? @_modifier "operator"))
  (simple_identifier) @name.definition.operator_function
) @definition.operator_function

; Infix function declarations
(function_declaration
  (modifiers
    (function_modifier) @_modifier (#eq? @_modifier "infix"))
  (simple_identifier) @name.definition.infix_function
) @definition.infix_function

; Inline function declarations
(function_declaration
  (modifiers
    (function_modifier) @_modifier (#eq? @_modifier "inline"))
  (simple_identifier) @name.definition.inline_function
) @definition.inline_function

; Tailrec function declarations
(function_declaration
  (modifiers
    (function_modifier) @_modifier (#eq? @_modifier "tailrec"))
  (simple_identifier) @name.definition.tailrec_function
) @definition.tailrec_function

; External function declarations
(function_declaration
  (modifiers
    (function_modifier) @_modifier (#eq? @_modifier "external"))
  (simple_identifier) @name.definition.external_function
) @definition.external_function

; Primary constructor declarations
(primary_constructor) @definition.primary_constructor

; Secondary constructor declarations
(secondary_constructor) @definition.secondary_constructor

; Property declarations
(property_declaration
  (variable_declaration
    (simple_identifier) @name.definition.property)
) @definition.property

; Const property declarations
(property_declaration
  (modifiers
    (property_modifier) @_modifier (#eq? @_modifier "const"))
  (variable_declaration
    (simple_identifier) @name.definition.const_property)
) @definition.const_property

; Lateinit property declarations
(property_declaration
  (modifiers
    (member_modifier) @_modifier (#eq? @_modifier "lateinit"))
  (variable_declaration
    (simple_identifier) @name.definition.lateinit_property)
) @definition.lateinit_property

; Property with accessors
(property_declaration
  (variable_declaration
    (simple_identifier) @name.definition.property)
  (getter)? @definition.getter
  (setter)? @definition.setter
) @definition.property_with_accessors

; Top-level property declarations
(property_declaration
  (variable_declaration
    (simple_identifier) @name.definition.top_level_property)
) @definition.top_level_property

; Variable declarations (in functions, etc.)
(variable_declaration
  (simple_identifier) @name.definition.variable
) @definition.variable

; Parameter declarations
(parameter
  (simple_identifier) @name.definition.parameter
) @definition.parameter

; Type parameter declarations
(type_parameter
  (type_identifier) @name.definition.type_parameter
) @definition.type_parameter

; =============================================================================
; ANNOTATIONS
; =============================================================================

; Annotation usage
(annotation) @definition.annotation_usage

; File annotation
(file_annotation) @definition.file_annotation

; =============================================================================
; EXPRESSIONS AND STATEMENTS
; =============================================================================

; If expressions
(if_expression) @expression.if

; When expressions
(when_expression) @expression.when

; Try expressions
(try_expression) @expression.try

; For loops
(for_statement) @statement.for

; While loops
(while_statement) @statement.while

; Do-while loops
(do_while_statement) @statement.do_while

; Jump expressions (return, break, continue, throw)
(jump_expression) @statement.jump

; =============================================================================
; FUNCTION CALLS AND REFERENCES
; =============================================================================

; Function calls
(call_expression) @expression.call

; Callable references
(callable_reference) @expression.callable_reference

; =============================================================================
; LITERALS AND CONSTANTS
; =============================================================================

; String literals
(string_literal) @literal.string

; Integer literals
(integer_literal) @literal.integer

; Real literals
(real_literal) @literal.real

; Boolean literals
(boolean_literal) @literal.boolean

; Null literal
(null_literal) @literal.null

; Character literals
(character_literal) @literal.character

; Collection literals
(collection_literal) @literal.collection

; Lambda literals
(lambda_literal) @literal.lambda

; Object literals
(object_literal) @literal.object

; =============================================================================
; TYPES
; =============================================================================

; Type references
(user_type
  (type_identifier) @type
) @type.reference

; Function types
(function_type) @type.function

; Nullable types
(nullable_type) @type.nullable

; Parenthesized types
(parenthesized_type) @type.parenthesized

; =============================================================================
; MODIFIERS
; =============================================================================

; Visibility modifiers
(visibility_modifier) @modifier.visibility

; Class modifiers
(class_modifier) @modifier.class

; Function modifiers
(function_modifier) @modifier.function

; Property modifiers
(property_modifier) @modifier.property

; Inheritance modifiers
(inheritance_modifier) @modifier.inheritance

; Parameter modifiers
(parameter_modifier) @modifier.parameter

; Variance modifiers
(variance_modifier) @modifier.variance

; =============================================================================
; BLOCKS AND BODIES
; =============================================================================

; Class bodies
(class_body) @block.class

; Function bodies
(function_body) @block.function

; Enum class bodies
(enum_class_body) @block.enum

; =============================================================================
; COMMENTS
; =============================================================================

; Line comments
(line_comment) @comment.line

; Block comments
(multiline_comment) @comment.block

; =============================================================================
; IDENTIFIERS AND NAMES
; =============================================================================

; Simple identifiers
(simple_identifier) @identifier

; Type identifiers
(type_identifier) @identifier.type

; Labels
(label) @identifier.label

; =============================================================================
; OPERATORS
; =============================================================================

; Note: Most operators are private nodes (_assignment_and_operator, etc.)
; and cannot be referenced directly in queries

; =============================================================================
; SPECIAL CONSTRUCTS
; =============================================================================

; Elvis operator
(elvis_expression) @expression.elvis

; Range expressions
(range_expression) @expression.range

; Infix expressions
(infix_expression) @expression.infix

; As expressions
(as_expression) @expression.as

; Spread expressions
(spread_expression) @expression.spread

; This expressions
(this_expression) @expression.this

; Super expressions
(super_expression) @expression.super

; =============================================================================
; ANONYMOUS FUNCTIONS
; =============================================================================

; Anonymous functions
(anonymous_function) @definition.anonymous_function

; Lambda expressions
(lambda_literal) @expression.lambda

; =============================================================================
; INITIALIZERS
; =============================================================================

; Anonymous initializers
(anonymous_initializer) @definition.anonymous_initializer

; =============================================================================
; DELEGATION
; =============================================================================

; Explicit delegation
(explicit_delegation) @expression.delegation

; Property delegation
(property_delegate) @expression.property_delegate

; =============================================================================
; TYPE CONSTRAINTS
; =============================================================================

; Type constraints
(type_constraints) @constraint.type

; Type constraint
(type_constraint
  (type_identifier) @name.definition.type_constraint
) @definition.type_constraint

