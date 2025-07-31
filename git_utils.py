#!/usr/bin/env python3
"""
Git utilities for incremental codebase scanning.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, List
from git import Repo, InvalidGitRepositoryError, GitCommandError

logger = logging.getLogger(__name__)


class GitManager:
    """Manages git repository operations for incremental scanning."""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.repo = None
        self._init_repo()
    
    def _init_repo(self):
        """Initialize git repository object."""
        try:
            self.repo = Repo(self.repo_path)
            logger.info(f"Initialized git repository at {self.repo_path}")
        except InvalidGitRepositoryError:
            logger.info(f"Not a git repository: {self.repo_path}")
            self.repo = None
        except Exception as e:
            logger.error(f"Error initializing git repository: {e}")
            self.repo = None
    
    def is_git_repo(self) -> bool:
        """Check if the path is a git repository."""
        return self.repo is not None and not self.repo.bare
    
    def get_current_commit_hash(self) -> Optional[str]:
        """Get the current commit hash."""
        if not self.is_git_repo():
            return None
        
        try:
            return self.repo.head.commit.hexsha
        except Exception as e:
            logger.error(f"Error getting current commit hash: {e}")
            return None
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        if not self.is_git_repo():
            return None
        
        try:
            return self.repo.active_branch.name
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            return None
    
    def get_changed_files(self, since_commit: Optional[str] = None) -> List[str]:
        """
        Get list of changed files since a specific commit.
        
        Args:
            since_commit: Commit hash to compare against. 
                         If None, uses the last commit.
            
        Returns:
            List of file paths that have changed
        """
        if not self.is_git_repo():
            return []
        
        try:
            if since_commit is None:
                # Get the last commit hash
                since_commit = self.repo.head.commit.hexsha
            
            # Get the diff between the current commit and the specified commit
            current_commit = self.repo.head.commit
            try:
                since_commit_obj = self.repo.commit(since_commit)
                diff = current_commit.diff(since_commit_obj)
            except (ValueError, GitCommandError):
                # If the commit doesn't exist or there's an error, return all files
                logger.warning(
                    f"Could not find commit {since_commit}, scanning all files"
                )
                return []
            
            changed_files = []
            for change in diff:
                if change.a_path:
                    changed_files.append(str(self.repo_path / change.a_path))
                if change.b_path and change.b_path != change.a_path:
                    changed_files.append(str(self.repo_path / change.b_path))
            
            # Remove duplicates and return
            return list(set(changed_files))
            
        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return []
    
    def get_untracked_files(self) -> List[str]:
        """Get list of untracked files."""
        if not self.is_git_repo():
            return []
        
        try:
            untracked = self.repo.untracked_files
            return [str(self.repo_path / file_path) for file_path in untracked]
        except Exception as e:
            logger.error(f"Error getting untracked files: {e}")
            return []
    
    def get_modified_files(self) -> List[str]:
        """Get list of modified files (including staged and unstaged changes)."""
        if not self.is_git_repo():
            return []
        
        try:
            modified_files = []
            
            # Get staged changes
            for diff in self.repo.index.diff(self.repo.head.commit):
                if diff.a_path:
                    modified_files.append(str(self.repo_path / diff.a_path))
            
            # Get unstaged changes
            for diff in self.repo.index.diff(None):
                if diff.a_path:
                    modified_files.append(str(self.repo_path / diff.a_path))
            
            return list(set(modified_files))
            
        except Exception as e:
            logger.error(f"Error getting modified files: {e}")
            return []
    
    def get_all_changed_files(self, since_commit: Optional[str] = None) -> List[str]:
        """
        Get all files that need to be rescanned 
        (changed, untracked, or modified).
        
        Args:
            since_commit: Commit hash to compare against
            
        Returns:
            List of file paths that need to be rescanned
        """
        changed_files = self.get_changed_files(since_commit)
        untracked_files = self.get_untracked_files()
        modified_files = self.get_modified_files()
        
        all_files = changed_files + untracked_files + modified_files
        return list(set(all_files))  # Remove duplicates
    
    def get_repo_info(self) -> Dict:
        """Get comprehensive repository information."""
        if not self.is_git_repo():
            return {
                "is_git_repo": False,
                "path": str(self.repo_path)
            }
        
        try:
            commit = self.repo.head.commit if self.repo.head.commit else None
            return {
                "is_git_repo": True,
                "path": str(self.repo_path),
                "current_commit": self.get_current_commit_hash(),
                "current_branch": self.get_current_branch(),
                "remote_urls": [remote.url for remote in self.repo.remotes],
                "last_commit_message": commit.message.strip() if commit else None,
                "last_commit_author": str(commit.author) if commit else None,
                "last_commit_date": (
                    commit.committed_datetime.isoformat() if commit else None
                )
            }
        except Exception as e:
            logger.error(f"Error getting repo info: {e}")
            return {
                "is_git_repo": True,
                "path": str(self.repo_path),
                "error": str(e)
            }


def is_git_repository(path: str) -> bool:
    """Check if a path is a git repository."""
    try:
        repo = Repo(path)
        return not repo.bare
    except (InvalidGitRepositoryError, Exception):
        return False


def get_git_info(path: str) -> Dict:
    """Get git information for a path."""
    git_manager = GitManager(path)
    return git_manager.get_repo_info() 