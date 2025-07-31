; =============================================================================
; Python Tree-sitter Query File
; Comprehensive queries for extracting Python symbols and relationships
; =============================================================================

; =============================================================================
; CLASS DEFINITIONS
; =============================================================================

; Basic class definitions
(class_definition
  name: (identifier) @name.definition.class) @definition.class

; Decorated class definitions
(decorated_definition
  definition: (class_definition
    name: (identifier) @name.definition.class)) @definition.class

; Class with type parameters (Python 3.12+)
(class_definition
  name: (identifier) @name.definition.class
  type_parameters: (type_parameter)) @definition.class

; =============================================================================
; FUNCTION DEFINITIONS
; =============================================================================

; Function definitions (including async, decorated, and with type parameters)
(function_definition
  name: (identifier) @name.definition.function) @definition.function

; Decorated function definitions
(decorated_definition
  definition: (function_definition
    name: (identifier) @name.definition.function)) @definition.function



; =============================================================================
; VARIABLE DEFINITIONS
; =============================================================================

; Variable assignments (including multiple assignments and augmented assignments)
(expression_statement
  (assignment
    left: (identifier) @name.definition.variable)) @definition.variable

(expression_statement
  (augmented_assignment
    left: (identifier) @name.definition.variable)) @definition.variable

; =============================================================================
; IMPORT STATEMENTS
; =============================================================================

; Import statements
(import_statement) @definition.import

; Import from statements
(import_from_statement) @definition.import

; Future import statements
(future_import_statement) @definition.import

; =============================================================================
; CONTROL FLOW STRUCTURES
; =============================================================================

; If statements
(if_statement) @definition.control_flow

; For loops
(for_statement) @definition.control_flow

; While loops
(while_statement) @definition.control_flow

; Try-except blocks
(try_statement) @definition.control_flow

; With statements
(with_statement) @definition.control_flow

; Match statements (Python 3.10+)
(match_statement) @definition.control_flow

; =============================================================================
; COMPREHENSIONS
; =============================================================================

; List comprehensions
(list_comprehension) @definition.comprehension

; Dictionary comprehensions
(dictionary_comprehension) @definition.comprehension

; Set comprehensions
(set_comprehension) @definition.comprehension

; Generator expressions
(generator_expression) @definition.comprehension

; =============================================================================
; DATA STRUCTURES
; =============================================================================

; List definitions
(list) @definition.data_structure

; Dictionary definitions
(dictionary) @definition.data_structure

; Set definitions
(set) @definition.data_structure

; Tuple definitions
(tuple) @definition.data_structure

; =============================================================================
; TYPE ANNOTATIONS
; =============================================================================

; Type annotations in function parameters
(typed_parameter) @definition.type_annotation

; Type annotations with default values
(typed_default_parameter) @definition.type_annotation

; Type aliases (Python 3.12+)
(type_alias_statement
  left: (type) @name.definition.type_alias) @definition.type_alias

; =============================================================================
; DECORATORS
; =============================================================================

; Decorator definitions
(decorator) @definition.decorator

; =============================================================================
; EXCEPTIONS AND ERROR HANDLING
; =============================================================================

; Exception clauses
(except_clause) @definition.exception

; Exception group clauses (Python 3.11+)
(except_group_clause) @definition.exception

; Raise statements
(raise_statement) @definition.exception

; Assert statements
(assert_statement) @definition.assertion

; =============================================================================
; SCOPE AND NAMESPACE
; =============================================================================

; Global statements
(global_statement) @definition.scope

; Nonlocal statements
(nonlocal_statement) @definition.scope

; =============================================================================
; PATTERN MATCHING (Python 3.10+)
; =============================================================================

; Case clauses in match statements
(case_clause) @definition.pattern

; Pattern matching with guards (simplified)
(case_clause) @definition.pattern

; =============================================================================
; EXPRESSIONS AND OPERATORS
; =============================================================================

; Function calls
(call
  function: (identifier) @name.reference.function) @reference.function_call

