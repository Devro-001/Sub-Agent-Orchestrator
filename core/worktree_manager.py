"""Git Worktree Manager: Filesystem Isolation and Concurrency Control for Multi-Agent Workflows."""

import json
import fnmatch
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from contracts.types import AgentRole


class WorktreeManager:
    """Manages creation, validation, and lifecycle of git worktrees per agent role."""

    def __init__(self, repo_root: str):
        self.repo_root = Path(repo_root).resolve()
        self.worktrees_dir = self.repo_root / ".worktrees"
        self._ensure_repo_initialized()

    def _ensure_repo_initialized(self) -> None:
        git_dir = self.repo_root / ".git"
        if not git_dir.exists():
            subprocess.run(["git", "init"], cwd=self.repo_root, check=True, capture_output=True)
            # Ensure local git identity is present for automated commits
            subprocess.run(
                ["git", "config", "user.name", "Antigravity Orchestrator"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "orchestrator@antigravity.local"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
            )
            # Create an initial commit if repo is empty
            subprocess.run(
                ["git", "commit", "--allow-empty", "-m", "chore: initial repository root"],
                cwd=self.repo_root,
                check=True,
                capture_output=True,
            )

    def create_worktree(self, role: AgentRole, task_id: str) -> Tuple[str, str]:
        """Creates an isolated git worktree for a task.

        Returns (branch_name, worktree_absolute_path).
        """
        role_slug = role.value if isinstance(role, AgentRole) else role
        role_clean = role_slug.replace("orchestrator-", "").replace("-engineer", "").replace("-auditor", "").replace("-learning", "")
        branch_name = f"worker/{role_clean}/{task_id}"
        worktree_path = self.worktrees_dir / f"{role_clean}-{task_id}"

        self.worktrees_dir.mkdir(parents=True, exist_ok=True)

        if worktree_path.exists():
            return branch_name, str(worktree_path)

        cmd = ["git", "worktree", "add", "-b", branch_name, str(worktree_path), "HEAD"]
        res = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True)
        if res.returncode != 0:
            # If branch already exists, checkout existing branch
            cmd_existing = ["git", "worktree", "add", str(worktree_path), branch_name]
            res2 = subprocess.run(cmd_existing, cwd=self.repo_root, capture_output=True, text=True)
            if res2.returncode != 0:
                raise RuntimeError(f"Failed to create worktree: {res.stderr}\n{res2.stderr}")

        return branch_name, str(worktree_path)

    def remove_worktree(self, worktree_path: str, delete_branch: bool = False, branch_name: Optional[str] = None) -> None:
        """Removes a worktree and cleans up lock files."""
        path = Path(worktree_path)
        if path.exists():
            subprocess.run(["git", "worktree", "remove", "--force", str(path)], cwd=self.repo_root, capture_output=True)
        
        subprocess.run(["git", "worktree", "prune"], cwd=self.repo_root, capture_output=True)

        if delete_branch and branch_name:
            subprocess.run(["git", "branch", "-D", branch_name], cwd=self.repo_root, capture_output=True)

    def list_worktrees(self) -> List[Dict[str, str]]:
        """List all active worktrees."""
        res = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=self.repo_root, capture_output=True, text=True)
        worktrees = []
        current: Dict[str, str] = {}
        for line in res.stdout.splitlines():
            if line.startswith("worktree "):
                current = {"path": line.split(" ", 1)[1]}
            elif line.startswith("branch "):
                current["branch"] = line.split(" ", 1)[1]
                worktrees.append(current)
                current = {}
        return worktrees

    def validate_file_boundaries(self, worktree_path: str, allowed_patterns: List[str]) -> Tuple[bool, List[str]]:
        """Verifies that changed files in the worktree do not violate file boundaries.

        Returns (is_valid, list_of_violating_files).
        """
        wt_path = Path(worktree_path)
        if not wt_path.exists():
            return True, []

        res = subprocess.run(["git", "status", "--porcelain", "-uall"], cwd=wt_path, capture_output=True, text=True)
        changed_files = []
        for line in res.stdout.splitlines():
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2:
                changed_files.append(parts[1])

        violating = []
        for f in changed_files:
            matched = any(fnmatch.fnmatch(f, pat) or fnmatch.fnmatch(f, pat.rstrip("*") + "*") for pat in allowed_patterns)
            if not matched:
                violating.append(f)

        return len(violating) == 0, violating
