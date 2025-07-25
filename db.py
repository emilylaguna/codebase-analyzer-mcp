import sqlite3
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import json


class DatabaseManager:
    def __init__(self, db_path: str = "codebase_analyzer.db"):
        self.db_path = db_path
        self.init_database()
    
    def _get_connection(self):
        """Get a SQLite connection with sqlite-vec extension loaded."""
        conn = sqlite3.connect(self.db_path)
        try:
            import sqlite_vec
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            return conn
        except ImportError:
            # sqlite-vec not available, return regular connection
            return conn
    
    def init_database(self):
        """Initialize the database with required tables."""
        with self._get_connection() as conn:
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            conn.enable_load_extension(True)
            
            # Create symbols table with project_id support
            conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    id INTEGER PRIMARY KEY,
                    project_id TEXT NOT NULL DEFAULT 'default',
                    language TEXT NOT NULL,
                    symbol_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_start INTEGER NOT NULL,
                    line_end INTEGER NOT NULL,
                    code_snippet TEXT NOT NULL,
                    file_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(project_id, language, name, file_path, line_start)
                )
            """)
            
            # Add project_id column if it doesn't exist (for existing databases)
            try:
                conn.execute("ALTER TABLE symbols ADD COLUMN project_id TEXT NOT NULL DEFAULT 'default'")
                print("Added project_id column to existing symbols table")
            except sqlite3.OperationalError:
                # Column already exists, ignore
                pass
            
            # Create relationships table for code relationships
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    id INTEGER PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    source_symbol_id INTEGER NOT NULL,
                    target_symbol_id INTEGER NOT NULL,
                    relationship_type TEXT NOT NULL,
                    relationship_data TEXT,  -- JSON data for additional info
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (source_symbol_id) REFERENCES symbols(id) ON DELETE CASCADE,
                    FOREIGN KEY (target_symbol_id) REFERENCES symbols(id) ON DELETE CASCADE,
                    UNIQUE(project_id, source_symbol_id, target_symbol_id, relationship_type)
                )
            """)
            
            # Create virtual table for embeddings using sqlite-vec
            try:
                # Create the virtual table with proper schema
                conn.execute("""
                    CREATE VIRTUAL TABLE IF NOT EXISTS symbol_embeddings 
                    USING vec0(
                        id INTEGER PRIMARY KEY,
                        embedding float[300]
                    )
                """)
                print("Successfully created vec0 virtual table")
            except sqlite3.OperationalError as e:
                # Fallback: create a regular table for embeddings
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS symbol_embeddings (
                        id INTEGER PRIMARY KEY,
                        embedding TEXT NOT NULL
                    )
                """)
                print(f"Warning: sqlite-vec not available ({e}), using fallback storage")
            
            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbols_project_id ON symbols(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbols_language ON symbols(language)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbols_file_path ON symbols(file_path)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_symbols_file_hash ON symbols(file_hash)")
            
            # Relationship indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_project_id ON relationships(project_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_symbol_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_symbol_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_source_type ON relationships(source_symbol_id, relationship_type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_relationships_target_type ON relationships(target_symbol_id, relationship_type)")
            
            conn.commit()
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of file content."""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception:
            return ""
    
    def file_needs_update(self, file_path: str, project_id: str = 'default') -> bool:
        """Check if file needs to be re-parsed based on hash comparison."""
        current_hash = self.get_file_hash(file_path)
        if not current_hash:
            return False
        
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM symbols WHERE file_path = ? AND file_hash = ? AND project_id = ?",
                (file_path, current_hash, project_id)
            )
            count = cursor.fetchone()[0]
            return count == 0
    
    def delete_file_symbols(self, file_path: str, project_id: str = 'default'):
        """Delete all symbols for a given file in a specific project."""
        with self._get_connection() as conn:
            # Get symbol IDs to delete from embeddings table
            cursor = conn.execute(
                "SELECT id FROM symbols WHERE file_path = ? AND project_id = ?",
                (file_path, project_id)
            )
            symbol_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete from embeddings table
            if symbol_ids:
                placeholders = ','.join('?' * len(symbol_ids))
                conn.execute(
                    f"DELETE FROM symbol_embeddings WHERE id IN ({placeholders})",
                    symbol_ids
                )
            
            # Delete from symbols table
            conn.execute("DELETE FROM symbols WHERE file_path = ? AND project_id = ?", (file_path, project_id))
            conn.commit()
    
    def delete_project(self, project_id: str):
        """Delete all symbols and embeddings for a specific project."""
        with self._get_connection() as conn:
            # Get symbol IDs to delete from embeddings table
            cursor = conn.execute(
                "SELECT id FROM symbols WHERE project_id = ?",
                (project_id,)
            )
            symbol_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete from embeddings table
            if symbol_ids:
                placeholders = ','.join('?' * len(symbol_ids))
                conn.execute(
                    f"DELETE FROM symbol_embeddings WHERE id IN ({placeholders})",
                    symbol_ids
                )
            
            # Delete from symbols table
            conn.execute("DELETE FROM symbols WHERE project_id = ?", (project_id,))
            conn.commit()
    
    def list_projects(self) -> List[Dict]:
        """List all projects with their statistics."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    project_id,
                    COUNT(*) as symbol_count,
                    COUNT(DISTINCT file_path) as file_count,
                    COUNT(DISTINCT language) as language_count,
                    MIN(created_at) as first_indexed,
                    MAX(created_at) as last_indexed
                FROM symbols 
                GROUP BY project_id
                ORDER BY symbol_count DESC
            """)
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    "project_id": row[0],
                    "symbol_count": row[1],
                    "file_count": row[2],
                    "language_count": row[3],
                    "first_indexed": row[4],
                    "last_indexed": row[5]
                })
            
            return projects
    
    def insert_symbol(self, symbol_data: Dict, project_id: str = 'default') -> int:
        """Insert a symbol and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO symbols 
                (project_id, language, symbol_type, name, file_path, line_start, line_end, code_snippet, file_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_id,
                symbol_data['language'],
                symbol_data['symbol_type'],
                symbol_data['name'],
                symbol_data['file_path'],
                symbol_data['line_start'],
                symbol_data['line_end'],
                symbol_data['code_snippet'],
                symbol_data['file_hash']
            ))
            conn.commit()
            lastrowid = cursor.lastrowid
            return lastrowid if lastrowid is not None else 0
    
    def insert_relationship(self, source_symbol_id: int, target_symbol_id: int, 
                          relationship_type: str, project_id: str = 'default', 
                          relationship_data: Optional[Dict] = None) -> int:
        """Insert a relationship between two symbols."""
        with self._get_connection() as conn:
            data_json = json.dumps(relationship_data) if relationship_data else None
            cursor = conn.execute("""
                INSERT OR REPLACE INTO relationships 
                (project_id, source_symbol_id, target_symbol_id, relationship_type, relationship_data)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, source_symbol_id, target_symbol_id, relationship_type, data_json))
            conn.commit()
            lastrowid = cursor.lastrowid
            return lastrowid if lastrowid is not None else 0
    
    def delete_symbol_relationships(self, symbol_id: int, project_id: str = 'default'):
        """Delete all relationships involving a specific symbol."""
        with self._get_connection() as conn:
            conn.execute("""
                DELETE FROM relationships 
                WHERE (source_symbol_id = ? OR target_symbol_id = ?) AND project_id = ?
            """, (symbol_id, symbol_id, project_id))
            conn.commit()
    
    def get_symbol_relationships(self, symbol_id: int, relationship_type: Optional[str] = None, 
                               direction: str = 'both', project_id: Optional[str] = None) -> List[Dict]:
        """Get relationships for a specific symbol."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            # Build query based on direction
            if direction == 'outgoing':
                where_clause = "r.source_symbol_id = ?"
                join_clause = """
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                """
            elif direction == 'incoming':
                where_clause = "r.target_symbol_id = ?"
                join_clause = """
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                """
            else:  # both
                where_clause = "(r.source_symbol_id = ? OR r.target_symbol_id = ?)"
                join_clause = """
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                """
            
            # Add relationship type filter
            if relationship_type:
                where_clause += f" AND r.relationship_type = ?"
            
            # Add project filter
            if project_id:
                where_clause += f" AND r.project_id = ?"
            
            # Build the full query
            query = f"""
                SELECT 
                    r.id,
                    r.relationship_type,
                    r.relationship_data,
                    s.id as source_id,
                    s.name as source_name,
                    s.symbol_type as source_type,
                    s.file_path as source_file,
                    s.line_start as source_line,
                    t.id as target_id,
                    t.name as target_name,
                    t.symbol_type as target_type,
                    t.file_path as target_file,
                    t.line_start as target_line,
                    CASE 
                        WHEN r.source_symbol_id = ? THEN 'outgoing'
                        ELSE 'incoming'
                    END as direction
                FROM relationships r
                {join_clause}
                WHERE {where_clause}
                ORDER BY r.relationship_type, s.name, t.name
            """
            
            # Build parameters - CASE statement parameter comes first
            params: List = [symbol_id]  # For the CASE statement
            
            if direction == 'both':
                params.extend([symbol_id, symbol_id])
            else:
                params.append(symbol_id)
            
            if relationship_type:
                params.append(str(relationship_type))
            
            if project_id:
                params.append(str(project_id))
            
            cursor = conn.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
    
    def find_callers(self, function_name: str, project_id: Optional[str] = None) -> List[Dict]:
        """Find all callers of a specific function."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            # Find the function first
            if project_id:
                cursor = conn.execute("""
                    SELECT id FROM symbols 
                    WHERE name = ? AND symbol_type IN ('function', 'method') AND project_id = ?
                """, (function_name, project_id))
            else:
                cursor = conn.execute("""
                    SELECT id FROM symbols 
                    WHERE name = ? AND symbol_type IN ('function', 'method')
                """, (function_name,))
            
            function_ids = [row[0] for row in cursor.fetchall()]
            
            if not function_ids:
                return []
            
            # Find callers
            placeholders = ','.join('?' * len(function_ids))
            if project_id:
                cursor = conn.execute(f"""
                    SELECT 
                        s.id as caller_id,
                        s.name as caller_name,
                        s.symbol_type as caller_type,
                        s.file_path as caller_file,
                        s.line_start as caller_line,
                        s.code_snippet as caller_code,
                        t.name as function_name,
                        t.file_path as function_file,
                        t.line_start as function_line
                    FROM relationships r
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                    WHERE r.target_symbol_id IN ({placeholders})
                    AND r.relationship_type = 'calls'
                    AND r.project_id = ?
                    ORDER BY s.file_path, s.line_start
                """, function_ids + [project_id])
            else:
                cursor = conn.execute(f"""
                    SELECT 
                        s.id as caller_id,
                        s.name as caller_name,
                        s.symbol_type as caller_type,
                        s.file_path as caller_file,
                        s.line_start as caller_line,
                        s.code_snippet as caller_code,
                        t.name as function_name,
                        t.file_path as function_file,
                        t.line_start as function_line
                    FROM relationships r
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                    WHERE r.target_symbol_id IN ({placeholders})
                    AND r.relationship_type = 'calls'
                    ORDER BY s.file_path, s.line_start
                """, function_ids)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def find_implementations(self, interface_name: str, project_id: Optional[str] = None) -> List[Dict]:
        """Find all implementations of an interface/protocol."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            # Find the interface first
            if project_id:
                cursor = conn.execute("""
                    SELECT id FROM symbols 
                    WHERE name = ? AND symbol_type IN ('interface', 'protocol', 'class') AND project_id = ?
                """, (interface_name, project_id))
            else:
                cursor = conn.execute("""
                    SELECT id FROM symbols 
                    WHERE name = ? AND symbol_type IN ('interface', 'protocol', 'class')
                """, (interface_name,))
            
            interface_ids = [row[0] for row in cursor.fetchall()]
            
            if not interface_ids:
                return []
            
            # Find implementations
            placeholders = ','.join('?' * len(interface_ids))
            if project_id:
                cursor = conn.execute(f"""
                    SELECT 
                        s.id as implementation_id,
                        s.name as implementation_name,
                        s.symbol_type as implementation_type,
                        s.file_path as implementation_file,
                        s.line_start as implementation_line,
                        s.code_snippet as implementation_code,
                        t.name as interface_name,
                        t.file_path as interface_file,
                        t.line_start as interface_line
                    FROM relationships r
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                    WHERE r.target_symbol_id IN ({placeholders})
                    AND r.relationship_type IN ('implements', 'extends', 'inherits')
                    AND r.project_id = ?
                    ORDER BY s.file_path, s.line_start
                """, interface_ids + [project_id])
            else:
                cursor = conn.execute(f"""
                    SELECT 
                        s.id as implementation_id,
                        s.name as implementation_name,
                        s.symbol_type as implementation_type,
                        s.file_path as implementation_file,
                        s.line_start as implementation_line,
                        s.code_snippet as implementation_code,
                        t.name as interface_name,
                        t.file_path as interface_file,
                        t.line_start as interface_line
                    FROM relationships r
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                    WHERE r.target_symbol_id IN ({placeholders})
                    AND r.relationship_type IN ('implements', 'extends', 'inherits')
                    ORDER BY s.file_path, s.line_start
                """, interface_ids)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_dependency_graph(self, project_id: Optional[str] = None, max_depth: int = 3) -> Dict:
        """Get a dependency graph for the project."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            # Get all relationships
            if project_id:
                cursor = conn.execute("""
                    SELECT 
                        r.relationship_type,
                        s.id as source_id,
                        s.name as source_name,
                        s.symbol_type as source_type,
                        s.file_path as source_file,
                        t.id as target_id,
                        t.name as target_name,
                        t.symbol_type as target_type,
                        t.file_path as target_file
                    FROM relationships r
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                    WHERE r.project_id = ?
                    ORDER BY r.relationship_type, s.name, t.name
                """, (project_id,))
            else:
                cursor = conn.execute("""
                    SELECT 
                        r.relationship_type,
                        s.id as source_id,
                        s.name as source_name,
                        s.symbol_type as source_type,
                        s.file_path as source_file,
                        t.id as target_id,
                        t.name as target_name,
                        t.symbol_type as target_type,
                        t.file_path as target_file
                    FROM relationships r
                    JOIN symbols s ON r.source_symbol_id = s.id
                    JOIN symbols t ON r.target_symbol_id = t.id
                    ORDER BY r.relationship_type, s.name, t.name
                """)
            
            relationships = [dict(row) for row in cursor.fetchall()]
            
            # Build graph structure
            nodes = {}
            edges = []
            
            for rel in relationships:
                # Add source node
                source_key = f"{rel['source_file']}:{rel['source_name']}"
                if source_key not in nodes:
                    nodes[source_key] = {
                        "id": rel['source_id'],
                        "name": rel['source_name'],
                        "type": rel['source_type'],
                        "file": rel['source_file']
                    }
                
                # Add target node
                target_key = f"{rel['target_file']}:{rel['target_name']}"
                if target_key not in nodes:
                    nodes[target_key] = {
                        "id": rel['target_id'],
                        "name": rel['target_name'],
                        "type": rel['target_type'],
                        "file": rel['target_file']
                    }
                
                # Add edge
                edges.append({
                    "source": source_key,
                    "target": target_key,
                    "type": rel['relationship_type']
                })
            
            return {
                "nodes": list(nodes.values()),
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
    
    def insert_embedding(self, symbol_id: int, embedding: List[float]):
        """Insert embedding for a symbol."""
        with self._get_connection() as conn:
            # Check if vec0 table exists
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='symbol_embeddings'
            """)
            table_info = cursor.fetchone()
            
            if table_info:
                # Check if it's a virtual table
                cursor = conn.execute("""
                    SELECT sql FROM sqlite_master 
                    WHERE type='table' AND name='symbol_embeddings'
                """)
                table_sql = cursor.fetchone()
                
                if table_sql and 'USING vec0' in table_sql[0]:
                    # Use vec0 format: JSON array of floats
                    embedding_json = json.dumps(embedding)
                    conn.execute(
                        "INSERT OR REPLACE INTO symbol_embeddings (id, embedding) VALUES (?, ?)",
                        (symbol_id, embedding_json)
                    )
                else:
                    # Fallback: store as JSON string
                    conn.execute(
                        "INSERT OR REPLACE INTO symbol_embeddings (id, embedding) VALUES (?, ?)",
                        (symbol_id, json.dumps(embedding))
                    )
            else:
                # Table doesn't exist, create fallback
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS symbol_embeddings (
                        id INTEGER PRIMARY KEY,
                        embedding TEXT NOT NULL
                    )
                """)
                conn.execute(
                    "INSERT OR REPLACE INTO symbol_embeddings (id, embedding) VALUES (?, ?)",
                    (symbol_id, json.dumps(embedding))
                )
            
            conn.commit()
    
    def search_by_name(self, name: str, language: Optional[str] = None, project_id: Optional[str] = None) -> List[Dict]:
        """Search symbols by exact name match."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            if project_id and language:
                cursor = conn.execute("""
                    SELECT * FROM symbols 
                    WHERE name LIKE ? AND language = ? AND project_id = ?
                    ORDER BY name, file_path
                """, (f"%{name}%", language, project_id))
            elif project_id:
                cursor = conn.execute("""
                    SELECT * FROM symbols 
                    WHERE name LIKE ? AND project_id = ?
                    ORDER BY name, file_path
                """, (f"%{name}%", project_id))
            elif language:
                cursor = conn.execute("""
                    SELECT * FROM symbols 
                    WHERE name LIKE ? AND language = ?
                    ORDER BY name, file_path
                """, (f"%{name}%", language))
            else:
                cursor = conn.execute("""
                    SELECT * FROM symbols 
                    WHERE name LIKE ?
                    ORDER BY name, file_path
                """, (f"%{name}%",))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def search_semantic(self, query_embedding: List[float], top_k: int = 10, project_id: Optional[str] = None) -> List[Dict]:
        """Search symbols using semantic similarity."""
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            
            # Check if vec0 table exists and is properly set up
            cursor = conn.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='symbol_embeddings'
            """)
            table_sql = cursor.fetchone()
            
            if table_sql and 'USING vec0' in table_sql[0]:
                # Use vec0 MATCH syntax for KNN search with subquery
                try:
                    query_json = json.dumps(query_embedding)
                    if project_id:
                        cursor = conn.execute("""
                            SELECT 
                                symbols.*,
                                0.0 as distance
                            FROM (
                                SELECT id FROM symbol_embeddings 
                                WHERE embedding match ? 
                                LIMIT ?
                            ) e
                            JOIN symbols ON symbols.id = e.id
                            WHERE symbols.project_id = ?
                        """, (query_json, top_k, project_id))
                    else:
                        cursor = conn.execute("""
                            SELECT 
                                symbols.*,
                                0.0 as distance
                            FROM (
                                SELECT id FROM symbol_embeddings 
                                WHERE embedding match ? 
                                LIMIT ?
                            ) e
                            JOIN symbols ON symbols.id = e.id
                        """, (query_json, top_k))
                    return [dict(row) for row in cursor.fetchall()]
                except sqlite3.OperationalError as e:
                    print(f"Warning: vec0 MATCH query failed: {e}")
                    # Fall through to fallback
            else:
                print("Warning: vec0 table not available")
            
            # Fallback: simple text search for now
            print("Warning: Semantic search not available, returning all symbols")
            if project_id:
                cursor = conn.execute("""
                    SELECT symbols.*, 0.0 AS distance
                    FROM symbols
                    WHERE project_id = ?
                    LIMIT ?
                """, (project_id, top_k))
            else:
                cursor = conn.execute("""
                    SELECT symbols.*, 0.0 AS distance
                    FROM symbols
                    LIMIT ?
                """, (top_k,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self, project_id: Optional[str] = None) -> Dict:
        """Get database statistics."""
        with self._get_connection() as conn:
            if project_id:
                # Project-specific stats
                cursor = conn.execute("SELECT COUNT(*) FROM symbols WHERE project_id = ?", (project_id,))
                total_symbols = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM symbol_embeddings e
                    JOIN symbols s ON e.id = s.id
                    WHERE s.project_id = ?
                """, (project_id,))
                symbols_with_embeddings = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT language, COUNT(*) FROM symbols 
                    WHERE project_id = ?
                    GROUP BY language
                """, (project_id,))
                languages = dict(cursor.fetchall())
                
                cursor = conn.execute("""
                    SELECT COUNT(DISTINCT file_path) FROM symbols 
                    WHERE project_id = ?
                """, (project_id,))
                total_files = cursor.fetchone()[0]
                
                # Relationship stats
                cursor = conn.execute("SELECT COUNT(*) FROM relationships WHERE project_id = ?", (project_id,))
                total_relationships = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT relationship_type, COUNT(*) FROM relationships 
                    WHERE project_id = ?
                    GROUP BY relationship_type
                """, (project_id,))
                relationship_types = dict(cursor.fetchall())
            else:
                # Global stats
                cursor = conn.execute("SELECT COUNT(*) FROM symbols")
                total_symbols = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM symbol_embeddings")
                symbols_with_embeddings = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT language, COUNT(*) FROM symbols GROUP BY language")
                languages = dict(cursor.fetchall())
                
                cursor = conn.execute("SELECT COUNT(DISTINCT file_path) FROM symbols")
                total_files = cursor.fetchone()[0]
                
                # Relationship stats
                cursor = conn.execute("SELECT COUNT(*) FROM relationships")
                total_relationships = cursor.fetchone()[0]
                
                cursor = conn.execute("""
                    SELECT relationship_type, COUNT(*) FROM relationships 
                    GROUP BY relationship_type
                """)
                relationship_types = dict(cursor.fetchall())
            
            # Check if vec0 is available
            cursor = conn.execute("""
                SELECT sql FROM sqlite_master 
                WHERE type='table' AND name='symbol_embeddings'
            """)
            table_sql = cursor.fetchone()
            vec0_available = table_sql and 'USING vec0' in table_sql[0] if table_sql else False
            
            return {
                "total_symbols": total_symbols,
                "symbols_with_embeddings": symbols_with_embeddings,
                "languages": languages,
                "total_files": total_files,
                "total_relationships": total_relationships,
                "relationship_types": relationship_types,
                "vec0_available": vec0_available,
                "project_id": project_id
            } 