; Attribute access
(attribute
  object: (_) @reference.object
  attribute: (identifier) @name.reference.attribute) @reference.attribute

; Subscript access
(subscript
  value: (_) @reference.object
  subscript: (_) @reference.subscript) @reference.subscript

; Binary operators
(binary_operator) @reference.binary_operator

; Unary operators
(unary_operator) @reference.unary_operator

; Comparison operators
(comparison_operator) @reference.comparison

; Boolean operators
(boolean_operator) @reference.boolean_operator

; =============================================================================
; LITERALS AND CONSTANTS
; =============================================================================

; String literals
(string) @definition.literal

; Concatenated strings
(concatenated_string) @definition.literal

; Integer literals
(integer) @definition.literal

; Float literals
(float) @definition.literal

; Boolean literals
(true) @definition.literal
(false) @definition.literal

; None literal
(none) @definition.literal

; Ellipsis
(ellipsis) @definition.literal

; =============================================================================
; SPECIAL CONSTRUCTS
; =============================================================================

; Yield statements
(yield) @definition.yield

; Await expressions
(await) @definition.await

; Named expressions (walrus operator)
(named_expression
  name: (identifier) @name.definition.variable) @definition.named_expression

; Conditional expressions (ternary operator)
(conditional_expression) @definition.conditional_expression

; =============================================================================
; COMMENTS AND DOCUMENTATION
; =============================================================================

; Comments (captured as extras in the grammar)
(comment) @definition.comment

; =============================================================================
; RELATIONSHIP QUERIES
; =============================================================================

; Class inheritance
(class_definition
  name: (identifier) @class.name
  superclasses: (argument_list
    (identifier) @parent.name)) @relationship.inheritance

; Function calls within functions
(function_definition
  name: (identifier) @function.name
  body: (block
    (expression_statement
      (call
        function: (identifier) @called_function.name)))) @relationship.function_call

; Method calls
(expression_statement
  (call
    function: (attribute
      object: (_) @object.name
      attribute: (identifier) @method.name))) @relationship.method_call

; Import relationships
(import_from_statement
  module_name: (dotted_name) @module.name
  name: (dotted_name) @imported.name) @relationship.import

; Variable usage
(expression_statement
  (assignment
    left: (identifier) @variable.name
    right: (identifier) @used_variable.name)) @relationship.variable_usage

; =============================================================================
; ADVANCED PATTERNS
; =============================================================================

; Async context managers (async with statements)
(with_statement) @definition.async_context

; Async for loops
(for_statement) @definition.async_loop

; Async function definitions
(function_definition
  name: (identifier) @name.definition.async_function) @definition.async_function

; Type hints in function return types
(function_definition
  name: (identifier) @name.definition.function
  return_type: (type)) @definition.typed_function

; Generic types
(generic_type) @definition.generic_type

; Union types
(union_type) @definition.union_type

; =============================================================================
; ERROR HANDLING PATTERNS
; =============================================================================

; Try-except with specific exception types
(try_statement
  body: (block)
  (except_clause
    value: (identifier) @exception_type.name)) @definition.exception_handler

; Try-except with exception aliases
(try_statement
  body: (block)
  (except_clause
    value: (identifier) @exception_type.name
    alias: (identifier) @exception_alias.name)) @definition.exception_handler

; =============================================================================
; COMPREHENSION PATTERNS
; =============================================================================

; List comprehensions (simplified)
(list_comprehension) @definition.comprehension

; Dictionary comprehensions (simplified)
(dictionary_comprehension) @definition.comprehension

; Set comprehensions (simplified)
(set_comprehension) @definition.comprehension

; Generator expressions (simplified)
(generator_expression) @definition.comprehension

; =============================================================================
; PATTERN MATCHING PATTERNS
; =============================================================================

; Pattern matching patterns
(case_clause) @definition.pattern

; =============================================================================
; TYPE SYSTEM PATTERNS
; =============================================================================

; Constrained types
(constrained_type) @definition.constrained_type

; Member types (qualified names)
(member_type) @definition.member_type

; Splat types
(splat_type) @definition.splat_type
