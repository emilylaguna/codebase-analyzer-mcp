# Codebase Analyzer - FastMCP Server

A FastMCP server for parsing, indexing, and semantically searching codebases using Tree-sitter and SpaCy embeddings.

## Features

- **Multi-language Support**: Parses 30+ programming languages using Tree-sitter WASM grammars
- **Semantic Search**: Vector-based search using SpaCy embeddings and sqlite-vec
- **Incremental Updates**: Only re-parses files that have changed
- **FastMCP Integration**: Native MCP server with async command support
- **Structured Symbol Extraction**: Extracts classes, functions, methods, and more
- **Multi-Project Support**: Index and manage multiple codebases with project isolation
- **Progress Reporting**: Real-time progress updates during long-running operations
- **FastMCP Resources**: Direct data access through REST-like resource URIs
- **Code Relationship Mapping**: Track function calls, inheritance, implementations, and dependencies

## Supported Languages

- Python, JavaScript, TypeScript, TSX
- Java, C#, C, C++
- Go, Rust, Ruby, PHP
- Swift, Kotlin, Scala
- Lua, HTML, CSS, JSON
- YAML, TOML, Vue
- Solidity, Zig, Elixir
- OCaml, Elm, Bash
- Elisp, SystemRDL, TLA+
- QL, ReScript

## Installation

### Prerequisites

- Python 3.12+
- FastMCP CLI (`pip install fastmcp`)

### Setup

1. **Clone and install dependencies**:
   ```bash
   git clone <repository>
   cd codebase-analyzer
   pip install -e .
   ```

2. **Install sqlite-vec**:
   ```bash
   pip install sqlite-vec
   ```

3. **Install SpaCy and download the embedding model**:
   ```bash
   pip install spacy
   python -m spacy download en_core_web_md
   ```

   > **Note**: You can also use `en_core_web_trf` for better quality (but slower) embeddings:
   > ```bash
   > python -m spacy download en_core_web_trf
   > ```

4. **Verify installation**:
   ```bash
   python -c "import spacy; nlp = spacy.load('en_core_web_md'); print('SpaCy ready!')"
   ```

## Usage

### Starting the Server

```bash
# For development with MCP Inspector
fastmcp dev main.py --ui-port 3000 --server-port 8000

# For production
fastmcp run main.py
```

The server will start and register the following MCP commands:

### Available Commands

#### 1. Index a Codebase

```bash
# Index with default project ID
mcp call index_codebase "/path/to/your/codebase"

# Index with custom project ID
mcp call index_codebase "/path/to/your/codebase" "my-project"
```

**Response**:
```json
{
  "success": true,
  "project_id": "my-project",
  "processed_files": 45,
  "total_symbols_added": 1234,
  "errors": [],
  "database_stats": {
    "total_symbols": 1234,
    "symbols_with_embeddings": 1234,
    "languages": {
      "python": 567,
      "javascript": 234,
      "typescript": 123
    },
    "total_files": 45,
    "project_id": "my-project"
  }
}
```

**Progress Reporting**: The indexing operation provides real-time progress updates:
- **File Discovery** (0-10%): Scanning for files to process
- **File Processing** (10-90%): Parsing files and generating embeddings
- **Finalization** (90-100%): Completing the indexing process

#### 2. Search by Symbol Name

```bash
# Search across all projects
mcp call search_symbol_by_name "functionName"

# Search within a specific project
mcp call search_symbol_by_name "functionName" "python" "my-project"

# Search with language filter
mcp call search_symbol_by_name "functionName" "python"
```

#### 3. Semantic Search

```bash
# Search across all projects
mcp call search_symbol_semantic "find functions that handle user authentication"

# Search within a specific project
mcp call search_symbol_semantic "find functions that handle user authentication" 10 "my-project"
```

#### 4. Project Management

```bash
# List all projects
mcp call list_projects

# Get statistics for a specific project
mcp call get_stats "my-project"

# Get global statistics
mcp call get_stats

# Delete a project
mcp call delete_project "my-project"
```

#### 5. Health Check

```bash
mcp call health_check
```

## Multi-Project Support

The codebase analyzer now supports multiple projects with complete isolation:

