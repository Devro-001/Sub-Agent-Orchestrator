"""Unit tests for TaskEngine atomic state machine and locking."""

import tempfile
import unittest
from pathlib import Path

from contracts.types import Task, TaskStatus, AgentRole, ProjectMeta, AuditResult, TroubleshootingCase
from core.task_engine import TaskEngine


class TestTaskEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test_ledger.db")
        self.engine = TaskEngine(self.db_path)

        # Register test project
        self.project = ProjectMeta(
            id="proj-001",
            name="Test Project",
            root_path="/tmp/test_project",
            description="Testing task engine",
        )
        self.engine.register_project(self.project)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_add_and_get_task(self):
        task = Task(
            id="task-01",
            project_id="proj-001",
            title="Backend Auth API",
            assigned_role=AgentRole.BACKEND,
            file_boundaries=["backend/**"],
        )
        self.engine.add_task(task)

        retrieved = self.engine.get_task("task-01")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "task-01")
        self.assertEqual(retrieved.assigned_role, AgentRole.BACKEND)
        self.assertEqual(retrieved.status, TaskStatus.IDLE)
        self.assertEqual(retrieved.file_boundaries, ["backend/**"])

    def test_atomic_claim_with_dependencies(self):
        # Task 1: Backend API (no deps)
        t1 = Task(
            id="t1",
            project_id="proj-001",
            title="Core Backend",
            assigned_role=AgentRole.BACKEND,
            file_boundaries=["backend/**"],
        )
        # Task 2: Frontend UI (depends on t1)
        t2 = Task(
            id="t2",
            project_id="proj-001",
            title="Core Frontend",
            assigned_role=AgentRole.FRONTEND,
            file_boundaries=["frontend/**"],
            dependencies=["t1"],
        )
        self.engine.add_task(t1)
        self.engine.add_task(t2)

        # Try to claim frontend task first -> should be None because t1 is not APPROVED/MERGED
        claimed_fe = self.engine.claim_next_task(AgentRole.FRONTEND, project_id="proj-001")
        self.assertIsNone(claimed_fe)

        # Claim backend task -> should succeed
        claimed_be = self.engine.claim_next_task(AgentRole.BACKEND, project_id="proj-001")
        self.assertIsNotNone(claimed_be)
        self.assertEqual(claimed_be.id, "t1")
        self.assertEqual(claimed_be.status, TaskStatus.CLAIMED)

        # Mark t1 as APPROVED
        self.engine.update_task_status("t1", TaskStatus.APPROVED)

        # Now frontend task should be claimable
        claimed_fe_after = self.engine.claim_next_task(AgentRole.FRONTEND, project_id="proj-001")
        self.assertIsNotNone(claimed_fe_after)
        self.assertEqual(claimed_fe_after.id, "t2")
        self.assertEqual(claimed_fe_after.status, TaskStatus.CLAIMED)

    def test_audit_pass_and_fail(self):
        task = Task(
            id="t-audit",
            project_id="proj-001",
            title="Audited Task",
            assigned_role=AgentRole.BACKEND,
            file_boundaries=["backend/**"],
        )
        self.engine.add_task(task)

        # Fail audit
        fail_audit = AuditResult(
            task_id="t-audit",
            reviewer_role=AgentRole.QA,
            verdict="FAIL",
            exit_code=1,
            test_output="AssertionError",
            findings=["CWE-89 SQL Injection found"],
        )
        self.engine.record_audit(fail_audit)
        t_failed = self.engine.get_task("t-audit")
        self.assertEqual(t_failed.status, TaskStatus.REJECTED)
        self.assertEqual(t_failed.retry_count, 1)

        # Pass audit
        pass_audit = AuditResult(
            task_id="t-audit",
            reviewer_role=AgentRole.QA,
            verdict="PASS",
            exit_code=0,
            test_output="100% tests passed",
        )
        self.engine.record_audit(pass_audit)
        t_passed = self.engine.get_task("t-audit")
        self.assertEqual(t_passed.status, TaskStatus.APPROVED)


if __name__ == "__main__":
    unittest.main()
