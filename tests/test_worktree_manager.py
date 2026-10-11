"""Unit tests for WorktreeManager filesystem isolation."""

import subprocess
import tempfile
import unittest
from pathlib import Path

from contracts.types import AgentRole
from core.worktree_manager import WorktreeManager


class TestWorktreeManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.repo_path = Path(self.temp_dir.name)
        self.manager = WorktreeManager(str(self.repo_path))

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_remove_worktree(self):
        branch, wt_path = self.manager.create_worktree(AgentRole.BACKEND, "task-99")
        self.assertTrue(Path(wt_path).exists())
        self.assertIn("task-99", branch)

        # Check list worktrees
        worktrees = self.manager.list_worktrees()
        paths = [w["path"] for w in worktrees]
        self.assertIn(str(wt_path), paths)

        # Remove worktree
        self.manager.remove_worktree(wt_path, delete_branch=True, branch_name=branch)
        self.assertFalse(Path(wt_path).exists())

    def test_file_boundaries_validation(self):
        branch, wt_path = self.manager.create_worktree(AgentRole.FRONTEND, "task-ui")
        wt = Path(wt_path)

        # Create valid frontend file
        (wt / "frontend").mkdir(parents=True, exist_ok=True)
        (wt / "frontend" / "App.jsx").write_text("export default function App() {}", encoding="utf-8")

        is_valid, violations = self.manager.validate_file_boundaries(
            wt_path, ["frontend/**", "styles/**"]
        )
        self.assertTrue(is_valid)
        self.assertEqual(violations, [])

        # Create violating backend file
        (wt / "server").mkdir(parents=True, exist_ok=True)
        (wt / "server" / "db.py").write_text("import sqlite3", encoding="utf-8")

        is_valid2, violations2 = self.manager.validate_file_boundaries(
            wt_path, ["frontend/**", "styles/**"]
        )
        self.assertFalse(is_valid2)
        self.assertIn("server/db.py", violations2)

        # Cleanup
        self.manager.remove_worktree(wt_path, delete_branch=True, branch_name=branch)


if __name__ == "__main__":
    unittest.main()
