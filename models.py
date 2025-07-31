"""
Pydantic models for typesafe tool inputs and outputs.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class SymbolType(str, Enum):
    """Enum for symbol types."""
    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    CONSTANT = "constant"
    INTERFACE = "interface"
    TYPE = "type"
    MODULE = "module"
    PACKAGE = "package"
    NAMESPACE = "namespace"
    ENUM = "enum"
    STRUCT = "struct"
    TRAIT = "trait"
    PROTOCOL = "protocol"
    ABSTRACT_CLASS = "abstract_class"
    CONSTRUCTOR = "constructor"
    DESTRUCTOR = "destructor"
    PROPERTY = "property"
    FIELD = "field"
    PARAMETER = "parameter"
    IMPORT = "import"
    EXPORT = "export"
    DECORATOR = "decorator"
    ANNOTATION = "annotation"
    MACRO = "macro"
    TEMPLATE = "template"
    GENERIC = "generic"
    ALIAS = "alias"
    TYPEDEF = "typedef"
    UNKNOWN = "unknown"


class RelationshipType(str, Enum):
    """Enum for relationship types."""
    CALLS = "calls"
    INHERITS = "inherits"
    IMPLEMENTS = "implements"
    IMPORTS = "imports"
    EXPORTS = "exports"
    REFERENCES = "references"
    CONTAINS = "contains"
    USES = "uses"
    DEPENDS_ON = "depends_on"
    EXTENDS = "extends"
    OVERRIDES = "overrides"
    SHADOWS = "shadows"
    ALIASES = "aliases"
    TYPEDEFS = "typedefs"
    INSTANTIATES = "instantiates"
    THROWS = "throws"
    CATCHES = "catches"
    RETURNS = "returns"
    PARAMETER_OF = "parameter_of"
    FIELD_OF = "field_of"
    METHOD_OF = "method_of"
    CONSTRUCTOR_OF = "constructor_of"
    DESTRUCTOR_OF = "destructor_of"
    GETTER_OF = "getter_of"
    SETTER_OF = "setter_of"
    ANNOTATES = "annotates"
    DECORATES = "decorates"
    MACRO_EXPANDS = "macro_expands"
    TEMPLATE_INSTANTIATES = "template_instantiates"
    GENERIC_SPECIALIZES = "generic_specializes"
    UNKNOWN = "unknown"


class Direction(str, Enum):
    """Enum for relationship directions."""
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    BOTH = "both"


class HealthStatus(str, Enum):
    """Enum for health status."""
    HEALTHY = "healthy"
    ERROR = "error"
    UNKNOWN = "unknown"
    RUNNING = "running"


# ============================================================================
# BASE MODELS
# ============================================================================

class Location(BaseModel):
    """Model for symbol location information."""
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    column: Optional[int] = Field(None, description="Column number")


class Symbol(BaseModel):
    """Model for a code symbol."""
    id: Optional[int] = Field(None, description="Database ID")
    project_id: Optional[str] = Field(None, description="Project identifier")
    name: str = Field(..., description="Symbol name")
    symbol_type: SymbolType = Field(..., description="Type of symbol")
    language: str = Field(..., description="Programming language")
    file_path: str = Field(..., description="File path")
    line_start: int = Field(..., description="Start line")
    line_end: Optional[int] = Field(None, description="End line")
    code_snippet: str = Field(..., description="Code snippet")
    score: Optional[float] = Field(None, description="Search relevance score")


class Relationship(BaseModel):
    """Model for symbol relationships."""
    type: RelationshipType = Field(..., description="Relationship type")
    direction: Direction = Field(..., description="Relationship direction")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional relationship data")


class RelatedSymbol(BaseModel):
    """Model for related symbols in relationships."""
    name: str = Field(..., description="Symbol name")
    type: SymbolType = Field(..., description="Symbol type")
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")


class SymbolRelationship(BaseModel):
    """Model for a complete symbol relationship."""
    symbol: Symbol = Field(..., description="Source symbol")
    relationship: Relationship = Field(..., description="Relationship details")
    related_symbol: RelatedSymbol = Field(..., description="Related symbol")


class Caller(BaseModel):
    """Model for function callers."""
    name: str = Field(..., description="Caller name")
    type: SymbolType = Field(..., description="Caller type")
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    code: Optional[str] = Field(None, description="Calling code")


class Function(BaseModel):
    """Model for function information."""
    name: str = Field(..., description="Function name")
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")


class CallerInfo(BaseModel):
    """Model for caller information."""
    caller: Caller = Field(..., description="Caller details")
    function: Function = Field(..., description="Function being called")
    project_id: Optional[str] = Field(None, description="Project identifier")


class Implementation(BaseModel):
    """Model for interface implementations."""
    name: str = Field(..., description="Implementation name")
    type: SymbolType = Field(..., description="Implementation type")
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")
    code: Optional[str] = Field(None, description="Implementation code")


class Interface(BaseModel):
    """Model for interface information."""
    name: str = Field(..., description="Interface name")
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")


class ImplementationInfo(BaseModel):
    """Model for implementation information."""
    implementation: Implementation = Field(..., description="Implementation details")
    interface: Interface = Field(..., description="Interface details")
    project_id: Optional[str] = Field(None, description="Project identifier")


class ProjectInfo(BaseModel):
    """Model for project information."""
    project_id: str = Field(..., description="Project identifier")
    name: str = Field(..., description="Project name")
    path: str = Field(..., description="Project path")
    is_git_repo: bool = Field(..., description="Whether it's a git repository")
    last_commit_hash: Optional[str] = Field(None, description="Last commit hash")
    last_branch: Optional[str] = Field(None, description="Last branch")
    last_scan_time: Optional[str] = Field(None, description="Last scan time")
    total_symbols: Optional[int] = Field(None, description="Total symbols")
    total_files: Optional[int] = Field(None, description="Total files")


class GitInfo(BaseModel):
    """Model for git repository information."""
    current_branch: str = Field(..., description="Current branch")
    current_commit_hash: str = Field(..., description="Current commit hash")
    remote_url: Optional[str] = Field(None, description="Remote URL")
    status: Optional[str] = Field(None, description="Repository status")


class EmbeddingModelInfo(BaseModel):
    """Model for embedding model information."""
    model_name: str = Field(..., description="Model name")
    model_dimensions: int = Field(..., description="Model dimensions")
    model_provider: str = Field(..., description="Model provider")


class DatabaseStats(BaseModel):
    """Model for database statistics."""
    total_symbols: int = Field(..., description="Total symbols")
    total_files: int = Field(..., description="Total files")
    total_projects: int = Field(..., description="Total projects")
    total_relationships: int = Field(..., description="Total relationships")
    total_embeddings: int = Field(..., description="Total embeddings")
    languages: Dict[str, int] = Field(..., description="Symbols per language")
    symbol_types: Dict[str, int] = Field(..., description="Symbols per type")


class HealthStatusInfo(BaseModel):
    """Model for health status information."""
    server: HealthStatus = Field(..., description="Server status")
    database: Union[HealthStatus, str] = Field(..., description="Database status")
    embeddings: Union[HealthStatus, str] = Field(..., description="Embeddings status")
    parser: Union[HealthStatus, str] = Field(..., description="Parser status")


class DependencyNode(BaseModel):
    """Model for dependency graph nodes."""
    id: str = Field(..., description="Node ID")
    name: str = Field(..., description="Symbol name")
    type: SymbolType = Field(..., description="Symbol type")
    file: str = Field(..., description="File path")
    line: int = Field(..., description="Line number")


class DependencyEdge(BaseModel):
    """Model for dependency graph edges."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    relationship_type: RelationshipType = Field(..., description="Relationship type")
    weight: Optional[float] = Field(None, description="Edge weight")


