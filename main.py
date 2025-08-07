#!/usr/bin/env python3
"""
FastMCP server for codebase parsing and semantic search.
"""

import logging
from pathlib import Path
from typing import Optional

from fastmcp import FastMCP, Context
from db import DatabaseManager
from embeddings import EmbeddingManager
from parsers.code_parser import CodeParser
from git_utils import GitManager
from models import (
    # Input models
    IndexCodebaseInput, SearchSymbolByNameInput, SearchSymbolSemanticInput,
    ForceFullRescanInput, DeleteProjectInput, GetProjectInfoInput, GetStatsInput,
    FindFunctionCallersInput, FindInterfaceImplementationsInput, GetSymbolRelationshipsInput,
    GetDependencyGraphInput, AnalyzeCallHierarchyInput,
    # Output models
    IndexCodebaseOutput, SearchSymbolByNameOutput, SearchSymbolSemanticOutput,
    ListProjectsOutput, ForceFullRescanOutput, DeleteProjectOutput, GetProjectInfoOutput,
    GetStatsOutput, HealthCheckOutput, FindFunctionCallersOutput, FindInterfaceImplementationsOutput,
    GetSymbolRelationshipsOutput, GetDependencyGraphOutput, AnalyzeCallHierarchyOutput,
    # Base models
    Symbol, SymbolType, RelationshipType, Direction, HealthStatus, DatabaseStats,
    ProjectInfo, GitInfo, EmbeddingModelInfo, HealthStatusInfo, Caller, Function,
    CallerInfo, Implementation, Interface, ImplementationInfo, SymbolRelationship,
    DependencyNode, DependencyEdge, Relationship, RelatedSymbol
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
app: FastMCP = FastMCP("codebase-analyzer")

# Global instances
db_manager: Optional[DatabaseManager] = None
embedding_manager: Optional[EmbeddingManager] = None
code_parser: Optional[CodeParser] = None


async def startup():
    """Initialize components on server startup."""
    global db_manager, embedding_manager, code_parser
    
    try:
        # Initialize database
        db_manager = DatabaseManager()
        logger.info("Database manager initialized")
        
        # Initialize embedding manager
        embedding_manager = EmbeddingManager()
        logger.info("Embedding manager initialized")
        
        # Initialize code parser
        code_parser = CodeParser()
        logger.info("Code parser initialized")
        
        logger.info("Codebase analyzer server started successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise


# ============================================================================
# RESOURCES
# ============================================================================


@app.resource("codebase://stats/{project_id}")
async def get_project_stats_resource(project_id: str, ctx: Optional[Context] = None) -> dict:
    """Get database statistics for a specific project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    stats = db_manager.get_stats(project_id)
    
    # Add embedding model info
    embedding_info = {}
    if embedding_manager:
        embedding_info = embedding_manager.get_model_info()
    
    return {
        "database_stats": stats,
        "embedding_model": embedding_info
    }


@app.resource("codebase://projects")
async def get_projects() -> list:
    """Get all projects."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    projects = db_manager.list_projects()
    return projects


@app.resource("codebase://symbols/{project_id}")
async def get_project_symbols(project_id: str, ctx: Optional[Context] = None) -> dict:
    """Get all symbols for a specific project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    # Get symbols for the project
    with db_manager._get_connection() as conn:
        conn.row_factory = db_manager._get_connection().row_factory
        cursor = conn.execute(
            "SELECT * FROM symbols WHERE project_id = ? ORDER BY language, name",
            (project_id,)
        )
        symbols = [dict(row) for row in cursor.fetchall()]
    
    return {
        "project_id": project_id,
        "total_symbols": len(symbols),
        "symbols": symbols
    }


@app.resource("codebase://symbols/{project_id}/{language}")
async def get_project_language_symbols(project_id: str, language: str, ctx: Optional[Context] = None) -> dict:
    """Get all symbols for a specific project and language."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    # Get symbols for the project and language
    with db_manager._get_connection() as conn:
        conn.row_factory = db_manager._get_connection().row_factory
        cursor = conn.execute(
            "SELECT * FROM symbols WHERE project_id = ? AND language = ? ORDER BY name",
            (project_id, language)
        )
        symbols = [dict(row) for row in cursor.fetchall()]
    
    return {
        "project_id": project_id,
        "language": language,
        "total_symbols": len(symbols),
        "symbols": symbols
    }


@app.resource("codebase://search/{project_id}/{query}")
async def search_symbols_in_project(project_id: str, query: str, ctx: Optional[Context] = None) -> dict:
    """Search for symbols by name within a specific project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    results = db_manager.search_by_name(query, project_id=project_id)
    
    return {
        "query": query,
        "project_id": project_id,
        "total_results": len(results),
        "results": results
    }


@app.resource("codebase://files/{project_id}")
async def get_project_files(project_id: str, ctx: Optional[Context] = None) -> dict:
    """Get all files indexed for a specific project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    with db_manager._get_connection() as conn:
        cursor = conn.execute(
            "SELECT DISTINCT file_path, language FROM symbols WHERE project_id = ? ORDER BY file_path",
            (project_id,)
        )
        files = [{"file_path": row[0], "language": row[1]} for row in cursor.fetchall()]
    
    return {
        "project_id": project_id,
        "total_files": len(files),
        "files": files
    }


@app.resource("codebase://languages/{project_id}")
async def get_project_languages(project_id: str, ctx: Optional[Context] = None) -> dict:
    """Get all languages used in a specific project with symbol counts."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    with db_manager._get_connection() as conn:
        cursor = conn.execute(
            "SELECT language, COUNT(*) as symbol_count FROM symbols WHERE project_id = ? GROUP BY language ORDER BY symbol_count DESC",
            (project_id,)
        )
        languages = [{"language": row[0], "symbol_count": row[1]} for row in cursor.fetchall()]
    
    return {
        "project_id": project_id,
        "total_languages": len(languages),
        "languages": languages
    }


@app.resource("codebase://callers/{project_id}/{function_name}")
async def get_function_callers(project_id: str, function_name: str, ctx: Optional[Context] = None) -> dict:
    """Get all callers of a specific function in a project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    callers = db_manager.find_callers(function_name, project_id)
    
    formatted_results = []
    for caller in callers:
        formatted_results.append({
            "caller": {
                "name": caller['caller_name'],
                "type": caller['caller_type'],
                "file": caller['caller_file'],
                "line": caller['caller_line'],
                "code": caller['caller_code']
            },
            "function": {
                "name": caller['function_name'],
                "file": caller['function_file'],
                "line": caller['function_line']
            }
        })
    
    return {
        "function_name": function_name,
        "project_id": project_id,
        "total_callers": len(formatted_results),
        "callers": formatted_results
    }


@app.resource("codebase://implementations/{project_id}/{interface_name}")
async def get_interface_implementations(project_id: str, interface_name: str, ctx: Optional[Context] = None) -> dict:
    """Get all implementations of an interface/protocol in a project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    implementations = db_manager.find_implementations(interface_name, project_id)
    
    formatted_results = []
    for impl in implementations:
        formatted_results.append({
            "implementation": {
                "name": impl['implementation_name'],
                "type": impl['implementation_type'],
                "file": impl['implementation_file'],
                "line": impl['implementation_line'],
                "code": impl['implementation_code']
            },
            "interface": {
                "name": impl['interface_name'],
                "file": impl['interface_file'],
                "line": impl['interface_line']
            }
        })
    
    return {
        "interface_name": interface_name,
        "project_id": project_id,
        "total_implementations": len(formatted_results),
        "implementations": formatted_results
    }


@app.resource("codebase://relationships/{project_id}/{symbol_name}")
async def get_symbol_relationships_resource(project_id: str, symbol_name: str, ctx: Optional[Context] = None) -> dict:
    """Get all relationships for a specific symbol in a project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    # Find the symbol first
    symbols = db_manager.search_by_name(symbol_name, project_id=project_id)
    if not symbols:
        return {
            "symbol_name": symbol_name,
            "project_id": project_id,
            "error": "Symbol not found"
        }
    
    # Get relationships for each symbol
    all_relationships = []
    for symbol in symbols:
        relationships = db_manager.get_symbol_relationships(
            symbol['id'], 
            project_id=project_id
        )
        
        for rel in relationships:
            all_relationships.append({
                "symbol": {
                    "name": symbol['name'],
                    "type": symbol['symbol_type'],
                    "file": symbol['file_path'],
                    "line": symbol['line_start']
                },
                "relationship": {
                    "type": rel['relationship_type'],
                    "direction": rel['direction'],
                    "data": rel['relationship_data']
                },
                "related_symbol": {
                    "name": rel['source_name'] if rel['direction'] == 'outgoing' else rel['target_name'],
                    "type": rel['source_type'] if rel['direction'] == 'outgoing' else rel['target_type'],
                    "file": rel['source_file'] if rel['direction'] == 'outgoing' else rel['target_file'],
                    "line": rel['source_line'] if rel['direction'] == 'outgoing' else rel['target_line']
                }
            })
    
    return {
        "symbol_name": symbol_name,
        "project_id": project_id,
        "total_relationships": len(all_relationships),
        "relationships": all_relationships
    }


@app.resource("codebase://dependencies/{project_id}")
async def get_project_dependencies(project_id: str, ctx: Optional[Context] = None) -> dict:
    """Get dependency graph for a project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    graph = db_manager.get_dependency_graph(project_id)
    
    return {
        "project_id": project_id,
        "total_nodes": graph['total_nodes'],
        "total_edges": graph['total_edges'],
        "nodes": graph['nodes'],
        "edges": graph['edges']
    }


@app.resource("codebase://hierarchy/{project_id}/{function_name}")
async def get_call_hierarchy(project_id: str, function_name: str, ctx: Optional[Context] = None) -> dict:
    """Get call hierarchy for a specific function in a project."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    # Find the function
    functions = db_manager.search_by_name(function_name, project_id=project_id)
    if not functions:
        return {
            "function_name": function_name,
            "project_id": project_id,
            "error": "Function not found"
        }
    
    # Build call hierarchy
    hierarchy = {
        "function": {
            "name": function_name,
            "project_id": project_id
        },
        "callers": [],
        "callees": []
    }
    
    # Get callers (who calls this function)
    callers = db_manager.find_callers(function_name, project_id)
    hierarchy["callers"] = [{
        "name": caller['caller_name'],
        "type": caller['caller_type'],
        "file": caller['caller_file'],
        "line": caller['caller_line']
    } for caller in callers]
    
    # Get callees (what this function calls)
    for function in functions:
        relationships = db_manager.get_symbol_relationships(
            function['id'],
            relationship_type='calls',
            direction='outgoing',
            project_id=project_id
        )
        
        for rel in relationships:
            hierarchy["callees"].append({
                "name": rel['target_name'],
                "type": rel['target_type'],
                "file": rel['target_file'],
                "line": rel['target_line']
            })
    
    return hierarchy


# ============================================================================
# TOOLS
# ============================================================================


@app.tool("index_codebase")
async def index_codebase(input_data: IndexCodebaseInput, ctx: Optional[Context] = None) -> IndexCodebaseOutput:
    """
    Parse and index a codebase directory with smart incremental scanning for git repositories.
    
    Args:
        input_data: Input parameters for indexing
        ctx: FastMCP context for progress reporting
        
    Returns:
        Indexing statistics and results
    """
    if not db_manager or not embedding_manager or not code_parser:
        raise RuntimeError("Server not properly initialized")
    
    try:
        codebase_path = Path(input_data.path)
        if not codebase_path.exists():
            return IndexCodebaseOutput(
                success=False,
                project_id=input_data.project_id,
                is_git_repo=False,
                processed_files=0,
                total_symbols_added=0,
                errors=[f"Path does not exist: {input_data.path}"],
                database_stats=DatabaseStats(
                    total_symbols=0, total_files=0, total_projects=0,
                    total_relationships=0, total_embeddings=0,
                    languages={}, symbol_types={}
                ),
                error=f"Path does not exist: {input_data.path}"
            )
        
        if not codebase_path.is_dir():
            return IndexCodebaseOutput(
                success=False,
                project_id=input_data.project_id,
                is_git_repo=False,
                processed_files=0,
                total_symbols_added=0,
                errors=[f"Path is not a directory: {input_data.path}"],
                database_stats=DatabaseStats(
                    total_symbols=0, total_files=0, total_projects=0,
                    total_relationships=0, total_embeddings=0,
                    languages={}, symbol_types={}
                ),
                error=f"Path is not a directory: {input_data.path}"
            )
        
        logger.info(f"Starting to index codebase: {input_data.path} for project: {input_data.project_id}")
        
        # Initialize git manager and check if this is a git repository
        git_manager = GitManager(str(codebase_path))
        is_git_repo = git_manager.is_git_repo()
        
        # Get or create project info
        project_info = db_manager.get_project_info(input_data.project_id)
        if project_info:
            last_commit_hash = project_info.get('last_commit_hash')
            last_branch = project_info.get('last_branch')
        else:
            last_commit_hash = None
            last_branch = None
        
        # Update project record
        current_commit_hash = git_manager.get_current_commit_hash() if is_git_repo else None
        current_branch = git_manager.get_current_branch() if is_git_repo else None
        
        db_manager.create_or_update_project(
            project_id=input_data.project_id,
            path=str(codebase_path),
            name=codebase_path.name,
            is_git_repo=is_git_repo,
            last_commit_hash=current_commit_hash,
            last_branch=current_branch
        )
        
        # Stage 1: File Discovery (0-10%)
        if ctx:
            await ctx.info(f"Discovering files in {input_data.path}")
            await ctx.report_progress(progress=0, total=100)
        
        # Determine which files to process based on git status
        files_to_process = []
        if is_git_repo and last_commit_hash and current_commit_hash != last_commit_hash:
            # Incremental scan: only process changed files
            if ctx:
                await ctx.info("Git repository detected - performing incremental scan")
            
            changed_files = git_manager.get_all_changed_files(last_commit_hash)
            for file_path_str in changed_files:
                if Path(file_path_str).is_file():
                    language = code_parser.detect_language(file_path_str)
                    if language:
                        files_to_process.append(file_path_str)
            
            logger.info(f"Incremental scan: found {len(files_to_process)} changed files")
        else:
            # Full scan: process all files that need updates
            if ctx:
                await ctx.info("Performing full scan of codebase")
            
            for file_path in codebase_path.rglob("*"):
                if file_path.is_file():
                    file_path_str = str(file_path)
                    language = code_parser.detect_language(file_path_str)
                    if language and db_manager.file_needs_update(file_path_str, input_data.project_id):
                        files_to_process.append(file_path_str)
            
            logger.info(f"Full scan: found {len(files_to_process)} files to process")
        
        if ctx:
            await ctx.info(f"Found {len(files_to_process)} files to process")
            await ctx.report_progress(progress=10, total=100)
        
        logger.info(f"Found {len(files_to_process)} files to process")
        
        # Process files with progress reporting
        total_symbols = 0
        processed_files = 0
        errors = []
        
        for i, file_path_str in enumerate(files_to_process):
            try:
                # Report progress for file processing (10-90%)
                progress = 10 + int((i / len(files_to_process)) * 80)
                if ctx:
                    await ctx.info(f"Processing file {i+1}/{len(files_to_process)}: {Path(file_path_str).name}")
                    await ctx.report_progress(progress=progress, total=100)
                
                # Delete existing symbols for this file
                db_manager.delete_file_symbols(file_path_str, input_data.project_id)
                # Parse file
                symbols = code_parser.parse_file(file_path_str)
                
                if symbols:
                    # Get file hash
                    file_hash = db_manager.get_file_hash(file_path_str)
                    
                    # Process symbols in batches for better memory management
                    # Use smaller batch size for files with many symbols to prevent memory issues
                    if len(symbols) > 1000:
                        batch_size = 25  # Smaller batches for very large files
                    else:
                        batch_size = 100  # Normal batch size
                    symbol_ids = {}  # Map symbol names to their IDs for relationship building
                    
                    for i in range(0, len(symbols), batch_size):
                        batch = symbols[i:i + batch_size]
                        
                        # Prepare batch data
                        batch_texts = []
                        batch_symbols = []
                        
                        for symbol in batch:
                            symbol['file_hash'] = file_hash
                            batch_symbols.append(symbol)
                            
                            # Prepare text for embedding
                            context_text = f"{symbol['symbol_type']} {symbol['name']} {symbol['code_snippet']}"
                            batch_texts.append(context_text)
                        
                        # Generate embeddings in batch
                        try:
                            batch_embeddings = embedding_manager.batch_get_embeddings(batch_texts)
                            
                            # Process each symbol in the batch
                            for j, symbol in enumerate(batch_symbols):
                                try:
                                    # Insert symbol into database
                                    symbol_id = db_manager.insert_symbol(symbol, input_data.project_id)
                                    symbol_ids[symbol['name']] = symbol_id
                                    
                                    # Store embedding
                                    db_manager.insert_embedding(symbol_id, batch_embeddings[j])
                                    
                                    total_symbols += 1
                                except Exception as symbol_error:
                                    logger.warning(f"Error processing symbol {symbol.get('name', 'unknown')} in {file_path_str}: {symbol_error}")
                                    continue
                                    
                        except Exception as batch_error:
                            logger.error(f"Error processing batch for {file_path_str}: {batch_error}")
                            # Fallback to individual processing for this batch
                            for symbol in batch_symbols:
                                try:
                                    symbol_id = db_manager.insert_symbol(symbol, input_data.project_id)
                                    symbol_ids[symbol['name']] = symbol_id
                                    
                                    # Generate embedding individually as fallback
                                    embedding = embedding_manager.get_embedding_for_code(
                                        symbol['code_snippet'],
                                        symbol['name'],
                                        symbol['symbol_type']
                                    )
                                    
                                    # Store embedding
                                    db_manager.insert_embedding(symbol_id, embedding)
                                    
                                    total_symbols += 1
                                except Exception as symbol_error:
                                    logger.warning(f"Error processing symbol {symbol.get('name', 'unknown')} in {file_path_str}: {symbol_error}")
                                    continue
                    
                    # Process relationships
                    total_relationships = 0
                    for symbol in symbols:
                        if 'relationships' in symbol and symbol['relationships']:
                            source_id = symbol_ids.get(symbol['name'])
                            if source_id:
                                for rel in symbol['relationships']:
                                    try:
                                        # Find target symbol
                                        target_symbols = db_manager.search_by_name(rel['target'], project_id=input_data.project_id)
                                        if target_symbols:
                                            # Use the first matching target
                                            target_id = target_symbols[0]['id']
                                            db_manager.insert_relationship(
                                                source_id, target_id, rel['type'], 
                                                input_data.project_id, rel
                                            )
                                            total_relationships += 1
                                    except Exception as rel_error:
                                        logger.warning(f"Error processing relationship {rel} for {symbol['name']}: {rel_error}")
                                        continue
                    
                    processed_files += 1
                    logger.info(f"Processed {file_path_str}: {len(symbols)} symbols")
                else:
                    logger.info(f"No symbols found in {file_path_str} (this is normal for some files)")
                
            except Exception as e:
                error_msg = f"Error processing {file_path_str}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        # Stage 3: Finalization (90-100%)
        if ctx:
            await ctx.info("Finalizing indexing...")
            await ctx.report_progress(progress=90, total=100)
        
        # Update project scan information
        if is_git_repo:
            db_manager.update_project_scan_info(
                input_data.project_id, 
                current_commit_hash, 
                current_branch
            )
        
        # Get final statistics
        stats = db_manager.get_stats(input_data.project_id)
        
        if ctx:
            await ctx.info(f"Indexing completed: {processed_files} files, {total_symbols} symbols")
            await ctx.report_progress(progress=100, total=100)
        
        # Convert stats to DatabaseStats model
        database_stats = DatabaseStats(
            total_symbols=stats.get('total_symbols', 0),
            total_files=stats.get('total_files', 0),
            total_projects=stats.get('total_projects', 0),
            total_relationships=stats.get('total_relationships', 0),
            total_embeddings=stats.get('total_embeddings', 0),
            languages=stats.get('languages', {}),
            symbol_types=stats.get('symbol_types', {})
        )
        
        result = IndexCodebaseOutput(
            success=True,
            project_id=input_data.project_id,
            is_git_repo=is_git_repo,
            current_commit_hash=current_commit_hash,
            current_branch=current_branch,
            last_commit_hash=last_commit_hash,
            last_branch=last_branch,
            processed_files=processed_files,
            total_symbols_added=total_symbols,
            errors=errors,
            database_stats=database_stats
        )
        
        logger.info(f"Indexing completed for project {input_data.project_id}: {processed_files} files, {total_symbols} symbols")
        return result
        
    except Exception as e:
        logger.error(f"Error during indexing: {e}")
        return IndexCodebaseOutput(
            success=False,
            project_id=input_data.project_id,
            is_git_repo=False,
            processed_files=0,
            total_symbols_added=0,
            errors=[str(e)],
            database_stats=DatabaseStats(
                total_symbols=0, total_files=0, total_projects=0,
                total_relationships=0, total_embeddings=0,
                languages={}, symbol_types={}
            ),
            error=str(e)
        )


@app.tool("search_symbol_by_name")
async def search_symbol_by_name(input_data: SearchSymbolByNameInput) -> SearchSymbolByNameOutput:
    """
    Search for symbols by exact name match.
    
    Args:
        input_data: Input parameters for symbol search
        
    Returns:
        Search results with symbol information
    """
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    try:
        logger.info(f"Searching for symbol: {input_data.name} (language: {input_data.language}, project: {input_data.project_id})")
        
        results = db_manager.search_by_name(input_data.name, input_data.language, input_data.project_id)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(Symbol(
                id=result["id"],
                project_id=result["project_id"],
                name=result["name"],
                symbol_type=SymbolType(result["symbol_type"]),
                language=result["language"],
                file_path=result["file_path"],
                line_start=result["line_start"],
                line_end=result["line_end"],
                code_snippet=result["code_snippet"]
            ))
        
        return SearchSymbolByNameOutput(
            success=True,
            query=input_data.name,
            language_filter=input_data.language,
            project_filter=input_data.project_id,
            total_results=len(formatted_results),
            results=formatted_results
        )
        
    except Exception as e:
        logger.error(f"Error during name search: {e}")
        return SearchSymbolByNameOutput(
            success=False,
            query=input_data.name,
            language_filter=input_data.language,
            project_filter=input_data.project_id,
            total_results=0,
            results=[],
            error=str(e)
        )


@app.tool("search_symbol_semantic")
async def search_symbol_semantic(input_data: SearchSymbolSemanticInput) -> SearchSymbolSemanticOutput:
    """
    Search for symbols using semantic similarity.
    
    Args:
        input_data: Input parameters for semantic search
        
    Returns:
        Search results with symbol information
    """
    if not db_manager or not embedding_manager:
        raise RuntimeError("Server not properly initialized")
    
    try:
        logger.info(f"Semantic search: {input_data.query} (top_k: {input_data.top_k}, project: {input_data.project_id})")
        
        # Generate embedding for the query
        query_embedding = embedding_manager.get_embedding(input_data.query)
        
        # Search in database
        results = db_manager.search_semantic(query_embedding, input_data.top_k, input_data.project_id)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(Symbol(
                id=result["id"],
                project_id=result["project_id"],
                name=result["name"],
                symbol_type=SymbolType(result["symbol_type"]),
                language=result["language"],
                file_path=result["file_path"],
                line_start=result["line_start"],
                line_end=result["line_end"],
                code_snippet=result["code_snippet"],
                score=result.get("score", 0.0)
            ))
        
        return SearchSymbolSemanticOutput(
            success=True,
            query=input_data.query,
            top_k=input_data.top_k,
            project_filter=input_data.project_id,
            total_results=len(formatted_results),
            results=formatted_results
        )
        
    except Exception as e:
        logger.error(f"Error during semantic search: {e}")
        return SearchSymbolSemanticOutput(
            success=False,
            query=input_data.query,
            top_k=input_data.top_k,
            project_filter=input_data.project_id,
            total_results=0,
            results=[],
            error=str(e)
        )


@app.tool("list_projects")
async def list_projects() -> ListProjectsOutput:
    """
    List all projects in the database with their statistics and git information.
    
    Returns:
        Project information with statistics
    """
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    try:
        projects = db_manager.list_projects()
        
        # Add git information for each project
        enhanced_projects = []
        for project in projects:
            project_id = project['project_id']
            project_info = db_manager.get_project_info(project_id)
            
            enhanced_project = ProjectInfo(
                project_id=project['project_id'],
                name=project['name'],
                path=project['path'],
                is_git_repo=project_info.get('is_git_repo', False) if project_info else False,
                last_commit_hash=project_info.get('last_commit_hash') if project_info else None,
                last_branch=project_info.get('last_branch') if project_info else None,
                last_scan_time=project_info.get('last_scan_time') if project_info else None,
                total_symbols=project.get('total_symbols'),
                total_files=project.get('total_files')
            )
            enhanced_projects.append(enhanced_project)
        
        return ListProjectsOutput(
            success=True,
            total_projects=len(enhanced_projects),
            projects=enhanced_projects
        )
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return ListProjectsOutput(
            success=False,
            total_projects=0,
            projects=[],
            error=str(e)
        )


@app.tool("force_full_rescan")
async def force_full_rescan(input_data: ForceFullRescanInput, ctx: Optional[Context] = None) -> ForceFullRescanOutput:
    """
    Force a full rescan of a project by clearing the last commit hash.
    
    Args:
        input_data: Input parameters for rescan
        ctx: FastMCP context for progress reporting
        
    Returns:
        Rescan status information
    """
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    try:
        logger.info(f"Forcing full rescan of project: {input_data.project_id}")
        
        if ctx:
            await ctx.info(f"Clearing git tracking for project: {input_data.project_id}")
        
        # Clear the last commit hash to force a full scan
        db_manager.update_project_scan_info(input_data.project_id, None, None)
        
        if ctx:
            await ctx.info("Git tracking cleared. Next scan will be full.")
        
        return ForceFullRescanOutput(
            success=True,
            project_id=input_data.project_id,
            message=f"Project {input_data.project_id} marked for full rescan"
        )
        
    except Exception as e:
        logger.error(f"Error forcing full rescan: {e}")
        return ForceFullRescanOutput(
            success=False,
            project_id=input_data.project_id,
            message="",
            error=str(e)
        )


@app.tool("delete_project")
async def delete_project(input_data: DeleteProjectInput, ctx: Optional[Context] = None) -> DeleteProjectOutput:
    """
    Delete all symbols and embeddings for a specific project.
    
    Args:
        input_data: Input parameters for project deletion
        ctx: FastMCP context for progress reporting
        
    Returns:
        Deletion status information
    """
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    try:
        logger.info(f"Deleting project: {input_data.project_id}")
        
        if ctx:
            await ctx.info(f"Starting deletion of project: {input_data.project_id}")
            await ctx.report_progress(progress=0, total=100)
        
        # Get project stats before deletion
        stats_before = db_manager.get_stats(input_data.project_id)
        
        if ctx:
            await ctx.info(f"Found {stats_before.get('total_symbols', 0)} symbols to delete")
            await ctx.report_progress(progress=25, total=100)
        
        # Delete the project
        db_manager.delete_project(input_data.project_id)
        
        if ctx:
            await ctx.info("Project deletion completed")
            await ctx.report_progress(progress=100, total=100)
        
        return DeleteProjectOutput(
            success=True,
            project_id=input_data.project_id,
            deleted_symbols=stats_before.get("total_symbols", 0),
            deleted_files=stats_before.get("total_files", 0),
            message=f"Project {input_data.project_id} deleted successfully"
        )
        
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        return DeleteProjectOutput(
            success=False,
            project_id=input_data.project_id,
            deleted_symbols=0,
            deleted_files=0,
            message="",
            error=str(e)
        )


@app.tool("get_project_info")
async def get_project_info(input_data: GetProjectInfoInput) -> GetProjectInfoOutput:
    """
    Get detailed information about a specific project including git status.
    
    Args:
        input_data: Input parameters for project info retrieval
        
    Returns:
        Project information with git status
    """
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    try:
        project_info = db_manager.get_project_info(input_data.project_id)
        if not project_info:
            return GetProjectInfoOutput(
                success=False,
                project_info=None,
                git_info=None,
                database_stats=None,
                error=f"Project {input_data.project_id} not found"
            )
        
        # Get git information if it's a git repository
        git_info = None
        if project_info.get('is_git_repo') and project_info.get('path'):
            try:
                git_manager = GitManager(project_info['path'])
                git_repo_info = git_manager.get_repo_info()
                git_info = GitInfo(
                    current_branch=git_repo_info.get('current_branch', ''),
                    current_commit_hash=git_repo_info.get('current_commit_hash', ''),
                    remote_url=git_repo_info.get('remote_url'),
                    status=git_repo_info.get('status')
                )
            except Exception as e:
                git_info = GitInfo(
                    current_branch='',
                    current_commit_hash='',
                    remote_url=None,
                    status=f"Error: {str(e)}"
                )
        
        # Get database statistics
        stats = db_manager.get_stats(input_data.project_id)
        database_stats = DatabaseStats(
            total_symbols=stats.get('total_symbols', 0),
            total_files=stats.get('total_files', 0),
            total_projects=stats.get('total_projects', 0),
            total_relationships=stats.get('total_relationships', 0),
            total_embeddings=stats.get('total_embeddings', 0),
            languages=stats.get('languages', {}),
            symbol_types=stats.get('symbol_types', {})
        )
        
        project_info_model = ProjectInfo(
            project_id=project_info['project_id'],
            name=project_info['name'],
            path=project_info['path'],
            is_git_repo=project_info.get('is_git_repo', False),
            last_commit_hash=project_info.get('last_commit_hash'),
            last_branch=project_info.get('last_branch'),
            last_scan_time=project_info.get('last_scan_time'),
            total_symbols=project_info.get('total_symbols'),
            total_files=project_info.get('total_files')
        )
        
        return GetProjectInfoOutput(
            success=True,
            project_info=project_info_model,
            git_info=git_info,
            database_stats=database_stats
        )
        
    except Exception as e:
        logger.error(f"Error getting project info: {e}")
        return GetProjectInfoOutput(
            success=False,
            project_info=None,
            git_info=None,
            database_stats=None,
            error=str(e)
        )


@app.tool("get_stats")
async def get_stats(input_data: GetStatsInput) -> GetStatsOutput:
    """
    Get database statistics.
    
    Args:
        input_data: Input parameters for stats retrieval
        
    Returns:
        Database statistics with embedding model info
    """
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    try:
        stats = db_manager.get_stats(input_data.project_id)
        
        # Add embedding model info
        embedding_info = None
        if embedding_manager:
            model_info = embedding_manager.get_model_info()
            embedding_info = EmbeddingModelInfo(
                model_name=model_info.get('model_name', ''),
                model_dimensions=model_info.get('model_dimensions', 0),
                model_provider=model_info.get('model_provider', '')
            )
        
        database_stats = DatabaseStats(
            total_symbols=stats.get('total_symbols', 0),
            total_files=stats.get('total_files', 0),
            total_projects=stats.get('total_projects', 0),
            total_relationships=stats.get('total_relationships', 0),
            total_embeddings=stats.get('total_embeddings', 0),
            languages=stats.get('languages', {}),
            symbol_types=stats.get('symbol_types', {})
        )
        
        return GetStatsOutput(
            success=True,
            database_stats=database_stats,
            embedding_model=embedding_info
        )
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return GetStatsOutput(
            success=False,
            database_stats=DatabaseStats(
                total_symbols=0, total_files=0, total_projects=0,
                total_relationships=0, total_embeddings=0,
                languages={}, symbol_types={}
            ),
            embedding_model=None,
            error=str(e)
        )


@app.tool("health_check")
async def health_check() -> HealthCheckOutput:
    """
    Check server health and component status.
    
    Returns:
        Health status information
    """
    try:
        health_status = HealthStatusInfo(
            server=HealthStatus.RUNNING,
            database=HealthStatus.UNKNOWN,
            embeddings=HealthStatus.UNKNOWN,
            parser=HealthStatus.UNKNOWN
        )
        
        if db_manager:
            try:
                db_manager.get_stats()
                health_status.database = HealthStatus.HEALTHY
            except Exception as e:
                health_status.database = f"error: {e}"
        
        if embedding_manager:
            try:
                embedding_manager.get_model_info()
                health_status.embeddings = HealthStatus.HEALTHY
            except Exception as e:
                health_status.embeddings = f"error: {e}"
        
        if code_parser:
            health_status.parser = HealthStatus.HEALTHY
        
        return HealthCheckOutput(
            success=True,
            health=health_status
        )
        
    except Exception as e:
        logger.error(f"Error during health check: {e}")
        return HealthCheckOutput(
            success=False,
            health=HealthStatusInfo(
                server=HealthStatus.ERROR,
                database=HealthStatus.ERROR,
                embeddings=HealthStatus.ERROR,
                parser=HealthStatus.ERROR
            ),
            error=str(e)
        )


@app.tool()
async def find_function_callers(input_data: FindFunctionCallersInput, ctx: Optional[Context] = None) -> FindFunctionCallersOutput:
    """Find all callers of a specific function or method."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    if ctx:
        await ctx.info(f"Searching for callers of function '{input_data.function_name}'")
    
    callers = db_manager.find_callers(input_data.function_name, input_data.project_id)
    
    # Format results
    formatted_results = []
    for caller in callers:
        formatted_results.append(CallerInfo(
            caller=Caller(
                name=caller['caller_name'],
                type=SymbolType(caller['caller_type']),
                file=caller['caller_file'],
                line=caller['caller_line'],
                code=caller['caller_code']
            ),
            function=Function(
                name=caller['function_name'],
                file=caller['function_file'],
                line=caller['function_line']
            ),
            project_id=input_data.project_id or "all"
        ))
    
    return FindFunctionCallersOutput(
        function_name=input_data.function_name,
        project_id=input_data.project_id,
        total_callers=len(formatted_results),
        callers=formatted_results
    )


@app.tool()
async def find_interface_implementations(input_data: FindInterfaceImplementationsInput, ctx: Optional[Context] = None) -> FindInterfaceImplementationsOutput:
    """Find all implementations of an interface, protocol, or abstract class."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    if ctx:
        await ctx.info(f"Searching for implementations of '{input_data.interface_name}'")
    
    implementations = db_manager.find_implementations(input_data.interface_name, input_data.project_id)
    
    # Format results
    formatted_results = []
    for impl in implementations:
        formatted_results.append(ImplementationInfo(
            implementation=Implementation(
                name=impl['implementation_name'],
                type=SymbolType(impl['implementation_type']),
                file=impl['implementation_file'],
                line=impl['implementation_line'],
                code=impl['implementation_code']
            ),
            interface=Interface(
                name=impl['interface_name'],
                file=impl['interface_file'],
                line=impl['interface_line']
            ),
            project_id=input_data.project_id or "all"
        ))
    
    return FindInterfaceImplementationsOutput(
        interface_name=input_data.interface_name,
        project_id=input_data.project_id,
        total_implementations=len(formatted_results),
        implementations=formatted_results
    )


@app.tool()
async def get_symbol_relationships(input_data: GetSymbolRelationshipsInput, ctx: Optional[Context] = None) -> GetSymbolRelationshipsOutput:
    """Get all relationships for a specific symbol."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    if ctx:
        await ctx.info(f"Getting relationships for symbol '{input_data.symbol_name}'")
    
    # Find the symbol first
    symbols = db_manager.search_by_name(input_data.symbol_name, project_id=input_data.project_id)
    if not symbols:
        return GetSymbolRelationshipsOutput(
            symbol_name=input_data.symbol_name,
            project_id=input_data.project_id,
            relationship_type=input_data.relationship_type,
            direction=input_data.direction,
            total_relationships=0,
            relationships=[],
            error="Symbol not found"
        )
    
    # Get relationships for each symbol
    all_relationships = []
    for symbol in symbols:
        relationships = db_manager.get_symbol_relationships(
            symbol['id'], 
            relationship_type=input_data.relationship_type.value if input_data.relationship_type else None,
            direction=input_data.direction.value,
            project_id=input_data.project_id
        )
        
        for rel in relationships:
            all_relationships.append(SymbolRelationship(
                symbol=Symbol(
                    name=symbol['name'],
                    symbol_type=SymbolType(symbol['symbol_type']),
                    language=symbol['language'],
                    file_path=symbol['file_path'],
                    line_start=symbol['line_start'],
                    line_end=symbol['line_end'],
                    code_snippet=symbol['code_snippet']
                ),
                relationship=Relationship(
                    type=RelationshipType(rel['relationship_type']),
                    direction=Direction(rel['direction']),
                    data=rel['relationship_data']
                ),
                related_symbol=RelatedSymbol(
                    name=rel['source_name'] if rel['direction'] == 'outgoing' else rel['target_name'],
                    type=SymbolType(rel['source_type'] if rel['direction'] == 'outgoing' else rel['target_type']),
                    file=rel['source_file'] if rel['direction'] == 'outgoing' else rel['target_file'],
                    line=rel['source_line'] if rel['direction'] == 'outgoing' else rel['target_line']
                )
            ))
    
    return GetSymbolRelationshipsOutput(
        symbol_name=input_data.symbol_name,
        project_id=input_data.project_id,
        relationship_type=input_data.relationship_type,
        direction=input_data.direction,
        total_relationships=len(all_relationships),
        relationships=all_relationships
    )


@app.tool()
async def get_dependency_graph(input_data: GetDependencyGraphInput, ctx: Optional[Context] = None) -> GetDependencyGraphOutput:
    """Get a dependency graph for the project showing relationships between symbols."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    if ctx:
        await ctx.info(f"Generating dependency graph for project '{input_data.project_id or 'all'}'")
    
    graph = db_manager.get_dependency_graph(input_data.project_id, input_data.max_depth)
    
    # Convert nodes to DependencyNode models
    nodes = []
    for node in graph['nodes']:
        nodes.append(DependencyNode(
            id=node['id'],
            name=node['name'],
            type=SymbolType(node['type']),
            file=node['file'],
            line=node['line']
        ))
    
    # Convert edges to DependencyEdge models
    edges = []
    for edge in graph['edges']:
        edges.append(DependencyEdge(
            source=edge['source'],
            target=edge['target'],
            relationship_type=RelationshipType(edge['relationship_type']),
            weight=edge.get('weight')
        ))
    
    return GetDependencyGraphOutput(
        project_id=input_data.project_id,
        max_depth=input_data.max_depth,
        total_nodes=graph['total_nodes'],
        total_edges=graph['total_edges'],
        nodes=nodes,
        edges=edges
    )


@app.tool()
async def analyze_call_hierarchy(input_data: AnalyzeCallHierarchyInput, ctx: Optional[Context] = None) -> AnalyzeCallHierarchyOutput:
    """Analyze the call hierarchy for a specific function."""
    if not db_manager:
        raise RuntimeError("Server not properly initialized")
    
    if ctx:
        await ctx.info(f"Analyzing call hierarchy for '{input_data.function_name}'")
    
    # Find the function
    functions = db_manager.search_by_name(input_data.function_name, project_id=input_data.project_id)
    if not functions:
        return AnalyzeCallHierarchyOutput(
            function=Function(
                name=input_data.function_name,
                file="",
                line=0
            ),
            project_id=input_data.project_id,
            callers=[],
            callees=[],
            max_depth=input_data.max_depth,
            error="Function not found"
        )
    
    # Build call hierarchy
    function_info = Function(
        name=input_data.function_name,
        file=functions[0]['file_path'] if functions else "",
        line=functions[0]['line_start'] if functions else 0
    )
    
    # Get callers (who calls this function)
    callers = db_manager.find_callers(input_data.function_name, input_data.project_id)
    caller_list = [Caller(
        name=caller['caller_name'],
        type=SymbolType(caller['caller_type']),
        file=caller['caller_file'],
        line=caller['caller_line']
    ) for caller in callers]
    
    # Get callees (what this function calls)
    callee_list = []
    for function in functions:
        relationships = db_manager.get_symbol_relationships(
            function['id'],
            relationship_type='calls',
            direction='outgoing',
            project_id=input_data.project_id
        )
        
        for rel in relationships:
            callee_list.append(Caller(
                name=rel['target_name'],
                type=SymbolType(rel['target_type']),
                file=rel['target_file'],
                line=rel['target_line']
            ))
    
    return AnalyzeCallHierarchyOutput(
        function=function_info,
        project_id=input_data.project_id,
        callers=caller_list,
        callees=callee_list,
        max_depth=input_data.max_depth
    )


def main():
    """Main entry point for the FastMCP server."""
    import asyncio
    
    logger.info("Starting Codebase Analyzer FastMCP server...")
    
    # Initialize components
    asyncio.run(startup())
    
    # Run the server
    # app.run(transport="http", port=9001)
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
