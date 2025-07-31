; =============================================================================
; JSON Tree-sitter Query File
; Comprehensive queries for extracting JSON symbols and relationships
; =============================================================================

; =============================================================================
; DOCUMENT STRUCTURE
; =============================================================================

; Top-level document containing multiple values
(document) @definition.document

; =============================================================================
; OBJECT DEFINITIONS
; =============================================================================

; Object definitions with key-value pairs
(object) @definition.object

; Key-value pairs within objects
(pair
  key: (string) @name.definition.key
  value: (_) @definition.value) @definition.pair

; =============================================================================
; ARRAY DEFINITIONS
; =============================================================================

; Array definitions
(array) @definition.array

; Array elements
(array
  (_) @definition.array_element) @definition.array_element

; =============================================================================
; VALUE DEFINITIONS
; =============================================================================

; String values
(string) @definition.string

; String content within strings
(string
  (string_content) @definition.string_content) @definition.string_content

; Escape sequences within strings
(string
  (escape_sequence) @definition.escape_sequence) @definition.escape_sequence

; Number values (integers and floats)
(number) @definition.number

; Boolean values
(true) @definition.boolean
(false) @definition.boolean

; Null values
(null) @definition.null

; =============================================================================
; NESTED STRUCTURES
; =============================================================================

; Nested objects within objects
(object
  (pair
    value: (object) @definition.nested_object)) @definition.nested_object

; Nested arrays within objects
(object
  (pair
    value: (array) @definition.nested_array)) @definition.nested_array

; Nested objects within arrays
(array
  (object) @definition.nested_object) @definition.nested_object

; Nested arrays within arrays
(array
  (array) @definition.nested_array) @definition.nested_array

; =============================================================================
; PRIMITIVE VALUES
; =============================================================================

; String literals
(string) @definition.literal

; Number literals
(number) @definition.literal

; Boolean literals
(true) @definition.literal
(false) @definition.literal

; Null literal
(null) @definition.literal

; =============================================================================
; COMMENTS (JSON with Comments)
; =============================================================================

; Line comments
(comment) @definition.comment

; Block comments
(comment) @definition.comment

; =============================================================================
; RELATIONSHIP QUERIES
; =============================================================================

; Object property relationships
(pair
  key: (string) @key.name
  value: (string) @value.name) @relationship.property

; Object property with nested object
(pair
  key: (string) @key.name
  value: (object) @nested_object.name) @relationship.nested_object

; Object property with array
(pair
  key: (string) @key.name
  value: (array) @array.name) @relationship.array_property

; Array element relationships
(array
  (string) @element.name) @relationship.array_element

(array
  (number) @element.name) @relationship.array_element

(array
  (object) @element.name) @relationship.array_element

(array
  (array) @element.name) @relationship.array_element

; =============================================================================
; STRUCTURAL PATTERNS
; =============================================================================

; Empty objects
(object) @definition.empty_object

; Empty arrays
(array) @definition.empty_array

; Single element arrays
(array
  (_) @definition.single_element_array) @definition.single_element_array

; Multiple element arrays
(array
  (_) @definition.array_element
  (_) @definition.array_element) @definition.multi_element_array

; =============================================================================
; DATA TYPE PATTERNS
; =============================================================================

; String patterns
(string
  (string_content) @definition.text_content) @definition.text_content

; Numeric patterns
(number) @definition.numeric_value

; Boolean patterns
(true) @definition.boolean_true
(false) @definition.boolean_false

; =============================================================================
; ESCAPE SEQUENCE PATTERNS
; =============================================================================

; Common escape sequences
(escape_sequence) @definition.escape_sequence

; =============================================================================
; ADVANCED PATTERNS
; =============================================================================

; JSON Schema-like patterns (objects with specific key patterns)
(object
  (pair
    key: (string) @schema_key.name
    value: (string) @schema_value.name)) @definition.schema_property

; Configuration-like patterns (objects with nested configuration)
(object
  (pair
    key: (string) @config_key.name
    value: (object) @config_value.name)) @definition.config_property

; List-like patterns (arrays of similar types)
(array
  (string) @list_item.name) @definition.string_list

(array
  (number) @list_item.name) @definition.number_list

(array
  (object) @list_item.name) @definition.object_list

; =============================================================================
; VALIDATION PATTERNS
; =============================================================================

; Required field patterns (objects with specific required keys)
(object
  (pair
    key: (string) @required_key.name
    value: (_) @required_value.name)) @definition.required_field

; Optional field patterns (objects with optional keys)
(object
  (pair
    key: (string) @optional_key.name
    value: (_) @optional_value.name)) @definition.optional_field

; =============================================================================
; METADATA PATTERNS
; =============================================================================

; Metadata objects (objects with metadata-like keys)
(object
  (pair
    key: (string) @metadata_key.name
    value: (_) @metadata_value.name)) @definition.metadata

; Version information patterns
(object
  (pair
    key: (string) @version_key.name
    value: (string) @version_value.name)) @definition.version_info

; =============================================================================
; ERROR PATTERNS
; =============================================================================

; Malformed JSON patterns (for error detection)
; Note: These would typically be caught by the parser, but we can identify
; potential issues in the AST structure

; =============================================================================
; UTILITY PATTERNS
; =============================================================================

; All string keys in objects
(pair
  key: (string) @key.name) @definition.object_key

; All string values
(string) @definition.string_value

; All numeric values
(number) @definition.numeric_value

; All boolean values
(true) @definition.boolean_value
(false) @definition.boolean_value

; All null values
(null) @definition.null_value

; =============================================================================
; HIERARCHY PATTERNS
; =============================================================================

; Root level objects
(document
  (object) @definition.root_object) @definition.root_object

; Root level arrays
(document
  (array) @definition.root_array) @definition.root_array

; Root level primitives
(document
  (string) @definition.root_string) @definition.root_string

(document
  (number) @definition.root_number) @definition.root_number

(document
  (true) @definition.root_boolean) @definition.root_boolean

(document
  (false) @definition.root_boolean) @definition.root_boolean

(document
  (null) @definition.root_null) @definition.root_null 