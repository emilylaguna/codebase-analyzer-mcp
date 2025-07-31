# Tree-sitter Queries Migration

This document describes the migration from TypeScript-wrapped tree-sitter queries to native SCM format.

## Overview

The codebase analyzer previously used TypeScript files containing tree-sitter SCM queries wrapped in template literals. These have been converted to native `.scm` files for better compatibility and cleaner structure.

## Changes Made

### 1. Query File Conversion

- **Before**: `queries/python.ts` containing:
  ```typescript
  export default `
  ; Class definitions
  (class_definition
    name: (identifier) @name.definition.class) @definition.class
  `
  ```

- **After**: `queries_scm/python.scm` containing:
  ```scm
  ; Class definitions
  (class_definition
    name: (identifier) @name.definition.class) @definition.class
  ```

### 2. Parser Updates

The `parser.py` file has been updated to:

- Use the new `queries_scm` directory by default
- Load `.scm` files directly instead of extracting from TypeScript files
- Simplified query loading logic (no more template literal parsing)

### 3. Supported Formats

The conversion script handled multiple TypeScript export formats:

- `export default \`query\``
- `export const queryName = \`query\``  
- `export default String.raw\`query\``

## File Structure

```
queries_scm/
├── python.scm          # Python language queries
├── swift.scm           # Swift language queries
├── javascript.scm      # JavaScript language queries
├── typescript.scm      # TypeScript language queries
├── java.scm            # Java language queries
├── rust.scm            # Rust language queries
├── cpp.scm             # C++ language queries
├── c.scm               # C language queries
├── c-sharp.scm         # C# language queries
├── go.scm              # Go language queries
├── ruby.scm            # Ruby language queries
├── php.scm             # PHP language queries
├── kotlin.scm          # Kotlin language queries
├── scala.scm           # Scala language queries
├── lua.scm             # Lua language queries
├── ocaml.scm           # OCaml language queries
├── elixir.scm          # Elixir language queries
├── elisp.scm           # Elisp language queries
├── css.scm             # CSS language queries
├── html.scm            # HTML language queries
├── vue.scm             # Vue language queries
├── solidity.scm        # Solidity language queries
├── zig.scm             # Zig language queries
├── toml.scm            # TOML language queries
├── systemrdl.scm       # SystemRDL language queries
├── tlaplus.scm         # TLA+ language queries
├── embedded_template.scm # Embedded template queries
├── swift_minimal.scm   # Swift minimal queries
└── swift_simple.scm    # Swift simple queries
```

## Benefits

1. **Native Format**: SCM files are the native format for tree-sitter queries
2. **Better Tooling**: IDE support and syntax highlighting for SCM files
3. **Simplified Loading**: No need to parse TypeScript template literals
4. **Cleaner Structure**: Direct query files without wrapper code
5. **Better Performance**: Faster loading without string parsing

## Migration Process

The migration was performed using an automated script that:

1. Scanned all `.ts` files in the `queries/` directory
2. Extracted SCM content from various TypeScript export formats
3. Created corresponding `.scm` files in `queries_scm/` directory
4. Updated the parser to use the new directory structure
5. Fixed syntax issues in Swift queries (invalid node types)
6. Removed trailing backticks from all SCM files

## Backward Compatibility

The original `queries/` directory with TypeScript files is preserved for reference. The parser now defaults to using `queries_scm/` but can be configured to use a different directory if needed.

## Testing

The migration has been tested to ensure:

- All 30 query files were successfully converted
- The parser can load SCM queries correctly
- Query content is preserved exactly as intended
- No functionality is lost in the conversion
- Swift query syntax issues were identified and fixed
- All trailing backticks were removed from SCM files

## Usage

The parser now automatically uses the SCM queries:

```python
from parsers.code_parser import CodeParser

# Uses queries_scm/ directory by default
parser = CodeParser()

# Can specify custom queries directory if needed
parser = CodeParser(queries_dir="custom_queries")
``` 