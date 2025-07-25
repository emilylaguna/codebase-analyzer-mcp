/*
Minimal Swift Tree-Sitter Query Patterns
Based on actual node types from the Swift grammar
*/
export default `
; Class/Struct declarations (Swift uses class_declaration for both)
(class_declaration
  name: (type_identifier) @name) @definition.class

; Function declarations
(function_declaration
  name: (simple_identifier) @name) @definition.function

; Property declarations
(property_declaration
  (pattern) @name) @definition.property

; Initializer declarations
(init_declaration
  "init" @name) @definition.initializer
` 