class DependencyGraph(BaseModel):
    """Model for dependency graph."""
    total_nodes: int = Field(..., description="Total nodes")
    total_edges: int = Field(..., description="Total edges")
    nodes: List[DependencyNode] = Field(..., description="Graph nodes")
    edges: List[DependencyEdge] = Field(..., description="Graph edges")


class CallHierarchy(BaseModel):
    """Model for call hierarchy."""
    function: Function = Field(..., description="Function details")
    project_id: Optional[str] = Field(None, description="Project identifier")
    callers: List[Caller] = Field(..., description="Function callers")
    callees: List[Caller] = Field(..., description="Function callees")
    max_depth: Optional[int] = Field(None, description="Maximum depth")


# ============================================================================
# TOOL INPUT MODELS
# ============================================================================

class IndexCodebaseInput(BaseModel):
    """Input model for index_codebase tool."""
    path: str = Field(..., description="Path to the codebase directory")
    project_id: str = Field(default="default", description="Unique identifier for this project")


class SearchSymbolByNameInput(BaseModel):
    """Input model for search_symbol_by_name tool."""
    name: str = Field(..., description="Symbol name to search for")
    language: Optional[str] = Field(None, description="Optional language filter")
    project_id: Optional[str] = Field(None, description="Optional project filter")