### Project Isolation
- Each project has its own namespace in the database
- Symbols from different projects are completely separated
- You can search within a project or across all projects
- Project-specific statistics and management

### Project Identifiers
- Use meaningful project IDs (e.g., "frontend-app", "backend-api", "shared-libs")
- Default project ID is "default" for backward compatibility
- Project IDs are case-sensitive and should be unique

### Example Workflow

```bash
# Index multiple projects
mcp call index_codebase "/path/to/frontend" "frontend-app"
mcp call index_codebase "/path/to/backend" "backend-api"
mcp call index_codebase "/path/to/shared" "shared-libs"

# List all projects
mcp call list_projects

# Search within a specific project
mcp call search_symbol_by_name "UserComponent" "typescript" "frontend-app"

# Search across all projects
mcp call search_symbol_semantic "database connection" 5

# Get project-specific stats
mcp call get_stats "frontend-app"

# Clean up a project
mcp call delete_project "old-project"
```

## Progress Reporting

The server provides real-time progress updates for long-running operations:

### Indexing Progress
- **File Discovery**: Shows how many files were found
- **File Processing**: Updates for each file being processed
- **Completion**: Final statistics and summary

### Project Deletion Progress
- **Preparation**: Counting symbols to delete
- **Deletion**: Removing symbols and embeddings
- **Completion**: Confirmation of deletion

### Client Requirements
- Clients must support progress tokens to receive progress updates
- Progress updates are sent via the MCP context
- If progress tokens aren't supported, operations still work but without progress feedback

## FastMCP Resources

