; =============================================================================
; ROBUST SWIFT TREE-SITTER QUERY FILE
; Based on actual tree-sitter-swift corpus examples
; =============================================================================

; =============================================================================
; TOP-LEVEL TYPE DECLARATIONS
; =============================================================================

; All type declarations use class_declaration with declaration_kind
(class_declaration
  declaration_kind: "class"
  name: (type_identifier) @class_name
) @class_definition

(class_declaration
  declaration_kind: "struct"
  name: (type_identifier) @struct_name
) @struct_definition

(class_declaration
  declaration_kind: "enum"
  name: (type_identifier) @enum_name
) @enum_definition

(class_declaration
  declaration_kind: "actor"
  name: (type_identifier) @actor_name
) @actor_definition

(class_declaration
  declaration_kind: "extension"
  name: (user_type) @extension_type_name
) @extension_definition

; =============================================================================
; PROTOCOLS
; =============================================================================

; Protocol declarations
(protocol_declaration
  name: (type_identifier) @protocol_name
) @protocol_definition

; =============================================================================
; FUNCTIONS
; =============================================================================

; Global function declarations
(function_declaration
  name: (simple_identifier) @function_name
) @function_definition

; =============================================================================
; INITIALIZERS AND DEINITIALIZERS
; =============================================================================

; Initializer declarations
(init_declaration
  "init" @initializer_name
) @initializer_definition

; Deinitializer declarations
(deinit_declaration
  "deinit" @deinitializer_name
) @deinitializer_definition

; =============================================================================
; PROPERTIES
; =============================================================================

; Property declarations
(property_declaration
  (pattern
    bound_identifier: (simple_identifier) @property_name
  )
) @property_definition

; =============================================================================
; SUBSCRIPTS
; =============================================================================

; Subscript declarations
(subscript_declaration
  (parameter
    (simple_identifier) @subscript_param_name
  )
) @subscript_definition

; =============================================================================
; TYPE ALIASES
; =============================================================================

; Type alias declarations
(typealias_declaration
  name: (type_identifier) @type_alias_name
) @type_alias_definition 