import asyncio
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from datetime import datetime
import subprocess
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Service for interacting with GitHub repositories"""
    
    def __init__(self):
        self.temp_dir = None
        
    async def clone_repository(self, github_url: str, commit_count: int) -> Dict[str, Any]:
        """Clone a GitHub repository and extract basic information"""
        
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp(prefix="code_archeologist_")
            logger.info(f"Created temp directory: {self.temp_dir}")
            
            # Extract repo name from URL
            repo_name = github_url.split("/")[-1].replace(".git", "")
            repo_path = os.path.join(self.temp_dir, repo_name)
            
            # Clone repository with limited depth for performance
            clone_depth = min(commit_count + 10, 100)  # Add buffer for commit analysis
            
            clone_cmd = [
                "git", "clone", 
                "--depth", str(clone_depth),
                github_url, 
                repo_path
            ]
            
            logger.info(f"Cloning repository: {github_url}")
            
            # Execute git clone from a stable directory
            original_cwd = os.getcwd()
            result = subprocess.run(clone_cmd, capture_output=True, text=True, cwd=original_cwd)
            
            if result.returncode != 0:
                raise Exception(f"Failed to clone repository: {result.stderr}")
            
            # Verify the repository was cloned successfully
            if not os.path.exists(repo_path):
                raise Exception(f"Repository path does not exist after cloning: {repo_path}")
            
            # Get repository information
            repo_info = await self._get_repository_info(repo_path)
            
            # Get file structure
            file_structure = await self._analyze_file_structure(repo_path)
            
            return {
                "path": repo_path,
                "info": repo_info,
                "file_structure": file_structure,
                "temp_dir": self.temp_dir
            }
            
        except Exception as e:
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            raise e
    
    async def _get_repository_info(self, repo_path: str) -> Dict[str, Any]:
        """Extract basic repository information"""
        
        try:
            # Don't change the current working directory - use cwd parameter instead
            
            # Get basic git info
            remote_url = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True, text=True, cwd=repo_path
            ).stdout.strip()
            
            # Get total commit count
            total_commits = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                capture_output=True, text=True, cwd=repo_path
            ).stdout.strip()
            
            # Get repository creation date (first commit)
            first_commit_date = subprocess.run(
                ["git", "log", "--reverse", "--format=%ai", "--max-count=1"],
                capture_output=True, text=True, cwd=repo_path
            ).stdout.strip()
            
            # Get latest commit info
            latest_commit = subprocess.run(
                ["git", "log", "-1", "--format=%H|%ai|%s|%an"],
                capture_output=True, text=True, cwd=repo_path
            ).stdout.strip()
            
            latest_parts = latest_commit.split("|") if latest_commit else []
            
            # Get branch info
            current_branch = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True, text=True, cwd=repo_path
            ).stdout.strip()
            
            # Get contributors
            contributors = subprocess.run(
                ["git", "shortlog", "-sn", "--all"],
                capture_output=True, text=True, cwd=repo_path
            ).stdout.strip()
            
            return {
                "remote_url": remote_url,
                "total_commits": int(total_commits) if total_commits.isdigit() else 0,
                "first_commit_date": first_commit_date,
                "latest_commit": {
                    "hash": latest_parts[0] if len(latest_parts) > 0 else "",
                    "date": latest_parts[1] if len(latest_parts) > 1 else "",
                    "message": latest_parts[2] if len(latest_parts) > 2 else "",
                    "author": latest_parts[3] if len(latest_parts) > 3 else ""
                },
                "current_branch": current_branch,
                "contributors": [line.strip() for line in contributors.split("\n") if line.strip()][:10]
            }
            
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {"error": str(e)}
    
    async def _analyze_file_structure(self, repo_path: str) -> Dict[str, Any]:
        """Analyze the file structure of the repository"""
        
        try:
            file_stats = {
                "total_files": 0,
                "total_lines": 0,
                "languages": {},
                "file_types": {},
                "directories": [],
                "large_files": []
            }
            
            # Common file extensions and their languages
            language_map = {
                ".py": "Python", ".js": "JavaScript", ".ts": "TypeScript",
                ".java": "Java", ".cpp": "C++", ".c": "C", ".cs": "C#",
                ".php": "PHP", ".rb": "Ruby", ".go": "Go", ".rs": "Rust",
                ".swift": "Swift", ".kt": "Kotlin", ".scala": "Scala",
                ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
                ".json": "JSON", ".xml": "XML", ".yaml": "YAML", ".yml": "YAML",
                ".md": "Markdown", ".txt": "Text", ".sql": "SQL",
                ".sh": "Shell", ".bash": "Shell", ".dockerfile": "Docker"
            }
            
            for root, dirs, files in os.walk(repo_path):
                # Skip .git directory
                if ".git" in root:
                    continue
                    
                # Track directories
                rel_root = os.path.relpath(root, repo_path)
                if rel_root != ".":
                    file_stats["directories"].append(rel_root)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_stats["total_files"] += 1
                    
                    # Get file extension
                    _, ext = os.path.splitext(file.lower())
                    
                    # Track file types
                    if ext:
                        file_stats["file_types"][ext] = file_stats["file_types"].get(ext, 0) + 1
                        
                        # Track languages
                        if ext in language_map:
                            lang = language_map[ext]
                            file_stats["languages"][lang] = file_stats["languages"].get(lang, 0) + 1
                    
                    # Count lines and check file size
                    try:
                        file_size = os.path.getsize(file_path)
                        
                        # Track large files (>1MB)
                        if file_size > 1024 * 1024:
                            file_stats["large_files"].append({
                                "path": os.path.relpath(file_path, repo_path),
                                "size_mb": round(file_size / (1024 * 1024), 2)
                            })
                        
                        # Count lines for text files
                        if ext in language_map and file_size < 10 * 1024 * 1024:  # Skip very large files
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    lines = sum(1 for _ in f)
                                    file_stats["total_lines"] += lines
                            except:
                                pass  # Skip binary files
                                
                    except Exception as e:
                        logger.warning(f"Error analyzing file {file_path}: {e}")
            
            # Sort languages by file count
            file_stats["languages"] = dict(
                sorted(file_stats["languages"].items(), key=lambda x: x[1], reverse=True)
            )
            
            # Sort file types by count
            file_stats["file_types"] = dict(
                sorted(file_stats["file_types"].items(), key=lambda x: x[1], reverse=True)
            )
            
            return file_stats
            
        except Exception as e:
            logger.error(f"Error analyzing file structure: {e}")
            return {"error": str(e)}
    
    async def analyze_commits(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze commit history for patterns and insights"""
        
        try:
            repo_path = repo_data["path"]
            
            # Get commit history with detailed information
            commit_cmd = [
                "git", "log", 
                "--format=%H|%ai|%s|%an|%ae",
                "--numstat",
                f"--max-count=50"  # Limit for demo
            ]
            
            result = subprocess.run(commit_cmd, capture_output=True, text=True, cwd=repo_path)
            
            if result.returncode != 0:
                raise Exception(f"Failed to get commit history: {result.stderr}")
            
            commits = []
            lines = result.stdout.split("\n")
            current_commit = None
            
            for line in lines:
                if "|" in line and len(line.split("|")) >= 4:
                    # New commit line
                    if current_commit:
                        commits.append(current_commit)
                    
                    parts = line.split("|")
                    current_commit = {
                        "hash": parts[0][:8],  # Short hash
                        "date": parts[1],
                        "message": parts[2],
                        "author": parts[3],
                        "email": parts[4],
                        "files_changed": [],
                        "additions": 0,
                        "deletions": 0
                    }
                elif line.strip() and current_commit and "\t" in line:
                    # File change line (additions, deletions, filename)
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        try:
                            additions = int(parts[0]) if parts[0] != "-" else 0
                            deletions = int(parts[1]) if parts[1] != "-" else 0
                            filename = parts[2]
                            
                            current_commit["files_changed"].append({
                                "filename": filename,
                                "additions": additions,
                                "deletions": deletions
                            })
                            current_commit["additions"] += additions
                            current_commit["deletions"] += deletions
                        except ValueError:
                            pass  # Skip malformed lines
            
            # Add the last commit
            if current_commit:
                commits.append(current_commit)
            
            # Analyze patterns
            analysis = await self._analyze_commit_patterns(commits)
            
            return {
                "commits": commits,
                "analysis": analysis,
                "total_analyzed": len(commits)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing commits: {e}")
            return {"error": str(e), "commits": []}
    
    async def _analyze_commit_patterns(self, commits: List[Dict]) -> Dict[str, Any]:
        """Analyze patterns in commit history"""
        
        try:
            if not commits:
                return {"error": "No commits to analyze"}
            
            # Author analysis
            authors = {}
            commit_sizes = []
            file_patterns = {}
            
            for commit in commits:
                # Author stats
                author = commit["author"]
                if author not in authors:
                    authors[author] = {"commits": 0, "additions": 0, "deletions": 0}
                
                authors[author]["commits"] += 1
                authors[author]["additions"] += commit["additions"]
                authors[author]["deletions"] += commit["deletions"]
                
                # Commit size analysis
                total_changes = commit["additions"] + commit["deletions"]
                commit_sizes.append(total_changes)
                
                # File pattern analysis
                for file_change in commit["files_changed"]:
                    filename = file_change["filename"]
                    ext = os.path.splitext(filename)[1].lower()
                    if ext:
                        file_patterns[ext] = file_patterns.get(ext, 0) + 1
            
            # Calculate averages
            avg_commit_size = sum(commit_sizes) / len(commit_sizes) if commit_sizes else 0
            
            # Sort authors by contribution
            top_authors = sorted(authors.items(), key=lambda x: x[1]["commits"], reverse=True)[:5]
            
            # Sort file patterns
            top_file_patterns = sorted(file_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
            
            return {
                "total_commits": len(commits),
                "average_commit_size": round(avg_commit_size, 2),
                "total_authors": len(authors),
                "top_authors": [{"name": name, **stats} for name, stats in top_authors],
                "file_patterns": dict(top_file_patterns),
                "commit_frequency": self._analyze_commit_frequency(commits)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing commit patterns: {e}")
            return {"error": str(e)}
    
    def _analyze_commit_frequency(self, commits: List[Dict]) -> Dict[str, Any]:
        """Analyze commit frequency patterns"""
        
        try:
            if not commits:
                return {}
            
            # Parse dates and analyze frequency
            from collections import defaultdict
            import re
            
            daily_commits = defaultdict(int)
            hourly_commits = defaultdict(int)
            
            for commit in commits:
                date_str = commit["date"]
                # Parse ISO format date
                if date_str:
                    try:
                        # Extract date and hour
                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
                        hour_match = re.search(r'(\d{2}):\d{2}:\d{2}', date_str)
                        
                        if date_match:
                            daily_commits[date_match.group(1)] += 1
                        
                        if hour_match:
                            hourly_commits[int(hour_match.group(1))] += 1
                            
                    except Exception:
                        pass
            
            return {
                "daily_distribution": dict(daily_commits),
                "hourly_distribution": dict(hourly_commits),
                "most_active_day": max(daily_commits.items(), key=lambda x: x[1])[0] if daily_commits else None,
                "most_active_hour": max(hourly_commits.items(), key=lambda x: x[1])[0] if hourly_commits else None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing commit frequency: {e}")
            return {}
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
            except Exception as e:
                logger.error(f"Error cleaning up temp directory: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()