class SearchSymbolSemanticInput(BaseModel):
    """Input model for search_symbol_semantic tool."""
    query: str = Field(..., description="Natural language query")
    top_k: int = Field(default=10, description="Number of top results to return")
    project_id: Optional[str] = Field(None, description="Optional project filter")


class ForceFullRescanInput(BaseModel):
    """Input model for force_full_rescan tool."""
    project_id: str = Field(..., description="Project identifier to rescan")


class DeleteProjectInput(BaseModel):
    """Input model for delete_project tool."""
    project_id: str = Field(..., description="Project identifier to delete")


class GetProjectInfoInput(BaseModel):
    """Input model for get_project_info tool."""
    project_id: str = Field(..., description="Project identifier")


class GetStatsInput(BaseModel):
    """Input model for get_stats tool."""
    project_id: Optional[str] = Field(None, description="Optional project filter")


class FindFunctionCallersInput(BaseModel):
    """Input model for find_function_callers tool."""
    function_name: str = Field(..., description="Function name to find callers for")
    project_id: Optional[str] = Field(None, description="Optional project filter")


class FindInterfaceImplementationsInput(BaseModel):
    """Input model for find_interface_implementations tool."""
    interface_name: str = Field(..., description="Interface name to find implementations for")
    project_id: Optional[str] = Field(None, description="Optional project filter")


class GetSymbolRelationshipsInput(BaseModel):
    """Input model for get_symbol_relationships tool."""
    symbol_name: str = Field(..., description="Symbol name to get relationships for")
    relationship_type: Optional[RelationshipType] = Field(None, description="Optional relationship type filter")
    direction: Direction = Field(default=Direction.BOTH, description="Relationship direction")
    project_id: Optional[str] = Field(None, description="Optional project filter")


class GetDependencyGraphInput(BaseModel):
    """Input model for get_dependency_graph tool."""
    project_id: Optional[str] = Field(None, description="Optional project filter")
    max_depth: int = Field(default=3, description="Maximum depth for the graph")


class AnalyzeCallHierarchyInput(BaseModel):
    """Input model for analyze_call_hierarchy tool."""
    function_name: str = Field(..., description="Function name to analyze")
    project_id: Optional[str] = Field(None, description="Optional project filter")
    max_depth: int = Field(default=3, description="Maximum depth for the hierarchy")


# ============================================================================
# TOOL OUTPUT MODELS
# ============================================================================

class IndexCodebaseOutput(BaseModel):
    """Output model for index_codebase tool."""
    success: bool = Field(..., description="Whether indexing was successful")
    project_id: str = Field(..., description="Project identifier")
    is_git_repo: bool = Field(..., description="Whether it's a git repository")
    current_commit_hash: Optional[str] = Field(None, description="Current commit hash")
    current_branch: Optional[str] = Field(None, description="Current branch")
    last_commit_hash: Optional[str] = Field(None, description="Last commit hash")
    last_branch: Optional[str] = Field(None, description="Last branch")
    processed_files: int = Field(..., description="Number of processed files")
    total_symbols_added: int = Field(..., description="Total symbols added")
    errors: List[str] = Field(..., description="List of errors")
    database_stats: DatabaseStats = Field(..., description="Database statistics")
    error: Optional[str] = Field(None, description="Error message if failed")


class SearchSymbolByNameOutput(BaseModel):
    """Output model for search_symbol_by_name tool."""
    success: bool = Field(..., description="Whether search was successful")
    query: str = Field(..., description="Search query")
    language_filter: Optional[str] = Field(None, description="Language filter used")
    project_filter: Optional[str] = Field(None, description="Project filter used")
    total_results: int = Field(..., description="Total results found")
    results: List[Symbol] = Field(..., description="Search results")
    error: Optional[str] = Field(None, description="Error message if failed")


class SearchSymbolSemanticOutput(BaseModel):
    """Output model for search_symbol_semantic tool."""
    success: bool = Field(..., description="Whether search was successful")
    query: str = Field(..., description="Search query")
    top_k: int = Field(..., description="Number of results requested")
    project_filter: Optional[str] = Field(None, description="Project filter used")
    total_results: int = Field(..., description="Total results found")
    results: List[Symbol] = Field(..., description="Search results")
    error: Optional[str] = Field(None, description="Error message if failed")