The codebase analyzer exposes indexed data through [FastMCP resources](https://gofastmcp.com/servers/resources), providing direct access to project information, symbols, and search results without requiring tool calls.

### Available Resources

#### Project Statistics
- **URI**: `codebase://stats/{project_id}`
- **Description**: Get database statistics for a specific project
- **Example**: `codebase://stats/my-project`

#### Project Symbols
- **URI**: `codebase://symbols/{project_id}`
- **Description**: Get all symbols for a specific project
- **Example**: `codebase://symbols/my-project`

#### Language-Specific Symbols
- **URI**: `codebase://symbols/{project_id}/{language}`
- **Description**: Get all symbols for a specific project and language
- **Example**: `codebase://symbols/my-project/python`

#### Project Files
- **URI**: `codebase://files/{project_id}`
- **Description**: Get all files indexed for a specific project
- **Example**: `codebase://files/my-project`

#### Project Languages
- **URI**: `codebase://languages/{project_id}`
- **Description**: Get all languages used in a specific project with symbol counts
- **Example**: `codebase://languages/my-project`

#### Symbol Search
- **URI**: `codebase://search/{project_id}/{query}`
- **Description**: Search for symbols by name within a specific project
- **Example**: `codebase://search/my-project/UserService`

### Resource Benefits

- **Direct Access**: No need for tool calls to access indexed data
- **REST-like Patterns**: Familiar URI structure for easy integration
- **Automatic Serialization**: JSON responses with proper MIME types
- **LLM-Friendly**: Structured data that's easy for LLMs to consume
- **Real-time**: Always reflects the current state of indexed data

### Example Resource Usage

```python
# Get project statistics
stats = await client.read_resource("codebase://stats/my-project")

# Get all Python symbols in a project
symbols = await client.read_resource("codebase://symbols/my-project/python")

# Search for a specific function
results = await client.read_resource("codebase://search/my-project/calculateTotal")

# Get all files in a project
files = await client.read_resource("codebase://files/my-project")
```

### Resource Response Format

All resources return JSON data with consistent structure:

```json
{
  "project_id": "my-project",
  "total_symbols": 150,
  "symbols": [
    {
      "id": 1,
      "project_id": "my-project",
      "name": "calculateTotal",
      "symbol_type": "function",
      "language": "python",
      "file_path": "/path/to/file.py",
      "line_start": 10,
      "line_end": 15,
      "code_snippet": "def calculateTotal(items):\n    return sum(items)"
    }
  ]
}
```

## Code Relationship Mapping

The codebase analyzer now supports **code relationship mapping**, allowing AI to understand how code elements relate to each other. This enables powerful queries like "show me all callers of this function" or "find all implementations of this protocol".

### Relationship Types

The analyzer tracks several types of code relationships:

- **Function Calls**: Which functions call other functions
- **Class Inheritance**: Which classes inherit from other classes
- **Interface Implementation**: Which classes implement interfaces/protocols
- **Method Calls**: Which methods call other methods
- **Dependencies**: Cross-file and cross-module dependencies

### Available Tools

#### Find Function Callers
```python
# Find all callers of a specific function
result = await client.call_tool("find_function_callers", {
    "function_name": "calculateTotal",
    "project_id": "my-project"
})
```

#### Find Interface Implementations
```python
# Find all implementations of an interface/protocol
result = await client.call_tool("find_interface_implementations", {
    "interface_name": "DataProcessor",
    "project_id": "my-project"
})
```

#### Get Symbol Relationships
```python
# Get all relationships for a specific symbol
result = await client.call_tool("get_symbol_relationships", {
    "symbol_name": "UserService",
    "relationship_type": "calls",  # Optional filter
    "direction": "both",  # "incoming", "outgoing", or "both"
    "project_id": "my-project"
})
```

#### Get Dependency Graph
```python
# Get a complete dependency graph for the project
result = await client.call_tool("get_dependency_graph", {
    "project_id": "my-project",
    "max_depth": 3
})
```

#### Analyze Call Hierarchy
```python
# Analyze the call hierarchy for a specific function
result = await client.call_tool("analyze_call_hierarchy", {
    "function_name": "main",
    "project_id": "my-project",
    "max_depth": 3
})
```

### Available Resources

#### Function Callers
- **URI**: `codebase://callers/{project_id}/{function_name}`
- **Description**: Get all callers of a specific function
- **Example**: `codebase://callers/my-project/calculateTotal`

#### Interface Implementations
- **URI**: `codebase://implementations/{project_id}/{interface_name}`
- **Description**: Get all implementations of an interface/protocol
- **Example**: `codebase://implementations/my-project/DataProcessor`

#### Symbol Relationships
- **URI**: `codebase://relationships/{project_id}/{symbol_name}`
- **Description**: Get all relationships for a specific symbol
- **Example**: `codebase://relationships/my-project/UserService`

#### Project Dependencies
- **URI**: `codebase://dependencies/{project_id}`
- **Description**: Get dependency graph for a project
- **Example**: `codebase://dependencies/my-project`

#### Call Hierarchy
- **URI**: `codebase://hierarchy/{project_id}/{function_name}`
- **Description**: Get call hierarchy for a specific function
- **Example**: `codebase://hierarchy/my-project/main`

### Example Use Cases

#### 1. Impact Analysis
```python
# Find all functions that would be affected if we change calculateTotal
callers = await client.read_resource("codebase://callers/my-project/calculateTotal")
print(f"Changing calculateTotal would affect {len(callers['callers'])} functions")
```

#### 2. Interface Discovery
```python
# Find all classes that implement a specific interface
implementations = await client.read_resource("codebase://implementations/my-project/DataProcessor")
for impl in implementations['implementations']:
    print(f"Found implementation: {impl['implementation']['name']}")
```

#### 3. Dependency Visualization
```python
# Get the complete dependency graph
graph = await client.read_resource("codebase://dependencies/my-project")
print(f"Project has {graph['total_nodes']} symbols with {graph['total_edges']} relationships")
```

#### 4. Call Chain Analysis
```python
# Analyze the call hierarchy for the main function
hierarchy = await client.read_resource("codebase://hierarchy/my-project/main")
print(f"Main function calls {len(hierarchy['callees'])} other functions")
print(f"Main function is called by {len(hierarchy['callers'])} functions")
```

### Relationship Data Structure

Relationships are stored with the following structure:

```json
{
  "source_symbol_id": 123,
  "target_symbol_id": 456,
  "relationship_type": "calls",
  "relationship_data": {
    "line": 15,
    "target_type": "function"
  }
}
```

### Benefits

- **Impact Analysis**: Understand what code would be affected by changes
- **Refactoring Support**: Find all usages before refactoring
- **Architecture Understanding**: Visualize code dependencies and relationships
- **Code Navigation**: Navigate through call chains and inheritance hierarchies
- **Documentation**: Automatically generate relationship documentation
- **Testing**: Identify which functions need testing based on usage

## Examples

### Basic Usage

```python
# Index a Python project
await index_codebase("/path/to/python/app", "python-app")

# Search for a specific function
results = await search_symbol_by_name("calculate_total", "python", "python-app")

# Semantic search for authentication functions
results = await search_symbol_semantic("user authentication login", 5, "python-app")
```

### Advanced Usage

```python
# Index multiple related projects
await index_codebase("/path/to/monorepo/frontend", "frontend")
await index_codebase("/path/to/monorepo/backend", "backend")
await index_codebase("/path/to/monorepo/shared", "shared")

# Cross-project search
results = await search_symbol_semantic("API endpoint", 10)  # Searches all projects

# Project-specific search
results = await search_symbol_by_name("UserService", "typescript", "frontend")
```

## Architecture

### Components

1. **Database Layer** (`db.py`)
   - SQLite with sqlite-vec for vector storage
   - Symbol metadata and embeddings tables
   - Incremental update support via file hashing

2. **Embedding Manager** (`embeddings.py`)
   - SpaCy integration for vector generation
   - Code-specific text preprocessing
   - Batch processing support

3. **Code Parser** (`parser.py`)
   - Tree-sitter WASM grammar loading
   - Language detection and symbol extraction
   - Query-based pattern matching

4. **FastMCP Server** (`main.py`)
   - Async command registration
   - Component orchestration
   - Error handling and logging

### Database Schema

```sql
-- Symbols table
CREATE TABLE symbols (
    id INTEGER PRIMARY KEY,
    language TEXT NOT NULL,
    symbol_type TEXT NOT NULL,
    name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    code_snippet TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(language, name, file_path, line_start)
);

-- Vector embeddings table
CREATE VIRTUAL TABLE symbol_embeddings 
USING vec0(
    id INTEGER PRIMARY KEY,
    embedding FLOAT[300]
);
```

## Configuration

### Environment Variables

- `SPACY_MODEL`: SpaCy model name (default: `en_core_web_md`)
- `DB_PATH`: Database file path (default: `codebase_analyzer.db`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Customization

#### Adding New Languages

1. Add the Tree-sitter WASM grammar to `grammars/`
2. Create a query file in `queries/` (see existing examples)
3. Update the language mapping in `parser.py`

#### Using Different Embedding Models

```python
# In main.py, modify the EmbeddingManager initialization:
embedding_manager = EmbeddingManager(model_name="en_core_web_trf")
```

## Performance Tips

1. **Use SSD storage** for better database performance
2. **Increase batch size** for large codebases
3. **Use `en_core_web_trf`** for better semantic search quality
4. **Monitor memory usage** with large embedding models

## Troubleshooting

### Common Issues

1. **SpaCy model not found**:
   ```bash
   python -m spacy download en_core_web_md
   ```

2. **sqlite-vec not available**:
   ```bash
   pip install sqlite-vec
   ```
   
   > **Note**: If you get "no such module: vec0" errors, the server will automatically fall back to a simpler storage method. Semantic search functionality will be limited but the server will still work.

3. **Tree-sitter grammar errors**:
   - Check that WASM files are in `grammars/`
   - Verify query files exist in `queries/`

4. **Memory issues with large codebases**:
   - Process in smaller batches
   - Use smaller embedding models
   - Monitor system resources

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
fastmcp serve main.py
```

## Development

### Project Structure

```
codebase-analyzer/
├── main.py              # FastMCP server entrypoint
├── db.py                # Database layer
├── embeddings.py        # SpaCy embedding manager
├── parser.py            # Tree-sitter parser
├── grammars/            # Tree-sitter WASM grammars
├── queries/             # Language-specific queries
├── pyproject.toml       # Dependencies and metadata
└── README.md           # This file
```

### Adding Features

1. **New MCP Commands**: Add `@mcp_command` decorators in `main.py`
2. **Database Schema**: Modify `db.py` and run migrations
3. **Language Support**: Add grammars and queries
4. **Embedding Models**: Extend `embeddings.py`

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
