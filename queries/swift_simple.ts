/*
Simplified Swift Tree-Sitter Query Patterns
*/
export default `
; Basic class declarations
(class_declaration
  name: (type_identifier) @name) @definition.class

; Basic struct declarations  
(struct_declaration
  name: (type_identifier) @name) @definition.struct

; Basic function declarations
(function_declaration
  name: (simple_identifier) @name) @definition.function

; Basic property declarations
(property_declaration
  (pattern) @name) @definition.property
` 