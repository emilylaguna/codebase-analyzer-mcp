-- SQL query to delete already indexed hidden files and folders from the database
-- This query identifies and removes symbols from files that should be filtered out

-- First, let's see what hidden files are currently in the database
SELECT 
    file_path,
    COUNT(*) as symbol_count,
    language
FROM symbols 
WHERE (
    -- Files/folders starting with a dot (hidden files/folders)
    file_path LIKE '/.%' OR
    file_path LIKE '%/.%' OR
    file_path LIKE '%/__pycache__%' OR
    file_path LIKE '%/.pytest_cache%' OR
    file_path LIKE '%/.mypy_cache%' OR
    file_path LIKE '%/node_modules%' OR
    file_path LIKE '%/.npm%' OR
    file_path LIKE '%/.yarn%' OR
    file_path LIKE '%/.gradle%' OR
    file_path LIKE '%/build%' OR
    file_path LIKE '%/target%' OR
    file_path LIKE '%/bin%' OR
    file_path LIKE '%/obj%' OR
    file_path LIKE '%/.idea%' OR
    file_path LIKE '%/.vscode%' OR
    file_path LIKE '%/.vs%' OR
    file_path LIKE '%/.DS_Store%' OR
    file_path LIKE '%/Thumbs.db%' OR
    file_path LIKE '%/dist%' OR
    file_path LIKE '%/.dist%' OR
    file_path LIKE '%/out%' OR
    file_path LIKE '%/.out%' OR
    file_path LIKE '%/coverage%' OR
    file_path LIKE '%/.coverage%' OR
    file_path LIKE '%/logs%' OR
    file_path LIKE '%/.logs%' OR
    file_path LIKE '%/tmp%' OR
    file_path LIKE '%/.tmp%' OR
    file_path LIKE '%/temp%' OR
    file_path LIKE '%/.temp%'
)
GROUP BY file_path, language
ORDER BY symbol_count DESC;

-- Now, delete the symbols from hidden files
-- WARNING: This will permanently delete data! Run the SELECT query above first to review.

DELETE FROM symbols 
WHERE (
    -- Files/folders starting with a dot (hidden files/folders)
    file_path LIKE '/.%' OR
    file_path LIKE '%/.%' OR
    file_path LIKE '%/__pycache__%' OR
    file_path LIKE '%/.pytest_cache%' OR
    file_path LIKE '%/.mypy_cache%' OR
    file_path LIKE '%/node_modules%' OR
    file_path LIKE '%/.npm%' OR
    file_path LIKE '%/.yarn%' OR
    file_path LIKE '%/.gradle%' OR
    file_path LIKE '%/build%' OR
    file_path LIKE '%/target%' OR
    file_path LIKE '%/bin%' OR
    file_path LIKE '%/obj%' OR
    file_path LIKE '%/.idea%' OR
    file_path LIKE '%/.vscode%' OR
    file_path LIKE '%/.vs%' OR
    file_path LIKE '%/.DS_Store%' OR
    file_path LIKE '%/Thumbs.db%' OR
    file_path LIKE '%/dist%' OR
    file_path LIKE '%/.dist%' OR
    file_path LIKE '%/out%' OR
    file_path LIKE '%/.out%' OR
    file_path LIKE '%/coverage%' OR
    file_path LIKE '%/.coverage%' OR
    file_path LIKE '%/logs%' OR
    file_path LIKE '%/.logs%' OR
    file_path LIKE '%/tmp%' OR
    file_path LIKE '%/.tmp%' OR
    file_path LIKE '%/temp%' OR
    file_path LIKE '%/.temp%'
);

-- Note: Due to foreign key constraints with CASCADE, 
-- related records in the relationships and symbol_embeddings tables 
-- will be automatically deleted when symbols are deleted.

-- To verify the deletion, you can run this query to see remaining files:
-- SELECT file_path, COUNT(*) as symbol_count FROM symbols GROUP BY file_path ORDER BY symbol_count DESC; 