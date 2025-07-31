# Swift Tree-Sitter Query Guide

## Overview

This guide explains the robust Swift tree-sitter query file (`queries_scm/swift.scm`) that extracts all top-level declarations from Swift code. The query file is based on the actual tree-sitter-swift grammar and corpus examples.

## Query File Structure

The SCM file captures the following Swift language constructs:

### 1. Top-Level Type Declarations

All type declarations in Swift use the `class_declaration` node with a `declaration_kind` field that specifies the actual type:

```scm
; Classes
(class_declaration
  declaration_kind: "class"
  name: (type_identifier) @class_name
) @class_definition

; Structs
(class_declaration
  declaration_kind: "struct"
  name: (type_identifier) @struct_name
) @struct_definition

; Enums
(class_declaration
  declaration_kind: "enum"
  name: (type_identifier) @enum_name
) @enum_definition

; Actors
(class_declaration
  declaration_kind: "actor"
  name: (type_identifier) @actor_name
) @actor_definition

; Extensions
(class_declaration
  declaration_kind: "extension"
  name: (user_type) @extension_type_name
) @extension_definition
```

### 2. Protocols

```scm
(protocol_declaration
  name: (type_identifier) @protocol_name
) @protocol_definition
```

### 3. Functions

```scm
(function_declaration
  name: (simple_identifier) @function_name
) @function_definition
```

### 4. Initializers and Deinitializers

```scm
(init_declaration
  "init" @initializer_name
) @initializer_definition

(deinit_declaration
  "deinit" @deinitializer_name
) @deinitializer_definition
```

### 5. Properties

```scm
(property_declaration
  (pattern
    bound_identifier: (simple_identifier) @property_name
  )
) @property_definition
```

### 6. Subscripts

```scm
(subscript_declaration
  (parameter
    (simple_identifier) @subscript_param_name
  )
) @subscript_definition
```

### 7. Type Aliases

```scm
(typealias_declaration
  name: (type_identifier) @type_alias_name
) @type_alias_definition
```

## How to Distinguish Between Type Declarations in Post-Processing

Since all type declarations use the same `class_declaration` node, you need to examine the `declaration_kind` field to distinguish between them. Here's how to do it in different programming languages:

### Python Example

```python
def process_swift_symbols(symbols):
    """Process Swift symbols and categorize them by declaration kind."""
    
    categorized_symbols = {
        'classes': [],
        'structs': [],
        'enums': [],
        'actors': [],
        'extensions': [],
        'protocols': [],
        'functions': [],
        'properties': [],
        'type_aliases': []
    }
    
    for symbol in symbols:
        symbol_type = symbol.get('symbol_type', '')
        capture_name = symbol.get('capture_name', '')
        
        # Handle type declarations with declaration_kind
        if symbol_type in ['class_definition', 'struct_definition', 'enum_definition', 
                          'actor_definition', 'extension_definition']:
            # Extract declaration_kind from the node
            declaration_kind = extract_declaration_kind(symbol)
            
            if declaration_kind == 'class':
                categorized_symbols['classes'].append(symbol)
            elif declaration_kind == 'struct':
                categorized_symbols['structs'].append(symbol)
            elif declaration_kind == 'enum':
                categorized_symbols['enums'].append(symbol)
            elif declaration_kind == 'actor':
                categorized_symbols['actors'].append(symbol)
            elif declaration_kind == 'extension':
                categorized_symbols['extensions'].append(symbol)
        
        # Handle other symbol types
        elif symbol_type == 'protocol_definition':
            categorized_symbols['protocols'].append(symbol)
        elif symbol_type == 'function_definition':
            categorized_symbols['functions'].append(symbol)
        elif symbol_type == 'property_definition':
            categorized_symbols['properties'].append(symbol)
        elif symbol_type == 'type_alias_definition':
            categorized_symbols['type_aliases'].append(symbol)
    
    return categorized_symbols

def extract_declaration_kind(symbol):
    """Extract the declaration_kind from a type declaration symbol."""
    # This would depend on your tree-sitter implementation
    # You need to access the actual node and get the declaration_kind field
    node = symbol.get('node')
    if node and hasattr(node, 'child_by_field_name'):
        kind_node = node.child_by_field_name('declaration_kind')
        if kind_node:
            return kind_node.text.decode('utf-8')
    return 'unknown'
```

### JavaScript/TypeScript Example