class ListProjectsOutput(BaseModel):
    """Output model for list_projects tool."""
    success: bool = Field(..., description="Whether listing was successful")
    total_projects: int = Field(..., description="Total projects")
    projects: List[ProjectInfo] = Field(..., description="List of projects")
    error: Optional[str] = Field(None, description="Error message if failed")


class ForceFullRescanOutput(BaseModel):
    """Output model for force_full_rescan tool."""
    success: bool = Field(..., description="Whether rescan was successful")
    project_id: str = Field(..., description="Project identifier")
    message: str = Field(..., description="Success message")
    error: Optional[str] = Field(None, description="Error message if failed")


class DeleteProjectOutput(BaseModel):
    """Output model for delete_project tool."""
    success: bool = Field(..., description="Whether deletion was successful")
    project_id: str = Field(..., description="Project identifier")
    deleted_symbols: int = Field(..., description="Number of deleted symbols")
    deleted_files: int = Field(..., description="Number of deleted files")
    message: str = Field(..., description="Success message")
    error: Optional[str] = Field(None, description="Error message if failed")


class GetProjectInfoOutput(BaseModel):
    """Output model for get_project_info tool."""
    success: bool = Field(..., description="Whether retrieval was successful")
    project_info: Optional[ProjectInfo] = Field(None, description="Project information")
    git_info: Optional[GitInfo] = Field(None, description="Git information")
    database_stats: Optional[DatabaseStats] = Field(None, description="Database statistics")
    error: Optional[str] = Field(None, description="Error message if failed")


class GetStatsOutput(BaseModel):
    """Output model for get_stats tool."""
    success: bool = Field(..., description="Whether retrieval was successful")
    database_stats: DatabaseStats = Field(..., description="Database statistics")
    embedding_model: Optional[EmbeddingModelInfo] = Field(None, description="Embedding model information")
    error: Optional[str] = Field(None, description="Error message if failed")


class HealthCheckOutput(BaseModel):
    """Output model for health_check tool."""
    success: bool = Field(..., description="Whether health check was successful")
    health: HealthStatusInfo = Field(..., description="Health status information")
    error: Optional[str] = Field(None, description="Error message if failed")


class FindFunctionCallersOutput(BaseModel):
    """Output model for find_function_callers tool."""
    function_name: str = Field(..., description="Function name")
    project_id: Optional[str] = Field(None, description="Project identifier")
    total_callers: int = Field(..., description="Total callers found")
    callers: List[CallerInfo] = Field(..., description="List of callers")


class FindInterfaceImplementationsOutput(BaseModel):
    """Output model for find_interface_implementations tool."""
    interface_name: str = Field(..., description="Interface name")
    project_id: Optional[str] = Field(None, description="Project identifier")
    total_implementations: int = Field(..., description="Total implementations found")
    implementations: List[ImplementationInfo] = Field(..., description="List of implementations")


class GetSymbolRelationshipsOutput(BaseModel):
    """Output model for get_symbol_relationships tool."""
    symbol_name: str = Field(..., description="Symbol name")
    project_id: Optional[str] = Field(None, description="Project identifier")
    relationship_type: Optional[RelationshipType] = Field(None, description="Relationship type filter")
    direction: Direction = Field(..., description="Relationship direction")
    total_relationships: int = Field(..., description="Total relationships found")
    relationships: List[SymbolRelationship] = Field(..., description="List of relationships")
    error: Optional[str] = Field(None, description="Error message if failed")


class GetDependencyGraphOutput(BaseModel):
    """Output model for get_dependency_graph tool."""
    project_id: Optional[str] = Field(None, description="Project identifier")
    max_depth: int = Field(..., description="Maximum depth used")
    total_nodes: int = Field(..., description="Total nodes in graph")
    total_edges: int = Field(..., description="Total edges in graph")
    nodes: List[DependencyNode] = Field(..., description="Graph nodes")
    edges: List[DependencyEdge] = Field(..., description="Graph edges")


class AnalyzeCallHierarchyOutput(BaseModel):
    """Output model for analyze_call_hierarchy tool."""
    function: Function = Field(..., description="Function details")
    project_id: Optional[str] = Field(None, description="Project identifier")
    callers: List[Caller] = Field(..., description="Function callers")
    callees: List[Caller] = Field(..., description="Function callees")
    max_depth: int = Field(..., description="Maximum depth used")
    error: Optional[str] = Field(None, description="Error message if failed") 