```typescript
interface SwiftSymbol {
  symbol_type: string;
  capture_name: string;
  node?: any;
  name?: string;
}

interface CategorizedSymbols {
  classes: SwiftSymbol[];
  structs: SwiftSymbol[];
  enums: SwiftSymbol[];
  actors: SwiftSymbol[];
  extensions: SwiftSymbol[];
  protocols: SwiftSymbol[];
  functions: SwiftSymbol[];
  properties: SwiftSymbol[];
  typeAliases: SwiftSymbol[];
}

function processSwiftSymbols(symbols: SwiftSymbol[]): CategorizedSymbols {
  const categorized: CategorizedSymbols = {
    classes: [],
    structs: [],
    enums: [],
    actors: [],
    extensions: [],
    protocols: [],
    functions: [],
    properties: [],
    typeAliases: []
  };

  for (const symbol of symbols) {
    const symbolType = symbol.symbol_type;
    
    // Handle type declarations with declaration_kind
    if (['class_definition', 'struct_definition', 'enum_definition', 
         'actor_definition', 'extension_definition'].includes(symbolType)) {
      
      const declarationKind = extractDeclarationKind(symbol);
      
      switch (declarationKind) {
        case 'class':
          categorized.classes.push(symbol);
          break;
        case 'struct':
          categorized.structs.push(symbol);
          break;
        case 'enum':
          categorized.enums.push(symbol);
          break;
        case 'actor':
          categorized.actors.push(symbol);
          break;
        case 'extension':
          categorized.extensions.push(symbol);
          break;
      }
    }
    // Handle other symbol types
    else if (symbolType === 'protocol_definition') {
      categorized.protocols.push(symbol);
    }
    else if (symbolType === 'function_definition') {
      categorized.functions.push(symbol);
    }
    else if (symbolType === 'property_definition') {
      categorized.properties.push(symbol);
    }
    else if (symbolType === 'type_alias_definition') {
      categorized.typeAliases.push(symbol);
    }
  }

  return categorized;
}

function extractDeclarationKind(symbol: SwiftSymbol): string {
  const node = symbol.node;
  if (node && node.childForFieldName) {
    const kindNode = node.childForFieldName('declaration_kind');
    if (kindNode) {
      return kindNode.text;
    }
  }
  return 'unknown';
}
```

### Rust Example

```rust
use tree_sitter::{Node, QueryCursor};

#[derive(Debug, Clone)]
struct SwiftSymbol {
    symbol_type: String,
    capture_name: String,
    name: Option<String>,
    node: Option<Node<'static>>,
}

#[derive(Debug, Default)]
struct CategorizedSymbols {
    classes: Vec<SwiftSymbol>,
    structs: Vec<SwiftSymbol>,
    enums: Vec<SwiftSymbol>,
    actors: Vec<SwiftSymbol>,
    extensions: Vec<SwiftSymbol>,
    protocols: Vec<SwiftSymbol>,
    functions: Vec<SwiftSymbol>,
    properties: Vec<SwiftSymbol>,
    type_aliases: Vec<SwiftSymbol>,
}

fn process_swift_symbols(symbols: Vec<SwiftSymbol>) -> CategorizedSymbols {
    let mut categorized = CategorizedSymbols::default();

    for symbol in symbols {
        match symbol.symbol_type.as_str() {
            "class_definition" | "struct_definition" | "enum_definition" | 
            "actor_definition" | "extension_definition" => {
                let declaration_kind = extract_declaration_kind(&symbol);
                match declaration_kind.as_str() {
                    "class" => categorized.classes.push(symbol),
                    "struct" => categorized.structs.push(symbol),
                    "enum" => categorized.enums.push(symbol),
                    "actor" => categorized.actors.push(symbol),
                    "extension" => categorized.extensions.push(symbol),
                    _ => {}
                }
            }
            "protocol_definition" => categorized.protocols.push(symbol),
            "function_definition" => categorized.functions.push(symbol),
            "property_definition" => categorized.properties.push(symbol),
            "type_alias_definition" => categorized.type_aliases.push(symbol),
            _ => {}
        }
    }

    categorized
}

fn extract_declaration_kind(symbol: &SwiftSymbol) -> String {
    if let Some(node) = &symbol.node {
        if let Some(kind_node) = node.child_by_field_name("declaration_kind") {
            return kind_node.utf8_text(node.tree().source()).unwrap_or("unknown").to_string();
        }
    }
    "unknown".to_string()
}
```

## Key Points for Post-Processing

1. **Declaration Kind Field**: The `declaration_kind` field contains the actual type: "class", "struct", "enum", "actor", or "extension".

2. **Node Access**: You need to access the actual tree-sitter node to get the `declaration_kind` field value.

3. **Capture Names**: The capture names (@class_name, @struct_name, etc.) help identify the symbol type, but the `declaration_kind` field is the definitive source.

4. **Extensions**: Extensions use `user_type` instead of `type_identifier` for the name field.

5. **Fallback Strategy**: If tree-sitter parsing fails, the parser falls back to regex-based extraction.

## Testing the Query

You can test the SCM file directly using the tree-sitter CLI:

```bash
tree-sitter query queries_scm/swift.scm your_swift_file.swift
```

This will show you the exact captures and their positions in the file.

## Compatibility

This SCM file is compatible with:
- Latest tree-sitter-swift grammar
- All major Swift language features
- Swift 5.0+ syntax
- Modern Swift constructs (actors, property wrappers, etc.)

## Limitations

- Local variable declarations are not captured (they require more complex patterns)
- Some advanced Swift features may require additional patterns
- Relationship extraction (inheritance, protocol conformance) requires separate queries

## Future Enhancements

1. Add relationship extraction patterns
2. Include local variable declarations
3. Add support for more advanced Swift features
4. Include generic constraint patterns
5. Add async/await specific patterns 